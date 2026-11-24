"""V23 measurement-lineage audit. No raw identifiers, coordinates, or individual-level rows emitted."""
import csv,io,json,re
from pathlib import Path
from collections import Counter
import numpy as np
import pandas as pd
from roost_fd_source_audit_v2 import OUT
from roost_slope_matched_panels_v21 import PANELS,summary,steps,core
from roost_slope_pinned_srtm_v21 import load_tiles,bilinear_hgt
from roost_slope_cadence_datum_v22 import README,anchors,gate,roster

BINS=[("1_2",1,2),("55_65",55,65),("110_130",110,130),("150_200",150,200),("250_300",250,300)]
SEMANTICS={"height_above_msl","height_above_mean_sea_level"}
META_RE=r"height|altitude|elevation|geoid|vertical|gps|sampling|interpolat|smooth|filter|tag|device|logger|sensor|fix|deployment|time"
SENSITIVE_RE=r"latitude|longitude|location[-_ ]lat|location[-_ ]long|roost|cave|@|\b-?\d{1,3}\.\d{3,}\b"

def docs(panel):
    uid,n,md5=README[panel]
    b=core.get({"url":"https://datarepository.movebank.org/server/api/core/bitstreams/"+uid+"/content","size_bytes":n,"md5":md5},"batter-slope-v23/1.0")
    lines=b.decode("utf-8-sig",errors="replace").splitlines()
    hits=[]
    for i,l in enumerate(lines):
        if re.search(META_RE,l,re.I) and not re.search(SENSITIVE_RE,l,re.I):
            # Keep only relevant metadata lines, never literal track values or identifiers.
            if re.search(r"height|altitude|geoid|vertical|sampl|interpolat|smooth|filter|tag model|device model|logger|gps fix|same as",l,re.I):
                hits.append({"line":i+1,"text":l.strip()[:400]})
    return {"md5":md5,"metadata_lines":hits[:55]}

def load(panel):
    c=json.loads((Path("contract")/PANELS[panel]).read_text())
    if "field" not in c["vertical"]:c["vertical"]["field"]=c["vertical"]["primary_field"]
    h=c["vertical"]["field"];ua="batter-slope-v23/1.0"
    b=core.get(c["source"]["gps"],ua);raw_header=next(csv.reader(io.StringIO(b.decode("utf-8-sig",errors="replace"))))
    gps,headers=core.read_csv(b)
    refs,rh=core.read_csv(core.get(c["source"]["reference"],ua))
    pre=core.build_pre_numeric(gps,headers,refs,c)
    rec=json.loads(Path("contract/roost_slope_existing_srtm_receipt_v21.json").read_text())["panels"][panel]
    assert rec["source_gps_md5"]==c["source"]["gps"]["md5"]
    grids=load_tiles(rec,-32768)
    # Source identifier(s) are internal; only aggregate number and distribution are returned.
    tagcols=[k for k in ("tag_local_identifier","tag_id","deployment_id","deployment_local_identifier","tag_identifier") if k in headers]
    categorycols=[k for k in headers if re.fullmatch(r"(tag|device|logger|sensor|gps)_(model|type|mode|fix_type|sampling_mode|manufacturer)",k)]
    altcols=[k for k in headers if k in SEMANTICS and k!=h]
    cohort_ids={k:str(i) for i,k in enumerate(sorted(pre["admitted_cohorts"]))}
    rows=[];failure=0
    for i,r in enumerate(gps):
        animal=core.iid(r)
        if not animal:continue
        try:t=pd.to_datetime(core.parse_time(r.get("timestamp","")),utc=True)
        except Exception:continue
        sid=pre["session_for_row"].get(i)
        co=pre["session_meta"][sid]["cohort"] if sid else None
        eligible=bool(sid and co in pre["admitted_cohorts"])
        lat=core.finite_float(r.get("location_lat"));lon=core.finite_float(r.get("location_long"))
        height=core.finite_float(r.get(h));ground=np.nan
        if eligible:
            try:ground=bilinear_hgt(grids,lat,lon,-32768)
            except Exception:failure+=1
        tag=next((str(r.get(k,"")).strip() for k in tagcols if str(r.get(k,"")).strip()),"")
        rows.append([str(animal),sid if eligible else None,t,lat,lon,height,ground,
          tag,cohort_ids.get(co) if eligible else None]+[core.finite_float(r.get(k)) for k in altcols]+[str(r.get(k,"")).strip() for k in categorycols])
    d=pd.DataFrame(rows,columns=["animal","session","time","lat","lon","height","ground","tag","cohort"]+altcols+categorycols)
    d=d.sort_values(["animal","time"],kind="stable").reset_index(drop=True)
    d["duplicate"]=d.duplicated(["animal","time"],keep=False)
    x=d.loc[d.session.notna()]
    r={
      "raw_rows":len(gps),"admitted_rows":len(x),"DEM_missing_rows":failure,
      "native_height_field":h,"raw_columns":raw_header,"reference_columns":rh,
      "canonical_header_collisions":{k:v for k,v in Counter(core.canon(k) for k in raw_header).items() if v>1},
      "gps_tag_id_fields":tagcols,"category_fields":categorycols,
      "n_nonempty_tag_ids":int(x.loc[x.tag!="","tag"].nunique()),
      "n_admitted_cohorts":len(cohort_ids),"same_semantic_alt_columns":{},"category_counts":{}
    }
    for k in altcols:
        p=x[["height",k]].dropna()
        r["same_semantic_alt_columns"][k]={"n":len(p),"native_minus_alt_m":summary(p.height-p[k]),"equal_fraction":float(np.mean(p.height==p[k])) if len(p) else None}
    for k in categorycols:
        cts=x[k].value_counts()
        # Restrict output to bounded category counts; no strings resembling tag IDs.
        r["category_counts"][k]={"distinct":len(cts),"nonempty":int((x[k]!="").sum()),
           "category_size_quantiles":summary(cts.to_numpy())}
    r["readme"]=docs(panel)
    return d,r

