"""V20 Dryad independent vampire-bat GPS source eligibility, no numeric altitude outcomes."""
import csv,io,json,hashlib,re,zipfile
from collections import Counter
from urllib.parse import quote,urljoin
import pandas as pd
from roost_fd_source_audit_v2 import OUT,S
DOI="10.5061/dryad.7wm37pw53"
BASE="https://datadryad.org"
CAP=60_000_000

def fetch(url,cap=CAP):
    b=bytearray()
    with S.get(url,stream=True,timeout=(15,60)) as r:
        r.raise_for_status()
        for c in r.iter_content(1024*1024):
            b.extend(c)
            if len(b)>cap:raise ValueError("bounded download exceeded")
    return bytes(b)

def api(path):return json.loads(fetch(urljoin(BASE,path),5_000_000))
def norm(s):return re.sub(r"[^a-z0-9]","",str(s).lower())
def file_digest(f,b):
    if f.get("size") is not None and len(b)!=int(f["size"]):raise ValueError("file size mismatch")
    digest=f.get("digest")
    sha=hashlib.sha256(b).hexdigest()
    if isinstance(digest,str) and re.fullmatch(r"[0-9a-fA-F]{64}",digest) and sha.lower()!=digest.lower():
        raise ValueError("SHA256 mismatch")
    return {"bytes":len(b),"sha256":sha,"published_digest":digest}
def read_table(b,fn):
    if fn.lower().endswith(".xlsx"):
        return pd.read_excel(io.BytesIO(b),sheet_name=None,dtype=str)
    for enc in ("utf-8-sig","cp1252"):
        try:
            d=pd.read_csv(io.BytesIO(b),dtype=str,encoding=enc,sep=None,engine="python")
            if d.shape[1]>2:return {"csv":d}
        except (UnicodeError,pd.errors.ParserError):pass
    raise ValueError("unrecognized table format")
def field(d,aliases):
    matches=[c for c in d if norm(c) in aliases]
    return matches[0] if len(matches)==1 else None

def audit(d):
    r={"rows":len(d),"columns":list(map(str,d.columns))}
    aliases={"altitude":{"altitude","heightabovemsl","heightaboveellipsoid","gpsaltitude","elevation"},
      "lat":{"y","latitude","lat","locationlat"},"lon":{"x","longitude","lon","long","locationlong"},
      "id":{"animalid","id","batid","bat","individualid","individual","tagid","tag"},
      "time":{"timestamp","datetime","datatime","dateandtime","timeutc","gpsdatetime","fixdatetime"},
      "date":{"date","gpsdate","fixdate"},"clock":{"time","gpstime","fixtime"},
      "rate":{"rate","fixrate","samplinginterval"},"session":{"session","night","trackid","tripid","deploymentid"}}
    fields={k:field(d,v) for k,v in aliases.items()}
    r["candidate_columns"]=fields
    if not all(fields[k] for k in ("altitude","lat","lon","id")):
        r["status"]="schema_review";return r
    alt=d[fields["altitude"]].astype("string").str.strip()
    missing=alt.isna()|alt.str.lower().isin(["","na","nan","null","none"])
    zero=alt.str.fullmatch(r"[+-]?0+(?:\.0+)?").fillna(False)
    ident=d[fields["id"]].astype("string").str.strip()
    def present(c):
        s=d[c].astype("string").str.strip()
        return s.notna()&~s.str.lower().isin(["","na","nan","null","none"])
    eligible=~missing&~zero&present(fields["lat"])&present(fields["lon"])&present(fields["id"])
    r.update(altitude_nonmissing=int((~missing).sum()),altitude_zero_flag=int(zero.sum()),
        simultaneous_field_presence=int(eligible.sum()),individuals_with_fields=int(ident[eligible].nunique()))
    if fields["rate"]:
        r["rate_labels"]={str(k):int(v) for k,v in d[fields["rate"]].value_counts().head(30).items()}
    if fields["time"]:tt=d[fields["time"]]
    elif fields["date"] and fields["clock"]:tt=d[fields["date"]].astype("string")+" "+d[fields["clock"]].astype("string")
    else:r["status"]="timestamp_schema_review";return r
    t=pd.to_datetime(tt,format="mixed",utc=True,errors="coerce")
    q=pd.DataFrame({"id":ident,"t":t,"ok":eligible})
    r["parsed_timestamp_rows"]=int(t.notna().sum())
    # Sort full observed timestamps before checking both endpoints, do not bridge missing altitude.
    q=q.dropna(subset=["id","t"]).sort_values(["id","t"])
    q["dup"]=q.duplicated(["id","t"],keep=False)
    q["dt"]=q.groupby("id").t.diff().dt.total_seconds()
    q["prev_ok"]=q.groupby("id").ok.shift(fill_value=False)
    q["prev_dup"]=q.groupby("id").dup.shift(fill_value=True)
    q["short_interval_pair"]=q.ok&q.prev_ok&~q.dup&~q.prev_dup&q.dt.between(5,120)
    cnt=q.groupby("id").short_interval_pair.sum()
    g=q.loc[q.dt>0,"dt"]
    r["positive_interval_quantiles_s"]={str(k):float(v) for k,v in g.quantile([0,.25,.5,.75,1]).items()} if len(g) else {}
    r["short_interval_pairs"]=int(q.short_interval_pair.sum())
    r["individuals_ge50_short_pairs"]=int((cnt>=50).sum())
    r["status"]="structural_candidate" if r["individuals_ge50_short_pairs"]>=6 else "interval_or_sample_gate_not_met"
    return r
