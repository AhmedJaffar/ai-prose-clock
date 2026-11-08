#!/usr/bin/env python3
"""Extract per-document features for every available corpus.

Writes ``data/generated/features/<corpus>.csv.gz``, one row per document, with
columns: corpus, id, month, + all features from ``src.features.doc_features``.

Corpora whose raw shards are not yet present are skipped, so this can run
while downloads are still in progress.
"""

import csv
import gzip
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import config, features, wordlists  # noqa: E402
from src.corpora import io as ciro  # noqa: E402

MIN_TOKENS = 20  # discard pathological/empty documents


def available_corpora():
    found = []
    for corpus in config.CORPORA:
        shard_dir = config.RAW / corpus
        if shard_dir.exists() and any(shard_dir.glob("*.jsonl.gz")):
            found.append(corpus)
    return found


def extract_corpus(corpus: str) -> Path:
    out_dir = config.DATA / "generated" / "features"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / ("%s.csv.gz" % corpus)

    rows = 0
    kept = 0
    fieldnames = None
    tmp = out_path.with_suffix(out_path.suffix + ".tmp")

    with gzip.open(tmp, "wt", encoding="utf-8", newline="") as fh:
        writer = None
        for month in ciro.month_iter():
            shard = ciro.shard_path(corpus, month)
            if not shard.exists():
                continue
            for record in ciro.read_jsonl_gz(shard):
                text = record.get("text") or ""
                if len(text) < 80:
                    continue
                feats = features.doc_features(text, wordlists.LLM_MARKERS_PRE)
                if feats["n_tokens"] < MIN_TOKENS:
                    continue
                row = {"corpus": corpus, "id": record.get("id", ""), "month": month}
                row.update(feats)
                if writer is None:
                    fieldnames = list(row.keys())
                    writer = csv.DictWriter(fh, fieldnames=fieldnames)
                    writer.writeheader()
                writer.writerow(row)
                rows += 1
                kept += 1
    if writer is None:
        tmp.unlink(missing_ok=True)
        print("[extract] %-11s no usable documents" % corpus, flush=True)
        return out_path

    tmp.replace(out_path)
    print("[extract] %-11s %d documents" % (corpus, kept), flush=True)
    return out_path


def main() -> int:
    corpora = available_corpora()
    if not corpora:
        print("[extract] no raw corpora present yet", flush=True)
        return 1
    print("[extract] corpora: %s" % ", ".join(corpora), flush=True)
    for corpus in corpora:
        extract_corpus(corpus)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
