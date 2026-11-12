#!/usr/bin/env python3
"""Screen the included genome reports for the land tenure / management type of the
sampling site. Writes results/land_type_auto.csv with one row per report: provisional
category, the cue terms found, and snippets for hand verification.

Usage: score_land_type.py XMLDIR scores_final.csv OUTCSV
Categories (provisional, from the paper's own words in the sampling section):
  federal_public      National Park/Forest/Monument/Seashore/Wildlife Refuge, BLM, NOAA sanctuary, military
  state_public        State Park/Beach/Reserve/Forest, CDFW wildlife area / ecological reserve, state MPA
  local_public        county/city/regional park, open-space or water district
  university_reserve  UC Natural Reserve System, field station, campus, university garden
  private_land        private property, ranch, land trust, Nature Conservancy preserve
  tribal_land         reservation, rancheria, Tribal land
  captive_cultivated  aquarium, zoo, hatchery, aquaculture, culture collection, nursery, bred colony, market
  marine_waters       sea/bay/coast with no named managed unit
  unspecified         locality named but tenure not stated / no locality
"""
import sys, re, csv, pathlib
from xml.etree import ElementTree as ET
sys.path.insert(0, str(pathlib.Path(__file__).parent))

xmldir, finalcsv, outcsv = map(pathlib.Path, sys.argv[1:4])

CUES = {
 "federal_public": re.compile(r"\b(National (?:Park|Forest|Monument|Seashore|Wildlife Refuge|Recreation Area|Grassland|Marine Sanctuary|Estuarine Research Reserve|Wild and Scenic River|Conservation Area)s?|"
     r"National Park Service|\bNPS\b|U\.?S\.? Forest Service|USFS|Bureau of Land Management|\bBLM\b|U\.?S\.? Fish and Wildlife Service|USFWS|"
     r"Wildlife Refuge|Bureau of Reclamation|Army Corps|Naval|Air Force|Marine Corps|Camp Pendleton|Vandenberg|Fort [A-Z]\w+|Department of Defense|"
     r"NOAA|Channel Islands|Death Valley|Joshua Tree|Yosemite|Sequoia|Kings Canyon|Lassen|Redwood National|Pinnacles|Point Reyes|Golden Gate National|Mojave National|"
     r"Parks Canada|National Park of|Nationalpark|Parque Nacional|Reserva Nacional|Department of Conservation|\bDOC\b)\b"),
 "state_public": re.compile(r"\b(State (?:Park|Beach|Reserve|Forest|Recreation Area|Marine (?:Reserve|Conservation Area|Park)|Natural Reserve|Wildlife Area|Historic Park|Game Refuge)s?|"
     r"California (?:Department of Parks|State Parks)|California Department of Fish and Wildlife|\bCDFW\b|Wildlife Area|Ecological Reserve|"
     r"Marine Protected Area|\bMPA\b|Department of Fish and (?:Wildlife|Game)|Provincial Park|state[- ]owned|state land)\b"),
 "local_public": re.compile(r"\b(Regional Park|County Park|City Park|Open Space (?:Preserve|District|Authority)|Regional Open Space|Park District|Water District|Municipal|"
     r"Metropolitan Water|Flood Control|County (?:Parks|Department)|Botanic(?:al)? Garden|Arboretum|public park)\b"),
 "university_reserve": re.compile(r"\b(Natural Reserve System|\bNRS\b|UC Natural Reserve|(?:Natural|Biological|Field|Research|Ecological) (?:Reserve|Station|Reservation)|Field Station|Marine Laboratory|Marine Station|"
     r"Hastings|Blue Oak Ranch|Sagehen|Angelo Coast|Bodega Marine|Jepson Prairie|Sedgwick|Jasper Ridge|McLaughlin|Quail Ridge|Stebbins|Boyd Deep Canyon|Sweeney Granite|"
     r"Younger Lagoon|Año Nuevo|Fort Ord Natural|Landels-Hill|Big Creek Reserve|Santa Cruz Island Reserve|Kenneth S\. Norris|Rancho Marino|Carpinteria Salt|Coal Oil Point|"
     r"Elliott Chaparral|Scripps Coastal|Dawson Los Monos|Motte Rimrock|James (?:San Jacinto|Reserve)|Emerson Oaks|Burns Piñon|Steele/Burnand|Valentine|Sierra Nevada Aquatic|"
     r"White Mountain Research|Chickering|Eagle Lake Field|Point Reyes Field|Bodega Bay|Hopland|Sierra Foothill|Blodgett|Whitaker|campus(?: of)?|University (?:of )?[A-Z]\w+ (?:campus|grounds|property|reserve|garden|greenhouse))\b"),
 "private_land": re.compile(r"\b(private (?:land|property|ranch|landowner|lands|properties|residence|garden|yard)s?|privately[- ]owned|landowner\w*|land ?owner\w*|The Nature Conservancy|\bTNC\b|Land Trust|Conservancy|Audubon|"
     r"ranch(?!o Marino)\w*|farm\w*|vineyard|orchard|backyard|residential|homeowner)\b", re.I),
 "tribal_land": re.compile(r"\b(Reservation(?! Road)|Rancheria|Tribal (?:land|lands|territory|property|trust)|Indian (?:land|lands|Reservation)|tribally[- ]owned|Pueblo of|First Nation (?:land|territory|reserve)|iwi)\b"),
 "captive_cultivated": re.compile(r"\b(aquarium|zoo\b|zoological|hatchery|aquaculture|mariculture|cultur(?:e|ed) (?:collection|strain|line)|culture collection|ATCC|CCAP|nursery|greenhouse|glasshouse|growth chamber|captive(?:-bred|ly)?|captivity|"
     r"laboratory (?:colony|population|strain|stock|culture|reared)|lab(?:oratory)?-reared|bred in|colony maintained|breeding (?:colony|program|facility)|stock cent(?:er|re)|germplasm|seed bank|"
     r"botanic(?:al)? garden|arboretum|cultivar|cultivated|commercial (?:supplier|source|vendor)|purchased|fish market|supermarket|pet (?:trade|store)|museum specimen|herbarium|rehabilitation cent(?:er|re)|wildlife (?:hospital|rehabilitation|center))\b", re.I),
 "marine_waters": re.compile(r"\b(offshore|open ocean|coastal waters|territorial waters|nearshore|intertidal|subtidal|kelp forest|reef|\bbay\b|sound\b|strait|gulf|sea\b|ocean|fjord|continental shelf|at a depth|depth of|trawl|dredge|SCUBA|dive|snorkel|tide ?pool|rocky shore|shoreline)\b", re.I),
}

