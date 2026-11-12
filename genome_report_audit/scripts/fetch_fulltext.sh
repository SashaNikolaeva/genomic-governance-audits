#!/bin/bash
# Download Europe PMC full-text XML for every PMCID in the given *_lite.json files.
# Usage: fetch_fulltext.sh OUTDIR lite1.json [lite2.json ...]
OUT="$1"; shift; mkdir -p "$OUT"
python3 -I -c '
import json,sys
ids=set()
for f in sys.argv[1:]:
    for r in json.load(open(f))["resultList"]["result"]:
        if r.get("pmcid"): ids.add(r["pmcid"])
print("\n".join(sorted(ids)))' "$@" | while read -r id; do
  f="$OUT/$id.xml"
  [ -s "$f" ] && [ "$(stat -f%z "$f")" -gt 1000 ] && continue
  curl -s --retry 3 --max-time 60 -o "$f" "https://www.ebi.ac.uk/europepmc/webservices/rest/$id/fullTextXML"
  [ "$(stat -f%z "$f" 2>/dev/null || echo 0)" -lt 1000 ] && { echo "small/failed: $id"; rm -f "$f"; }
  sleep 0.3
done
echo "files: $(ls "$OUT" | wc -l)"
