#!/usr/bin/env python3
from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "figures" / "integrated_mechanism_localization_v1.csv"
OUT = ROOT / "figures" / "integrated_mechanism_localization_v1.svg"

tests = [
    "Speed",
    "Speed x turn",
    "Place x state 2 km",
    "Place x state 500 m",
    "Place x state 250 m",
    "Self lag >=1 d",
    "Self lag >=3 d",
    "Self lag >=7 d",
    "Same-night 2 km",
]
panels = [
    "Eidolon",
    "Hypsignathus",
    "Phyllostomus 2022",
    "Phyllostomus 2023",
    "Phyllostomus 2016",
]

records = {}
with DATA.open(newline="", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        records[(r["test"], r["panel"])] = {
            "excess": float(r["calibrated_excess"]),
            "p": float(r["p_upper"]),
            "n": int(r["n"]),
            "status": r["status"],
        }

matrix = np.full((len(tests), len(panels)), np.nan)
for i, test in enumerate(tests):
    for j, panel in enumerate(panels):
        rec = records.get((test, panel))
        if rec is not None:
            matrix[i, j] = rec["excess"]

fig, ax = plt.subplots(figsize=(9.4, 6.3))
masked = np.ma.masked_invalid(matrix)
im = ax.imshow(masked, aspect="auto")

ax.set_xticks(range(len(panels)))
ax.set_xticklabels(panels, rotation=30, ha="right")
ax.set_yticks(range(len(tests)))
ax.set_yticklabels(tests)
ax.set_title("Localization of centered vertical individuality in original positive systems")

for i, test in enumerate(tests):
    for j, panel in enumerate(panels):
        rec = records.get((test, panel))
        if rec is None:
            ax.text(j, i, "NE", ha="center", va="center", fontsize=8)
        else:
            label = f"{rec['excess']:+.2f}\np={rec['p']:.4f}"
            if rec["status"] != "PASS":
                label += "\nunresolved"
            ax.text(j, i, label, ha="center", va="center", fontsize=7)

cb = fig.colorbar(im, ax=ax)
cb.set_label("Null-calibrated centered identity excess (nats/fix)")
ax.text(
    0.0, -0.18,
    "NE = structurally non-evaluable under the frozen support gate. "
    "Cells summarize post-freeze stress tests, not independent confirmation.",
    transform=ax.transAxes, ha="left", va="top", fontsize=8
)
fig.tight_layout()
fig.savefig(OUT)
print(OUT)
