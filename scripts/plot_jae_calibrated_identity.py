#!/usr/bin/env python3
"""Submission figures for calibrated vertical-identity manuscript v0.3.4."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"results"/"calibrated_vertical_identity_v0_3_4.csv"
RESULTS=ROOT/"results"
OUT=ROOT/"figures"/"submission_v0_3_4"
OUT.mkdir(parents=True,exist_ok=True)

def rows():
    with DATA.open(newline="",encoding="utf-8") as fh:
        return list(csv.DictReader(fh))

def save(fig,stem):
    fig.tight_layout()
    fig.savefig(OUT/f"{stem}.pdf")
    fig.savefig(OUT/f"{stem}.png",dpi=240)
    plt.close(fig)

def conceptual():
    fig,ax=plt.subplots(figsize=(8.3,5.1))
    ax.set_xlim(0,10); ax.set_ylim(0,7); ax.axis("off")
    boxes=[
        (0.4,4.7,2.4,1.2,"Observed movement\nx, y, z"),
        (3.4,5.0,2.5,1.0,"Horizontal fidelity\nwhere the bat flies"),
        (3.4,3.4,2.5,1.0,"Vertical identity\nwhich z states it uses"),
        (6.6,4.2,2.8,1.3,"Common-cell standardization\nsame horizontal weights\nfor self and other"),
        (6.6,1.6,2.8,1.2,"Residual vertical identity\nbeyond horizontal fidelity"),
    ]
    for x,y,w,h,label in boxes:
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.05",fill=False,linewidth=1.2))
        ax.text(x+w/2,y+h/2,label,ha="center",va="center",fontsize=10)
    arrows=[
        ((2.8,5.3),(3.4,5.5)),
        ((2.8,5.0),(3.4,3.9)),
        ((5.9,5.5),(6.6,4.9)),
        ((5.9,3.9),(6.6,4.5)),
        ((8.0,4.2),(8.0,2.8)),
    ]
    for a,b in arrows:
        ax.annotate("",xy=b,xytext=a,arrowprops={"arrowstyle":"->","linewidth":1.0})
    ax.text(0.4,1.0,
        "Question: does the same individual retain predictive vertical information\n"
        "after horizontal cell-use differences are held constant?",
        fontsize=9)
    ax.set_title("Separating vertical individuality from horizontal space-use fidelity")
    save(fig,"figure1_conceptual_standardization")

def focal():
    v1=json.loads((RESULTS/"individual_vertical_strategy_result_v1.json").read_text())
    v2=json.loads((RESULTS/"spatial_interaction_refinement_result_v2.json").read_text())
    ids=list(v2["primary"]["individual_ids"])
    short=[f"Bat{i+1}" for i in range(len(ids))]
    total=v1["primary"]["individual_total_identity_advantage"]
    residual=v2["primary"]["individual_diagonal_spatial_residual_gain"]
    x=list(range(len(ids)))
    fig,ax=plt.subplots(figsize=(7.2,5.0))
    ax.plot(x,[float(total[i]) for i in ids],marker="o",label="Early → late individual identity")
    ax.plot(x,[float(residual[i]) for i in ids],marker="o",label="Residual cell × height after marginal adjustment")
    ax.axhline(0,linewidth=0.8)
    ax.set_xticks(x,short)
    ax.set_ylabel("Held-out log-score gain (nats/event)")
    ax.set_title("Focal vertical identity repeats, but a fixed residual map is not established")
    ax.legend(frameon=False)
    ax.text(0.02,0.98,"Identity assignment p = 0.000174\nResidual-map p = 0.160",
            transform=ax.transAxes,ha="left",va="top",fontsize=9)
    save(fig,"figure2_focal_identity_boundary")

def observed_vs_null(field_obs,field_null,lo_field,hi_field,ylabel,title,stem):
    rr=rows()
    labels=[r["label"] for r in rr]
    x=list(range(len(rr)))
    obs=[float(r[field_obs]) for r in rr]
    null=[float(r[field_null]) for r in rr]
    lo=[float(r[lo_field]) for r in rr]
    hi=[float(r[hi_field]) for r in rr]
    err_low=[o-l for o,l in zip(obs,lo)]
    err_high=[h-o for o,h in zip(obs,hi)]
    fig,ax=plt.subplots(figsize=(8.0,5.3))
    ax.errorbar(x,obs,yerr=[err_low,err_high],fmt="o",capsize=3,label="Observed (individual bootstrap 95%)")
    ax.scatter(x,null,marker="x",s=65,label="Session-label permutation null mean")
    for i in x:
        ax.plot([i,i],[null[i],obs[i]],linewidth=0.8)
    ax.axhline(0,linewidth=0.8)
    ax.set_xticks(x,labels,rotation=22,ha="right")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(frameon=False,fontsize=8)
    save(fig,stem)

def marginal_identity():
    observed_vs_null(
        "common_cell_marginal","common_cell_marginal_null_mean",
        "common_cell_marginal_boot_lo","common_cell_marginal_boot_hi",
        "Common-cell vertical identity (nats/fix)",
        "Vertical individual identity remains after horizontal cell-use standardization",
        "figure3_common_cell_vertical_identity"
    )

def conditional_increment():
    observed_vs_null(
        "common_cell_advantage","common_cell_advantage_null_mean",
        "common_cell_advantage_boot_lo","common_cell_advantage_boot_hi",
        "Additional cell-conditioned identity (nats/fix)",
        "Additional cell-conditioned information is small but exceeds the estimator null",
        "figure4_calibrated_conditional_increment"
    )

def decomposition_shift():
    rr=rows()
    labels=[r["label"] for r in rr]
    x=list(range(len(rr)))
    ordinary=[float(r["ordinary_advantage"]) for r in rr]
    standardized=[float(r["common_cell_advantage"]) for r in rr]
    fig,ax=plt.subplots(figsize=(8.0,5.3))
    ax.plot(x,ordinary,marker="o",label="Original conditional advantage")
    ax.plot(x,standardized,marker="o",label="After common-cell standardization")
    ax.axhline(0,linewidth=0.8)
    ax.set_xticks(x,labels,rotation=22,ha="right")
    ax.set_ylabel("Conditional − marginal identity (nats/fix)")
    ax.set_title("Horizontal standardization removes the apparent 2022 marginal-dominant contrast")
    ax.legend(frameon=False)
    save(fig,"figure5_decomposition_shift")

def main():
    conceptual()
    focal()
    marginal_identity()
    conditional_increment()
    decomposition_shift()
    print(OUT)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
