"""V21 matched conditional ground-following across prior panels, no wind predictors."""
import json,sys
from pathlib import Path
import numpy as np
import pandas as pd
from roost_fd_source_audit_v2 import OUT
from roost_fd_source_audit_v3 import quant
from roost_slope_tadarida_v19 import load as load_tadarida,fit
from roost_slope_pinned_srtm_v21 import load_tiles,bilinear_hgt
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import scripts.run_new_species_replications as core

BASE=["prev_rate","log_dt","hspeed","start_height","start_ground"]
PANELS={
    "phyllostomus_2016":"phyllostomus_2016_dry_architecture_v1.json",
    "phyllostomus_2022":"phyllostomus_replication_v1.json",
    "phyllostomus_2023":"phyllostomus_2023_replication_v1.json"}
def summary(x):
    a=np.asarray(x,dtype=float);a=a[np.isfinite(a)]
    return quant(a) if len(a) else {}

def prior(panel):
    c=json.loads((Path("contract")/PANELS[panel]).read_text())
    if "field" not in c["vertical"]:c["vertical"]["field"]=c["vertical"]["primary_field"]
    h=c["vertical"]["field"]
    ua="batter-slope-v21/1.0"
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
        height=core.finite_float(r.get(h))
        ground=np.nan
        if eligible:
            target+=1
            if lat is not None and lon is not None:
                try:ground=bilinear_hgt(grids,lat,lon,-32768)
                except Exception:fail+=1
            else:fail+=1
        rows.append((animal,sid if eligible else None,t,lat,lon,height,ground))
    d=pd.DataFrame(rows,columns=["animal","session","time","lat","lon","height","ground"])
    d=d.sort_values(["animal","time"],kind="stable").reset_index(drop=True)
    d["duplicate"]=d.duplicated(["animal","time"],keep=False)
    audit={"native_height_field":h,"gps_md5":c["source"]["gps"]["md5"],
      "raw_rows":len(gps),"parsed_rows":len(d),"bad_timestamp":badtime,
      "source_admitted_rows":target,"DEM_missing_rows":fail,"pinned_tiles":len(grids),
      "admitted_cohorts":len(pre["admitted_cohorts"]),
      "duplicate_timestamp_rows":int(d.duplicate.sum())}
    return d,audit

def tadarida():
    d,qc=load_tadarida()
    d=d.rename(columns={"animal-id":"animal","BatDay":"session","location-lat":"lat","location-long":"lon",
        "height-above-msl":"height","height_terrain":"ground"})
    d["session"]=d.animal.astype(str)+"::"+d.session.astype(str)
    return d[["animal","session","time","lat","lon","height","ground","duplicate"]],qc

def steps(d):
    parts=[]
    for aid,g in d.groupby("animal",sort=True):
        g=g.sort_values("time",kind="stable").reset_index(drop=True)
        if len(g)<3:continue
        a=g.iloc[:-1].reset_index(drop=True);b=g.iloc[1:].reset_index(drop=True)
        dt=(b.time-a.time).dt.total_seconds().to_numpy()
        la1=np.deg2rad(a.lat.to_numpy(float));la2=np.deg2rad(b.lat.to_numpy(float))
        dl=np.deg2rad(b.lon.to_numpy(float)-a.lon.to_numpy(float))
        hav=np.sin((la2-la1)/2)**2+np.cos(la1)*np.cos(la2)*np.sin(dl/2)**2
        dist=2*6371008.8*np.arcsin(np.sqrt(np.clip(hav,0,1)))
        valid=a.session.notna()&b.session.notna()&(a.session==b.session)&~a.duplicate&~b.duplicate
        with np.errstate(divide="ignore",invalid="ignore"):
            y=(b.height.to_numpy(float)-a.height.to_numpy(float))/dt
            q=(b.ground.to_numpy(float)-a.ground.to_numpy(float))/dt
            speed=dist/dt
        z=pd.DataFrame({"animal":str(aid),"session":a.session,"dt":dt,"y":y,"q":q,
           "hspeed":speed,"start_height":a.height,"start_ground":a.ground,"valid":valid})
        z["prev_rate"]=z.y.shift();z["prev_dt"]=z.dt.shift();z["prev_speed"]=z.hspeed.shift()
        z["prev_valid"]=z.valid.shift(fill_value=False)&(z.session==z.session.shift())
        # Fixed parity on full ordered rows; no outcome-dependent subsampling.
        z["step"]=np.arange(len(z))
        parts.append(z)
    if not parts:return pd.DataFrame()
    return pd.concat(parts,ignore_index=True)

