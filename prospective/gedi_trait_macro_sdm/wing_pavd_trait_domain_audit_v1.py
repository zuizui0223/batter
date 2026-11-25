"""Frozen-coefficient trait domain and measurement-source sensitivity.
No ecological response data, re-fitting, tuning, species exclusion or new prediction admission.
Use exact 280-species LSA table, its row lineage, and already frozen European model.
The predicted score is the relative coefficient for one training-SD change in lower PAVD
fraction, with all other environment coordinates fixed; it is not actual altitude,
habitat suitability, occupancy, or an independently validated global species ranking.
"""
import hashlib,json,pathlib
import numpy as np,pandas as pd
from scipy.spatial import ConvexHull
from scipy.stats import spearmanr
O=pathlib.Path("wing_trait_domain");O.mkdir(exist_ok=True)
N="scientificName.iucn"
TRAITS=["AR","log_WL","log_mass"]
MODEL="3e282cdcf4d21bf41234f1cae0e2ef71a3359269c68d592742c10101ac1feb97"
PINS={"traits":("wing/primary_LSA_physical.csv","99a19c169e18a0bafa4a518b7f844b56d2fe846cac13d5c035f4eae562a74c7b"),"lineage":("wing/source_row_lineage.csv","681e6f1b92f163cfa789632b6136b3892468a800076f2c171e76fcbdc533f5ca"),"model":("frozen/frozen_model.json",MODEL)}
R={"stage":"frozen model physical trait coverage and source reference sensitivity","status":"START","new_fit":False,"inputs":PINS,"limits":["Trait-space overlap is not environmental overlap or external validation.","Relative profile response at training standardization is a model-derived score, not actual species occupancy, preference or altitude.","Reference groups are not verified independent biological samples. Leave-one-reference ranges are sensitivity, not confidence intervals; one-reference species have no measurable between-source sensitivity.","Convex hull of 14 training taxa is a conservative interpolation check only; absence from hull does not prove prediction failure.","No response outcome, test label, or fitted coefficient changed."]}
def sha(p):
    with pathlib.Path(p).open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def save():
    (O/"report.json").write_text(json.dumps(R,indent=2,allow_nan=False)+"\n")
    print("WING_DOMAIN_REPORT="+json.dumps(R,allow_nan=False),flush=True)
def truth(s):
    v=s.astype(str).str.lower();assert v.isin(["true","false"]).all()
    return v.eq("true")
