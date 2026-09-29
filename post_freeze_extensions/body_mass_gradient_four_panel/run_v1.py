#!/usr/bin/env python3
from __future__ import annotations

import argparse, csv, io, json, math, sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from batter.analysis import Event, conditional_profile, z_bin
import scripts.run_tag_altitude_bias_shape as shape
from post_freeze_extensions.body_mass_transfer.preflight_v1 import ref_mass, state_endpoints

CONTRACT=ROOT/"post_freeze_extensions/body_mass_gradient_four_panel/contract_v1.json"
PREFLIGHT=ROOT/"post_freeze_extensions/body_mass_gradient_four_panel/input/preflight_result_v1.json"
OUT=ROOT/"post_freeze_extensions/body_mass_gradient_four_panel/result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/body_mass_gradient_four_panel/RESULT_V1.md"
EDGES=(-math.inf,-400.0,-200.0,-100.0,-50.0,0.0,50.0,100.0,200.0,400.0,math.inf)
K=len(EDGES)-1
ALPHA=0.5


def spearman(x,y):
    xr=rankdata(np.asarray(x,dtype=float),method="average")
    yr=rankdata(np.asarray(y,dtype=float),method="average")
    xc=xr-xr.mean(); yc=yr-yr.mean()
    den=math.sqrt(float(np.dot(xc,xc)*np.dot(yc,yc)))
    return float(np.dot(xc,yc)/den) if den>0 else None


def build_events(panel,c):
    records,source=shape.panel_raw(panel)
    medians={}
    by_session=defaultdict(list)
    for r in records:
        by_session[(r["cohort"],r["session"])].append(r)
    for key,vals in by_session.items():
        medians[key]=float(np.median([r["h"] for r in vals]))

    eps=state_endpoints(records,int(c["context_matching"]["maximum_step_interval_seconds"]))
    events=defaultdict(list)
    for r in eps:
        med=medians[(r["cohort"],r["session"])]
        resid=float(r["h"]-med)
        events[r["cohort"]].append(Event(
            individual=r["iid"],
            timestamp=r["t"],
            cell=r["stratum"],
            zbin=z_bin(resid,edges=EDGES),
            session=r["session"]
        ))
    return dict(events),source


def mean_log_gain(target,p_donor,p_base):
    supported=[e for e in target if e.cell in p_donor and e.cell in p_base]
    if len(supported)<50:
        return None,len(supported)
    vals=[
        math.log(float(p_donor[e.cell][e.zbin]))-
        math.log(float(p_base[e.cell][e.zbin]))
        for e in supported
    ]
    return float(np.mean(vals)),len(supported)


