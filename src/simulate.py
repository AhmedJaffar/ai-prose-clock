"""Synthetic validation for the excess-vocabulary clock.

Real corpora let us estimate, but they cannot tell us whether the estimator is
*correct*.  Here we generate monthly word-count matrices with a known,
injected LLM-style diffusion and check that the full pipeline recovers it:

* the marker words injected with a diffusion curve must be recovered as the
  top-ranked excess words;
* the fitted half-adoption date must be close to the true inflection;
* trend-matched non-marker words must show ~zero excess (specificity);
* a *placebo* shock injected inside the pre-period must produce no post-period
  excess, because the counterfactual absorbs it.

This is the estimator's unit test, and it is reported in the paper.
"""

from typing import Dict, List, Sequence, Tuple

import numpy as np

from . import clock, excess


def _t(months: Sequence[str]) -> np.ndarray:
    return np.array([clock.month_to_year(m) for m in months], dtype=float)


def simulate_corpus(
    months: Sequence[str],
    n_words: int = 500,
    n_markers: int = 20,
    seed: int = 0,
    shock: float = 2022.92,
    K: float = 0.5,
    g: float = 2.5,
    tokens_per_month: int = 2_000_000,
) -> Tuple[np.ndarray, List[str], np.ndarray, List[str]]:
    """Return ``(totals, words, counts, marker_words)`` for a synthetic corpus."""
    rng = np.random.default_rng(seed)
    t = _t(months)
    n_months = len(months)

    base = np.exp(rng.normal(-6.0, 1.2, n_words))
    trend = rng.normal(0.0, 0.02, n_words)
    month_of_year = np.array([int(m[5:7]) for m in months], dtype=float)
    seasonal = 1.0 + 0.08 * np.sin(2 * np.pi * month_of_year / 12.0)

    rate = base[:, None] * np.exp(trend[:, None] * (t[None, :] - t[0])) * seasonal[None, :]

    marker_idx = rng.choice(n_words, n_markers, replace=False)
    lift = clock.logistic(t, K, g, shock)
    rate[marker_idx, :] = rate[marker_idx, :] * (1.0 + lift[None, :])

    counts = rng.poisson(rate * tokens_per_month).astype(np.int64)
    totals = np.full(n_months, tokens_per_month, dtype=np.float64)
    words = ["w%03d" % i for i in range(n_words)]
    return totals, words, counts, [words[i] for i in marker_idx]


def run_validation(
    months: Sequence[str],
    shock: float = 2022.92,
    placebo_shock: float = 2020.5,
    seed: int = 0,
) -> Dict[str, object]:
    """Run the recovery and specificity tests on synthetic data."""
    totals, words, counts, true_markers = simulate_corpus(months, seed=seed, shock=shock)
    fit = excess.fit_counterfactual(months, totals, counts)

    ranked = excess.discover_markers(months, words, fit)
    top_n = {row["word"] for row in ranked[: len(true_markers)]}
    recovered = len(top_n & set(true_markers)) / len(true_markers)

    index = excess.composite_index(months, words, fit, true_markers)
    fitted = clock.fit_clock(months, index["values"], index["se"], n_boot=200, seed=seed)

    placebo = excess.placebo_words(words, fit, n=len(true_markers), seed=seed + 1)
    placebo_index = excess.composite_index(months, words, fit, placebo)
    post = np.array([m >= "2023-01" for m in months])
    placebo_mean = float(np.mean(placebo_index["values"][post]))

    # A shock placed inside the pre-period must be absorbed by the counterfactual.
    p_totals, p_words, p_counts, _ = simulate_corpus(
        months, seed=seed, shock=placebo_shock
    )
    p_fit = excess.fit_counterfactual(months, p_totals, p_counts)
    p_ranked = excess.discover_markers(months, p_words, p_fit)
    p_top_mean = float(np.mean([r["mean_excess"] for r in p_ranked[: len(true_markers)]]))

    true_half_month = clock.year_to_month(shock)
    recovered_half = fitted.get("half_month") if fitted.get("ok") else None

    return {
        "true_shock": shock,
        "true_half_month": true_half_month,
        "top_ranked_marker_recovery": recovered,
        "n_markers": len(true_markers),
        "fitted_ok": bool(fitted.get("ok")),
        "fitted_half_month": recovered_half,
        "fitted_onset_month": fitted.get("onset_month"),
        "fitted_saturation_month": fitted.get("saturation_month"),
        "half_date_error_months": (
            abs(clock.month_to_year(recovered_half) - shock) * 12 if recovered_half else None
        ),
        "placebo_index_post_mean": placebo_mean,
        "placebo_shock_top_mean_excess": p_top_mean,
        "checks": {
            "recovers_markers": recovered > 0.8,
            "dates_within_3_months": bool(
                recovered_half
                and abs(clock.month_to_year(recovered_half) - shock) * 12 <= 3
            ),
            "placebo_specific": abs(placebo_mean) < 0.05,
            "placebo_date_flat": abs(p_top_mean) < 0.05,
        },
    }
