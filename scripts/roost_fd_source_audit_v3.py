"""V3 exact, independently corroborated cave keys; species crosswalk and observed FD.
Aggregate output only. No cave IDs, names, coordinates or row-level data exported.
"""
import io,json,sys,re,unicodedata,hashlib
import numpy as np
import pandas as pd
from roost_fd_source_audit_v2 import get,clean,S,OUT
from roost_fd_source_audit_v1 import binomial

def label(v):
    s=clean(v)
    if s is None:return None
    return " ".join(unicodedata.normalize("NFKC",s).casefold().split())
def series_label(s):return s.map(label)
def binom_struct(g,e):
    g=label(g);e=label(e)
    if g and e and re.fullmatch("[a-z]+",g):
        if re.fullmatch("[a-z-]+",e):return g+" "+e
        b=binomial(e)
        if b and b.split()[0]==g:return b
    return None
def count(x):return int(x.sum())
def frac(x):return float(x.mean()) if len(x) else None
def quant(x):
    x=np.asarray(x,dtype=float);x=x[np.isfinite(x)]
    return dict(zip(["min","q25","median","q75","max"],map(float,np.quantile(x,[0,.25,.5,.75,1])))) if len(x) else {}
def exact_species(o,t):
    raw_t=series_label(t["Species.name"]);raw_o=series_label(o["Species.name"])
    struct=pd.Series([binom_struct(g,e) for g,e in zip(t["Genus"],t["Species"])],index=t.index)
    basic=t["Species.name"].map(binomial)
    conflict=basic.notna()&struct.notna()&(basic!=struct)
    canon=basic.fillna(struct).mask(conflict)
    # Explicit species-level structured columns can recover author-tagged names;
    # require the raw label to begin with the structured binomial (or be identical).
    recovery=basic.isna()&struct.notna()
    starts=pd.Series([bool(a and b and (a==b or a.startswith(b+" ") or a.startswith(b+"("))) for a,b in zip(raw_t,struct)],index=t.index)
    canon=canon.mask(recovery&~starts)
    ref=pd.DataFrame({"raw":raw_t,"canon":canon})
    raw_groups=ref.dropna().groupby("raw").canon.agg(lambda x:sorted(set(x)))
    exact={k:v[0] for k,v in raw_groups.items() if len(v)==1}
    oc=o["Species.name"].map(binomial)
    from_raw=raw_o.map(exact)
    mismatch=oc.notna()&from_raw.notna()&(oc!=from_raw)
    oc=oc.fillna(from_raw).mask(mismatch)
    dup=set(canon[canon.duplicated(keep=False)&canon.notna()])
    audit={"trait_rows":len(t),"trait_strict_binomials":count(basic.notna()),
       "trait_structured_recovered":count(basic.isna()&canon.notna()),"trait_conflicts":count(conflict),
       "trait_unique_valid_species":int(canon.nunique()),"trait_duplicate_species":len(dup),
       "occ_strict_binomials":count(o["Species.name"].map(binomial).notna()),
       "occ_exact_raw_recovered":count(o["Species.name"].map(binomial).isna()&oc.notna()),
       "occ_valid_species_rows":count(oc.notna()),"occ_conflicts":count(mismatch),
       "unresolved_trait_name_token_counts":{str(k):int(v) for k,v in raw_t[canon.isna()].dropna().str.split().str.len().value_counts().items()},
       "unresolved_occ_name_token_counts":{str(k):int(v) for k,v in raw_o[oc.isna()].dropna().str.split().str.len().value_counts().items()}}
    return oc,canon,dup,audit
