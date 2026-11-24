"""V17 bounded measured-force diagnostic after negative categorical V16.
Public source, no contact. Do not scan force columns or retune.
"""
import io,json,re,hashlib,zipfile
import numpy as np
import pandas as pd
from roost_fd_source_audit_v2 import OUT
from roost_fd_source_audit_v3 import quant
from roost_fd_source_audit_v4 import name
from roost_fd_empirical_null_v5 import numeric
from roost_fd_study_wing_v7 import study_wing
from roost_fd_independent_roost_v11 import download
from roost_fd_independent_roost_v12 import readcsv
from roost_fd_independent_roost_v15 import retrieve,wing_table,URL,HASH
from roost_fd_physical_regime_v16 import predict

PRIMARY="PeakPOS_100"
SECONDARY="ImpTOT_50"

def source():
    b,meta=download(URL,25_000_000)
    assert hashlib.sha256(b).hexdigest()==HASH
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        def member(end):
            a=[n for n in z.namelist() if not n.startswith("__MACOSX") and n.endswith(end)]
            assert len(a)==1
            return z.read(a[0])
        f=readcsv(member("Impulse_Ouputs_20230630_NO-Rnaso_SpecAvg.csv"))
        s=readcsv(member("Bat landing roosting data.csv"))
        texts=[]
        for end in ("Bat_Landing-Force_Analysis.R","Bat_Landing-Force_Analysis.Rmd"):
            texts.append(member(end).decode("utf-8",errors="replace"))
    audit={}
    for c in (PRIMARY,SECONDARY):
        # Verify the named endpoint in original analysis code, not a guessed column.
        refs=[l.strip()[:400] for code in texts for l in code.splitlines() if re.search(r"\b"+re.escape(c)+r"\b",l)]
        audit[c]={"column_present":c in f,"source_code_references":refs[:20],"verified":bool(c in f and refs)}
    assert len(s)==36 and len(f)==18
    s["species"]=s.Taxon.map(name)
    assert s.species.notna().all() and s.species.is_unique
    assert set(s.Landing_Regime)=={"high","low"}
    s["landing_low"]=(s.Landing_Regime=="low").astype(int)
    s["expected_points"]=pd.to_numeric(s.Landing_Style_Cont,errors="coerce")
    f["species"]=(f.Genus.astype(str).str.strip()+" "+f.Species.astype(str).str.strip()).map(name)
    f["force_points"]=pd.to_numeric(f.Points,errors="coerce")
    for c in (PRIMARY,SECONDARY):f[c]=numeric(f[c])
    counts=f.species.dropna().value_counts()
    duplicate=set(counts[counts>1].index)
    f=f[f.species.notna()&~f.species.isin(duplicate)].copy()
    j=f.merge(s[["species","landing_low","expected_points"]],on="species",how="left",validate="one_to_one")
    ok=j.expected_points.notna()&j.force_points.notna()&(j.force_points==j.expected_points)
    return j.loc[ok].copy(),{"supplement":meta,"force_table_rows":18,"exact_species_names":int(f.species.nunique()),
        "duplicate_species_excluded":len(duplicate),"style_match_rows":int(j.expected_points.notna().sum()),
        "points_agree_rows":int(ok.sum()),"endpoint_audit":audit}

def cv(d,outcome):
    y=np.log(d[outcome].to_numpy(float))
    d=d.copy()
    for a in ("mass","ar","wl"):d["log_"+a]=np.log(d[a])
    fam=d.wing_family.to_numpy();groups=sorted(set(fam))
    styles=d.landing_low.to_numpy()
    models={"M0":["log_mass","landing_low"],"M1":["log_mass","landing_low","log_ar"],
            "M2":["log_mass","landing_low","log_ar","log_wl"]}
    out={"n":len(d),"families":len(groups),"landing_counts":{str(k):int(v) for k,v in d.landing_low.value_counts().items()},
         "outcome_quantiles":quant(d[outcome]),"status":"insufficient_support"}
    if len(d)<12 or len(groups)<4 or min(int(styles.sum()),len(d)-int(styles.sum()))<5:return out
    for g in groups:
        tr=fam!=g
        if tr.sum()<8 or len(set(styles[tr]))<2:
            out["status"]="insufficient_training_fold";return out
    losses={};out["models"]={}
    for k,cols in models.items():
        X=d[cols].to_numpy(float);loss=[]
        for g in groups:
            te=fam==g;tr=~te
            yp=predict(X[tr],X[te],y[tr]);loss.append(float(np.mean((yp-y[te])**2)))
        losses[k]=np.array(loss)
        mu=X.mean(axis=0);sd=X.std(axis=0);sd=np.where(sd>1e-12,sd,1.)
        Z=(X-mu)/sd;beta=np.linalg.solve(Z.T@Z+np.eye(Z.shape[1]),Z.T@(y-y.mean()))
        out["models"][k]={"equal_family_RMSE_log_response":float(np.sqrt(losses[k].mean())),
            "full_sample_standardized_ridge_coefficients":dict(zip(cols,map(float,beta)))}
    for k in models:
        out["models"][k]["delta_RMSE_vs_M0"]=float(np.sqrt(losses[k].mean())-np.sqrt(losses["M0"].mean()))
        out["models"][k]["families_better_than_M0"]=int((losses[k]<losses["M0"]).sum())
    out["M2_minus_M1_RMSE"]=float(np.sqrt(losses["M2"].mean())-np.sqrt(losses["M1"].mean()))
    out["status"]="exploratory"
    return out

def main():
    report={"status":"started","claim_boundary":"Small source sample, direct force diagnostic; not causal mediation or community analysis."}
    dest=OUT/"audit_v17.json"
    def save():dest.write_text(json.dumps(report,indent=2,allow_nan=False))
    save()
    try:
        d,report["source_audit"]=source();save()
        if not report["source_audit"]["endpoint_audit"][PRIMARY]["verified"]:
            report["status"]="endpoint_review_required";save();print(dest.read_text());return 2
        raw=retrieve(report,save)
        if raw is None:raise ValueError("pinned wing file unavailable")
        t,_=wing_table(raw);w,_=study_wing(raw,"direct_or_formula")
        w["species"]=w["scientificName.iucn"].map(name);assert w.species.is_unique
        t=t.merge(w[["species","wingLoading_Nm2"]],on="species",validate="one_to_one").rename(columns={"wingLoading_Nm2":"wl"})
        j=d.merge(t,on="species",how="left",validate="one_to_one")
        complete=j.dropna(subset=["ar","wl","mass","wing_family",PRIMARY]).copy()
        report["coverage"]={"eligible_force_rows":len(d),"AR_matches":int(j.ar.notna().sum()),
          "complete_primary":len(complete),"complete_families":int(complete.wing_family.nunique())}
        report["primary"]=cv(complete,PRIMARY)
        if report["source_audit"]["endpoint_audit"][SECONDARY]["verified"] and complete[SECONDARY].notna().all():
            report["secondary"]=cv(complete,SECONDARY)
        else:report["secondary"]={"status":"not_verified_or_incomplete_on_primary_roster"}
        report["status"]="completed_diagnostic"
    except Exception as e:report["status"]="blocked";report["error"]=type(e).__name__+": "+str(e)[:200]
    save();print(dest.read_text())
    return 0 if report["status"]=="completed_diagnostic" else 2
if __name__=="__main__":raise SystemExit(main())
