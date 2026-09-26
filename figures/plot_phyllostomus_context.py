#!/usr/bin/env python3
"""Within-species architecture contrast for Phyllostomus hastatus."""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "results" / "architecture_primary_v0_3.csv"
OUT = ROOT / "figures" / "phyllostomus_context_v0_3.pdf"

ORDER = ["phyllostomus_2016", "phyllostomus_2022", "phyllostomus_2023"]
LABELS = {
    "phyllostomus_2016": "2016 La Gruta",
    "phyllostomus_2022": "2022",
    "phyllostomus_2023": "2023",
}


def main() -> int:
    with INPUT.open(newline="", encoding="utf-8") as fh:
        all_rows = {r["panel_id"]: r for r in csv.DictReader(fh)}
    rows = [all_rows[x] for x in ORDER]

    x = range(len(rows))
    marginal = [float(r["marginal_identity_nats_per_fix"]) for r in rows]
    interaction = [float(r["place_x_height_nats_per_fix"]) for r in rows]

    fig, ax = plt.subplots(figsize=(6.6, 5.2))
    ax.plot(x, marginal, marker="o", label="Marginal-height identity")
    ax.plot(x, interaction, marker="o", label="Conditional advantage")
    ax.axhline(0.0, linewidth=0.8)
    ax.set_xticks(list(x), [LABELS[r["panel_id"]] for r in rows])
    ax.set_ylabel("Identity information (nats/fix)")
    ax.set_title("Within-species variation in vertical identity architecture")
    ax.legend(frameon=False)
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
