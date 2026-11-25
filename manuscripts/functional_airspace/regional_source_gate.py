"""V2: diagnose HAL identity mismatch; source headers only, no ecological fit."""
import csv, hashlib, io, json, pathlib, re, urllib.request, urllib.error, urllib.parse
OUT=pathlib.Path("functional_site_source_receipt.json")
BASE="https://datadryad.org"
DOI="10.5061/dryad.x0k6djhrp"
EXPECTED={"cleaed_manual.output_27.11.2023.csv":2740496,"Marker_night_inventory_0704.2022_edit_(2).csv":2740491}
def get(url,limit):
    req=urllib.request.Request(url,headers={"User-Agent":"batter-research-source-gate/2.0","Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=40) as r:
        b=r.read(limit+1)
        if len(b)>limit: raise ValueError("bounded response exceeded")
        return b
def get_json(url): return json.loads(get(url,2_000_000))
def href(o,k): return o.get("_links",{}).get(k,{}).get("href")
def official(x):
    if not isinstance(x,str): raise ValueError("missing HAL link")
    u=urllib.parse.urljoin(BASE,x)
    p=urllib.parse.urlparse(u)
    if p.scheme!="https" or p.hostname!="datadryad.org" or not p.path.startswith("/api/v2/"):
        raise ValueError("unexpected API link")
    return u
def link_id(o,kind):
    s=href(o,"self") or ""
    m=re.search(r"/"+kind+r"/([0-9]+)(?:[/?#]|$)",s)
    via=int(m.group(1)) if m else None
    field=o.get("id")
    if field is not None:
        field=int(field)
        if via is not None and field!=via:raise ValueError("conflicting HAL ID")
    return via if via is not None else field
def pages(url,key):
    seen=set(); items=[]; info=[]
    while url:
        url=official(url)
        if url in seen or len(seen)>=10: raise ValueError("pagination limit or cycle")
        seen.add(url); d=get_json(url)
        entries=d.get("_embedded",{}).get(key)
        info.append({"top_keys":sorted(d),"embedded_keys":sorted(d.get("_embedded",{})),"count":d.get("count"),"total":d.get("total"),"entries":len(entries) if isinstance(entries,list) else None})
        if not isinstance(entries,list): raise ValueError("unexpected embedded schema")
        items.extend(entries); url=href(d,"next")
    if info and isinstance(info[0]["total"],int) and len(items)!=info[0]["total"]:raise ValueError("incomplete listing")
    return items,info
out={"scope":"V2 HAL link identity repair; metadata + public file header validation only","doi":DOI,"files":{}}
try:
    root=BASE+"/api/v2/datasets/"+urllib.parse.quote("doi:"+DOI,safe="")
    d=get_json(root)
    if d.get("identifier") not in {"doi:"+DOI,DOI}:raise ValueError("dataset DOI mismatch")
    out["dataset_keys"]=sorted(d)
    out["dataset_link_relations"]=sorted(d.get("_links",{}))
    versions,info=pages(href(d,"stash:versions") or root+"/versions","stash:versions")
    out["version_paging"]=info
    out["versions"]=[{"version_id":link_id(v,"versions"),"version_number":v.get("versionNumber"),"self":href(v,"self")} for v in versions]
    if len(versions)!=1:raise ValueError("not unique published version; no selection after mismatch")
    v=versions[0];vid=link_id(v,"versions")
    if vid is None:raise ValueError("unresolved version identity")
    out["version_id"]=vid
    f_url=href(v,"stash:files") or BASE+"/api/v2/versions/"+str(vid)+"/files"
    items,info=pages(f_url,"stash:files")
    out["file_paging"]=info
    out["inventory"]=[{"name":pathlib.PurePosixPath(x.get("path","")).name,"api_id":link_id(x,"files"),"size":x.get("size"),"digest":x.get("digest"),"digest_type":x.get("digestType"),"link_relations":sorted(x.get("_links",{})),"item_keys":sorted(x)} for x in items]
    for name,file_id in EXPECTED.items():
        r={"public_stream_id":file_id};out["files"][name]=r
        matches=[x for x in items if pathlib.PurePosixPath(x.get("path","")).name==name]
        if len(matches)!=1:
            r["status"]="STOP_NAME_NOT_UNIQUE";continue
        x=matches[0];aid=link_id(x,"files");r["api_file_id"]=aid
        r["declared_size"]=x.get("size");r["declared_digest"]=x.get("digest");r["declared_digest_type"]=x.get("digestType")
        if aid!=file_id:
            r["status"]="STOP_ID_DIFFERENCE_DIAGNOSED";continue
        try:
            b=get(BASE+"/downloads/file_stream/"+str(file_id),12_000_000)
            r["bytes"]=len(b);r["sha256"]=hashlib.sha256(b).hexdigest()
            if x.get("size") is not None and int(x["size"])!=len(b):raise ValueError("size mismatch")
            dt=str(x.get("digestType","")).lower().replace("-","")
            if x.get("digest") and dt in {"md5","sha256","sha1"}:
                r["digest_verified"]=hashlib.new(dt,b).hexdigest().lower()==str(x["digest"]).lower()
                if not r["digest_verified"]:raise ValueError("publisher digest mismatch")
            rows=csv.reader(io.StringIO(b.decode("utf-8-sig")),delimiter=";" if name.startswith("Marker_night") else ",")
            header=next(rows)
            if len(header)<3 or any(len(h)>150 for h in header):raise ValueError("invalid CSV header")
            r["header"]=header;r["row_count"]=sum(1 for row in rows if row);r["status"]="BYTES_AND_SCHEMA_OBTAINED_NOT_MODEL_ADMITTED"
        except Exception as e:
            r["status"]="STOP_SOURCE";r["error_type"]=type(e).__name__;r["http_status"]=getattr(e,"code",None)
except Exception as e:
    out["metadata_status"]="STOP_METADATA";out["error_type"]=type(e).__name__;out["reason"]=str(e)[:180] if isinstance(e,ValueError) else None;out["http_status"]=getattr(e,"code",None)
OUT.write_text(json.dumps(out,indent=2),encoding="utf-8")
print(json.dumps(out,indent=2))
