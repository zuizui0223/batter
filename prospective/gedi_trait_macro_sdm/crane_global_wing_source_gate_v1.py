"""Public Zenodo source gate for Crane et al. 2022 (doi:10.1111/mam.12270).
Do not infer AR/WL from index proxies or impute data; source rows only if verified.
No biological response fitting. Inspect original tabular files or archives.
"""
import collections,csv,hashlib,io,json,pathlib,re,zipfile,tarfile
from urllib.parse import urlparse,quote
import requests,openpyxl
OUT=pathlib.Path("crane_wing_source");OUT.mkdir(exist_ok=True)
LOCAL=pathlib.Path("crane_wing_original");LOCAL.mkdir(exist_ok=True)
DOI="10.5281/zenodo.4309198"
R={"stage":"global wing morphology original source gate, no ecological fit","cited_doi":DOI,"article_doi":"10.1111/mam.12270","status":"START","inventory":[],"files":[],"limits":["Study and species pooled measurements not independent replications.","Trait definitions, wing area conventions, species synonym and imputation status require source review; no silent filling.","No claimed match to FWS or continental species before actual table acquisition."]}
def save():
    (OUT/"report.json").write_text(json.dumps(R,indent=2,allow_nan=False))
    print("CRANE_WING_REPORT="+json.dumps(R,allow_nan=False),flush=True)
def sha(p,kind="sha256"):
    with p.open("rb") as f:return hashlib.file_digest(f,kind).hexdigest()
def record():
    # DOI may identify a concept; resolve to the official version record.
    q=requests.get("https://doi.org/"+DOI,timeout=(15,45))
    q.raise_for_status()
    p=urlparse(q.url);m=re.search(r"/records?/(\d+)",p.path)
    if not(m and p.hostname in {"zenodo.org","www.zenodo.org"}):raise ValueError("unexpected DOI landing page")
    rec=int(m[1]);z=requests.get(f"https://zenodo.org/api/records/{rec}",timeout=(15,45));z.raise_for_status();d=z.json()
    assert d["doi"]==DOI or d.get("conceptdoi")==DOI,(d.get("doi"),d.get("conceptdoi"))
    R["resolved_record"]={"record":rec,"doi":d["doi"],"conceptdoi":d.get("conceptdoi"),"title":d.get("metadata",{}).get("title"),"license":d.get("metadata",{}).get("license")}
    # DOI resolves to the authors\u0027 earlier working title, not the final paper title.
    assert rec==4309199 and d["doi"]=="10.5281/zenodo.4309199" and d.get("conceptdoi")==DOI
    assert "crane" in R["resolved_record"]["title"].lower() and "wing" in R["resolved_record"]["title"].lower()
    R["inventory"]=[{"name":v["key"],"size":v["size"],"checksum":v["checksum"]} for v in d["files"]]
    save();return rec,d
def acquire(rec,v):
    name=v["key"];size=int(v["size"]);assert 0<size<=30_000_000
    p=LOCAL/pathlib.Path(name).name
    htype,hd=v["checksum"].split(":",1)
    assert htype in ("md5","sha256")
    url=f"https://zenodo.org/api/records/{rec}/files/{quote(name,safe='')}/content"
    with requests.get(url,stream=True,timeout=(20,90),headers={"Accept-Encoding":"identity"}) as q:
        q.raise_for_status();assert q.status_code==200
        n=0
        with p.open("wb") as f:
            for b in q.iter_content(65536):
                n+=len(b);assert n<=size;f.write(b)
    assert n==size and sha(p,htype)==hd
    return p,{"name":name,"bytes":n,"sha256":sha(p),"published_checksum":v["checksum"],"publisher_checksum_verified":True}
def table_info(rows):
    rows=list(rows)
    if not rows:return {"rows":0}
    width=max(map(len,rows));head=rows[:5]
    return {"rows_including_header":len(rows),"columns_max":width,"first_rows":[[str(x)[:130] if x is not None else "" for x in row] for row in head],"nonempty_rows":sum(any(x is not None and str(x).strip() for x in row) for row in rows)}
def inspect_bytes(v,name):
    suffix=pathlib.Path(name).suffix.lower()
    if suffix in (".csv",".tsv",".txt"):
        s=v.decode("utf-8-sig",errors="replace")
        if suffix==".txt" and not re.search("trait|wing|appendix|species|mass|readme|reference",name,re.I):return None
        if suffix==".txt" and "readme" in name.lower():return {"readme_excerpt":s[:3500]}
        try:sep=csv.Sniffer().sniff(s[:8192],delimiters=",;\t").delimiter
        except csv.Error:return {"text_excerpt":s[:2000]}
        return table_info(csv.reader(io.StringIO(s),delimiter=sep))
    if suffix in (".xlsx",".xlsm"):
        z=openpyxl.load_workbook(io.BytesIO(v),read_only=True,data_only=True)
        return {"sheets":{x.title:table_info(x.values) for x in z}}
    return None
