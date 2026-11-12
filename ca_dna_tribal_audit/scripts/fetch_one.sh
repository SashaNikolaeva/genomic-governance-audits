#!/bin/bash
# Usage: fetch_one.sh OUTDIR PMCID  (downloads one Europe PMC full-text XML)
f="$1/$2.xml"
if [ -s "$f" ] && [ "$(stat -f%z "$f")" -gt 1000 ]; then exit 0; fi
curl -s --retry 3 --max-time 90 -o "$f" "https://www.ebi.ac.uk/europepmc/webservices/rest/$2/fullTextXML"
if [ "$(stat -f%z "$f" 2>/dev/null || echo 0)" -lt 1000 ]; then echo "small/failed: $2"; rm -f "$f"; fi
