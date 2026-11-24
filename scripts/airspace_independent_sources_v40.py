"""V40 public metadata inventory only; no ecological outcomes or file downloads."""
import json,re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote
from pathlib import Path
import requests
from roost_fd_source_audit_v2 import OUT

def get(url,params=None):
    r=requests.get(url,params=params,headers={"Accept":"application/json","User-Agent":"batter-3d-source-metadata/1.0"},timeout=(10,25))
    r.raise_for_status()
    return r.json()
def fmeta(name,size,checksum=None):
    # Filenames here are public archive objects, not paths to field observations.
    name=str(name or "")
    return {"name":name if not re.search(r"\d{4}[-_]\d\d[-_]\d\d|(?:lat|lon)[_-]?\d",name,re.I) else "[redacted filename]",
      "size":size,"checksum":checksum,"schema_candidate":bool(re.search(r"\.(?:csv|tsv|mat|xlsx|rds|npz|npy|las|laz|ply|pcd|zip|7z|json|txt|r|m)$",name,re.I))}
def figshare(i,v=None):
    url=f"https://api.figshare.com/v2/articles/{i}"+(f"/versions/{v}" if v is not None else "")
    j=get(url)
    return {"status":"metadata","id":i,"title":j.get("title"),"doi":j.get("doi"),"version":j.get("version"),
      "license":(j.get("license") or {}).get("name"),"files":[fmeta(f.get("name"),f.get("size"),f.get("computed_md5") or f.get("supplied_md5")) for f in j.get("files",[])]}
def zenodo(i):
    j=get(f"https://zenodo.org/api/records/{i}")
    m=j.get("metadata",{})
    return {"status":"metadata","id":i,"title":m.get("title"),"doi":m.get("doi"),"version":m.get("version"),"access_right":m.get("access_right"),"license":m.get("license"),
      "files":[fmeta(f.get("key"),f.get("size"),f.get("checksum")) for f in j.get("files",[])]}
def dryad(doi):
    j=get("https://datadryad.org/api/v2/datasets/"+quote("doi:"+doi,safe=""))
    out={"status":"metadata","title":j.get("title"),"identifier":j.get("identifier"),"files":[]}
    v=j.get("_links",{}).get("stash:version",{}).get("href")
    if v:
        vv=get(v if v.startswith("http") else "https://datadryad.org"+v)
        f=vv.get("_links",{}).get("stash:files",{}).get("href")
        if f:
            a=get(f if f.startswith("http") else "https://datadryad.org"+f)
            out["files"]=[fmeta(x.get("path"),x.get("size"),x.get("digest")) for x in a.get("_embedded",{}).get("stash:files",[])]
    return out
def crossref(doi):
    m=get("https://api.crossref.org/works/"+quote(doi,safe=""))["message"]
    return {"status":"metadata","title":m.get("title"),"doi":m.get("DOI"),"relation":m.get("relation"),"link_types":[{"content_type":x.get("content-type"),"URL":x.get("URL")} for x in m.get("link",[])],
      "dataset_references":[{"DOI":x.get("DOI"),"article-title":x.get("article-title"),"unstructured":str(x.get("unstructured",""))[:200]} for x in m.get("reference",[]) if re.search(r"zenodo|figshare|dryad|dataset|data set|osf.io|github",json.dumps(x),re.I)][:25]}
def datacite(title,author):
    j=get("https://api.datacite.org/dois",{"query":f'titles.title:"{title}" AND creators.name:{author}',"page[size]":20})
    out=[]
    for x in j.get("data",[]):
        a=x.get("attributes",{})
        out.append({"doi":a.get("doi"),"title":a.get("titles"),"url":a.get("url"),"type":a.get("types",{}).get("resourceTypeGeneral"),"version":a.get("version"),"related_identifiers":a.get("relatedIdentifiers")})
    return {"status":"metadata","total":j.get("meta",{}).get("total"),"records":out}
TASKS={
 "omalley_v3":lambda:figshare(26124277,3),
 "nagy":lambda:figshare(31112509),
 "diebold":lambda:zenodo(13857870),
 "barre":lambda:zenodo(10149959),
 "corcoran_weller":lambda:dryad("10.5061/dryad.pc1q122"),
 "umadi":lambda:zenodo(21834638),
 "teshima_crossref":lambda:crossref("10.1098/rspb.2026.1463"),
 "teshima_datacite":lambda:datacite("Evidence for latent regularities in echolocation-guided flight behaviour of bats","Teshima"),
 "aoki_crossref":lambda:crossref("10.1016/j.anbehav.2026.123669"),
 "aoki_datacite":lambda:datacite("Head–beam coordination in FM and CF-FM bats reveals distinct echolocation strategies during obstacle avoidance flight","Aoki")
}
def safe(f):
    try:return f()
    except requests.HTTPError as e:return {"status":"blocked","error":"HTTPError","http_status":e.response.status_code if e.response is not None else None}
    except Exception as e:return {"status":"blocked","error":type(e).__name__}
def main():
    out={"status":"metadata_only","source_bytes_downloaded":False,"ecological_outcomes_read":False,"sources":{}}
    dest=OUT/"audit_v40_independent_airspace_sources.json"
    def save():dest.write_text(json.dumps(out,indent=2,allow_nan=False))
    save()
    with ThreadPoolExecutor(max_workers=5) as pool:
        ff={k:pool.submit(safe,f) for k,f in TASKS.items()}
        for k,f in ff.items():out["sources"][k]=f.result();save()
    print(dest.read_text())
if __name__=="__main__":main()
