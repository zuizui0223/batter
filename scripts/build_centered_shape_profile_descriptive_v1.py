#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_cross_panel_estimator_calibration as cal
import scripts.run_tag_altitude_bias_shape as shape

CONTRACT=Path("contract/centered_shape_profile_descriptive_v1.json")
OUT_CSV=Path("results/centered_shape_individual_profiles_v1.csv")
OUT_JSON=Path("results/centered_shape_individual_profiles_v1.json")
FIG_DIR=Path("figures/submission_v0_3_7")
FIG_PDF=FIG_DIR/"figure6_individual_centered_shape_profiles.pdf"
FIG_PNG=FIG_DIR/"figure6_individual_centered_shape_profiles.png"

PANELS=(
    "eidolon",
    "hypsignathus",
    "phyllostomus_2022",
    "phyllostomus_2023",
    "phyllostomus_2016",
)
PANEL_LABELS={
    "eidolon":"E. helvum",
    "hypsignathus":"H. monstrosus",
    "phyllostomus_2022":"P. hastatus 2022",
    "phyllostomus_2023":"P. hastatus 2023",
    "phyllostomus_2016":"P. hastatus 2016",
}
BIN_LABELS=(
    "<-400",
    "-400:-200",
    "-200:-100",
    "-100:-50",
    "-50:0",
    "0:50",
    "50:100",
    "100:200",
    "200:400",
    ">400",
)


def group_conditional(A, labels):
    counts=A["counts"]
    L=len(A["label_names"])
    C=counts.shape[1]
    K=counts.shape[2]
    group_counts=np.zeros((L,C,K),dtype=np.int32)
    for lab in range(L):
        sel=np.flatnonzero(labels==lab)
        if len(sel):
            group_counts[lab]=counts[sel].sum(axis=0)
    group_cell_tot=group_counts.sum(axis=2)
    out=np.full((L,C,K),np.nan,dtype=float)
    for lab in range(L):
        pc=np.flatnonzero(group_cell_tot[lab]>0)
        if len(pc):
            out[lab,pc,:]=(group_counts[lab,pc,:]+cal.ALPHA)/(group_cell_tot[lab,pc,None]+cal.ALPHA*K)
    return out


def session_self_profiles(A, cohort_name):
    counts=A["counts"]
    cell_tot=A["cell_tot"]
    sess_cond=A["sess_cond"]
    labels=A["orig_labels"]
    group_cond=group_conditional(A,labels)
    idx_all=np.arange(len(A["sessions"]))
    rows=[]

    for t in range(len(A["sessions"])):
        lab=int(labels[t])
        self_sel=np.flatnonzero((labels==lab)&(idx_all!=t))
        if len(self_sel)==0:
            continue

        p_self=cal.mean_nan_axis0(sess_cond[self_sel])
        other_idx=np.array([x for x in range(len(A["label_names"])) if x!=lab],dtype=int)
        if len(other_idx)==0:
            continue
        p_other=cal.mean_nan_axis0(group_cond[other_idx])

        target_cell_tot=cell_tot[t]
        supported=(target_cell_tot>0)&(~np.isnan(p_self[:,0]))&(~np.isnan(p_other[:,0]))
        scored=int(target_cell_tot[supported].sum())
        if scored<cal.MIN_SCORED:
            continue

        supported_idx=np.flatnonzero(supported)
        weights=[]
        for s in self_sel:
            w=cell_tot[s,supported_idx].astype(float)
            total=w.sum()
            if total>0:
                weights.append(w/total)
        if not weights:
            continue

        w=np.mean(np.stack(weights),axis=0)
        w=w/w.sum()
        profile=np.sum(p_self[supported_idx,:]*w[:,None],axis=0)
        profile=profile/profile.sum()

        rows.append({
            "cohort":cohort_name,
            "session":A["sessions"][t],
            "individual":A["label_names"][lab],
            "scored_fixes":scored,
            "profile":profile,
        })
    return rows


