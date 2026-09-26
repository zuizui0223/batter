#!/usr/bin/env python3
"""Figure-ready architecture plane for the frozen v0.3 paper programme."""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "results" / "architecture_primary_v0_3.csv"
OUT = ROOT / "figures" / "architecture_plane_v0_3.pdf"

LABELS = {
    "tadarida_msl": "T. teniotis (MSL)",
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

    fig, ax = plt.subplots(figsize=(7.2, 5.8))
    for row in rows:
        x = float(row["marginal_identity_nats_per_fix"])
        y = float(row["place_x_height_nats_per_fix"])
        ax.scatter(x, y, s=55)
        ax.annotate(
            LABELS[row["panel_id"]],
            (x, y),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
        )

    ax.axhline(0.0, linewidth=0.8)
    ax.axvline(0.0, linewidth=0.8)
    ax.set_xlabel("Marginal-height identity gain (nats/fix)")
    ax.set_ylabel("Conditional advantage = conditional − marginal (nats/fix)")
    ax.set_title("Predictive architectures of cross-night vertical identity")
    ax.text(
        0.98, 0.97, "conditional-dominant",
        transform=ax.transAxes, ha="right", va="top", fontsize=9,
    )
    ax.text(
        0.98, 0.03, "marginal-dominant",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=9,
    )
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
