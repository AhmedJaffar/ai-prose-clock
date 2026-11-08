"""arXiv abstract corpus.

Retrieval notes (verified live against the API on 2026-11-07)
--------------------------------------------------------------
* The endpoint must be **HTTPS**: ``http://export.arxiv.org/api/query`` returns
  an empty body, ``https://export.arxiv.org/api/query`` returns Atom XML.
* arXiv asks that clients make **at most one request every three seconds**.
  This module enforces that spacing for every request (including retries) via
  :func:`_sleep_spacing`.
* One query is issued per ``(category, month)``.  The per-month sample is then
  drawn **round-robin across categories** up to ``cap`` so that no single
  category dominates the month; the queried category is stored as
  ``meta["category"]``.
* Papers cross-listed in several categories are returned by several queries;
  records are de-duplicated by arXiv id before the round-robin selection.
* Within a category results are sorted by submission date (ascending).  When a
  category has more than ``FETCH_PER_CATEGORY`` papers in a month only the
  earliest ones are fetched; this is a deterministic month-internal ordering,
  not a random sample, and it is documented here rather than silently fixed.
* Atom namespaces: default ``http://www.w3.org/2005/Atom`` plus
  ``http://arxiv.org/schemas/atom`` for ``primary_category`` and
  ``http://a9.com/-/spec/opensearch/1.1/`` for ``totalResults``.

Record schema written to ``data/raw/arxiv/<YYYY-MM>.jsonl.gz``::

    {"id": "arxiv:2401.00642", "date": "2024-01-01", "text": "<abstract>",
     "meta": {"category": "cs.CL", "source": "arxiv",
              "title": "...", "primary_category": "cs.CL"}}
"""

from __future__ import annotations

import random
import re
import time
import xml.etree.ElementTree as ET

import requests

from .. import config
from . import io as cio

ARXIV_API = "https://export.arxiv.org/api/query"

#: Categories queried for every month.  Two representatives each for the
#: ``math`` and ``physics`` branches so those registers are not represented by
#: a single sub-field (as requested in the brief).
CATEGORIES = [
    "cs.CL",
    "cs.LG",
    "cs.AI",
    "stat.ML",
    "math.NT",
    "math.CO",
    "hep-th",
    "cond-mat.stat-mech",
]

#: arXiv API etiquette: at most one request every three seconds.
REQUEST_SPACING = 3.0

#: Records requested per category per month.  With eight categories this is
#: 1600 candidates, always enough for the round-robin to reach a 1000 cap when
#: the month really contains that many papers across the categories.
FETCH_PER_CATEGORY = 200

#: Hard per-request ceiling (arXiv allows up to 2000).
MAX_RESULTS = 2000
TIMEOUT = 120
RETRIES = 5

_NS = {
    "a": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
    "os": "http://a9.com/-/spec/opensearch/1.1/",
}

_WS_RE = re.compile(r"\s+")
_ABS_SUFFIX_RE = re.compile(r"v\d+$")
_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

_last_request_at = 0.0


# ---------------------------------------------------------------------------
# rate limiting / HTTP
# ---------------------------------------------------------------------------
def _sleep_spacing(spacing: float = REQUEST_SPACING) -> None:
    """Block until at least ``spacing`` seconds have passed since our last GET."""
    global _last_request_at
    wait = _last_request_at + spacing - time.monotonic()
    if wait > 0:
        time.sleep(wait)
    _last_request_at = time.monotonic()


def _month_query(category: str, month: str) -> str:
    """``search_query`` selecting one arXiv category within one calendar month."""
    first, last = cio.month_bounds(month)
    lo = first.replace("-", "") + "0000"  # YYYYMMDDHHMM
    hi = last.replace("-", "") + "2359"
    return "cat:%s AND submittedDate:[%s TO %s]" % (category, lo, hi)


def _entry_id(atom_id: str) -> str:
    """Canonical arXiv id from an Atom ``<id>`` URL, without the version."""
    tail = atom_id.rsplit("/abs/", 1)[-1].strip()
    tail = _ABS_SUFFIX_RE.sub("", tail)
    return "arxiv:" + tail


def _clean(text: str) -> str:
    return _WS_RE.sub(" ", (text or "")).strip()


def _parse_feed(content: bytes, category: str) -> tuple:
    """Return ``(records, total_results)`` parsed from an Atom feed."""
    root = ET.fromstring(content)
    total_el = root.find("os:totalResults", _NS)
    try:
        total = int(total_el.text) if total_el is not None and total_el.text else 0
    except ValueError:
        total = 0

    records = []
    for entry in root.findall("a:entry", _NS):
        atom_id = (entry.findtext("a:id", default="", namespaces=_NS) or "").strip()
        published = (entry.findtext("a:published", default="", namespaces=_NS) or "").strip()
        date = published.split("T")[0]
        abstract = entry.findtext("a:summary", default="", namespaces=_NS) or ""
        title = entry.findtext("a:title", default="", namespaces=_NS) or ""
        if not atom_id or not _ISO_DATE_RE.match(date) or not abstract.strip():
            continue
        primary_el = entry.find("arxiv:primary_category", _NS)
        primary = primary_el.attrib.get("term", "") if primary_el is not None else ""
        records.append(
            {
                "id": _entry_id(atom_id),
                "date": date,
                "text": _clean(abstract),
                "meta": {
                    "category": category,
                    "source": "arxiv",
                    "title": _clean(title),
                    "primary_category": primary,
                },
            }
        )
    return records, total


