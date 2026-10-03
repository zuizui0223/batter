#!/usr/bin/env python3
"""Generate JAE submission figures for calibrated vertical identity v0.4.0."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/"results"
MAIN_OUT=ROOT/"figures"/"submission_v0_4_0"
SI_OUT=ROOT/"figures"/"supporting_v0_4_0"
MAIN_OUT.mkdir(parents=True,exist_ok=True)
SI_OUT.mkdir(parents=True,exist_ok=True)

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

def save(fig,stem,outdir=MAIN_OUT):
    fig.tight_layout()
    fig.savefig(outdir/f"{stem}.pdf")
    fig.savefig(outdir/f"{stem}.png",dpi=240)
    plt.close(fig)

def fig1():
    fig,ax=plt.subplots(figsize=(9.0,6.4))
    ax.set_xlim(0,12); ax.set_ylim(0,9); ax.axis("off")

    boxes=[
        (0.4,6.7,2.5,1.2,"Apparent individual\nvertical differences"),
        (3.5,6.7,2.7,1.2,"Remove simple alternatives\ncommon horizontal weights\n+ session centering"),
        (6.9,6.7,2.7,1.2,"Persistent individual\nvertical organization"),
        (1.0,3.7,3.2,1.55,"Persistence diagnostics\nterrain-relative: 4/4\nmulti-day + 500-m place × state"),
        (7.0,3.7,3.2,1.55,"Partitioning diagnostics\npositive S_rel: 0/4\nco-use separation: 1/4"),
        (4.25,1.0,3.5,1.65,"Ecological synthesis\npersonal solutions persist\nwithout exclusive vertical niches"),
    ]
    for x,y,w,h,label in boxes:
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.06",fill=False,linewidth=1.2))
        ax.text(x+w/2,y+h/2,label,ha="center",va="center",fontsize=9.5)

    arrows=[
        ((2.9,7.3),(3.5,7.3)),
        ((6.2,7.3),(6.9,7.3)),
        ((8.25,6.7),(2.6,5.25)),
        ((8.25,6.7),(8.6,5.25)),
        ((2.6,3.7),(5.55,2.65)),
        ((8.6,3.7),(6.45,2.65)),
    ]
    for start,end in arrows:
        ax.annotate("",xy=end,xytext=start,arrowprops={"arrowstyle":"->","linewidth":1.0})

    ax.text(0.55,0.18,
            "Origin and maintenance are distinct: processes may generate individual specialization without\n"
            "requiring ongoing vertical exclusion to keep personal strategies predictive across bouts.",
            fontsize=9.2)
    ax.set_title("From vertical individuality to maintenance without exclusive spatial partitioning")
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
    ax.set_title("Motivating Tadarida identity repeats, but a fixed residual map is not established")
    ax.legend(frameon=False)
    ax.text(0.02,0.98,"Identity assignment p = 0.000174\nResidual-map p = 0.160",
            transform=ax.transAxes,ha="left",va="top",fontsize=9)
    save(fig,"supporting_figure_S1_focal_identity_boundary",SI_OUT)

def fig3():
    rr=read_csv("calibrated_vertical_identity_v0_3_8.csv")
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
    save(fig,"figure2_common_cell_vertical_identity")

def fig4():
    rr=read_csv("calibrated_vertical_identity_v0_3_8.csv")
    x=list(range(len(rr)))
    obs=[float(r["pairwise_self_win"]) for r in rr]
    null=[float(r["pairwise_null_mean"]) for r in rr]
    lo=[float(r["pairwise_boot_lo"]) for r in rr]
    hi=[float(r["pairwise_boot_hi"]) for r in rr]
    fig,ax=plt.subplots(figsize=(8.3,5.0))
    ax.errorbar(x,obs,yerr=[[o-l for o,l in zip(obs,lo)],[h-o for o,h in zip(obs,hi)]],fmt="o",capsize=3,label="Observed self-win")
    ax.scatter(x,null,marker="x",s=70,label="Permutation null mean")
    for i in x:
        ax.plot([i,i],[null[i],obs[i]],linewidth=0.8)
    ax.axhline(0.5,linewidth=0.7,linestyle="--")
    ax.set_ylim(0.4,1.0)
    ax.set_xticks(x,[r["label"] for r in rr],rotation=22,ha="right")
    ax.set_ylabel("Pairwise self-identification fraction")
    ax.set_title("Pairwise individuality must be judged against panel-specific nulls")
    ax.text(0.02,0.04,"Dashed 0.5 line is intuitive only",transform=ax.transAxes,fontsize=8)
    ax.legend(frameon=False,fontsize=8)
    save(fig,"figure3_pairwise_self_identification")

def fig5():
    rr=read_csv("calibrated_vertical_identity_v0_3_8.csv")
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
    save(fig,"supporting_figure_S2_architecture_correction",SI_OUT)

def fig6():
    rr=read_csv("endpoint_exclusion_v0_3_8.csv")
    x=list(range(len(rr)))
    obs=[float(r["observed"]) for r in rr]
    null=[float(r["null_mean"]) for r in rr]
    fig,ax=plt.subplots(figsize=(8.5,5.2))
    ax.scatter(x,obs,marker="o",label="Observed after 1-km exclusion")
    ax.scatter(x,null,marker="x",s=70,label="Permutation null mean")
    for i,r in enumerate(rr):
        ax.plot([i,i],[null[i],obs[i]],linewidth=0.8)
        verdict="PASS" if r["passes"]=="true" else ("FAIL n" if r["fail_reason"]=="n_gate" else "FAIL p")
        ax.text(i,max(obs[i],null[i])+0.025,verdict,ha="center",fontsize=8)
    ax.set_ylim(min(null)-0.03,max(obs)+0.075)
    ax.axhline(0,linewidth=0.8)
    ax.set_xticks(x,[r["label"] for r in rr],rotation=24,ha="right")
    ax.set_ylabel("Common-cell vertical identity (nats/fix)")
    ax.set_title("Endpoint-neighbourhood exclusion gives panel-dependent robustness")
    ax.legend(frameon=False,fontsize=8)
    save(fig,"figure4_endpoint_exclusion")

def fig7():
    rr=read_csv("tag_altitude_bias_shape_v1.csv")
    labels={
        "tadarida":"T. teniotis",
        "eidolon":"E. helvum",
        "hypsignathus":"H. monstrosus",
        "phyllostomus_2022":"P. hastatus 2022",
        "phyllostomus_2023":"P. hastatus 2023",
        "phyllostomus_2016":"P. hastatus 2016",
    }
    x=list(range(len(rr)))
    obs=[float(r["centered_observed"]) for r in rr]
    null=[float(r["null_mean"]) for r in rr]
    fig,ax=plt.subplots(figsize=(8.5,5.2))
    ax.scatter(x,obs,marker="o",label="Observed centered-shape identity")
    ax.scatter(x,null,marker="x",s=70,label="Permutation null mean")
    for i,r in enumerate(rr):
        ax.plot([i,i],[null[i],obs[i]],linewidth=0.8)
        ax.text(i,max(obs[i],null[i])+0.035,"PASS" if r["passes"]=="true" else "FAIL",ha="center",fontsize=8)
    ax.set_ylim(min(null)-0.08,max(obs)+0.12)
    ax.axhline(0,linewidth=0.8)
    ax.set_xticks(x,[labels[r["panel_id"]] for r in rr],rotation=24,ha="right")
    ax.set_ylabel("Centered-shape identity (nats/fix)")
    ax.set_title("All five comparative panels retain vertical-distribution shape after altitude centering")
    ax.legend(frameon=False,fontsize=8)
    save(fig,"figure5_shift_invariant_shape")

def main():
    fig1(); fig2(); fig3(); fig4(); fig5(); fig6(); fig7()
    print(MAIN_OUT)
    print(SI_OUT)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
