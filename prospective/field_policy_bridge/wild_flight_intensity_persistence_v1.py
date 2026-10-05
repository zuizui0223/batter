#!/usr/bin/env python3
"""Prospective wild-field FlightIntensity persistence bridge."""
from __future__ import annotations
import collections, copy, json, math, sys
from pathlib import Path
import numpy as np
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_new_species_replications as core

PANELS={
 "hypsignathus":("contract/hypsignathus_replication_v1.json",202610051301),
 "phyllostomus_2022":("contract/phyllostomus_replication_v1.json",202610051302),
 "phyllostomus_2023":("contract/phyllostomus_2023_replication_v1.json",202610051303),
 "phyllostomus_2016":("contract/phyllostomus_2016_dry_architecture_v1.json",202610051304),
}
MAX_DT=1800.0
MIN_INTERVALS=50
MIN_INDIVIDUALS=5
NPERM=9999

def panel_contract(panel,path):
    c=json.loads((ROOT/path).read_text(encoding="utf-8"))
    if panel=="phyllostomus_2016":
        q=copy.deepcopy(c)
        q["vertical"]={
          "field":c["vertical"]["primary_field"],
          "primary_edges_m":c["vertical"]["edges_m"],
        }
        return q
    return c

def load_session_rows(panel,path):
    c=panel_contract(panel,path)
    gps=core.get(c["source"]["gps"],f"batter-wild-flight-intensity-{panel}/1.0")
    ref=core.get(c["source"]["reference"],f"batter-wild-flight-intensity-{panel}/1.0")
    rows,headers=core.read_csv(gps); refs,_=core.read_csv(ref)
    pre=core.build_pre_numeric(rows,headers,refs,c)
    trans={
      cohort:Transformer.from_crs("EPSG:4326",f"EPSG:{meta['epsg']}",always_xy=True)
      for cohort,meta in pre["projections"].items()
    }
    by=collections.defaultdict(list)
    hf=c["vertical"]["field"]
    numeric_fail=0
    for idx,row in enumerate(rows):
        sid=pre["session_for_row"].get(idx)
        if sid is None:continue
        sm=pre["session_meta"][sid]; cohort=sm["cohort"]
        if cohort not in pre["admitted_cohorts"]:continue
        lon=core.finite_float(row.get("location_long"))
        lat=core.finite_float(row.get("location_lat"))
        z=core.finite_float(row.get(hf))
        if lon is None or lat is None or z is None:
            numeric_fail+=1;continue
        try:t=core.parse_time(row.get("timestamp",""))
        except Exception:
            numeric_fail+=1;continue
        x,y=trans[cohort].transform(lon,lat)
        by[(cohort,sid,sm["individual"])].append((t,float(x),float(y),float(z)))
    return by,pre,numeric_fail,hf

def session_features(vals):
    vals=sorted(vals,key=lambda x:x[0])
    v3=[];vz=[]
    for a,b in zip(vals[:-1],vals[1:]):
        dt=(b[0]-a[0]).total_seconds()
        if not (math.isfinite(dt) and 0<dt<=MAX_DT):continue
        dx=b[1]-a[1];dy=b[2]-a[2];dz=b[3]-a[3]
        s3=math.sqrt(dx*dx+dy*dy+dz*dz)/dt
        sv=abs(dz)/dt
        if math.isfinite(s3) and math.isfinite(sv):
            v3.append(s3);vz.append(sv)
    if len(v3)<MIN_INTERVALS:return None,len(v3)
    a=np.asarray(v3,float);b=np.asarray(vz,float)
    f=np.asarray([np.median(a),np.percentile(a,90),np.median(b),np.percentile(b,90)],float)
    if not np.all(np.isfinite(f)):return None,len(v3)
    return f,len(v3)

