#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, math, sys
from collections import Counter, defaultdict
from datetime import timedelta
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from batter.analysis import Event, conditional_profile, z_bin
import scripts.run_cross_panel_estimator_calibration as cal
import scripts.run_tag_altitude_bias_shape as shape

CONTRACT=ROOT/"post_freeze_extensions/fine_place_same_night_four_panel/contract_v1.json"
OUT=ROOT/"post_freeze_extensions/fine_place_same_night_four_panel/result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/fine_place_same_night_four_panel/RESULT_V1.md"
EDGES=(-math.inf,-400.0,-200.0,-100.0,-50.0,0.0,50.0,100.0,200.0,400.0,math.inf)
ALPHA=0.5


def shifted_night(t):
    return (t-timedelta(hours=12)).date().isoformat()


def turn_angle(v1x,v1y,v2x,v2y):
    a=math.hypot(v1x,v1y); b=math.hypot(v2x,v2y)
    if a<=0 or b<=0:
        return None
    z=max(-1.0,min(1.0,(v1x*v2x+v1y*v2y)/(a*b)))
    return math.acos(z)


def prepare_panel(panel,c):
    records,source=shape.panel_raw(panel)
    by_session=defaultdict(list)
    for r in records:
        by_session[(r["cohort"],r["session"])].append(r)

    medians={}
    endpoints=[]
    max_dt=int(c["context"]["maximum_step_interval_seconds"])
    for key,vals in sorted(by_session.items()):
        vals=sorted(vals,key=lambda x:x["t"])
        medians[key]=float(np.median([r["h"] for r in vals]))
        for i in range(2,len(vals)):
            a,b,d=vals[i-2],vals[i-1],vals[i]
            dt1=(b["t"]-a["t"]).total_seconds()
            dt2=(d["t"]-b["t"]).total_seconds()
            if not all(math.isfinite(x) and x>0 and x<=max_dt for x in (dt1,dt2)):
                continue
            v1x,v1y=b["x"]-a["x"],b["y"]-a["y"]
            v2x,v2y=d["x"]-b["x"],d["y"]-b["y"]
            tr=turn_angle(v1x,v1y,v2x,v2y)
            if tr is None:
                continue
            sp=math.hypot(v2x,v2y)/dt2
            endpoints.append({
                "cohort":d["cohort"],"session":d["session"],"iid":d["iid"],
                "t":d["t"],"x":d["x"],"y":d["y"],"h":d["h"],
                "speed":float(sp),"turn":float(tr)
            })

    speeds=defaultdict(list); turns=defaultdict(list)
    for r in endpoints:
        speeds[r["cohort"]].append(r["speed"]); turns[r["cohort"]].append(r["turn"])
    thresholds={
        cohort:{
            "speed":float(np.median(np.asarray(speeds[cohort],dtype=float))),
            "turn":float(np.median(np.asarray(turns[cohort],dtype=float)))
        } for cohort in sorted(speeds)
    }

    grid=float(c["context"]["horizontal_cell_m"])
    endpoint_by_session=defaultdict(list)
    for r in endpoints:
        th=thresholds[r["cohort"]]
        state=int(r["speed"]>th["speed"])*2+int(r["turn"]>th["turn"])
        resid=float(r["h"]-medians[(r["cohort"],r["session"])])
        cell=(math.floor(r["x"]/grid),math.floor(r["y"]/grid),state)
        endpoint_by_session[(r["cohort"],r["session"])].append({
            "iid":r["iid"],"t":r["t"],"cell":cell,"zbin":z_bin(resid,edges=EDGES)
        })

    purity=float(c["context"]["minimum_session_night_purity"])
    cohorts=defaultdict(dict)
    for key,vals in sorted(endpoint_by_session.items()):
        cnt=Counter(shifted_night(r["t"]) for r in vals)
        night,n=cnt.most_common(1)[0]
        frac=n/len(vals)
        if frac<purity:
            continue
        kept=[r for r in vals if shifted_night(r["t"])==night]
        cohort,session=key
        iid=kept[0]["iid"]
        cohorts[cohort][session]={
            "session":session,
            "original_label":iid,
            "night":night,
            "night_purity":frac,
            "events":kept,
        }

    return dict(cohorts),{
        "source":source,
        "cohort_thresholds":thresholds,
        "retained_session_count":sum(len(v) for v in cohorts.values()),
        "kinematic_endpoint_count":len(endpoints)
    }


def profile_events(session_records,labels):
    out=[]
    for rec in session_records:
        lab=labels[rec["session"]]
        for e in rec["events"]:
            out.append(Event(
                individual=lab,
                timestamp=e["t"],
                cell=e["cell"],
                zbin=e["zbin"],
                session=rec["session"]
            ))
    return out


