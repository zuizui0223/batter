#!/usr/bin/env python3
"""Post-outcome measurement architecture audit for wild FlightIntensity carrier panels."""
from __future__ import annotations
import collections, importlib.util, json, math, statistics
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("W",HERE/"wild_flight_intensity_persistence_v1.py")
W=importlib.util.module_from_spec(spec);spec.loader.exec_module(W)
core=W.core

FEATURE_NAMES=["median_speed3d","p90_speed3d","median_abs_vspeed","p90_abs_vspeed"]
META_KEYS=("sensor","tag","manufacturer","model","sampling","frequency","burst","duty","gps","deployment","study_site")

def q(v,p):
    a=np.asarray([x for x in v if x is not None and math.isfinite(float(x))],float)
    return float(np.quantile(a,p)) if len(a) else None

def med_iqr(v):
    return {"median":q(v,.5),"q25":q(v,.25),"q75":q(v,.75)}

def session_diag(vals):
    vals=sorted(vals,key=lambda x:x[0])
    if len(vals)<2:return None
    dts=[];valid=[];zero_h=[];zero_z=[];abs_dz=[]
    for a,b in zip(vals[:-1],vals[1:]):
        dt=(b[0]-a[0]).total_seconds()
        if math.isfinite(dt) and dt>0:
            dts.append(float(dt))
            dx=b[1]-a[1];dy=b[2]-a[2];dz=b[3]-a[3]
            zero_h.append(1.0 if (dx==0 and dy==0) else 0.0)
            zero_z.append(1.0 if dz==0 else 0.0)
            if dz!=0 and math.isfinite(dz):abs_dz.append(abs(float(dz)))
            if dt<=W.MAX_DT:
                valid.append((dt,dx,dy,dz))
    if not dts:return None
    zvals=[float(x[3]) for x in vals if math.isfinite(float(x[3]))]
    uniq=len(set(zvals))
    duration=(vals[-1][0]-vals[0][0]).total_seconds()
    feat,nvalid=W.session_features(vals)
    return {
      "source_rows":len(vals),
      "positive_dt_count":len(dts),
      "valid_policy_interval_count":len(valid),
      "retained_interval_fraction":len(valid)/len(dts) if dts else None,
      "median_dt":q(dts,.5),"p10_dt":q(dts,.1),"p90_dt":q(dts,.9),
      "max_retained_dt":max([x[0] for x in valid]) if valid else None,
      "session_duration_s":float(duration),
      "zero_horizontal_step_fraction":float(np.mean(zero_h)) if zero_h else None,
      "zero_vertical_step_fraction":float(np.mean(zero_z)) if zero_z else None,
      "unique_height_values":uniq,
      "unique_height_fraction":uniq/len(zvals) if zvals else None,
      "median_abs_nonzero_height_step":q(abs_dz,.5),
      "p90_abs_height_step":q(abs_dz,.9),
      "policy_valid":feat is not None,
      "raw_policy_features":feat.tolist() if feat is not None else None,
    }

def reference_vocab(panel,path):
    c=W.panel_contract(panel,path)
    ref=core.get(c["source"]["reference"],f"batter-field-measurement-audit-{panel}/1.0")
    rows,headers=core.read_csv(ref)
    out={}
    for h in headers:
        canon=h.strip().lower().replace(" ","_")
        if any(k in canon for k in META_KEYS):
            vals=sorted({str(r.get(h,"")).strip() for r in rows if str(r.get(h,"")).strip()})
            out[h]=vals[:200]
    return out

