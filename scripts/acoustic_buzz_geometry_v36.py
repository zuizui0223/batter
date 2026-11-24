"""V36: trajectory-level classifier-score prediction, not prey capture or absolute height."""
import hashlib,io,json,pathlib,unicodedata,urllib.parse
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit
from bayer_field_join_v17 import fetch
OUT=pathlib.Path("results/acoustic_buzz_geometry_v36.json")
NAME="data_bats_barre et al 2023.csv"
URL="https://zenodo.org/api/records/10149959/files/"+urllib.parse.quote(NAME,safe="")+"/content"
SHA="5425b39d4c36184567ec22b38a871ee27a7cf02834e021de4da82f6d0f065cdf"
KEY=["id_site","typeSite","date","Trajectory_identifier"]
CATS=["Species_corrected","guild"]
NUM=["x (m)","y (m)","z (m)","-dz (m)","+dz (m)","Speed","sinuosity","Imprecision","buzz_proba","mean_buzz_proba"]
def q(x):
    a=np.asarray(x,float);a=a[np.isfinite(a)]
    return np.quantile(a,[.05,.5,.95]).tolist() if len(a) else []
def numeric(s):
    s=s.astype(str).str.strip()
    blank=s.str.casefold().isin(["","na","nan","null","n/a"])
    s=s.mask(blank,"")
    # Reject mixed punctuation in individual fields, do not treat sentinel text as a value.
    v=pd.to_numeric(s.str.replace(",",".",regex=False),errors="coerce")
    v=v.where(np.isfinite(v))
    return v,{"blank":int(blank.sum()),"nonparseable_nonblank":int((~blank&v.isna()).sum()),"finite":int(v.notna().sum())}
