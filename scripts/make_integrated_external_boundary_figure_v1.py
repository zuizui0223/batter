#!/usr/bin/env python3
from pathlib import Path
import csv
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "figures" / "integrated_external_boundary_v1.csv"
OUT = ROOT / "figures" / "integrated_external_boundary_v1.svg"

rows = []
with DATA.open(newline="", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        for k in ["observed", "null_mean", "q025", "q975", "calibrated_excess", "p_upper"]:
            r[k] = float(r[k])
        r["n"] = int(r["n"])
        r["null_low_centered"] = r["q025"] - r["null_mean"]
        r["null_high_centered"] = r["q975"] - r["null_mean"]
        rows.append(r)

def row_label(label):
    if label == "Nyctalus noctula":
        return r"$\it{Nyctalus\ noctula}$"
    if label.startswith("Hipposideros"):
        return r"$\it{Hipposideros\ armiger}$ / $\it{Hipposideros\ pratti}$"
    if label == "Myotis vivesi":
        return r"$\it{Myotis\ vivesi}$"
    if label == "Pteropus poliocephalus (MSL)":
        return r"$\it{Pteropus\ poliocephalus}$ (MSL)"
    if label == "Pteropus poliocephalus (MSL-DEM)":
        return r"$\it{Pteropus\ poliocephalus}$ (MSL−DEM)"
    return label

ys = list(range(len(rows), 0, -1))
fig, ax = plt.subplots(figsize=(9.0, 5.7))

for y, r in zip(ys, rows):
    ax.hlines(y, r["null_low_centered"], r["null_high_centered"], linewidth=2)
    marker = "o" if r["verdict"] == "PASS" else "x"
    ax.scatter(r["calibrated_excess"], y, marker=marker, s=70, zorder=3)
    ax.annotate(
        f"n={r['n']}", xy=(0, y), xycoords=("axes fraction", "data"),
        xytext=(-6, 0), textcoords="offset points",
        ha="right", va="center", fontsize=8
    )

ax.axvline(0, linewidth=1)
ax.set_yticks(ys)
ax.set_yticklabels([row_label(r["label"]) for r in rows])
ax.tick_params(axis="y", pad=42)
ax.set_xlim(-0.13, 0.20)
ax.set_xlabel("Null-calibrated centered vertical identity excess (nats/fix)")
ax.set_title("External boundary tests and Pteropus terrain diagnostic")
ax.set_ylim(0.5, len(rows) + 0.5)

ax.plot([], [], linestyle="-", linewidth=2, label="central 95% permutation-null interval")
ax.scatter([], [], marker="o", label="met pre-specified criterion")
ax.scatter([], [], marker="x", label="did not meet pre-specified criterion")
ax.legend(
    loc="upper center", bbox_to_anchor=(0.5, -0.18),
    ncol=3, fontsize=8, frameon=False
)

fig.subplots_adjust(left=0.41, right=0.98, top=0.89, bottom=0.26)
fig.savefig(OUT)
print(OUT)
