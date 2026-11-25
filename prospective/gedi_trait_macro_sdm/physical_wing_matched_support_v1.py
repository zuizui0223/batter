"""Source-only wing trait admission audit; no ecological response fit.
Frozen LSA table, exact names and original geographic criteria. No trait imputation,
synonym guessing, or relaxed original SDM admission.
"""
import hashlib,json,pathlib
import numpy as np,pandas as pd
O=pathlib.Path("wing_matched_support");O.mkdir(exist_ok=True)
P={
 "traits":(pathlib.Path("wing/primary_LSA_physical.csv"),"99a19c169e18a0bafa4a518b7f844b56d2fe846cac13d5c035f4eae562a74c7b"),
 "europe":(pathlib.Path("fixed/all_bat_species_cell_source_year_environment.csv.gz"),"85ad737229aa7b10720a8d5c8bd0ea389f63f908c37871c7ce46ae87c9bed1d6"),
 "flags":(pathlib.Path("observation/source_cell_year_observation_flags.csv.gz"),"de971292065a8aee3491880adb00a5623efae61bc83b2bd2ae4d663b45edf0f0")}
R={"stage":"fixed physical wing trait matched support, no ecological fit","status":"START","original_SDM_admitted":False,"limits":["Exact-name match only; shared names do not establish independently measured traits or taxonomic equivalence.","FWS report is pre-environment support at 6 km; not admitted final forest comparison.","European coverage uses frozen 1-km forest/latitude masks, not measured PAVD or complete effort support.","No new model or inference of wing-trait effects."]}
def save():
    def scalar(x):
        if isinstance(x,np.generic):return x.item()
        raise TypeError(type(x).__name__)
    (O/"report.json").write_text(json.dumps(R,indent=2,allow_nan=False,default=scalar))
    print("WING_SUPPORT_REPORT="+json.dumps(R,allow_nan=False,default=scalar),flush=True)
def sha(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def boolean(v):
    return v.astype(str).str.lower().eq("true")
def main():
    for p,h in P.values():assert sha(p)==h,str(p)
    R["input_sha256"]={k:h for k,(p,h) in P.items()}
    t=pd.read_csv(P["traits"][0]).rename(columns={"scientificName.iucn":"species"})
    V=["AR","WL_N_m2","mass_g_physical"]
    assert len(t)==280 and not t.species.duplicated().any() and np.isfinite(t[V]).all().all() and t[V].gt(0).all().all()
    t=t.set_index("species")
    a=pd.read_csv(P["europe"][0],dtype={"species":str,"snapshot_species_key":str,"dataset_key":str,"year":str,"license":str},keep_default_na=False,low_memory=False)
    f=pd.read_csv(P["flags"][0],dtype={"species":str,"snapshot_species_key":str,"dataset_key":str,"year":str,"license":str},keep_default_na=False,low_memory=False)
    K=["species","snapshot_species_key","cell_x","cell_y","dataset_key","year","license"]
    assert a.records.sum()==219960 and f.records.sum()==219960
    assert not a.duplicated(K).any() and not f.duplicated(K).any()
    f=f[K+["records","flag_explicit_captive","flag_roost_context"]].rename(columns={"records":"flag_records"})
    a=a.merge(f,on=K,validate="one_to_one");assert a.records.eq(a.flag_records).all() and a.records.sum()==219960
    assert a.flag_explicit_captive.sum()==0 and a.flag_roost_context.sum()==684
    a["usable_records"]=a.records-a.flag_roost_context
    assert a.usable_records.ge(0).all()
    names=a.groupby("species").snapshot_species_key.nunique()
    a["exact_match"]=a.species.isin(t.index)&a.species.isin(names[names.eq(1)].index)
    def cov(mask):
        q=a[mask&a.exact_match&a.usable_records.gt(0)]
        v=q[["species","cell_x","cell_y"]].drop_duplicates()
        z=[]
        for name,g in v.groupby("species",sort=True):
            n=len(g);nb=int(g.groupby([g.cell_x//200,g.cell_y//200]).size().ge(5).sum())
            z.append({"species":name,"cells":n,"blocks_ge5":nb,"pass":bool(n>=30 and nb>=4),"trait_references":int(t.loc[name,"reference_count"])})
        passed=[x["species"] for x in z if x["pass"]]
        return {"records":int(q.usable_records.sum()),"species_cells":len(v),"species":len(z),"geographic_pass_species":len(passed),"passing_names":passed,"support":z}
    R["europe"]={
      "all_observations":cov(pd.Series(True,index=a.index)),
      "all_forest":cov(boolean(a.forest_profile_support)),
      "training_latitude_forest":cov(boolean(a.forest_profile_support)&boolean(a.training_latitude_support)),
      "northern_forest":cov(boolean(a.forest_profile_support)&boolean(a.north_extrapolation))}
    R["europe"]["snapshot_names"]=int(a.species.nunique())
    R["europe"]["exact_trait_names"]=int(a.loc[a.exact_match,"species"].nunique())
    p=pathlib.Path("fws/report.json");d=json.loads(p.read_text())
    s=d["pre_environment_comparison_support"]
    assert d["status"]=="PRE_ENVIRONMENT_GATE_PASS" and s["comparisons"]==10480 and s["eligible_taxa"]==9
    roster=sorted(x["species"] for x in s["taxon_support"] if x["eligible"])
    found=sorted(set(roster)&set(t.index))
    R["fws"]={"original_eligible_names":roster,"matched_names":found,"matched_species":len(found),"missing":sorted(set(roster)-set(found)),"max_training_taxa_if_two_unknown_species":len(found)-2,"original_cold_start_min_training_taxa":8,"source_report_sha256":sha(p),"trait_values":t.loc[found,V+["reference_count"]].reset_index().to_dict("records")}
    # Descriptive trait-domain coverage. No fit or score, no implied ecological equivalence.
    e=R["europe"]["training_latitude_forest"]["passing_names"]
    def range_summary(names):
        v=t.loc[names,V]
        return {k:{"min":float(v[k].min()),"median":float(v[k].median()),"max":float(v[k].max())} for k in V} if len(names) else {}
    R["trait_domain"]={"europe_training_latitude_pass":range_summary(e),"fws_pre_environment_matched":range_summary(found),"FWS_within_Europe_marginal_ranges":{k:int(t.loc[found,k].between(t.loc[e,k].min(),t.loc[e,k].max()).sum()) for k in V} if len(e) else {}}
    R["status"]="WING_SUPPORT_AUDIT_COMPLETE_NO_FIT";save()
if __name__=="__main__":
    try:main()
    except Exception as e:R.update(status="INCOMPLETE",error_type=type(e).__name__,error=str(e)[:220]);save();raise
