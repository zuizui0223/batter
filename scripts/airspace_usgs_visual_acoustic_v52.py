"""V52 USGS paired observation source inventory and structure, no ecological outcomes."""
import csv,io,json,hashlib,re
from collections import Counter
from pathlib import PurePosixPath
from urllib.parse import urlparse
from xml.etree import ElementTree as ET
import requests
from openpyxl import load_workbook
from roost_fd_source_audit_v2 import OUT
from airspace_schema_v41 import structure
DOI="10.5066/F7542MG1"
ITEMS={"release":("59725a0ee4b0ec1a4885ee40","acoustic and visual surveys"),
       "detections":("5bae6e45e4b08583a5d310ce","vocalization and visual detections"),
       "vocalization":("5bae6e07e4b08583a5d310c5","vocalization metrics")}
HEAD={"User-Agent":"batter-public-USGS-structure-audit/1.0"}
MAX_FILE=2_000_000;MAX_TOTAL=5_000_000
PAT=r"\b(?:visual\w*|acoustic\w*|video\w*|audio\w*|synchron\w*|detect\w*|distance\w*|proximity|near|mid|far|flight\w*|straight|curved|erratic|site\w*|night\w*|date\w*|time\w*|call\w*|pass\w*|event\w*|effort\w*|duration\w*|count\w*|presence|absence)\b"
def sha(b):return hashlib.sha256(b).hexdigest()
def get(url):
    r=requests.get(url,headers=HEAD,timeout=(10,30));r.raise_for_status();return r.json()
def safe_name(s):
    s=str(s or "")
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_. ()/-]{0,100}",s) and not re.search(r"\d{3,}|latitude|longitude|coordinates",s,re.I):return s
    return "field_"+sha(s.encode())[:12]
def status(e):
    x={"status":"blocked","error":type(e).__name__}
    if isinstance(e,requests.HTTPError) and e.response is not None:x["HTTP_status"]=e.response.status_code
    return x
def doc(b):
    root=ET.fromstring(b)
    fields=[]
    for node in root.iter():
        if node.tag.rsplit("}",1)[-1].lower()!="attr":continue
        vals={x.tag.rsplit("}",1)[-1].lower():(x.text or "") for x in node}
        label=vals.get("attrlabl","")
        desc=vals.get("attrdef","")
        if not label:continue
        fields.append({"field":safe_name(label),"semantic_tokens":sorted(set(m.group(0).lower() for m in re.finditer(PAT,label+" "+desc,re.I)))})
    return {"attribute_count":len(fields),"attribute_semantics":fields[:150]}
def tab(b,ext):
    if ext==".xml":return {"format":"FGDC_XML","schema":doc(b)}
    if ext==".xlsx":
        w=load_workbook(io.BytesIO(b),read_only=True,data_only=False)
        try:
            res=[]
            for i,s in enumerate(w.worksheets[:15]):
                it=s.values
                h=next(it,())
                res.append({"sheet_index":i,"schema":structure(h,it)})
            return {"format":"xlsx","sheets":res}
        finally:w.close()
    for enc in ("utf-8-sig","cp1252"):
        try:t=b.decode(enc);break
        except UnicodeDecodeError:continue
    else:raise ValueError("encoding")
    if ext==".txt":
        # No arbitrary text body emitted.
        return {"format":"text","line_count":len(t.splitlines()),"semantic_tokens":dict(Counter(m.group(0).lower() for m in re.finditer(PAT,t,re.I)))}
    try:d=csv.Sniffer().sniff(t[:20000],delimiters=",;\t")
    except csv.Error:d=csv.excel_tab if ext==".tsv" else csv.excel
    r=csv.reader(io.StringIO(t,newline=""),d);h=next(r)
    return {"format":"delimited","delimiter":repr(d.delimiter),"encoding":enc,"schema":structure(h,r)}
def fsize(f):
    for k in ("size","contentLength","length"):
        try:
            n=int(f.get(k))
            if n>=0:return n
        except (ValueError,TypeError):pass
    return None
