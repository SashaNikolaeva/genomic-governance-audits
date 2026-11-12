#!/bin/bash
# Page through the Europe PMC population query (full text available) and save all records.
# Usage: fetch_population.sh OUT.json
OUT="$1"; E="https://www.ebi.ac.uk/europepmc/webservices/rest/search"
P='(TITLE:"California" OR ABSTRACT:"California") AND ABSTRACT:(sequenc* OR genom* OR genotyp* OR "DNA barcoding" OR metabarcod* OR "environmental DNA" OR eDNA OR microsatellite* OR phylogeograph* OR "population genetic*" OR "population genomic*" OR "conservation genetic*" OR "landscape genetic*" OR RADseq OR "RAD-seq" OR SNPs) AND ABSTRACT:(species OR populations OR wildlife OR plants OR fish OR birds OR insects OR ecosystem OR habitat OR conservation OR ecology OR ecological OR marine OR forest OR watershed OR endemic) NOT ABSTRACT:(patients OR patient OR clinical OR hospital OR cancer OR tumor OR "human genome" OR GWAS OR "case-control" OR participants OR "human subjects" OR cohort) AND (PUB_YEAR:[2011 TO 2026]) AND (HAS_FT:Y)'
cursor="*"; : > "$OUT.pages"
for i in 1 2 3 4 5; do
  curl -s -G "$E" --data-urlencode "query=$P" --data-urlencode "resultType=lite" --data-urlencode "pageSize=1000" --data-urlencode "format=json" --data-urlencode "cursorMark=$cursor" -o "page$i.json"
  n=$(python3 -I -c 'import json,sys; d=json.load(open(sys.argv[1])); print(len(d["resultList"]["result"]))' "page$i.json")
  next=$(python3 -I -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get("nextCursorMark",""))' "page$i.json")
  echo "page $i: $n records"; echo "page$i.json" >> "$OUT.pages"
  [ "$n" -lt 1000 ] && break; [ -z "$next" ] && break; cursor="$next"
done
python3 -I - "$OUT" $(cat "$OUT.pages") <<'PY'
import json,sys
out=sys.argv[1]; res=[]; seen=set()
for f in sys.argv[2:]:
    for r in json.load(open(f))["resultList"]["result"]:
        k=r.get("pmcid") or r.get("id")
        if k in seen: continue
        seen.add(k); res.append(r)
json.dump({"hitCount":len(res),"resultList":{"result":res}},open(out,"w"))
print("population records:",len(res),"with pmcid:",sum(1 for r in res if r.get("pmcid")))
PY
rm -f page*.json "$OUT.pages"
