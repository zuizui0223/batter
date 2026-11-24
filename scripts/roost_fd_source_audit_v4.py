"""V4: occurrence-defined assemblages; independent landscape join; selective measured-wing acquisition.
Only aggregate results, source schema and species-name diagnostics are printed. No cave-level output.
"""
import io,json,sys,re,hashlib,unicodedata
from decimal import Decimal,InvalidOperation
import numpy as np
import pandas as pd
from remotezip import RemoteZip
from roost_fd_source_audit_v2 import get,clean,S,OUT
from roost_fd_source_audit_v3 import label,series_label,quant
from roost_fd_source_audit_v1 import binomial

def name(v):
    s=label(v)
    if s is None:return None
    # Standardize spaces and case only, not synonyms, subspecies or spelling.
    s=s.replace("_"," ")
    s=" ".join(s.split())
    return s if re.fullmatch(r"[a-z]+ [a-z-]+",s) else None
def coordinate(v,lim):
    try:
        d=Decimal(str(v).strip().replace("\u2212","-"))
        if not d.is_finite() or abs(d)>lim:return None
        return str(d.normalize()) if d else "0"
    except (InvalidOperation,ValueError):return None
def cavekeys(df,occ):
    country=series_label(df["Country.record" if occ else "Country"])
    site=series_label(df["Cave.site" if occ else "Cave_Name"])
    lat=df["Lattitude" if occ else "Latitude"].map(lambda x:coordinate(x,90))
    lon=df["Longitude"].map(lambda x:coordinate(x,180))
    invalid={"cave","caves","unknown","unnamed","not known","n.a.","unidentified"}
    return pd.Series([tuple(v) if all(x is not None for x in v) and v[1] not in invalid else None
                       for v in zip(country,site,lat,lon)],index=df.index,dtype=object)
def source_taxa(o,t):
    oc=o["Species.name"].map(name);tc=t["Species.name"].map(name)
    dup=set(tc[tc.notna()&tc.duplicated(keep=False)])
    # A species with an unresolved name is counted in denominator, not silently replaced.
    raw=series_label(o["Species.name"])
    tax=oc.fillna(raw.map(lambda x:"unresolved:"+x if x else None))
    audit={"occ_valid_binomial_rows":int(oc.notna().sum()),"trait_valid_binomial_rows":int(tc.notna().sum()),
           "occ_unique_species":int(oc.nunique()),"trait_unique_species":int(tc.nunique()),"duplicate_trait_species":len(dup),
           "unresolved_trait_examples":sorted(set(series_label(t.loc[tc.isna(),"Species.name"]).dropna()))[:15],
           "unresolved_occ_examples":sorted(set(raw[oc.isna()].dropna()))[:15]}
    return tax,oc,tc,dup,audit
def assemblages(o,l,t):
    tax,oc,tc,dups,sa=source_taxa(o,t)
    k=cavekeys(o,True);kl=cavekeys(l,False)
    pairs=pd.DataFrame({"cave":k,"tax":tax,"species":oc,
        "realm":series_label(o["Biogeographical.realm"]),"series":series_label(o["Cave.data.series"]),
        "source":series_label(o["Record.source"])}).dropna(subset=["cave","tax"])
    # Cave tuples do not escape this process. Duplicate reports collapsed to cave x taxon.
    raw_n=len(pairs)
    realm_n=pairs.groupby("cave",sort=False).realm.nunique()
    series_n=pairs.groupby("cave",sort=False).series.nunique()
    sources_n=pairs.groupby("cave",sort=False).source.nunique()
    pairs=pairs.drop_duplicates(["cave","tax"]).copy()
    lcounts=kl.dropna().value_counts()
    good=set(lcounts[lcounts==1].index)
    occ_set=set(pairs.cave)
    audit={"species":sa,"occ_rows_with_complete_site_key":int(k.notna().sum()),
           "occ_distinct_site_keys":int(k.nunique()),"land_distinct_site_keys":int(kl.nunique()),
           "land_nonunique_keys":int((lcounts>1).sum()),"exact_unique_land_match_caves":len(occ_set&good),
           "exact_unique_land_match_fraction":len(occ_set&good)/len(occ_set) if occ_set else None,
           "cave_taxon_pairs":len(pairs),"duplicate_occurrence_reports_collapsed":raw_n-len(pairs),
           "caves_with_multiple_series":int((series_n>1).sum()),"caves_with_multiple_sources":int((sources_n>1).sum()),
           "caves_with_conflicting_realms":int((realm_n>1).sum()),
           "cave_richness":quant(pairs.groupby("cave",sort=False).size())}
    tr=pd.DataFrame({"species":tc,"mass":pd.to_numeric(t["Body.mass"].map(clean),errors="coerce"),
       "diet":series_label(t["Feeding groups"])})
    tr=tr[tr.species.notna()&~tr.species.isin(dups)].copy()
    tr.loc[~(tr.mass>0),"mass"]=np.nan
    # Paper specifies grams. Preserve source feeding category strings; metadata check before confirmatory use.
    tr["logmass"]=np.log(tr.mass)
    audit["mass_grams"]=quant(tr.mass)
    audit["diet_labels"]={str(k):int(v) for k,v in tr.diet.value_counts().items()}
    return pairs,tr,audit

