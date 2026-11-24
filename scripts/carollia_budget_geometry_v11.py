"""V11 exploratory sensitivity; exact published WingMorph.txt required.
Run python scripts/carollia_budget_geometry_v11.py /path/WingMorph.txt
No raw data redistribution; no field behavior inference.
"""
import sys, pathlib, hashlib, json
import numpy as np
import pandas as pd
from scipy.optimize import brentq
from carollia_individual_wind_geometry_v10 import compute
MD5="83c25901480df694ab049016955ce130"
def cv(x): return float(np.std(x,ddof=1)/np.mean(x))
def jac(r):
    i,j=np.triu_indices(len(r),1)
    return float(np.median(np.minimum(r[i]**2,r[j]**2).sum(1)/np.maximum(r[i]**2,r[j]**2).sum(1)))
def metrics(r):
    a=np.pi*(r*r).mean(axis=1)
    return {"cv":cv(a),"jaccard":jac(r),"median_area":float(np.median(a))}
def crossing(fn,lo=0,hi=1.5):
    xs=np.linspace(lo,hi,round((hi-lo)/.05)+1)
    return [float(brentq(fn,a,b)) for a,b in zip(xs[:-1],xs[1:]) if fn(a)*fn(b)<0]
def main(path):
    raw=path.read_bytes()
    assert hashlib.md5(raw).hexdigest()==MD5
    d=pd.read_csv(path,sep="\t")
    assert len(d)==116 and not d.isna().any().any()
    m=d.M.to_numpy();b=d.B.to_numpy();s=d.S.to_numpy()
    z=np.log(m/np.exp(np.log(m).mean()))
    allrows=np.ones(len(m),bool); distinct=~d.ID.str.casefold().duplicated(keep=False).to_numpy()
    results={}
    for name,model,lo,hi in [("primary","author",5,7),("wider_low","author",2,7),("wider_high","author",5,9),("reduced","reduced",5,7)]:
        g=compute(m,b,s,model=model,lo=lo,hi=hi,step=.01)
        rr={}
        for w in (2,4):
            for label,k in [("all",allrows),("exclude_collision",distinct)]:
                a0=g[0]["area"][k];aw=g[w]["area"][k];x=z[k]
                t=np.log(aw/a0)
                base=np.var(t,ddof=1)+2*np.cov(np.log(a0),t,ddof=1)[0,1]
                slope=4*np.cov(x,t,ddof=1)[0,1]
                def delta(alpha):
                    q=np.exp(2*alpha*x)
                    return cv(aw*q)-cv(a0*q)
                rr[f"wind{w}_{label}"]={"cv_roots":crossing(delta),"logvar_intercept":float(base),
                    "logvar_slope":float(slope),"logvar_root":float(-base/slope) if slope else None,
                    "delta_cv":{str(alpha):delta(alpha) for alpha in (0,.5,2/3,.75,1,1.25,1.5)}}
                for alpha in (0,.75,1):
                    lhs=np.var(np.log(aw)+2*alpha*x,ddof=1)-np.var(np.log(a0)+2*alpha*x,ddof=1)
                    assert np.isclose(lhs,base+slope*alpha,atol=1e-12)
        results[name]=rr
        if name=="primary":
            results["budget_jaccard"]={}
            for alpha in (0,.5,2/3,.75,1,1.25,1.5):
                q=np.exp(alpha*z)[:,None]
                results["budget_jaccard"][str(alpha)]={"calm":metrics(g[0]["radius"]*q),"w4":metrics(g[4]["radius"]*q)}
    # Joint time/energy constraints, independently enumerate both speed choices.
    a=2.4*(m*9.8)**2/(1.205*np.pi*b*b);c=.5*1.205*(.02*s+.00285*m**(2/3))
    fine=np.linspace(5,7,201);pp=a[:,None]/fine+c[:,None]*fine**3
    T=float(np.median(1/pp[np.arange(len(m)),np.argmin(pp/fine,axis=1)]))
    u=fine[::10];p=pp[:,::10];theta=np.arange(180)*2*np.pi/180
    joint={}
    for ratio in (.5,.75,1,1.5):
        joint[str(ratio)]={}
        for w in (0,4):
            r=np.empty((len(m),len(theta)))
            for j,t in enumerate(theta):
                g=np.sqrt(u*u-(w*np.sin(t))**2);gp=g+w*np.cos(t);gm=g-w*np.cos(t)
                assert min(gp.min(),gm.min())>0
                time=1/gp[:,None]+1/gm[None,:]
                cost=(p/gp)[:,:,None]+(p/gm)[:,None,:]
                r[:,j]=np.minimum(1/cost,ratio*T/time[None,:,:]).max((1,2))
            joint[str(ratio)][str(w)]=metrics(r)
    results["joint_time_energy"]={"Tref_seconds_per_J":T,"metrics":joint}
    result={"scope":"conditional exploration with measured morphology not measured budgets or behavior","source_sha256":hashlib.sha256(raw).hexdigest(),"results":results}
    out=pathlib.Path("results/carollia_budget_geometry_v11.json");out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    print(out.read_text())
if __name__=="__main__":main(pathlib.Path(sys.argv[1]))
