"""Public source gate; no biological fitting or correction of FWS labels."""
import hashlib,io,json,pathlib,re,zipfile,csv
from urllib.parse import quote,urljoin,urlparse
import requests,openpyxl
O=pathlib.Path("acoustic_source");O.mkdir(exist_ok=True)
R={"stage":"acoustic observation and trait source gate","status":"START","sources":{},"limits":["Reference calls are not field detections; no calibrated FWS error correction.","Do not infer full multiclass confusion from separate binary margins.","Peak frequency and min-max geometric midpoint are different traits.","No biological fit or imputation."]}
def save():
    (O/"report.json").write_text(json.dumps(R,indent=2,allow_nan=False))
    print("ACOUSTIC_SOURCE_REPORT="+json.dumps(R,allow_nan=False),flush=True)
def grab(url,cap):
    with requests.get(url,stream=True,timeout=(15,60),headers={"Accept-Encoding":"identity","User-Agent":"batter-public-research/1.0"}) as q:
        q.raise_for_status()
        if q.headers.get("Content-Length") and int(q.headers["Content-Length"])>cap:raise ValueError("byte cap")
        data=bytearray()
        for x in q.iter_content(65536):
            data.extend(x)
            if len(data)>cap:raise ValueError("byte cap")
        return bytes(data)
def inspect(raw,name):
    suffix=pathlib.Path(name).suffix.lower()
    if suffix in (".csv",".tsv"):
        s=raw.decode("utf-8-sig",errors="strict")
        delim="\t" if suffix==".tsv" else ","
        rows=list(csv.reader(io.StringIO(s),delimiter=delim))
        if not rows:return {"rows":0}
        return {"rows_including_header":len(rows),"columns":rows[0],"column_count":len(rows[0]),"ragged_rows":sum(len(x)!=len(rows[0]) for x in rows[1:])}
    if suffix==".xlsx":
        w=openpyxl.load_workbook(io.BytesIO(raw),read_only=True,data_only=True)
        return {"sheets":[{"name":x.title,"rows":x.max_row,"columns":x.max_column,"first_rows":[[str(y)[:100] if y is not None else "" for y in row] for row in x.iter_rows(min_row=1,max_row=min(6,x.max_row),max_col=min(22,x.max_column),values_only=True)]} for x in w]}
    if suffix in (".md",".txt"):
        s=raw.decode("utf-8-sig",errors="replace")
        return {"documentation_excerpt":s[:3000]}
    return None
def sha(v):return hashlib.sha256(v).hexdigest()
def plos():
    t=R["sources"]["Solick2024"]={"doi":"10.1371/journal.pone.0300664","files":[]}
    for tag,ext in [("s001","xlsx"),("s004","zip")]:
        doi="10.1371/journal.pone.0300664."+tag
        a={"doi":doi}
        try:
            # Standard publisher's supplementary-file endpoint.
            u="https://journals.plos.org/plosone/article/file?type=supplementary&id="+doi
            raw=grab(u,25_000_000)
            assert raw[:2]==b"PK"
            with zipfile.ZipFile(io.BytesIO(raw)) as z:
                a.update(bytes=len(raw),sha256=sha(raw))
                if ext=="xlsx":
                    assert "xl/workbook.xml" in z.namelist()
                    p=O/("solick_"+tag+".xlsx");p.write_bytes(raw)
                    a.update(local_file=p.name,schema=inspect(raw,p.name),status="VERIFIED_FORMAT")
                else:
                    a["inventory"]=[{"name":x.filename,"bytes":x.file_size,"crc32":f"{x.CRC:08x}"} for x in z.infolist() if not x.is_dir()]
                    selected=[x for x in z.infolist() if not x.is_dir() and pathlib.Path(x.filename).suffix.lower() in (".csv",".tsv",".xlsx",".md",".txt") and 0<x.file_size<=5_000_000 and "__MACOSX" not in x.filename]
                    assert len(selected)<=50 and sum(x.file_size for x in selected)<=20_000_000
                    a["tables"]=[]
                    for i,x in enumerate(selected):
                        v=z.read(x)
                        p=O/f"solick_s004_{i:02d}_{pathlib.PurePosixPath(x.filename).name}"
                        p.write_bytes(v)
                        entry={"member":x.filename,"local_file":p.name,"sha256":sha(v),"bytes":len(v),"zip_crc_verified":True}
                        try:entry["schema"]=inspect(v,p.name)
                        except Exception as e:entry["schema_error"]=type(e).__name__
                        a["tables"].append(entry)
                    a["status"]="VERIFIED_ARCHIVE"
        except requests.HTTPError as e:a.update(status="HTTP_STOP",http=e.response.status_code if e.response is not None else None)
        except Exception as e:a.update(status="SOURCE_STOP",error=type(e).__name__)
        t["files"].append(a);save()