def select(s,lo,hi,parity):
    ok=s.valid&s.prev_valid&s.dt.between(lo,hi)&s.prev_dt.between(lo,hi)
    ok&=s.hspeed.between(2,50)&s.prev_speed.between(2,50)&(s.y.abs()<=15)&(s.prev_rate.abs()<=15)
    d=s.loc[ok].copy()
    if parity:d=d[d.step%2==0].copy()
    d["log_dt"]=np.log(d.dt)
    d=d.replace([np.inf,-np.inf],np.nan).dropna(subset=BASE+["y","q"])
    counts=d.animal.value_counts();d=d[d.animal.isin(counts[counts>=50].index)].reset_index(drop=True)
    return d

def compare(d,base):
    groups=sorted(d.animal.unique())
    out={"n":len(d),"animals":len(groups),"sessions":int(d.session.nunique()),"status":"insufficient_animals"}
    if len(groups)<6:return out
    y=d.y.to_numpy(float);aid=d.animal.to_numpy()
    preds=[np.full(len(d),np.nan),np.full(len(d),np.nan)]
    coefs=[]
    for k in groups:
        te=aid==k;tr=~te
        counts=d.loc[tr,"animal"].value_counts()
        w=d.loc[tr,"animal"].map(1/counts).to_numpy();w=w/w.mean()
        for i,cols in enumerate([base,base+["q"]]):
            X=d[cols].to_numpy(float)
            mu,sd,cy,b=fit(X[tr],y[tr],w)
            preds[i][te]=cy+((X[te]-mu)/sd)@b
            if i:coefs.append(float(b[-1]/sd[-1]))
    assert all(np.isfinite(p).all() for p in preds)
    m=[pd.DataFrame({"animal":aid,"loss":(p-y)**2}).groupby("animal").loss.mean() for p in preds]
    r0=float(np.sqrt(m[0].mean()));r1=float(np.sqrt(m[1].mean()))
    out.update(status="exploratory",M0_RMSE=r0,M1_RMSE=r1,delta_RMSE=r1-r0,
       relative_RMSE_improvement=(r0-r1)/r0 if r0>0 else None,
       animals_improved=int((m[1]<m[0]).sum()),q_coefficient=summary(coefs),
       animal_delta_MSE=summary(m[1]-m[0]))
    return out

def main():
    result={"status":"exploratory_prior_panels","claim_boundary":"Conditional on observed paths; no causal trait effect, no independent new cohorts, different DEM/datum semantics.","panels":{}}
    dest=OUT/"audit_v21_slope.json"
    def save():dest.write_text(json.dumps(result,indent=2,allow_nan=False))
    for panel in ["tadarida"]+list(PANELS):
        try:
            d,a=tadarida() if panel=="tadarida" else prior(panel)
            s=steps(d);p={"source":a,"status":"computed","interval_s":summary(s.loc[(s.dt>0)&s.valid,"dt"]),"runs":{}}
            for label,lo,hi,parity in [("primary",5,120,True),("all_steps",5,120,False),("shorter",10,60,True),("longer",30,300,True)]:
                x=select(s,lo,hi,parity)
                q={"dt":summary(x.dt),"q":summary(x.q),"steps_per_animal":summary(x.animal.value_counts()),
                    "animals_both_q_signs":int(sum(g.q.min()<0<g.q.max() for _,g in x.groupby("animal"))),
                    "LOIO":compare(x,BASE)}
                if label=="primary":q["less_shared_altitude_noise"]=compare(x,[k for k in BASE if k not in ("prev_rate","start_height")])
                p["runs"][label]=q
            result["panels"][panel]=p
        except Exception as e:
            # Do not print a source exception that might contain tile IDs or coordinates.
            result["panels"][panel]={"status":"blocked","error_type":type(e).__name__}
        save()
    print(dest.read_text())
    return 0 if any(p["status"]=="computed" for p in result["panels"].values()) else 2
if __name__=="__main__":raise SystemExit(main())
