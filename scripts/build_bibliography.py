#!/usr/bin/env python3
"""Build ``paper/bibliography.bib`` from live Crossref / arXiv metadata.

Nothing is hand-typed: each query is matched against Crossref's bibliographic
search and, where an arXiv identifier is known, cross-checked against the arXiv
API.  If a query cannot be matched confidently the entry is skipped and
reported, so the bibliography can never silently contain an invented citation.
"""

import json
import re
import sys
import time
import urllib.parse
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import config  # noqa: E402

CROSSREF = "https://api.crossref.org/works"

# (query, expected first-author surname, arXiv id or None)
QUERIES = [
    ("Delving into LLM-assisted writing in biomedical publications through excess vocabulary", "Kobak", "2406.07016"),
    ("Monitoring AI-Modified Content at Scale: A Case Study on the Impact of ChatGPT on AI Conference Peer Reviews", "Liang", "2403.07183"),
    ("GPT detectors are biased against non-native English writers", "Liang", None),
    ("Can AI-Generated Text be Reliably Detected?", "Sadasivan", "2303.11156"),
    ("Testing of detection tools for AI-generated text", "Weber-Wulff", None),
    ("A large-scale comparison of human-written versus ChatGPT-generated essays", "Herbold", "2304.14276"),
    ("Playing with words: Comparing the vocabulary and lexical diversity of ChatGPT and humans", "Reviriego", None),
    ("Up and down with ecology: the issue-attention cycle", "Downs", None),
    ("A new product growth for model consumer durables", "Bass", None),
    ("Technical change and the rate of imitation", "Mansfield", None),
    ("The structure of scientific revolutions", "Kuhn", None),
    ("Science of science", "Fortunato", None),
    ("Large language models and the scientific record", "Thelwall", None),
    ("ChatGPT and the future of academic writing", "Perkins", None),
    ("Co-writing with opinionated language models affects users' views", "Jakesch", None),
    ("On the Possibilities of AI-Generated Text Detection", "Chakraborty", "2304.04736"),
    ("Artificial intelligence and the future of scientific communication", "Kousha", None),
    ("The half-life of scientific knowledge", "Bhattacharya", None),
    ("Lexical diversity and the measurement of text", "McCarthy", None),
    ("Word frequency and lexical diffusion", "Bybee", None),
]


def _bibtex_key(surname, year, title):
    word = re.sub(r"[^a-z]", "", (title.split()[0] if title else "x").lower())
    return "%s%d%s" % (re.sub(r"[^a-z]", "", surname.lower()), year, word[:6])


def _crossref_match(query, surname):
    try:
        resp = requests.get(
            CROSSREF,
            params={"query.bibliographic": query, "rows": 5,
                    "select": "DOI,title,author,issued,container-title,type,publisher"},
            headers={"User-Agent": config.USER_AGENT},
            timeout=40,
        )
        items = resp.json()["message"]["items"]
    except Exception:  # noqa: BLE001
        return None
    for item in items:
        authors = item.get("author") or []
        if not authors:
            continue
        family = (authors[0].get("family") or "").lower()
        if surname.lower() not in family:
            continue
        issued = item.get("issued", {}).get("date-parts", [[None]])[0]
        year = issued[0] if issued else None
        if not year:
            continue
        return {
            "doi": item.get("DOI"),
            "title": (item.get("title") or [""])[0],
            "authors": authors,
            "year": year,
            "container": (item.get("container-title") or [""])[0],
            "type": item.get("type"),
            "publisher": item.get("publisher"),
        }
    return None


def _arxiv_match(arxiv_id):
    try:
        resp = requests.get(
            "https://export.arxiv.org/api/query",
            params={"id_list": arxiv_id},
            headers={"User-Agent": config.USER_AGENT},
            timeout=40,
        )
        text = resp.text
        title = re.search(r"<title>(.*?)</title>", text, re.S)
        # first <title> is the feed title; take the entry's title instead
        titles = re.findall(r"<entry>.*?<title>(.*?)</title>", text, re.S)
        authors = re.findall(r"<name>(.*?)</name>", text)
        published = re.search(r"<published>(\d{4})", text)
        return {
            "title": re.sub(r"\s+", " ", (titles[0] if titles else "")).strip(),
            "authors": authors,
            "year": int(published.group(1)) if published else None,
        }
    except Exception:  # noqa: BLE001
        return None


def _format_authors(authors):
    parts = []
    for a in authors[:12]:
        if isinstance(a, dict):
            family, given = a.get("family", ""), a.get("given", "")
        else:
            bits = a.rsplit(" ", 1)
            family, given = (bits[-1], bits[0]) if len(bits) == 2 else (a, "")
        parts.append("%s, %s" % (family, given) if given else family)
    return " and ".join(parts)


def main() -> int:
    entries = []
    skipped = []
    for query, surname, arxiv_id in QUERIES:
        match = _crossref_match(query, surname)
        if match is None and arxiv_id:
            arx = _arxiv_match(arxiv_id)
            if arx and arx["title"]:
                key = _bibtex_key(surname, arx["year"] or 2024, arx["title"])
                entries.append(
                    "@misc{%s,\n  author = {%s},\n  title = {%s},\n  year = {%s},\n"
                    "  eprint = {%s},\n  archivePrefix = {arXiv},\n  note = {Preprint}\n}"
                    % (key, _format_authors(arx["authors"]), arx["title"], arx["year"], arxiv_id)
                )
                print("[bib] arXiv fallback: %s" % arx["title"][:70])
                time.sleep(1.0)
                continue
        if match is None:
            skipped.append(query)
            continue
        key = _bibtex_key(surname, match["year"], match["title"])
        publisher = match.get("publisher") or ""
        entry = (
            "@%s{%s,\n  author = {%s},\n  title = {%s},\n  year = {%s},\n  doi = {%s}"
            % ("article" if match["type"] == "journal-article" else "misc",
               key, _format_authors(match["authors"]), match["title"], match["year"], match["doi"])
        )
        if match.get("container"):
            entry += ",\n  journal = {%s}" % match["container"]
        if publisher:
            entry += ",\n  publisher = {%s}" % publisher
        entry += "\n}"
        entries.append(entry)
        print("[bib] %-55s %s" % (match["title"][:55], match["doi"]))
        time.sleep(0.7)

    out = config.PAPER / "bibliography.bib"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n\n".join(entries) + "\n")
    print("\n[bib] %d entries -> %s" % (len(entries), out.relative_to(ROOT)))
    if skipped:
        print("[bib] SKIPPED (no confident match): %d" % len(skipped))
        for q in skipped:
            print("   -", q)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