def norm(s):return unicodedata.normalize("NFKD",str(s)).encode("ascii","ignore").decode().strip().lower()
def aggregate(d):
    audit={"source_rows":len(d),"exact_duplicate_rows":int(d.duplicated(keep=False).sum()),
      "missing_key_rows":int(d[KEY].eq("").any(axis=1).sum()),"numeric":{},"trajectory_stages":{}}
    assert len(d)==15346
    for c in NUM:d[c],audit["numeric"][c]=numeric(d[c])
    d=d.loc[~d[KEY].eq("").any(axis=1)].copy()
    audit["type_counts"]=d.typeSite.value_counts().to_dict()
    audit["guild_counts"]=d.guild.value_counts().to_dict()
    audit["distinct_site_codes"]=int(d.id_site.nunique())
    audit["distinct_literal_dates"]=int(d.date.nunique())
    audit["site_codes_spanning_dates"]=int((d.groupby("id_site").date.nunique()>1).sum())
    # Paper reports nine sampling nights at nine farms. No assuming arbitrary date codes are nights.
    parsed={}
    for fmt in ("%Y-%m-%d","%d/%m/%Y","%m/%d/%Y","%d-%m-%Y","%Y/%m/%d","%Y%m%d","%d.%m.%Y"):
        t=pd.to_datetime(d.date,format=fmt,errors="coerce")
        if t.notna().all() and t.between("2022-09-21","2022-10-01").all():
            parsed[fmt]=t.dt.strftime("%Y-%m-%d")
    distinct={tuple(t.unique()) for t in parsed.values()}
    audit["valid_date_formats"]=list(parsed)
    if parsed and len(distinct)==1:d["date"]=next(iter(parsed.values()))
    elif d.date.nunique()!=9:
        return None,audit,"STOP_DATE_GROUPING"
    audit["date_grouping"]="parsed" if parsed and len(distinct)==1 else "nine literal date groups (author night count)"
    # Union dates sharing a site code. Hold all linked records together.
    dates=sorted(d.date.unique());parent={a:a for a in dates}
    def root(a):
        while parent[a]!=a:a=parent[a]
        return a
    for _,v in d.groupby("id_site"):
        a=sorted(v.date.unique())
        for b in a[1:]:parent[root(b)]=root(a[0])
    d["block"]=d.date.map(lambda a:root(a))
    audit["n_blocks"]=int(d.block.nunique())
    audit["dates_per_block"]=sorted(int(x) for x in d.groupby("block").date.nunique())
    audit["raw_unique_trajectory_ids"]=int(d.Trajectory_identifier.nunique())
    audit["trajectory_key_count"]=int(d.groupby(KEY).ngroups)
    stages={"groups":0,"constant_taxon":0,"valid_target":0,"three_precise_positions":0,"kinematics":0}
    rows=[];diff=[];constant_buzz=0;with_buzz=0;badmean=0;rowcounts=[]
    for _,g in d.groupby(KEY,sort=False):
        stages["groups"]+=1
        if any(g[c].nunique()!=1 or not g[c].iloc[0].strip() for c in CATS):continue
        stages["constant_taxon"]+=1
        y=g.mean_buzz_proba.to_numpy(float)
        if not len(y) or not np.isfinite(y).all() or y.min()<0 or y.max()>1 or np.ptp(y)>1e-8:
            badmean+=1;continue
        stages["valid_target"]+=1
        a=g.buzz_proba.dropna()
        if len(a):
            with_buzz+=1;constant_buzz+=int(a.nunique()==1)
            diff.append(abs(float(a.mean())-float(y[0])))
        rowcounts.append(len(g))
        mask=g[["x (m)","y (m)","z (m)","-dz (m)","+dz (m)","Imprecision"]].notna().all(axis=1)&g.Imprecision.gt(0)
        p=g.loc[mask]
        if len(p)<3:continue
        stages["three_precise_positions"]+=1
        s=g.Speed[g.Speed.between(0,20)];u=g.sinuosity[g.sinuosity.between(1,70)]
        if not len(s) or not len(u):continue
        stages["kinematics"]+=1
        xyz=p[["x (m)","y (m)","z (m)"]].to_numpy()
        dz=p["-dz (m)"].abs()+p["+dz (m)"].abs()
        z=xyz[:,2]
        r={"block":g.block.iloc[0],"type":g.typeSite.iloc[0],"species":g.Species_corrected.iloc[0],"guild":g.guild.iloc[0],
           "y":float(y[0]),"n":len(p),"r":float(np.median(np.linalg.norm(xyz,axis=1))),"imprecision":float(p.Imprecision.median()),"dz":float(dz.median()),
           "mean_speed":float(s.mean()),"min_speed":float(s.min()),"sinuosity":float(u.median()),
           "z":float(np.median(z)),"ziqr":float(np.quantile(z,.75)-np.quantile(z,.25))}
        rows.append(r)
    audit["trajectory_stages"]=stages
    audit["nonconstant_or_invalid_mean_buzz_trajectories"]=badmean
    audit["constant_row_buzz_trajectories"]=constant_buzz
    audit["trajectories_with_row_buzz"]=with_buzz
    audit["abs_published_minus_rowmean_buzz_quantiles"]=q(diff)
    audit["positions_per_valid_target_trajectory_quantiles"]=q(rowcounts)
    if not rows:return None,audit,"STOP_NO_VALID_TRAJECTORIES"
    out=pd.DataFrame(rows);audit["aggregate_trajectories"]=len(out)
    audit["aggregate_positions"]=int(out.n.sum())
    audit["aggregated_block_sizes"]=sorted(int(x) for x in out.block.value_counts())
    audit["type_trajectory_counts"]=out.type.value_counts().to_dict()
    audit["trajectory_median_z_quantiles_m"]=q(out.z)
    audit["trajectory_median_vertical_width_quantiles_m"]=q(out.dz)
    audit["trajectory_median_radius_quantiles_m"]=q(out.r)
    audit["score_quantiles"]=q(out.y)
    return out,audit,"COMPLETE"
def design(tr,te,name):
    # identical training-only one-hot and numeric scaling for each model, no response-based transforms.
    cols=["n","r","imprecision","dz"]
    if name in ("K","H","Hshape"):cols+=["mean_speed","min_speed","sinuosity"]
    def a(d):
        x=np.log1p(d[cols].to_numpy(float))
        if name in ("H","Hshape"):x=np.column_stack([x,d.z,d.z**2])
        if name=="Hshape":x=np.column_stack([x,d.ziqr])
        return x
    x,z=a(tr),a(te);m=x.mean(0);sd=x.std(0);sd[sd<1e-12]=1
    x=(x-m)/sd;z=(z-m)/sd
    for c in ["type","species","guild"]:
        levels=sorted(tr[c].unique())
        x=np.column_stack([x]+[tr[c].eq(k).to_numpy(float) for k in levels])
        z=np.column_stack([z]+[te[c].eq(k).to_numpy(float) for k in levels])
    return np.column_stack([np.ones(len(x)),x]),np.column_stack([np.ones(len(z)),z])
