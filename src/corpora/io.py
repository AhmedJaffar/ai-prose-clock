"""Shared on-disk layout for corpus shards.

Every corpus writes ``data/raw/<corpus>/<YYYY-MM>.jsonl.gz`` with one JSON
record per line::

    {"id": str, "date": "YYYY-MM-DD", "text": str, "meta": {...}}

Writing is atomic (temp file + rename) so an interrupted download never leaves
a corrupt shard that a later resumable run would trust.
"""

import gzip
import json
import os
from pathlib import Path
from typing import Iterable, Iterator, List

from .. import config


def month_iter(start: str = config.WINDOW_START, end: str = config.WINDOW_END) -> List[str]:
    """All ``YYYY-MM`` months in the inclusive study window."""
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


def month_bounds(month: str):
    """First and last calendar day of a ``YYYY-MM`` month."""
    year, mon = (int(x) for x in month.split("-"))
    first = "%04d-%02d-01" % (year, mon)
    if mon == 12:
        last = "%04d-12-31" % year
    else:
        import calendar

        last = "%04d-%02d-%02d" % (year, mon, calendar.monthrange(year, mon)[1])
    return first, last


def shard_path(corpus: str, month: str) -> Path:
    return config.RAW / corpus / ("%s.jsonl.gz" % month)


def write_jsonl_gz(path: Path, records: Iterable[dict]) -> int:
    """Atomically write records to a gzipped JSONL shard. Returns the count."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    count = 0
    with gzip.open(tmp, "wt", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    os.replace(tmp, path)
    return count


def read_jsonl_gz(path: Path) -> Iterator[dict]:
    with gzip.open(Path(path), "rt", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def shard_is_complete(corpus: str, month: str, min_records: int = 1) -> bool:
    """Whether a month shard already exists with enough records (for resume)."""
    path = shard_path(corpus, month)
    if not path.exists():
        return False
    try:
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            n = sum(1 for _ in fh)
        return n >= min_records
    except Exception:  # noqa: BLE001 - a corrupt shard should be rebuilt
        return False
