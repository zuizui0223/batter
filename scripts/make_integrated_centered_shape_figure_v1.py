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

def panel_label(panel):
    if panel == "Tadarida teniotis":
        return r"$\it{Tadarida\ teniotis}$"
    if panel == "Eidolon helvum":
        return r"$\it{Eidolon\ helvum}$"
    if panel == "Hypsignathus monstrosus":
        return r"$\it{Hypsignathus\ monstrosus}$"
    if panel.startswith("Phyllostomus hastatus"):
        year = panel.rsplit(" ", 1)[-1]
        return rf"$\it{{Phyllostomus\ hastatus}}$ {year}"
    return panel

ys = list(range(len(rows), 0, -1))
fig, ax = plt.subplots(figsize=(8.8, 5.8))

for y, r in zip(ys, rows):
    ax.hlines(y, r["null_low_centered"], r["null_high_centered"], linewidth=2)
    marker = "o" if r["verdict"] == "PASS" else "x"
    ax.scatter(r["calibrated_excess"], y, s=70, marker=marker, zorder=3)
    ax.annotate(
        f"n={r['n']}", xy=(0, y), xycoords=("axes fraction", "data"),
        xytext=(-6, 0), textcoords="offset points",
        ha="right", va="center", fontsize=8
    )

ax.axvline(0, linewidth=1)
ax.set_yticks(ys)
ax.set_yticklabels([panel_label(r["panel"]) for r in rows])
ax.tick_params(axis="y", pad=42)
ax.set_xlim(-0.75, 0.70)
ax.set_xlabel("Null-calibrated centered vertical identity excess (nats/fix)")
ax.set_title("Centered vertical-distribution individuality in the original archive")
ax.set_ylim(0.5, len(rows) + 0.5)

ax.plot([], [], linestyle="-", linewidth=2, label="central 95% permutation-null interval")
ax.scatter([], [], marker="o", label="met pre-specified criterion")
ax.scatter([], [], marker="x", label="did not meet pre-specified criterion")
ax.legend(
    loc="upper center", bbox_to_anchor=(0.5, -0.17),
    ncol=3, fontsize=8, frameon=False
)

fig.subplots_adjust(left=0.34, right=0.98, top=0.90, bottom=0.25)
fig.savefig(OUT)
print(OUT)
