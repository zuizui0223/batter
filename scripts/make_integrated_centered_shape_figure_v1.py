#!/usr/bin/env python3
from pathlib import Path
import csv
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "figures" / "integrated_centered_shape_v1.csv"
OUT = ROOT / "figures" / "integrated_centered_shape_v1.svg"

rows = []
with DATA.open(newline="", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        for k in ["observed", "null_mean", "calibrated_excess", "p_upper"]:
            r[k] = float(r[k])
        r["n"] = int(r["n"])
        rows.append(r)

ys = list(range(len(rows), 0, -1))
fig, ax = plt.subplots(figsize=(8.0, 4.8))

for y, r in zip(ys, rows):
    marker = "o" if r["verdict"] == "PASS" else "x"
    ax.scatter(r["calibrated_excess"], y, s=70, marker=marker)

ax.axvline(0, linewidth=1)
ax.set_yticks(ys)
ax.set_yticklabels([f"{r['panel']}  (n={r['n']})" for r in rows])
ax.set_xlim(-0.08, 0.64)
ax.set_xlabel("Null-calibrated centered vertical identity excess (nats/fix)")
ax.set_title("Centered vertical-distribution individuality in the original archive")
ax.set_ylim(0.5, len(rows) + 0.5)

fig.tight_layout()
fig.savefig(OUT)
print(OUT)
