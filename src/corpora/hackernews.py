"""Hacker News comment corpus via the Algolia HN search API.

Algolia caps the number of results reachable per query, so each month is split
into sub-windows (roughly weekly) and sampled across the whole month rather than
taking only the most recent comments.
"""

import re
import time
from datetime import datetime, timezone

import requests

from .. import config
from . import io

TAG_RE = re.compile(r"<[^>]+>")


def _clean(html: str) -> str:
    text = TAG_RE.sub(" ", html or "")
    for entity, char in (("&#x27;", "'"), ("&quot;", '"'), ("&amp;", "&"),
                         ("&lt;", "<"), ("&gt;", ">"), ("&#x2F;", "/")):
        text = text.replace(entity, char)
    return re.sub(r"\s+", " ", text).strip()


def _fetch_window(start_ts: int, end_ts: int, want: int):
    collected = []
    for page in range(0, 6):
        if len(collected) >= want:
            break
        try:
            r = requests.get(
                "https://hn.algolia.com/api/v1/search_by_date",
                params={
                    "tags": "comment",
                    "numericFilters": "created_at_i>%d,created_at_i<%d" % (start_ts, end_ts),
                    "hitsPerPage": 200,
                    "page": page,
                },
                headers={"User-Agent": config.USER_AGENT},
                timeout=30,
            )
        except Exception as exc:  # noqa: BLE001
            print("  ! hn request failed: %r" % (exc,), flush=True)
            break
        if r.status_code != 200:
            print("  ! hn HTTP %s" % r.status_code, flush=True)
            break
        hits = r.json().get("hits", [])
        if not hits:
            break
        collected.extend(hits)
        if len(hits) < 200:
            break
        time.sleep(0.25)
    return collected[:want]


def build(start: str = None, end: str = None, cap: int = config.DOCS_PER_MONTH_CAP) -> int:
    months = io.month_iter(start or config.WINDOW_START, end or config.WINDOW_END)
    total = 0
    for month in months:
        if io.shard_is_complete("hackernews", month, min_records=100):
            continue
        first, _last = io.month_bounds(month)
        t0 = int(datetime.strptime(first, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp())
        t1 = t0 + 30 * 86400

        n_windows = 5
        span = (t1 - t0) // n_windows
        records = []
        for k in range(n_windows):
            if len(records) >= cap:
                break
            want = max(1, (cap - len(records)) // (n_windows - k))
            for hit in _fetch_window(t0 + k * span, t0 + (k + 1) * span, want):
                text = _clean(hit.get("comment_text"))
                if len(text) < 60:
                    continue
                records.append(
                    {
                        "id": str(hit.get("objectID")),
                        "date": (hit.get("created_at") or "")[:10],
                        "text": text,
                        "meta": {"source": "hn", "story": hit.get("story_title")},
                    }
                )
        io.write_jsonl_gz(io.shard_path("hackernews", month), records)
        total += len(records)
        print("[hn] %s %d docs" % (month, len(records)), flush=True)
    return total
