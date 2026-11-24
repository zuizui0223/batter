"""V13 locked, conditional ART geometry. Source hash, SI and ID gates.
Not observed activity or measured physiological budgets. No raw data printed.
"""
import hashlib, json, pathlib, urllib.request
import numpy as np
import pandas as pd
from carollia_individual_wind_geometry_v10 import compute, coeffs

ROOT=pathlib.Path("results")
SOURCES={"CarolliaWings.txt":(20738264,"a7bb180dc8db5e66a116ba55929fa8c5","492100e67f429e0e0e57c698ab0d680d791d12cb20f67a0b3caa66b0fcc74d6f"),
"WingMorph.txt":(7126170,"83c25901480df694ab049016955ce130","46fb9c339feb2a9b0a9277aa52dd3e8e25ffd598cd1457a663f96ed8c8a394a4")}
def load(name):
    rec,md5,sha=SOURCES[name]
    req=urllib.request.Request(f"https://zenodo.org/api/records/{rec}/files/{name}/content",headers={"User-Agent":"batter-research-source-audit/1.0"})
    with urllib.request.urlopen(req,timeout=40) as f: b=f.read(100001)
    assert hashlib.md5(b).hexdigest()==md5 and hashlib.sha256(b).hexdigest()==sha
    import io
    return pd.read_csv(io.BytesIO(b),sep=r"\s+",dtype={"ID":str})
def q(x): return [float(z) for z in np.quantile(x,[.05,.5,.95])]
def cv(a): return float(np.std(a,ddof=1)/np.mean(a))
def stats(a0,aw,lab):
    ret=aw/a0
    out={}
    for g in ["T","NT","F"]:
        ix=lab==g
        a,b,r=a0[ix],aw[ix],ret[ix]
        out[g]={"n":int(ix.sum()),"calm_geomean":float(np.exp(np.mean(np.log(a)))),"wind_geomean":float(np.exp(np.mean(np.log(b)))),"ret_q":q(r),"cv0":cv(a),"cvw":cv(b),"delta_logvar":float(np.var(np.log(b),ddof=1)-np.var(np.log(a),ddof=1))}
    return out
def contrast(y,m,lab):
    t,n=lab=="T",lab=="NT"
    low=max(m[t].min(),m[n].min()); high=min(m[t].max(),m[n].max())
    keep=(t|n)&(m>=low)&(m<=high)
    out={"unadjusted_logratio":float(np.log(y[t]).mean()-np.log(y[n]).mean()),"mass_support_g":[float(low*1000),float(high*1000)],"nT":int((keep&t).sum()),"nNT":int((keep&n).sum())}
    if min(out["nT"],out["nNT"])>=10:
        x=np.log(m[keep]/np.exp(np.mean(np.log(m[keep]))))
        X=np.column_stack([np.ones(len(x)),(lab[keep]=="T").astype(float),x,x*x])
        beta=np.linalg.lstsq(X,np.log(y[keep]),rcond=None)[0]
        out["adjusted_logratio"]=float(beta[1])
        out["design_rank"]=int(np.linalg.matrix_rank(X))
    return out
def summarize(a0,aw,m,lab):
    return {"groups":stats(a0,aw,lab),"contrasts":{"calm":contrast(a0,m,lab),"wind":contrast(aw,m,lab),"retention":contrast(aw/a0,m,lab)}}
def joint(m,b,s,lab):
    a,c=coeffs(m,b,s,"author")
    u=np.linspace(5,7,21); p=a[:,None]/u+c[:,None]*u**3
    male=lab!="F"; ref=float(np.median(1/p[np.arange(len(m)),np.argmin(p/u,axis=1)][male]))
    caps=[.75,1.,1.5]; radii={ratio:{} for ratio in caps}
    for w in [0,4]:
        rs={ratio:np.zeros((len(m),180)) for ratio in caps}
        for j,th in enumerate(np.arange(180)*2*np.pi/180):
            g=np.sqrt(u*u-(w*np.sin(th))**2);gp=g+w*np.cos(th);gm=g-w*np.cos(th)
            tt=1/gp[:,None]+1/gm[None,:];cost=(p/gp)[:,:,None]+(p/gm)[:,None,:]
            for ratio in caps:rs[ratio][:,j]=np.minimum(1/cost,ratio*ref/tt[None,:,:]).max((1,2))
        for ratio in caps:radii[ratio][w]=np.pi*(rs[ratio]**2).mean(1)
    out={str(r):summarize(radii[r][0],radii[r][4],m,lab) for r in caps}
    out["counterfactual_T075_NT1"] = summarize(np.where(lab=="T",radii[.75][0],radii[1.][0]),np.where(lab=="T",radii[.75][4],radii[1.][4]),m,lab)
    return {"Tref_seconds_per_J":ref,"caps":out}