def fit(tr,te,name):
    x,z=design(tr,te,name);y=tr.y.to_numpy(float)
    def fun(b):
        eta=x@b
        loss=np.logaddexp(0,eta).sum()-y@eta+.5*np.sum(b[1:]**2)
        g=x.T@(expit(eta)-y);g[1:]+=b[1:]
        return loss,g
    b=np.zeros(x.shape[1]);b[0]=np.log(np.clip(y.mean(),1e-6,1-1e-6)/np.clip(1-y.mean(),1e-6,1-1e-6))
    r=minimize(fun,b,jac=True,method="L-BFGS-B",options={"maxiter":1000,"ftol":1e-11})
    if not r.success:raise RuntimeError("fractional optimizer failed: "+str(r.message))
    eta=z@r.x;obs=te.y.to_numpy(float)
    return {"loss":float(np.mean(np.logaddexp(0,eta)-obs*eta)),"mse":float(np.mean((expit(eta)-obs)**2))}
def test():
    # Ensure synthetic labels recover known additional height signal without test fitting.
    rng=np.random.default_rng(26);n=240
    d=pd.DataFrame({c:rng.uniform(1,4,n) for c in ("n","r","imprecision","dz","mean_speed","min_speed","sinuosity","ziqr")})
    d["z"]=rng.normal(size=n);d["type"]="control";d["species"]="a";d["guild"]="MRE";d["y"]=expit(-2+1.5*d.z)
    assert fit(d.iloc[:160],d.iloc[160:],"H")["loss"]<fit(d.iloc[:160],d.iloc[160:],"K")["loss"]
def panel(d):
    sizes=d.block.value_counts()
    # Retain entire groups of at least 10, independent of outcome values.
    d=d[d.block.isin(sizes[sizes>=10].index)].copy()
    o={"trajectories":len(d),"blocks":int(d.block.nunique()),"block_sizes":sorted(int(x) for x in d.block.value_counts())}
    if len(d)<100 or d.block.nunique()<5:o["status"]="STOP_LOW_SUPPORT";return o
    models=["D","K","H","Hshape"];rows=[];unseen=0
    for k in sorted(d.block.unique()):
        tr=d[d.block!=k];te=d[d.block==k]
        unseen+=int((~te.species.isin(tr.species)).sum())
        rows.append({m:fit(tr,te,m) for m in models})
    o["status"]="SCORED";o["unseen_species_test_trajectories"]=unseen
    o["mean_metrics"]={m:{k:float(np.mean([r[m][k] for r in rows])) for k in ("loss","mse")} for m in models}
    gains=np.array([r["K"]["loss"]-r["H"]["loss"] for r in rows])
    mseg=np.array([r["K"]["mse"]-r["H"]["mse"] for r in rows])
    loo=(gains.sum()-gains)/(len(gains)-1)
    o["height_gain"]={"log_loss":float(gains.mean()),"mse":float(mseg.mean()),"positive_blocks":int((gains>0).sum()),
      "leave_one_block_range":[float(loo.min()),float(loo.max())]}
    o["gate"]=bool(gains.mean()>0 and mseg.mean()>0 and (gains>0).sum()>len(gains)/2 and loo.min()>0)
    return o
def run():
    test();b,_=fetch(URL,3186436)
    assert len(b)==3186436 and hashlib.md5(b).hexdigest()=="60ce63b79fd8a5b9bc4771997de97839" and hashlib.sha256(b).hexdigest()==SHA
    d=pd.read_csv(io.BytesIO(b),sep=";",dtype=str,keep_default_na=False,encoding="utf-8-sig")
    d.columns=d.columns.str.strip()
    assert all(c in d for c in KEY+CATS+NUM)
    a,audit,status=aggregate(d)
    result={"scope":"detected trajectory buzz classifier mark, array-relative z; no capture or occupancy inference","source_sha256":SHA,"test":"PASS","audit":audit,"status":status}
    if a is None:return result
    control=a.type.map(norm).isin(["control","c","temoin","control site"])
    solar=a.type.map(norm).isin(["solar","s","solar site","solar farm","pv","treatment"])
    result["type_mapping"]={"control_count":int(control.sum()),"solar_count":int(solar.sum()),"unmapped_count":int((~(control|solar)).sum())}
    if not control.any() or not solar.any() or (~(control|solar)).any():
        result["status"]="STOP_UNVERIFIED_TYPE_CODES";return result
    result["panels"]={}
    for k,z in [("control_primary",a[control]),("pooled",a),("control_width_le2m",a[control&a.dz.le(2)]),("pooled_width_le2m",a[a.dz.le(2)])]:
        result["panels"][k]=panel(z)
    result["positive_gate"]=bool(all(result["panels"][k].get("gate",False) for k in ("control_primary","pooled")))
    return result
if __name__=="__main__":
    try:r=run()
    except Exception as e:r={"status":"STOP","error":repr(e)}
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(r,indent=2,allow_nan=False,ensure_ascii=False)+"\n");print(OUT.read_text())
