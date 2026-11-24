"""V27: Does prior horizontal-route directness modify subsequent conditional terrain response?
Observational proxy, not verified foraging/commuting. Prior GPS panels; no raw locations.
"""
import json
import numpy as np
import pandas as pd
from roost_fd_source_audit_v2 import OUT
from roost_slope_matched_panels_v21 import summary,fit
from roost_slope_device_matched_scale_v24 import load,tadarida,anchors,interval

PANELS=["tadarida","phyllostomus_2016","phyllostomus_2023"]
BASE=["log_dt","hspeed","start_ground","prior_speed","R"]

def dist(a,b):
    la,lb=np.deg2rad([a.lat,b.lat]);dl=np.deg2rad(b.lon-a.lon)
    h=np.sin((lb-la)/2)**2+np.cos(la)*np.cos(lb)*np.sin(dl/2)**2
    return float(2*6371008.8*np.arcsin(np.sqrt(np.clip(h,0,1))))

def windows(d):
    a,info=anchors(d,60,5);rows=[];n=0
    if a.empty:return pd.DataFrame(),info
    for (animal,session),g in a.groupby(["animal","session"],sort=True):
        g=g.sort_values("time").reset_index(drop=True)
        for i in range(0,len(g)-3,3):
            r0,r1,r2,r3=[g.iloc[j] for j in (i,i+1,i+2,i+3)]
            n+=1
            dt1=(r1.time-r0.time).total_seconds();dt2=(r2.time-r1.time).total_seconds()
            if not (55<=dt1<=65 and 55<=dt2<=65):continue
            s1=dist(r0,r1);s2=dist(r1,r2)
            if not (2<=s1/dt1<=50 and 2<=s2/dt2<=50):continue
            s=interval(r2,r3)
            if s is None or not 55<=s["dt"]<=65:continue
            direct=dist(r0,r2)/(s1+s2)
            if not -1e-10<=direct<=1+1e-10:raise ValueError("invalid route directness")
            direct=float(np.clip(direct,0,1))
            rows.append({**s,"animal":str(animal),"session":str(session),"prior_speed":(s1+s2)/(dt1+dt2),
              "R":direct,"q_R":s["q"]*direct})
    info={**info,"candidate_windows":n,"valid_windows_before_animal_gate":len(rows)}
    if not rows:return pd.DataFrame(),info
    x=pd.DataFrame(rows)
    assert np.isfinite(x[BASE+["q","q_R","y"]].to_numpy(float)).all()
    cnt=x.animal.value_counts()
    return x[x.animal.isin(cnt[cnt>=50].index)].copy(),info

def cv(d):
    if d.empty:return {"status":"no_windows","n":0,"animals":0}
    groups=sorted(d.animal.unique())
    r={"n":len(d),"animals":len(groups),"chains":int(d.session.nunique()),
       "windows_per_animal":summary(d.animal.value_counts()),"status":"insufficient_animals"}
    if len(groups)<6:return r
    models={"M0":BASE,"M1":BASE+["q"],"M2":BASE+["q","q_R"]}
    aid=d.animal.to_numpy();y=d.y.to_numpy(float)
    pred={k:np.full(len(d),np.nan) for k in models};coef={k:[] for k in models}
    for a in groups:
        te=aid==a;tr=~te
        counts=d.loc[tr,"animal"].value_counts()
        w=d.loc[tr,"animal"].map(1/counts).to_numpy();w=w/w.mean()
        for k,cols in models.items():
            X=d[cols].to_numpy(float);mu,sd,cy,b=fit(X[tr],y[tr],w)
            pred[k][te]=cy+((X[te]-mu)/sd)@b
            coef[k].append(dict(zip(cols,map(float,b/sd))))
    assert all(np.isfinite(v).all() for v in pred.values())
    loss={k:pd.DataFrame({"animal":aid,"sq":(v-y)**2}).groupby("animal").sq.mean() for k,v in pred.items()}
    rmse={k:float(np.sqrt(v.mean())) for k,v in loss.items()}
    r["status"]="exploratory"
    r["models"]={k:{"equal_animal_RMSE":rmse[k]} for k in models}
    r["M1_q_coefficients"]=summary([c["q"] for c in coef["M1"]])
    r["M2_q_R_coefficients"]=summary([c["q_R"] for c in coef["M2"]])
    r["M2_effective_q_at_R085"]=summary([c["q"]+.85*c["q_R"] for c in coef["M2"]])
    r["M2_effective_q_at_R095"]=summary([c["q"]+.95*c["q_R"] for c in coef["M2"]])
    r["contrasts"]={}
    for k,b in [("M1","M0"),("M2","M1")]:
        v=loss[k]-loss[b]
        r["contrasts"][k+"_minus_"+b]={"delta_RMSE":rmse[k]-rmse[b],
         "relative_RMSE_improvement":(rmse[b]-rmse[k])/rmse[b] if rmse[b]>0 else None,
         "animals_improved":int((v<0).sum()),"animal_delta_MSE":summary(v)}
    return r

def descriptive(d):
    if d.empty:return {"n":0}
    x=d.q*d.dt;y=d.y*d.dt;nz=(x!=0)&(y!=0)
    a=[]
    for _,g in d.groupby("animal"):
        if len(g)<10:continue
        u=(g.q*g.dt).rank();v=(g.y*g.dt).rank()
        if u.std()>0 and v.std()>0:
            c=u.corr(v)
            if np.isfinite(c):a.append(c)
    return {"n":len(d),"animals":int(d.animal.nunique()),"q":summary(d.q),"R":summary(d.R),
       "animals_both_q_signs":int(sum(g.q.min()<0<g.q.max() for _,g in d.groupby("animal"))),
       "median_animal_displacement_spearman":summary(a),"nonzero_both":int(nz.sum()),
       "same_sign_fraction":float((np.sign(x[nz])==np.sign(y[nz])).mean()) if nz.any() else None}
def run(d):
    x,a=windows(d)
    r={"window_audit":a,"primary":cv(x)}
    if x.empty:return r
    lo=x[x.R<=.85];hi=x[x.R>=.95]
    r["all"]=descriptive(x);r["low_directness"]=descriptive(lo);r["high_directness"]=descriptive(hi)
    lc=lo.animal.value_counts();hc=hi.animal.value_counts()
    keep=set(lc[lc>=10].index)&set(hc[hc>=10].index)
    r["common_support_animals"]=len(keep)
    # Same prior model comparison on all windows of supported animals.
    # Do not condition the primary continuous analysis on response.
    r["common_support_sensitivity"]=cv(x[x.animal.isin(keep)])
    return r
def main():
    r={"status":"conditional_movement_context_diagnostic",
       "claim_boundary":"Prior horizontal route directness, not observed feeding state. Conditional on realized target path; no causal behavioral effect.","panels":{}}
    dest=OUT/"audit_v27_slope.json"
    def save():dest.write_text(json.dumps(r,indent=2,allow_nan=False))
    save()
    for p in PANELS:
        try:
            d,_=tadarida() if p=="tadarida" else load(p)
            d["alternate"]=np.nan
            r["panels"][p]={"status":"computed",**run(d)}
        except Exception as e:r["panels"][p]={"status":"blocked","error_type":type(e).__name__}
        save()
    print(dest.read_text())
    return 0 if all(v["status"]=="computed" for v in r["panels"].values()) else 2
if __name__=="__main__":raise SystemExit(main())
