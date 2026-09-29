#!/usr/bin/env python3
from __future__ import annotations

import json, math, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_tag_altitude_bias_shape as shape
import scripts.run_cross_panel_estimator_calibration as cal
from batter.analysis import z_bin

CONTRACT=ROOT/"post_freeze_extensions/phyllostomus_2023_phase_attribution/contract_v1.json"
OUT=ROOT/"post_freeze_extensions/phyllostomus_2023_phase_attribution/result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/phyllostomus_2023_phase_attribution/RESULT_V1.md"
EDGES=(-math.inf,-400.0,-200.0,-100.0,-50.0,0.0,50.0,100.0,200.0,400.0,math.inf)
K=len(EDGES)-1
ALPHA=0.5


def turn_angle(a,b,c):
    v1x,v1y=b["x"]-a["x"],b["y"]-a["y"]
    v2x,v2y=c["x"]-b["x"],c["y"]-b["y"]
    n1=math.hypot(v1x,v1y); n2=math.hypot(v2x,v2y)
    if n1<=0 or n2<=0:
        return None
    z=max(-1.0,min(1.0,(v1x*v2x+v1y*v2y)/(n1*n2)))
    return math.acos(z)


def prepare():
    records,source=shape.panel_raw("phyllostomus_2023")
    by_session=defaultdict(list)
    for r in records:
        by_session[(r["cohort"],r["session"])].append(r)

    medians={}
    raw=[]
    for key,vals in sorted(by_session.items()):
        vals=sorted(vals,key=lambda x:x["t"])
        medians[key]=float(np.median([r["h"] for r in vals]))
        for i in range(2,len(vals)):
            a,b,c=vals[i-2],vals[i-1],vals[i]
            d1=(b["t"]-a["t"]).total_seconds()
            d2=(c["t"]-b["t"]).total_seconds()
            if not all(math.isfinite(d) and d>0 and d<=1800 for d in (d1,d2)):
                continue
            tr=turn_angle(a,b,c)
            if tr is None:
                continue
            sp=math.hypot(c["x"]-b["x"],c["y"]-b["y"])/d2
            raw.append({
                "cohort":c["cohort"],"session":c["session"],"iid":c["iid"],
                "t":c["t"],"x":c["x"],"y":c["y"],"h":c["h"],
                "speed":float(sp),"turn":float(tr)
            })

    speeds=defaultdict(list);turns=defaultdict(list)
    for r in raw:
        speeds[r["cohort"]].append(r["speed"])
        turns[r["cohort"]].append(r["turn"])
    thresholds={cohort:{
        "speed":float(np.median(np.asarray(speeds[cohort],dtype=float))),
        "turn":float(np.median(np.asarray(turns[cohort],dtype=float)))
    } for cohort in speeds}

    by_valid_session=defaultdict(list)
    for r in raw:
        th=thresholds[r["cohort"]]
        state=int(r["speed"]>th["speed"])*2+int(r["turn"]>th["turn"])
        by_valid_session[(r["cohort"],r["session"])].append({**r,"state":state})

    cohorts=defaultdict(dict)
    for key,vals in sorted(by_valid_session.items()):
        vals=sorted(vals,key=lambda x:x["t"])
        t0=vals[0]["t"]; t1=vals[-1]["t"]
        dur=(t1-t0).total_seconds()
        if dur<=0:
            continue
        base_counts={}
        phase_counts={}
        phase_to_base={}
        med=medians[key]
        iid=vals[0]["iid"]
        for r in vals:
            frac=(r["t"]-t0).total_seconds()/dur
            phase=min(2,max(0,int(frac*3)))
            base=(math.floor(r["x"]/5000.0),math.floor(r["y"]/5000.0),r["state"])
            pcell=base+(phase,)
            zb=z_bin(float(r["h"]-med),edges=EDGES)
            if base not in base_counts:
                base_counts[base]=np.zeros(K,dtype=float)
            if pcell not in phase_counts:
                phase_counts[pcell]=np.zeros(K,dtype=float)
            base_counts[base][zb]+=1
            phase_counts[pcell][zb]+=1
            phase_to_base[pcell]=base
        cohort,session=key
        cohorts[cohort][session]={
            "session":session,"original_label":iid,
            "base_counts":base_counts,"phase_counts":phase_counts,
            "phase_to_base":phase_to_base
        }
    return dict(cohorts),{"source":source,"thresholds":thresholds,"session_count":sum(len(x) for x in cohorts.values()),"valid_endpoint_count":len(raw)}


