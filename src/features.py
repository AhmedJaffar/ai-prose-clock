"""Document-level feature extraction for The AI Prose Clock.

Two kinds of quantity are produced:

* **Per-document features** (this module) - token counts, typographic habits,
  formulaic phrases, sentence statistics, and counts of a fixed marker list.
  These are small enough to store for every document and are what allows
  document-level bootstrap confidence intervals.
* **Monthly vocabulary counts** (``src/excess.py``) - the large aggregate used
  for excess-vocabulary discovery.

The tokeniser is deliberately simple and language-agnostic-by-default: the
corpora analysed here are overwhelmingly English, and a fixed regex keeps the
features reproducible across machines without a heavyweight NLP dependency.
"""

import re
from collections import Counter
from typing import Dict, Iterable, List

WORD_RE = re.compile(r"[a-z]+(?:'[a-z]+)?")
SENT_RE = re.compile(r"[.!?]+")

# Multi-word formulaic patterns frequently over-represented in LLM prose.
MULTIWORD_PATTERNS = {
    "mw_not_only_but_also": re.compile(r"\bnot only\b[^.!?]{0,120}\bbut also\b"),
    "mw_it_is_important_to_note": re.compile(r"\bit is important to note\b"),
    "mw_it_is_worth_noting": re.compile(r"\bit is worth noting\b"),
    "mw_in_todays": re.compile(r"\bin today's\b"),
    "mw_plays_a_crucial_role": re.compile(r"\bplays a crucial role\b"),
    "mw_a_testament_to": re.compile(r"\ba testament to\b"),
    "mw_in_the_realm_of": re.compile(r"\bin the realm of\b"),
    "mw_serves_as_a": re.compile(r"\bserves as a\b"),
    "mw_delve_into": re.compile(r"\bdelve into\b"),
}


def word_tokens(text: str) -> List[str]:
    """Lowercased alphabetic-ish tokens (apostrophes retained)."""
    return WORD_RE.findall(text.lower())


def typography_counts(text: str) -> Dict[str, int]:
    """Direct string counts for typographic markers (cheap, no regex)."""
    return {
        "em_dash": text.count("\u2014"),
        "en_dash": text.count("\u2013"),
        "curly_open": text.count("\u201c"),
        "curly_close": text.count("\u201d"),
        "semicolon": text.count(";"),
        "colon": text.count(":"),
        "paren_open": text.count("("),
        "bullet_dash": len(re.findall(r"(?m)^\s*[-*]\s+", text)),
        "numbered_list": len(re.findall(r"(?m)^\s*\d+[.)]\s+", text)),
    }


def sentence_stats(tokens: List[str], text: str) -> Dict[str, float]:
    """Mean sentence length, dispersion, and type-token ratio."""
    n_tokens = len(tokens)
    sentences = [s for s in SENT_RE.split(text) if s.strip()]
    n_sent = max(len(sentences), 1)
    lengths = [len(WORD_RE.findall(s.lower())) for s in sentences] or [n_tokens]
    mean_len = sum(lengths) / len(lengths) if lengths else 0.0
    var = sum((x - mean_len) ** 2 for x in lengths) / max(len(lengths) - 1, 1)
    return {
        "n_sentences": n_sent,
        "mean_sent_len": mean_len,
        "sd_sent_len": var ** 0.5,
        "ttr": (len(set(tokens)) / n_tokens) if n_tokens else 0.0,
    }


def marker_counts(tokens: List[str], markers: Iterable[str]) -> Dict[str, int]:
    """Counts of the pre-registered marker words in one document."""
    counter = Counter(tokens)
    return {"w_" + m: int(counter.get(m, 0)) for m in markers}


def doc_features(text: str, markers: Iterable[str]) -> Dict[str, object]:
    """All per-document features for one text."""
    tokens = word_tokens(text)
    features: Dict[str, object] = {
        "n_tokens": len(tokens),
        "n_chars": len(text),
    }
    features.update(sentence_stats(tokens, text))
    features.update(typography_counts(text))
    for name, pattern in MULTIWORD_PATTERNS.items():
        features[name] = 1 if pattern.search(text.lower()) else 0
    features.update(marker_counts(tokens, markers))
    return features


def typographic_index(features_row: Dict[str, object]) -> float:
    """A single typographic channel value per 1,000 tokens.

    Deliberately excludes the lexical markers so that the typographic channel
    is independent evidence rather than a re-reading of the same signal.
    """
    n = float(features_row.get("n_tokens", 0) or 0)
    if n <= 0:
        return float("nan")
    per_k = 1000.0 / n
    return per_k * (
        float(features_row.get("em_dash", 0))
        + float(features_row.get("curly_open", 0))
        + 2.0 * float(features_row.get("mw_not_only_but_also", 0))
        + 2.0 * float(features_row.get("mw_it_is_important_to_note", 0))
        + 2.0 * float(features_row.get("mw_it_is_worth_noting", 0))
    )
