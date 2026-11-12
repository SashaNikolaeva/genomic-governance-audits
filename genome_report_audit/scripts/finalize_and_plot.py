#!/usr/bin/env python3
"""Merge automated scores with manual exclusions/adjudications; write final table,
summary, and the figure. Usage: finalize_and_plot.py RESULTSDIR FIGDIR"""
import csv, json, sys, pathlib
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

res, figd = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]); figd.mkdir(exist_ok=True)
rows = list(csv.DictReader(open(res / "scores_all.csv")))
excl = {r["pmcid"]: r["reason"] for r in csv.DictReader(open(res / "exclusions.csv"))}
adj = {(a["pmcid"], a["criterion"]): a for a in csv.DictReader(open(res / "adjudications.csv"))}
T = lambda v: v == "True"
CRITS = ["indigenous_lands", "consultation_care", "local_contexts"]
final, unreviewed = [], []
for r in rows:
    if r["pmcid"] in excl: continue
    o = {k: r[k] for k in ("pmcid", "stratum", "year", "journal", "doi", "title")}
    o["location_reported"] = T(r["location_reported"]); o["coordinates"] = T(r["coordinates"])
    o["permit_mentioned"] = T(r["permit_mentioned"]); o["open_deposition"] = T(r["open_deposition"])
    o["us_sampling"] = T(r["us_sampling"])
    for c in CRITS:
        a = adj.get((r["pmcid"], c))
        if a: o[c] = a["verified"] == "1"; o[c + "_category"] = a["category"]; o[c + "_note"] = a["note"]
        else:
            o[c] = T(r[c]); o[c + "_category"] = "unreviewed_auto_positive" if o[c] else ""; o[c + "_note"] = ""
            if o[c]: unreviewed.append((r["pmcid"], c))
    # cultural-significance-only mentions are kept as a separate, softer category
    o["indigenous_cultural_mention"] = o["indigenous_lands_category"] == "cultural_significance_only"
    final.append(o)
if unreviewed: print("UNREVIEWED POSITIVES:", unreviewed)
cols = list(final[0].keys())
with open(res / "scores_final.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(final)

ROWS = [("location_reported", "Sampling locality reported"),
        ("permit_mentioned", "Collection permit or authorization mentioned"),
        ("indigenous_lands", "Indigenous lands or peoples acknowledged\nfor the sampled site"),
        ("consultation_care", "Consultation or partnership with an\nIndigenous Nation reported"),
        ("local_contexts", "Local Contexts TK/BC Label or Notice attached")]
STRATA = [("CCGP", "California Conservation Genomics Project\ngenome reports, J. Heredity 2022–2026"),
          ("EBP-other", "Other EBP-affiliated wild-species\ngenome reports, 2022–2026")]
summary = {}
for s, _ in STRATA:
    rs = [o for o in final if o["stratum"] == s]; n = len(rs)
    summary[s] = {"n": n, **{k: sum(1 for o in rs if o[k]) for k, _ in ROWS},
                  "indigenous_cultural_mention": sum(1 for o in rs if o["indigenous_cultural_mention"]),
                  "coordinates": sum(1 for o in rs if o["coordinates"]),
                  "open_deposition": sum(1 for o in rs if o["open_deposition"]),
                  "us_sampling": sum(1 for o in rs if o["us_sampling"])}
json.dump(summary, open(res / "summary_final.json", "w"), indent=1); print(json.dumps(summary, indent=1))

# ---- figure: horizontal grouped bars, percent of reports, direct n/N labels ----
plt.rcParams.update({"font.family": "Helvetica", "font.size": 8.5, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.spines.left": False})
COL = {"CCGP": "#2a78d6", "EBP-other": "#eb6834"}
fig, ax = plt.subplots(figsize=(180/25.4, 105/25.4), dpi=300)
h, gap = 0.34, 0.04
ylabels = []
for i, (k, lab) in enumerate(ROWS):
    y0 = len(ROWS) - 1 - i
    for j, (s, _) in enumerate(STRATA):
        n = summary[s]["n"]; c = summary[s][k]; pct = 100 * c / n
        y = y0 + (h + gap) / 2 - j * (h + gap)
        ax.barh(y, pct, height=h, color=COL[s], edgecolor="none")
        if pct == 0:
            ax.plot([0], [y], marker="|", color=COL[s], ms=9, mew=1.6)
        ax.text(pct + 1.2, y, f"{c}/{n}", va="center", ha="left", color="#52514e", fontsize=7.5)
    ylabels.append((y0, lab))
ax.set_yticks([y for y, _ in ylabels]); ax.set_yticklabels([l for _, l in ylabels], color="#0b0b0b")
ax.tick_params(axis="y", length=0, pad=6); ax.tick_params(axis="x", colors="#52514e", length=3)
ax.set_xlim(0, 100); ax.xaxis.set_major_formatter(PercentFormatter(decimals=0))
ax.set_xlabel("Share of genome reports", color="#52514e")
ax.grid(axis="x", color="#e6e5e1", lw=0.6); ax.set_axisbelow(True); ax.spines["bottom"].set_color("#c3c2b7")
handles = [plt.Rectangle((0, 0), 1, 1, color=COL[s]) for s, _ in STRATA]
ax.legend(handles, [f"{lab.replace(chr(10), ' ')} (n = {summary[s]['n']})" for s, lab in STRATA],
          loc="lower left", bbox_to_anchor=(0, 1.0), frameon=False, fontsize=7.5, handlelength=1.2, borderaxespad=0)
fig.tight_layout()
for ext in ("png", "pdf", "svg"): fig.savefig(figd / f"governance_audit.{ext}", bbox_inches="tight")
print("figure written to", figd)