def smooth(counts):
    x=np.asarray(counts,dtype=float)+ALPHA
    return x/x.sum()


def self_profile(sessions,sids,key):
    per=defaultdict(list)
    for sid in sids:
        for cell,cnt in sessions[sid][key].items():
            per[cell].append(smooth(cnt))
    return {cell:np.mean(np.stack(vals),axis=0) for cell,vals in per.items()}


def other_profile(sessions,sids,labels,key):
    grouped={}
    for sid in sids:
        lab=labels[sid]
        for cell,cnt in sessions[sid][key].items():
            k=(lab,cell)
            if k not in grouped:
                grouped[k]=np.zeros(K,dtype=float)
            grouped[k]+=cnt
    per=defaultdict(list)
    for (lab,cell),cnt in grouped.items():
        per[cell].append(smooth(cnt))
    return {cell:np.mean(np.stack(vals),axis=0) for cell,vals in per.items()}


def score(cohorts,labels_by_cohort,min_scored=50):
    rows=[]
    for cohort,sessions in sorted(cohorts.items()):
        labels=labels_by_cohort[cohort]
        ids=sorted(sessions)
        all_labs=sorted(set(labels.values()))
        for sid in ids:
            lab=labels[sid]
            self_sids=[x for x in ids if x!=sid and labels[x]==lab]
            if not self_sids:
                continue
            other_sids=[x for x in ids if labels[x]!=lab]
            if not other_sids:
                continue

            ps_phase=self_profile(sessions,self_sids,"phase_counts")
            po_phase=other_profile(sessions,other_sids,labels,"phase_counts")
            ps_base=self_profile(sessions,self_sids,"base_counts")
            po_base=other_profile(sessions,other_sids,labels,"base_counts")

            target=sessions[sid]
            supported=[
                pcell for pcell in target["phase_counts"]
                if pcell in ps_phase and pcell in po_phase
                and target["phase_to_base"][pcell] in ps_base
                and target["phase_to_base"][pcell] in po_base
            ]
            scored=int(sum(target["phase_counts"][pcell].sum() for pcell in supported))
            if scored<min_scored:
                continue

            phase_sum=0.0;base_sum=0.0
            for pcell in supported:
                cnt=target["phase_counts"][pcell]
                base=target["phase_to_base"][pcell]
                mask=cnt>0
                if not np.any(mask):
                    continue
                phase_sum+=float(np.dot(cnt[mask],np.log(ps_phase[pcell][mask])-np.log(po_phase[pcell][mask])))
                base_sum+=float(np.dot(cnt[mask],np.log(ps_base[base][mask])-np.log(po_base[base][mask])))
            g_phase=phase_sum/scored
            g_base=base_sum/scored
            rows.append({
                "cohort":cohort,"session":sid,"label":lab,"scored_events":scored,
                "phase_gain":float(g_phase),"collapsed_gain":float(g_base),
                "phase_increment":float(g_phase-g_base)
            })

    per={}
    for lab in sorted({r["label"] for r in rows}):
        rs=[r for r in rows if r["label"]==lab]
        if rs:
            per[lab]={
                "evaluable_sessions":len(rs),
                "phase_gain":float(np.mean([r["phase_gain"] for r in rs])),
                "collapsed_gain":float(np.mean([r["collapsed_gain"] for r in rs])),
                "phase_increment":float(np.mean([r["phase_increment"] for r in rs]))
            }
    vals=list(per.values())
    return {
        "eligible_individuals":len(vals),
        "phase_gain":float(np.mean([v["phase_gain"] for v in vals])) if vals else None,
        "collapsed_gain":float(np.mean([v["collapsed_gain"] for v in vals])) if vals else None,
        "phase_increment":float(np.mean([v["phase_increment"] for v in vals])) if vals else None,
        "individual_results":per,
        "session_results":rows
    }