def main():
    result={"status":"source_preflight","doi":DOI,"numeric_altitude_outcomes_read":False,"files":[]}
    dest=OUT/"audit_v20_desmodus.json"
    def save():dest.write_text(json.dumps(result,indent=2,allow_nan=False))
    save()
    try:
        doc=api("/api/v2/datasets/"+quote("doi:"+DOI,safe=""))
        result["title"]=doc.get("title")
        result["publication_date"]=doc.get("publicationDate")
        result["abstract"]=str(doc.get("abstract") or "")[:1800]
        v=api(doc["_links"]["stash:version"]["href"])
        result["version"]=v.get("versionNumber") or v.get("version")
        files=api(v["_links"]["stash:files"]["href"]).get("_embedded",{}).get("stash:files",[])
        for f in files:
            fn=f.get("path") or f.get("filename") or ""
            q={k:f.get(k) for k in ("path","size","digest","mimeType")}
            q["download"]=f.get("_links",{}).get("stash:download",{}).get("href")
            result["files"].append(q)
            if not q["download"] or (f.get("size") or 0)>CAP:continue
            try:
                if fn.lower().endswith((".md",".txt")):
                    b=fetch(urljoin(BASE,q["download"]),min(CAP,2_000_000));q["verified"]=file_digest(f,b)
                    # Only data-dictionary lines, never arbitrary location values.
                    lines=b.decode("utf-8-sig",errors="replace").splitlines()
                    q["dictionary_lines"]=[line.strip()[:500] for line in lines if re.search(r"altitude|sampling interval|satellite|WGS84|timestamp|gps fix|date.?time",line,re.I) and not re.search(r"\b\d{2,3}\.\d{3,}\b",line)][:20]
                elif fn.lower().endswith((".csv",".tsv",".xlsx")):
                    b=fetch(urljoin(BASE,q["download"]));q["verified"]=file_digest(f,b)
                    q["tables"]={n:audit(d) for n,d in read_table(b,fn).items()}
                elif fn.lower().endswith(".zip"):
                    b=fetch(urljoin(BASE,q["download"]));q["verified"]=file_digest(f,b)
                    with zipfile.ZipFile(io.BytesIO(b)) as z:
                        q["members"]=[{"name":i.filename,"bytes":i.file_size} for i in z.infolist() if not i.is_dir()][:100]
                        q["tables"]={}
                        for i in z.infolist():
                            if i.file_size<=CAP and i.filename.lower().endswith((".csv",".tsv",".xlsx")):
                                for k,d in read_table(z.read(i),i.filename).items():q["tables"][i.filename+"::"+k]=audit(d)
            except Exception as e:q["error"]=type(e).__name__+": "+str(e)[:160]
            save()
        result["status"]="completed_source_preflight"
    except Exception as e:result["status"]="metadata_blocked";result["error"]=type(e).__name__+": "+str(e)[:200]
    save();print(dest.read_text())
    return 0 if result["status"]=="completed_source_preflight" else 2
if __name__=="__main__":raise SystemExit(main())
