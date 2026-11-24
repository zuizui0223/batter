"""V19 conditional slope-following versus modeled vertical wind, prior Tadarida data."""
import io,hashlib,json
import numpy as np
import pandas as pd
from roost_fd_source_audit_v2 import OUT
from roost_fd_source_audit_v3 import quant
from run_uplift_reaction_norm import download,EXPECTED_MD5,EXPECTED_SIZE

BASE=["prev_rate","log_dt","hspeed","start_msl","start_ground","hwind"]

def load():
    b=download()
    assert len(b)==EXPECTED_SIZE and hashlib.md5(b).hexdigest()==EXPECTED_MD5
    d=pd.read_csv(io.BytesIO(b),low_memory=False)
    cols=["location-lat","location-long","height-above-msl","height_terrain","height_true","U.Component","V.Component","W.Component"]
    assert set(cols+["animal-id","BatDay","timestamp"])<=set(d)
    for c in cols:d[c]=pd.to_numeric(d[c],errors="coerce").replace([np.inf,-np.inf],np.nan)
    d["time"]=pd.to_datetime(d.timestamp,format="mixed",utc=True,errors="coerce")
    d=d.dropna(subset=["animal-id","BatDay","time"]).sort_values(["animal-id","BatDay","time"],kind="stable")
    d["duplicate"]=d.duplicated(["animal-id","BatDay","time"],keep=False)
    residual=d["height-above-msl"]-d.height_terrain-d.height_true
    qc={"timestamp_valid_rows":len(d),"duplicate_timestamp_rows":int(d.duplicate.sum()),
        "MSL_minus_ground_minus_AGL_m":quant(residual.dropna()),
        "source_bytes":len(b),"source_md5":EXPECTED_MD5}
    return d,qc

def steps(d):
    parts=[]
    for (animal,session),g in d.groupby(["animal-id","BatDay"],sort=True):
        g=g.reset_index(drop=True)
        if len(g)<3:continue
        a=g.iloc[:-1].reset_index(drop=True);b=g.iloc[1:].reset_index(drop=True)
        dt=(b.time-a.time).dt.total_seconds().to_numpy()
        lat1=np.deg2rad(a["location-lat"].to_numpy());lat2=np.deg2rad(b["location-lat"].to_numpy())
        dl=np.deg2rad(b["location-long"].to_numpy()-a["location-long"].to_numpy())
        h=np.sin((lat2-lat1)/2)**2+np.cos(lat1)*np.cos(lat2)*np.sin(dl/2)**2
        dist=2*6371008.8*np.arcsin(np.sqrt(np.clip(h,0,1)))
        with np.errstate(divide="ignore",invalid="ignore"):
            y=(b["height-above-msl"].to_numpy()-a["height-above-msl"].to_numpy())/dt
            q=(b.height_terrain.to_numpy()-a.height_terrain.to_numpy())/dt
            speed=dist/dt
        z=pd.DataFrame({"animal":str(animal),"session":str(animal)+"::"+str(session),
             "step":np.arange(len(a)),"dt":dt,"y":y,"q":q,"hspeed":speed,
             "start_msl":a["height-above-msl"],"start_ground":a.height_terrain,
             "hwind":np.hypot(a["U.Component"],a["V.Component"]),"W":a["W.Component"],
             "dup":a.duplicate|b.duplicate})
        z["prev_rate"]=z.y.shift();z["prev_dt"]=z.dt.shift();z["prev_speed"]=z.hspeed.shift()
        z["prev_dup"]=z.dup.shift(fill_value=True)
        parts.append(z)
    return pd.concat(parts,ignore_index=True)

def select(s,low,high,parity):
    # Previous interval is used only for observed prior state; never skip across missing rows.
    ok=s.dt.between(low,high)&s.prev_dt.between(low,high)&s.hspeed.between(2,50)&s.prev_speed.between(2,50)
    ok&=(s.y.abs()<=15)&(s.prev_rate.abs()<=15)&~s.dup&~s.prev_dup
    x=s.loc[ok].copy()
    if parity:x=x[x.step%2==0].copy()
    x["log_dt"]=np.log(x.dt)
    x=x.replace([np.inf,-np.inf],np.nan).dropna(subset=BASE+["q","W","y"])
    counts=x.animal.value_counts()
    x=x[x.animal.isin(counts[counts>=50].index)].reset_index(drop=True)
    return x

