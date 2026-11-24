"""V22: time-matched ground-rate comparison and height measurement audit.
Same pinned sources and admission rules. No location or individual-level output.
"""
import json,sys,re
from pathlib import Path
import numpy as np
import pandas as pd
from roost_fd_source_audit_v2 import OUT
from roost_slope_matched_panels_v21 import (
    BASE,PANELS,compare,steps,summary,tadarida,core
)
from roost_slope_pinned_srtm_v21 import load_tiles,bilinear_hgt

FIELDS=("height_above_msl","height_above_ellipsoid")
README={
"phyllostomus_2016":("e7926fab-d856-47a4-b3b2-436bd29ea798",18149,"2a4e03fb9ce09108e91a91e3e6006571"),
"phyllostomus_2022":("e11034b2-42ee-4387-b87b-bce15a93db1f",22854,"d4cdca285845567f9894195818fe0313"),
"phyllostomus_2023":("749a612c-dc72-4867-9194-2fbac6cd0f75",18952,"7f6999d25186d45243cdb2096d060876")}
def readme(panel):
    try:
        uid,n,md5=README[panel]
        b=core.get({"url":"https://datarepository.movebank.org/server/api/core/bitstreams/"+uid+"/content","size_bytes":n,"md5":md5},"batter-slope-v22/1.0")
        s=b.decode("utf-8-sig",errors="replace")
        hits=[]
        for l in s.splitlines():
            if re.search(r"height[-_ ]above[-_ ](?:msl|ellipsoid)|geoid|vertical (?:accuracy|error)|altitude|sampling (?:rate|interval)",l,re.I):
                # Return only field descriptions with no coordinates or location values.
                if not re.search(r"\b-?\d{1,3}\.\d{3,}\b|latitude|longitude|location[-_]lat|location[-_]long|roost|cave",l,re.I):
                    hits.append(l.strip()[:300])
        return {"status":"verified","md5":md5,"vertical_or_cadence_lines":hits[:20]}
    except Exception as e:return {"status":"blocked","error_type":type(e).__name__}

def load_panel(panel):
    if panel=="tadarida":
        d,a=tadarida()
        d["alternate"]=np.nan
        a["native_height_field"]="height_above_msl";a["alternate_field"]=None
        return d,a
    c=json.loads((Path("contract")/PANELS[panel]).read_text())
    if "field" not in c["vertical"]:c["vertical"]["field"]=c["vertical"]["primary_field"]
    h=c["vertical"]["field"];alt=next(k for k in FIELDS if k!=h)
    ua="batter-slope-v22/1.0"
    gps,headers=core.read_csv(core.get(c["source"]["gps"],ua))
    refs,_=core.read_csv(core.get(c["source"]["reference"],ua))
    pre=core.build_pre_numeric(gps,headers,refs,c)
    rec=json.loads(Path("contract/roost_slope_existing_srtm_receipt_v21.json").read_text())["panels"][panel]
    assert rec["source_gps_md5"]==c["source"]["gps"]["md5"]
    grids=load_tiles(rec,-32768)
    rows=[];fail=0;target=0;badtime=0
    for i,r in enumerate(gps):
        animal=core.iid(r)
        if not animal:continue
        try:t=pd.to_datetime(core.parse_time(r.get("timestamp","")),utc=True)
        except Exception:badtime+=1;continue
        sid=pre["session_for_row"].get(i)
        eligible=bool(sid and pre["session_meta"][sid]["cohort"] in pre["admitted_cohorts"])
        lat=core.finite_float(r.get("location_lat"));lon=core.finite_float(r.get("location_long"))
        height=core.finite_float(r.get(h));other=core.finite_float(r.get(alt))
        ground=np.nan
        if eligible:
            target+=1
            if lat is not None and lon is not None:
                try:ground=bilinear_hgt(grids,lat,lon,-32768)
                except Exception:fail+=1
            else:fail+=1
        rows.append((str(animal),sid if eligible else None,t,lat,lon,height,ground,other))
    d=pd.DataFrame(rows,columns=["animal","session","time","lat","lon","height","ground","alternate"])
    d=d.sort_values(["animal","time"],kind="stable").reset_index(drop=True)
    d["duplicate"]=d.duplicated(["animal","time"],keep=False)
    a={"native_height_field":h,"alternate_field":alt if alt in headers else None,
       "native_gps_md5":c["source"]["gps"]["md5"],"raw_rows":len(gps),"source_admitted_rows":target,
       "bad_timestamp":badtime,"DEM_missing_rows":fail,"pinned_tiles":len(grids),
       "duplicate_timestamp_rows":int(d.duplicate.sum()),"readme":readme(panel)}
    return d,a

def height_audit(d,a):
    s=d.loc[d.session.notna()].copy()
    out={}
    for c in ("height","alternate"):
        v=s[c].dropna().to_numpy(float);v=v[np.isfinite(v)]
        out[c]={"n":len(v),"unique":len(np.unique(v)),
            "quantiles":summary(v),"zero_fraction":float(np.mean(v==0)) if len(v) else None,
            "integer_fraction":float(np.mean(np.isclose(v,np.round(v),rtol=0,atol=1e-8))) if len(v) else None}
    pair=s[["height","alternate"]].dropna()
    out["paired_native_minus_alternate"]={"n":len(pair),"difference_m":summary(pair.height-pair.alternate)}
    return out

