#!/usr/bin/env python3
"""Fast, resumable acquisition of the two scholarly corpora.

Design notes
------------
The arXiv API is rate-limited and punishes per-category queries with long
backoffs, so we use **two OR-queries per month** instead of one query per
category:

    Q1  cs.CL | cs.LG | cs.AI | stat.ML          (AI/CS)
    Q2  math.NT | math.CO | hep-th | cond-mat.stat-mech   (maths/physics)

That is ~190 requests for the whole window rather than ~750, which keeps us
inside the politeness budget.  The per-document primary category is stored in
``meta`` so field heterogeneity can still be analysed later.

Europe PMC needs a single cursor-paged query per month.

Usage:  ./.venv/bin/python scripts/fetch_scholarly.py [arxiv|pubmed|all]
"""

import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import config  # noqa: E402
from src.corpora import io as ciro  # noqa: E402

ATOM = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
ARXIV_URL = "https://export.arxiv.org/api/query"
EPMC_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

QUERIES = {
    # One combined query per month. The arXiv API throttles aggressively and
    # each extra query per month roughly doubles both wall time and 429 risk.
    "combined": (
        "(cat:cs.CL OR cat:cs.LG OR cat:cs.AI OR cat:stat.ML "
        "OR cat:math.NT OR cat:math.CO OR cat:hep-th OR cat:cond-mat.stat-mech)"
    ),
}


def _get(url, params, retries=4, timeout=90):
    delay = 4.0
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, headers={"User-Agent": config.USER_AGENT}, timeout=timeout)
            if resp.status_code == 200:
                return resp
            if resp.status_code in (429, 503):
                wait = min(delay * (attempt + 1), 45)
                print("    throttled (%s), waiting %.0fs" % (resp.status_code, wait), flush=True)
                time.sleep(wait)
                continue
        except Exception as exc:  # noqa: BLE001
            print("    request error: %r" % (exc,), flush=True)
        time.sleep(delay)
    return None


def _month_window(month: str):
    first, last = ciro.month_bounds(month)
    return first.replace("-", "") + "0000", last.replace("-", "") + "2359"


def fetch_arxiv(months, cap=config.DOCS_PER_MONTH_CAP):
    for month in months:
        if ciro.shard_is_complete("arxiv", month, min_records=100):
            continue
        lo, hi = _month_window(month)
        records, seen = [], set()
        per_query = max(cap // len(QUERIES), 100)
        for name, base in QUERIES.items():
            query = "%s AND submittedDate:[%s TO %s]" % (base, lo, hi)
            resp = _get(ARXIV_URL, {"search_query": query, "max_results": per_query,
                                    "sortBy": "submittedDate", "sortOrder": "descending"})
            if resp is None:
                continue
            try:
                root = ET.fromstring(resp.content)
            except ET.ParseError:
                continue
            for entry in root.findall("a:entry", ATOM):
                ident = (entry.findtext("a:id", default="", namespaces=ATOM) or "").strip()
                if not ident or ident in seen:
                    continue
                seen.add(ident)
                published = entry.findtext("a:published", default="", namespaces=ATOM) or ""
                summary = (entry.findtext("a:summary", default="", namespaces=ATOM) or "").strip()
                if len(summary) < 60:
                    continue
                prim = entry.find("arxiv:primary_category", ATOM)
                records.append({
                    "id": ident.rsplit("/", 1)[-1],
                    "date": published[:10],
                    "text": " ".join(summary.split()),
                    "meta": {"source": "arxiv", "category": prim.get("term") if prim is not None else name,
                             "title": " ".join((entry.findtext("a:title", default="", namespaces=ATOM) or "").split())},
                })
                if len(records) >= cap:
                    break
            time.sleep(10.0)  # arXiv is strict; 1 request per 10s avoids long 429 backoffs
            if len(records) >= cap:
                break
        ciro.write_jsonl_gz(ciro.shard_path("arxiv", month), records[:cap])
        print("[arxiv] %s %d docs" % (month, len(records[:cap])), flush=True)


def _fetch_pubmed_month(month, cap=config.DOCS_PER_MONTH_CAP):
    """Fetch one month of biomedical abstracts from Europe PMC."""
    if ciro.shard_is_complete("pubmed", month, min_records=100):
        return 0
    year, mon = month.split("-")
    first, last = ciro.month_bounds(month)
    records, cursor = [], "*"
    while len(records) < cap and cursor:
        params = {
            # FIRST_PDATE range is the reliable filter; PUB_MONTH / HAS_ABS are
            # not valid field names in the Europe PMC query grammar.
            "query": "FIRST_PDATE:[%s TO %s] AND SRC:MED AND HAS_ABSTRACT:Y" % (first, last),
            "format": "json",
            "pageSize": min(1000, cap - len(records)),
            "resultType": "core",
            "cursorMark": cursor,
        }
        resp = _get(EPMC_URL, params, timeout=60)
        if resp is None:
            break
        try:
            payload = resp.json()
        except Exception:  # noqa: BLE001
            break
        results = payload.get("resultList", {}).get("result", [])
        if not results:
            break
        for item in results:
            abstract = (item.get("abstractText") or "").strip()
            if len(abstract) < 80:
                continue
            date = item.get("firstPublicationDate") or item.get("electronicPublicationDate") or ""
            if not date or len(date) < 10:
                date = "%s-%s-15" % (year, mon)
            records.append({
                "id": str(item.get("id", "")),
                "date": date[:10],
                "text": " ".join(abstract.split()),
                "meta": {"source": "europepmc", "category": "biomed",
                         "journal": (item.get("journalInfo", {}) or {}).get("journal", {}).get("title", ""),
                         "title": (item.get("title") or "").strip()},
            })
        next_cursor = payload.get("nextCursorMark")
        if not next_cursor or next_cursor == cursor:
            break
        cursor = next_cursor
    ciro.write_jsonl_gz(ciro.shard_path("pubmed", month), records[:cap])
    print("[pubmed] %s %d docs" % (month, len(records[:cap])), flush=True)
    return len(records[:cap])


def fetch_pubmed(months, cap=config.DOCS_PER_MONTH_CAP, workers=6):
    """Fetch all months concurrently (distinct hosts/files, so this is safe)."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    total = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_fetch_pubmed_month, m, cap): m for m in months}
        for future in as_completed(futures):
            try:
                total += future.result()
            except Exception as exc:  # noqa: BLE001
                print("  ! pubmed month failed: %r" % (exc,), flush=True)
    return total


def main() -> int:
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    months = ciro.month_iter()
    print("[scholarly] %d months, %s .. %s" % (len(months), config.WINDOW_START, config.WINDOW_END), flush=True)
    # Europe PMC is fast and reliable, so it goes first: it secures one complete
    # corpus before the slow, rate-limited arXiv pass begins.
    if which in ("pubmed", "all"):
        fetch_pubmed(months)
    if which in ("arxiv", "all"):
        fetch_arxiv(months)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
