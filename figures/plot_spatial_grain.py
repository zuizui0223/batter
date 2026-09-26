#!/usr/bin/env python3
"""Exploratory spatial-grain figure for the frozen v0.3 programme."""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "results" / "spatial_grain_v0_3.csv"
OUT = ROOT / "figures" / "spatial_grain_v0_3.pdf"

LABELS = {
    "tadarida_agl": "T. teniotis (AGL)",
    "eidolon": "E. helvum",
    "hypsignathus": "H. monstrosus",
    "phyllostomus_2022": "P. hastatus 2022",
    "phyllostomus_2023": "P. hastatus 2023",
    "phyllostomus_2016": "P. hastatus 2016",
}


def main() -> int:
    with INPUT.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    groups = defaultdict(list)
    for row in rows:
        groups[row["panel_id"]].append(row)

    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    for panel_id, values in groups.items():
        values.sort(key=lambda r: float(r["cell_size_m"]))
        x = [float(r["cell_size_m"]) / 1000.0 for r in values]
        y = [float(r["conditional_identity_nats_per_fix"]) for r in values]
        ax.plot(x, y, marker="o", label=LABELS[panel_id])

    ax.axhline(0.0, linewidth=0.8)
    ax.set_xlabel("Horizontal conditioning cell size (km)")
    ax.set_ylabel("Conditional identity gain (nats/fix)")
    ax.set_xticks([2.5, 5.0, 10.0])
    ax.set_title("Spatial grain of cross-night vertical individuality")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
