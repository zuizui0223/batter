"""V51 provenance diagnostic only; no functional-space statistic."""
import concurrent.futures as cf,io,json,pathlib,hashlib
import numpy as np
import pandas as pd
import roeleke_functional_space_v46 as v46
import roeleke_json_export_v48 as v48
from bayer_field_join_v17 import fetch
from hurme_detected_functional_space_v41 import quant
OUT=pathlib.Path("results/roeleke_provenance_v51.json")
URL="https://www.movebank.org/movebank/service/direct-read?entity_type=study&study_id=622521340"
def summaries(v):
    x=np.asarray(v,dtype=float)
    return {"n":len(x),"mean":float(x.mean()),"median":float(np.median(x)),"MAD_unscaled":float(np.median(np.abs(x-np.median(x)))),"quantiles":quant(x)} if len(x) else {}
def archive():
    meta,routes=v46.layer_check()
    d,role,receipt=v48.exact_json(routes,meta)
    o={"source_receipts":receipt}
    if d is None:o["status"]="STOP_SOURCE";return o
    assert len(d)==5627
    t=pd.to_datetime(d.timestamp.str.strip(),format="%d.%m.%Y %H:%M",errors="coerce")
    assert t.notna().all()
    x=d.copy();x["t"]=t
    for k,c in [("animal","individual_local_identifier"),("tag","tag_local_identifier"),("site_group","site")]:x[k]=x[c].str.strip()
    x["marks"]=pd.to_numeric(x.buzz,errors="coerce")
    x["ym"]=t.dt.strftime("%Y-%m")
    n=x.marks.to_numpy(float);assert np.isfinite(n).all() and (n>=0).all() and (n==np.floor(n)).all()
    fid=d.ogc_fid.str.strip()
    x["duplicate_full"]=d.duplicated(subset=[c for c in d if c!="ogc_fid"],keep=False)
    g=x.groupby("animal")
    a=g.agg(fixes=("marks","size"),marks=("marks","sum"),positive=("marks",lambda s:int((s>0).sum())),tags=("tag","nunique"),sites=("site_group","nunique"),dates=("t",lambda s:s.dt.date.nunique()),months=("ym","nunique"))
    m=x.groupby(["animal","t"]).size()
    o.update(status="COMPLETE_DIAGNOSTIC_ONLY",rows=len(x),unique_feature_ids=int(fid.nunique()),blank_feature_ids=int(fid.eq("").sum()),duplicate_full_rows=int(x.duplicate_full.sum()),animals=int(x.animal.nunique()),tags=int(x.tag.nunique()),sites=int(x.site_group.nunique()),blank_keys={k:int(x[k].eq("").sum()) for k in ("animal","tag","site_group")},animals_with_multiple_tags=int((a.tags>1).sum()),animals_with_multiple_sites=int((a.sites>1).sum()),animals_with_multiple_calendar_dates=int((a.dates>1).sum()),animals_with_multiple_months=int((a.months>1).sum()),occupied_minutes=len(m),rows_in_tied_minutes=int(m[m>1].sum()),minute_bundle_size_counts={str(int(k)):int(v) for k,v in m.value_counts().items()},fixes_per_animal=summaries(a.fixes),marks_per_animal=summaries(a.marks),animals_meeting_count_support=int(((a.fixes>=100)&(a.positive>=10)&(a.tags==1)&(a.sites==1)).sum()),site_groups=[])
    for i,(site,b) in enumerate(x.groupby("site_group",sort=True)):
        v=b.groupby("animal").marks.sum()
        # Anonymized site index and aggregate year/month, not raw identifiers.
        o["site_groups"].append({"anonymous_site":i+1,"animals":len(v),"fixes":len(b),"marks":int(b.marks.sum()),"marks_per_animal":summaries(v),"year_month_counts":[{"year_month":k,"fixes":len(y),"animals":int(y.animal.nunique())} for k,y in b.groupby("ym")]})
    o["published_cohort_count_match"]=bool(sorted(z["animals"] for z in o["site_groups"])==[12,15] and o["animals"]==27)
    return o
def movebank():
    b,_=fetch(URL,1_000_000)
    d=pd.read_csv(io.BytesIO(b),dtype=str,keep_default_na=False)
    assert "id" in d and len(d)==1 and d.id.iloc[0]=="622521340"
    r=d.iloc[0]
    keys=["id","number_of_individuals","number_of_deployments","number_of_tags","number_of_deployed_locations","taxon_ids","sensor_type_ids","license_type","i_can_see_data","i_have_download_access","there_are_data_which_i_cannot_see","study_permission"]
    o={"status":"METADATA_ONLY","sha256":hashlib.sha256(b).hexdigest(),"metadata":{k:str(r[k]) for k in keys if k in r}}
    for k in ["timestamp_first_deployed_location","timestamp_last_deployed_location"]:
        if k in r:
            t=pd.to_datetime(r[k],errors="coerce")
            o[k+"_year_month"]=t.strftime("%Y-%m") if pd.notna(t) else None
    return o
def safe(f):
    try:return f()
    except Exception as e:return {"status":"STOP_DIAGNOSTIC","error_type":type(e).__name__,"http_status":getattr(e,"code",None)}
def run():
    with cf.ThreadPoolExecutor(max_workers=2) as ex:a=list(ex.map(safe,[archive,movebank]))
    return {"scope":"provenance audit only; V50 source gate stays failed; no outcome estimator","archive":a[0],"movebank":a[1]}
if __name__=="__main__":
    r=run();OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(r,indent=2,allow_nan=False)+"\n");print(OUT.read_text())
