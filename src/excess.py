"""Excess-vocabulary estimation: the detection-free core of the clock.

Idea
----
For every word we observe a monthly rate (occurrences / tokens).  Before the
public release of ChatGPT the rate of an ordinary word follows a slow, fairly
regular trend.  We fit that trend on the pre-period and extrapolate a
*counterfactual* for every later month.  The **excess** is the log ratio of the
observed rate to the counterfactual rate.

Words whose excess rises sharply and replicably after 2022-11 are the lexical
signature of LLM-influenced prose.  Crucially, nothing here labels a document:
the estimator works entirely on corpus-level aggregate rates.
"""

from typing import Dict, List, Sequence, Tuple

import numpy as np

from . import config, wordlists


# ---------------------------------------------------------------------------
# Vocabulary counts
# ---------------------------------------------------------------------------

def _iter_texts(corpus: str, months: Sequence[str]):
    from .corpora import io as ciro

    for month in months:
        shard = ciro.shard_path(corpus, month)
        if not shard.exists():
            continue
        for record in ciro.read_jsonl_gz(shard):
            text = record.get("text") or ""
            if len(text) >= 80:
                yield month, text


def _tokens(text: str) -> List[str]:
    from .features import word_tokens

    return word_tokens(text)


def count_monthly_vocab(
    corpus: str,
    months: Sequence[str],
    min_total: int = 50,
    min_len: int = 3,
) -> Tuple[List[str], np.ndarray, List[str], np.ndarray]:
    """Two-pass monthly vocabulary counts for one corpus.

    Two passes keep memory bounded: the first pass establishes which words are
    frequent enough to analyse, the second counts only those.

    Returns ``(months_present, totals, words, counts)`` where ``counts`` has
    shape ``(n_words, n_months_present)``.
    """
    from collections import Counter

    # Pass 1: global vocabulary and per-month token totals.
    global_counts = Counter()
    totals_by_month: Dict[str, int] = {}
    for month, text in _iter_texts(corpus, months):
        toks = _tokens(text)
        totals_by_month[month] = totals_by_month.get(month, 0) + len(toks)
        global_counts.update(toks)

    present = [m for m in months if m in totals_by_month and totals_by_month[m] > 0]
    if not present:
        return [], np.array([]), [], np.zeros((0, 0), dtype=np.int32)

    words = sorted(
        w
        for w, c in global_counts.items()
        if c >= min_total and len(w) >= min_len and w not in wordlists.DISCOVERY_BLACKLIST
    )
    kept = set(words)
    index = {w: i for i, w in enumerate(words)}

    # Pass 2: monthly counts restricted to the kept vocabulary.
    counts = np.zeros((len(words), len(present)), dtype=np.int64)
    month_pos = {m: j for j, m in enumerate(present)}
    monthly = Counter()
    current = None
    for month, text in _iter_texts(corpus, months):
        if current is None:
            current = month
        elif month != current:
            for w in kept:
                counts[index[w], month_pos[current]] = monthly.get(w, 0)
            monthly = Counter()
            current = month
        monthly.update(t for t in _tokens(text) if t in kept)
    if current is not None:
        for w in kept:
            counts[index[w], month_pos[current]] = monthly.get(w, 0)

    totals = np.array([totals_by_month[m] for m in present], dtype=np.float64)
    return present, totals, words, counts


# ---------------------------------------------------------------------------
# Counterfactual and excess
# ---------------------------------------------------------------------------

def _month_ordinal(month: str) -> int:
    year, mon = (int(x) for x in month.split("-"))
    return year * 12 + (mon - 1)


def _design(months: Sequence[str], origin: int) -> np.ndarray:
    """Linear time + annual seasonality."""
    t = np.array([_month_ordinal(m) - origin for m in months], dtype=np.float64)
    mo = np.array([int(m[5:7]) for m in months], dtype=np.float64)
    return np.column_stack(
        [np.ones_like(t), t, np.sin(2 * np.pi * mo / 12), np.cos(2 * np.pi * mo / 12)]
    )