def inspect(p):
    suffix=p.suffix.lower()
    if suffix==".zip":
        with zipfile.ZipFile(p) as z:
            members=[x for x in z.infolist() if not x.is_dir()]
            out={"archive_members":[{"name":x.filename,"bytes":x.file_size} for x in members],"tables":{}}
            for m in members:
                if m.file_size>10_000_000:continue
                if re.search(r"\.(csv|tsv|xlsx|xlsm|txt)$",m.filename,re.I):
                    v=z.read(m);x=inspect_bytes(v,m.filename)
                    if x is not None:out["tables"][m.filename]={"sha256":hashlib.sha256(v).hexdigest(),**x}
            return out
    return inspect_bytes(p.read_bytes(),p.name)
def acquire_zip_members(rec,d):
    # Published version is a single 648 MB ZIP; use the already proven
    # public Zenodo HTTP range implementation from AHN4. Never load all
    # figure/model binaries or claim complete archive MD5 on partial reads.
    from ahn4_structural_validation_v1 import RangeReader
    f=[x for x in d["files"] if x["key"]=="Supplementary Files.zip"]
    assert len(f)==1
    f=f[0];size=int(f["size"]);assert 600_000_000<=size<=700_000_000
    assert f["checksum"]=="md5:3b34b6cf8b466190537b9a13ea57d459"
    url=f"https://zenodo.org/api/records/{rec}/files/{quote(f['key'],safe='')}/content"
    R["archive"]={"name":f["key"],"size":size,"published_checksum":f["checksum"],"full_archive_md5_verified":False,"public_url":url}
    save()
    rr=RangeReader(url,size)
    tables=OUT/"original_tables";tables.mkdir(exist_ok=True)
    with zipfile.ZipFile(rr) as z:
        members=[i for i in z.infolist() if not i.is_dir()]
        inv=[{"name":i.filename,"size":i.file_size,"compressed_size":i.compress_size,"crc32":f"{i.CRC:08x}"} for i in members]
        (OUT/"zip_inventory.json").write_text(json.dumps(inv,indent=2))
        R["archive"]["member_count"]=len(inv)
        R["archive"]["inventory_sha256"]=sha(OUT/"zip_inventory.json")
        candidates=[i for i in members if re.search(r"\.(csv|tsv|xlsx|xlsm|txt)$",i.filename,re.I) and 0<i.file_size<=10_000_000 and not any(x in i.filename.lower() for x in ["/.git/","__macosx","/figures/","/plots/"])]
        # Retrieve all actual small source tables, bounded before inspecting values.
        R["archive"]["selected_candidates"]=[{"name":i.filename,"size":i.file_size} for i in candidates]
        save()
        assert len(candidates)<=150 and sum(i.file_size for i in candidates)<=50_000_000,"source selection budget"
        for j,i in enumerate(candidates):
            try:
                raw=z.read(i)
                assert len(raw)==i.file_size
                q=tables/(f"{j+1:03d}_"+pathlib.PurePosixPath(i.filename).name)
                q.write_bytes(raw)
                schema=inspect_bytes(raw,i.filename)
                receipt={"name":i.filename,"local_file":str(q.relative_to(OUT)),"bytes":len(raw),"sha256":sha(q),"zip_crc32":f"{i.CRC:08x}","zip_crc_verified":True}
                if schema is not None:
                    # Log only structural previews; full verified source table in artifact.
                    receipt["schema"]=schema
                R["files"].append(receipt)
                # Avoid printing the entire growing archive table on every file.
                print("CRANE_MEMBER",j+1,q.name,len(raw),flush=True)
            except Exception as e:
                R["files"].append({"name":i.filename,"status":"SOURCE_STOP","error_type":type(e).__name__})
    R["archive"]["range_bytes_read"]=rr.transferred
    rr.session.close()
def main():
    rec,d=record()
    acquire_zip_members(rec,d)
    R["status"]="SOURCE_SCHEMA_READY" if any(x.get("schema") is not None and x.get("zip_crc_verified") for x in R["files"]) else "SOURCE_NOT_ADMITTED"
    save()
if __name__=="__main__":
    try:main()
    except Exception as e:R.update(status="INCOMPLETE",error_type=type(e).__name__,error=str(e)[:200]);save();raise
