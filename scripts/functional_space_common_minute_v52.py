"""V52 common minute-bundle reference on separate, source-defined archived cohorts."""
import concurrent.futures as cf,hashlib,json,pathlib,time
import numpy as np
import pandas as pd
import roeleke_minute_bundle_v50 as v50
import roeleke_functional_space_v46 as v46
import roeleke_json_export_v48 as v48
import hurme_detected_functional_space_v41 as v41
from hurme_label_semantics_v40 import get,read
OUT=pathlib.Path("results/functional_space_common_minute_v52.json")
def prepare(d):
    x=d.copy();o={"raw_rows":len(x),"clock":"recorded minute; timezone not inferred"}
    assert len(x)==5627
    t=pd.to_datetime(x.timestamp.str.strip(),format="%d.%m.%Y %H:%M",errors="coerce")
    alt=pd.to_datetime(x.timestamp.str.strip(),format="%m.%d.%Y %H:%M",errors="coerce")
    valid_t=t.notna()
    july=float(t[valid_t].dt.month.eq(7).mean()) if valid_t.any() else 0.
    years=bool(t[valid_t].dt.year.between(2016,2018).all())
    o.update(parsed_times=int(valid_t.sum()),alternate_parsed_times=int(alt.notna().sum()),year_counts={str(int(k)):int(v) for k,v in t.dt.year.value_counts().items()},month_counts={str(int(k)):int(v) for k,v in t.dt.month.value_counts().items()},july_fraction=july)
    # V52 new archived-cohort analysis, not reversal of the failed V50 gate.
    # Calendar months identify this exact export; they are not asserted to be correct.
    if not valid_t.all() or not years or alt.notna().mean()>=.95:
        return None,o,"STOP_CLOCK_FORMAT"
    if o["year_counts"]!={"2016":764,"2017":1874,"2018":2989} or o["month_counts"]!={"7":3753,"8":1874}:
        return None,o,"STOP_V51_COHORT_DRIFT"
    if d.individual_local_identifier.nunique()!=27 or d.tag_local_identifier.nunique()!=27 or sorted(d.groupby("site").individual_local_identifier.nunique().tolist())!=[12,15]:
        return None,o,"STOP_V51_COHORT_DRIFT"
    fid=x.ogc_fid.str.strip()
    o["unique_feature_ids"]=int(fid.nunique());o["blank_feature_ids"]=int(fid.eq("").sum())
    if fid.eq("").any() or not fid.is_unique:return None,o,"STOP_FEATURE_ID"
    # Distinct features in the same recorded minute are retained.
    duplicate=x.duplicated(subset=[c for c in x if c!="ogc_fid"],keep=False)
    x["t"]=t
    x["animal"]=x.individual_local_identifier.str.strip();x["tag"]=x.tag_local_identifier.str.strip();x["site"]=x.site.str.strip()
    for k in ("lon","lat"):x[k]=pd.to_numeric(x[k],errors="coerce")
    x["marks"]=pd.to_numeric(x.buzz.str.strip(),errors="coerce")
    n=x.marks.to_numpy(float)
    good=np.isfinite(n)&(n>=0)&(n==np.floor(n))&(n<2**53)
    valid=valid_t&x.lon.between(-180,180)&x.lat.between(-86,86)&x.animal.ne("")&x.tag.ne("")&x.site.ne("")&good&~duplicate
    o.update(exact_duplicate_rows_excluding_feature_id=int(duplicate.sum()),complete_unique_rows=int(valid.sum()),complete_unique_fraction=float(valid.mean()),valid_mark_rows=int(good.sum()),raw_valid_mark_total=int(n[good].sum()),retained_mark_total=int(x.loc[valid,"marks"].sum()),retained_positive_fixes=int((valid&x.marks.gt(0)).sum()))
    if duplicate.any() or valid.mean()<.95:return None,o,"STOP_COMPLETENESS"
    x=x[valid].copy();x["marks"]=x.marks.astype(np.int64)
    x=x.sort_values(["animal","t"],kind="stable")
    m=x.groupby(["animal","t"]).size()
    mins=x[["animal","t"]].drop_duplicates()
    gaps=mins.groupby("animal").t.diff().dt.total_seconds()/60
    gaps=gaps[gaps>0]
    o.update(animals=int(x.animal.nunique()),tags=int(x.tag.nunique()),sites=int(x.site.nunique()),occupied_animal_minutes=len(m),rows_in_tied_minutes=int(m[m>1].sum()),minute_bundle_size_counts={str(int(k)):int(v) for k,v in m.value_counts().items()},distinct_minute_gap_quantiles=quant(gaps),fraction_adjacent_occupied_minute_gaps_le2=float(gaps.le(2).mean()) if len(gaps) else None)
    if not len(gaps) or gaps.le(2).mean()<.5:return None,o,"STOP_COARSE_CONTINUITY"
    return x,o,"COMPLETE"