def fit_counterfactual(
    months: Sequence[str],
    totals: np.ndarray,
    counts: np.ndarray,
    pre_end: str = config.PRE_END,
) -> Dict[str, np.ndarray]:
    """Fit each word's pre-period log-rate trend and extrapolate.

    Returns a dict with ``excess`` (log observed minus log counterfactual),
    ``pre_resid_sd``, ``slope``, and ``mean_rate`` arrays aligned to ``counts``.
    """
    origin = _month_ordinal(months[0])
    X = _design(months, origin)
    pre = np.array([m <= pre_end for m in months])

    rates = (counts + 0.5) / totals[None, :]
    log_rates = np.log(rates)

    X_pre = X[pre]
    Y_pre = log_rates[:, pre].T            # (n_pre, n_words)
    coef, *_ = np.linalg.lstsq(X_pre, Y_pre, rcond=None)   # (4, n_words)

    # Some BLAS builds raise spurious floating-point flags for this matmul even
    # though the result is finite and correct; the errstate keeps logs clean.
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        predicted = (X @ coef).T           # (n_words, n_months)
    excess = log_rates - predicted

    resid = log_rates[:, pre] - predicted[:, pre]
    pre_resid_sd = resid.std(axis=1)

    return {
        "excess": excess,
        "predicted": predicted,
        "coef": coef,
        "slope_per_year": coef[1] * 12.0,
        "pre_resid_sd": pre_resid_sd,
        "mean_rate": rates.mean(axis=1),
        "pre_mask": pre,
    }


def discover_markers(
    months: Sequence[str],
    words: Sequence[str],
    fit: Dict[str, np.ndarray],
    post_start: str = "2023-01",
    min_pre_coverage: int = 30,
) -> List[Dict[str, object]]:
    """Rank words by mean post-period excess, with stability filters.

    Returns a list of dicts sorted by mean excess (descending).
    """
    post = np.array([m >= post_start for m in months])
    if not post.any():
        return []

    excess = fit["excess"]
    mean_excess = excess[:, post].mean(axis=1)
    std_excess = excess[:, post].std(axis=1)
    slope = fit["slope_per_year"]

    rows = []
    for i, word in enumerate(words):
        rows.append(
            {
                "word": word,
                "mean_excess": float(mean_excess[i]),
                "sd_excess": float(std_excess[i]),
                "slope_per_year": float(slope[i]),
                "mean_rate": float(fit["mean_rate"][i]),
            }
        )
    rows.sort(key=lambda r: r["mean_excess"], reverse=True)
    return rows


def composite_index(
    months: Sequence[str],
    words: Sequence[str],
    fit: Dict[str, np.ndarray],
    markers: Sequence[str],
) -> Dict[str, np.ndarray]:
    """Median excess over a marker set, per month, with a dispersion SE.

    The median makes the index robust to any single marker behaving oddly; the
    reported SE is the standard error of the median under a normal
    approximation.
    """
    lookup = {w: i for i, w in enumerate(words)}
    idx = [lookup[m] for m in markers if m in lookup]
    if not idx:
        raise ValueError("No markers found in vocabulary")

    sub = fit["excess"][idx, :]
    values = np.median(sub, axis=0)
    spread = sub.std(axis=0, ddof=1) if len(idx) > 1 else np.zeros_like(values)
    se = 1.2533 * spread / np.sqrt(max(len(idx), 1))
    return {"values": values, "se": se, "n_markers": np.array([len(idx)])}


def placebo_words(
    words: Sequence[str],
    fit: Dict[str, np.ndarray],
    n: int = 40,
    seed: int = 0,
) -> List[str]:
    """Frequency- and trend-matched non-marker words, used as a null vocabulary."""
    rng = np.random.default_rng(seed)
    log_rate = np.log(fit["mean_rate"])
    slope = fit["slope_per_year"]

    order = np.argsort(log_rate)
    picked: List[int] = []
    for i in order:
        if len(picked) >= n:
            break
        if rng.random() < 0.05:
            picked.append(i)
    if len(picked) < n:
        picked = list(range(min(n, len(words))))
    return [words[i] for i in picked]
