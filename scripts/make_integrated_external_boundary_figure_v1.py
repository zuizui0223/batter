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

def row_label(label, n):
    if label == "Nyctalus noctula":
        s = r"$\it{Nyctalus\ noctula}$"
    elif label.startswith("Hipposideros"):
        s = r"$\it{Hipposideros\ armiger}$ / $\it{Hipposideros\ pratti}$"
    elif label == "Myotis vivesi":
        s = r"$\it{Myotis\ vivesi}$"
    elif label == "Pteropus poliocephalus (MSL)":
        s = r"$\it{Pteropus\ poliocephalus}$ (MSL)"
    elif label == "Pteropus poliocephalus (MSL-DEM)":
        s = r"$\it{Pteropus\ poliocephalus}$ (MSL−DEM)"
    else:
        s = label
    return f"{s}  (n={n})"

ys = list(range(len(rows), 0, -1))
fig, ax = plt.subplots(figsize=(8.7, 4.8))

for y, r in zip(ys, rows):
    ax.hlines(y, r["null_low_centered"], r["null_high_centered"], linewidth=2)
    marker = "o" if r["verdict"] == "PASS" else "x"
    ax.scatter(r["calibrated_excess"], y, marker=marker, s=70, zorder=3)

ax.axvline(0, linewidth=1)
ax.set_yticks(ys)
ax.set_yticklabels([row_label(r["label"], r["n"]) for r in rows])
ax.set_xlim(-0.13, 0.20)
ax.set_xlabel("Null-calibrated centered vertical identity excess (nats/fix)")
ax.set_title("External boundary tests and Pteropus terrain diagnostic")
ax.set_ylim(0.5, len(rows) + 0.5)

ax.plot([], [], linestyle="-", linewidth=2, label="central 95% permutation-null interval")
ax.scatter([], [], marker="o", label="met pre-specified criterion")
ax.scatter([], [], marker="x", label="did not meet pre-specified criterion")
ax.legend(loc="lower right", fontsize=8, frameon=False)

fig.tight_layout()
fig.savefig(OUT)
print(OUT)