def primary(z):
    return {k:z[k+"_1000m"]["equal_origin"]["concentration_log_effective_cell_ratio"] for k in ("count","positive_fix")}
def evaluate(rows,s,o):
    o["support"]=s
    if s["movable_mark_fraction"]<.5:o["status"]="STOP_LOW_ROTATABLE_SUPPORT";return o
    z=v50.analyze(rows)
    o["results"]=z;o["primary"]=primary(z)
    o["gate"]=bool(all(x["origin_robust_gate"] for x in o["primary"].values()))
    o["status"]="COMPLETE"
    return o
def noctule():
    o={"scope":"exact authorized archived noctule sample; date provenance unresolved"}
    meta,routes=v46.layer_check()
    d,role,receipts=v48.exact_json(routes,meta);o["source_receipts"]=receipts
    if d is None:o["status"]="STOP_SOURCE";return o
    x,a,status=prepare(d);o["structural_audit"]=a;o["status"]=status
    if x is None:return o
    rows,s=v50.collect(x)
    if len(rows)!=22:o.update(status="STOP_V51_SUPPORT_DRIFT",support=s);return o
    return evaluate(rows,s,o)
def get_retry(k):
    b,r=get(k);first=dict(r)
    if b is None and "TimeoutError" in r.get("error",""):
        time.sleep(2);b,r=get(k)
        return k,b,{"attempts":[first,dict(r)],**r}
    return k,b,{"attempts":[first],**r}
def vivesi():
    o={"scope":"exact Hurme deployment cohort deliberately coarsened to minutes","sources":{}}
    raw={}
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        for k,b,r in ex.map(get_retry,["gps","reference","readme"]):
            o["sources"][k]=r
            if b is not None:raw[k]=b
    if len(raw)!=3:o["status"]="STOP_SOURCE";return o
    assert hashlib.sha256(raw["reference"]).hexdigest()==v41.REF_SHA
    g,r=read(raw["gps"]),read(raw["reference"])
    assert r["behavior-according-to"].str.strip().str.casefold().eq("values indicate buzz count").all()
    assert r["duty-cycle"].str.strip().nunique()==1
    g,a=v41.attach(g,r);o["deployment_join"]=a
    if g is None:o["status"]="STOP_DEPLOYMENT_JOIN";return o
    native,s=v41.collect(g);o["native_support"]=s
    if (s["eligible_deployments"],s["eligible_animals"],s["eligible_fixes"],s["eligible_positive_fixes"],s["eligible_detected_buzzes"])!=(14,11,13855,602,693):
        o["status"]="STOP_NATIVE_SUPPORT_DRIFT";return o
    rows=[];total={}
    # Keep real deployment boundaries. Aggregate within original individuals via v42 summarize.
    for dep,b in g.groupby("dep",sort=True):
        x=b.copy()
        x["animal"]=x["individual-local-identifier"]
        x["tag"]=x["tag-local-identifier"]
        x["site"]="single_study"
        x["t"]=x.t.dt.floor("min")
        rr,ss=v50.collect(x)
        if not rr:continue
        assert len(rr)==1
        rows+=rr
        for k in ("fixes","positive_fixes","marks","movable_fixes","movable_marks","strata","rotatable_strata","minute_bundles"):
            total[k]=total.get(k,0)+int(ss[k])
    support={"eligible_deployments":len(rows),"eligible_animals":len(set(r["animal"] for r in rows)),**total}
    support["movable_mark_fraction"]=total.get("movable_marks",0)/max(1,total.get("marks",0))
    support["movable_fix_fraction"]=total.get("movable_fixes",0)/max(1,total.get("fixes",0))
    if (len(rows),support["eligible_animals"],total.get("fixes"),total.get("positive_fixes"),total.get("marks"))!=(14,11,13855,602,693):
        o.update(status="STOP_COARSE_SUPPORT_DRIFT",support=support);return o
    return evaluate(rows,support,o)
def safe(fn):
    try:return fn()
    except Exception as e:return {"status":"STOP","error_type":type(e).__name__,"http_status":getattr(e,"code",None)}
def run():
    v50.test();v41.test()
    # Independent seed initialization in each dataset; no pooling or matched individuals across species.
    a=safe(vivesi);b=safe(noctule)
    return {"scope":"new V52 harmonized minute-resolution archived-track comparison; no exact article replication or causal claim","synthetic_tests":"PASS","reference":{"rotations":499,"seed":41025,"strata":"within deployment or animal; recorded hour x occupied-minute segment gap>3min x bundle size","grids_m":[1000,500,2000],"origins":4,"actual_audio_effort":"unknown"},"vivesi":a,"noctule":b,"common_reference_gate":bool(a.get("status")=="COMPLETE" and b.get("status")=="COMPLETE" and a.get("gate") and b.get("gate"))}
if __name__=="__main__":
    try:r=run()
    except Exception as e:r={"status":"STOP","error_type":type(e).__name__}
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(r,indent=2,allow_nan=False)+"\n");print(OUT.read_text())