def anchors(d,target,tol):
    # Contiguous valid raw fixes, deterministic nearest actual endpoint.
    # Do not bridge known exclusions, duplicate times, missing heights or long gaps.
    out=[];chains=0;anchor_rows=0;stretches=0
    for _,g in d.groupby("animal",sort=True):
        g=g.sort_values("time",kind="stable").reset_index(drop=True)
        secs=g.time.astype("int64").to_numpy()/1e9
        valid=(g.session.notna()&~g.duplicate&g[["lat","lon","height","ground"]].notna().all(axis=1)).to_numpy()
        valid&=np.isfinite(g[["lat","lon","height","ground"]].to_numpy(float)).all(axis=1)
        sess=g.session.to_numpy()
        cuts=[];start=None
        for i in range(len(g)):
            if not valid[i]:
                if start is not None:cuts.append((start,i));start=None
                continue
            if start is None:start=i
            elif sess[i]!=sess[i-1] or secs[i]-secs[i-1]>target+tol or secs[i]<=secs[i-1]:
                cuts.append((start,i));start=i
        if start is not None:cuts.append((start,len(g)))
        stretches+=len(cuts)
        for lo,hi in cuts:
            p=lo;chosen=[p]
            def emit(chosen):
                nonlocal chains,anchor_rows
                if len(chosen)<3:return
                chains+=1;anchor_rows+=len(chosen)
                q=g.iloc[chosen].copy()
                q["session"]="chain_"+str(chains)
                out.append(q)
            while p+1<hi:
                t=secs[p]+target
                l=max(p+1,int(np.searchsorted(secs,t-tol,side="left")))
                r=min(hi,int(np.searchsorted(secs,t+tol,side="right")))
                if l<r:
                    # ascending times and argmin first tie.
                    nxt=l+int(np.argmin(np.abs(secs[l:r]-t)))
                    chosen.append(nxt);p=nxt
                else:
                    emit(chosen);p+=1;chosen=[p]
            emit(chosen)
    return (pd.concat(out,ignore_index=True) if out else d.iloc[:0].copy()),{
       "valid_stretches":stretches,"chains_ge3_anchors":chains,"anchor_rows":anchor_rows}

def gate(s,lo,hi):
    if s.empty:return np.zeros(0,dtype=bool)
    ok=s.valid&s.prev_valid&s.dt.between(lo,hi)&s.prev_dt.between(lo,hi)
    ok&=s.hspeed.between(2,50)&s.prev_speed.between(2,50)&(s.y.abs()<=15)&(s.prev_rate.abs()<=15)
    return ok.to_numpy()&np.isfinite(s[["prev_rate","hspeed","start_height","start_ground","y","q"]].to_numpy(float)).all(axis=1)
def roster(s,ok):
    d=s.loc[ok].copy()
    d["log_dt"]=np.log(d.dt)
    counts=d.animal.value_counts()
    return d.loc[d.animal.isin(counts[counts>=50].index)].copy()
def scores(d):
    if d.empty:return {"n":0,"animals":0,"status":"insufficient_animals"}
    return {"dt":summary(d.dt),"q":summary(d.q),"vertical_rate":summary(d.y),
       "absolute_vertical_displacement_m":summary(np.abs(d.y*d.dt)),
       "unchanged_height_fraction":float(np.mean(d.y==0)),
       "steps_per_animal":summary(d.animal.value_counts()),
       "LOIO":compare(d,BASE),
       "less_shared_altitude_noise":compare(d,[x for x in BASE if x not in ("prev_rate","start_height")])}
def analyze(d,target,tol):
    a,info=anchors(d,target,tol)
    result={"target_s":target,"tolerance_s":tol,"anchors":info}
    if a.empty:return {**result,"status":"no_anchors"}
    sn=steps(a);ok=gate(sn,target-tol,target+tol)
    result["native_eligible_before_animal_gate"]=int(ok.sum())
    result["native"]=scores(roster(sn,ok))
    if a.alternate.notna().any():
        sa=steps(a.assign(height=a.alternate))
        assert len(sn)==len(sa) and sn[["animal","session","step"]].equals(sa[["animal","session","step"]])
        joint=ok&gate(sa,target-tol,target+tol)
        n=roster(sn,joint);v=roster(sa,joint)
        assert n.index.equals(v.index)
        result["paired_height_fields"]={"eligible_before_animal_gate":int(joint.sum()),
          "n":len(n),"animals":int(n.animal.nunique()),"native_minus_alternate_rate":summary(n.y-v.y),
          "native":scores(n),"alternate":scores(v)}
    return result

def main():
    report={"status":"measurement_diagnostic","claim_boundary":"Prior source panels; cadence matched, height reference and measurement error may differ. No causal trait/year claim.","panels":{}}
    dest=OUT/"audit_v22_slope.json"
    def save():dest.write_text(json.dumps(report,indent=2,allow_nan=False))
    save()
    for p in ["tadarida"]+list(PANELS):
        try:
            d,src=load_panel(p)
            report["panels"][p]={"source":src,"height_audit":height_audit(d,src),"runs":{}}
            save()
            for target,tol in [(120,10),(60,5)]:
                report["panels"][p]["runs"][str(target)]=analyze(d,target,tol);save()
            report["panels"][p]["status"]="computed"
        except Exception as e:
            report["panels"].setdefault(p,{})
            report["panels"][p].update(status="blocked",error_type=type(e).__name__)
        save()
    print(dest.read_text())
    return 0 if any(p.get("status")=="computed" for p in report["panels"].values()) else 2
if __name__=="__main__":raise SystemExit(main())
