"""V38: exact source-score reconciliation; conditional within-track diagnostic."""
import hashlib,io,json,pathlib,re
from collections import Counter
import numpy as np
import pandas as pd
import acoustic_buzz_geometry_v36 as v36
from bayer_field_join_v17 import fetch
OUT=pathlib.Path("results/acoustic_point_mark_v38.json")
def q(a):
    a=np.asarray(a,float)
    a=a[np.isfinite(a)]
    return np.quantile(a,[0,.05,.5,.95,1]).tolist() if len(a) else []
def token_kind(s):
    s=str(s).strip()
    if not s:return "blank"
    if re.fullmatch(r"(?i)nan|na|n/a|null",s):return "missing_text"
    if re.fullmatch(r"[+-]?\d+(?:[.,]\d+)?",s):return "number"
    if re.fullmatch(r"(?i)[+-]?\d+(?:[.,]\d+)?e[+-]?\d+",s):return "scientific"
    if re.fullmatch(r"\d{1,2}:\d{2}:\d{2}(?:[.,]\d+)?",s):return "clock"
    if re.fullmatch(r"\d{1,2}:\d{2}(?:[.,]\d+)?",s):return "short_clock"
    return "other"
def night_summary(rows,field):
    if not rows:return {"trajectories":0,"nights":0,"status":"STOP_LOW_SUPPORT"}
    d=pd.DataFrame(rows);d=d[np.isfinite(d[field])]
    sizes=d.groupby("date").size()
    selected=d[d.date.isin(sizes[sizes>=10].index)]
    out={"trajectories_all":len(d),"nights_all":len(sizes),"trajectories":len(selected),"nights":int(selected.date.nunique()),
         "block_sizes":sorted(int(x) for x in selected.groupby("date").size())}
    if len(selected)<100 or selected.date.nunique()<5:out["status"]="STOP_LOW_SUPPORT";return out
    a=selected.groupby("date")[field].mean().to_numpy()
    loo=(a.sum()-a)/(len(a)-1)
    out.update(status="SCORED",mean_equal_night=float(a.mean()),positive_nights=int((a>0).sum()),
       negative_nights=int((a<0).sum()),leave_one_night_range=[float(loo.min()),float(loo.max())],
       trajectory_quantiles=q(selected[field]))
    if "pairs" in selected:
        out["pairs"]=int(selected.pairs.sum());out["unequal_score_pairs"]=int(selected.unequal.sum())
        out["fraction_unequal"]=float(selected.unequal.sum()/selected.pairs.sum())
        out["mean_pair_vertical_separation_m"]=float(selected.groupby("date").mean_dz.mean().mean())
    return out
def greedy(g,width_limit):
    m=g["score"].between(0,1)&g[["x (m)","y (m)","z (m)","Imprecision","width"]].notna().all(axis=1)&g.Imprecision.gt(0)
    if width_limit is not None:m &= g.width.le(width_limit)
    p=g.loc[m]
    if len(p)<2:return None
    z=p["z (m)"].to_numpy();r=p.radius.to_numpy();u=p.Imprecision.to_numpy();w=p.width.to_numpy();score=p.score.to_numpy()
    # Pair selection independent of mark magnitude, deterministic chronological source-row tie break.
    i,j=np.triu_indices(len(p),1)
    dr=np.abs(r[i]-r[j]);du=np.abs(u[i]-u[j]);dz=np.abs(z[i]-z[j])
    k=(dr<=1)&(du<=1)&(dz>=np.maximum(.5,(w[i]+w[j])/2))
    i,j,dr,du,dz=i[k],j[k],dr[k],du[k],dz[k]
    order=np.lexsort((j,i,dr+du))
    used=set();v=[];height=[]
    for k in order:
        a,b=int(i[k]),int(j[k])
        if a in used or b in used:continue
        used.update((a,b));v.append(float((score[a]-score[b])*np.sign(z[a]-z[b])));height.append(float(dz[k]))
    if not v:return None
    return {"date":g.date.iloc[0],"type":g.typeSite.iloc[0],"contrast":float(np.mean(v)),
        "pairs":len(v),"unequal":int(np.count_nonzero(v)),"mean_dz":float(np.mean(height))}
def test():
    g=pd.DataFrame({"date":["d"]*2,"typeSite":["C"]*2,"score":[.1,.4],"x (m)":[0,0],"y (m)":[1,1],"z (m)":[0,1],"Imprecision":[1,1],"width":[.2,.2],"radius":[1,np.sqrt(2)]})
    x=greedy(g,2);assert x["pairs"]==1 and np.isclose(x["contrast"],.3)
    g.loc[1,"width"]=4;assert greedy(g,2) is None and greedy(g,None) is None