def pairs(d):
    chunks=[]
    for aid,g in d.groupby("animal",sort=True):
        a=g.iloc[:-1].reset_index(drop=True);b=g.iloc[1:].reset_index(drop=True)
        if not len(a):continue
        dt=(b.time-a.time).dt.total_seconds().to_numpy()
        la=np.deg2rad(a.lat.to_numpy(float));lb=np.deg2rad(b.lat.to_numpy(float))
        dl=np.deg2rad(b.lon.to_numpy(float)-a.lon.to_numpy(float))
        hav=np.sin((lb-la)/2)**2+np.cos(la)*np.cos(lb)*np.sin(dl/2)**2
        dist=2*6371008.8*np.arcsin(np.sqrt(np.clip(hav,0,1)))
        dh=b.height-a.height;dg=b.ground-a.ground
        valid=(a.session.notna()&b.session.notna()&(a.session==b.session)&~a.duplicate&~b.duplicate).to_numpy()
        valid&=(dt>0)&np.isfinite(dist)&np.isfinite(dh)&np.isfinite(dg)
        with np.errstate(divide="ignore",invalid="ignore"):
            z=pd.DataFrame({"animal":str(aid),"session":a.session,"cohort":a.cohort,"tag":a.tag,
                 "dt":dt,"dh":dh,"dg":dg,"speed":dist/dt,"rate":dh/dt,"valid":valid})
        z["prev_dh"]=z.dh.shift();z["prev_dt"]=z.dt.shift();z["prev_speed"]=z.speed.shift()
        z["prev_valid"]=z.valid.shift(fill_value=False)&(z.session==z.session.shift())
        chunks.append(z[z.valid])
    return pd.concat(chunks,ignore_index=True)

