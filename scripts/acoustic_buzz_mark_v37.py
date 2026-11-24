"""V37: source-mark prediction only, no reconstruction of uncertain point scores."""
import hashlib,io,json,pathlib,re
import numpy as np
import pandas as pd
import acoustic_buzz_geometry_v36 as v36
from bayer_field_join_v17 import fetch
OUT=pathlib.Path("results/acoustic_buzz_mark_v37.json")

def token_audit(s):
    s=s.astype(str).str.strip()
    patterns={
        "blank":r"(?i)^(?:|NA|NaN|null|N/A)$",
        "integer":r"^[+-]?\d+$",
        "decimal_dot":r"^[+-]?(?:\d+\.\d*|\.\d+)$",
        "decimal_comma":r"^[+-]?(?:\d+,\d*|,\d+)$",
        "scientific":r"^[+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+)[eE][+-]?\d+$",
        "date_like":r"^\d{1,4}[-/]\d{1,2}(?:[-/]\d{1,4})?(?:\s.*)?$",
        "percent":r"^[+-]?\d+(?:[.,]\d+)?\s*%$",
        "spreadsheet_error":r"^#(?:DIV/0!|N/A|VALUE!|REF!|NUM!|NAME\?|NULL!)$"}
    covered=np.zeros(len(s),bool);counts={}
    for name,pat in patterns.items():
        m=s.str.fullmatch(pat).to_numpy();counts[name]=int((m&~covered).sum());covered|=m
    counts["other"]=int((~covered).sum())
    a,_=v36.numeric(s);q=a.dropna().to_numpy(float)
    # Examples of unparseable tokens are intentionally not emitted.
    return {"patterns":counts,"finite":len(q),"quantiles":v36.q(q),
        "min_max":[float(q.min()),float(q.max())] if len(q) else [],
        "negative":int((q<0).sum()),"above1":int((q>1).sum()),
        "fraction_in_range":{str(k):float(np.mean((q>=0)&(q<=k))) if len(q) else None for k in (1,100,1000,10000)}}
def diagnostic(d):
    out={c:token_audit(d[c]) for c in ("buzz_proba","mean_buzz_proba")}
    a=d[v36.KEY+["buzz_proba","mean_buzz_proba"]].copy()
    for c in ("buzz_proba","mean_buzz_proba"):a[c],_=v36.numeric(a[c])
    valid=[];bad={"nonparseable":0,"out_of_range":0,"nonconstant":0}
    for _,g in a.groupby(v36.KEY,sort=False):
        y=g.mean_buzz_proba.to_numpy(float);x=g.buzz_proba.to_numpy(float)
        if not np.isfinite(y).all():bad["nonparseable"]+=1;continue
        if y.min()<0 or y.max()>1:bad["out_of_range"]+=1;continue
        if np.ptp(y)>1e-8:bad["nonconstant"]+=1;continue
        if np.isfinite(x).all():valid.append((float(y[0]),x))
    out["invalid_trajectory_mean_reasons"]=bad
    out["complete_diagnostic_groups"]=len(valid);out["fixed_scaling_diagnostics"]={}
    for factor in (1.,.01,.001,.0001):
        delta=np.array([abs(y-float(np.mean(x*factor))) for y,x in valid])
        xx=np.concatenate([x*factor for _,x in valid]) if valid else np.array([])
        out["fixed_scaling_diagnostics"][str(factor)]={"abs_diff_quantiles":v36.q(delta),
           "groups_within_1e-6":int((delta<=1e-6).sum()),
           "row_fraction_in_0_1":float(np.mean((xx>=0)&(xx<=1))) if len(xx) else None}
    out["boundary"]="No scale selected; no pointwise score or reconstructed mean used in models."
    return out
def run():
    v36.test()
    b,_=fetch(v36.URL,3186436)
    assert len(b)==3186436 and hashlib.md5(b).hexdigest()=="60ce63b79fd8a5b9bc4771997de97839" and hashlib.sha256(b).hexdigest()==v36.SHA
    d=pd.read_csv(io.BytesIO(b),sep=";",dtype=str,keep_default_na=False,encoding="utf-8-sig")
    d.columns=d.columns.str.strip()
    enc=diagnostic(d)
    a,audit,status=v36.aggregate(d.copy())
    result={"scope":"archived trajectory mark only; separate source encoding diagnostic; no capture or occupancy inference",
      "source_sha256":v36.SHA,"test":"PASS","audit":audit,"encoding_diagnostic":enc,"status":status}
    if a is None:return result
    exact=(audit["trajectory_stages"]["groups"]==1319 and len(a)==1202 and
           audit["type_trajectory_counts"]=={"C":737,"T":465} and audit["n_blocks"]==9)
    result["v36_support_reproduction"]=bool(exact)
    if not exact:result["status"]="STOP_V36_SUPPORT_DRIFT";return result
    control=a.type.eq("C")
    result["type_mapping"]="C is control from article. T retained as literal category, probable treatment, not a verified codebook."
    result["panels"]={}
    for k,z in [("control_primary",a[control]),("pooled",a),("control_width_le2m",a[control&a.dz.le(2)]),("pooled_width_le2m",a[a.dz.le(2)])]:
        result["panels"][k]=v36.panel(z)
    result["positive_gate"]=bool(all(result["panels"][k].get("gate",False) for k in ("control_primary","pooled")))
    result["status"]="ARCHIVED_MARK_COMPARISON_COMPLETE"
    return result
if __name__=="__main__":
    try:r=run()
    except Exception as e:r={"status":"STOP","error":repr(e)}
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(r,indent=2,allow_nan=False,ensure_ascii=False)+"\n");print(OUT.read_text())
