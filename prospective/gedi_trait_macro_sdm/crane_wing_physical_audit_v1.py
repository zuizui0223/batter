"""Source-only QA of Crane et al. 2020 deposited version 4309199.
No imputation, no fitted ecological response, no post-outcome taxonomic merges.
"""
import pathlib,hashlib,json,math,collections
import numpy as np,pandas as pd
OUT=pathlib.Path("crane_physical_audit");OUT.mkdir(exist_ok=True)
SRC=pathlib.Path("crane/original_tables")
PINS={
"wingReview_wm_data_raw.csv":"f1d0f91bdc71e75de77ebaed50fc7263d93a08a3a4bcde37bc924ed569f52eff",
"wingReview_wm_data_final.csv":"60666f4892dfe536534ad953bc1810b93ded33ce454373ec1e1b410a97ba2c97",
"wingReview_wm_data_speciesLevel.csv":"26d06fa7b64b00756259d010d098232d98b40a3e899d62afc9d63ac6815d9fea",
"wingReview_metadata.csv":"5a47b44432d9f452b7c5c1ca20204b947f5d6630a67db423a9b9362458145e1a",
"wingReview_method_data.csv":"2f3b9ed80f9ea2720f10a70ba0eaa508f1a074611de13a8c5bd2debe4d1479ed",
"wingReview_spp_correction.csv":"9535f81b91a03f3399c446f8458989a65cb3d4e4cfef8863836008b893133c57"}
N="scientificName.iucn"
FWS=["Corynorhinus rafinesquii","Eptesicus fuscus","Lasiurus borealis","Lasiurus cinereus","Myotis austroriparius","Myotis grisescens","Myotis leibii","Myotis lucifugus","Myotis septentrionalis","Myotis sodalis","Nycticeius humeralis","Perimyotis subflavus"]
GBIF=["Lasionycteris noctivagans","Lasiurus borealis","Nycticeius humeralis","Parastrellus hesperus","Tadarida brasiliensis","Artibeus jamaicensis","Eptesicus fuscus","Aeorestes cinereus","Antrozous pallidus"]
R={"stage":"original wing source physical-unit and exact-name coverage audit only","source_doi":"10.5281/zenodo.4309199","source_sha256":PINS,"status":"START","tables":{},"limits":["Do not treat compiled measurements as independent individuals or studies.","Source standard area definition must be verified from metadata; no cross-definition pooling.","Reported and recomputed traits remain separate. No silent correction, proxy substitution or imputation.","Same-row physical identities are approximate for published means; ratio of means differs from mean of ratios.","Exact scientific names only; synonyms not merged, including Aeorestes/Lasiurus.","No acoustic traits or actual ecological fit in this source."]}
def save():
    (OUT/"report.json").write_text(json.dumps(R,indent=2,allow_nan=False))
    print("CRANE_PHYSICAL_REPORT="+json.dumps(R,allow_nan=False),flush=True)