def fd(pairs,tr,variables,categorical=()):
    tr=tr.dropna(subset=list(variables)).copy()
    assert tr.species.is_unique
    j=pairs.merge(tr[["species",*variables]],on="species",how="left",validate="many_to_one")
    spans={c:float(tr[c].max()-tr[c].min()) for c in variables if c not in categorical}
    if any(not np.isfinite(v) or v<=0 for v in spans.values()):raise ValueError("degenerate numeric trait")
    rr=[];cover=[]
    for _,g in j.groupby("cave",sort=False):
        h=g.dropna(subset=list(variables));n=len(h);N=len(g);cover.append(n/N)
        if n<3 or n/N<.8:continue
        ds=[]
        for c in variables:
            x=h[c].to_numpy()
            d=(x[:,None]!=x[None,:]).astype(float) if c in categorical else abs(x[:,None]-x[None,:])/spans[c]
            ds.append(float(d.mean()))
        q=float(np.mean(ds))
        rr.append((N,n,n/N,q,q*n/(n-1)))
    r=np.asarray(rr).reshape(-1,5)
    valid_species=set(tr.species)
    return {"eligible_caves":len(r),"eligible_caves_100pct":int((r[:,2]==1).sum()),
      "complete_trait_species":len(valid_species),"matched_species":int(pairs.loc[pairs.species.isin(valid_species),"species"].nunique()),
      "matched_pairs":int(j[list(variables)].notna().all(axis=1).sum()),"total_pairs":len(pairs),
      "median_cave_coverage":float(np.median(cover)) if cover else None,"coverage":quant(cover),
      "eligible_observed_richness":quant(r[:,0]),"rao_q":quant(r[:,3]),"mpd":quant(r[:,4]),
      "status":"descriptive_only"}

def wing():
    url="https://zenodo.org/api/records/4309199/files/Supplementary%20Files.zip/content"
    base="Supplementary Files/Code and Data/Data/"
    files=["wingReview_wm_data_speciesLevel.csv","wingReview_metadata.csv","wingReview_wm_data_final.csv"]
    data={};meta={}
    with RemoteZip(url,support_suffix_range=False,session=S,timeout=25) as z:
        for f in files:
            b=z.read(base+f)
            assert len(b)<2000000
            for enc in ("utf-8-sig","cp1252","latin1"):
                try:d=pd.read_csv(io.BytesIO(b),encoding=enc);break
                except UnicodeDecodeError:continue
            data[f]=d;meta[f]={"rows":len(d),"columns":list(map(str,d.columns)),
                 "bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}
    return data,meta
def wing_candidates(w):
    # Column detection is deliberately conservative; unknown units/aggregation await metadata review.
    def norm(c):return re.sub(r"[^a-z0-9]","",str(c).lower())
    sc=[]
    for c in w.columns:
        v=w[c].map(name)
        if v.notna().sum()>=20:sc.append((str(c),int(v.notna().sum()),int(v.nunique())))
    return {"species_column_candidates":sc,
            "numeric_column_counts":{str(c):int(pd.to_numeric(w[c],errors="coerce").notna().sum()) for c in w.columns},
            "column_aliases":{"aspect_ratio":[str(c) for c in w if norm(c) in {"ar","aspectratio","wingaspectratio","meanar","armean","arspp","aravg"}],
             "wing_loading":[str(c) for c in w if norm(c) in {"wl","wingloading","wingloadingnm2","meanwl","wlmean","wlspp","wlavg"}]}}
def main():
    r={"status":"blocked","sources":{}};f={}
    for k in ("traits","occ","land"):
        try:f[k],r["sources"][k]=get(k)
        except Exception as e:f[k]=None;r["sources"][k]={"error":str(e)[:250]}
    pairs=None
    if all(v is not None for v in f.values()):
        try:
            pairs,tr,r["assemblage_audit"]=assemblages(f["occ"],f["land"],f["traits"])
            if len(pairs)==0:raise ValueError("no assemblages")
            r["resource_fd"]=fd(pairs,tr,["logmass","diet"],categorical=["diet"])
            r["status"]="occurrence_fd_descriptive"
        except Exception as e:r["analysis_error"]=type(e).__name__+": "+str(e)[:300]
    dest=OUT/"audit_v4.json"
    dest.write_text(json.dumps(r,indent=2,allow_nan=False))
    try:
        data,r["wing_files"]=wing()
        w=data["wingReview_wm_data_speciesLevel.csv"]
        r["wing_schema"]=wing_candidates(w)
        r["wing_status"]="acquired_schema_review_required"
        sc=r["wing_schema"]["species_column_candidates"]
        # Exact name coverage of each plausible name column, no guessing quantitative variables.
        if pairs is not None:
            present=set(pairs.species.dropna())
            r["wing_schema"]["candidate_name_overlaps"]={c:len(set(w[c].map(name).dropna())&present) for c,_,_ in sc}
    except Exception as e:r["wing_status"]="blocked";r["wing_error"]=type(e).__name__+": "+str(e)[:300]
    dest.write_text(json.dumps(r,indent=2,allow_nan=False))
    print(json.dumps(r,indent=2,allow_nan=False))
    return 0 if r["status"]=="occurrence_fd_descriptive" else 2
if __name__=="__main__":sys.exit(main())
