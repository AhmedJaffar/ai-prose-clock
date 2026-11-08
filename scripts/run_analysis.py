#!/usr/bin/env python3
"""End-to-end analysis: excess vocabulary -> composite index -> diffusion clock.

Produces ``analysis/results.json`` (every number quoted in the manuscript) and
the publication figures.  It refuses to write results for a corpus with too
little data, so a half-finished download cannot silently become a finding.

Usage:  ./.venv/bin/python scripts/run_analysis.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import clock, config, excess, features, wordlists  # noqa: E402
from src.corpora import io as ciro  # noqa: E402

MIN_DOCS = 300          # refuse to analyse a corpus with fewer documents
MIN_MONTHS = 60         # need a reasonable time series
NEGATIVE_CONTROL = "nvd"


def available_corpora():
    found = []
    for corpus in config.CORPORA:
        d = config.RAW / corpus
        if d.exists() and len(list(d.glob("*.jsonl.gz"))) >= MIN_MONTHS:
            found.append(corpus)
    return found


def placebo_break_test(present, totals, counts, words, markers):
    """Refit with the pre-period ending in 2020-10 and inspect 2021-01..2022-10.

    If the method is sound, a fake shock date inside the pre-period is absorbed
    by the counterfactual, so the marker excess over the fake post-period is
    ~0.  A large value means the estimator manufactures breaks.
    """
    try:
        fit = excess.fit_counterfactual(present, totals, counts, pre_end="2020-10")
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": repr(exc)[:200]}
    lookup = {w: i for i, w in enumerate(words)}
    idx = [lookup[m] for m in markers if m in lookup]
    if not idx:
        return {"ok": False}
    fake_post = np.array([("2021-01" <= m <= "2022-10") for m in present])
    if not fake_post.any():
        return {"ok": False}
    mean_excess = float(np.mean(fit["excess"][np.ix_(idx, np.where(fake_post)[0])]))
    return {"ok": True, "fake_post_mean_excess": mean_excess}


def typographic_clock(corpus, months):
    path = config.DATA / "generated" / "features" / ("%s.csv.gz" % corpus)
    if not path.exists():
        return None
    df = pd.read_csv(path)
    if df.empty:
        return None
    df["typo_index"] = df.apply(lambda row: features.typographic_index(row), axis=1)
    monthly = (
        df.dropna(subset=["typo_index"])
        .groupby("month")["typo_index"]
        .agg(["mean", "sem", "count"])
        .reset_index()
    )
    monthly = monthly[monthly["count"] >= 30]
    if len(monthly) < MIN_MONTHS:
        return None
    months_t = monthly["month"].tolist()
    values = monthly["mean"].to_numpy()
    se = monthly["sem"].fillna(0.01).to_numpy()
    fitted = clock.fit_clock(months_t, values, se)
    return {
        "months": months_t,
        "values": [float(x) for x in values],
        "se": [float(x) for x in se],
        "clock": fitted,
    }


def specificity_test(present, totals, counts, words, fit, markers, n_draws=1000, seed=0):
    """Could *any* ten frequent words have produced this index?

    We compare the marker index against the null distribution obtained by
    repeatedly sampling the same number of frequency-eligible non-marker words.
    This is the within-corpus placebo that replaces the weak external negative
    control, and it cannot be gamed by selecting words on their outcome.
    """
    pre_mask = np.array([m <= config.PRE_END for m in present])
    post_mask = np.array([m >= config.POST_START for m in present])
    pre_freq = counts[:, pre_mask].mean(axis=1)
    marker_set = set(markers)
    eligible = [i for i, w in enumerate(words) if pre_freq[i] >= 3.0 and w not in marker_set]
    if len(eligible) < 100:
        return {"ok": False, "reason": "too_few_eligible_words"}

    post_excess = fit["excess"][:, post_mask].mean(axis=1)
    lookup = {w: i for i, w in enumerate(words)}
    observed = float(post_excess[[lookup[m] for m in markers]].mean())

    rng = np.random.default_rng(seed)
    null = np.array([
        post_excess[rng.choice(eligible, size=len(markers), replace=False)].mean()
        for _ in range(n_draws)
    ])
    return {
        "ok": True,
        "observed_mean_excess": observed,
        "null_mean": float(null.mean()),
        "null_sd": float(null.std()),
        "p_empirical": float((np.sum(null >= observed) + 1) / (n_draws + 1)),
        "n_eligible": len(eligible),
        "n_draws": n_draws,
    }


def analyse_corpus(corpus, months):
    present, totals, words, counts = excess.count_monthly_vocab(corpus, months)
    if len(present) < MIN_MONTHS or len(words) < 50:
        return {"ok": False, "reason": "insufficient_data", "n_months": len(present), "n_words": len(words)}

    fit = excess.fit_counterfactual(present, totals, counts)
    ranked = excess.discover_markers(present, words, fit)

    available = set(words)
    pre_mask = np.array([m <= config.PRE_END for m in present])
    post_mask = np.array([m >= config.POST_START for m in present])
    lookup = {w: i for i, w in enumerate(words)}
    # ONLY pre-registered markers may build the index. Falling back to words
    # selected for having large excess would be selection on the outcome and
    # would manufacture a result in any corpus (this is exactly what the
    # negative control exposed on a first pass).
    candidates = [w for w in wordlists.LLM_MARKERS_PRE if w in available]
    markers = [w for w in candidates if counts[lookup[w], pre_mask].mean() >= 3.0]
    marker_source = "pre_registered"
    if len(markers) < 5:
        return {
            "ok": False,
            "reason": "insufficient_estimable_markers",
            "n_estimable": len(markers),
            "estimable": markers,
            "n_months": len(present),
            "n_words": len(words),
            "n_tokens": int(totals.sum()),
            "top_discovered": ranked[:25],
        }

    index = excess.composite_index(present, words, fit, markers)
    fitted = clock.fit_clock(present, index["values"], index["se"])

    post = np.array([m >= config.POST_START for m in present])
    pre = np.array([m <= config.PRE_END for m in present])
    if fitted.get("ok"):
        pred = clock.logistic(
            np.array([clock.month_to_year(m) for m in present]),
            fitted["K"], fitted["g_per_year"], fitted["half_adoption"],
        )
        ss_res = float(np.sum((index["values"] - pred) ** 2))
        ss_tot = float(np.sum((index["values"] - np.mean(index["values"])) ** 2))
        fitted["r2"] = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")

    result = {
        "ok": True,
        "n_months": len(present),
        "n_words": len(words),
        "n_tokens": int(totals.sum()),
        "marker_source": marker_source,
        "markers_used": markers,
        "n_markers_used": len(markers),
        "pre_mean_excess": float(np.mean(index["values"][pre])),
        "post_mean_excess": float(np.mean(index["values"][post])),
        "excess_change": float(np.mean(index["values"][post]) - np.mean(index["values"][pre])),
        "months": present,
        "index_values": [float(x) for x in index["values"]],
        "index_se": [float(x) for x in index["se"]],
        "clock": fitted,
        "top_discovered": ranked[:25],
        "specificity": specificity_test(present, totals, counts, words, fit, markers),
        "placebo_break": placebo_break_test(present, totals, counts, words, markers),
        "typographic": typographic_clock(corpus, months),
    }
    return result


def main() -> int:
    months = ciro.month_iter()
    corpora = available_corpora()
    print("[analysis] corpora with enough shards: %s" % (", ".join(corpora) or "none"), flush=True)
    if not corpora:
        print("[analysis] nothing to do yet - corpora incomplete", flush=True)
        return 1

    results = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window": {"start": config.WINDOW_START, "end": config.WINDOW_END,
                   "pre_end": config.PRE_END, "post_start": config.POST_START},
        "negative_control": NEGATIVE_CONTROL,
        "pre_registered_markers": wordlists.LLM_MARKERS_PRE,
        "corpora": {},
    }

    for corpus in corpora:
        print("[analysis] %s ..." % corpus, flush=True)
        results["corpora"][corpus] = analyse_corpus(corpus, months)

    out = config.ANALYSIS / "results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))

    print("\n=== headline ===", flush=True)
    for corpus, res in results["corpora"].items():
        if not res.get("ok"):
            print("%-11s SKIPPED (%s)" % (corpus, res.get("reason")))
            continue
        clk = res["clock"]
        tag = "CONTROL" if corpus == NEGATIVE_CONTROL else ""
        if clk.get("ok"):
            print(
                "%-11s half-adoption=%s  (95%% CI %s..%s)  onset=%s  saturation=%s  R2=%.2f %s"
                % (corpus, clk.get("half_month"), clk.get("half_month_ci", ["?", "?"])[0],
                   clk.get("half_month_ci", ["?", "?"])[1], clk.get("onset_month"),
                   clk.get("saturation_month"), clk.get("r2", float("nan")), tag)
            )
        else:
            print("%-11s clock fit failed %s" % (corpus, tag))
        print("            post-pre excess = %+.3f | placebo(fake 2020 break) = %.3f"
              % (res["excess_change"], res["placebo_break"].get("fake_post_mean_excess", float("nan"))))

    print("\nwrote %s" % out.relative_to(ROOT), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