def score_panel(panel,c,pre):
    mass=ref_mass(panel)
    events_by_cohort,source=build_events(panel,c)

    pre_targets={
        iid for iid,rec in pre["panel_results"][panel]["targets"].items()
        if rec.get("evaluable")
    }
    expected=int(c["panel_statistic"]["exact_expected_n"][panel])
    if len(pre_targets)!=expected:
        raise RuntimeError(f"{panel}: preflight target n {len(pre_targets)} != expected {expected}")

    target_pairs={}
    cohort_mass_ids={}
    diagnostics={}

    for cohort,events in sorted(events_by_cohort.items()):
        by_session=defaultdict(list)
        by_ind=defaultdict(list)
        for e in events:
            by_session[e.session].append(e)
            by_ind[e.individual].append(e)
        ids=sorted(i for i in by_ind if i in mass)
        cohort_mass_ids[cohort]=ids

        for target in sorted(set(ids)&pre_targets):
            target_sessions=[(sid,vals) for sid,vals in by_session.items() if vals and vals[0].individual==target]
            donors=[d for d in ids if d!=target]
            pair_rows=[]
            for donor in donors:
                donor_events=by_ind[donor]
                p_donor=conditional_profile(donor_events,unit="session",alpha=ALPHA,k=K)

                baseline_donors=[d for d in donors if d!=donor]
                if len(baseline_donors)<2:
                    continue
                baseline_events=[e for d in baseline_donors for e in by_ind[d]]
                p_base=conditional_profile(baseline_events,unit="individual",alpha=ALPHA,k=K)

                sess=[]
                for sid,tvals in target_sessions:
                    gain,n=mean_log_gain(tvals,p_donor,p_base)
                    if gain is not None:
                        sess.append({"session":sid,"gain":gain,"scored_events":n})
                if not sess:
                    continue
                gain=float(np.mean([x["gain"] for x in sess]))
                pair_rows.append({
                    "donor":donor,
                    "mass_difference":abs(float(mass[donor])-float(mass[target])),
                    "gain":gain,
                    "evaluable_sessions":len(sess),
                    "session_results":sess
                })

            distinct=len({r["mass_difference"] for r in pair_rows})
            if len(pair_rows)>=int(c["target_statistic"]["minimum_donors"]) and distinct>=int(c["target_statistic"]["minimum_distinct_mass_distances"]):
                rho=spearman([r["mass_difference"] for r in pair_rows],[r["gain"] for r in pair_rows])
                target_pairs[target]={
                    "cohort":cohort,
                    "target_mass":float(mass[target]),
                    "donor_count":len(pair_rows),
                    "distinct_mass_distance_count":distinct,
                    "observed_rho":rho,
                    "pairs":pair_rows
                }
            diagnostics[target]={"cohort":cohort,"raw_scored_donor_count":len(pair_rows),"distinct_mass_distance_count":distinct}

    if set(target_pairs)!=pre_targets:
        missing=sorted(pre_targets-set(target_pairs))
        extra=sorted(set(target_pairs)-pre_targets)
        raise RuntimeError(f"{panel}: vertical scorer target set mismatch; missing={missing}; extra={extra}")
    if len(target_pairs)!=expected:
        raise RuntimeError(f"{panel}: vertical scorer target n {len(target_pairs)} != expected {expected}")

    obs=float(np.mean([target_pairs[t]["observed_rho"] for t in sorted(target_pairs)]))

    setting_seed=int(c["calibration"]["seeds"][panel])
    B=int(c["calibration"]["B"])
    rng=np.random.default_rng(setting_seed)
    null=np.empty(B,dtype=float)
    invalid=0

    # Precompute fixed donor gain ranks and index maps.
    cohort_ids={coh:sorted(ids) for coh,ids in cohort_mass_ids.items()}
    cohort_masses={coh:np.array([float(mass[i]) for i in ids],dtype=float) for coh,ids in cohort_ids.items()}
    target_specs=[]
    for target,rec in sorted(target_pairs.items()):
        coh=rec["cohort"]; ids=cohort_ids[coh]; idx={x:i for i,x in enumerate(ids)}
        donor_ids=[p["donor"] for p in rec["pairs"]]
        gains=np.array([p["gain"] for p in rec["pairs"]],dtype=float)
        target_specs.append({
            "target":target,"cohort":coh,"target_idx":idx[target],
            "donor_idx":np.array([idx[d] for d in donor_ids],dtype=int),
            "gain_ranks":rankdata(gains,method="average")
        })

    for b in range(B):
        perm_mass={}
        for coh,masses in cohort_masses.items():
            perm_mass[coh]=masses[rng.permutation(len(masses))]
        rhos=[]
        for spec in target_specs:
            pm=perm_mass[spec["cohort"]]
            dist=np.abs(pm[spec["donor_idx"]]-pm[spec["target_idx"]])
            dr=rankdata(dist,method="average")
            gr=spec["gain_ranks"]
            dc=dr-dr.mean(); gc=gr-gr.mean()
            den=math.sqrt(float(np.dot(dc,dc)*np.dot(gc,gc)))
            if den>0:
                rhos.append(float(np.dot(dc,gc)/den))
        if not rhos:
            null[b]=np.nan; invalid+=1
        else:
            null[b]=float(np.mean(rhos))
    valid=null[np.isfinite(null)]
    if len(valid)==0:
        raise RuntimeError(f"{panel}: no valid mass-label permutations")
    p=float((1+np.sum(valid<=obs))/(len(valid)+1))
    passed=bool(obs<0 and p<=0.05)

    return {
        "panel":panel,
        "source":source,
        "preflight_expected_target_n":expected,
        "observed_target_n":len(target_pairs),
        "observed_equal_target_mean_rho":obs,
        "permutation":{
            "B":B,"seed":setting_seed,
            "valid_replicates":int(len(valid)),"invalid_replicates":int(invalid),
            "null_mean":float(valid.mean()),
            "null_q025":float(np.quantile(valid,0.025)),
            "null_q50":float(np.quantile(valid,0.5)),
            "null_q975":float(np.quantile(valid,0.975)),
            "one_sided_p_null_le_observed":p
        },
        "pass":passed,
        "targets":target_pairs,
        "diagnostics":diagnostics
    }


