#!/usr/bin/env python3
"""Score California non-human DNA papers (Europe PMC JATS XML) on governance criteria.

Usage: score_ca_dna.py XMLDIR population_lite.json OUTDIR
Adds: mou_mentioned (memorandum of understanding/intent, infection-context MOI excluded),
human_subjects (screen-out), california_sampling, nonhuman_organism (inclusion screen).

Criteria (reviewer's rubric):
  1. location_reported   sampling locality given (coordinates and/or named place)
  2. indigenous_lands    Indigenous / Tribal lands, peoples, or a named Nation identified
  3. consultation_care   consultation, Tribal permission, CARE / Indigenous data sovereignty
  4. local_contexts      Local Contexts TK/BC Label or Notice attached
Context columns: permit_mentioned, permit_issuers, us_sampling, california, open_deposition.
Every positive flag carries the matching snippets so a human can verify it.
"""
import sys, re, json, csv, pathlib
from xml.etree import ElementTree as ET

xmldir, pop_json, outdir = map(pathlib.Path, sys.argv[1:4])
outdir.mkdir(parents=True, exist_ok=True)

def meta(f):
    return {r["pmcid"]: r for r in json.load(open(f))["resultList"]["result"] if r.get("pmcid")}
pop = meta(pop_json)

TRIBES = r"""Yurok|Karuk|Karok|Hoopa|Hupa|Tolowa|Wiyot|Pomo|Miwok|Me-Wuk|Mewuk|Ohlone|Muwekma|Esselen|Chumash|Tongva|Gabrielino|
Kumeyaay|Kumiai|Cahuilla|Luise[ñn]o|Quechan|Chemehuevi|Paiute|Shoshone|Achumawi|Atsugewi|Yokuts|Maidu|Konkow|Nisenan|Wintun|Wintu|
Nomlaki|Patwin|Paskenta|Pechanga|Morongo|Viejas|Barona|Sycuan|Iipay|Rincon Band|Soboba|Torres-Martinez|Kashia|Kashaya|Round Valley|
Tule River|Santa Ynez Band|Amah Mutsun|Salinan|Costanoan|Washoe|Mono Lake Kutzadika|Timbisha|Modoc Tribe|Klamath Tribes|Pit River Tribe|
Navajo|Diné|Hopi|Apache|Cherokee|Lakota|Dakota|Ojibwe|Anishinaabe|Haudenosaunee|Seminole|Choctaw|Chickasaw|Tlingit|Haida|Inupiat|
Yup'ik|Kanaka Maoli|Native Hawaiian|M[āa]ori|Aboriginal|Torres Strait|First Nations?|Métis|Inuit|S[áa]mi"""
TRIBES = TRIBES.replace("\n", "")

