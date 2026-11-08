"""NVD CVE description corpus - the negative-control corpus.

CVE descriptions are short, templated security prose written by vendors and
coordinators.  They are not plausibly mass-produced with an LLM, so a rise in
the LLM-style index here would falsify the method rather than support the
hypothesis.
"""

import time

import requests

from .. import config
from . import io


def _fetch_window(start_iso: str, end_iso: str, want: int):
    collected = []
    start_index = 0
    while len(collected) < want:
        try:
            r = requests.get(
                "https://services.nvd.nist.gov/rest/json/cves/2.0",
                params={
                    "pubStartDate": start_iso,
                    "pubEndDate": end_iso,
                    "resultsPerPage": 2000,
                    "startIndex": start_index,
                },
                headers={"User-Agent": config.USER_AGENT},
                timeout=60,
            )
        except Exception as exc:  # noqa: BLE001
            print("  ! nvd request failed: %r" % (exc,), flush=True)
            break
        if r.status_code != 200:
            print("  ! nvd HTTP %s" % r.status_code, flush=True)
            break
        payload = r.json()
        vulns = payload.get("vulnerabilities", [])
        if not vulns:
            break
        collected.extend(vulns)
        start_index += payload.get("resultsPerPage", len(vulns))
        if start_index >= payload.get("totalResults", 0):
            break
        time.sleep(6.5)  # courtesy pause: unauthenticated limit is ~5 req / 30 s
    return collected[:want]


def _english_description(cve: dict) -> str:
    for desc in cve.get("descriptions", []):
        if desc.get("lang") == "en":
            return (desc.get("value") or "").strip()
    return ""


def build(start: str = None, end: str = None, cap: int = config.DOCS_PER_MONTH_CAP) -> int:
    months = io.month_iter(start or config.WINDOW_START, end or config.WINDOW_END)
    total = 0
    for month in months:
        if io.shard_is_complete("nvd", month, min_records=20):
            continue
        first, last = io.month_bounds(month)
        records = []
        for vuln in _fetch_window(first + "T00:00:00.000", last + "T23:59:59.999", cap):
            cve = vuln.get("cve", {})
            text = _english_description(cve)
            if len(text) < 40:
                continue
            records.append(
                {
                    "id": cve.get("id", ""),
                    "date": (cve.get("published") or "")[:10],
                    "text": text,
                    "meta": {"source": "nvd"},
                }
            )
        io.write_jsonl_gz(io.shard_path("nvd", month), records)
        total += len(records)
        print("[nvd] %s %d docs" % (month, len(records)), flush=True)
        time.sleep(1.0)
    return total
