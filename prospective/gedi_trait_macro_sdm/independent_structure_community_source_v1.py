"""Bounded new independent source gate. No ecological fit."""
import csv, hashlib, io, json, pathlib, sys, urllib.parse
from collections import Counter
import requests
S=requests.Session()
M=1024**2
mode=sys.argv[1]
O=pathlib.Path("independent_"+mode);O.mkdir(exist_ok=True)
R={"source":mode,"status":"START","ecological_fit":False,"transfers":[]}
class Stop(Exception):pass
def need(x,msg):
    if not x:raise ValueError(msg)
def allowed(url):
    p=urllib.parse.urlparse(url);h=p.hostname or ""
    return p.scheme=="https" and not p.username and not p.password and (h=="www.envidat.ch" if mode=="swiss" else h.endswith(".gov.uk") or h=="gov.uk" or h.endswith(".forestresearch.gov.uk"))
def get(url,cap,name):
    need(allowed(url),"unverified provider host")
    entry={"resource":name,"url":url};R["transfers"].append(entry)
    for hop in range(2):
        with S.get(url,stream=True,timeout=(15,60),allow_redirects=False,headers={"Accept-Encoding":"identity"}) as q:
            entry["http"]=q.status_code;entry["retry_after"]=q.headers.get("Retry-After")
            if q.status_code in (401,403,429) or q.status_code>=500:raise Stop("HTTP "+str(q.status_code))
            if q.status_code in (301,302,303,307,308):
                need(hop==0,"redirect budget")
                url=urllib.parse.urljoin(url,q.headers["Location"]);need(allowed(url),"redirect outside provider")
                entry["redirect"]=url;continue
            need(q.status_code==200,"HTTP "+str(q.status_code))
            size=q.headers.get("Content-Length")
            if size is not None:need(int(size)<=cap,"declared size cap")
            data=bytearray()
            for chunk in q.iter_content(65536):
                data.extend(chunk);need(len(data)<=cap,"body size cap")
            if size is not None and q.headers.get("Content-Encoding","identity")=="identity":need(len(data)==int(size),"truncated")
            need(len(data)>0,"empty resource")
            entry.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),content_type=q.headers.get("Content-Type"))
            return bytes(data)
    raise ValueError("redirect exhausted")
def table_audit(b):
    s=None
    for enc in ("utf-8-sig","cp1252"):
        try:s=b.decode(enc);break
        except UnicodeError:pass
    need(s is not None and not s.lstrip().lower().startswith(("<html","<!doctype","{")),"not delimited text")
    dia=csv.Sniffer().sniff(s[:32768],delimiters=",;\t")
    rows=csv.reader(io.StringIO(s),dia);h=next(rows);need(len(h)>1 and len(set(h))==len(h),"invalid header")
    n=0;bad=0;miss=Counter();number=Counter();seen=Counter()
    for row in rows:
        if not row:continue
        n+=1
        if len(row)!=len(h):bad+=1;continue
        for k,v in zip(h,row):
            if v.strip().lower() in ("","na","nan","null","n/a"):miss[k]+=1;continue
            seen[k]+=1
            try:float(v);number[k]+=1
            except ValueError:pass
    need(n>0 and bad==0,"malformed or empty table")
    return {"rows":n,"columns":h,"delimiter":dia.delimiter,"missing":dict(miss),"numeric_nonmissing":dict(number),"nonmissing":dict(seen)}
def save_asset(name,b,kind):
    if kind=="csv":a=table_audit(b)
    elif kind=="pdf":
        need(b.startswith(b"%PDF-"),"PDF signature");a={"pdf_signature":True}
    else:
        need(not b.lstrip().lower().startswith((b"<html",b"<!doctype")),"HTML in script")
        a={"text_lines":len(b.decode("utf-8-sig",errors="replace").splitlines())}
    (O/name).write_bytes(b);R.setdefault("schemas",{})[name]=a
def swiss():
    base="https://www.envidat.ch/dataset/b64e697c-bef8-455f-a2ca-96e269fdfd1c/resource/"
    assets=[
        ("fielddata.csv","8b121238-5319-4a48-ad15-a0382e8e37f8/download/fielddata_2020-02-14_guilds.csv",16*M,"csv"),
        ("dictionary.csv","121b2a4d-d2a0-416e-bd23-3a744cb57b1b/download/variable-description_20220411.csv",2*M,"csv"),
        ("original_analysis.R","50bc0f40-a3ab-49d6-82bb-35ffe03d387f/download/r_script_publication_20220405.r",2*M,"text")]
    for name,path,cap,kind in assets:save_asset(name,get(base+path,cap,name),kind)
    R["status"]="SOURCE_BYTES_READY_REQUIRES_DESIGN_REVIEW"
def england():
    uid="5aab3da3-6074-48cc-9828-fa51d9972ee7"
    meta=get("https://ckan.publishing.service.gov.uk/api/3/action/package_show?id="+uid,2*M,"package")
    j=json.loads(meta);need(j.get("success") is True,"CKAN failure");d=j["result"]
    need(d["id"]==uid and d["title"].strip()=="National Woodland Bat Survey - Verified Bat Activity","package identity")
    rows=d["resources"];R["package"]={"id":d["id"],"title":d["title"],"license_id":d.get("license_id"),"metadata_modified":d.get("metadata_modified"),"resources":[{"id":x.get("id"),"name":x.get("name"),"format":x.get("format"),"url":x.get("url")} for x in rows]}
    selected=[]
    for name,cap,kind in [("National Woodland Bat Survey Evidence Pack 2021-24.pdf",32*M,"pdf"),("National Woodland Bat Survey Data 2021-24.csv",64*M,"csv")]:
        cand=[x for x in rows if str(x.get("name","")).strip().casefold()==name.casefold()]
        need(len(cand)==1,"unique official resource "+name);selected.append((name,cand[0]["url"],cap,kind))
    lim=[x for x in rows if "limitations" in str(x.get("name","")).lower() and (str(x.get("format","")).lower()=="pdf" or str(x.get("url","")).lower().split("?")[0].endswith(".pdf"))]
    need(len(lim)<=1,"ambiguous limits resource")
    if lim:selected.insert(0,("NCEA_limitations.pdf",lim[0]["url"],32*M,"pdf"))
    R["limitations_pdf_enumerated"]=bool(lim)
    for name,url,cap,kind in selected:save_asset(name,get(url,cap,name),kind)
    (O/"package.json").write_bytes(meta)
    R["status"]="SOURCE_BYTES_READY_REQUIRES_DESIGN_REVIEW"
try:
    {"swiss":swiss,"england":england}[mode]()
except Exception as e:
    R.update(status="STOP_SOURCE_OR_QC",error_type=type(e).__name__,reason=str(e)[:180])
finally:
    (O/"report.json").write_text(json.dumps(R,ensure_ascii=False,indent=2)+"\n")
    print("INDEPENDENT_SOURCE_REPORT="+json.dumps(R,ensure_ascii=False),flush=True)
