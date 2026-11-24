"""V29 fixed-window joint directional choice and continuous vertical-rate predictive scoring.
No raw coordinates, identities, or individual predictions exported.
"""
import json
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from scipy.special import logsumexp
from scipy.stats import t,norm
from roost_fd_source_audit_v2 import OUT
from roost_slope_matched_panels_v21 import summary,fit
from roost_slope_direction_choice_v28 import (
    PANELS,SEED,NCONTROL,anchors,displacement,destinations,candidate_features,
    center,fit_choice,load,tadarida,Copernicus)
from roost_slope_two_proxy_v26 import HASHES

EXPECTED={
    "tadarida":(1458,7,-2.617559102538118,-2.608297124069317),
    "phyllostomus_2016":(805,9,-1.5144688257587342,-1.5143048761308464),
    "phyllostomus_2023":(1371,11,-1.7271012619829784,-1.7237417826972548)}
DF=5

def choices_with_vertical(d,dem):
    # Replay V28, keeping an additional response and covariates on exactly the same sets.
    a,info=anchors(d,60,5);rng=np.random.default_rng(SEED)
    feats=[];animals=[];responses=[];vertical=[]
    counts={"candidate_windows":0,"horizontal_gate":0,"incomplete_DEM_sets":0,"complete_sets_before_animal_gate":0}
    if a.empty:raise RuntimeError("no anchor chains")
    for (animal,session),g in a.groupby(["animal","session"],sort=True):
        g=g.sort_values("time").reset_index(drop=True)
        for i in range(0,len(g)-2,2):
            a0,a1,a2=[g.iloc[j] for j in (i,i+1,i+2)]
            counts["candidate_windows"]+=1
            d0,t0=displacement(a0,a1);d1,t1=displacement(a1,a2)
            dt0=(a1.time-a0.time).total_seconds();dt1=(a2.time-a1.time).total_seconds()
            if not(55<=dt0<=65 and 55<=dt1<=65 and 2<=d0/dt0<=50 and 2<=d1/dt1<=50):continue
            counts["horizontal_gate"]+=1
            h=np.r_[t1,rng.uniform(-np.pi,np.pi,NCONTROL)]
            lat,lon=destinations(a1.lat,a1.lon,h,d1)
            lat[0]=a2.lat;lon[0]=a2.lon
            start=dem.value(float(a1.lat),float(a1.lon))
            if start is None:
                counts["incomplete_DEM_sets"]+=1;continue
            z=[dem.value(float(la),float(lo)) for la,lo in zip(lat,lon)]
            if any(v is None or not np.isfinite(v) for v in z):
                counts["incomplete_DEM_sets"]+=1;continue
            gradient=(np.asarray(z,float)-start)/d1
            X=candidate_features(h,t0,gradient)
            y=(float(a2.height)-float(a1.height))/dt1
            v=np.r_[np.log(dt1),d1/dt1,d0/dt0,start,X[0,:8],gradient[0]*d1/dt1]
            if not(np.isfinite(X).all() and np.isfinite(v).all() and np.isfinite(y)):
                raise ValueError("nonfinite on V28 retained set")
            feats.append(X);animals.append(str(animal));responses.append(y);vertical.append(v)
    counts["complete_sets_before_animal_gate"]=len(feats)
    if not feats:raise RuntimeError("no complete sets")
    X=np.asarray(feats);aid=np.asarray(animals);y=np.asarray(responses);v=np.asarray(vertical)
    cnt=pd.Series(aid).value_counts();keep=np.isin(aid,cnt[cnt>=50].index)
    return X[keep],aid[keep],y[keep],v[keep],{**info,**counts,"animals_before_gate":len(cnt),"animals_after_gate":int(len(set(aid[keep])))}

def t_scale(res,w):
    def objective(log_s):
        scale=np.exp(log_s)
        return -float(np.dot(w,t.logpdf(res/scale,df=DF)-log_s))
    r=minimize_scalar(objective,bounds=(-12,12),method="bounded",options={"xatol":1e-9})
    if not r.success or not np.isfinite(r.x):raise RuntimeError("residual scale optimizer failed")
    return float(np.exp(r.x))

def animal_means(aid,values):
    return pd.DataFrame({"animal":aid,"v":values}).groupby("animal").v.mean()

def contrast(a,b):
    d=a-b
    return {"delta_equal_animal_mean":float(d.mean()),"animals_improved":int((d>0).sum()),"animal_deltas":summary(d)}