def figshare():
    t=R["sources"]["Giacomini2026"]={"doi":"10.5061/dryad.c59zw3rnt","collection_doi":"10.6084/m9.figshare.c.8229731","inventory":[],"files":[]}
    try:
        base="https://api.figshare.com/v2"
        q=requests.get(base+"/collections/8229731",timeout=30);q.raise_for_status()
        meta=q.json()
        assert "skull morphological adaptations" in meta.get("title","").lower()
        q=requests.get(base+"/collections/8229731/articles",params={"page_size":100},timeout=30);q.raise_for_status()
        articles=q.json();assert len(articles)<=100
        for x in articles:
            q=requests.get(base+"/articles/"+str(x["id"]),timeout=30);q.raise_for_status()
            a=q.json()
            rec={"article_id":a["id"],"title":a.get("title"),"doi":a.get("doi"),"license":a.get("license"),"files":[]}
            for f in a.get("files",[]):
                rec["files"].append({k:f.get(k) for k in ("id","name","size","computed_md5","supplied_md5")})
                name=f["name"]
                if not (re.search(r"covariate|readme|trait|table|data",name,re.I) and pathlib.Path(name).suffix.lower() in (".csv",".tsv",".xlsx",".md",".txt") and 0<f["size"]<=5_000_000):continue
                u=f["downloadUrl"];assert u.startswith("https://")
                raw=grab(u,5_000_000);assert len(raw)==f["size"]
                md5=hashlib.md5(raw).hexdigest()
                expected=f.get("computed_md5") or f.get("supplied_md5")
                if expected:assert md5==expected
                p=O/("giacomini_"+str(f["id"])+"_"+pathlib.Path(name).name)
                p.write_bytes(raw)
                t["files"].append({"article_id":a["id"],"name":name,"local_file":p.name,"sha256":sha(raw),"bytes":len(raw),"publisher_md5_verified":bool(expected),"schema":inspect(raw,name)})
            t["inventory"].append(rec);save()
        t["figshare_status"]="TABULAR_FILES_READY" if t["files"] else "NO_MATCHED_TABULAR_FILES"
    except requests.HTTPError as e:t.update(figshare_status="HTTP_STOP",figshare_http=e.response.status_code if e.response is not None else None)
    except Exception as e:t.update(figshare_status="SOURCE_STOP",figshare_error=type(e).__name__)
    # Independently retrieve official public Dryad metadata; file access may be gated.
    try:
        u="https://datadryad.org/api/v2/datasets/"+quote("doi:"+t["doi"],safe="")
        q=requests.get(u,timeout=30);q.raise_for_status();d=q.json()
        t["dryad_title"]=d.get("title")
        href=d.get("_links",{}).get("stash:version",{}).get("href")
        if href:
            v=requests.get(urljoin(u,href),timeout=30);v.raise_for_status();m=v.json()
            t["dryad_version"]=m.get("versionNumber")
            href=m.get("_links",{}).get("stash:files",{}).get("href")
            if href:
                q=requests.get(urljoin(u,href),timeout=30);q.raise_for_status()
                fs=q.json().get("_embedded",{}).get("stash:files",[])
                t["dryad_file_inventory"]=[{k:f.get(k) for k in ("id","path","size","digest","digestType")} for f in fs]
                for f in fs:
                    name=f.get("path","")
                    if pathlib.Path(name).name not in {"Covariates.csv","README.md"} or not 0<int(f.get("size",0))<=5_000_000:continue
                    dl=f.get("_links",{}).get("stash:download",{}).get("href")
                    if not dl:continue
                    raw=grab(urljoin(u,dl),5_000_000);assert len(raw)==int(f["size"])
                    p=O/("giacomini_dryad_"+pathlib.Path(name).name)
                    p.write_bytes(raw)
                    t["files"].append({"source":"Dryad","name":name,"local_file":p.name,"bytes":len(raw),"sha256":sha(raw),"schema":inspect(raw,name)})
        t["dryad_status"]="METADATA_COMPLETE"
    except requests.HTTPError as e:t.update(dryad_status="HTTP_STOP",dryad_http=e.response.status_code if e.response is not None else None)
    except Exception as e:t.update(dryad_status="SOURCE_STOP",dryad_error=type(e).__name__)
    save()
if __name__=="__main__":
    plos();figshare()
    R["status"]="SOURCE_GATE_FINISHED_REQUIRES_SEMANTIC_AUDIT";save()
