# Governance audit of recent reference-genome reports

Run 2026-11-12. Folder: `genome_report_audit/` in the `genomic-governance-audits` repository.
Scripts: `scripts/fetch_fulltext.sh` (download), `scripts/score_reports.py` (automated
screen with snippets), `scripts/finalize_and_plot.py` (manual verdicts merged, figure).
Tables: `results/scores_final.csv` (one row per included paper, all flags, verdict notes),
`results/exclusions.csv`, `results/adjudications.csv`, `results/positives_list.md`.

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
   strains). **n = 77 wild-species genome reports, global**, 31 of them US-sampled.

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

| Criterion | CCGP (n = 75) | Other EBP-affiliated (n = 77) |
|---|---|---|
| Sampling locality reported | 74 (99%) | 43 (56%) |
| Coordinates given | 63 (84%) | 20 (26%) |
| Collection permit or authorization mentioned | 39 (52%) | 39 (51%) |
| Indigenous lands or peoples acknowledged for the sampled site | 2 (3%) | 4 (5%) |
| Cultural significance of the species mentioned (not counted above) | 3 | 2 |
| Consultation or partnership with an Indigenous Nation reported | 0 (0%) | 2 (3%) |
| Local Contexts TK/BC Label or Notice attached | 0 (0%) | 0 (0%) |
| Data deposited in an open repository (NCBI/ENA etc.) | 75 (100%) | 77 (100%) |

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

## Caveats to state in the paper

- Text-based: a Local Contexts Notice attached in NCBI BioSample metadata rather than
  in the paper would be missed. (None of the 152 papers mentions one.)
- Nine CCGP reports without open full text (paywalled/not served) are not scored.
- Criterion 1 and the permit criterion are automated with spot checks; criteria 2–4 are
  fully hand-verified (36 adjudications in `results/adjudications.csv`).
- Stratum 2 is global; the Indigenous-lands criterion is less applicable to some
  European and Asian sampling sites, which depresses its rate. Restricting to the 31
  US-sampled reports does not change the conclusion (see `scores_final.csv`).
- The original PRISMA repo (`SashaNikolaeva/prisma-tribal-dna-review`, Feb 2026) asked a
  different question (any CA ecological DNA paper with tribal-agreement language in the
  abstract) and is not the source of these numbers.
