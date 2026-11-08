#!/usr/bin/env python
"""Build the scholarly corpora for *The AI Prose Clock* and validate them.

Corpora built here (both are monthly, 2019-01 .. 2026-10, capped at
``config.DOCS_PER_MONTH_CAP`` documents per month):

* ``arxiv``  - arXiv abstracts, stratified across eight categories
* ``pubmed`` - PubMed abstracts via the Europe PMC REST API

Each corpus is written to ``data/raw/<corpus>/<YYYY-MM>.jsonl.gz`` by the
shared :mod:`src.corpora.io` layer, so runs are resumable: complete months are
skipped and an interrupted run continues where it stopped.

After building, the script validates what is on disk (not just what was built
in this invocation, so resumed runs validate correctly): every month has a
non-empty shard, every record has the required schema, record dates sit in the
shard's month, and per-corpus min/median/max documents per month are reported.
Finally it prints three randomly sampled documents per corpus (truncated).

Usage::

    ./.venv/bin/python scripts/build_corpora_scholarly.py
    ./.venv/bin/python scripts/build_corpora_scholarly.py --corpora pubmed
    ./.venv/bin/python scripts/build_corpora_scholarly.py --start 2024-01 --end 2024-03
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import config  # noqa: E402
from src.corpora import arxiv, io as cio, pubmed  # noqa: E402

CORPUS_MODULES = {"arxiv": arxiv, "pubmed": pubmed}


# ---------------------------------------------------------------------------
# validation helpers
# ---------------------------------------------------------------------------
def scan_corpus(corpus: str, months: list) -> dict:
    """Validate every month shard on disk and collect summary statistics."""
    per_month = []
    schema_bad = 0
    empty_text = 0
    date_misaligned = 0
    duplicate_ids = 0
    category_counts = {}
    total_records = 0
    total_bytes = 0
    missing_months = []

    for month in months:
        path = cio.shard_path(corpus, month)
        if not path.exists():
            missing_months.append(month)
            continue
        size = path.stat().st_size
        total_bytes += size
        count = 0
        seen = set()
        with_io = cio.read_jsonl_gz(path)
        for record in with_io:
            count += 1
            if not isinstance(record, dict):
                schema_bad += 1
                continue
            meta = record.get("meta")
            if (
                not isinstance(record.get("id"), str)
                or not isinstance(record.get("date"), str)
                or len(record.get("date", "")) != 10
                or not isinstance(record.get("text"), str)
                or not isinstance(meta, dict)
                or not isinstance(meta.get("category"), str)
                or not isinstance(meta.get("source"), str)
            ):
                schema_bad += 1
                continue
            if not record["text"].strip():
                empty_text += 1
            if record["date"][:7] != month:
                date_misaligned += 1
            if record["id"] in seen:
                duplicate_ids += 1
            seen.add(record["id"])
            category_counts[meta["category"]] = category_counts.get(meta["category"], 0) + 1
        per_month.append({"month": month, "records": count, "bytes": size})
        total_records += count

    counts = [entry["records"] for entry in per_month if entry["records"] > 0]
    return {
        "corpus": corpus,
        "months_expected": len(months),
        "months_present": len(per_month),
        "missing_months": missing_months,
        "empty_months": [entry["month"] for entry in per_month if entry["records"] == 0],
        "total_records": total_records,
        "total_bytes": total_bytes,
        "min_per_month": min(counts) if counts else 0,
        "median_per_month": int(statistics.median(counts)) if counts else 0,
        "max_per_month": max(counts) if counts else 0,
        "schema_violations": schema_bad,
        "empty_text": empty_text,
        "date_misaligned": date_misaligned,
        "duplicate_ids": duplicate_ids,
        "categories": dict(sorted(category_counts.items())),
        "per_month": per_month,
    }


def _random_doc(corpus: str, month: str, rng: random.Random):
    """Return one random record from a shard (reservoir sampling)."""
    picked = None
    seen = 0
    for record in cio.read_jsonl_gz(cio.shard_path(corpus, month)):
        seen += 1
        if rng.random() < 1.0 / seen:
            picked = record
    return picked


def spot_check(corpus: str, months: list, n: int, seed: int = 20261107) -> None:
    """Print ``n`` random documents from ``corpus``, text truncated."""
    rng = random.Random(seed)
    available = [m for m in months if cio.shard_path(corpus, m).exists()]
    if not available:
        print("  (no shards to spot-check)")
        return
    picks = rng.sample(available, min(n, len(available)))
    for month in picks:
        record = _random_doc(corpus, month, rng)
        if record is None:
            continue
        text = " ".join(record["text"].split())
        print(
            "  %s  id=%s  date=%s  meta=%s"
            % (corpus, record["id"], record["date"], json.dumps(record["meta"], ensure_ascii=False))
        )
        print("    text[:180]: %s" % text[:180])
    print()


def print_summary(scan: dict) -> None:
    print(
        "  months=%d/%d  records=%d  bytes=%d (%.1f MB)"
        % (
            scan["months_present"],
            scan["months_expected"],
            scan["total_records"],
            scan["total_bytes"],
            scan["total_bytes"] / 1e6,
        )
    )
    print(
        "  docs/month: min=%d  median=%d  max=%d"
        % (scan["min_per_month"], scan["median_per_month"], scan["max_per_month"])
    )
    print("  schema violations=%d  empty text=%d  date not in shard month=%d  duplicate ids=%d"
          % (scan["schema_violations"], scan["empty_text"], scan["date_misaligned"], scan["duplicate_ids"]))
    if scan["missing_months"]:
        print("  MISSING shards: %s" % ", ".join(scan["missing_months"]))
    if scan["empty_months"]:
        print("  EMPTY shards: %s" % ", ".join(scan["empty_months"]))
    if len(scan["categories"]) <= 12:
        print("  categories: %s" % json.dumps(scan["categories"], ensure_ascii=False))


def month_span(start: str, end: str) -> list:
    y0, m0 = (int(x) for x in start.split("-"))
    y1, m1 = (int(x) for x in end.split("-"))
    months = []
    year, month = y0, m0
    while (year, month) <= (y1, m1):
        months.append("%04d-%02d" % (year, month))
        month += 1
        if month == 13:
            year, month = year + 1, 1
    return months


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--corpora", default="arxiv,pubmed", help="comma-separated: %s" % ",".join(CORPUS_MODULES))
    parser.add_argument("--start", default=config.WINDOW_START)
    parser.add_argument("--end", default=config.WINDOW_END)
    parser.add_argument("--cap", type=int, default=config.DOCS_PER_MONTH_CAP)
    parser.add_argument("--refresh", action="store_true", help="rebuild months even if the shard exists")
    parser.add_argument("--spot-check", type=int, default=3, help="random documents to print per corpus")
    parser.add_argument("--no-build", action="store_true", help="only validate existing shards")
    args = parser.parse_args(argv)

    corpora = [name.strip() for name in args.corpora.split(",") if name.strip()]
    for name in corpora:
        if name not in CORPUS_MODULES:
            parser.error("unknown corpus %r (choose from %s)" % (name, ", ".join(CORPUS_MODULES)))

    months = month_span(args.start, args.end)
    print(
        "Building corpora=%s  window=%s..%s (%d months)  cap=%d/month"
        % (",".join(corpora), args.start, args.end, len(months), args.cap)
    )
    print("-" * 78)

    started = time.time()
    summaries = []
    for name in corpora:
        module = CORPUS_MODULES[name]
        print("== %s ==" % name)
        if args.no_build:
            print("[%s] build skipped (--no-build)" % name, flush=True)
            continue
        summary = module.build(start=args.start, end=args.end, cap=args.cap, refresh=args.refresh)
        summaries.append(summary)
        print(
            "[%s] done: built=%d skipped=%d records=%d bytes=%d errors=%d"
            % (
                name,
                summary["built"],
                summary["skipped"],
                summary["records"],
                summary["bytes"],
                len(summary["errors"]),
            ),
            flush=True,
        )
        for error in summary["errors"]:
            print("[%s]   error %s: %s" % (name, error["month"], error["error"]), flush=True)
    build_seconds = time.time() - started
    print("-" * 78)

    print("Validation (scanning shards on disk)")
    scans = []
    failures = 0
    for name in corpora:
        print("== %s ==" % name)
        scan = scan_corpus(name, months)
        scans.append(scan)
        print_summary(scan)
        problems = (
            scan["missing_months"]
            or scan["empty_months"]
            or scan["schema_violations"]
            or scan["duplicate_ids"]
            or scan["empty_text"]
        )
        if problems:
            failures += 1
        print()
    for summary in summaries:
        if summary["errors"]:
            failures += 1

    print("Spot checks")
    for name in corpora:
        print("== %s ==" % name)
        spot_check(name, months, args.spot_check)
    print("-" * 78)
    print(
        "Wall time: %.1fs build + %.1fs validation | build errors: %d | validation failures: %d"
        % (build_seconds, time.time() - started - build_seconds, sum(len(s["errors"]) for s in summaries), failures)
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
