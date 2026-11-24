"""V2: strict lossless CSV parsing, internal-trait FD pilot and separate wing-source discovery.
No cave names, coordinates or individual cave results are exported.
"""
import csv, io, json, hashlib, collections, re, sys, math
from pathlib import Path
import pandas as pd
import numpy as np
import requests
from roost_fd_source_audit_v1 import binomial, norm
OUT=Path("roost_fd_audit"); OUT.mkdir(exist_ok=True)
S=requests.Session()
S.headers["User-Agent"]="batter-academic-data-audit/2.0"
URLS={"traits":"https://figshare.com/ndownloader/files/34091936",
      "occ":"https://figshare.com/ndownloader/files/34091939",
      "land":"https://figshare.com/ndownloader/files/34091942"}
EXPECTED={"traits":679,"land":2001}
def parse(data, expected=None):
    if data[:2]==b"PK":
        sheets=pd.read_excel(io.BytesIO(data),sheet_name=None,dtype=str)
        good=[(n,d) for n,d in sheets.items() if d.shape[0]>10 and d.shape[1]>2 and (expected is None or len(d)==expected)]
        if len(good)!=1: raise ValueError("Ambiguous workbook")
        return good[0][1],{"format":"xlsx","sheet":str(good[0][0])}
    if data[:2] in (b"\xff\xfe",b"\xfe\xff"):
        encs=["utf-16"]
    else: encs=["utf-8-sig","cp1252","latin1"]
    diag=[]
    for enc in encs:
        try: txt=data.decode(enc)
        except UnicodeError: continue
        if "\x00" in txt: continue
        for sep in (",",";","\t","|"):
            for mode in ("normal","literal"):
                try:
                    rows=[r for r in csv.reader(io.StringIO(txt,newline=""),delimiter=sep,
                          quoting=csv.QUOTE_MINIMAL if mode=="normal" else csv.QUOTE_NONE,strict=True) if any(x.strip() for x in r)]
                    if len(rows)<11: continue
                    widths=collections.Counter(map(len,rows))
                    header=[v.strip() for v in rows[0]]
                    n=len(header)
                    diag.append({"encoding":enc,"delimiter":repr(sep),"quoting":mode,"rows":len(rows)-1,"widths":dict(widths)})
                    if n<3 or len(set(header))!=n or not all(header) or len(widths)!=1: continue
                    if expected is not None and len(rows)-1!=expected: continue
                    if not any(norm(c) in {"datasetsequenceid","speciesname","cavedatas","species"} for c in header): continue
                    return pd.DataFrame(rows[1:],columns=header),{"format":"csv","encoding":enc,"delimiter":repr(sep),"quoting":mode}
                except csv.Error:
                    diag.append({"encoding":enc,"delimiter":repr(sep),"quoting":mode,"error":"csv.Error"})
    raise ValueError("No lossless parse; diagnostic="+json.dumps(diag)[:8500])
