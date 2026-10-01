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
        for k in ["observed", "null_mean", "q025", "q975", "calibrated_excess", "p_upper"]:
            r[k] = float(r[k])
        r["n"] = int(r["n"])
        r["null_low_centered"] = r["q025"] - r["null_mean"]
        r["null_high_centered"] = r["q975"] - r["null_mean"]
        rows.append(r)

def panel_label(panel, n):
    if panel == "Tadarida teniotis":
        s = r"$\it{Tadarida\ teniotis}$"
    elif panel == "Eidolon helvum":
        s = r"$\it{Eidolon\ helvum}$"
    elif panel == "Hypsignathus monstrosus":
        s = r"$\it{Hypsignathus\ monstrosus}$"
    elif panel.startswith("Phyllostomus hastatus"):
        year = panel.rsplit(" ", 1)[-1]
        s = rf"$\it{{Phyllostomus\ hastatus}}$ {year}"
    else:
        s = panel
    return f"{s}  (n={n})"

ys = list(range(len(rows), 0, -1))
fig, ax = plt.subplots(figsize=(8.6, 4.9))

for y, r in zip(ys, rows):
    ax.hlines(y, r["null_low_centered"], r["null_high_centered"], linewidth=2)
    marker = "o" if r["verdict"] == "PASS" else "x"
    ax.scatter(r["calibrated_excess"], y, s=70, marker=marker, zorder=3)

ax.axvline(0, linewidth=1)
ax.set_yticks(ys)
ax.set_yticklabels([panel_label(r["panel"], r["n"]) for r in rows])
ax.set_xlim(-0.75, 0.70)
ax.set_xlabel("Null-calibrated centered vertical identity excess (nats/fix)")
ax.set_title("Centered vertical-distribution individuality in the original archive")
ax.set_ylim(0.5, len(rows) + 0.5)

ax.plot([], [], linestyle="-", linewidth=2, label="central 95% permutation-null interval")
ax.scatter([], [], marker="o", label="met pre-specified criterion")
ax.scatter([], [], marker="x", label="did not meet pre-specified criterion")
ax.legend(loc="lower right", fontsize=8, frameon=False)

fig.tight_layout()
fig.savefig(OUT)
print(OUT)
