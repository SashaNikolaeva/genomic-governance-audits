#!/usr/bin/env python3
"""Download Europe PMC full-text XML for every PMCID in one or more *_lite.json
search results. Usage: fetch_fulltext.py OUTDIR lite1.json [lite2.json ...]"""
import json, sys, time, urllib.request, pathlib
out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
ids = {}
for f in sys.argv[2:]:
    for r in json.load(open(f))["resultList"]["result"]:
        if r.get("pmcid"): ids[r["pmcid"]] = r
done = skipped = failed = 0
for pmcid in sorted(ids):
    p = out / f"{pmcid}.xml"
    if p.exists() and p.stat().st_size > 1000: skipped += 1; continue
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
    try:
        with urllib.request.urlopen(url, timeout=60) as h: data = h.read()
        if len(data) < 500: failed += 1; print("empty", pmcid); continue
        p.write_bytes(data); done += 1
    except Exception as e:
        failed += 1; print("fail", pmcid, e)
    time.sleep(0.4)
print(f"downloaded {done}, already had {skipped}, failed {failed}, total ids {len(ids)}")
