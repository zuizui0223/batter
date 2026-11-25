"""V50 coarse-time external corroboration; no fabricated second-level timestamps."""
import json,pathlib
from collections import defaultdict,Counter
import numpy as np
import pandas as pd
from pyproj import Transformer
import roeleke_functional_space_v46 as v46
import roeleke_json_export_v48 as v48
from hurme_functional_space_v42 import B,SEED,GRIDS,OFFSETS,metric,summarize
from hurme_detected_functional_space_v41 import distribution,quant
OUT=pathlib.Path("results/roeleke_minute_bundle_v50.json")
def prepare(d):
    x=d.copy();o={"raw_rows":len(x),"clock":"recorded minute; timezone not inferred"}
    assert len(x)==5627
    t=pd.to_datetime(x.timestamp.str.strip(),format="%d.%m.%Y %H:%M",errors="coerce")
    alt=pd.to_datetime(x.timestamp.str.strip(),format="%m.%d.%Y %H:%M",errors="coerce")
    valid_t=t.notna()
    july=float(t[valid_t].dt.month.eq(7).mean()) if valid_t.any() else 0.
    years=bool(t[valid_t].dt.year.between(2016,2018).all())
    o.update(parsed_times=int(valid_t.sum()),alternate_parsed_times=int(alt.notna().sum()),year_counts={str(int(k)):int(v) for k,v in t.dt.year.value_counts().items()},month_counts={str(int(k)):int(v) for k,v in t.dt.month.value_counts().items()},july_fraction=july)
    if valid_t.mean()<.95 or not years or july<.95 or (alt.notna().mean()>=.95 and not alt.equals(t)):
        return None,o,"STOP_TIME_PROVENANCE"
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
    if valid.mean()<.95:return None,o,"STOP_COMPLETENESS"
    x=x[valid].copy();x["marks"]=x.marks.astype(np.int64)
    x=x.sort_values(["animal","t"],kind="stable")
    m=x.groupby(["animal","t"]).size()
    mins=x[["animal","t"]].drop_duplicates()
    gaps=mins.groupby("animal").t.diff().dt.total_seconds()/60
    gaps=gaps[gaps>0]
    o.update(animals=int(x.animal.nunique()),tags=int(x.tag.nunique()),sites=int(x.site.nunique()),occupied_animal_minutes=len(m),rows_in_tied_minutes=int(m[m>1].sum()),minute_bundle_size_counts={str(int(k)):int(v) for k,v in m.value_counts().items()},distinct_minute_gap_quantiles=quant(gaps),fraction_adjacent_occupied_minute_gaps_le2=float(gaps.le(2).mean()) if len(gaps) else None)
    if not len(gaps) or gaps.le(2).mean()<.5:return None,o,"STOP_COARSE_CONTINUITY"
    return x,o,"COMPLETE"
def collect(x):
    tr=Transformer.from_crs("EPSG:4326","EPSG:6933",always_xy=True)
    rows=[];ex={"inconsistent_tag_or_site":0,"below100_fixes":0,"below10_positive_fixes":0}
    totals=Counter()
    for aid,g in x.groupby("animal",sort=True):
        if g.tag.nunique()!=1 or g.site.nunique()!=1:ex["inconsistent_tag_or_site"]+=1;continue
        g=g.sort_values("t",kind="stable").reset_index(drop=True);w=g.marks.to_numpy(np.int64);n=len(g)
        if n<100:ex["below100_fixes"]+=1;continue
        if (w>0).sum()<10:ex["below10_positive_fixes"]+=1;continue
        xx,yy=tr.transform(g.lon.to_numpy(),g.lat.to_numpy());xy=np.column_stack([xx,yy]);assert np.isfinite(xy).all()
        buckets=defaultdict(list);prev=None;segment=0
        for t,p in g.groupby("t",sort=True):
            if prev is not None and (t-prev).total_seconds()>180:segment+=1
            prev=t
            ix=p.index.to_numpy(np.int64)
            buckets[(segment,t.floor("h"),len(ix))].append(ix)
        bundles=list(buckets.values());groups=[np.concatenate(z) for z in bundles]
        assert np.array_equal(np.sort(np.concatenate(groups)),np.arange(n))
        cells={}
        for size in GRIDS:
            _,c=np.unique(np.floor(xy/size).astype(np.int64),axis=0,return_inverse=True);cells[size]=c
        movable=[np.concatenate(z) for z in bundles if len(z)>=2]
        move=np.concatenate(movable) if movable else np.array([],dtype=np.int64)
        totals.update(fixes=n,positive_fixes=int((w>0).sum()),marks=int(w.sum()),movable_fixes=len(move),movable_marks=int(w[move].sum()),strata=len(bundles),rotatable_strata=sum(len(z)>=2 for z in bundles),minute_bundles=sum(len(z) for z in bundles))
        rows.append({"animal":aid,"site":g.site.iloc[0],"xy":xy,"cells":cells,"marks":w,"groups":groups,"bundles":bundles})
    support={"eligible_animals":len(rows),"excluded_tracks":ex,**dict(totals),"track_fix_quantiles":quant([len(r["marks"]) for r in rows]),"track_mark_quantiles":quant([int(r["marks"].sum()) for r in rows]),"movable_mark_fraction":float(totals["movable_marks"]/totals["marks"]) if totals["marks"] else 0.,"movable_fix_fraction":float(totals["movable_fixes"]/totals["fixes"]) if totals["fixes"] else 0.}
    return rows,support