def check(f,b):
    # Only verify advertised algorithm-tagged digests, or unambiguously named MD5/SHA fields.
    hashes={}
    for k in ("md5","sha256"):
        v=f.get(k)
        if isinstance(v,str) and re.fullmatch(r"[0-9a-fA-F]{32}" if k=="md5" else r"[0-9a-fA-F]{64}",v):
            assert hashlib.new(k,b).hexdigest()==v.lower()
            hashes[k]=v.lower()
    v=f.get("checksum")
    if isinstance(v,dict):
        alg=str(v.get("type") or v.get("algorithm") or "").lower().replace("-","")
        value=v.get("value") or v.get("hash")
        if alg in ("md5","sha1","sha256") and isinstance(value,str):
            assert hashlib.new(alg,b).hexdigest()==value.lower()
            hashes[alg]=value.lower()
    elif isinstance(v,str) and re.fullmatch(r"[0-9a-fA-F]{32}",v):
        assert hashlib.md5(b).hexdigest()==v.lower();hashes["md5"]=v.lower()
    return hashes
def main():
    dest=OUT/"audit_v52_usgs_visual_acoustic.json"
    out={"status":"structure_only","doi":DOI,"ecological_outcomes_analyzed":False,"source_code_executed":False,"items":{}}
    def save():dest.write_text(json.dumps(out,indent=2,allow_nan=False))
    save()
    try:
        j=get("https://api.datacite.org/dois/"+DOI)["data"]["attributes"]
        assert j["doi"].casefold()==DOI.casefold()
        out["datacite"]={"status":"metadata","titles":[x.get("title") for x in j.get("titles",[])],"publisher":j.get("publisher"),"landing_host":urlparse(j.get("url") or "").hostname}
    except Exception as e:out["datacite"]=status(e)
    total=0
    for tag,(id,phrase) in ITEMS.items():
        q={"item_id":id,"files":[]}
        out["items"][tag]=q
        try:
            j=get("https://www.sciencebase.gov/catalog/item/"+id+"?format=json")
            assert j["id"]==id and phrase in j["title"].casefold()
            q.update(status="metadata",title=j["title"],parent_matches_release=(j.get("parentId")==ITEMS["release"][0]),has_children=j.get("hasChildren"))
            ff=j.get("files") or []
            for f in ff:
                name=str(f.get("name") or "")
                ext=PurePosixPath(name).suffix.lower()
                n=fsize(f)
                u=f.get("downloadUri") or f.get("url")
                r={"name":safe_name(name),"extension":ext,"size_bytes":n,"download_link_advertised":isinstance(u,str) and bool(u),"metadata_keys":sorted(f.keys())}
                q["files"].append(r)
                if ext not in (".csv",".tsv",".txt",".xlsx",".xml"):
                    r["status"]="metadata_only_other_extension";continue
                if n is None or n>MAX_FILE or total+n>MAX_TOTAL:
                    r["status"]="metadata_only_size_gate";continue
                if not isinstance(u,str) or urlparse(u).scheme!="https" or not (urlparse(u).hostname or "").endswith((".usgs.gov",".sciencebase.gov")):
                    r["status"]="metadata_only_link_gate";continue
                try:
                    data=bytearray()
                    with requests.get(u,headers=HEAD,stream=True,timeout=(15,60)) as rr:
                        rr.raise_for_status()
                        for c in rr.iter_content(65536):
                            data.extend(c)
                            if len(data)>n or len(data)>MAX_FILE:raise ValueError("size cap")
                    b=bytes(data);assert len(b)==n
                    r["published_hashes_verified"]=check(f,b);r["sha256_download_receipt"]=sha(b);total+=len(b)
                    r["schema"]=tab(b,ext);r["status"]="inspected"
                except Exception as e:r.update(status(e))
        except Exception as e:q.update(status(e))
        save()
    out["bytes_downloaded"]=total
    save();print(dest.read_text())
    return 0 if any(q.get("status")=="metadata" for q in out["items"].values()) else 2
if __name__=="__main__":raise SystemExit(main())