def aggregate(c,panel_dir):
    panels={}
    for p in c["preflight"]["included_panels"]:
        path=panel_dir/f"panel_{p}_v1.json"
        if not path.exists(): raise RuntimeError(f"missing {path}")
        panels[p]=json.loads(path.read_text())
    n=sum(int(x["pass"]) for x in panels.values())
    cat="3_or_4_pass" if n>=3 else ("1_or_2_pass" if n>=1 else "0_pass")
    return {
        "schema_version":1,"study_id":c["study_id"],"submission_claims_unchanged":True,
        "panels":panels,
        "synthesis":{
            "pass_count":n,"panel_count":len(panels),"category":cat,
            "interpretation":c["synthesis"]["decision_matrix"][cat]
        },
        "generalization_limit":c["synthesis"]["generalization_limit"],
        "claim_boundary":c["claim_boundary"]
    }


def markdown(payload):
    s=payload["synthesis"]
    lines=["# Four-panel body-mass donor-gradient transfer v1","",
           "**POST-FREEZE STRUCTURALLY-EVALUABLE SUBSET TEST. No inference to Eidolon.**","",
           f"- passing panels: **{s['pass_count']}/{s['panel_count']}**",
           f"- synthesis: **{s['category']}**","",
           "| panel | target n | mean target rho | p(null <= observed) | pass |",
           "|---|---:|---:|---:|---:|"]
    for p,v in payload["panels"].items():
        lines.append(f"| {p} | {v['observed_target_n']} | {v['observed_equal_target_mean_rho']:+.3f} | {v['permutation']['one_sided_p_null_le_observed']:.4f} | {'PASS' if v['pass'] else 'FAIL'} |")
    lines += ["","## Interpretation","",s["interpretation"],"",
              "Animal mass is a morphology proxy, not wing loading or causal morphology.",""]
    return "\n".join(lines)


def main():
    ap=argparse.ArgumentParser()
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--panel")
    g.add_argument("--aggregate",action="store_true")
    ap.add_argument("--panel-dir",default="post_freeze_extensions/body_mass_gradient_four_panel/panel_results")
    args=ap.parse_args()
    c=json.loads(CONTRACT.read_text())
    pre=json.loads(PREFLIGHT.read_text())
    panel_dir=ROOT/args.panel_dir
    if args.panel:
        if args.panel not in c["preflight"]["included_panels"]: raise SystemExit("unknown panel")
        payload=score_panel(args.panel,c,pre)
        panel_dir.mkdir(parents=True,exist_ok=True)
        (panel_dir/f"panel_{args.panel}_v1.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
        print(json.dumps({"panel":args.panel,"target_n":payload["observed_target_n"],"mean_rho":payload["observed_equal_target_mean_rho"],"p":payload["permutation"]["one_sided_p_null_le_observed"],"pass":payload["pass"]},sort_keys=True))
        return 0
    payload=aggregate(c,panel_dir)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    OUT_MD.write_text(markdown(payload))
    print(json.dumps({"pass_count":payload["synthesis"]["pass_count"],"category":payload["synthesis"]["category"],"panels":{p:{"rho":v["observed_equal_target_mean_rho"],"p":v["permutation"]["one_sided_p_null_le_observed"],"pass":v["pass"]} for p,v in payload["panels"].items()}},sort_keys=True))
    return 0

if __name__=="__main__": raise SystemExit(main())
