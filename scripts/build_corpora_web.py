#!/usr/bin/env python3
"""Build the web-register corpora: Hacker News comments and NVD CVE descriptions.

Resumable: complete month shards are skipped, so this can be interrupted and
restarted safely.

Usage:  ./.venv/bin/python scripts/build_corpora_web.py [hn|nvd|all]
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import config  # noqa: E402
from src.corpora import hackernews, nvd  # noqa: E402


def main() -> int:
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    print("[web] window %s .. %s" % (config.WINDOW_START, config.WINDOW_END), flush=True)

    if which in ("hn", "all"):
        n = hackernews.build()
        print("[web] hackernews total: %d" % n, flush=True)
    if which in ("nvd", "all"):
        n = nvd.build()
        print("[web] nvd total: %d" % n, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
