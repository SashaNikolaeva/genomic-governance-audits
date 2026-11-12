# Governance audit of California non-human DNA research, 2011–2026

Run 2026-11-12. Folder `ca_dna_tribal_audit/` in the `genomic-governance-audits` repository.
Scripts: `scripts/fetch_population.sh` (Europe PMC query, all records), `scripts/fetch_fulltext_parallel.sh`
+ `scripts/fetch_one.sh` (full-text JATS XML), `scripts/score_ca_dna.py` (automated screen with
snippets), `scripts/finalize_and_plot_ca.py` (merges hand verdicts, writes final table, summary, figure).
Tables: `results/scores_final.csv` (one row per included paper), `results/exclusions.csv` (title screen),
`results/adjudications.csv` (149 hand verdicts), `results/positives_list.md`, `results/summary_final.json`.

## Question

Among peer-reviewed, non-human DNA-based studies of California organisms and environments, how many
report (1) the sampling locality, (2) a collection permit, (3) the Indigenous lands or peoples of the
sampled site, (4) consultation, permission or partnership with a Tribal Nation, (5) a formal agreement
(MOU / research agreement) with a Tribal Nation, and (6) a Local Contexts TK/BC Label or Notice?

This supersedes an earlier abstract-level search (February 2026) that could not see acknowledgements
or methods and therefore could not answer the question.

## Population and flow

| Stage | n |
|---|---|
| Europe PMC, title/abstract: "California" AND DNA-method terms AND ecology terms, NOT human-clinical terms, 2011–2026 | 2,720 |
| … with full text served by Europe PMC (`HAS_FT:Y`) | 1,096 |
| … full-text XML retrieved and parsed (Europe PMC did not serve the remaining 181) | 910 |
| Excluded by title screen (human/clinical 20; laboratory/model/vaccine 39; agricultural crop, livestock, pet, crop pathogen 107; software/database/review/meeting 24; sampling outside California 60; built environment 4; two IDs in two groups) | 248 |
| **Scored** | **662** |

The query strings are in `scripts/fetch_population.sh`. Field-collected pest insects were kept
(they are wild populations); crop plants, livestock, crop pathogens and lab strains were not.

## Rubric

Same rubric as the genome-report audit. Criteria 1–2 are automated regex screens of the
biological-materials / methods text (spot-checked). Criteria 3–6 were regex-screened across the whole
paper with reference lists stripped, and **every automated hit (142) was then read and classified by
hand**; the verdicts and reasons are in `results/adjudications.csv`. "Cultural significance" mentions
(a species was used or valued by Indigenous people, with no identification of the sampled site's
lands) are tallied separately and not counted as acknowledgement.

## Results (n = 662)

| Criterion | n | % |
|---|---|---|
| Sampling locality reported | 470 | 71 |
| Coordinates given | 266 | 40 |
| Collection permit or authorization mentioned | 401 | 61 |
| … of which the sample was taken under a Memorandum of Understanding with CDFW | 10 | 1.5 |
| Indigenous lands or peoples acknowledged for the sampled site | 20 | 3.0 |
| … naming a Nation | 16 | 2.4 |
| … generic ("Native Peoples of California") | 4 | 0.6 |
| Cultural significance of the species mentioned, lands not identified (not counted above) | 15 | 2.3 |
| Consultation, permission or partnership with a Tribal Nation reported | 6 | 0.9 |
| Formal agreement (MOU / research agreement) with a Tribal Nation mentioned | 1 | 0.2 |
| Local Contexts TK/BC Label or Notice attached | 0 | 0 |
| Data deposited in an open repository (NCBI/ENA/Dryad etc.) | 570 | 86 |

**The six consultation/partnership cases** (`results/positives_list.md`):

1. PMC5892934 (2018): access to the Hoopa Valley Reservation granted by Hoopa Tribal Forestry and the Hoopa Tribal Council; Tribal co-author.
2. PMC7548186 (2020): agreements with Native American Tribes (unnamed), private landowners and NGOs govern release of mountain-lion sample coordinates. The only formal Tribal agreement in the set.
3. PMC7788075 (2020): permission from the Hopi Tribal Historic Preservation Officer to use a Hopi word as a species name (naming, not sampling).
4. PMC12016506 (2025): Big Valley Band of Pomo Indians and its Environmental Protection Office assisted sampling at Clear Lake.
5. PMC13373871 (2026): named British Columbia First Nations thanked for permission to reanalyze DNA from their territories (the paper also samples California).
6. PMC13516315 (2026): Karuk Tribe Department of Natural Resources (Karuk Wildlife Team) are co-authors.

Only four of these concern a California Tribal Nation and the sampling or data itself.

**Trend.** Land acknowledgements are recent: 0 of 146 papers in 2011–2016, 2 of 151 in 2017–2020,
7 of 172 in 2021–2023, 11 of 193 in 2024–2026. Consultation/partnership shows no trend (0, 3, 0, 3).
Permits are reported in roughly half to two-thirds of papers in every period.

**The MOU is already the instrument for samples.** Ten papers collected tissue "under a Memorandum of
Understanding with the California Department of Fish and Wildlife" alongside scientific collecting
permits. The instrument that the paper proposes for data governance is in routine use upstream, with a
state agency as the counterparty.

## Caveats

- Open full text only: 1,096 of 2,720 population papers have Europe PMC full text and 910 could be
  retrieved. Papers behind paywalls are not scored; the automated screen cannot see supplementary files.
- Inclusion was decided from titles (plus the California-sampling flag); some crop-pathogen or
  Mexico-only papers may remain and some borderline ecological papers may have been dropped. The
  full list with reasons is in `results/exclusions.csv`.
- Criteria 1–2 are automated. Criteria 3–6 are hand-verified; a reader can re-check every verdict
  from the snippet columns in `results/scores_all.csv`.
- A Local Contexts Notice attached only in repository metadata (not in the paper) would be missed.