def bundle_rotations(bundles,n,B,rng):
    rot=np.tile(np.arange(n),(B,1))
    for group in bundles:
        ix=np.stack(group) # k ordered occupied minutes, each with identical fix count m
        k,m=ix.shape
        shifts=rng.integers(0,k,size=B)
        src=ix[(np.arange(k)[None,:]+shifts[:,None])%k]
        perm=np.argsort(rng.random((B,k,m)),axis=2)
        mapped=np.take_along_axis(src,perm,axis=2)
        rot[:,ix.ravel()]=mapped.reshape(B,k*m)
    assert np.all(np.sort(rot,axis=1)==np.arange(n))
    return rot
def test():
    v48.test()
    groups=[[np.array([0,1]),np.array([2,3])],[np.array([4,5])],[np.array([6]),np.array([7])]]
    rot=bundle_rotations(groups,8,20,np.random.default_rng(1))
    assert np.all(np.sort(rot[:,0:2],axis=1)==np.where((rot[:,0:1]<2),np.array([0,1]),np.array([2,3])))
    assert np.all(np.sort(rot[:,4:6],axis=1)==np.array([4,5]))
    assert np.all(np.sort(rot[:,6:8],axis=1)==np.array([6,7]))
def analyze(rows):
    rng=np.random.default_rng(SEED);observed={};simulated={}
    for r in rows:
        rot=bundle_rotations(r["bundles"],len(r["marks"]),B,rng)
        for kind,w in (("count",r["marks"]),("positive_fix",(r["marks"]>0).astype(int))):
            expected=np.zeros(n)
            for ix in r["groups"]:expected[ix]=float(w[ix].sum())/len(ix)
            rw=w[rot];assert np.all(rw.sum(1)==w.sum())
            for size in GRIDS:
                aa=[];ss=[]
                for off in OFFSETS:
                    _,cc=np.unique(np.floor(r["xy"]/size-np.array(off)).astype(np.int64),axis=0,return_inverse=True)
                    if off==(0.,0.):assert np.array_equal(cc,r["cells"][size])
                    k=int(cc.max())+1
                    ref=distribution(cc,expected,k);q=distribution(cc,w,k)
                    aa.append(metric(q,ref))
                    ss.append(np.asarray([metric(distribution(cc,z,k),ref) for z in rw]))
                key=f"{kind}_{size}m";observed.setdefault(key,[]).append(np.stack(aa));simulated.setdefault(key,[]).append(np.stack(ss))
    out={}
    for key,a in observed.items():
        a=np.stack(a);s=np.stack(simulated[key])
        per=[summarize(rows,a[:,i,:],s[:,i,:,:]) for i in range(4)]
        avg=summarize(rows,a.mean(1),s.mean(1))
        for k in avg:
            avg[k]["passing_origins"]=sum(p[k]["gate"] for p in per)
            avg[k]["origin_robust_gate"]=bool(avg[k]["gate"] and avg[k]["passing_origins"]>=3)
        out[key]={"origins":[{"offset":list(o),"metrics":p} for o,p in zip(OFFSETS,per)],"equal_origin":avg}
    return out


def run():
    test();r={"scope":"independent minute-resolution detected-mark concentration; qualitative corroboration only","source_doi":"10.4228/ZALF.DK.112","article_doi":"10.1111/oik.07158","synthetic_tests":"PASS"}
    try:meta,routes=v46.layer_check()
    except Exception as e:r.update(status="STOP_PERMISSION_OR_IDENTITY",error=type(e).__name__);return r
    d,role,receipts=v48.exact_json(routes,meta);r["source_receipts"]=receipts
    if d is None:r["status"]="STOP_SOURCE";return r
    x,o,status=prepare(d);r["structural_audit"]=o;r["status"]=status
    if x is None:return r
    rows,s=collect(x);r["support"]=s
    if len(rows)<6:r["status"]="STOP_LOW_SUPPORT";return r
    if s["movable_mark_fraction"]<.5:r["status"]="STOP_LOW_ROTATABLE_SUPPORT";return r
    r["reference"]={"rotations":B,"seed":SEED,"strata":"recorded hour x segment gap>3min x fixes per minute; rotate bundles, randomize within target minute","boundary":"no verified exact 31s cadence or actual audio effort"}
    r["results"]=analyze(rows)
    def primary(z):return {k:z[k+"_1000m"]["equal_origin"]["concentration_log_effective_cell_ratio"] for k in ("count","positive_fix")}
    r["primary"]=primary(r["results"]);r["corroboration_gate"]=bool(all(v["origin_robust_gate"] for v in r["primary"].values()))
    r["site_summaries"]=[]
    for i,s in enumerate(sorted(set(z["site"] for z in rows))):
        rr=[z for z in rows if z["site"]==s]
        o={"anonymous_site":i+1,"animals":len(rr),"fixes":sum(len(z["marks"]) for z in rr),"marks":sum(int(z["marks"].sum()) for z in rr)}
        if len(rr)>=6:o["primary"]=primary(analyze(rr))
        else:o["status"]="STOP_LOW_SUPPORT"
        r["site_summaries"].append(o)
    r["status"]="COMPLETE";return r
if __name__=="__main__":
    try:r=run()
    except Exception as e:r={"status":"STOP","error":type(e).__name__+":"+str(e)[:250]}
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(r,indent=2,allow_nan=False)+"\n");print(OUT.read_text())
