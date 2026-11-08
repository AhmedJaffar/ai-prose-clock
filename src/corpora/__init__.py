"""Corpus acquisition modules.

Each module exposes a ``build(start, end, cap)`` function that writes one
gzipped JSONL shard per month containing at least the keys::

    {"id": str, "date": "YYYY-MM-DD", "text": str, "meta": {...}}

Shards are written through :mod:`src.corpora.io` so that every corpus on disk
has an identical layout and the feature extractor can be corpus-agnostic.
"""