def get(key):
    r=S.get(URLS[key],timeout=(15,45));r.raise_for_status()
    b=r.content
    meta={"url":URLS[key],"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}
    try:
        df,fmt=parse(b,EXPECTED.get(key))
        meta.update(fmt); meta.update(rows=len(df),columns=list(df.columns))
        return df,meta
    except Exception as e:
        meta["error"]=str(e);return None,meta
def clean(x):
    s=str(x).strip()
    return s if s.lower() not in {"","nan","na","n/a","none","null","unknown","-","?","not available","data deficient"} else None
def col(df, names):
    cols=[c for c in df if norm(c) in names]
    return cols[0] if len(cols)==1 else None
def names(df):
    # Prefer explicitly binomial species-name column, not the separate epithet.
    for aliases in ({"speciesname","scientificname","binomial","scientificnames"},{"species","taxon"}):
        c=col(df,aliases)
        if c is not None and df[c].map(binomial).notna().sum()>10:
            return df[c].map(binomial),c
    raise ValueError("No unambiguous binomial field")
def source_wing():
    # Public metadata endpoint for alternative measured wing-trait compilation.
    try:
        r=S.get("https://zenodo.org/api/records/4309198",timeout=(10,30));r.raise_for_status()
        j=r.json()
        return {"status":"metadata_only","record":j.get("id"),"title":j.get("metadata",{}).get("title"),
                "files":[{"name":f.get("key"),"size":f.get("size"),"checksum":f.get("checksum"),"download":f.get("links",{}).get("self")} for f in j.get("files",[])]}
    except Exception as e:
        return {"status":"metadata_failed","error":str(e)[:250],
                "alternative":"https://doi.org/10.1111/mam.12270 (appendices S7-S9)"}
def coverage(o,t,l):
    on,oc=names(o);tn,tc=names(t)
    candidates=[]
    for c in o:
        if norm(c) not in {"cavedatas","caveid","cavesid","cavecode","siteid","caveidentifier","datasetsequenceid","cavename","cave"}: continue
        for lc in l:
            if norm(c)!=norm(lc): continue
            a=o[c].map(clean); b=l[lc].map(clean); bs=set(b.dropna())
            k=int(a.nunique()); matched=float(a.isin(bs).mean())
            candidates.append({"occ_col":c,"land_col":lc,"unique_occ":k,"unique_land":int(b.nunique()),"land_duplicate":int(b.dropna().duplicated().sum()),"match_fraction":matched,"repeated_occ":int(a.dropna().duplicated().sum())})
    # Do not use sequence IDs, labels/names or row numbers as cave identity.
    # Require explicit cave IDs and unique landscape key plus high coverage.
    good=[a for a in candidates if norm(a["occ_col"]) in {"cavedatas","caveid","cavesid","cavecode","siteid","caveidentifier"} and a["land_duplicate"]==0 and a["repeated_occ"]>0 and a["match_fraction"]>=.9]
    report={"species_fields":{"occ":oc,"traits":tc},"cave_key_candidates":candidates,
            "occ_rows_valid_binomial":int(on.notna().sum()),"trait_rows_valid_binomial":int(tn.notna().sum())}
    if len(good)!=1:
        report.update(status="cave_key_review_required");return report
    key=good[0]["occ_col"];landkey=good[0]["land_col"]
    # Audit consistency of shared country/name labels without printing their values.
    a=o[key].map(clean); lkey=l[landkey].map(clean)
    for field in ("country","cavename"):
        oc2=col(o,{field});lc2=col(l,{field})
        if oc2 is not None and lc2 is not None:
            lookup=dict(zip(lkey,l[lc2].map(clean)))
            aa=o[oc2].map(clean);bb=a.map(lookup)
            both=aa.notna()&bb.notna()
            agreement=float((aa[both].str.casefold()==bb[both].str.casefold()).mean()) if both.any() else None
            report[field+"_agreement"]=agreement
            if agreement is not None and agreement<.95:
                report.update(status="cave_key_label_conflict");return report
    pairs=pd.DataFrame({"cave":a,"species":on}).dropna().drop_duplicates()
    # Use exactly one trait row per valid binomial; duplicates are not silently averaged.
    tr=pd.DataFrame({"species":tn,"mass":pd.to_numeric(t["Body.mass"].map(clean),errors="coerce"),
                     "diet":t["Feeding groups"].map(clean)}).dropna(subset=["species"])
    dup=set(tr.loc[tr.species.duplicated(keep=False),"species"])
    tr=tr[~tr.species.isin(dup)].copy();tr.loc[~(tr.mass>0),"mass"]=np.nan
    valid=tr.dropna(subset=["mass","diet"]).copy()
    valid["lm"]=np.log(valid.mass)
    report["counts"]={"caves":int(pairs.cave.nunique()),"species":int(pairs.species.nunique()),
        "pairs":len(pairs),"matched_names":int(pairs.species.isin(tr.species).sum()),
        "trait_duplicate_species_excluded":len(dup),"trait_complete_species":len(valid)}
    report["trait_qc"]={"mass_quantiles":{str(k):float(v) for k,v in tr.mass.quantile([0,.01,.5,.99,1]).items()},
      "feeding_categories":{str(k):int(v) for k,v in tr.diet.value_counts().items()}}
    # Missingness / observed-only descriptive FD, not richness-conditioned inference.
    j=pairs.merge(valid[["species","lm","diet"]],on="species",how="left",validate="many_to_one")
    span=valid.lm.max()-valid.lm.min()
    assert np.isfinite(span) and span>0
    qs=[];cover=[];rich=[]
    for _,g in j.groupby("cave"):
        h=g.dropna(subset=["lm","diet"]);n=len(h);N=len(g);cover.append(n/N)
        if n<3 or n/N<.8:continue
        x=h.lm.to_numpy();d=h.diet.to_numpy()
        G=.5*np.abs(x[:,None]-x[None,:])/span+.5*(d[:,None]!=d[None,:])
        qs.append(float(G.mean()));rich.append(N)
    report["fd_pilot"]={"status":"provisional_numeric_mass_and_raw_feeding_labels_not_unit_validated",
        "eligible_caves":len(qs),"median_complete_fraction":float(np.median(cover)) if cover else None,
        "rao_q_quantiles":dict(zip(["min","q25","median","q75","max"],map(float,np.quantile(qs,[0,.25,.5,.75,1])))) if qs else {},
        "richness_range":[min(rich),max(rich)] if rich else [],
        "caution":"Raw categorical feeding labels and numeric mass only; units/label coding require metadata review. Incidence weights. No landscape association, no flight traits, no causal inference."}
    report["status"]="pilot_only";return report
def main():
    frames={};r={"sources":{}}
    for key in URLS:
        try: frames[key],r["sources"][key]=get(key)
        except Exception as e: frames[key]=None;r["sources"][key]={"error":str(e)[:1000]}
    r["wing_alternative"]=source_wing()
    r["status"]="blocked"
    if all(v is not None for v in frames.values()):
        try:
            r["internal_traits"]=coverage(frames["occ"],frames["traits"],frames["land"])
            r["status"]=r["internal_traits"]["status"]
        except Exception as e:r["analysis_error"]=str(e)[:500]
    (OUT/"audit_v2.json").write_text(json.dumps(r,indent=2,ensure_ascii=False,allow_nan=False),encoding="utf8")
    print(json.dumps(r,indent=2,ensure_ascii=False,allow_nan=False))
    return 0 if r["status"]=="pilot_only" else 2
if __name__=="__main__":sys.exit(main())