def fit(X,y,weights):
    mu=np.average(X,axis=0,weights=weights);sd=np.sqrt(np.average((X-mu)**2,axis=0,weights=weights))
    sd=np.where(sd>1e-12,sd,1)
    Z=(X-mu)/sd;cy=np.average(y,weights=weights)
    beta=np.linalg.solve(Z.T@(weights[:,None]*Z)+10*np.eye(Z.shape[1]),Z.T@(weights*(y-cy)))
    return mu,sd,cy,beta

def cv(d,block,base):
    y=d.y.to_numpy();blocks=sorted(d[block].unique());animals=d.animal.to_numpy()
    models={"M0":base,"M1":base+["q"],"M2":base+["q","W"]}
    preds={k:np.full(len(d),np.nan) for k in models}
    coefs={k:[] for k in models}
    if len(set(animals))<6:return {"status":"insufficient_animals","n":len(d),"animals":len(set(animals))}
    for b in blocks:
        te=d[block].to_numpy()==b;tr=~te
        if len(set(animals[tr]))<5:return {"status":"insufficient_training_animals","n":len(d)}
        cnt=d.loc[tr,"animal"].value_counts()
        w=d.loc[tr,"animal"].map(1/cnt).to_numpy();w=w/w.mean()
        for key,cols in models.items():
            X=d[cols].to_numpy(float);mu,sd,cy,beta=fit(X[tr],y[tr],w)
            preds[key][te]=cy+((X[te]-mu)/sd)@beta
            coefs[key].append(dict(zip(cols,beta/sd)))
    assert all(np.isfinite(v).all() for v in preds.values())
    loss={k:pd.DataFrame({"animal":animals,"sq":(p-y)**2}).groupby("animal").sq.mean() for k,p in preds.items()}
    res={"status":"exploratory","n":len(d),"animals":len(set(animals)),"blocks":len(blocks),"models":{}}
    for k,v in loss.items():
        res["models"][k]={"equal_animal_RMSE":float(np.sqrt(v.mean())),
            "fold_q_coefficients":quant([c["q"] for c in coefs[k]]) if "q" in models[k] else {},
            "fold_W_coefficients":quant([c["W"] for c in coefs[k]]) if "W" in models[k] else {}}
    res["contrasts"]={}
    for a,b in [("M1","M0"),("M2","M1"),("M2","M0")]:
        diff=loss[a]-loss[b]
        res["contrasts"][a+"_minus_"+b]={"delta_RMSE":float(np.sqrt(loss[a].mean())-np.sqrt(loss[b].mean())),
          "animals_improved":int((diff<0).sum()),"animal_delta_MSE_quantiles":quant(diff)}
    return res

def main():
    report={"status":"exploratory_prior_source_only","claim_boundary":"Conditional on observed horizontal path; modeled winds, not selection or causal uplift. No raw locations."}
    dest=OUT/"audit_v19_slope.json"
    def save():dest.write_text(json.dumps(report,indent=2,allow_nan=False))
    save()
    try:
        d,report["source_QC"]=load()
        s=steps(d);report["raw_step_dt"]=quant(s.loc[s.dt>0,"dt"])
        report["runs"]={}
        for title,lo,hi,p in [("primary",5,120,True),("all_steps",5,120,False),("shorter",10,60,True),("longer",30,300,True)]:
            x=select(s,lo,hi,p)
            report["runs"][title]={"n":len(x),"animals":int(x.animal.nunique()),"sessions":int(x.session.nunique()),
                "steps_per_animal":quant(x.animal.value_counts()),"q":quant(x.q),"W":quant(x.W),
                "animals_both_q_signs":int(sum(g.q.min()<0<g.q.max() for _,g in x.groupby("animal"))),
                "animals_both_W_signs":int(sum(g.W.min()<0<g.W.max() for _,g in x.groupby("animal")))}
            if len(x):
                report["runs"][title]["LOIO"]=cv(x,"animal",BASE)
                if title=="primary":
                    report["runs"][title]["session_holdout"]=cv(x,"session",BASE)
                    report["runs"][title]["less_shared_altitude_noise"]=cv(x,"animal",[k for k in BASE if k not in ("prev_rate","start_msl")])
            save()
    except Exception as e:report["status"]="blocked";report["error"]=type(e).__name__+": "+str(e)[:180]
    save();print(dest.read_text())
    return 0 if report["status"]!="blocked" else 2
if __name__=="__main__":raise SystemExit(main())