RX = {
 "indigenous_lands": re.compile(
    r"\b(Tribal|Tribe|Tribes|Indigenous|Native American|Native Nations?|Native peoples?|Native lands?|American Indian|"
    r"ancestral (?:lands?|territor\w+|homelands?)|traditional (?:lands?|territor\w+|homelands?)|unceded|land acknowledg\w+|"
    r"Rancheria|Indian Reservation|(?:[A-Z][\w'-]+ )?Reservation\b(?! (?:Road|Ranch|Point|Creek|Lake|System|Blvd))|"
    r"indigenous (?:peoples?|communit\w+|lands?|nations?|knowledge|data)|(?:" + TRIBES + r"))\b"),
 "consultation_care": re.compile(
    r"\b(consult\w*|CARE [Pp]rinciples|Indigenous [Dd]ata [Ss]overeignty|data sovereignty|FPIC|free,? prior,? and informed consent|"
    r"\bOCAP\b|co-?produc\w+ with|Traditional (?:Ecological )?Knowledge|benefit[- ]sharing|Nagoya|"
    r"permission (?:of|from) (?:the )?(?:[A-Z][\w'-]+ )*(?:Tribe|Tribal|Nation|Band|Rancheria)|"
    r"Tribal (?:Council|Historic Preservation|Chair\w*|Environmental|permit\w*|approv\w*|partner\w*|collaborat\w*|consent|government|authorit\w+|liaison|members?|elders?))"),
 "local_contexts": re.compile(
    r"(Local Contexts|localcontexts\.org|\bTK Labels?\b|\bBC Labels?\b|Biocultural (?:Labels?|Notices?)|Traditional Knowledge (?:Labels?|Notices?)|\bBC Notices?\b|TK Notices?)"),
 "coordinates": re.compile(
    r"(-?\d{1,3}\.\d{2,6}\s*°?\s*[NSEW]\b|\b\d{1,3}°\s?\d{1,2}[′']|\blat(?:itude)?\b.{0,30}\blong(?:itude)?\b|\b-?1[0-2]\d\.\d{3,}\b|\bGPS\b|coordinates?)", re.I),
 "named_place": re.compile(
    r"\b(?:[A-Z][\w'-]+ (?:[A-Z][\w'-]+ )?)(?:County|National Park|National Forest|National Monument|National Wildlife Refuge|National Seashore|National Recreation Area|"
    r"State Park|State Beach|State Reserve|Natural Reserve|Reserve|Preserve|Research Station|Field Station|Marine Laboratory|Wildlife Area|Ecological Reserve|"
    r"Island|Bay|River|Creek|Lake|Lagoon|Estuary|Slough|Marsh|Beach|Point|Cape|Mount|Mountains?|Peak|Valley|Canyon|Pass|Spring|Harbor|Cove|Ranch|Dunes|Desert|Basin|Watershed|Wilderness)\b"),
 "withheld": re.compile(r"(locality|location|coordinates?)[^.]{0,80}(withheld|obscured|not (?:be )?(?:reported|provided|disclosed)|generalized|sensitive)", re.I),
 "permit": re.compile(r"\b(permit(?!s (?:non-commercial|unrestricted|re-?use|any|the))\w*|Scientific Collect\w+ (?:Permit|License)|collecting licen[cs]e|IACUC|Animal Care and Use|take authori[sz]ation|MOU|memorandum of understanding)\b", re.I),
 "issuers": re.compile(r"(California Department of Fish and Wildlife|\bCDFW\b|NOAA|National Marine Fisheries|U\.?S\.? Fish and Wildlife|USFWS|National Park Service|\bNPS\b|California (?:Department of Parks|State Parks)|Bureau of Land Management|\bBLM\b|U\.?S\.? Forest Service|USFS|UC Natural Reserve|Natural Reserve System|Bureau of Reclamation|Department of Defense|private (?:land|property|landowner)\w*|landowner\w*|Tribe|Tribal|Nation)"),
 "us": re.compile(r"\b(USA|U\.S\.A\.|United States|U\.S\.|Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawai'?i|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington(?! ?,? D\.?C)|West Virginia|Wisconsin|Wyoming|Puerto Rico)\b"),
 "mou": re.compile(r"\b(memorand(?:um|a) of (?:understanding|intent|agreement)|\bMOUs?\b|\bMOI\b(?! ?(?:=|of \d|\d))|data[- ]sharing agreement|research agreement|collaborative agreement)", re.I),
 "moi_infection": re.compile(r"multiplicity of infection|MOI ?(?:=|of) ?\d|at an MOI|viral MOI|phage MOI", re.I),
 "human": re.compile(r"\b(patients?|human (?:subjects|participants|samples|DNA|genome|microbiome|gut)|informed consent|institutional review board|\bIRB\b|cohort of|case-control|GWAS)\b", re.I),
 "organism": re.compile(r"\b(species|population|wildlife|plant|fish|bird|insect|mammal|amphibian|reptile|invertebrate|fung|microb|bacteri|vir|eDNA|environmental DNA|ecosystem|habitat|conservation|phylogeograph)", re.I),
 "deposit": re.compile(r"\b(GenBank|NCBI|BioProject|PRJNA\d+|GCA_\d+|SRA\b|ENA\b|European Nucleotide Archive|DDBJ|Dryad|Zenodo)\b"),
}

def txt(el): return " ".join("".join(el.itertext()).split()) if el is not None else ""

def sections(root):
    """Return dict of lowercase section title -> text, plus 'all', 'ack', 'methods', 'materials'."""
    out = {"all": txt(root)}
    ack = " ".join(txt(a) for a in root.iter("ack"))
    meth = mat = ""
    for s in root.iter("sec"):
        t = txt(s.find("title")).lower()
        if "acknowledg" in t: ack += " " + txt(s)
        if t.startswith("method") or "materials and methods" in t: meth += " " + txt(s)
        if any(k in t for k in ("biological material", "sample", "specimen", "collection", "tissue", "sampling", "study organism", "study species", "voucher")):
            mat += " " + txt(s)
    out["ack"], out["methods"], out["materials"] = ack, meth or out["all"], mat or meth or out["all"]
    return out