def stats(x):
    out={"n":len(x),"animals":int(x.animal.nunique())}
    if x.empty:return out
    out.update(dt=summary(x.dt),abs_dh=summary(abs(x.dh)),abs_dg=summary(abs(x.dg)),speed=summary(x.speed),
        rate=summary(x.rate),zero_dh=float(np.mean(x.dh==0)),
        fraction_abs_rate_gt15=float(np.mean(abs(x.rate)>15)),
        integer_increment_fraction=float(np.mean(np.isclose(x.dh,np.round(x.dh),rtol=0,atol=1e-8))))
    triple=x.prev_valid&(x.dt==x.prev_dt)&x.prev_speed.between(2,50)&x.speed.between(2,50)
    t=x.loc[triple];delta=abs(t.dh-t.prev_dh)
    out["moving_equal_dt_triples"]={"n":len(t),"fraction_dh_diff_le_point1":float(np.mean(delta<=.1+1e-10)) if len(t) else None,
      "fraction_dh_diff_le_point001":float(np.mean(delta<=.001+1e-10)) if len(t) else None}
    return out

def assoc(x):
    if x.empty:return {"n":0}
    a=x.y*x.dt;b=x.q*x.dt
    def corr(a,b,rank=False):
        if rank:a=a.rank();b=b.rank()
        if len(a)<3 or a.std()==0 or b.std()==0:return None
        z=float(a.corr(b));return z if np.isfinite(z) else None
    same=(np.sign(a)==np.sign(b))
    nz=(a!=0)&(b!=0)
    per=[]
    for _,g in x.groupby("animal"):
        aa=g.y*g.dt;bb=g.q*g.dt
        per.append(corr(aa,bb,True))
    return {"n":len(x),"animals":int(x.animal.nunique()),
       "pearson_displacement":corr(a,b),"spearman_displacement":corr(a,b,True),
       "median_animal_spearman":summary([z for z in per if z is not None]),
       "nonzero_both":int(nz.sum()),"same_sign_fraction_nonzero":float(same[nz].mean()) if nz.any() else None,
       "abs_height_displacement":summary(abs(a)),"abs_ground_displacement":summary(abs(b))}

def main():
    r={"status":"measurement_diagnostic","claim_boundary":"Scale/lineage audit; no inferred sensor correction or behavioral year claim.","panels":{}}
    dest=OUT/"audit_v23_slope.json"
    def save():dest.write_text(json.dumps(r,indent=2,allow_nan=False))
    for panel in PANELS:
        try:
            d,a=load(panel)
            p=pairs(d);x=p[p.speed.between(2,50)].copy()
            q={"source":a,"all_pairs":stats(p),"moving_pairs":stats(x),"cadence":{}}
            for k,lo,hi in BINS:
                q["cadence"][k]={"all":stats(p[p.dt.between(lo,hi)]),"moving":stats(x[x.dt.between(lo,hi)])}
            if panel=="phyllostomus_2022":
                for k,z in [("exact120",x[x.dt==120]),("other",x[x.dt!=120])]:
                    groups=[g for _,g in z[z.tag!=""].groupby("tag") if len(g)>=50]
                    q.setdefault("2022_tag_strata",{})[k]={"n_groups_ge50":len(groups),
                     "tag_median_abs_dh":summary([float(abs(g.dh).median()) for g in groups]),
                     "tag_median_abs_dg":summary([float(abs(g.dg).median()) for g in groups]),
                     "tag_median_speed":summary([float(g.speed.median()) for g in groups])}
                q["cohort_cadence"]=[{"cohort_index":i,"exact120":stats(g[g.dt==120]),"other":stats(g[g.dt!=120])}
                  for i,(_,g) in enumerate(x.groupby("cohort",sort=True))]
            d["alternate"]=np.nan
            a120,anc=anchors(d,120,10)
            if len(a120):
                s=steps(a120);y=roster(s,gate(s,110,130));q["matched120"]=assoc(y)
            else:q["matched120"]={"n":0}
            r["panels"][panel]={"status":"computed",**q}
        except Exception as e:r["panels"][panel]={"status":"blocked","error_type":type(e).__name__}
        save()
    print(dest.read_text())
    return 0 if any(x["status"]=="computed" for x in r["panels"].values()) else 2
if __name__=="__main__":raise SystemExit(main())
