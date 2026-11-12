#!/bin/bash
# Parallel download of Europe PMC full-text XML for every PMCID in the given *_lite.json files.
# Usage: fetch_fulltext_parallel.sh OUTDIR lite.json [lite2.json ...]
OUT="$1"; shift; mkdir -p "$OUT"; HERE="$(cd "$(dirname "$0")" && pwd)"
python3 -I -c '
import json,sys
ids=set()
for f in sys.argv[1:]:
    for r in json.load(open(f))["resultList"]["result"]:
        if r.get("pmcid"): ids.add(r["pmcid"])
print("\n".join(sorted(ids)))' "$@" | xargs -P 6 -n 1 bash "$HERE/fetch_one.sh" "$OUT"
echo "DONE files: $(ls "$OUT" | wc -l)"