def prepare(panel,path):
    by,pre,numeric_fail,hf=load_session_rows(panel,path)
    sessions=[]
    for (cohort,sid,iid),vals in sorted(by.items()):
        f,n=session_features(vals)
        sessions.append({
          "cohort":cohort,"session":sid,"iid":iid,
          "n_source_rows":len(vals),"n_valid_intervals":n,
          "valid":f is not None,"features":f
        })

    # Standardize only within each frozen cohort, label-free.
    stopped_cohorts={}
    for cohort in sorted({s["cohort"] for s in sessions}):
        rr=[s for s in sessions if s["cohort"]==cohort and s["valid"]]
        if len(rr)<2:
            stopped_cohorts[cohort]="fewer_than_2_valid_sessions";continue
        M=np.vstack([s["features"] for s in rr])
        mu=M.mean(axis=0);sd=M.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):
            stopped_cohorts[cohort]="zero_or_nonfinite_feature_sd";continue
        for s in rr:
            z=(s["features"]-mu)/sd
            s["I"]=float(np.mean(z))
            s["zfeatures"]=z
    sessions=[s for s in sessions if s.get("I") is not None]

    counts=collections.Counter((s["cohort"],s["iid"]) for s in sessions)
    eligible_keys={k for k,n in counts.items() if n>=2}
    sessions=[s for s in sessions if (s["cohort"],s["iid"]) in eligible_keys]

    # Fail closed if one source individual occurs in >1 cohort in this test.
    cohorts_by_i=collections.defaultdict(set)
    for s in sessions:cohorts_by_i[s["iid"]].add(s["cohort"])
    multi={i:sorted(v) for i,v in cohorts_by_i.items() if len(v)>1}
    if multi:
        raise RuntimeError(f"{panel}: individual spans multiple policy cohorts: {multi}")

    return sessions,{
      "height_field":hf,
      "numeric_parse_failures":numeric_fail,
      "source_admitted_cohorts":pre["admitted_cohorts"],
      "stopped_policy_cohorts":stopped_cohorts,
      "valid_policy_sessions_before_repeat_filter":sum(s["valid"] for s in prepare_raw_sessions_for_count(by)),
    }

def prepare_raw_sessions_for_count(by):
    # compact helper used only for an audit count; no re-parsing of source
    out=[]
    for _,vals in by.items():
        f,n=session_features(vals);out.append({"valid":f is not None})
    return out

def stat_reference(sessions,labels):
    """Original direct implementation retained for equivalence checks."""
    by_label=collections.defaultdict(list)
    for s,lab in zip(sessions,labels):
        by_label[(s["cohort"],lab)].append(float(s["I"]))
    per=collections.defaultdict(list)
    for idx,(s,lab) in enumerate(zip(sessions,labels)):
        self_vals=[float(ss["I"]) for j,(ss,ll) in enumerate(zip(sessions,labels))
                   if j!=idx and ss["cohort"]==s["cohort"] and ll==lab]
        if not self_vals:continue
        selfc=float(np.mean(self_vals))
        donors=[]
        donor_labels=sorted({ll for ss,ll in zip(sessions,labels)
                             if ss["cohort"]==s["cohort"] and ll!=lab})
        for d in donor_labels:
            vals=[float(ss["I"]) for ss,ll in zip(sessions,labels)
                  if ss["cohort"]==s["cohort"] and ll==d]
            if vals:donors.append(float(np.mean(vals)))
        if len(donors)<2:continue
        q=float(s["I"])
        H=float(np.mean([abs(q-d) for d in donors])-abs(q-selfc))
        per[(s["cohort"],lab)].append(H)
    indiv={f"{co}:{i}":float(np.mean(v)) for (co,i),v in per.items() if v}
    if len(indiv)<MIN_INDIVIDUALS:return None,indiv
    return float(np.mean(list(indiv.values()))),indiv


def stat(sessions,labels):
    """Algebraically equivalent fast implementation of stat_reference()."""
    per=collections.defaultdict(list)
    byco=collections.defaultdict(list)
    for idx,s in enumerate(sessions):
        byco[s["cohort"]].append(idx)
    for cohort,idxs in byco.items():
        labs=[labels[i] for i in idxs]
        vals=np.asarray([float(sessions[i]["I"]) for i in idxs],dtype=float)
        sums=collections.defaultdict(float)
        counts=collections.Counter()
        for lab,v in zip(labs,vals):
            sums[lab]+=float(v); counts[lab]+=1
        cents={lab:sums[lab]/counts[lab] for lab in counts if counts[lab]>0}
        for idx,lab,q in zip(idxs,labs,vals):
            n=counts[lab]
            if n<2:continue
            selfc=(sums[lab]-float(q))/(n-1)
            donors=[cent for dl,cent in cents.items() if dl!=lab]
            if len(donors)<2:continue
            H=float(np.mean(np.abs(float(q)-np.asarray(donors,dtype=float)))-abs(float(q)-selfc))
            per[(cohort,lab)].append(H)
    indiv={f"{co}:{i}":float(np.mean(v)) for (co,i),v in per.items() if v}
    if len(indiv)<MIN_INDIVIDUALS:return None,indiv
    return float(np.mean(list(indiv.values()))),indiv