def main():
    for p,h in PINS.values():assert sha(p)==h,p
    m=json.loads(pathlib.Path(PINS["model"][0]).read_text())
    tr=m["train_names"];assert len(tr)==14 and len(set(tr))==14 and m["traits"]==TRAITS and m["environment"][-1]=="PAVD_lower_fraction"
    d=pd.read_csv(PINS["traits"][0]).set_index(N)
    assert d.index.is_unique and len(d)==280
    V=["AR","WL_N_m2","mass_g_physical"]
    q=pd.read_csv(PINS["lineage"][0],dtype={"refID":str},keep_default_na=False)
    assert len(q)==404 and q.areaDefinition.eq("LSA").all()
    ok=~truth(q.aspectRatio_conflict)&~truth(q.wingLoading_Nm2_conflict)
    q=q[ok].copy();assert len(q)==399
    q["mass_g_physical"]=pd.to_numeric(q.mass_g,errors="raise")
    q[V]=q[V].apply(pd.to_numeric,errors="raise")
    assert np.isfinite(q[V]).all().all() and q[V].gt(0).all().all()
    ref=q.groupby([N,"refID"])[V].median()
    rec=ref.groupby(level=0)[V].median().reindex(d.index)
    assert np.allclose(rec,d[V],rtol=1e-10,atol=1e-12)
    assert np.array_equal(ref.groupby(level=0).size().reindex(d.index),d.reference_count)
    d["log_WL"]=np.log(d.WL_N_m2);d["log_mass"]=np.log(d.mass_g_physical)
    s=m["stats"];X=d[TRAITS].to_numpy(float)
    center=d.loc[tr,TRAITS].mean().to_numpy(float);sd=np.asarray(s["trait_sd"])
    assert np.allclose(d.loc[tr,TRAITS].std(ddof=0).to_numpy(float),sd,rtol=1e-10)
    Z=(X-center)/sd
    Ztr=(d.loc[tr,TRAITS].to_numpy(float)-center)/sd
    hull=ConvexHull(Ztr)
    inside=(Z@hull.equations[:,:-1].T+hull.equations[:,-1]<=1e-9).all(1)
    assert int(inside[d.index.isin(tr)].sum())==14
    marginal=((X>=np.asarray(s["trait_min"])-1e-10)&(X<=np.asarray(s["trait_max"])+1e-10)).all(1)
    beta=np.asarray(m["coefficients"]["W_M"]).reshape(3,len(m["environment"]))[:,-1]
    assert np.allclose(beta,[-.021592995501431844,-.012238828382874947,.03706438176940525],rtol=1e-12)
    bAR=m["coefficients"]["AR_M"][-1]
    d["relative_profile_score"]=Z@beta
    d["AR_only_relative_profile_score"]=Z[:,0]*bAR
    d["within_all_marginal_ranges"]=marginal
    d["within_training_convex_hull"]=inside
    d["training_species"]=d.index.isin(tr)
    d["reference_loo_min"]=np.nan;d["reference_loo_max"]=np.nan
    for name,v in ref.groupby(level=0):
        if len(v)<2:continue
        x=v[V].to_numpy(float)
        loo=[]
        for j in range(len(x)):
            a=np.median(np.delete(x,j,axis=0),axis=0)
            a[1:]=np.log(a[1:])
            loo.append(float(((a-center)/sd)@beta))
        d.loc[name,["reference_loo_min","reference_loo_max"]]=[min(loo),max(loo)]
    d["reference_loo_range"]=d.reference_loo_max-d.reference_loo_min
    d["reference_loo_crosses_training_mean"]=(d.reference_loo_min<=0)&(d.reference_loo_max>=0)
    p=pathlib.Path("support/report.json")
    sup=json.loads(p.read_text());assert sup["status"]=="WING_SUPPORT_AUDIT_COMPLETE_NO_FIT" and sup["fws"]["matched_species"]==8
    fws=sup["fws"]["matched_names"];assert len(set(fws))==8 and set(fws)<=set(d.index) and not set(fws)&set(tr)
    def summarize(names):
        v=d.loc[names];multi=v.reference_count.gt(1)
        vals=v.loc[multi,"reference_loo_range"]
        cor=spearmanr(v.relative_profile_score,v.AR_only_relative_profile_score).statistic
        return {"species":len(v),"within_all_marginal_ranges":int(v.within_all_marginal_ranges.sum()),"within_training_convex_hull":int(v.within_training_convex_hull.sum()),"one_reference":int((~multi).sum()),"multiple_reference":int(multi.sum()),"multi_reference_relative_score_crosses_zero":int(v.loc[multi,"reference_loo_crosses_training_mean"].sum()),"median_loo_range":float(vals.median()) if len(vals) else None,"rank_correlation_W_vs_AR":float(cor) if np.isfinite(cor) else None}
    R["global_280"]=summarize(d.index);R["europe_14"]=summarize(tr);R["FWS_8_pre_environment"]=summarize(fws)
    R["trait_correlation_training"]=dict(zip(TRAITS,[dict(zip(TRAITS,map(float,row))) for row in np.corrcoef(Ztr,rowvar=False)]))
    R["FWS_rows"]=json.loads(d.loc[fws,V+["reference_count","relative_profile_score","AR_only_relative_profile_score","within_all_marginal_ranges","within_training_convex_hull","reference_loo_min","reference_loo_max"]].reset_index().to_json(orient="records"))
    p=O/"frozen_trait_domain.csv";d.reset_index().to_csv(p,index=False)
    R["output_sha256"]=sha(p);R["status"]="TRAIT_DOMAIN_AUDIT_COMPLETE_NO_ECOLOGICAL_VALIDATION";save()
if __name__=="__main__":
    try:main()
    except Exception as e:R.update(status="INCOMPLETE",error_type=type(e).__name__,error=str(e)[:200]);save();raise
