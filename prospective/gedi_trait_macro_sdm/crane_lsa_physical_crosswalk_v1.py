"""Frozen source-only reconstruction. See CRANE_LSA_PHYSICAL_CROSSWALK_CONTRACT_V1.md."""
import hashlib,json,pathlib,io,math,re
import numpy as np,pandas as pd
OUT=pathlib.Path("crane_lsa_crosswalk");OUT.mkdir(exist_ok=True)
SRC=pathlib.Path("crane/original_tables")
RAW="f1d0f91bdc71e75de77ebaed50fc7263d93a08a3a4bcde37bc924ed569f52eff"
META="5a47b44432d9f452b7c5c1ca20204b947f5d6630a67db423a9b9362458145e1a"
N="scientificName.iucn"
R={"stage":"explicit lifting-surface physical traits and exact-name geographic support only","source_doi":"10.5281/zenodo.4309199","status":"START","limits":["No imputation, no cross-definition pooling, no guessed synonym mapping or ecological fit.","Ratios of published source means are not individual-level measurements.","Study-reference equal weighting does not establish independent samples."]}
def sha(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def read(name,pin):
    q=list(SRC.glob("*_"+name));assert len(q)==1 and sha(q[0])==pin,name
    raw=q[0].read_bytes()
    for enc in ("utf-8-sig","cp1252","iso-8859-1"):
        try:s=raw.decode(enc);break
        except UnicodeDecodeError:pass
    R.setdefault("decoding",{})[name]=enc
    return pd.read_csv(io.StringIO(s),dtype=str,keep_default_na=False)
def positive(s):
    x=pd.to_numeric(s,errors="coerce")
    return x.where(np.isfinite(x)&x.gt(0))
def save():
    (OUT/"report.json").write_text(json.dumps(R,indent=2,allow_nan=False))
    print("CRANE_LSA_REPORT="+json.dumps(R,allow_nan=False),flush=True)
def agg(d):
    vars=["AR","WL_N_m2","mass_g_physical"]
    if d.empty:return pd.DataFrame(columns=[N,*vars,"reference_count","source_rows"])
    ref=d.groupby([N,"refID"],sort=True)[vars].median().reset_index()
    a=ref.groupby(N)[vars].median()
    a["reference_count"]=ref.groupby(N).size()
    a["source_rows"]=d.groupby(N).size()
    for k in vars:
        a[k+"_min_ref"]=ref.groupby(N)[k].min()
        a[k+"_max_ref"]=ref.groupby(N)[k].max()
    return a.reset_index()
def main():
    raw=read("wingReview_wm_data_raw.csv",RAW);meta=read("wingReview_metadata.csv",META)
    assert len(raw)==968 and raw[N].nunique()==464
    assert meta.loc[meta.fieldTitle.eq("areaDefinition"),"dataDesc"].str.contains("lifting surface area",case=False).any()
    d=raw.copy();d["source_row"]=np.arange(2,len(d)+2)
    for k in ["mass_g","wingSpan_cm","wingArea_cm2"]:
        d[k+"_positive"]=positive(d[k])
    d["mass_g_physical"]=d.mass_g_positive
    d["AR"]=d.wingSpan_cm_positive**2/d.wingArea_cm2_positive
    d["WL_N_m2"]=98.1*d.mass_g_positive/d.wingArea_cm2_positive
    is_missing=lambda s:s.str.strip().str.lower().isin(["","na","nan","n/a"])
    for k,calc in [("aspectRatio","AR"),("wingLoading_Nm2","WL_N_m2")]:
        present=~is_missing(d[k]);v=positive(d[k])
        d[k+"_valid_supplied"]=present&v.notna()
        d[k+"_ratio"]=v/d[calc]
        d[k+"_conflict"]=present&(~v.notna()|~d[k+"_ratio"].between(.8,1.2))
    masks=[
        ("explicit_LSA",d.areaDefinition.str.strip().eq("LSA")),
        ("exact_binomial_and_ref",d[N].str.fullmatch(r"[A-Z][a-z]+ [a-z][a-z]+")&d.refID.str.strip().ne("")),
        ("same_row_physical_primitives",d[["AR","WL_N_m2","mass_g_physical"]].notna().all(1)),
    ]
    m=pd.Series(True,index=d.index);flow=[]
    for k,v in masks:
        m&=v.fillna(False);flow.append({"stage":k,"rows":int(m.sum()),"species":int(d.loc[m,N].nunique())})
    physical=d[m].copy()
    no_conflict=~physical.aspectRatio_conflict&~physical.wingLoading_Nm2_conflict
    p=physical[no_conflict].copy()
    strict=p[p.aspectRatio_valid_supplied&p.wingLoading_Nm2_valid_supplied].copy()
    a=agg(p);c=agg(physical);z=agg(strict)
    for name,t in [("primary_LSA_physical",a),("all_explicit_LSA",c),("both_reported_agreement",z)]:
        q=OUT/(name+".csv");t.to_csv(q,index=False)
        R.setdefault("tables",{})[name]={"species":len(t),"references":int(t.reference_count.sum()),"source_rows":int(t.source_rows.sum()),"sha256":sha(q)}
    fields=["source_row",N,"refID","year","areaDefinition","methodMeasurement","sex","sampleSize","mass_g","wingSpan_cm","wingArea_cm2","aspectRatio","wingLoading_Nm2","AR","WL_N_m2","aspectRatio_ratio","wingLoading_Nm2_ratio","aspectRatio_conflict","wingLoading_Nm2_conflict"]
    q=OUT/"source_row_lineage.csv";physical[fields].to_csv(q,index=False)
    R["source_row_lineage_sha256"]=sha(q);R["attrition"]=flow
    R["excluded_disagreement_rows"]=int((~no_conflict).sum())
    names=set(a[N]);fws="Corynorhinus rafinesquii;Eptesicus fuscus;Lasiurus borealis;Lasiurus cinereus;Myotis austroriparius;Myotis grisescens;Myotis leibii;Myotis lucifugus;Myotis septentrionalis;Myotis sodalis;Nycticeius humeralis;Perimyotis subflavus".split(";")
    gbif="Lasionycteris noctivagans;Lasiurus borealis;Nycticeius humeralis;Parastrellus hesperus;Tadarida brasiliensis;Artibeus jamaicensis;Eptesicus fuscus;Aeorestes cinereus;Antrozous pallidus".split(";")
    def match(roster):return {"roster_species":len(roster),"matches":len(set(roster)&names),"missing":sorted(set(roster)-names)}
    R["exact_name_support"]={"FWS_12_candidates":match(fws),"North_American_GBIF_9_geographic":match(gbif)}
    for region,pin in [("North_America","81c900ad8f201cbbaa6bda3405f9346b930f7b71e3d3f61bcefb535fd3da41ba"),("East_Asia","37fa0656a310691eb3bec989043421afa9ed5630b117ca9311418c4cf52610c0")]:
        q=pathlib.Path("continental")/(region+"_species_coverage.json")
        assert sha(q)==pin
        v=json.loads(q.read_text())
        roster=[x["species_names"][0] for x in v if len(x["species_names"])==1]
        passing=[x["species_names"][0] for x in v if x["geographic_pass"] and len(x["species_names"])==1]
        R["exact_name_support"][region]={"all_single_name_taxa":match(roster),"pre_environment_geographic_pass":match(passing)}
    q=pathlib.Path("traits/physical_trait_crosswalk.csv")
    assert sha(q)=="43bb5284308a9fe732beda51886172cb87268e5d00620eb27956d5808dae809f"
    e=pd.read_csv(q,dtype=str,keep_default_na=False)
    e["prior_AR"]=positive(e.AR);e["prior_WL"]=positive(e.WL_N_m2)
    m=a.merge(e[["source_name","prior_AR","prior_WL"]],left_on=N,right_on="source_name",validate="one_to_one")
    def ratio(k,l):
        x=(m[k]/m[l]).dropna()
        return {"n":len(x),"quantiles":np.quantile(x,[0,.25,.5,.75,1]).tolist() if len(x) else [],"within_20pct":int(x.between(.8,1.2).sum())}
    R["between_compilation_audit"]={"exact_names":len(m),"AR_ratio":ratio("AR","prior_AR"),"WL_ratio":ratio("WL_N_m2","prior_WL"),"note":"Not independent measurement; previous source area definition and literature may differ."}
    R["status"]="LSA_PHYSICAL_CROSSWALK_READY_NO_ECOLOGICAL_FIT";save()
if __name__=="__main__":
    try:main()
    except Exception as e:
        R.update(status="INCOMPLETE",error_type=type(e).__name__,error=str(e)[:200]);save();raise
