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
land = {a["pmcid"]: a for a in csv.DictReader(open(res / "land_type_adjudications.csv"))}  # hand verdicts, one per report
T = lambda v: v == "True"
CRITS = ["indigenous_lands", "consultation_care", "local_contexts"]
final, unreviewed = [], []
for r in rows:
    if r["pmcid"] in excl: continue
    o = {k: r[k] for k in ("pmcid", "stratum", "year", "journal", "doi", "title")}
    o["location_reported_auto"] = T(r["location_reported"]); o["coordinates"] = T(r["coordinates"])
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
    L = land.get(r["pmcid"])
    if L is None: unreviewed.append((r["pmcid"], "land_type"))
    o["land_type"] = L["land_type"] if L else "unreviewed"; o["land_type_basis"] = L["basis"] if L else ""
    o["sampling_site"] = L["site"] if L else ""; o["land_type_note"] = L["note"] if L else ""
    # criterion 1 is taken from the hand read (the regex misses town names and counts zoos)
    o["location_reported"] = (L["wild_locality_reported"] == "1") if L else o["location_reported_auto"]
    final.append(o)
if unreviewed: print("UNREVIEWED POSITIVES:", unreviewed)
cols = list(final[0].keys())
with open(res / "scores_final.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(final)

ROWS = [("location_reported", "Wild sampling locality reported"),
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
                  "location_reported_auto": sum(1 for o in rs if o["location_reported_auto"]),
                  "open_deposition": sum(1 for o in rs if o["open_deposition"]),
                  "us_sampling": sum(1 for o in rs if o["us_sampling"])}
LAND = [("federal_public", "Federal (national) public land or waters"),
        ("state_public", "State or provincial public land or waters"),
        ("local_public", "County or municipal park"),
        ("university_reserve", "University reserve, station or garden"),
        ("private_land", "Private land or preserve"),
        ("indigenous_lands_waters", "Indigenous co-governance of the site\ndescribed in the report"),
        ("marine_waters", "Public waters, no named managed unit"),
        ("ex_situ", "Ex situ source (captive, cultivated, museum)"),
        ("unspecified", "Land tenure not stated or not resolvable")]
for s_, _ in STRATA:
    rs = [o for o in final if o["stratum"] == s_]
    summary[s_]["land_type"] = {k: sum(1 for o in rs if o["land_type"] == k) for k, _ in LAND}
    summary[s_]["land_type_basis"] = {b: sum(1 for o in rs if o["land_type_basis"] == b) for b in ("stated", "inferred", "none")}
    pub = ("federal_public", "state_public", "local_public", "university_reserve", "marine_waters")
    summary[s_]["public_or_university"] = sum(1 for o in rs if o["land_type"] in pub)
json.dump(summary, open(res / "summary_final.json", "w"), indent=1); print(json.dumps(summary, indent=1))

# ---- figure: two panels of horizontal grouped bars (A governance criteria, B land tenure) ----
plt.rcParams.update({"font.family": "Helvetica", "font.size": 8.5, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.spines.left": False})
COL = {"CCGP": "#2a78d6", "EBP-other": "#eb6834"}
h, gap = 0.34, 0.04

def panel(ax, rows, getter, letter, title):
    ylabels = []
    for i, (k, lab) in enumerate(rows):
        y0 = len(rows) - 1 - i
        for j, (s_, _) in enumerate(STRATA):
            n = summary[s_]["n"]; c = getter(s_, k); pct = 100 * c / n
            y = y0 + (h + gap) / 2 - j * (h + gap)
            ax.barh(y, pct, height=h, color=COL[s_], edgecolor="none")
            if pct == 0: ax.plot([0], [y], marker="|", color=COL[s_], ms=9, mew=1.6)
            ax.text(pct + 1.2, y, f"{c}/{n}", va="center", ha="left", color="#52514e", fontsize=7.5)
        ylabels.append((y0, lab))
    ax.set_yticks([y for y, _ in ylabels]); ax.set_yticklabels([l for _, l in ylabels], color="#0b0b0b")
    ax.tick_params(axis="y", length=0, pad=6); ax.tick_params(axis="x", colors="#52514e", length=3)
    ax.set_xlim(0, 100); ax.xaxis.set_major_formatter(PercentFormatter(decimals=0))
    ax.set_xlabel("Share of genome reports", color="#52514e")
    ax.grid(axis="x", color="#e6e5e1", lw=0.6); ax.set_axisbelow(True); ax.spines["bottom"].set_color("#c3c2b7")
    ax.text(-0.52, 1.02, letter, transform=ax.transAxes, fontsize=11, fontweight="bold", va="bottom", ha="left")
    ax.text(-0.46, 1.02, title, transform=ax.transAxes, fontsize=8.5, va="bottom", ha="left", color="#0b0b0b")

fig, (axA, axB) = plt.subplots(2, 1, figsize=(180/25.4, 200/25.4), dpi=300,
                               gridspec_kw={"height_ratios": [len(ROWS), len(LAND)], "hspace": 0.42})
panel(axA, ROWS, lambda s_, k: summary[s_][k], "A", "Governance reporting")
panel(axB, LAND, lambda s_, k: summary[s_]["land_type"][k], "B", "Land tenure of the sampling site")
handles = [plt.Rectangle((0, 0), 1, 1, color=COL[s_]) for s_, _ in STRATA]
axA.legend(handles, [f"{lab.replace(chr(10), ' ')} (n = {summary[s_]['n']})" for s_, lab in STRATA],
           loc="lower left", bbox_to_anchor=(0, 1.12), frameon=False, fontsize=7.5, handlelength=1.2, borderaxespad=0)
for ext in ("png", "pdf", "svg"): fig.savefig(figd / f"governance_audit.{ext}", bbox_inches="tight")
print("figure written to", figd)
