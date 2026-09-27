#!/usr/bin/env python3
"""Generate JAE submission figures for calibrated vertical identity v0.3.4."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/"results"
OUT=ROOT/"figures"/"submission_v0_3_4"
OUT.mkdir(parents=True,exist_ok=True)

SHORT={
    "Bat1_3D6001852B958":"Bat1",
    "Bat2_3D6001852B95D":"Bat2",
    "Bat3_3D6001852B978":"Bat3",
    "Bat4_3D6001852B980":"Bat4",
    "Bat5_3D6001852B98C":"Bat5",
    "Bat6_3D6001852B98E":"Bat6",
    "Bat7_3D6001852B9A3":"Bat7",
    "Bat8_3D6001852B9A7":"Bat8",
}

def read_csv(path):
    with (RESULTS/path).open(newline="",encoding="utf-8") as fh:
        return list(csv.DictReader(fh))

def save(fig,stem):
    fig.tight_layout()
    fig.savefig(OUT/f"{stem}.pdf")
    fig.savefig(OUT/f"{stem}.png",dpi=240)
    plt.close(fig)

def fig1():
    fig,ax=plt.subplots(figsize=(8.4,5.4))
    ax.set_xlim(0,10); ax.set_ylim(0,7); ax.axis("off")
    boxes=[
        (0.4,4.8,2.2,1.1,"Repeated 3-D movement\n(x, y, z)"),
        (3.1,5.1,2.3,1.0,"Horizontal occupancy\nwhere the bat flies"),
        (3.1,3.5,2.3,1.0,"Vertical profile\nwhich z states it uses"),
        (6.1,4.2,3.2,1.5,"Common-cell counterfactual\napply the same horizontal weights\nto self and other vertical profiles"),
        (6.5,1.6,2.4,1.1,"Held-out vertical identity\nbeyond cell occupancy"),
    ]
    for x,y,w,h,label in boxes:
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.05",fill=False,linewidth=1.2))
        ax.text(x+w/2,y+h/2,label,ha="center",va="center",fontsize=10)
    for a,b in [
        ((2.6,5.35),(3.1,5.55)),((2.6,5.05),(3.1,4.0)),
        ((5.4,5.55),(6.1,4.9)),((5.4,4.0),(6.1,4.6)),
        ((7.7,4.2),(7.7,2.7)),
    ]:
        ax.annotate("",xy=b,xytext=a,arrowprops={"arrowstyle":"->","linewidth":1.0})
    ax.text(0.4,1.0,
            "Key alternative: apparent vertical individuality can arise when individuals repeatedly use\n"
            "different horizontal patches with different terrain or vertical opportunity.",
            fontsize=9)
    ax.set_title("Testing vertical individuality after horizontal occupancy standardization")
    save(fig,"figure1_horizontal_standardization")

def fig2():
    v1=json.loads((RESULTS/"individual_vertical_strategy_result_v1.json").read_text())
    v2=json.loads((RESULTS/"spatial_interaction_refinement_result_v2.json").read_text())
    ids=list(v2["primary"]["individual_ids"])
    total=v1["primary"]["individual_total_identity_advantage"]
    residual=v2["primary"]["individual_diagonal_spatial_residual_gain"]
    x=list(range(len(ids)))
    fig,ax=plt.subplots(figsize=(7.3,5.0))
    ax.plot(x,[float(total[i]) for i in ids],marker="o",label="Early → late identity gain")
    ax.plot(x,[float(residual[i]) for i in ids],marker="o",label="Residual cell × height gain")
    ax.axhline(0,linewidth=0.8)
    ax.set_xticks(x,[SHORT.get(i,i.split("_")[0]) for i in ids])
    ax.set_ylabel("Held-out log-score gain (nats/event)")
    ax.set_title("Focal identity repeats, but a fixed residual map is not established")
    ax.legend(frameon=False)
    ax.text(0.02,0.98,"Identity assignment p = 0.000174\nResidual-map p = 0.160",
            transform=ax.transAxes,ha="left",va="top",fontsize=9)
    save(fig,"figure2_focal_identity_boundary")

def fig3():
    rr=read_csv("calibrated_vertical_identity_v0_3_4.csv")
    x=list(range(len(rr)))
    obs=[float(r["common_cell_marginal"]) for r in rr]
    null=[float(r["null_common_cell_marginal"]) for r in rr]
    lo=[float(r["common_cell_marginal_boot_lo"]) for r in rr]
    hi=[float(r["common_cell_marginal_boot_hi"]) for r in rr]
    fig,ax=plt.subplots(figsize=(8.3,5.3))
    ax.errorbar(x,obs,yerr=[[o-l for o,l in zip(obs,lo)],[h-o for o,h in zip(obs,hi)]],
                fmt="o",capsize=3,label="Observed common-cell identity")
    ax.scatter(x,null,marker="x",s=70,label="Session-label permutation null mean")
    for i in x:
        ax.plot([i,i],[null[i],obs[i]],linewidth=0.8)
    ax.axhline(0,linewidth=0.8)
    ax.set_xticks(x,[r["label"] for r in rr],rotation=22,ha="right")
    ax.set_ylabel("Log-score identity (nats/fix)")
    ax.set_title("Vertical identity exceeds exchangeability after common horizontal weighting")
    ax.legend(frameon=False,fontsize=8)
    save(fig,"figure3_common_cell_vertical_identity")

def fig4():
    rr=read_csv("calibrated_vertical_identity_v0_3_4.csv")
    x=list(range(len(rr)))
    obs=[float(r["pairwise_self_win"]) for r in rr]
    lo=[float(r["pairwise_boot_lo"]) for r in rr]
    hi=[float(r["pairwise_boot_hi"]) for r in rr]
    fig,ax=plt.subplots(figsize=(8.3,5.0))
    ax.errorbar(x,obs,yerr=[[o-l for o,l in zip(obs,lo)],[h-o for o,h in zip(obs,hi)]],fmt="o",capsize=3)
    ax.axhline(0.5,linewidth=0.8,linestyle="--")
    ax.set_ylim(0.4,1.0)
    ax.set_xticks(x,[r["label"] for r in rr],rotation=22,ha="right")
    ax.set_ylabel("Pairwise self-identification fraction")
    ax.set_title("Same-bat vertical profiles usually outpredict specific alternatives")
    ax.text(0.02,0.04,"0.5 is an intuitive reference only; no new significance test",transform=ax.transAxes,fontsize=8)
    save(fig,"figure4_pairwise_self_identification")

def fig5():
    rr=read_csv("calibrated_vertical_identity_v0_3_4.csv")
    x=list(range(len(rr)))
    old=[float(r["ordinary_advantage"]) for r in rr]
    new=[float(r["common_cell_advantage"]) for r in rr]
    fig,ax=plt.subplots(figsize=(8.3,5.1))
    ax.plot(x,old,marker="o",label="Original conditional − marginal")
    ax.plot(x,new,marker="o",label="After common-cell standardization")
    ax.axhline(0,linewidth=0.8)
    ax.set_xticks(x,[r["label"] for r in rr],rotation=22,ha="right")
    ax.set_ylabel("Conditional increment (nats/fix)")
    ax.set_title("Horizontal standardization removes the apparent 2022 architecture contrast")
    ax.legend(frameon=False)
    save(fig,"figure5_architecture_correction")

def fig6():
    rr=read_csv("tadarida_focal_robustness_v0_3_4.csv")
    x=list(range(len(rr)))
    obs=[float(r["common_cell_marginal"]) for r in rr]
    null=[float(r["null_mean"]) for r in rr]
    lo=[float(r["boot_lo"]) for r in rr]
    hi=[float(r["boot_hi"]) for r in rr]
    fig,ax=plt.subplots(figsize=(8.5,5.2))
    ax.errorbar(x,obs,yerr=[[o-l for o,l in zip(obs,lo)],[h-o for o,h in zip(obs,hi)]],fmt="o",capsize=3,label="Observed AGL identity")
    ax.scatter(x,null,marker="x",s=70,label="Permutation null mean")
    for i,r in enumerate(rr):
        ax.plot([i,i],[null[i],obs[i]],linewidth=0.8)
        ax.text(i, max(obs[i],null[i])+0.08, "PASS" if r["passes"]=="true" else "FAIL",ha="center",fontsize=8)
    ax.axhline(0,linewidth=0.8)
    ax.set_xticks(x,[r["label"] for r in rr],rotation=24,ha="right")
    ax.set_ylabel("Common-cell AGL identity (nats/fix)")
    ax.set_title("Focal terrain-relative identity is scale-dependent and endpoint-sensitive")
    ax.legend(frameon=False,fontsize=8)
    save(fig,"figure6_focal_robustness")

def main():
    fig1(); fig2(); fig3(); fig4(); fig5(); fig6()
    print(OUT)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
