"""Source admission only: never fit outcomes, never print raw data."""
import csv, hashlib, io, json, pathlib, urllib.request, urllib.error, urllib.parse
OUT=pathlib.Path("functional_site_source_receipt.json")
BASE="https://datadryad.org"
EXPECTED={"cleaed_manual.output_27.11.2023.csv":2740496,"Marker_night_inventory_0704.2022_edit_(2).csv":2740491}
def get(url,limit):
    req=urllib.request.Request(url,headers={"User-Agent":"batter-research-source-gate/1.0","Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=40) as r:
        b=r.read(limit+1)
        if len(b)>limit: raise ValueError("bounded response exceeded")
        return b
def get_json(url):
    return json.loads(get(url,2_000_000))
def href(o,k):
    return o.get("_links",{}).get(k,{}).get("href")
def official(x):
    u=urllib.parse.urljoin(BASE,x)
    if urllib.parse.urlparse(u).hostname!="datadryad.org":raise ValueError("unexpected API host")
    return u
out={"scope":"metadata + public source header validation only; no ecological fit","doi":"10.5061/dryad.x0k6djhrp","files":{}}
try:
    d=get_json(BASE+"/api/v2/datasets/"+urllib.parse.quote("doi:"+out["doi"],safe=""))
    if out["doi"] not in str(d.get("identifier","")):raise ValueError("dataset DOI mismatch")
    vurl=href(d,"stash:version")
    if not vurl:
        versions=get_json(official(href(d,"stash:versions")))
        vs=versions.get("_embedded",{}).get("stash:versions",[])
        if len(vs)!=1:raise ValueError("no unique version")
        v=vs[0]
    else:v=get_json(official(vurl))
    f=get_json(official(href(v,"stash:files")))
    items=f.get("_embedded",{}).get("stash:files",[])
    out["version_id"]=v.get("id")
    for name,file_id in EXPECTED.items():
        r={"file_id":file_id}
        out["files"][name]=r
        match=[x for x in items if pathlib.PurePosixPath(x.get("path","")).name==name and int(x.get("id",-1))==file_id]
        if len(match)!=1:
            r["status"]="STOP_ID_NOT_MATCHED";continue
        x=match[0];r["declared_size"]=x.get("size");r["declared_digest"]=x.get("digest");r["declared_digest_type"]=x.get("digestType")
        try:
            # Official, publicly linked file stream; no credentials, no repeated retries.
            b=get(BASE+"/downloads/file_stream/"+str(file_id),12_000_000)
            r["bytes"]=len(b);r["sha256"]=hashlib.sha256(b).hexdigest()
            if x.get("size") is not None and int(x["size"])!=len(b):raise ValueError("size mismatch")
            dt=str(x.get("digestType","")).lower().replace("-","")
            if x.get("digest") and dt in {"md5","sha256","sha1"}:
                r["digest_verified"]=hashlib.new(dt,b).hexdigest().lower()==str(x["digest"]).lower()
                if not r["digest_verified"]:raise ValueError("publisher digest mismatch")
            s=b.decode("utf-8-sig")
            delimiter=";" if name.startswith("Marker_night") else ","
            rows=csv.reader(io.StringIO(s),delimiter=delimiter)
            header=next(rows)
            if len(header)<3 or any(len(h)>150 for h in header):raise ValueError("invalid CSV header")
            r["header"]=header;r["row_count"]=sum(1 for row in rows if row);r["status"]="BYTES_AND_SCHEMA_OBTAINED_NOT_MODEL_ADMITTED"
        except Exception as e:
            r["status"]="STOP_SOURCE";r["error_type"]=type(e).__name__;r["http_status"]=getattr(e,"code",None)
except Exception as e:
    out["metadata_status"]="STOP_METADATA";out["error_type"]=type(e).__name__;out["http_status"]=getattr(e,"code",None)
OUT.write_text(json.dumps(out,indent=2),encoding="utf-8")
print(json.dumps(out,indent=2))
