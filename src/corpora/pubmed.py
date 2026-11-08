"""PubMed / Europe PMC abstract corpus.

Retrieval notes (verified live against Europe PMC REST v6.9 on 2026-11-07)
---------------------------------------------------------------------------
* The brief suggested ``HAS_ABS:Y``; that field does **not** exist in this API
  version and silently matches zero records.  The working field is
  ``HAS_ABSTRACT:Y``.
* ``PUB_MONTH`` is likewise not functional (``PUB_YEAR:2024 AND PUB_MONTH:1``
  returns 0 hits); month selection is done with a publication-date range::

      FIRST_PDATE:[2024-01-01 TO 2024-01-31] AND HAS_ABSTRACT:Y AND SRC:MED

  ``SRC:MED`` restricts to MEDLINE/PubMed records (Europe PMC also indexes
  preprints and Agricola/patents, which we do not want in a PubMed corpus).
* Full text is not used: ``resultType=core`` returns ``abstractText`` plus the
  metadata fields we store.  ``firstPublicationDate`` is normally a complete
  ISO date; when only year-month is available the record is dated to the first
  of that month and the precision is counted (``--exact-date share`` printed).
* Pagination is cursor-based (``cursorMark=*`` then ``nextCursorMark``);
  ``pageSize`` may be at most 1000, which is also our monthly cap, so most
  months are a single request.  We still paginate defensively until the cap or
  the result set is exhausted.

Record schema written to ``data/raw/pubmed/<YYYY-MM>.jsonl.gz``::

    {"id": "med:40036396", "date": "2024-01-31", "text": "<abstract>",
     "meta": {"category": "biomed", "source": "europepmc",
              "title": "...", "journal": "..."}}
"""

from __future__ import annotations

import html
import random
import re
import time

import requests

from .. import config
from . import io as cio

EUROPEPMC_SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

PAGE_SIZE = 1000  # Europe PMC maximum; equals the corpus monthly cap
TIMEOUT = 120
RETRIES = 5

#: Polite pause between Europe PMC requests (shared config value).
REQUEST_SPACING = max(float(config.API_SLEEP), 0.25)

_WS_RE = re.compile(r"\s+")
_TAG_RE = re.compile(r"<[a-zA-Z/!][^>]*>")
_ISO_DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_YEAR_MONTH_RE = re.compile(r"^(\d{4})-(\d{2})$")

_last_request_at = 0.0


# ---------------------------------------------------------------------------
# rate limiting / HTTP
# ---------------------------------------------------------------------------
def _sleep_spacing(spacing: float = REQUEST_SPACING) -> None:
    global _last_request_at
    wait = _last_request_at + spacing - time.monotonic()
    if wait > 0:
        time.sleep(wait)
    _last_request_at = time.monotonic()


def _month_query(month: str) -> str:
    first, last = cio.month_bounds(month)
    return "FIRST_PDATE:[%s TO %s] AND HAS_ABSTRACT:Y AND SRC:MED" % (first, last)


def _clean_text(text: str) -> str:
    """Strip Europe PMC's inline markup (``<h4>Background</h4>`` etc.)."""
    text = _TAG_RE.sub(" ", text or "")
    text = html.unescape(text)
    return _WS_RE.sub(" ", text).strip()


def _normalise_date(raw) -> tuple:
    """Return ``(iso_date_or_None, precision)`` from Europe PMC metadata."""
    if raw is None or raw == "":
        return None, "missing"
    text = str(raw).strip()
    if _ISO_DATE_RE.match(text):
        return text, "exact"
    match = _YEAR_MONTH_RE.match(text)
    if match:
        return match.group(1) + "-" + match.group(2) + "-01", "month"
    return None, "unparseable"


def _journal_title(result: dict) -> str:
    journal_info = result.get("journalInfo") or {}
    journal = journal_info.get("journal") or {}
    return str(journal.get("title") or journal.get("medlineAbbreviation") or "")


def _to_record(result: dict) -> tuple:
    """Map one Europe PMC result to our record schema.

    Returns ``(record, precision)``; ``record`` is ``None`` when the result
    cannot be represented truthfully (no id, no abstract, no usable date).
    """
    abstract = result.get("abstractText")
    if not abstract or not str(abstract).strip():
        return None, "no_abstract"
    raw_id = result.get("pmid") or result.get("id")
    if raw_id is None or str(raw_id).strip() == "":
        return None, "no_id"
    date, precision = _normalise_date(result.get("firstPublicationDate"))
    if date is None:
        return None, "bad_date"
    record = {
        "id": "med:%s" % str(raw_id).strip(),
        "date": date,
        "text": _clean_text(str(abstract)),
        "meta": {
            "category": "biomed",
            "source": "europepmc",
            "title": _clean_text(str(result.get("title") or "")),
            "journal": _journal_title(result),
        },
    }
    return record, precision


