# Governance audit of recent reference-genome reports

Run 2026-11-12. Folder: `genome_report_audit/` in the `genomic-governance-audits` repository.
Scripts: `scripts/fetch_fulltext.sh` (download), `scripts/score_reports.py` (automated
screen with snippets), `scripts/finalize_and_plot.py` (manual verdicts merged, figure).
Tables: `results/scores_final.csv` (one row per included paper, all flags, verdict notes),
`results/exclusions.csv`, `results/adjudications.csv`, `results/land_type_adjudications.csv`
(hand land-tenure call per report), `results/positives_list.md`.

## Sample

Two strata from Europe PMC (search run 2026-11-12), full text (JATS XML) only.

1. **CCGP census.** Every paper matching "California Conservation Genomics Project" in
   *Journal of Heredity*: 87 hits; 81 have Europe PMC full text, 78 downloaded (3 not
   served by Europe PMC), 3 excluded as non-genome-report papers (overview, phylogeny,
   history). **n = 75 genome reports, 2022–2026.** This is the complete set of CCGP genome
   reports with open full text, not a sample.
2. **Other EBP-affiliated genome reports.** Papers citing "Earth BioGenome Project" or
   "Vertebrate Genomes Project" with "reference genome"/"genome assembly", 2022–2026,
   excluding CCGP, Wellcome Open Research/Open Research Europe genome notes (UK/EU
   Darwin Tree of Life boilerplate), preprints, and non-genome-report titles: 122
   candidates with full text, 113 downloaded, 36 excluded by hand (software, methods,
   consortium descriptions, reviews; domesticated breeds, crop cultivars, laboratory
   strains), plus one software paper (PMC9946810) caught during the land-tenure review.
   **n = 76 wild-species genome reports, global**, 31 of them US-sampled.

## Rubric (reviewer's four criteria plus permit)

| Criterion | How scored |
|---|---|
| Sampling locality reported | Coordinates or a named place (county, park, reserve, water body, etc.) in the biological-materials/methods text. Automated. |
| Collection permit or authorization mentioned | Permit, scientific collecting permit, IACUC, take authorization, MOU in body text (CC-license boilerplate excluded). Automated; 8 random hits checked by hand, all genuine. |
| Indigenous lands or peoples acknowledged for the sampled site | Automated screen (Tribal/Indigenous/Native American/ancestral or unceded territory/named Nations, 56-tribe California dictionary) then **every hit read by hand**. Counted only if the paper identifies the sampled site's Indigenous lands or peoples (land acknowledgement or naming the Nation/custodians). Mentions of a species' cultural significance without identifying the sampled lands are tallied separately ("cultural mention"). |
| Consultation or partnership with an Indigenous Nation reported | Automated screen (consult*, Tribal Council/permission, CARE, Indigenous data sovereignty, FPIC, benefit-sharing, Nagoya) then **every hit read by hand**. Nagoya compliance statements, author "consultant" roles and co-author "consultation" are not counted. |
| Local Contexts TK/BC Label or Notice attached | Local Contexts, TK/BC Label or Notice anywhere in the paper. Every hit read by hand. |

Reference lists were stripped before screening so that cited titles (e.g. "Indigenous
data sovereignty…") could not trigger a hit.

## Results

| Criterion | CCGP (n = 75) | Other EBP-affiliated (n = 76) |
|---|---|---|
| Sampling locality reported | 74 (99%) | 42 (55%) |
| Coordinates given | 63 (84%) | 19 (25%) |
| Collection permit or authorization mentioned | 39 (52%) | 39 (51%) |
| Indigenous lands or peoples acknowledged for the sampled site | 2 (3%) | 4 (5%) |
| Cultural significance of the species mentioned (not counted above) | 3 | 2 |
| Consultation or partnership with an Indigenous Nation reported | 0 (0%) | 2 (3%) |
| Local Contexts TK/BC Label or Notice attached | 0 (0%) | 0 (0%) |
| Data deposited in an open repository (NCBI/ENA etc.) | 75 (100%) | 76 (100%) |

The two CCGP acknowledgements: California walnut (PMC10445516: "Native Peoples of
California… traditional land caretakers", no Nation named) and Island Oak (PMC10936553:
Channel Islands as ancestral unceded territory of the Chumash and Gabrielino-Tongva
Peoples). Neither reports consultation.

The two reports with consultation or partnership are both from jurisdictions with a
Treaty or land-claims framework: Hector's and Māui dolphin, Aotearoa (PMC12415809,
consultation with iwi and hapū; data described as taonga and tapu) and beluga/narwhal,
Nunavut/Nunavik (PMC10659057, samples provided by Inuit harvesters). The other two
acknowledgements are Australian (Barrow Island Traditional Owners; Palawa custodians).