def panel_profiles(panel):
    records,source=shape.panel_raw(panel)
    events_by_cohort,_=shape.centered_events(records)
    k=len(shape.EDGES)-1
    arrays={c:cal.make_cohort_arrays(e,k) for c,e in sorted(events_by_cohort.items())}

    # Exact evaluable target-session set from the frozen centered-shape estimator.
    observed,per_ind,session_rows=cal.observed_eval(arrays)
    expected_sessions={(r["cohort"],r["session"],r["individual"]) for r in session_rows}

    reconstructed=[]
    for cohort,A in arrays.items():
        reconstructed.extend(session_self_profiles(A,cohort))
    got_sessions={(r["cohort"],r["session"],r["individual"]) for r in reconstructed}
    if got_sessions!=expected_sessions:
        missing=sorted(expected_sessions-got_sessions)
        extra=sorted(got_sessions-expected_sessions)
        raise RuntimeError(f"{panel}: reconstructed target-session mismatch missing={missing[:3]} extra={extra[:3]}")

    by_ind=defaultdict(list)
    cohorts_by_ind=defaultdict(set)
    scored_by_ind=defaultdict(int)
    for row in reconstructed:
        by_ind[row["individual"]].append(row["profile"])
        cohorts_by_ind[row["individual"]].add(row["cohort"])
        scored_by_ind[row["individual"]]+=int(row["scored_fixes"])

    if set(by_ind)!=set(per_ind):
        raise RuntimeError(f"{panel}: individual set mismatch vs frozen centered-shape audit")

    rows=[]
    for iid in sorted(by_ind):
        mat=np.stack(by_ind[iid])
        p=mat.mean(axis=0)
        p=p/p.sum()
        rows.append({
            "panel":panel,
            "panel_label":PANEL_LABELS[panel],
            "individual":iid,
            "evaluable_sessions":len(by_ind[iid]),
            "cohorts":";".join(sorted(cohorts_by_ind[iid])),
            "total_scored_fixes_across_targets":scored_by_ind[iid],
            "upper_tail_mass_ge_100m":float(p[7:].sum()),
            "lower_tail_mass_le_minus100m":float(p[:3].sum()),
            "central_mass_minus50_to_50m":float(p[4:6].sum()),
            "profile":[float(x) for x in p],
        })

    req=json.loads(Path("contract/tag_altitude_bias_audit_v1.json").read_text(encoding="utf-8"))[
        "primary_shift_invariant_shape_test"
    ]["required_evaluable_individuals"][panel]
    if len(rows)!=int(req):
        raise RuntimeError(f"{panel}: descriptive n {len(rows)} != frozen evaluable n {req}")

    rows.sort(key=lambda r:(r["upper_tail_mass_ge_100m"],r["individual"]))
    return rows,source,observed


def write_outputs(all_rows,panel_meta):
    OUT_CSV.parent.mkdir(parents=True,exist_ok=True)
    fields=[
        "panel","panel_label","individual","row_order","evaluable_sessions","cohorts",
        "total_scored_fixes_across_targets",
        "lower_tail_mass_le_minus100m","central_mass_minus50_to_50m","upper_tail_mass_ge_100m",
    ]+[f"bin_{i}_{BIN_LABELS[i]}" for i in range(len(BIN_LABELS))]

    with OUT_CSV.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=fields)
        w.writeheader()
        for panel in PANELS:
            rows=[r for r in all_rows if r["panel"]==panel]
            for order,r in enumerate(rows,1):
                out={k:r[k] for k in fields if k in r}
                out["row_order"]=order
                for i,x in enumerate(r["profile"]):
                    out[f"bin_{i}_{BIN_LABELS[i]}"]=x
                w.writerow(out)

    payload={
        "study_id":"batter-centered-shape-profile-descriptive-v1",
        "contract":str(CONTRACT),
        "purpose":"descriptive visualization only; no new inferential endpoint",
        "centered_edges_m":list(shape.EDGES),
        "profile_definition":"equal-session mean of the exact common-cell standardized identity-matched self profiles used for evaluable target sessions in the frozen centered-shape audit",
        "row_order":"ascending upper-tail mass at residual height >=100 m; tie by individual identifier",
        "panels":panel_meta,
        "individual_profiles":[
            {
                **{k:v for k,v in r.items() if k!="profile"},
                "bin_probabilities":r["profile"],
            }
            for r in all_rows
        ],
        "claim_boundary":{
            "new_hypothesis_test":False,
            "new_permutation":False,
            "clustering":False,
            "strategy_classes":False,
            "behavioral_state_inferred":False,
            "nonadditive_device_error_resolved":False,
        },
    }
    OUT_JSON.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")