def _fetch_page(query: str, cursor: str) -> dict:
    """One Europe PMC search page, retried with backoff."""
    params = {
        "query": query,
        "format": "json",
        "pageSize": PAGE_SIZE,
        "resultType": "core",
        "cursorMark": cursor,
    }
    last_error = None
    for attempt in range(RETRIES + 1):
        _sleep_spacing(REQUEST_SPACING)
        try:
            resp = requests.get(
                EUROPEPMC_SEARCH,
                params=params,
                headers={"User-Agent": config.USER_AGENT},
                timeout=TIMEOUT,
            )
        except requests.RequestException as exc:
            last_error = repr(exc)
            time.sleep(min(5 * (attempt + 1), 60))
            continue

        if resp.status_code == 200:
            try:
                payload = resp.json()
            except ValueError as exc:
                last_error = "JSON decode error: %r" % (exc,)
                time.sleep(min(5 * (attempt + 1), 60))
                continue
            if "resultList" not in payload:
                last_error = "unexpected JSON: %s" % str(payload)[:200]
                time.sleep(min(5 * (attempt + 1), 60))
                continue
            return payload

        last_error = "HTTP %s" % resp.status_code
        if resp.status_code in (408, 429, 500, 502, 503, 504):
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
            "Europe PMC query failed (%s) for %r: %s"
            % (resp.status_code, query, resp.text[:300])
        )

    raise RuntimeError("Europe PMC query failed after retries for %r: %s" % (query, last_error))


def _month_records(month: str, cap: int) -> tuple:
    """Return ``(records, stats)`` for one month, paginating until ``cap``."""
    query = _month_query(month)
    records = []
    seen = set()
    cursor = "*"
    stats = {"hit_count": 0, "requests": 0, "dropped": {}, "precision": {}}

    while len(records) < cap:
        payload = _fetch_page(query, cursor)
        stats["requests"] += 1
        stats["hit_count"] = int(payload.get("hitCount") or 0)
        results = (payload.get("resultList") or {}).get("result") or []
        if not results:
            break

        for result in results:
            if len(records) >= cap:
                break
            record, precision = _to_record(result)
            if record is None:
                stats["dropped"][precision] = stats["dropped"].get(precision, 0) + 1
                continue
            if record["id"] in seen:
                continue
            seen.add(record["id"])
            records.append(record)
            stats["precision"][precision] = stats["precision"].get(precision, 0) + 1

        next_cursor = payload.get("nextCursorMark")
        if not next_cursor or next_cursor == cursor:
            break
        cursor = next_cursor

    return records, stats


# ---------------------------------------------------------------------------
# public API
# ---------------------------------------------------------------------------
def build(
    start: str = config.WINDOW_START,
    end: str = config.WINDOW_END,
    cap: int = config.DOCS_PER_MONTH_CAP,
    refresh: bool = False,
) -> dict:
    """Download PubMed abstracts, one gzipped JSONL shard per month.

    Complete months are skipped so an interrupted run resumes where it
    stopped.  Returns a summary dict with per-month counts and failures.
    """
    months = cio.month_iter(start, end)
    summary = {
        "corpus": "pubmed",
        "start": start,
        "end": end,
        "cap": cap,
        "months": len(months),
        "built": 0,
        "skipped": 0,
        "records": 0,
        "bytes": 0,
        "per_month": [],
        "errors": [],
        "dropped": {},
        "date_precision": {},
    }

    for month in months:
        if not refresh and cio.shard_is_complete("pubmed", month):
            summary["skipped"] += 1
            print("[pubmed] %s  skip (shard complete)" % month, flush=True)
            continue
        try:
            records, stats = _month_records(month, cap)
        except Exception as exc:  # noqa: BLE001 - report and continue, resumable
            summary["errors"].append({"month": month, "error": repr(exc)})
            print("[pubmed] %s  FAILED: %r" % (month, exc), flush=True)
            continue

        if not records:
            summary["errors"].append({"month": month, "error": "zero records returned"})
            print(
                "[pubmed] %s  FAILED: zero records (hitCount=%s)"
                % (month, stats["hit_count"]),
                flush=True,
            )
            continue

        path = cio.shard_path("pubmed", month)
        count = cio.write_jsonl_gz(path, records)
        size = path.stat().st_size
        summary["built"] += 1
        summary["records"] += count
        summary["bytes"] += size
        summary["per_month"].append({"month": month, "records": count, "bytes": size})
        for key, value in stats["dropped"].items():
            summary["dropped"][key] = summary["dropped"].get(key, 0) + value
        for key, value in stats["precision"].items():
            summary["date_precision"][key] = summary["date_precision"].get(key, 0) + value
        approx = stats["precision"].get("month", 0)
        print(
            "[pubmed] %s  records=%d  bytes=%d  hitCount=%d  requests=%d%s"
            % (
                month,
                count,
                size,
                stats["hit_count"],
                stats["requests"],
                ("  month-precision-dates=%d" % approx) if approx else "",
            ),
            flush=True,
        )

    return summary