def run():
    test();b,_=fetch(v36.URL,3186436)
    assert len(b)==3186436 and hashlib.sha256(b).hexdigest()==v36.SHA and hashlib.md5(b).hexdigest()=="60ce63b79fd8a5b9bc4771997de97839"
    raw=pd.read_csv(io.BytesIO(b),sep=";",dtype=str,keep_default_na=False,encoding="utf-8-sig")
    raw.columns=raw.columns.str.strip()
    assert len(raw)==15346
    d=raw.copy()
    for c in v36.NUM:d[c],_=v36.numeric(d[c])
    d["score"]=d.buzz_proba;d["placeholder"]=d.score.eq(999);d["valid"]=d.score.between(0,1)
    d["radius"]=np.linalg.norm(d[["x (m)","y (m)","z (m)"]].to_numpy(float),axis=1)
    d["width"]=d["-dz (m)"].abs()+d["+dz (m)"].abs()
    other=~(d.placeholder|d.valid)
    result={"scope":"exact source placeholder diagnostic; conditional within-trajectory contrast, not observed captures",
        "status":"SOURCE_DIAGNOSTIC","sha256":v36.SHA,"rows":len(d),"test":"PASS",
        "exact999":int(d.placeholder.sum()),"valid_probability":int(d.valid.sum()),"other_invalid":int(other.sum()),
        "other_invalid_quantiles":q(d.loc[other,"score"]),
        "time_token_patterns":dict(Counter(raw.time.map(token_kind))),
        "date_token_patterns":dict(Counter(raw.date.map(token_kind)))}
    dif=[];invalid=Counter();missing=[];eligible=[];run_lengths=[];n_all999=0;n_allvalid=0;n_mixed=0;duptimes=0;constant=0
    for key,g in d.groupby(v36.KEY,sort=False):
        y=g.mean_buzz_proba.to_numpy(float);v=g.loc[g.valid,"score"].to_numpy(float)
        is999=bool(g.placeholder.all());n_all999+=is999;n_allvalid+=bool(g.valid.all());n_mixed+=bool(g.valid.any() and g.placeholder.any())
        duptimes+=int(g.time.duplicated().sum())
        x=g.score.to_numpy()
        if len(x):
            r=np.flatnonzero(np.r_[True,x[1:]!=x[:-1],True]);run_lengths.extend(np.diff(r).tolist())
        constant+=int(g.valid.any() and g.loc[g.valid,"score"].nunique()==1)
        if g.valid.any() and g.placeholder.any():
            p=g[g.placeholder];a=g[g.valid]
            missing.append({"date":g.date.iloc[0],"type":g.typeSite.iloc[0],
                "radius_difference":float(p.radius.mean()-a.radius.mean()),"z_difference":float(p["z (m)"].mean()-a["z (m)"].mean())})
        if not np.isfinite(y).all():
            invalid["nonparseable"]+=1
            invalid["nonparseable_all999"]+=is999
            for k,n in Counter(raw.loc[g.index,"mean_buzz_proba"].map(token_kind)).items():invalid["token_"+k]+=n
            continue
        if y.min()<0 or y.max()>1 or np.ptp(y)>1e-8:invalid["other_invalid_mean"]+=1;continue
        if not len(v) or (~(g.placeholder|g.valid)).any():
            invalid["valid_archived_mean_no_valid_reconstruction"]+=1;continue
        delta=abs(float(v.mean())-float(y[0]));dif.append(delta)
        if delta<=1e-6:eligible.append(g)
    valid_count=1319-invalid["nonparseable"]-invalid["other_invalid_mean"]
    assert valid_count==1301
    result.update(trajectory_count=1319,all999_trajectories=int(n_all999),allvalid_trajectories=int(n_allvalid),
        mixed_trajectories=int(n_mixed),invalid_archived_mean=dict(invalid),valid_archived_mean_trajectories=valid_count,
        reconstructable_trajectories=len(dif),mean_reconstruction_abs_difference_quantiles=q(dif),
        match_le1e6=int((np.asarray(dif)<=1e-6).sum()),match_le1e4=int((np.asarray(dif)<=1e-4).sum()),
        fraction_valid_archived_means_matching=len(eligible)/valid_count,
        duplicate_literal_time_rows_within_trajectory=int(duptimes),equal_score_run_length_quantiles=q(run_lengths),
        constant_valid_score_trajectories=int(constant))
    result["placeholder_geometry"]={}
    for name in ("C","pooled"):
        a=[r for r in missing if name=="pooled" or r["type"]=="C"]
        result["placeholder_geometry"][name]={k:night_summary(a,k) for k in ("radius_difference","z_difference")}
    dates=set(g.date.iloc[0] for g in eligible)
    ok=int(other.sum())==0 and len(eligible)/valid_count>=.95 and len(eligible)>=100 and len(dates)>=5
    result["point_gate"]=bool(ok)
    if not ok:
        result["status"]="STOP_POINT_MARK_GATE";return result
    result["status"]="POINT_MARK_DIAGNOSTIC"
    result["matched_geometry"]={}
    for width in (2,None):
        pairs=[r for g in eligible if (r:=greedy(g,width)) is not None]
        result["matched_geometry"]["width_le2" if width==2 else "all_widths"]={
            "control":night_summary([r for r in pairs if r["type"]=="C"],"contrast"),
            "pooled":night_summary(pairs,"contrast")}
    return result
if __name__=="__main__":
    try:r=run()
    except Exception as e:r={"status":"STOP","error":repr(e)}
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(r,indent=2,allow_nan=False,ensure_ascii=False)+"\n");print(OUT.read_text())
