"""Turning the excess index into a dated diffusion curve - the "clock".

A logistic diffusion curve is fitted to the monthly index:

    index(t) = K / (1 + exp(-g * (t - t0)))

where ``K`` is the saturation level, ``g`` the diffusion speed, and ``t0`` the
inflection month.  The reported clock dates are the 10%, 50% and 90% crossings.

Uncertainty is propagated by parametric bootstrap from the per-month standard
errors of the index, which is conservative: it treats months as independent,
so the resulting intervals are wide rather than optimistic.
"""

from typing import Dict, List, Optional, Sequence

import numpy as np
from scipy.optimize import curve_fit


def month_to_year(month: str) -> float:
    year, mon = (int(x) for x in month.split("-"))
    return year + (mon - 1) / 12.0


def year_to_month(value: float) -> str:
    year = int(np.floor(value))
    mon = int(round((value - year) * 12)) + 1
    if mon < 1:
        year, mon = year - 1, 12
    if mon > 12:
        year, mon = year + 1, 1
    return "%04d-%02d" % (year, mon)


def logistic(t, K, g, t0):
    return K / (1.0 + np.exp(-g * (t - t0)))


def fit_logistic(t: np.ndarray, y: np.ndarray) -> Optional[Dict[str, float]]:
    """Fit the diffusion curve; returns None if fitting fails."""
    if len(t) < 6 or not np.isfinite(y).all():
        return None
    initial = [max(float(np.max(y)), 0.05) * 1.2, 1.5, float(t[y > np.max(y) * 0.5].mean()) if np.any(y > np.max(y) * 0.5) else float(np.median(t))]
    bounds = ([0.0, 0.05, float(t.min()) - 3.0], [5.0, 40.0, float(t.max()) + 1.0])
    try:
        popt, _ = curve_fit(logistic, t, y, p0=initial, bounds=bounds, maxfev=20000)
    except Exception:  # noqa: BLE001
        return None
    K, g, t0 = (float(x) for x in popt)
    if not np.isfinite([K, g, t0]).all():
        return None
    return {
        "K": K,
        "g": g,
        "t0": t0,
        "onset_10pct": t0 - np.log(9.0) / g,
        "half": t0,
        "saturation_90pct": t0 + np.log(9.0) / g,
    }


def _r_squared(t: np.ndarray, y: np.ndarray, params: Dict[str, float]) -> float:
    pred = logistic(t, params["K"], params["g"], params["t0"])
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    return 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")


MIN_R2 = 0.40          # below this the curve is not identified
MAX_PLAUSIBLE_G = 15.0  # per year; steeper than this is a degenerate fit


def fit_clock(
    months: Sequence[str],
    values: Sequence[float],
    se: Optional[Sequence[float]] = None,
    n_boot: int = 400,
    seed: int = 0,
) -> Dict[str, object]:
    """Fit the clock and bootstrap its dates.

    Returns the point estimate, bootstrap confidence intervals for the three
    crossing dates, and the fraction of bootstrap fits that failed (a useful
    diagnostic: a high failure rate means the curve is not well identified).
    """
    t = np.array([month_to_year(m) for m in months], dtype=float)
    y = np.asarray(values, dtype=float)
    mask = np.isfinite(y)
    t, y = t[mask], y[mask]
    if se is None:
        sigma = None
    else:
        sigma = np.asarray(se, dtype=float)[mask]
        sigma = np.where(np.isfinite(sigma) & (sigma > 1e-6), sigma, np.nanmedian(sigma) if np.any(np.isfinite(sigma)) else 0.05)

    point = fit_logistic(t, y)
    if point is None:
        return {"ok": False, "reason": "fit_failed"}

    r2 = _r_squared(t, y, point)
    if r2 < MIN_R2 or point["g"] > MAX_PLAUSIBLE_G:
        # A diffusion curve that does not explain the series, or that rises
        # implausibly fast, is not a dated diffusion - report it as unidentified
        # rather than extrapolating absurd crossing dates from it.
        return {
            "ok": False,
            "reason": "not_identified",
            "r2": float(r2),
            "g_per_year": float(point["g"]),
        }

    rng = np.random.default_rng(seed)
    boots: List[Dict[str, float]] = []
    failures = 0
    sigma_use = sigma if sigma is not None else np.full_like(y, float(np.std(y)) * 0.2)
    for _ in range(n_boot):
        sampled = y + rng.normal(0.0, sigma_use)
        fitted = fit_logistic(t, sampled)
        if fitted is None:
            failures += 1
            continue
        boots.append(fitted)

    def _ci(key):
        if not boots:
            return [float("nan"), float("nan")]
        arr = np.array([b[key] for b in boots])
        arr = arr[np.isfinite(arr)]
        if arr.size == 0:
            return [float("nan"), float("nan")]
        return [float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))]

    result = {
        "ok": True,
        "n_months": int(len(t)),
        "K": point["K"],
        "g_per_year": point["g"],
        "r2": float(r2),
        "onset_10pct": point["onset_10pct"],
        "half_adoption": point["half"],
        "saturation_90pct": point["saturation_90pct"],
        "onset_month": year_to_month(point["onset_10pct"]),
        "half_month": year_to_month(point["half"]),
        "saturation_month": year_to_month(point["saturation_90pct"]),
        "onset_ci": _ci("onset_10pct"),
        "half_ci": _ci("half"),
        "saturation_ci": _ci("saturation_90pct"),
        "n_boot": len(boots),
        "n_boot_failed": failures,
    }
    for key in ("onset", "half", "saturation"):
        lo_hi = result[key + "_ci"] if key != "half" else result["half_ci"]
        if np.isfinite(lo_hi[0]):
            result[key + "_month_ci"] = [year_to_month(lo_hi[0]), year_to_month(lo_hi[1])]
    return result


def fit_quality(t: np.ndarray, y: np.ndarray, params: Dict[str, float]) -> Dict[str, float]:
    """R-squared of the fitted diffusion curve (for reporting only)."""
    pred = logistic(t, params["K"], params["g"], params["t0"])
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return {"r2": r2, "rmse": float(np.sqrt(ss_res / len(y)))}