def txt(el): return " ".join("".join(el.itertext()).split()) if el is not None else ""
def materials(root):
    mat = meth = ""
    for s in root.iter("sec"):
        t = txt(s.find("title")).lower()
        if t.startswith("method") or "materials and methods" in t: meth += " " + txt(s)
        if any(k in t for k in ("biological material", "sample", "specimen", "collection", "tissue", "sampling", "study organism", "study species", "voucher", "nomenclature")):
            mat += " " + txt(s)
    ack = " ".join(txt(a) for a in root.iter("ack"))
    return (mat or meth or txt(root)), ack

def snippets(rx, s, n=4, w=120):
    res, seen = [], set()
    for m in rx.finditer(s):
        k = m.group(0).lower()
        if k in seen: continue
        seen.add(k); a, b = max(0, m.start()-w), min(len(s), m.end()+w)
        res.append("…" + s[a:b] + "…")
        if len(res) >= n: break
    return res

PRIORITY = ["tribal_land", "university_reserve", "federal_public", "state_public", "local_public", "private_land", "captive_cultivated", "marine_waters"]
rows = []
for r in csv.DictReader(open(finalcsv)):
    f = xmldir / f"{r['pmcid']}.xml"
    root = ET.parse(f).getroot()
    mat, ack = materials(root)
    o = {"pmcid": r["pmcid"], "stratum": r["stratum"], "year": r["year"], "title": r["title"]}
    found = {}
    for k, rx in CUES.items():
        sn = snippets(rx, mat)
        if not sn and k in ("federal_public", "state_public", "university_reserve", "private_land", "tribal_land"):
            sn = snippets(rx, ack, n=2)          # permits/thanks in acknowledgements name the manager
        if sn: found[k] = sn
    o["cues"] = ";".join(found)
    o["auto_land_type"] = next((k for k in PRIORITY if k in found), "unspecified")
    for k in CUES: o[k + "_snippets"] = " | ".join(found.get(k, []))
    o["materials_excerpt"] = mat[:900]
    rows.append(o)
with open(outcsv, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
from collections import Counter
for s in ("CCGP", "EBP-other"):
    print(s, Counter(o["auto_land_type"] for o in rows if o["stratum"] == s))