def _fetch(category: str, month: str, max_results: int, start: int = 0):
    """Fetch one page of a ``(category, month)`` query; retry with backoff."""
    params = {
        "search_query": _month_query(category, month),
        "start": start,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "ascending",
    }
    last_error = None
    for attempt in range(RETRIES + 1):
        _sleep_spacing(REQUEST_SPACING)
        try:
            resp = requests.get(
                ARXIV_API,
                params=params,
                headers={"User-Agent": config.USER_AGENT},
                timeout=TIMEOUT,
            )
        except requests.RequestException as exc:  # network layer
            last_error = repr(exc)
            time.sleep(min(5 * (attempt + 1), 60))
            continue

        if resp.status_code == 200 and resp.content.strip():
            try:
                return _parse_feed(resp.content, category)
            except ET.ParseError as exc:  # malformed feed -> retry
                last_error = "XML parse error: %r" % (exc,)
                time.sleep(min(5 * (attempt + 1), 60))
                continue

        last_error = "HTTP %s" % resp.status_code
        if resp.status_code in (408, 429, 500, 502, 503, 504) or not resp.content.strip():
            retry_after = resp.headers.get("Retry-After")
            try:
                delay = float(retry_after) if retry_after else None
            except ValueError:
                delay = None
            if delay is None:
                delay = min(2 ** attempt * 5, 120) * (0.5 + random.random())
            time.sleep(min(max(delay, 1.0), 180.0))
            continue
        raise RuntimeError(
            "arXiv query failed (%s) for %s %s: %s"
            % (resp.status_code, category, month, resp.text[:300])
        )

    raise RuntimeError("arXiv query failed after retries for %s %s: %s" % (category, month, last_error))


# ---------------------------------------------------------------------------
# stratified selection
# ---------------------------------------------------------------------------
def _round_robin(pools: dict, cap: int) -> list:
    """Interleave category pools 1:1, de-duplicating by record id, until cap."""
    order = list(pools)
    cursor = {cat: 0 for cat in order}
    seen = set()
    selected = []
    while len(selected) < cap:
        advanced = False
        for cat in order:
            if len(selected) >= cap:
                break
            pool = pools[cat]
            i = cursor[cat]
            while i < len(pool):
                record = pool[i]
                i += 1
                if record["id"] in seen:
                    continue
                seen.add(record["id"])
                selected.append(record)
                advanced = True
                break
            cursor[cat] = i
        if not advanced:
            break
    return selected


def _month_records(month: str, cap: int, categories: list) -> list:
    """Build the (sub)sample of records for one month."""
    pools = {}
    totals = {}
    for category in categories:
        records, total = _fetch(category, month, FETCH_PER_CATEGORY)
        pools[category] = records
        totals[category] = total

    selected = _round_robin(pools, cap)

    # Defensive top-up: only triggers if de-duplication or a category with a
    # small footprint stopped the round-robin short of the cap while the API
    # still holds more records.  Rare, but cheap to guard.
    if len(selected) < cap:
        topped_up = False
        for category in categories:
            fetched = len(pools[category])
            if fetched and fetched < totals[category] and fetched < MAX_RESULTS:
                extra, _ = _fetch(
                    category,
                    month,
                    min(MAX_RESULTS - fetched, totals[category] - fetched),
                    start=fetched,
                )
                if extra:
                    pools[category].extend(extra)
                    topped_up = True
        if topped_up:
            selected = _round_robin(pools, cap)

    return selected


# ---------------------------------------------------------------------------
# public API
# ---------------------------------------------------------------------------
def build(
    start: str = config.WINDOW_START,
    end: str = config.WINDOW_END,
    cap: int = config.DOCS_PER_MONTH_CAP,
    categories=None,
    refresh: bool = False,
) -> dict:
    """Download arXiv abstracts, one gzipped JSONL shard per month.

    Months whose shard already exists (``shard_is_complete``) are skipped, so
    an interrupted run resumes where it stopped.  Returns a summary dict with
    per-month record/byte counts and any failed months.
    """
    categories = list(categories or CATEGORIES)
    months = cio.month_iter(start, end)
    summary = {
        "corpus": "arxiv",
        "start": start,
        "end": end,
        "cap": cap,
        "categories": categories,
        "months": len(months),
        "built": 0,
        "skipped": 0,
        "records": 0,
        "bytes": 0,
        "per_month": [],
        "errors": [],
    }

    for month in months:
        if not refresh and cio.shard_is_complete("arxiv", month):
            summary["skipped"] += 1
            print("[arxiv] %s  skip (shard complete)" % month, flush=True)
            continue
        try:
            records = _month_records(month, cap, categories)
        except Exception as exc:  # noqa: BLE001 - report and continue, resumable
            summary["errors"].append({"month": month, "error": repr(exc)})
            print("[arxiv] %s  FAILED: %r" % (month, exc), flush=True)
            continue

        path = cio.shard_path("arxiv", month)
        count = cio.write_jsonl_gz(path, records)
        size = path.stat().st_size
        summary["built"] += 1
        summary["records"] += count
        summary["bytes"] += size
        summary["per_month"].append({"month": month, "records": count, "bytes": size})
        cats = len({r["meta"]["category"] for r in records})
        print(
            "[arxiv] %s  records=%d  bytes=%d  categories=%d"
            % (month, count, size, cats),
            flush=True,
        )

    return summary