def score_panel(cohorts,labels_by_cohort,min_scored):
    session_rows=[]
    for cohort,sessions_dict in sorted(cohorts.items()):
        records=list(sessions_dict.values())
        labels=labels_by_cohort[cohort]
        for target in records:
            sid=target["session"]
            lab=labels[sid]
            self_recs=[r for r in records if r["session"]!=sid and labels[r["session"]]==lab]
            night_other_recs=[
                r for r in records
                if r["night"]==target["night"] and labels[r["session"]]!=lab
            ]
            if not self_recs:
                session_rows.append({"cohort":cohort,"session":sid,"label":lab,"evaluable":False,"reason":"no_self_history"})
                continue
            if not night_other_recs:
                session_rows.append({"cohort":cohort,"session":sid,"label":lab,"evaluable":False,"reason":"no_same_night_other"})
                continue

            self_events=profile_events(self_recs,labels)
            night_events=profile_events(night_other_recs,labels)
            p_self=conditional_profile(self_events,unit="session",alpha=ALPHA,k=len(EDGES)-1)
            p_night=conditional_profile(night_events,unit="individual",alpha=ALPHA,k=len(EDGES)-1)

            target_events=[
                e for e in target["events"]
                if e["cell"] in p_self and e["cell"] in p_night
            ]
            if len(target_events)<min_scored:
                session_rows.append({
                    "cohort":cohort,"session":sid,"label":lab,"evaluable":False,
                    "reason":"insufficient_common_support","scored_events":len(target_events)
                })
                continue
            gains=[
                math.log(float(p_self[e["cell"]][e["zbin"]]))-
                math.log(float(p_night[e["cell"]][e["zbin"]]))
                for e in target_events
            ]
            session_rows.append({
                "cohort":cohort,"session":sid,"label":lab,"night":target["night"],
                "evaluable":True,"scored_events":len(target_events),
                "same_night_other_individual_count":len({labels[r["session"]] for r in night_other_recs}),
                "gain":float(np.mean(gains))
            })

    per_ind={}
    for lab in sorted({r["label"] for r in session_rows if r.get("evaluable")}):
        vals=[r["gain"] for r in session_rows if r.get("evaluable") and r["label"]==lab]
        if vals:
            per_ind[lab]={
                "evaluable_sessions":len(vals),
                "mean_gain":float(np.mean(vals)),
                "positive_session_fraction":float(np.mean(np.asarray(vals)>0))
            }
    vals=[v["mean_gain"] for v in per_ind.values()]
    return {
        "eligible_individuals":len(vals),
        "equal_individual_mean_gain":float(np.mean(vals)) if vals else None,
        "positive_individual_fraction":float(np.mean(np.asarray(vals)>0)) if vals else None,
        "individual_results":per_ind,
        "session_results":session_rows
    }


def observed_labels(cohorts):
    return {
        cohort:{sid:rec["original_label"] for sid,rec in sessions.items()}
        for cohort,sessions in cohorts.items()
    }


def permuted_labels(cohorts,rng):
    out={}
    for cohort,sessions in sorted(cohorts.items()):
        ids=sorted(sessions)
        labs=np.asarray([sessions[sid]["original_label"] for sid in ids],dtype=object)
        perm=rng.permutation(labs)
        out[cohort]={sid:str(perm[i]) for i,sid in enumerate(ids)}
    return out


def run_panel(panel,c):
    cohorts,diag=prepare_panel(panel,c)
    obs_labels=observed_labels(cohorts)
    min_scored=int(c["predictors"]["minimum_supported_target_events"])
    observed=score_panel(cohorts,obs_labels,min_scored)
    expected=int(c["preflight"]["exact_evaluable_individuals"][panel])
    if observed["eligible_individuals"]!=expected:
        raise RuntimeError(f"{panel}: observed n {observed['eligible_individuals']} != frozen preflight n {expected}")

    setting={x["panel"]:x for x in c["calibration"]["settings"]}[panel]
    rng=np.random.default_rng(int(setting["seed"]))
    null=[]; eligible=[]; invalid=0
    for _ in range(int(setting["B"])):
        labels=permuted_labels(cohorts,rng)
        p=score_panel(cohorts,labels,min_scored)
        if p["eligible_individuals"]<1 or p["equal_individual_mean_gain"] is None:
            invalid+=1
            continue
        null.append(float(p["equal_individual_mean_gain"]))
        eligible.append(int(p["eligible_individuals"]))
    if not null:
        raise RuntimeError(f"{panel}: no valid null replicates")

    calibration=cal.tail_summary(null,float(observed["equal_individual_mean_gain"]))
    passed=(
        observed["eligible_individuals"]==expected
        and calibration["observed_minus_null_mean"]>0
        and calibration["p_null_ge_observed"]<=0.05
    )
    return {
        "schema_version":1,"study_id":c["study_id"],"panel":panel,
        "diagnostics":diag,
        "observed":observed,
        "permutation":{
            "B":int(setting["B"]),"seed":int(setting["seed"]),
            "valid_replicates":len(null),"invalid_replicates":invalid,
            "eligible_individual_count_min":int(min(eligible)),
            "eligible_individual_count_max":int(max(eligible)),
            "calibration":calibration
        },
        "primary_verdict":{
            "expected_evaluable_individuals":expected,
            "exact_n_met":True,
            "calibrated_excess_positive":calibration["observed_minus_null_mean"]>0,
            "upper_tail_le_0_05":calibration["p_null_ge_observed"]<=0.05,
            "pass":bool(passed)
        },
        "claim_boundary":c["claim_boundary"]
    }


