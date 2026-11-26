"""Post-result cross-source descriptive check only. No prediction validation or model tuning.
Compare the existing fixed European wing-profile rank with separately estimated Polesia
regularized PAVD site-use and detection slopes, exact single-species labels only.
"""
import hashlib,json,pathlib,itertools
import numpy as np,pandas as pd
from scipy.stats import spearmanr,kendalltau
O=pathlib.Path("polesia_wing_rank");O.mkdir(exist_ok=True)
F=pathlib.Path("prospective/gedi_trait_macro_sdm/POLESIA_OCCUPANCY_DETECTION_RECEIPT_V1.json")
T=pathlib.Path("domain/frozen_trait_domain.csv")
R={"stage":"post-result frozen wing rank vs Polesia regularized site-use/detection slopes","status":"START","new_fit":False,"limits":["Polesia ecological coefficients were inspected before this descriptive comparison. Not an unopened confirmation.","Polesia full models did not outperform intercept-only; regularized coefficients have uncertain identification and no slope uncertainty estimates in the receipt.","Same species can occur in European training; exact species labels only, complexes excluded. No phylogenetic independence assumed.","Different estimands: conditional relative recorded-label response vs conditional site use and detection. Compare ordinal ranks only, not coefficient magnitudes.","Do not choose, reweight, or refit the previously tested external model from this comparison."]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save():
    s=json.dumps(R,allow_nan=False,default=lambda v:v.item() if isinstance(v,np.generic) else v.tolist() if isinstance(v,np.ndarray) else None)
    (O/"report.json").write_text(s+"\n");print("POLESIA_WING_REPORT="+s,flush=True)
def rank(x,y):
    a=float(spearmanr(x,y).statistic);b=float(kendalltau(x,y).statistic)
    if not np.isfinite(a) or not np.isfinite(b):return {"status":"UNDEFINED_CONSTANT_RANK"}
    loo=[float(spearmanr(np.delete(x,i),np.delete(y,i)).statistic) for i in range(len(x))] if len(x)>=4 else []
    loo=[x for x in loo if np.isfinite(x)]
    return {"spearman":a,"kendall":b,"leave_one_species_spearman_range":[min(loo),max(loo)] if loo else None,"n":len(x)}
def main():
    assert sha(T)=="6d9ba6bbada4e103606f09f15f25fab9cde13e26c2a15d6e3366fa48808f9f06"
    blob=hashlib.sha1(("blob "+str(F.stat().st_size)+"\0").encode()+F.read_bytes()).hexdigest()
    assert blob=="c40c7d67dc238b2b838c063b8b763f7eafa76693"
    f=json.loads(F.read_text());assert f["status"]=="COMPLETE_DESCRIPTIVE_ONLY"
    assert (f["support"]["sites"],f["support"]["nights"],f["support"]["labels"])==(124,733,8)
    d=pd.DataFrame(f["joint_full_data_regularized_coefficients"],columns=f["coefficient_columns"])
    d["species"]=d.acoustic_label.map(lambda x:x.replace("_"," ").capitalize() if len(x.split("_"))==2 else "")
    t=pd.read_csv(T).rename(columns={"scientificName.iucn":"species"})
    assert len(t)==280 and t.species.is_unique
    cols=["species","AR","WL_N_m2","mass_g_physical","reference_count","relative_profile_score","AR_only_relative_profile_score","within_training_convex_hull","training_species"]
    a=d.merge(t[cols],on="species",how="left",validate="one_to_one")
    R["unmatched_or_complex_labels"]=a.loc[a.relative_profile_score.isna(),"acoustic_label"].tolist()
    a=a[a.relative_profile_score.notna()].copy()
    for col in ["training_species","within_training_convex_hull"]:
        val=a[col].astype(str).str.lower()
        assert val.isin(["true","false"]).all()
        a[col]=val.eq("true")
    ntrain=int(a.training_species.sum())
    R["support"]={"matched_single_species":len(a),"training_species":ntrain,"unseen_species":len(a)-ntrain,"in_training_hull":int(a.within_training_convex_hull.sum()),"single_reference":int(a.reference_count.eq(1).sum())}
    assert 0<=R["support"]["unseen_species"]<=len(a)
    R["rows"]=json.loads(a.to_json(orient="records"))
    R["ranks"]={}
    if len(a)<5:R["status"]="STOP_TOO_FEW_MATCHED_SPECIES";save();return
    for n,x in [("frozen_W",a.relative_profile_score),("frozen_AR",a.AR_only_relative_profile_score)]:
        R["ranks"][n]={k:rank(x.to_numpy(),a[k].to_numpy()) for k in ["site_use_PAVD","conditional_detection_PAVD"]}
    # Record the two full-data slopes' association as an identifiability caveat.
    R["site_use_vs_detection_rank"]=rank(a.site_use_PAVD.to_numpy(),a.conditional_detection_PAVD.to_numpy())
    R["unseen_only_status"]="INSUFFICIENT_FOR_INDEPENDENT_RANK_VALIDATION" if R["support"]["unseen_species"]<5 else "DESCRIPTIVE_ONLY"
    R["source_receipt_sha256"]=sha(F);R["status"]="COMPLETE_DESCRIPTIVE_ONLY";save()
if __name__=="__main__":
    try:main()
    except Exception as e:R.update(status="INCOMPLETE",error_type=type(e).__name__,error=str(e)[:180]);save();raise
