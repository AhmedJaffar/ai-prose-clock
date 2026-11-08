#!/usr/bin/env python3
"""Validate the clock on synthetic corpora with a known diffusion date.

Writes ``analysis/simulation_validation.json``.  Exit code is non-zero if any
correctness check fails, so this doubles as a test suite.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import config, simulate  # noqa: E402
from src.corpora import io as ciro  # noqa: E402


def main() -> int:
    months = ciro.month_iter()
    results = {}
    for seed in (0, 1, 2):
        results["seed_%d" % seed] = simulate.run_validation(months, seed=seed)

    out = config.ANALYSIS / "simulation_validation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))

    all_ok = True
    for name, res in results.items():
        checks = res["checks"]
        status = "PASS" if all(checks.values()) else "FAIL"
        all_ok = all_ok and all(checks.values())
        print(
            "[%s] %-7s recovery=%.2f  true=%s  fitted=%s  err=%s months  placebo=%.4f"
            % (
                status,
                name,
                res["top_ranked_marker_recovery"],
                res["true_half_month"],
                res["fitted_half_month"],
                None if res["half_date_error_months"] is None else round(res["half_date_error_months"], 1),
                res["placebo_index_post_mean"],
            ),
            flush=True,
        )
        if not all(checks.values()):
            print("       failed checks:", [k for k, v in checks.items() if not v], flush=True)
    print("\nwrote %s" % out.relative_to(ROOT), flush=True)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