def run(panel,X,aid,y,V):
    en,ea,h0,h1=EXPECTED[panel]
    assert (len(aid),len(set(aid)))==(en,ea)
    groups=sorted(set(aid));n=len(aid)
    H={k:np.full(n,np.nan) for k in ["H0","H1"]}
    T={k:np.full(n,np.nan) for k in ["V0","V1"]}
    G={k:np.full(n,np.nan) for k in T}
    P={k:np.full(n,np.nan) for k in T}
    scale={k:[] for k in T};coef=[]
    for animal in groups:
        te=aid==animal;tr=~te
        cnt=pd.Series(aid[tr]).value_counts();w=pd.Series(aid[tr]).map(1/cnt).to_numpy();w/=w.mean()
        for k,p in [("H0",8),("H1",9)]:
            b=fit_choice(X[tr,:,:p],w);u=center(X[te,:,:p])@b
            H[k][te]=u[:,0]-logsumexp(u,axis=1)
        for k,p in [("V0",12),("V1",13)]:
            mu,sd,cy,b=fit(V[tr,:p],y[tr],w)
            train=cy+((V[tr,:p]-mu)/sd)@b
            pred=cy+((V[te,:p]-mu)/sd)@b
            res=y[tr]-train;s=t_scale(res,w)
            g=max(float(np.sqrt(np.average(res*res,weights=w))),np.exp(-12))
            P[k][te]=pred
            T[k][te]=t.logpdf((y[te]-pred)/s,df=DF)-np.log(s)
            G[k][te]=norm.logpdf(y[te],loc=pred,scale=g)
            scale[k].append(s)
            if k=="V1":coef.append(float(b[-1]/sd[-1]))
    for a in [H,T,G,P]:assert all(np.isfinite(v).all() for v in a.values())
    hm={k:animal_means(aid,v) for k,v in H.items()}
    assert np.allclose([hm["H0"].mean(),hm["H1"].mean()],[h0,h1],atol=1e-7,rtol=0)
    tm={k:animal_means(aid,v) for k,v in T.items()}
    gm={k:animal_means(aid,v) for k,v in G.items()}
    out={"n":n,"animals":len(groups),"V28_score_reproduced":True,
        "direction":{"H0":float(hm["H0"].mean()),"H1":float(hm["H1"].mean()),"increment":contrast(hm["H1"],hm["H0"])},
        "vertical_rate":summary(y),"fraction_abs_rate_gt15":float(np.mean(np.abs(y)>15)),
        "q_coefficient_V1":summary(coef),"vertical":{}}
    for k in T:
        mse=animal_means(aid,(y-P[k])**2)
        out["vertical"][k]={"equal_animal_RMSE":float(np.sqrt(mse.mean())),
            "equal_animal_t_log_density":float(tm[k].mean()),"equal_animal_gaussian_log_density":float(gm[k].mean()),
            "training_t_scale_across_folds":summary(scale[k])}
    def joint(vm):
        m={h+v:hm[h]+vm[v] for h in hm for v in vm}
        dh=hm["H1"]-hm["H0"];dv=vm["V1"]-vm["V0"]
        assert np.allclose((m["H1V1"]-m["H0V0"]).to_numpy(),(dh+dv).to_numpy(),rtol=0,atol=1e-12)
        return {"joint_log_scores":{k:float(v.mean()) for k,v in m.items()},
            "direction_only":contrast(m["H1V0"],m["H0V0"]),
            "vertical_only":contrast(m["H0V1"],m["H0V0"]),
            "both":contrast(m["H1V1"],m["H0V0"]),
            "both_minus_direction_only":contrast(m["H1V1"],m["H1V0"]),
            "both_minus_vertical_only":contrast(m["H1V1"],m["H0V1"])}
    out["student_t_joint"]=joint(tm);out["gaussian_joint_sensitivity"]=joint(gm)
    return out

def test():
    r=np.array([-2.,-1.,0.,1.,2.]);w=np.ones(len(r))
    s=t_scale(r,w);assert np.isfinite(s) and s>0
    assert np.isclose(t_scale(3*r,w),3*s,rtol=1e-6)

def main():
    report={"status":"conditional_joint_endpoint_pilot","claim_boundary":"Choice-set log probability plus vertical-rate log density conditional on known chord length and time. Not an occupancy SDM or proof of feedback.","panels":{}}
    dest=OUT/"audit_v29_slope.json"
    def save():dest.write_text(json.dumps(report,indent=2,allow_nan=False))
    save();test();report["synthetic_test"]="pass";save()
    for p in PANELS:
        q={}
        try:
            d,_=tadarida() if p=="tadarida" else load(p)
            d["alternate"]=np.nan;dem=Copernicus()
            X,aid,y,V,a=choices_with_vertical(d,dem)
            assert {r["sha256"] for r in dem.receipts}==HASHES[p]
            q["choice_audit"]=a;q["DEM_source_hash_match"]=True
            q["result"]=run(p,X,aid,y,V);q["status"]="computed"
        except Exception as e:q["status"]="blocked";q["error_type"]=type(e).__name__
        report["panels"][p]=q;save()
    print(dest.read_text())
    return 0 if all(q["status"]=="computed" for q in report["panels"].values()) else 2
if __name__=="__main__":raise SystemExit(main())