Permits are routinely documented in the same paragraph as coordinates (CDFW scientific
collecting permits, USFWS, NMFS, State Parks). One CCGP sample (bobcat, PMC9709964) was
collected "under a Memorandum of Understanding with the California Department of Fish
and Wildlife": the MOU instrument is already in use upstream of the data.

## Land tenure of the sampling site (figure panel B)

Each included report was read by hand and the site where the sequenced individual (or its
wild parent/seed) was collected was classified by land or water tenure. Basis of each call:
*stated* = the report names the managing unit or owner; *inferred* = the report names a
well-known site whose manager is public record but is not given (Cow Mountain Recreation
Management Area = BLM; McClures Beach and Lifeboat House = Point Reyes National Seashore;
Sonora Peak = USFS wilderness; Mitsui Ranch, Flying M Ranch = private); *none* = place
named but tenure not stated or not resolvable, or no place given. Multi-genome papers are
scored on the first-named species. Ex situ sources (zoo, hatchery, garden accession, museum
tissue, pet trade, market) are their own class, with the wild origin in the note column.

| Land tenure | CCGP (n = 75) | Other EBP-affiliated (n = 76) |
|---|---|---|
| Federal (national) public land or waters | 15 (20%) | 4 (5%) |
| State or provincial public land or waters | 9 (12%) | 4 (5%) |
| County or municipal park | 3 (4%) | 0 |
| University reserve, station or garden | 6 (8%) | 1 (1%) |
| Private land or preserve | 6 (8%) | 3 (4%) |
| Indigenous-governed lands or waters | 0 | 2 (3%) |
| Public waters, no named managed unit | 4 (5%) | 13 (17%) |
| Ex situ source (captive, cultivated, museum) | 5 (7%) | 25 (33%) |
| Not stated or not resolvable | 27 (36%) | 24 (32%) |
| Basis: stated / inferred / none | 30 / 14 / 31 | 33 / 6 / 37 |

Points for the paper: 37 of 75 CCGP genomes come from public land, public waters or
university reserves (Yosemite, Joshua Tree, three National Forests, BLM and CDFW units,
State Parks and State Beaches, five UC Natural Reserve System sites), i.e. from land
held by agencies with existing Tribal-consultation obligations or land acknowledgements,
and none of those reports names the Nation whose territory the unit occupies. The only
two reports whose sites fall under Indigenous governance (Nunavut land-claim waters;
Aotearoa coastal waters under iwi rangatiratanga) are the same two that document
consultation. A third of CCGP reports give a place name but no tenure (roadsides, creek
mouths, canyons, towns), which is itself a reporting gap for any future notice-to-Nation
default.

## Caveats to state in the paper

- Text-based: a Local Contexts Notice attached in NCBI BioSample metadata rather than
  in the paper would be missed. (None of the 151 papers mentions one.)
- Nine CCGP reports without open full text (paywalled/not served) are not scored.
- Criterion 1 and the permit criterion are automated with spot checks; criteria 2–4 are
  fully hand-verified (36 adjudications in `results/adjudications.csv`). Land tenure is
  hand-classified for all 151 reports; 20 calls are inferred from a named site rather than
  stated in the report, and are labelled as such in `land_type_adjudications.csv`.
- Stratum 2 is global; the Indigenous-lands criterion is less applicable to some
  European and Asian sampling sites, which depresses its rate. Restricting to the 31
  US-sampled reports does not change the conclusion (see `scores_final.csv`).
- The original PRISMA repo (`SashaNikolaeva/prisma-tribal-dna-review`, Feb 2026) asked a
  different question (any CA ecological DNA paper with tribal-agreement language in the
  abstract) and is not the source of these numbers.
