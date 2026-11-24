"""V14 cross-model robustness. No empirical movement or budget observations."""
import hashlib, json, pathlib, sys
import numpy as np
import pandas as pd
from carollia_art_geometry_v13 import summarize, SOURCES, coeffs

def run(source,work):
    raw=source.read_bytes()
    assert hashlib.md5(raw).hexdigest()==SOURCES["CarolliaWings.txt"][1]
    assert hashlib.sha256(raw).hexdigest()==SOURCES["CarolliaWings.txt"][2]
    d=pd.read_csv(source,sep=r"\s+",dtype={"ID":str})
    d=d.loc[~d.ID.str.casefold().duplicated(keep=False)].reset_index(drop=True)
    assert d.ART.value_counts().to_dict()=={"F":284,"NT":156,"T":49}
    m=d.BMass.to_numpy()/1000;b=d.WSpan.to_numpy()/1000;s=d.WArea.to_numpy()/1e6;lab=d.ART.to_numpy()
    support=pd.read_csv(work/"afpt_support.csv")
    common=support.common.astype(str).str.lower().eq("true").to_numpy()
    u=support.speed.to_numpy()[common]
    p=pd.read_csv(work/"afpt_curves.csv").to_numpy()[:,common]
    report={"scope":"conditional cross-model scenario; no observed budgets or behavior","source_sha256":SOURCES["CarolliaWings.txt"][2],"frequency_hz_assumed":9,
      "support":{"n_common":int(common.sum()),"n_total":len(common),"speeds":u.tolist(),"valid_counts":support.n_valid.tolist(),"full_band":bool(common.mean()>=.8 and common[0] and common[-1])}}
    if len(u)<2:
        report["status"]="STOP_NO_COMMON_SUPPORT"
        return report
    assert p.shape==(len(m),len(u)) and np.isfinite(p).all() and (p>0).all()
    a,c=coeffs(m,b,s,"author")
    pn=a[:,None]/u+c[:,None]*u**3
    report["status"]="PASS_CONDITIONAL_COMPARISON" if report["support"]["full_band"] else "RESTRICTED_SUPPORT_ONLY"
    report["models"]={}
    gm=np.exp(np.log(m).mean())
    theta=np.arange(180)*2*np.pi/180
    caps=[.75,1.,1.5]
    for label,power in [("afpt",p),("norberg_common_grid",pn)]:
        ref=float(np.median((1/power[np.arange(len(m)),np.argmin(power/u,axis=1)])[lab!="F"]))
        area={};joint={r:{} for r in caps};bounds={}
        for w in (0,4):
            radii=np.empty((len(m),len(theta)))
            time_radii={r:np.empty_like(radii) for r in caps}
            count=np.zeros(len(m))
            for j,t in enumerate(theta):
                g=np.sqrt(u*u-(w*np.sin(t))**2);gp=g+w*np.cos(t);gn=g-w*np.cos(t)
                assert min(gp.min(),gn.min())>0
                cp=power/gp;cn=power/gn
                radii[:,j]=1/(cp.min(1)+cn.min(1))
                count+=np.isin(cp.argmin(1),[0,len(u)-1])+np.isin(cn.argmin(1),[0,len(u)-1]).astype(int)
                cost=cp[:,:,None]+cn[:,None,:]
                time=1/gp[:,None]+1/gn[None,:]
                for r in caps:
                    time_radii[r][:,j]=np.minimum(1/cost,r*ref/time).max((1,2))
            area[w]=np.pi*np.mean(radii*radii,axis=1)
            bounds[w]=float(np.mean(count/(2*len(theta))))
            for r in caps:joint[r][w]=np.pi*np.mean(time_radii[r]**2,axis=1)
        report["models"][label]={"boundary_fraction":bounds,"Tref_seconds_per_J":ref,
            "energy":{str(alpha):summarize(area[0]*(m/gm)**(2*alpha),area[4]*(m/gm)**(2*alpha),m,lab) for alpha in (0,.75,1)},
            "joint":{str(r):summarize(joint[r][0],joint[r][4],m,lab) for r in caps}}
    return report
if __name__=="__main__":
    result=run(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
    p=pathlib.Path("results/carollia_art_afpt_v14.json");p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    print(json.dumps(result,indent=2,allow_nan=False))
    if result["status"].startswith("STOP"):raise SystemExit(2)
