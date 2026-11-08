#!/usr/bin/env python3
"""Render human-readable result tables from analysis/results.json.

Writes ``analysis/tables.md``.  The manuscript quotes these tables directly, so
the numbers cannot drift from the pipeline output.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import config  # noqa: E402


def fmt(value, digits=3):
    if value is None:
        return "-"
    if isinstance(value, str):
        return value
    try:
        return ("%." + str(digits) + "f") % float(value)
    except (TypeError, ValueError):
        return str(value)


def main() -> int:
    path = config.ANALYSIS / "results.json"
    if not path.exists():
        print("[summarize] no results.json")
        return 1
    res = json.loads(path.read_text())
    corpora = res["corpora"]
    lines = ["# Result tables", "", "Generated from `analysis/results.json`.", ""]

    # Table 1 - corpus description
    lines += ["## Table 1. Corpora", "",
              "| Corpus | Months | Tokens analysed | Distinct words | Role |",
              "|---|---:|---:|---:|---|"]
    for name, r in corpora.items():
        if not r.get("ok"):
            lines.append("| %s | - | - | - | skipped: %s |" % (name, r.get("reason", "?")))
            continue
        role = "negative control" if name == res["negative_control"] else "treated"
        lines.append(
            "| %s | %d | %s | %s | %s |"
            % (name, r["n_months"], format(r["n_tokens"], ","), format(r["n_words"], ","), role)
        )
    lines.append("")

    # Table 2 - clock
    lines += ["## Table 2. Diffusion clock", "",
              "| Corpus | Onset (10%) | Half-adoption (50%) | Saturation (90%) | R² |",
              "|---|---|---|---|---:|"]
    for name, r in corpora.items():
        if not r.get("ok") or not r.get("clock", {}).get("ok"):
            continue
        c = r["clock"]
        lines.append(
            "| %s | %s | **%s** | %s | %s |"
            % (name, c.get("onset_month", "-"), c.get("half_month", "-"),
               c.get("saturation_month", "-"), fmt(c.get("r2"), 2))
        )
    lines.append("")

    # Table 3 - CI and diagnostics
    lines += ["## Table 3. Half-adoption dates with bootstrap CIs and diagnostics", "",
              "| Corpus | Half-adoption | 95% CI | Pre-period excess | Post-period excess | Change | Placebo (fake 2020 break) |",
              "|---|---|---|---:|---:|---:|---:|"]
    for name, r in corpora.items():
        if not r.get("ok"):
            continue
        c = r.get("clock", {})
        ci = c.get("half_month_ci", ["-", "-"]) if c.get("ok") else ["-", "-"]
        placebo = r.get("placebo_break", {}).get("fake_post_mean_excess")
        lines.append(
            "| %s | %s | %s .. %s | %s | %s | %s | %s |"
            % (name, c.get("half_month", "-"), ci[0], ci[1],
               fmt(r.get("pre_mean_excess")), fmt(r.get("post_mean_excess")),
               fmt(r.get("excess_change")), fmt(placebo))
        )
    lines.append("")

    # Table 4 - top discovered words
    lines += ["## Table 4. Largest post-2022 excess words (data-driven)", ""]
    for name, r in corpora.items():
        if not r.get("ok"):
            continue
        top = r.get("top_discovered", [])[:15]
        words = ", ".join("%s (%s)" % (row["word"], fmt(row["mean_excess"], 2)) for row in top)
        lines.append("**%s:** %s" % (name, words))
        lines.append("")

    # Table 5 - markers used
    lines += ["## Table 5. Pre-registered markers available per corpus", "",
              "| Corpus | Markers used | Source |", "|---|---:|---|"]
    for name, r in corpora.items():
        if not r.get("ok"):
            continue
        lines.append("| %s | %d | %s |" % (name, r["n_markers_used"], r["marker_source"]))
    lines.append("")

    # Table 6 - typographic channel
    lines += ["## Table 6. Typographic channel clock", "",
              "| Corpus | Half-adoption | Onset | Saturation |", "|---|---|---|---|"]
    for name, r in corpora.items():
        typo = r.get("typographic") if r.get("ok") else None
        if not typo or not typo.get("clock", {}).get("ok"):
            continue
        c = typo["clock"]
        lines.append("| %s | %s | %s | %s |" % (name, c.get("half_month"), c.get("onset_month"), c.get("saturation_month")))
    lines.append("")

    out = config.ANALYSIS / "tables.md"
    out.write_text("\n".join(lines))
    print(out.read_text())
    print("[summarize] wrote %s" % out.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