def observed_labels(cohorts):
    return {cohort:{sid:r["original_label"] for sid,r in sessions.items()} for cohort,sessions in cohorts.items()}


def perm_labels(cohorts,rng):
    out={}
    for cohort,sessions in sorted(cohorts.items()):
        ids=sorted(sessions)
        labs=np.asarray([sessions[sid]["original_label"] for sid in ids],dtype=object)
        pp=rng.permutation(labs)
        out[cohort]={sid:str(pp[i]) for i,sid in enumerate(ids)}
    return out


def main():
    c=json.loads(CONTRACT.read_text())
    cohorts,diag=prepare()
    obs=score(cohorts,observed_labels(cohorts))
    expected=int(c["fixed_context"]["expected_evaluable_individuals"])
    if obs["eligible_individuals"]!=expected:
        raise RuntimeError(f"observed n {obs['eligible_individuals']} != {expected}")

    B=int(c["calibration"]["B"]);seed=int(c["calibration"]["seed"])
    rng=np.random.default_rng(seed)
    null_inc=[];null_phase=[];null_base=[];invalid=0
    for _ in range(B):
        p=score(cohorts,perm_labels(cohorts,rng))
        if p["eligible_individuals"]<1:
            invalid+=1;continue
        null_inc.append(p["phase_increment"])
        null_phase.append(p["phase_gain"])
        null_base.append(p["collapsed_gain"])

    inc=cal.tail_summary(null_inc,obs["phase_increment"])
    phase=cal.tail_summary(null_phase,obs["phase_gain"])
    base=cal.tail_summary(null_base,obs["collapsed_gain"])
    supported=inc["observed_minus_null_mean"]<0 and inc["p_null_le_observed"]<=0.05

    payload={
        "schema_version":1,"study_id":c["study_id"],
        "diagnostics":diag,
        "observed":obs,
        "permutation":{
            "B":B,"seed":seed,"invalid_replicates":invalid,
            "phase_increment":inc,
            "phase_gain":phase,
            "collapsed_gain":base
        },
        "primary_supported":bool(supported),
        "interpretation":(
            "Support-matched phase conditioning removes more same-individual predictive advantage than expected under whole-session label exchangeability."
            if supported else
            "The 2023 phase-conditioned attenuation is not distinguishable from the support-matched permutation expectation; sparsity/finite-sample effects remain a viable explanation."
        ),
        "claim_boundary":c["claim_boundary"],
        "submission_claims_unchanged":True
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    OUT_MD.write_text(
        "# P. hastatus 2023 support-matched phase attribution v1\n\n"
        "**POST-HOC MECHANISTIC LOCALIZATION; NOT INDEPENDENT CONFIRMATION.**\n\n"
        f"- n: **{obs['eligible_individuals']}**\n"
        f"- support-matched collapsed gain: **{obs['collapsed_gain']:+.4f}**\n"
        f"- phase-conditioned gain: **{obs['phase_gain']:+.4f}**\n"
        f"- paired phase increment: **{obs['phase_increment']:+.4f}**\n"
        f"- null-centered phase increment: **{inc['observed_minus_null_mean']:+.4f}**\n"
        f"- one-sided p(null <= observed): **{inc['p_null_le_observed']:.4f}**\n"
        f"- frozen attribution verdict: **{'PASS' if supported else 'FAIL'}**\n\n"
        "Both models are scored on exactly the same phase-supported target endpoints.\n"
    )
    print(json.dumps({
        "n":obs["eligible_individuals"],
        "collapsed_gain":obs["collapsed_gain"],
        "phase_gain":obs["phase_gain"],
        "phase_increment":obs["phase_increment"],
        "calibrated_phase_increment":inc["observed_minus_null_mean"],
        "p_lower":inc["p_null_le_observed"],
        "supported":supported
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
