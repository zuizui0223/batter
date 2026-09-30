#!/usr/bin/env python3
from pathlib import Path
import csv
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "figures" / "integrated_external_boundary_v1.csv"
OUT = ROOT / "figures" / "integrated_external_boundary_v1.svg"

rows = []
with DATA.open(newline="", encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        row["calibrated_excess"] = float(row["calibrated_excess"])
        row["p_upper"] = float(row["p_upper"])
        row["n"] = int(row["n"])
        rows.append(row)

y = list(range(len(rows), 0, -1))
fig, ax = plt.subplots(figsize=(8.0, 4.8))

for yy, row in zip(y, rows):
    marker = "o" if row["verdict"] == "PASS" else "x"
    ax.scatter(row["calibrated_excess"], yy, marker=marker, s=70)
    ax.text(
        row["calibrated_excess"], yy + 0.18,
        f"p={row['p_upper']:.4f}, n={row['n']}",
        ha="center", va="bottom", fontsize=8
    )

ax.axvline(0, linewidth=1)
ax.set_yticks(y)
ax.set_yticklabels([row["label"] for row in rows])
ax.set_xlabel("Null-calibrated centered vertical identity excess (nats/fix)")
ax.set_title("External boundary tests and Pteropus terrain diagnostic")
ax.set_ylim(0.5, len(rows) + 0.8)

ax.text(
    0.99, 0.02,
    "Source tests are shown under their own frozen programmes; no pooled prevalence is implied.\n"
    "Pteropus MSL-DEM is a post-outcome frozen confound diagnostic.\n"
    "Terrain-only diagnostic: excess +0.37887, p=0.0034.",
    transform=ax.transAxes, ha="right", va="bottom", fontsize=8
)

fig.tight_layout()
fig.savefig(OUT)
print(OUT)
