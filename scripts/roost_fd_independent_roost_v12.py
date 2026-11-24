"""V12 roost-trait source recovery and pre-analysis schema audit.
Do not infer non-use from unrecorded use, or equate species pools with assemblages.
No location-level data, coordinates or source-level observation rows are emitted.
"""
import io,json,re,hashlib
import pandas as pd
from roost_fd_source_audit_v2 import S,OUT
from roost_fd_source_audit_v3 import label
from roost_fd_source_audit_v4 import wing,name
from roost_fd_study_wing_v7 import study_wing
from roost_fd_independent_roost_v11 import download

IDS={"roost":38642873,"taxon":38642894,"description":38642897,
     "morphology":39765382,"foraging":38642870,"references":38642900}
def norm(x):return re.sub("[^a-z0-9]","",str(x).lower())
def readcsv(b):
    for enc in ("utf-8-sig","cp1252","latin1"):
        try:
            d=pd.read_csv(io.BytesIO(b),sep=None,engine="python",encoding=enc,dtype=str)
            if d.shape[1]>2 and len(d)>0:return d
        except (UnicodeError,pd.errors.ParserError):continue
    raise ValueError("no valid csv")
def inspect(d):
    return {"n":len(d),"columns":list(map(str,d.columns)),
        "nonmissing":{str(c):int(d[c].notna().sum()) for c in d},
        "distinct":{str(c):int(d[c].nunique()) for c in d}}
def get_euro():
    meta,ms=download("https://api.figshare.com/v2/articles/21777161/versions/2",2_000_000)
    doc=json.loads(meta);files={int(f["id"]):f for f in doc["files"]}
    frames={};audit={}
    for key,i in IDS.items():
        try:
            f=files[i];url=f.get("downloadUrl") or f.get("download_url") or "https://figshare.com/ndownloader/files/"+str(i)
            b,m=download(url,5_000_000)
            if len(b)!=int(f["size"]):raise ValueError("size mismatch")
            expected=f.get("computed_md5") or f.get("supplied_md5")
            if expected and hashlib.md5(b).hexdigest()!=expected:raise ValueError("md5 mismatch")
            d=readcsv(b);frames[key]=d;audit[key]={**m,**inspect(d),"file_id":i}
        except Exception as e:audit[key]={"error":type(e).__name__+": "+str(e)[:200]}
    return frames,audit
def schema_audit(frames):
    out={}
    if "description" in frames:
        d=frames["description"];cols=[c for c in d if re.search("trait|definition|description|category|unit|type",str(c),re.I)]
        rows=d[d[cols].fillna("").apply(lambda x:bool(re.search("roost|hibernacul|maternity|cave|underground", " ".join(x.astype(str)),re.I)),axis=1)]
        out["roost_definitions"]=[{str(c):str(v[c])[:900] for c in cols if pd.notna(v[c])} for _,v in rows.iterrows()][:40]
    if "roost" in frames:
        d=frames["roost"];out["roost_vocab"]={}
        for c in d:
            # only trait/value fields, not record, locality, or source IDs
            if re.search("trait|value|season|type|depend|importance|unit",str(c),re.I) and 0<d[c].nunique()<=80:
                out["roost_vocab"][str(c)]={str(k):int(v) for k,v in d[c].value_counts().items()}
        tr=[c for c in d if norm(c) in {"trait","traitid","idtrait","traitname"}]
        vv=[c for c in d if norm(c) in {"value","traitvalue","valuetrait","valuecategory"}]
        if len(tr)==1 and len(vv)==1:
            out["values_by_trait"]={str(k):{str(a):int(b) for a,b in g[vv[0]].value_counts().items()} for k,g in d.groupby(tr[0]) if g[vv[0]].nunique()<=50}
    if "taxon" in frames:
        d=frames["taxon"];out["taxon_name_candidates"]={str(c):int(d[c].map(name).notna().sum()) for c in d if d[c].map(name).notna().sum()>10}
        try:
            data,meta=wing();w,qc=study_wing(data["wingReview_wm_data_final.csv"],"direct_or_formula")
            valid=w.dropna(subset=["aspectRatio"]);names=set(valid["scientificName.iucn"].map(name).dropna())
            out["wing_overlap_by_taxon_column"]={str(c):len(set(d[c].map(name).dropna())&names) for c in out["taxon_name_candidates"]}
            out["wing_hash"]=meta["wingReview_wm_data_final.csv"]["sha256"]
        except Exception as e:out["wing_error"]=type(e).__name__
    return out
def landing():
    url="https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/SCBE4W"
    b,m=download(url,4_000_000);j=json.loads(b);v=j["data"]["latestVersion"];out={"source":m,"dataset_version":[v.get("versionNumber"),v.get("versionMinorNumber")],"files":[]}
    for f in v["files"]:
        d=f["dataFile"];fn=d.get("filename","");out["files"].append({"id":d["id"],"name":fn,"size":d.get("filesize"),"content_type":d.get("contentType"),"restricted":bool(f.get("restricted",False))})
    # inspect candidate roost/landing style tables (not location-level trajectory/force records)
    for q in out["files"]:
        if q["restricted"] or (q["size"] or 0)>5_000_000 or not re.search("roost|landing.?style|species|ecology",q["name"],re.I):continue
        try:
            b,m=download("https://dataverse.harvard.edu/api/access/datafile/"+str(q["id"]),5_000_000)
            q["download"]=m
            if q["name"].lower().endswith((".csv",".tab",".tsv",".txt")):
                d=readcsv(b);q["table"]=inspect(d)
                q["trait_vocab"]={str(c):{str(k):int(v) for k,v in d[c].value_counts().items()} for c in d if re.search("roost|style|substrate|stiff|orient|maneuver|landing",str(c),re.I) and d[c].nunique()<=30}
        except Exception as e:q["error"]=type(e).__name__+": "+str(e)[:150]
    return out
def main():
    result={"status":"schema_audit","independent_roost_analysis":"not yet performed",
      "interpretation":"Regional, fixed-margin, and roost species-pool comparisons are distinct estimands, not bounds on one true effect."}
    dest=OUT/"audit_v12.json"
    def save():dest.write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False))
    try:
        frames,result["euro_files"]=get_euro()
        result["euro_schema"]=schema_audit(frames)
        result["euro_acquired"]=all(k in frames for k in ("roost","taxon","description"))
    except Exception as e:result["euro_error"]=type(e).__name__+": "+str(e)[:200]
    save()
    try:result["landing_dataverse"]=landing()
    except Exception as e:result["landing_error"]=type(e).__name__+": "+str(e)[:200]
    save();print(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False))
    return 0 if result.get("euro_acquired") else 2
if __name__=="__main__":raise SystemExit(main())
