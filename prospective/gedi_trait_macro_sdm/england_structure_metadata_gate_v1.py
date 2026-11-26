"""Official catalogue only. No raster download or ecological fit."""
import hashlib,json,pathlib,re,urllib.parse
from html.parser import HTMLParser
import requests
O=pathlib.Path("england_structure_metadata");O.mkdir(exist_ok=True)
R={"status":"START","ecological_fit":False,"transfers":[]}
S=requests.Session()
def require(t,m):
    if not t:raise ValueError(m)
def allowed(u):
    p=urllib.parse.urlparse(u);h=p.hostname or ""
    return p.scheme=="https" and not p.username and not p.password and (h.endswith(".gov.uk") or h=="gov.uk" or h.endswith(".arcgis.com") or h=="arcgis.com" or h.endswith(".arcgisusercontent.com"))
def fetch(u,name,cap=8*1024**2):
    require(allowed(u),"unverified host")
    rec={"resource":name,"url":u};R["transfers"].append(rec)
    for hop in range(3):
        with S.get(u,stream=True,timeout=(15,45),allow_redirects=False,headers={"Accept-Encoding":"identity"}) as q:
            rec["http"]=q.status_code
            if q.status_code in (401,403,429) or q.status_code>=500:raise RuntimeError("STOP_HTTP_"+str(q.status_code))
            if q.status_code in (301,302,303,307,308):
                u=urllib.parse.urljoin(u,q.headers["Location"]);require(allowed(u),"unverified redirect");rec.setdefault("redirects",[]).append(u);continue
            require(q.status_code==200,"HTTP "+str(q.status_code));n=q.headers.get("Content-Length")
            if n is not None:require(int(n)<=cap,"size cap")
            b=bytearray()
            for part in q.iter_content(65536):
                b.extend(part);require(len(b)<=cap,"body cap")
            if n is not None and q.headers.get("Content-Encoding","identity")=="identity":require(int(n)==len(b),"truncation")
            rec.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),content_type=q.headers.get("Content-Type"))
            return bytes(b)
    raise RuntimeError("redirect budget")
def save_json(name,b):
    j=json.loads(b);(O/name).write_bytes(b);return j
class Links(HTMLParser):
    def __init__(self):super().__init__();self.urls=[]
    def handle_starttag(self,t,a):
        for k,v in a:
            if k in ("href","src") and v:self.urls.append(v)
try:
    uid="7ac16040-f61f-4ace-9c07-22945e6d0292"
    d=save_json("package.json",fetch("https://ckan.publishing.service.gov.uk/api/3/action/package_show?id="+uid,"catalogue"))
    require(d.get("success") is True,"catalogue failure");d=d["result"];require(d["id"]==uid and d["title"].strip().casefold()=="woodland structure in england","catalogue identity")
    rows=[{"name":x.get("name"),"url":x.get("url"),"format":x.get("format"),"id":x.get("id")} for x in d["resources"]];R["resources"]=rows
    # Metadata links may carry a published ArcGIS Hub item ID. Query the public item only if explicitly present.
    ids=set()
    for x in rows:
        u=x["url"] or "";p=urllib.parse.urlparse(u)
        if allowed(u) and "arcgis.com" in (p.hostname or ""):
            ids.update(re.findall(r"(?i)(?<![a-f0-9])[a-f0-9]{32}(?![a-f0-9])",u))
    R["catalogue_item_ids"]=sorted(ids);require(len(ids)<=4,"metadata item budget")
    R["items"]=[]
    for i in sorted(ids):
        u="https://www.arcgis.com/sharing/rest/content/items/"+i
        m=save_json(i+".json",fetch(u+"?f=json","public item metadata"))
        require(m.get("id","").lower()==i.lower() and m.get("access")=="public","public item identity/access")
        links=Links();links.feed(m.get("description") or "");links.feed(m.get("snippet") or "")
        R["items"].append({"id":i,"title":m.get("title"),"type":m.get("type"),"owner":m.get("owner"),"url":m.get("url"),"size":m.get("size"),"accessInformation":m.get("accessInformation"),"licenseInfo":m.get("licenseInfo"),"links":links.urls})
    R["status"]="CATALOGUE_READY_ASSET_REVIEW_REQUIRED"
except Exception as e:R.update(status="STOP_SOURCE_OR_QC",error_type=type(e).__name__,reason=str(e)[:240])
finally:
    (O/"report.json").write_text(json.dumps(R,indent=2,ensure_ascii=False)+"\n")
    print("ENGLAND_STRUCTURE_REPORT="+json.dumps(R,ensure_ascii=False))
