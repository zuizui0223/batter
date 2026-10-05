#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np,pandas as pd
import statsmodels.formula.api as smf

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("BV",HERE/"phyllostomus_fixed_bin_bivariate_carrier_v1.py")
BV=importlib.util.module_from_spec(spec);spec.loader.exec_module(BV)

def prepared(panel):
    rows,audit=BV.B.prepare(panel)
    if not rows or not audit["colony_retention_pass"]: return None,audit
    rr=BV.standardize_2d(rows)
    if rr is None:return None,audit
    path=BV.B.W.PANELS[panel][0]
    raw,_,_,_=BV.B.W.load_session_rows(panel,path)
    day={}
    for key,vals in raw.items():
        if vals:
            day[(str(key[0]),str(key[1]),str(key[2]))]=min(x[0] for x in vals).date().isoformat()
    out=[]
    for r in rr:
        k=(str(r["cohort"]),str(r["session"]),str(r["iid"]))
        if k in day:
            out.append({"cohort":str(r["cohort"]),"individual":f"{r['cohort']}::{r['iid']}",
                        "day":f"{r['cohort']}::{day[k]}","H":float(r["policy2"][0]),"V":float(r["policy2"][1]),"all":"all"})
    return pd.DataFrame(out),audit

def fit(df,col):
    m=smf.mixedlm(f"{col} ~ 0 + C(cohort)",df,groups=df["all"],re_formula="0",
                  vc_formula={"individual":"0 + C(individual)","day":"0 + C(day)"})
    r=m.fit(reml=True,method="lbfgs",maxiter=500,disp=False)
    vals={n:float(v) for n,v in zip(m.exog_vc.names,r.vcomp)}
    vi=vals["individual"];vd=vals["day"];ve=float(r.scale);tot=vi+vd+ve
    return {"var_individual":vi,"var_day":vd,"var_residual":ve,
            "frac_individual":vi/tot,"frac_day":vd/tot,"frac_residual":ve/tot,
            "ICC_ind_conditional_day":vi/(vi+ve),"converged":bool(r.converged),
            "n_sessions":len(df),"n_individuals":int(df.individual.nunique()),"n_days":int(df.day.nunique())}

def rob(df,col,key,base):
    vals=[]
    for x in sorted(df[key].unique()):
        q=df[df[key]!=x].copy()
        if q.individual.nunique()<3 or q.day.nunique()<3:continue
        try: vals.append(fit(q,col)["frac_individual"])
        except Exception: pass
    if not vals:return None
    a=np.asarray(vals,float)
    return {"n":len(a),"min":float(a.min()),"median":float(np.median(a)),"max":float(a.max()),"full":base}

def run(year,panel):
    df,audit=prepared(panel)
    if df is None or len(df)<10:return {"status":"STOP_SUPPORT","audit":audit}
    fits={c:fit(df,c) for c in ["H","V"]}
    mean={k:float(np.mean([fits[c][k] for c in ["H","V"]])) for k in ["frac_individual","frac_day","frac_residual","ICC_ind_conditional_day"]}
    robustness={c:{"drop_individual":rob(df,c,"individual",fits[c]["frac_individual"]),
                   "drop_day":rob(df,c,"day",fits[c]["frac_individual"])} for c in ["H","V"]}
    return {"status":"DONE","n_sessions":len(df),"components":fits,"two_dimensional_summary":mean,"robustness":robustness}

def main():
    print(json.dumps({"contract":"FIELD_POLICY_VARIANCE_DECOMPOSITION_V1.md",
      "years":{y:run(y,p) for y,p in BV.PANELS.items()}},indent=2))
if __name__=="__main__":main()