def join_caves(o,l):
    a=series_label(o["Cave.data.series"]);b=series_label(l["Cave_Datas"])
    duplicate=b.notna()&b.duplicated(keep=False)
    lgood=l.loc[b.notna()&~duplicate].copy();lgood.index=b[b.notna()&~duplicate]
    matched=a.isin(lgood.index)
    audit={"occ_key_unique":int(a.nunique()),"land_key_unique":int(b.nunique()),
       "land_duplicate_rows":count(duplicate),"occ_key_missing":count(a.isna()),
       "matched_occ_rows":count(matched),"match_fraction":frac(matched),
       "matched_unique_keys":int(a[matched].nunique())}
    checks={}
    for left,right in [("Country.record","Country"),("Cave.site","Cave_Name"),("Biogeographical.realm","Biogeographical.realm")]:
        x=series_label(o[left]);y=a.map(series_label(lgood[right]))
        have=matched&x.notna()&y.notna()
        agree=pd.Series(False,index=o.index);agree.loc[have]=x.loc[have]==y.loc[have]
        checks[left]=(have,agree)
        audit[left]={"comparable":count(have),"agree":count(agree),"agreement":frac(agree[have])}
    xlat=pd.to_numeric(o["Lattitude"],errors="coerce");xlon=pd.to_numeric(o["Longitude"],errors="coerce")
    ylat=a.map(pd.to_numeric(lgood["Latitude"],errors="coerce"));ylon=a.map(pd.to_numeric(lgood["Longitude"],errors="coerce"))
    have=matched&xlat.notna()&xlon.notna()&ylat.notna()&ylon.notna()
    # Published rounded coordinates are corroboration only, not an identity key.
    dif=np.maximum(abs(xlat-ylat),abs(((xlon-ylon+180)%360)-180))
    same=have&(dif<=.011)
    audit["coord_check"]={"comparable":count(have),"within_0_011_degree":count(same),
        "agreement":frac(same[have]),"difference_deg_quantiles":quant(dif[have])}
    # Require exact ID and country and either matching cave label or coordinate corroboration.
    ch,ca=checks["Country.record"];nh,na=checks["Cave.site"]
    # Contradictory country/name/coordinate evidence is excluded, not forced.
    verified=matched&ca&(na|same)&~(nh&~na)&~(have&~same)
    audit["verified_occ_rows"]=count(verified);audit["verified_caves"]=int(a[verified].nunique())
    audit["verified_fraction"]=frac(verified)
    return a,verified,lgood,audit
def pilot(o,t,l):
    oc,tc,dups,sa=exact_species(o,t)
    key,verified,land,ja=join_caves(o,l)
    result={"species_audit":sa,"cave_join":ja}
    if ja["verified_fraction"] is None or ja["verified_fraction"]<.8:
        result["status"]="cave_key_review_required";return result
    # Preserve non-binomial unique raw occurrence labels in denominator to avoid overstated coverage.
    # They are unresolved taxa, never imputed to a known species.
    label_fallback=series_label(o["Species.name"]).map(lambda v:"unresolved:"+v if v else None)
    tax=oc.fillna(label_fallback)
    pairs=pd.DataFrame({"cave":key,"tax":tax,"species":oc,"realm":series_label(o["Biogeographical.realm"])}).loc[verified].dropna(subset=["cave","tax"]).drop_duplicates(["cave","tax"])
    tr=pd.DataFrame({"species":tc,"mass":pd.to_numeric(t["Body.mass"].map(clean),errors="coerce"),"diet":series_label(t["Feeding groups"])})
    tr=tr[tr.species.notna()&~tr.species.isin(dups)].copy()
    tr.loc[~(tr.mass>0),"mass"]=np.nan
    valid=tr.dropna(subset=["mass","diet"]).copy()
    valid["lm"]=np.log(valid.mass)
    result["counts"]={"verified_caves":int(pairs.cave.nunique()),"verified_distinct_cave_taxon_pairs":len(pairs),
       "verified_named_species":int(pairs.species.nunique()),"verified_unresolved_pairs":count(pairs.species.isna()),
       "exact_trait_matched_species":int(pairs.loc[pairs.species.isin(tr.species),"species"].nunique()),
       "complete_mass_diet_species":int(valid.species.nunique()),
       "matched_mass_diet_species":int(pairs.loc[pairs.species.isin(valid.species),"species"].nunique())}
    result["trait_qc"]={"mass_quantiles":quant(tr.mass),"feeding_categories":{str(k):int(v) for k,v in tr.diet.value_counts().items()},
        "nonpositive_or_nonnumeric_mass":count(tr.mass.isna())}
    j=pairs.merge(valid[["species","lm","diet"]],on="species",how="left",validate="many_to_one")
    span=valid.lm.max()-valid.lm.min()
    if not np.isfinite(span) or span<=0:raise ValueError("No valid mass span")
    rr=[];cov=[]
    for _,g in j.groupby("cave"):
        h=g.dropna(subset=["lm","diet"]);n=len(h);N=len(g);cov.append(n/N)
        if n<3 or n/N<.8:continue
        x=h.lm.to_numpy();d=h.diet.to_numpy()
        mass=float((abs(x[:,None]-x[None,:])/span).mean())
        diet=float((d[:,None]!=d[None,:]).mean())
        rr.append((N,n,mass,diet,(mass+diet)/2))
    r=np.asarray(rr).reshape(-1,5)
    result["fd_pilot"]={"eligible_caves":len(r),"complete_pair_fraction":frac(j.lm.notna()),"cave_coverage":quant(cov),
       "richness":quant(r[:,0]),"mass_rao_q":quant(r[:,2]),"diet_rao_q":quant(r[:,3]),"combined_rao_q":quant(r[:,4]),
       "status":"descriptive_only_pending_trait_units_and_category_metadata"}
    result["status"]="pilot_only";return result