def panel_audit(panel,path):
    by,pre,numeric_fail,hf=W.load_session_rows(panel,path)
    sess=[]
    for (co,sid,iid),vals in sorted(by.items()):
        d=session_diag(vals)
        if d is None:continue
        sess.append({"cohort":co,"session":sid,"individual":iid,**d})

    cohorts={}
    for co in sorted({x["cohort"] for x in sess}):
        rr=[x for x in sess if x["cohort"]==co]
        vr=[x for x in rr if x["policy_valid"]]
        counts=collections.Counter(x["individual"] for x in vr)
        rep=[i for i,n in counts.items() if n>=2]
        features=np.vstack([x["raw_policy_features"] for x in vr]) if vr else np.empty((0,4))
        fsd=[]
        fmin=[];fmax=[];flags=[]
        for k,name in enumerate(FEATURE_NAMES):
            if len(features)>=2:
                sd=float(np.std(features[:,k],ddof=1))
                mn=float(np.min(features[:,k]));mx=float(np.max(features[:,k]))
            else:
                sd=math.nan;mn=math.nan;mx=math.nan
            samefrac=None
            if len(features):
                vals,cnt=np.unique(features[:,k],return_counts=True)
                samefrac=float(np.max(cnt)/len(features))
            flag=(not math.isfinite(sd)) or sd==0 or (samefrac is not None and samefrac>.95)
            fsd.append(sd);fmin.append(mn);fmax.append(mx)
            flags.append({"feature":name,"sd":sd,"min":mn,"max":mx,
                          "max_identical_fraction":samefrac,"degenerate_flag":flag})
        cohorts[co]={
          "source_admitted_sessions":len(rr),
          "policy_valid_sessions":len(vr),
          "individuals_represented":len(set(x["individual"] for x in rr)),
          "individuals_with_ge2_policy_valid_sessions":len(rep),
          "valid_intervals_per_session":med_iqr([x["valid_policy_interval_count"] for x in rr]),
          "median_dt_per_session":med_iqr([x["median_dt"] for x in rr]),
          "duration_s_per_session":med_iqr([x["session_duration_s"] for x in rr]),
          "median_zero_vertical_step_fraction":q([x["zero_vertical_step_fraction"] for x in rr],.5),
          "median_unique_height_fraction":q([x["unique_height_fraction"] for x in rr],.5),
          "raw_feature_audit":flags,
        }
    panel_summary={
      "median_cohort_median_dt":q([v["median_dt_per_session"]["median"] for v in cohorts.values()],.5),
      "median_cohort_valid_intervals":q([v["valid_intervals_per_session"]["median"] for v in cohorts.values()],.5),
      "median_cohort_duration_s":q([v["duration_s_per_session"]["median"] for v in cohorts.values()],.5),
      "median_cohort_zero_vertical_fraction":q([v["median_zero_vertical_step_fraction"] for v in cohorts.values()],.5),
      "median_cohort_unique_height_fraction":q([v["median_unique_height_fraction"] for v in cohorts.values()],.5),
      "median_cohort_raw_feature_sd":{
        FEATURE_NAMES[k]:q([v["raw_feature_audit"][k]["sd"] for v in cohorts.values()],.5)
        for k in range(4)
      }
    }
    return {
      "height_field":hf,
      "numeric_parse_failures":numeric_fail,
      "cohorts":cohorts,
      "panel_summary":panel_summary,
      "reference_metadata_vocabularies":reference_vocab(panel,path),
      "session_count":len(sess),
    }

def safe_ratio(a,b):
    if a is None or b is None or b==0:return None
    return float(a/b)

def main():
    panels={}
    for panel,(path,_) in W.PANELS.items():
        panels[panel]=panel_audit(panel,path)

    a=panels["phyllostomus_2022"]["panel_summary"]
    b=panels["phyllostomus_2023"]["panel_summary"]
    compare={
      "median_dt_ratio_2023_over_2022":safe_ratio(b["median_cohort_median_dt"],a["median_cohort_median_dt"]),
      "valid_intervals_ratio_2023_over_2022":safe_ratio(b["median_cohort_valid_intervals"],a["median_cohort_valid_intervals"]),
      "duration_ratio_2023_over_2022":safe_ratio(b["median_cohort_duration_s"],a["median_cohort_duration_s"]),
      "zero_vertical_fraction_difference_2023_minus_2022":(
        b["median_cohort_zero_vertical_fraction"]-a["median_cohort_zero_vertical_fraction"]
        if b["median_cohort_zero_vertical_fraction"] is not None and a["median_cohort_zero_vertical_fraction"] is not None else None),
      "unique_height_fraction_difference_2023_minus_2022":(
        b["median_cohort_unique_height_fraction"]-a["median_cohort_unique_height_fraction"]
        if b["median_cohort_unique_height_fraction"] is not None and a["median_cohort_unique_height_fraction"] is not None else None),
      "raw_feature_sd_ratio_2023_over_2022":{
        n:safe_ratio(b["median_cohort_raw_feature_sd"][n],a["median_cohort_raw_feature_sd"][n])
        for n in FEATURE_NAMES
      }
    }

    deg2016=[]
    for co,v in panels["phyllostomus_2016"]["cohorts"].items():
        for x in v["raw_feature_audit"]:
            if x["degenerate_flag"]:
                deg2016.append({"cohort":co,**x})

    out={
      "contract":"FIELD_CARRIER_MEASUREMENT_AUDIT_CONTRACT_V1.md",
      "status":"POST_OUTCOME_MEASUREMENT_DIAGNOSTIC",
      "panels":panels,
      "phyllostomus_2022_vs_2023":compare,
      "phyllostomus_2016_degenerate_features":deg2016,
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