def assert_stat_equivalence(sessions):
    labs=[s["iid"] for s in sessions]
    a,ai=stat_reference(sessions,labs)
    b,bi=stat(sessions,labs)
    if (a is None)!=(b is None) or (a is not None and abs(a-b)>1e-12) or ai.keys()!=bi.keys():
        raise RuntimeError("fast-stat observed equivalence check failed")
    for k in ai:
        if abs(ai[k]-bi[k])>1e-12:
            raise RuntimeError(f"fast-stat individual equivalence failed {k}")
    rng=np.random.default_rng(202610051399)
    for _ in range(3):
        pl=perm_labels(sessions,rng)
        a,ai=stat_reference(sessions,pl)
        b,bi=stat(sessions,pl)
        if (a is None)!=(b is None) or (a is not None and abs(a-b)>1e-12) or ai.keys()!=bi.keys():
            raise RuntimeError("fast-stat permutation equivalence check failed")
        for k in ai:
            if abs(ai[k]-bi[k])>1e-12:
                raise RuntimeError(f"fast-stat permutation individual equivalence failed {k}")


def perm_labels(sessions,rng):
    labels=[s["iid"] for s in sessions]
    out=list(labels)
    byco=collections.defaultdict(list)
    for i,s in enumerate(sessions):byco[s["cohort"]].append(i)
    for _,idx in byco.items():
        vals=np.asarray([labels[i] for i in idx],dtype=object)
        rng.shuffle(vals)
        for k,i in enumerate(idx):out[i]=str(vals[k])
    return out

def run_panel(panel,path,seed):
    sessions,audit=prepare(panel,path)
    keys=sorted({(s["cohort"],s["iid"]) for s in sessions})
    support={
      "eligible_individuals":len(keys),
      "eligible_individual_keys":[f"{c}:{i}" for c,i in keys],
      "eligible_sessions":len(sessions),
      "sessions_per_individual":dict(collections.Counter(f"{s['cohort']}:{s['iid']}" for s in sessions)),
      "session_audit":[{
        "cohort":s["cohort"],"session":s["session"],"individual":s["iid"],
        "n_source_rows":s["n_source_rows"],"n_valid_intervals":s["n_valid_intervals"],
        "I":s["I"]
      } for s in sessions],
      **audit
    }
    if len(keys)<MIN_INDIVIDUALS:
        return {"status":"STOP_STRUCTURAL_SUPPORT",**support}
    labs=[s["iid"] for s in sessions]
    obs,ind=stat(sessions,labs)
    if obs is None:return {"status":"STOP_OBSERVED_SUPPORT",**support}
    rng=np.random.default_rng(seed);null=[]
    for _ in range(NPERM):
        pl=perm_labels(sessions,rng)
        q,_=stat(sessions,pl)
        if q is not None:null.append(q)
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs))/(1+len(a)))
    pos=sum(v>0 for v in ind.values());n=len(ind);need=math.ceil(.70*n)
    passed=bool(obs>0 and p<=.05 and pos>=need and len(a)>=9500)
    return {
      "status":"PASS_PANEL" if passed else "FAIL_PANEL",
      **support,
      "H_panel":float(obs),"individual_H":ind,
      "positive_individuals":pos,"required_positive_individuals":need,
      "positive_fraction":pos/n,
      "requested_permutations":NPERM,"valid_permutations":int(len(a)),
      "seed":seed,"null_mean":float(a.mean()),
      "null_q025":float(np.quantile(a,.025)),"null_q975":float(np.quantile(a,.975)),
      "p_one_sided":p
    }

def main():
    results={}
    for panel,(path,seed) in PANELS.items():
        results[panel]=run_panel(panel,path,seed)
    passed=sum(r["status"]=="PASS_PANEL" for r in results.values())
    out={
      "contract":"WILD_FLIGHT_INTENSITY_PERSISTENCE_CONTRACT_V1.md",
      "status":"POST_JAE_PROSPECTIVE_MECHANISM_BRIDGE",
      "panels":results,
      "n_panels_passed":passed,
      "cross_panel_bridge_rule":">=3 of 4 panels pass",
      "field_FlightIntensity_carrier_supported":passed>=3,
      "vertical_shape_bridge_may_open":passed>=3
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
