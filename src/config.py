"""Shared configuration for The AI Prose Clock."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CACHE = DATA / "cache"
RAW = DATA / "raw"
ANALYSIS = ROOT / "analysis"
FIGURES = ROOT / "figures"
PAPER = ROOT / "paper"

# Study window: ChatGPT public release is 2022-11-30, so the pre-period ends 2022-10.
WINDOW_START = "2019-01"
WINDOW_END = "2026-10"
PRE_END = "2022-10"          # last month treated as pre-treatment
POST_START = "2022-11"       # first month treated as post-treatment

DOCS_PER_MONTH_CAP = 1000

CORPORA = ["arxiv", "pubmed", "hackernews", "edgar", "nvd"]

USER_AGENT = (
    "AIProseClock/0.1 (https://github.com/AhmedJaffar/ai-prose-clock; "
    "research; contact: ahmedjaffar.ca)"
)

API_SLEEP = 0.4
MAX_WORKERS = 4
