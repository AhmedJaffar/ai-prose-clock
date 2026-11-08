#!/usr/bin/env python3
"""Check that the analysis is internally consistent and that the manuscript's
quoted numbers match `analysis/results.json`.

This is a guard against the most common failure mode in computational papers:
numbers in the prose drifting away from the pipeline output.

Exit code is non-zero if any check fails.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import config, clock  # noqa: E402


def _check(cond, msg, failures):
    print(("  PASS  " if cond else "  FAIL  ") + msg)
    if not cond:
        failures.append(msg)


def main() -> int:
    failures = []
    results_path = config.ANALYSIS / "results.json"
    if not results_path.exists():
        print("[verify] no results.json")
        return 1
    results = json.loads(results_path.read_text())
    corpora = results.get("corpora", {})
    control = results.get("negative_control")

    print("[verify] corpus-level checks")
    for name, res in corpora.items():
        if not res.get("ok"):
            continue
        clk = res.get("clock", {})
        if clk.get("ok"):
            _check(
                clk["half_ci"][0] <= clk["half_adoption"] <= clk["half_ci"][1],
                "%s: fitted half-adoption inside bootstrap CI" % name,
                failures,
            )
            _check(
                clk["onset_10pct"] <= clk["half_adoption"] <= clk["saturation_90pct"],
                "%s: onset <= half <= saturation" % name,
                failures,
            )
        else:
            print("  NOTE  %s: clock fit unavailable" % name)

        # A rise is only expected where the instrument is identified; a null or
        # negative change is a legitimate reported result, not a failure.
        if name != control and clk.get("ok"):
            _check(
                res["post_mean_excess"] >= res["pre_mean_excess"],
                "%s: post-period excess >= pre-period excess" % name,
                failures,
            )

    if control in corpora and corpora[control].get("ok"):
        ctrl = corpora[control]
        others = [
            v["excess_change"] for k, v in corpora.items()
            if v.get("ok") and k != control
        ]
        if others:
            _check(
                ctrl["excess_change"] < max(others),
                "negative control: change smaller than the largest treated corpus",
                failures,
            )

    print("[verify] simulation validation")
    sim_path = config.ANALYSIS / "simulation_validation.json"
    if sim_path.exists():
        sim = json.loads(sim_path.read_text())
        for name, res in sim.items():
            _check(all(res["checks"].values()), "%s: all synthetic checks pass" % name, failures)

    print("[verify] manuscript numbers")
    manuscript = config.PAPER / "manuscript.md"
    if manuscript.exists():
        text = manuscript.read_text()
        _check("[TK]" not in text, "manuscript contains no unfilled [TK] placeholders", failures)
        for name, res in corpora.items():
            clk = res.get("clock", {}) if res.get("ok") else {}
            month = clk.get("half_month")
            if month:
                _check(
                    month in text,
                    "%s half-adoption month %s appears in the manuscript" % (name, month),
                    failures,
                )
    else:
        print("  NOTE  manuscript.md not written yet")

    print("\n%d failure(s)" % len(failures))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
