"""V7 post-V6 wing-source repair using study-level direct and formula-derived traits.
No site-level data exported. Formula uses mass in g, wing area in cm2, span in cm.
Equal reference-study weighting, not pooled individual means; no imputation.
"""
import json
import numpy as np
import pandas as pd
from roost_fd_source_audit_v2 import get,OUT
from roost_fd_source_audit_v3 import quant
from roost_fd_source_audit_v4 import wing,name
from roost_fd_empirical_null_v5 import prepare,null_groups,numeric,SEED
from roost_fd_wing_qc_v6 import compact

AXES=[("flight",["logar","logwl"],[]),("resource",["logmass","diet"],["diet"]),("AR_only",["logar"],[]),("WL_only",["logwl"],[])]
def study_wing(raw,mode):
    s=pd.DataFrame({"species":raw["scientificName.iucn"].map(name),"ref":raw["refID"],
      "ar_direct":numeric(raw["aspectRatio"]),"wl_direct":numeric(raw["wingLoading_Nm2"]),
      "mass":numeric(raw["mass_g"]),"area":numeric(raw["wingArea_cm2"]),"span":numeric(raw["wingSpan_cm"])})
    s["wl_formula"]=98.0665*s.mass/s.area
    s["ar_formula"]=s.span**2/s.area
    for f in ["wl_direct","wl_formula"]:s.loc[~s[f].between(1,100),f]=np.nan
    for f in ["ar_direct","ar_formula"]:s.loc[~s[f].between(2,20),f]=np.nan
    s["ar"]=s.ar_direct if mode=="direct_only" else s.ar_direct.fillna(s.ar_formula)
    s["wl"]=s.wl_direct if mode=="direct_only" else s.wl_direct.fillna(s.wl_formula)
    s=s.dropna(subset=["species","ref"])
    # Repeated rows within a reference receive equal within-reference weight; references equal between species.
    m=s.groupby(["species","ref"],sort=True)[["ar","wl"]].median()
    t=m.groupby(level=0).median()
    counts=m.groupby(level=0).count()
    w=t.rename(columns={"ar":"aspectRatio","wl":"wingLoading_Nm2"}).reset_index().rename(columns={"species":"scientificName.iucn"})
    w["n.AR"]=w["scientificName.iucn"].map(counts.ar)
    w["n.WL"]=w["scientificName.iucn"].map(counts.wl)
    qc={"mode":mode,"rows_valid_name_ref":len(s),"species_total":len(w),
        "direct_AR_rows":int(s.ar_direct.notna().sum()),"direct_WL_rows":int(s.wl_direct.notna().sum()),
        "formula_AR_available_rows":int(s.ar_formula.notna().sum()),"formula_WL_available_rows":int(s.wl_formula.notna().sum()),
        "formula_fill_AR_rows":int((s.ar_direct.isna()&s.ar.notna()).sum()),
        "formula_fill_WL_rows":int((s.wl_direct.isna()&s.wl.notna()).sum()),
        "complete_species":int(w[["aspectRatio","wingLoading_Nm2"]].notna().all(axis=1).sum()),
        "AR":quant(w.aspectRatio),"WL":quant(w.wingLoading_Nm2),
        "reported_to_formula_WL":quant(s.wl_direct/s.wl_formula),
        "reported_to_formula_AR":quant(s.ar_direct/s.ar_formula),
        "area_definition_labels":{str(k):int(v) for k,v in raw["areaDefinition"].fillna("missing").value_counts().items()},
        "note":"Plausibility bounds 1-100 N/m2 and AR 2-20 fixed before output as diagnostic; no empirical proof of hard biological limits. Reported valid values take precedence. Formula-based values are derived from same source row, not imputed. Study-weighted medians differ from pooled original estimand."}
    return w,qc
def main():
    o,_=get("occ");l,_=get("land");t,_=get("traits");data,meta=wing()
    raw=data["wingReview_wm_data_final.csv"]
    result={"status":"posthoc_study_level_diagnostic","wing_sources":meta,"modes":{}}
    for mode in ("direct_only","direct_or_formula"):
        w,qc=study_wing(raw,mode);runs={}
        for repair in (False,True):
            x,tr,audit=prepare(o,l,t,w,repair)
            rr={"audit":audit,"paired_realm":compact(null_groups(x,tr,AXES,"realm",.8))}
            if repair:
                rr["frequency_weighted"]=compact(null_groups(x,tr,AXES,"realm",.8,weighted=True))
                rr["country"]=compact(null_groups(x,tr,AXES,"country",.8))
                rr["complete"]=compact(null_groups(x,tr,AXES,"realm",1.))
            runs["repair" if repair else "strict"]=rr
        result["modes"][mode]={"qc":qc,"runs":runs}
    (OUT/"audit_v7.json").write_text(json.dumps(result,indent=2,allow_nan=False))
    print(json.dumps(result,indent=2,allow_nan=False))
if __name__=="__main__":main()
