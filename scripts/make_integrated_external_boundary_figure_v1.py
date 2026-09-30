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

ys = list(range(len(rows), 0, -1))
fig, ax = plt.subplots(figsize=(8.4, 4.8))

for y, row in zip(ys, rows):
    marker = "o" if row["verdict"] == "PASS" else "x"
    ax.scatter(row["calibrated_excess"], y, marker=marker, s=70)
    ax.text(0.72, y, f"p={row['p_upper']:.4f}, n={row['n']}",
            transform=ax.get_yaxis_transform(), ha="left", va="center", fontsize=8)

ax.axvline(0, linewidth=1)
ax.set_yticks(ys)
ax.set_yticklabels([row["label"] for row in rows])
ax.set_xlim(-0.07, 0.22)
ax.set_xlabel("Null-calibrated centered vertical identity excess (nats/fix)")
ax.set_title("External boundary tests and Pteropus terrain diagnostic")
ax.set_ylim(0.5, len(rows) + 0.5)

fig.tight_layout()
fig.savefig(OUT)
print(OUT)
