#!/usr/bin/env python3
"""Submission figures for the frozen v0.3.1/v0.3.2 batter manuscript."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT = ROOT / "figures" / "submission_v0_3_2"
OUT.mkdir(parents=True, exist_ok=True)

SHORT = {
    "Bat1_3D6001852B958": "Bat1",
    "Bat2_3D6001852B95D": "Bat2",
    "Bat3_3D6001852B978": "Bat3",
    "Bat4_3D6001852B980": "Bat4",
    "Bat5_3D6001852B98C": "Bat5",
    "Bat6_3D6001852B98E": "Bat6",
    "Bat7_3D6001852B9A3": "Bat7",
    "Bat8_3D6001852B9A7": "Bat8",
}

PANEL_LABEL = {
    "tadarida_msl": "T. teniotis (MSL)",
    "tadarida_agl": "T. teniotis (AGL)",
    "eidolon": "E. helvum",
    "hypsignathus": "H. monstrosus",
    "phyllostomus_2022": "P. hastatus 2022",
    "phyllostomus_2023": "P. hastatus 2023",
    "phyllostomus_2016": "P. hastatus 2016",
}


def read_csv(name: str):
    with (RESULTS / name).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def save(fig, stem: str):
    fig.tight_layout()
    fig.savefig(OUT / f"{stem}.pdf")
    fig.savefig(OUT / f"{stem}.png", dpi=240)
    plt.close(fig)


def focal_reconciliation():
    v1 = json.loads((RESULTS / "individual_vertical_strategy_result_v1.json").read_text())
    v2 = json.loads((RESULTS / "spatial_interaction_refinement_result_v2.json").read_text())
    ids = list(v2["primary"]["individual_ids"])
    total = v1["primary"]["individual_total_identity_advantage"]
    residual = v2["primary"]["individual_diagonal_spatial_residual_gain"]

    x = list(range(len(ids)))
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    ax.plot(x, [float(total[i]) for i in ids], marker="o", label="Conditional identity vs population")
    ax.plot(x, [float(residual[i]) for i in ids], marker="o", label="Residual cell × height after marginal adjustment")
    ax.axhline(0.0, linewidth=0.8)
    ax.set_xticks(x, [SHORT[i] for i in ids])
    ax.set_ylabel("Held-out log-score gain (nats/event)")
    ax.set_title("Focal repeatable identity and the stronger residual-map test")
    ax.legend(frameon=False)
    ax.text(
        0.02, 0.98,
        "Identity assignment: p = 0.000174\nResidual-map test: p = 0.160",
        transform=ax.transAxes, ha="left", va="top", fontsize=9,
    )
    save(fig, "figure2_focal_reconciliation")


def architecture_plane():
    rows = read_csv("architecture_primary_v0_3.csv")
    fig, ax = plt.subplots(figsize=(7.2, 5.7))
    for r in rows:
        x = float(r["marginal_identity_nats_per_fix"])
        y = float(r["place_x_height_nats_per_fix"])  # frozen column; interpreted as conditional advantage
        ax.scatter(x, y, s=65)
        ax.annotate(PANEL_LABEL[r["panel_id"]], (x, y), xytext=(5, 5), textcoords="offset points", fontsize=8)
    ax.axhline(0.0, linewidth=0.8)
    ax.axvline(0.0, linewidth=0.8)
    ax.set_xlabel("Marginal identity gain (nats/fix)")
    ax.set_ylabel("Conditional advantage (conditional − marginal; nats/fix)")
    ax.set_title("Predictive architectures of cross-night vertical identity")
    ax.text(0.98, 0.97, "conditional-dominant", transform=ax.transAxes, ha="right", va="top", fontsize=9)
    ax.text(0.98, 0.03, "marginal-dominant", transform=ax.transAxes, ha="right", va="bottom", fontsize=9)
    save(fig, "figure3_architecture_plane")


def pairwise_plane():
    rows = read_csv("architecture_pairwise_v0_3.csv")
    fig, ax = plt.subplots(figsize=(7.2, 5.7))
    for r in rows:
        x = float(r["marginal_pairwise_gain"])
        y = float(r["place_x_height_pairwise_gain"])  # frozen column; interpreted as conditional advantage
        ax.scatter(x, y, s=65)
        ax.annotate(PANEL_LABEL[r["panel_id"]], (x, y), xytext=(5, 5), textcoords="offset points", fontsize=8)
    ax.axhline(0.0, linewidth=0.8)
    ax.axvline(0.0, linewidth=0.8)
    ax.set_xlabel("Pairwise marginal self-vs-alternative gain (nats/fix)")
    ax.set_ylabel("Pairwise conditional advantage (nats/fix)")
    ax.set_title("Architecture direction persists without a pooled alternative baseline")
    save(fig, "figure4_pairwise_architecture")


def phyllostomus_context():
    rows = {r["panel_id"]: r for r in read_csv("architecture_primary_v0_3.csv")}
    order = ["phyllostomus_2016", "phyllostomus_2022", "phyllostomus_2023"]
    x = list(range(3))
    marg = [float(rows[k]["marginal_identity_nats_per_fix"]) for k in order]
    adv = [float(rows[k]["place_x_height_nats_per_fix"]) for k in order]
    labels = ["2016 La Gruta", "2022", "2023"]

    fig, ax = plt.subplots(figsize=(6.8, 5.0))
    ax.plot(x, marg, marker="o", label="Marginal identity")
    ax.plot(x, adv, marker="o", label="Conditional advantage")
    ax.axhline(0.0, linewidth=0.8)
    ax.set_xticks(x, labels)
    ax.set_ylabel("Predictive identity information (nats/fix)")
    ax.set_title("Phyllostomus architecture is not temporally fixed")
    ax.legend(frameon=False)
    ax.text(0.02, 0.02, "2016 prospective 2022-like prediction: not supported", transform=ax.transAxes, fontsize=8)
    save(fig, "figure5_phyllostomus_context")


def spatial_grain():
    rows = read_csv("spatial_grain_v0_3.csv")
    groups = {}
    for r in rows:
        groups.setdefault(r["panel_id"], []).append(r)

    fig, ax = plt.subplots(figsize=(7.2, 5.5))
    for panel_id, values in groups.items():
        values.sort(key=lambda r: float(r["cell_size_m"]))
        x = [float(r["cell_size_m"]) / 1000.0 for r in values]
        y = [float(r["conditional_identity_nats_per_fix"]) for r in values]
        ax.plot(x, y, marker="o", label=PANEL_LABEL[panel_id])
    ax.axhline(0.0, linewidth=0.8)
    ax.set_xlabel("Horizontal conditioning cell size (km)")
    ax.set_ylabel("Conditional identity gain (nats/fix)")
    ax.set_xticks([2.5, 5.0, 10.0])
    ax.set_title("Spatial grain is exploratory and system dependent")
    ax.legend(frameon=False, fontsize=8)
    save(fig, "figure6_spatial_grain")


def main() -> int:
    focal_reconciliation()
    architecture_plane()
    pairwise_plane()
    phyllostomus_context()
    spatial_grain()
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