def wing_probe():
    # Public article supplement (pooled species and study-level wing measurements).
    urls=["https://onlinelibrary.wiley.com/doi/suppl/10.1111/mam.12270/supinfo/mam12270-sup-0004-AppendixS7-S9.xlsx"]
    errors=[]
    for url in urls:
        try:
            r=S.get(url,timeout=(10,25));r.raise_for_status()
            b=r.content
            if b[:2]!=b"PK":raise ValueError("not xlsx")
            f=pd.read_excel(io.BytesIO(b),sheet_name=None,nrows=0)
            return {"status":"workbook_acquired","url":url,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest(),"sheets":{str(k):list(map(str,v.columns)) for k,v in f.items()}}
        except Exception as e:errors.append(str(e)[:200])
    try:
        from remotezip import RemoteZip
        u="https://zenodo.org/api/records/4309199/files/Supplementary%20Files.zip/content"
        # Read archive index, not the 648MB archive. Only list tabular members.
        with RemoteZip(u,support_suffix_range=False,session=S,timeout=25) as z:
            files=[i for i in z.infolist() if not i.is_dir() and re.search(r"\.(csv|tsv|xlsx|xls|rds|rdata)$",i.filename,re.I)]
            return {"status":"archive_index_only","errors":errors,"members":[{"name":i.filename,"bytes":i.file_size} for i in files][:100]}
    except Exception as e:errors.append(str(e)[:250])
    return {"status":"blocked","errors":errors}
def main():
    report={"sources":{},"status":"blocked"};f={}
    for k in ("traits","occ","land"):
        try:f[k],report["sources"][k]=get(k)
        except Exception as e:f[k]=None;report["sources"][k]={"error":str(e)[:300]}
    if all(v is not None for v in f.values()):
        try:
            report["internal"]=pilot(f["occ"],f["traits"],f["land"]);report["status"]=report["internal"]["status"]
        except Exception as e:report["error"]=type(e).__name__+": "+str(e)[:300]
    # Write audit even if alternative wing retrieval is slow; update after attempt.
    dest=OUT/"audit_v3.json"
    dest.write_text(json.dumps(report,indent=2,allow_nan=False))
    report["wing"]=wing_probe()
    dest.write_text(json.dumps(report,indent=2,allow_nan=False))
    print(json.dumps(report,indent=2,allow_nan=False))
    return 0 if report["status"]=="pilot_only" else 2
if __name__=="__main__":sys.exit(main())