def plot(all_rows):
    FIG_DIR.mkdir(parents=True,exist_ok=True)
    panel_rows={p:[r for r in all_rows if r["panel"]==p] for p in PANELS}
    vmax=max(max(r["profile"]) for r in all_rows)

    heights=[max(4,len(panel_rows[p])) for p in PANELS]
    fig=plt.figure(figsize=(8.7,11.0))
    gs=fig.add_gridspec(len(PANELS),1,height_ratios=heights,hspace=0.22)
    axes=[]
    image=None
    for i,panel in enumerate(PANELS):
        ax=fig.add_subplot(gs[i,0])
        axes.append(ax)
        mat=np.array([r["profile"] for r in panel_rows[panel]],dtype=float)
        image=ax.imshow(mat,aspect="auto",interpolation="nearest",vmin=0.0,vmax=vmax)
        ax.axvline(4.5,linewidth=0.7)
        ax.set_yticks([])
        ax.set_ylabel(f"{PANEL_LABELS[panel]}\n(n={len(panel_rows[panel])})",rotation=0,ha="right",va="center")
        if i<len(PANELS)-1:
            ax.set_xticks([])
        else:
            ax.set_xticks(range(len(BIN_LABELS)),BIN_LABELS,rotation=35,ha="right")
            ax.set_xlabel("Session-centered residual height bin (m)")
    cbar=fig.colorbar(image,ax=axes,location="right",fraction=0.025,pad=0.02)
    cbar.set_label("Common-cell standardized self-profile probability")
    fig.suptitle(
        "Repeatable individual shapes of vertical space use in the five comparative panels\n"
        "Rows are individuals, ordered within panel by upper-tail mass (>=100 m)",
        y=0.995,
    )
    fig.subplots_adjust(top=0.95,bottom=0.08,left=0.20,right=0.90)
    fig.savefig(FIG_PDF)
    fig.savefig(FIG_PNG,dpi=240)
    plt.close(fig)


def main():
    contract=json.loads(CONTRACT.read_text(encoding="utf-8"))
    if tuple(contract["panels"])!=PANELS:
        raise RuntimeError("panel list differs from frozen descriptive contract")

    all_rows=[]
    panel_meta={}
    for panel in PANELS:
        rows,source,observed=panel_profiles(panel)
        all_rows.extend(rows)
        panel_meta[panel]={
            "label":PANEL_LABELS[panel],
            "n_individuals":len(rows),
            "n_evaluable_target_sessions":sum(r["evaluable_sessions"] for r in rows),
            "source":source,
            "frozen_centered_shape_observed":observed["common_cell_marginal"],
        }
        print(json.dumps({
            "panel":panel,
            "n":len(rows),
            "upper_tail_min":min(r["upper_tail_mass_ge_100m"] for r in rows),
            "upper_tail_max":max(r["upper_tail_mass_ge_100m"] for r in rows),
        },sort_keys=True))

    write_outputs(all_rows,panel_meta)
    plot(all_rows)
    print(OUT_CSV)
    print(OUT_JSON)
    print(FIG_PDF)
    print(FIG_PNG)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