def main():
    ROOT.mkdir(exist_ok=True)
    d=load("CarolliaWings.txt")
    assert len(d)==491 and d.ART.value_counts().to_dict()=={"F":286,"NT":156,"T":49}
    assert ((d.Sex=="F")==(d.ART=="F")).all()
    assert d.ID.notna().all()
    dup=d.ID.str.casefold().duplicated(keep=False)
    report={"scope":"model-derived conditional mechanical accessibility, not observed behavior","source_sha256":SOURCES["CarolliaWings.txt"][2],"audit":{"n":len(d),"unique":d.ID.nunique(),"duplicate_rows":int(dup.sum()),"duplicate_groups":d.loc[dup,"ART"].value_counts().to_dict(),"identical_duplicate_rows":int(d.loc[dup].duplicated(keep=False).sum()),"nCapt":d.NCapt.value_counts(dropna=False).sort_index().to_dict()}}
    d=d.loc[~dup].reset_index(drop=True)
    assert not d[["BMass","WSpan","WArea","AR","WL"]].isna().any().any()
    assert (d[["BMass","WSpan","WArea","AR","WL"]]>0).all().all()
    m=d.BMass.to_numpy()/1000;b=d.WSpan.to_numpy()/1000;s=d.WArea.to_numpy()/1e6;lab=d.ART.to_numpy()
    ar=b*b/s;wl=m*9.8/s
    assert np.all((m>.005)&(m<.05)&(b>.15)&(b<.6)&(s>.005)&(s<.05))
    errors={name:q(np.abs(obs-pred)/pred) for name,obs,pred in [("AR",d.AR.to_numpy(),ar),("WL",d.WL.to_numpy(),wl)]}
    report["audit"].update(n_retained=len(d),n_by_group=d.ART.value_counts().to_dict(),relative_trait_errors=errors,trait_medians={g:{"mass_g":float(np.median(m[lab==g])*1000),"span_mm":float(np.median(b[lab==g])*1000),"area_mm2":float(np.median(s[lab==g])*1e6),"AR":float(np.median(ar[lab==g])),"WL":float(np.median(wl[lab==g]))} for g in ["F","NT","T"]})
    try:
        old=load("WingMorph.txt")
        same=old.Sex.to_numpy()[:,None]==d.Sex.to_numpy()[None,:]
        ok=same&(abs(old.M.to_numpy()[:,None]-m[None,:])<=.00005)&(abs(old.B.to_numpy()[:,None]-b[None,:])<=.00005)&(abs(old.S.to_numpy()[:,None]-s[None,:])<=.00001)
        report["audit"]["fingerprint_candidates"]={"pairs":int(ok.sum()),"old_rows":int(ok.any(1).sum()),"new_rows":int(ok.any(0).sum())}
    except Exception as e:report["audit"]["fingerprint_status"]=repr(e)
    if any(v[1]>.01 or v[2]>.05 for v in errors.values()):
        report["status"]="STOP_TRAIT_UNIT_DISCREPANCY"
    else:
        report["status"]="PASS_CONDITIONAL_SCENARIOS"
        geom={}
        gm=np.exp(np.mean(np.log(m)));gb=np.exp(np.mean(np.log(b)));gs=np.exp(np.mean(np.log(s)))
        for name,model,bb,ss in [("norberg","author",b,s),("reduced","reduced",b,s),("mass_only","author",gb*(m/gm)**(1/3),gs*(m/gm)**(2/3))]:
            z=compute(m,bb,ss,model=model,lo=5,hi=7,winds=(0,2,4),nt=180,step=.02)
            geom[name]={"boundary4_q":q(z[4]["bounds"]),"wind":{}}
            for w in [2,4]:
                geom[name]["wind"][str(w)]={}
                for alpha in [0,.75,1]:
                    factor=(m/gm)**(2*alpha)
                    geom[name]["wind"][str(w)][str(alpha)]=summarize(z[0]["area"]*factor,z[w]["area"]*factor,m,lab)
        report["geometry"]=geom
        report["joint"]=joint(m,b,s,lab)
    p=ROOT/"carollia_art_v13.json";p.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    # Concise aggregate log: full results artifact includes all scenarios.
    print(json.dumps({"status":report["status"],"audit":report["audit"],
        "geometry":{k:{"wind4_equal":v["wind"]["4"]["0"],"wind4_alpha1":v["wind"]["4"]["1"],"boundary4_q":v["boundary4_q"]} for k,v in report.get("geometry",{}).items()},
        "joint":report.get("joint",{})},indent=2,allow_nan=False))
    if not report["status"].startswith("PASS"):raise SystemExit(2)
if __name__=="__main__":main()