def sha(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def read(name):
    hit=list(SRC.glob("*_"+name));assert len(hit)==1,(name,len(hit))
    p=hit[0];assert sha(p)==PINS[name],name
    import io
    raw=p.read_bytes()
    # Preserve original byte hash and avoid replacement characters. Legacy
    # European author strings may be encoded Windows-1252/ISO-8859-1.
    for encoding in ("utf-8-sig","cp1252","iso-8859-1"):
        try:decoded=raw.decode(encoding,errors="strict");break
        except UnicodeDecodeError:continue
    R.setdefault("source_text_decoding",{})[name]=encoding
    return pd.read_csv(io.StringIO(decoded),dtype=str,keep_default_na=False)
def num(x):
    v=pd.to_numeric(x,errors="coerce")
    return v.where(np.isfinite(v)&v.gt(0))
def summary(d):
    n=len(d)
    a={k:num(d[k]) for k in ["mass_g","wingSpan_cm","wingArea_cm2","aspectRatio","wingLoading_Nm2"]}
    calc_ar=a["wingSpan_cm"]**2/a["wingArea_cm2"]
    calc_wl=98.1*a["mass_g"]/a["wingArea_cm2"]
    z={"rows":n,"distinct_species":int(d[N].nunique()),"numeric_positive":{k:int(v.notna().sum()) for k,v in a.items()},"direct_complete_AR_WL_mass":int(pd.concat([a[k] for k in ["aspectRatio","wingLoading_Nm2","mass_g"]],axis=1).notna().all(1).sum()),"recomputable_AR_rows":int(calc_ar.notna().sum()),"recomputable_WL_rows":int(calc_wl.notna().sum())}
    for k,v,w in [("AR",a["aspectRatio"],calc_ar),("WL",a["wingLoading_Nm2"],calc_wl)]:
        rat=(v/w).dropna();rat=rat[np.isfinite(rat)&rat.gt(0)]
        z[k+"_reported_vs_physical"]={"paired_rows":len(rat),"ratio_quantiles":np.quantile(rat,[0,.05,.5,.95,1]).tolist() if len(rat) else [],"within_20pct":int(rat.between(.8,1.2).sum()),"outside_factor_2":int((~rat.between(.5,2)).sum()),"below_factor_100":int(rat.lt(.01).sum()),"above_factor_100":int(rat.gt(100).sum())}
    z["WL_reported_below_0_1_N_m2"]=int(a["wingLoading_Nm2"].lt(.1).sum())
    if "WL_calc" in d:
        w=num(d.WL_calc);rat=(w/calc_wl).dropna()
        z["published_WL_calc_vs_SI_identity"]={"rows":len(rat),"ratio_quantiles":np.quantile(rat,[0,.05,.5,.95,1]).tolist() if len(rat) else [],"within_20pct":int(rat.between(.8,1.2).sum())}
    return z
def candidate_support(d,roster):
    ans=[]
    for sp in roster:
        v=d[d[N].eq(sp)]
        m=num(v.mass_g);ws=num(v.wingSpan_cm);wa=num(v.wingArea_cm2);ar=num(v.aspectRatio);wl=num(v.wingLoading_Nm2)
        ar_phys=ws**2/wa;wl_phys=98.1*m/wa
        direct=ar.notna()&wl.notna()&m.notna()
        physical=ar_phys.notna()&wl_phys.notna()
        # "stand" is a source-coded area class. Its semantic status is kept
        # explicit; no assumption other area definitions are equivalent.
        standard=v.areaDefinition.str.strip().str.casefold().eq("stand") if "areaDefinition" in v else pd.Series(False,index=v.index)
        row={"species":sp,"raw_rows":len(v),"references":int(v.refID.nunique()) if "refID" in v else None,"rows_direct_AR_WL_mass":int(direct.sum()),"rows_recomputable_AR_WL_mass":int(physical.sum()),"stand_rows_recomputable_AR_WL_mass":int((physical&standard).sum()),"area_codes":sorted(set(v.areaDefinition)) if "areaDefinition" in v else []}
        ans.append(row)
    return {"roster_species":len(roster),"exact_name_matches":sum(v["raw_rows"]>0 for v in ans),"direct_complete_species":sum(v["rows_direct_AR_WL_mass"]>0 for v in ans),"recomputable_complete_species":sum(v["rows_recomputable_AR_WL_mass"]>0 for v in ans),"stand_recomputable_complete_species":sum(v["stand_rows_recomputable_AR_WL_mass"]>0 for v in ans),"species":ans}
def main():
    raw=read("wingReview_wm_data_raw.csv");final=read("wingReview_wm_data_final.csv");pool=read("wingReview_wm_data_speciesLevel.csv");meta=read("wingReview_metadata.csv");methods=read("wingReview_method_data.csv");syn=read("wingReview_spp_correction.csv")
    assert (len(raw),len(final),len(pool))==(968,932,434)
    assert not pool[N].duplicated().any()
    fields=meta[meta.fieldTitle.str.contains("areaDefinition|wingLoading|wingArea|wingSpan|aspectRatio|mass_g|WL_calc|AR_calc|RWL_calc",case=False,regex=True)].to_dict("records")
    R["published_field_definitions"]=fields
    R["area_definition_counts"]={"raw":raw.areaDefinition.value_counts(dropna=False).to_dict(),"final":final.areaDefinition.value_counts(dropna=False).to_dict()}
    R["study_count_raw"]=int(raw.refID.nunique());R["methods_rows"]=len(methods);R["source_synonym_table_rows"]=len(syn)
    for k,d in [("raw",raw),("final",final),("pooled",pool)]:
        R["tables"][k]=summary(d)
    R["raw_by_area_definition"]={str(k):summary(v) for k,v in raw.groupby("areaDefinition",dropna=False)}
    R["regional_exact_name_coverage"]={"FWS_12":candidate_support(raw,FWS),"GBIF_9":candidate_support(raw,GBIF)}
    R["status"]="PHYSICAL_QA_COMPLETE_NO_MODEL_ADMISSION";save()
if __name__=="__main__":
    try:main()
    except Exception as e:R.update(status="INCOMPLETE",error=type(e).__name__+": "+str(e)[:180]);save();raise
