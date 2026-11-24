"""Fetch pinned public source files; audit schemas and exact-name coverage.
No coordinates, cave names, or row-level cave records in outputs.
Run with Python 3.11+, pandas, requests, openpyxl. A schema ambiguity is a stop.
"""
import hashlib, io, json, re, sys
from pathlib import Path
import pandas as pd
import requests

OUT=Path("roost_fd_audit"); OUT.mkdir(exist_ok=True)
SOURCES={
 "cave_traits": ["https://figshare.com/ndownloader/files/34091936"],
 "occurrence": ["https://figshare.com/ndownloader/files/34091939"],
 "landscape": ["https://figshare.com/ndownloader/files/34091942"],
 "wing": ["https://datadryad.org/downloads/file_stream/561736",
          "https://datadryad.org/api/v2/files/561736/download"]
}
SESSION=requests.Session()
SESSION.headers["User-Agent"]="batter-academic-data-audit/1.0"
def get(key):
 errors=[]
 for url in SOURCES[key]:
    try:
        r=SESSION.get(url,timeout=(15,60)); r.raise_for_status()
        data=r.content
        if len(data)<500 or b"<html" in data[:1000].lower() or b"<!doctype html" in data[:1000].lower():
            raise ValueError("HTML or truncated response")
        if data[:2]==b"PK":
            frames=pd.read_excel(io.BytesIO(data),sheet_name=None)
        else:
            frames=None
            for enc in ("utf-8-sig","cp1252"):
                try:
                    frames={"csv":pd.read_csv(io.BytesIO(data),encoding=enc,sep=None,engine="python")}
                    break
                except (UnicodeError,pd.errors.ParserError): pass
            if frames is None: raise ValueError("Cannot decode CSV")
        if not any(len(f)>10 and len(f.columns)>2 for f in frames.values()):
            raise ValueError("No substantial table")
        return frames,dict(url=url,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),
                           sheets={str(n):dict(rows=len(f),columns=list(map(str,f.columns))) for n,f in frames.items()})
    except Exception as e:
        errors.append(type(e).__name__+": "+str(e)[:250])
 return {},{"errors":errors}

def norm(x): return re.sub(r"[^a-z0-9]","",str(x).lower())
def binomial(s):
    # Conservative exact match, never silently collapse subspecies or fuzzy synonyms.
    s=re.sub(r"[_\s]+"," ",str(s).strip()).lower()
    return s if re.fullmatch(r"[a-z]+ [a-z-]+",s) else None
def matchcol(df,aliases):
    choices=[c for c in df.columns if norm(c) in aliases]
    return choices[0] if len(choices)==1 else None
def species(df):
    c=matchcol(df,{"species","speciesname","scientificname","scientificnames","binomial","taxon","binomialname","speciesbinomial","speciesfull","fullspeciesname","speciestaxon"})
    if c is not None: return df[c].map(binomial)
    g=matchcol(df,{"genus"}); s=matchcol(df,{"specific epithet".replace(" ",""),"specificepithet","epithet","speciesepithet"})
    if g is not None and s is not None: return (df[g].astype(str)+" "+df[s].astype(str)).map(binomial)
    return None

def candidate(frames,key):
    valid=[]
    for name,df in frames.items():
        names=species(df)
        if names is None or names.notna().sum()<10: continue
        if key=="occurrence":
            cave=matchcol(df,{"caveid","cavesid","cavecode","siteid","caveuniqueid","caveidentifier","idcave","cave"})
            if cave is None: continue
        valid.append((name,df,names))
    if len(valid)!=1: raise ValueError(f"{key}: {len(valid)} unambiguous schema candidates")
    return valid[0]

def main():
    audit={}; frames={}
    for key in SOURCES:
        frames[key],audit[key]=get(key)
    report={"source_audit":audit,"status":"blocked"}
    if any(not v for v in frames.values()):
        report["reason"]="One or more public downloads failed"
    else:
        try:
            _,o,on=candidate(frames["occurrence"],"occurrence")
            _,w,wn=candidate(frames["wing"],"wing")
            cave=matchcol(o,{"caveid","cavesid","cavecode","siteid","caveuniqueid","caveidentifier","idcave","cave"})
            pairs=pd.DataFrame({"cave":o[cave],"species":on}).dropna().drop_duplicates()
            valid_w=set(wn.dropna())
            present=set(pairs.species)
            covered=pairs.assign(match=pairs.species.isin(valid_w)).groupby("cave").match.agg(["size","sum"])
            report["coverage"]={
                "unique_caves":int(len(covered)),"unique_species":len(present),"cave_species_pairs":len(pairs),
                "trait_name_count":len(valid_w),"matched_species":len(present&valid_w),
                "matched_pairs":int(covered["sum"].sum()),"caves_ge_3_matched":int((covered["sum"]>=3).sum()),
                "caves_ge_3_matched_and_80pct":int(((covered["sum"]>=3)&(covered["sum"]/covered["size"]>=.8)).sum()),
                "occurrence_rows_invalid_names":int(on.isna().sum()),"wing_rows_invalid_names":int(wn.isna().sum()),
                "wing_rows_duplicate_valid_names":int(wn.dropna().duplicated().sum())}
            aliases={"aspect_ratio":{"ar","aspectratio","wingaspectratio"},"wing_loading":{"wl","wingloading","wingloadingnm2"},
                     "forearm":{"fa","forearm","forearmlength","forearmlengthmm"},"frequency":{"frequency","echolocationfrequency","peakfrequency","fpeak","pf","freq"}}
            report["trait_candidate_columns"]={k:matchcol(w,v) for k,v in aliases.items()}
            report["status"]="exact_name_audit_only"
        except Exception as e:
            report["reason"]=str(e)
    (OUT/"audit.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    # Output only schema and aggregate counts, never source values.
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return 0 if report["status"]=="exact_name_audit_only" else 2
if __name__=="__main__": sys.exit(main())