def snippets(rx, s, n=3, w=110):
    res, seen = [], set()
    for m in rx.finditer(s):
        k = m.group(0).lower()
        if k in seen: continue
        seen.add(k); a, b = max(0, m.start()-w), min(len(s), m.end()+w)
        res.append("…" + s[a:b] + "…")
        if len(res) >= n: break
    return res

rows = []
for f in sorted(xmldir.glob("PMC*.xml")):
    pmcid = f.stem
    if pmcid not in pop: continue
    stratum = "CA-DNA"; m = pop[pmcid]
    try: root = ET.parse(f).getroot()
    except ET.ParseError as e: print("parse error", pmcid, e); continue
    S = sections(root)
    body_no_refs = S["all"]
    # strip reference list to avoid matching cited titles (e.g. "Indigenous data sovereignty" papers)
    refl = root.find(".//ref-list")
    if refl is not None:
        rt = txt(refl)
        if rt and rt in body_no_refs: body_no_refs = body_no_refs.replace(rt, " ")
    r = {"pmcid": pmcid, "stratum": stratum, "year": m.get("pubYear"), "journal": m.get("journalTitle"),
         "doi": m.get("doi"), "title": m.get("title"), "open_access": m.get("isOpenAccess")}
    coords = snippets(RX["coordinates"], S["materials"]); place = snippets(RX["named_place"], S["materials"])
    r["coordinates"] = bool(coords); r["named_place"] = bool(place); r["locality_withheld"] = bool(RX["withheld"].search(S["all"]))
    r["location_reported"] = r["coordinates"] or r["named_place"]
    r["location_snippets"] = " | ".join((coords + place)[:3])
    for k in ("indigenous_lands", "consultation_care", "local_contexts"):
        sn = snippets(RX[k], body_no_refs); r[k] = bool(sn); r[k + "_snippets"] = " | ".join(sn)
    pm = snippets(RX["permit"], body_no_refs); r["permit_mentioned"] = bool(pm); r["permit_snippets"] = " | ".join(pm)
    r["permit_issuers"] = ";".join(sorted({x for x in RX["issuers"].findall(S["ack"] + " " + S["materials"])}))
    r["us_sampling"] = bool(RX["us"].search(S["materials"])); r["california"] = bool(re.search(r"\bCalifornia\b", S["materials"]))
    r["open_deposition"] = bool(RX["deposit"].search(S["all"]))
    mo = snippets(RX["mou"], body_no_refs)
    r["mou_mentioned"] = bool(mo) and not (RX["moi_infection"].search(body_no_refs) and all("MOI" in x for x in mo))
    r["mou_snippets"] = " | ".join(mo)
    hs = snippets(RX["human"], body_no_refs, n=2); r["human_subjects_terms"] = bool(hs); r["human_snippets"] = " | ".join(hs)
    r["nonhuman_organism"] = bool(RX["organism"].search(S["materials"] + " " + S["all"][:3000]))
    r["california_sampling"] = bool(re.search(r"\bCalifornia\b", S["materials"]))
    r["n_chars"] = len(S["all"])
    rows.append(r)

cols = list(rows[0].keys())
with open(outdir / "scores_all.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)
def summ(rs):
    n = len(rs)
    return {"n": n, **{k: sum(1 for r in rs if r[k]) for k in
            ("location_reported", "coordinates", "named_place", "locality_withheld", "indigenous_lands",
             "consultation_care", "local_contexts", "permit_mentioned", "open_deposition", "us_sampling", "california")}}
def summ2(rs):
    d = summ(rs)
    for k in ("mou_mentioned", "human_subjects_terms", "nonhuman_organism", "california_sampling"):
        d[k] = sum(1 for r in rs if r[k])
    return d
summary = {"CA-DNA_all": summ2(rows),
           "CA-DNA_screened_in": summ2([r for r in rows if r["nonhuman_organism"] and not r["human_subjects_terms"]])}
json.dump(summary, open(outdir / "summary_auto.json", "w"), indent=1)
print(json.dumps(summary, indent=1))
