#!/usr/bin/env python3
"""Merge automated scores with manual exclusions/adjudications for the California
non-human DNA audit; write final table, PRISMA-style counts, summary, and figure.
Usage: finalize_and_plot_ca.py RESULTSDIR FIGDIR POPULATION_ABSTRACT_COUNT POPULATION_FT_COUNT"""
import csv, json, sys, pathlib
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

res, figd = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]); figd.mkdir(exist_ok=True)
n_abstract, n_ft = int(sys.argv[3]), int(sys.argv[4])
rows = list(csv.DictReader(open(res / "scores_all.csv")))
excl = {r["pmcid"]: r["reason"] for r in csv.DictReader(open(res / "exclusions.csv"))} if (res / "exclusions.csv").exists() else {}
adj = {(a["pmcid"], a["criterion"]): a for a in csv.DictReader(open(res / "adjudications.csv"))} if (res / "adjudications.csv").exists() else {}
T = lambda v: v == "True"
CRITS = ["indigenous_lands", "consultation_care", "local_contexts", "mou_mentioned"]
final, unreviewed, screened_out = [], [], {"manual_exclusion": 0}
for r in rows:
    if r["pmcid"] in excl: screened_out["manual_exclusion"] += 1; continue
    # inclusion is decided by the hand-made exclusions.csv (title screen); the automated
    # human-terms flag is kept as a column only, because journal boilerplate ("Informed
    # Consent Statement: not applicable"), plant GWAS and human-DNA contamination notes trip it
    o = {k: r[k] for k in ("pmcid", "year", "journal", "doi", "title")}
    for k in ("location_reported", "coordinates", "permit_mentioned", "open_deposition", "california_sampling"): o[k] = T(r[k])
    for c in CRITS:
        a = adj.get((r["pmcid"], c))
        if a: o[c] = a["verified"] == "1"; o[c + "_category"] = a["category"]; o[c + "_note"] = a["note"]
        else:
            o[c] = T(r[c]); o[c + "_category"] = "unreviewed_auto_positive" if o[c] else ""; o[c + "_note"] = ""
            if o[c]: unreviewed.append((r["pmcid"], c))
    o["indigenous_cultural_mention"] = o["indigenous_lands_category"] == "cultural_significance_only"
    o["tribal_mou"] = o["mou_mentioned_category"] == "tribal_agreement"
    final.append(o)
if unreviewed: print("UNREVIEWED POSITIVES:", len(unreviewed), unreviewed[:40])
with open(res / "scores_final.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(final[0].keys())); w.writeheader(); w.writerows(final)
n = len(final)
ROWS = [("location_reported", "Sampling locality reported"),
        ("permit_mentioned", "Collection permit or authorization mentioned"),
        ("indigenous_lands", "Indigenous lands or peoples acknowledged\nfor the sampled site"),
        ("consultation_care", "Consultation, permission or partnership\nwith a Tribal Nation reported"),
        ("tribal_mou", "Formal agreement (MOU/research agreement)\nwith a Tribal Nation mentioned"),
        ("local_contexts", "Local Contexts TK/BC Label or Notice attached")]
summary = {"population_abstract_level": n_abstract, "population_with_fulltext": n_ft, "downloaded_and_parsed": len(rows),
           "screened_out": screened_out, "n_scored": n,
           **{k: sum(1 for o in final if o[k]) for k, _ in ROWS},
           "indigenous_cultural_mention": sum(1 for o in final if o["indigenous_cultural_mention"]),
           "any_mou_text": sum(1 for o in final if o["mou_mentioned"]),
           "coordinates": sum(1 for o in final if o["coordinates"]),
           "open_deposition": sum(1 for o in final if o["open_deposition"]),
           "california_sampling_text": sum(1 for o in final if o["california_sampling"]),
           "agency_mou_for_sampling": sum(1 for o in final if o["mou_mentioned_category"] == "agency_mou"),
           "consultation_categories": {c: sum(1 for o in final if o["consultation_care"] and o["consultation_care_category"] == c)
                                       for c in sorted({o["consultation_care_category"] for o in final if o["consultation_care"]})},
           "lands_categories": {c: sum(1 for o in final if o["indigenous_lands"] and o["indigenous_lands_category"] == c)
                                for c in sorted({o["indigenous_lands_category"] for o in final if o["indigenous_lands"]})}}
json.dump(summary, open(res / "summary_final.json", "w"), indent=1); print(json.dumps(summary, indent=1))

plt.rcParams.update({"font.family": "Helvetica", "font.size": 8.5, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.spines.left": False})
fig, ax = plt.subplots(figsize=(180/25.4, 85/25.4), dpi=300)
for i, (k, lab) in enumerate(ROWS):
    y = len(ROWS) - 1 - i; c = summary[k]; pct = 100 * c / n
    ax.barh(y, pct, height=0.55, color="#2a78d6", edgecolor="none")
    if pct == 0: ax.plot([0], [y], marker="|", color="#2a78d6", ms=11, mew=1.6)
    ax.text(pct + 1.2, y, f"{c}/{n}", va="center", ha="left", color="#52514e", fontsize=7.5)
ax.set_yticks(range(len(ROWS))[::-1]); ax.set_yticklabels([l for _, l in ROWS], color="#0b0b0b")
ax.tick_params(axis="y", length=0, pad=6); ax.tick_params(axis="x", colors="#52514e", length=3)
ax.set_xlim(0, 100); ax.xaxis.set_major_formatter(PercentFormatter(decimals=0))
ax.set_xlabel(f"Share of California non-human DNA papers with open full text, 2011–2026 (n = {n})", color="#52514e")
ax.grid(axis="x", color="#e6e5e1", lw=0.6); ax.set_axisbelow(True); ax.spines["bottom"].set_color("#c3c2b7")
fig.tight_layout()
for ext in ("png", "pdf", "svg"): fig.savefig(figd / f"ca_dna_governance_audit.{ext}", bbox_inches="tight")
print("figure written to", figd)