def aggregate(c,panel_dir):
    panels={}
    for p in c["preflight"]["exact_evaluable_individuals"]:
        path=panel_dir/f"panel_{p}_v1.json"
        if not path.exists(): raise RuntimeError(f"missing panel {path}")
        panels[p]=json.loads(path.read_text())
    n=sum(int(v["primary_verdict"]["pass"]) for v in panels.values())
    category="3_or_4_pass" if n>=3 else ("1_or_2_pass" if n>=1 else "0_pass")
    return {
        "schema_version":1,"study_id":c["study_id"],"submission_claims_unchanged":True,
        "panels":panels,
        "synthesis":{"pass_count":n,"panel_count":len(panels),"category":category,"interpretation":c["synthesis"]["decision_matrix"][category]},
        "claim_boundary":c["claim_boundary"],"stop_rule":c["stop_rule"]
    }


def markdown(payload):
    s=payload["synthesis"]
    lines=[
      "# Four-panel 2-km fine-place × same-night vertical context test v1","",
      "**POST-FREEZE EXPLORATORY MECHANISM TEST. No inference to Eidolon.**","",
      f"- panels passing: **{s['pass_count']}/{s['panel_count']}**",
      f"- synthesis: **{s['category']}**","",
      "| panel | n | observed gain | calibrated excess | p(null >= observed) | pass |",
      "|---|---:|---:|---:|---:|---:|"
    ]
    for p,v in payload["panels"].items():
        x=v["permutation"]["calibration"]
        lines.append(f"| {p} | {v['observed']['eligible_individuals']} | {v['observed']['equal_individual_mean_gain']:+.3f} | {x['observed_minus_null_mean']:+.3f} | {x['p_null_ge_observed']:.4f} | {'PASS' if v['primary_verdict']['pass'] else 'FAIL'} |")
    lines += ["","## Interpretation","",s["interpretation"],"",
              "Same-night is a broad temporal-context proxy; it is not exact local weather matching.",""]
    return "\n".join(lines)


def main():
    ap=argparse.ArgumentParser()
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--panel")
    g.add_argument("--aggregate",action="store_true")
    ap.add_argument("--panel-dir",default="post_freeze_extensions/fine_place_same_night_four_panel/panel_results")
    args=ap.parse_args()
    c=json.loads(CONTRACT.read_text())
    panel_dir=ROOT/args.panel_dir
    if args.panel:
        if args.panel not in c["preflight"]["exact_evaluable_individuals"]:
            raise SystemExit(f"unknown panel {args.panel}")
        payload=run_panel(args.panel,c)
        panel_dir.mkdir(parents=True,exist_ok=True)
        path=panel_dir/f"panel_{args.panel}_v1.json"
        path.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
        x=payload["permutation"]["calibration"]
        print(json.dumps({
          "panel":args.panel,"n":payload["observed"]["eligible_individuals"],
          "observed_gain":payload["observed"]["equal_individual_mean_gain"],
          "calibrated_excess":x["observed_minus_null_mean"],
          "p_upper":x["p_null_ge_observed"],"pass":payload["primary_verdict"]["pass"]
        },sort_keys=True))
        return 0

    payload=aggregate(c,panel_dir)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    OUT_MD.write_text(markdown(payload))
    print(json.dumps({
      "pass_count":payload["synthesis"]["pass_count"],"category":payload["synthesis"]["category"],
      "panels":{p:{
        "observed_gain":v["observed"]["equal_individual_mean_gain"],
        "calibrated_excess":v["permutation"]["calibration"]["observed_minus_null_mean"],
        "p_upper":v["permutation"]["calibration"]["p_null_ge_observed"],
        "pass":v["primary_verdict"]["pass"]
      } for p,v in payload["panels"].items()}
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
