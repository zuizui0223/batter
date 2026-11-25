"""V44 public source recovery, no outcome fit or raw record export."""
import concurrent.futures as cf,csv,hashlib,io,json,pathlib,re,urllib.parse,zipfile
from html.parser import HTMLParser
from bayer_field_join_v17 import fetch
from acoustic_foraging_source_v35 import inspect_csv
OUT=pathlib.Path("results/functional_space_external_v44.json")
def js(url):return json.loads(fetch(url,5_000_000)[0])
def public_link(s,base):
    u=urllib.parse.urljoin(base,str(s))
    p=urllib.parse.urlsplit(u)
    if p.scheme!="https" or not p.hostname or p.username or p.password:return None
    # Never expose credentials or temporary signatures in logs.
    if re.search(r"token|signature|credential|auth|secret|x-amz",p.query,re.I):return None
    return u
class Links(HTMLParser):
    def __init__(self,base):super().__init__();self.base=base;self.links=[];self.meta=[];self.ld=False;self.parts=[];self.schemas=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ("a","link","script"):
            v=a.get("href",a.get("src"))
            if v:
                u=public_link(v,self.base)
                if u and re.search(r"download|\.csv|\.zip|\.mat|\.json|/api/|files|catalogue|\.js(?:\?|$)",u,re.I):
                    self.links.append({"tag":tag,"url":u,"rel":a.get("rel"),"download":bool("download" in a)})
        if tag=="meta" and re.search(r"citation|dc\.|og:|schema",a.get("name",a.get("property","")),re.I):
            key=a.get("name",a.get("property",""));v=a.get("content","")
            if re.search("title|identifier|doi|url|type",key,re.I) and len(v)<500:self.meta.append([key,v])
        if tag=="script" and a.get("type")=="application/ld+json":self.ld=True;self.parts=[]
    def handle_data(self,data):
        if self.ld:self.parts.append(data)
    def handle_endtag(self,tag):
        if tag=="script" and self.ld:
            self.ld=False
            try:
                d=json.loads("".join(self.parts));self.schemas.append(schema(d))
            except Exception:pass
def schema(d,depth=0):
    if depth>=3:return type(d).__name__
    if isinstance(d,dict):return {k:schema(v,depth+1) for k,v in list(d.items())[:40]}
    if isinstance(d,list):return {"length":len(d),"first":schema(d[0],depth+1) if d else None}
    return type(d).__name__
def html(url):
    try:
        b,final=fetch(url,5_000_000);p=Links(final);p.feed(b.decode("utf-8",errors="replace"))
        return {"status":"RETRIEVED","final_url":public_link(final,url),"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest(),"publisher_links":p.links[:70],"metadata":p.meta[:25],"jsonld_structure":p.schemas[:6]}
    except Exception as e:return {"status":"STOP_HTML","error":repr(e)}
def roeleke():
    doi="10.4228/ZALF.DK.112";d=js("https://api.datacite.org/dois/"+doi)["data"]["attributes"]
    assert d["doi"].lower()==doi.lower()
    assert d["titles"][0]["title"]=="Flexibility of social foraging behaviour in an insectivorous bat"
    assert any("creativecommons.org/licenses/by/4.0" in x.get("rightsUri","") for x in d["rightsList"])
    landing=d["url"];assert landing=="https://repository.zalf.de/catalogue/uuid/98e9cf64-cd23-43c8-a9bf-c6c23831c4cf"
    return {"status":"EXACT_ARTICLE_LINK_CONFIRMED","doi":doi,"title":d["titles"],"landing":html(landing),"alternate_identifiers":d.get("alternateIdentifiers",[]),"descriptions":d.get("descriptions",[])[:2]}
def collect_files(x,out):
    if isinstance(x,list):
        for a in x:collect_files(a,out)
    elif isinstance(x,dict):
        if any(k in x for k in ("filename","name","file_name")):
            row={k:x[k] for k in ("filename","name","file_name","id","size","content_type","type","folder_id","parent_id") if k in x and isinstance(x[k],(str,int,float,bool,type(None)))}
            cd=x.get("content_details",{})
            if isinstance(cd,dict):row["content_details"]={k:cd[k] for k in ("sha256_hash","size","content_type","checksum") if k in cd}
            out.append(row)
        for k,v in x.items():
            if isinstance(v,(list,dict)):collect_files(v,out)
def stidsholt():
    out={"doi":"10.17632/smx7n93syw.1"}
    try:
        d=js("https://data.mendeley.com/public-api/datasets/smx7n93syw/files?version=1")
        rows=[];collect_files(d,rows)
        out.update(status="PUBLIC_API_INSPECTED",response_schema=schema(d),file_or_folder_metadata=rows[:100])
    except Exception as e:out.update(status="STOP_FILE_API",error=repr(e))
    out["landing"]=html("https://data.mendeley.com/datasets/smx7n93syw/1")
    return out
def table_header(b,name):
    s=b.decode("utf-8-sig",errors="strict")
    if not name.lower().endswith((".csv",".tsv")):
        return {"line_count":len(s.splitlines()),"documentation_keywords":{k:len(re.findall(p,s,re.I)) for k,p in {"buzz":"buzz|attack","time":"timestamp|time","location":"latitude|longitude|GPS","effort":"duty.cycle|sampling|recording|effort"}.items()}}
    return inspect_csv(b)
def niga():
    out={"doi":"10.5061/dryad.mgqnk993n","mirror_doi":"10.5281/zenodo.7546169"}
    try:
        m=js("https://api.datacite.org/dois/"+out["doi"])["data"]["attributes"]
        assert any(r.get("relatedIdentifier")=="10.5281/zenodo.7546169" and r.get("relationType")=="IsSourceOf" for r in m["relatedIdentifiers"])
        z=js("https://zenodo.org/api/records/7546169")
        assert z["id"]==7546169
        meta=z["metadata"];doi=z.get("doi",meta.get("doi"))
        assert doi in (out["doi"],out["mirror_doi"]) or z.get("conceptdoi")==out["mirror_doi"]
        assert "nyctalus aviator" in meta["title"].lower()
        lic=meta.get("license",meta.get("rights"))
        assert re.search(r"cc[- ]?(?:by|zero|0)",json.dumps(lic),re.I)
        out.update(status="MIRROR_VERIFIED",title=meta["title"],license=lic,record_doi=doi,files=[])
        budget=20_000_000
        for f in z["files"]:
            name=f["key"];size=int(f["size"]);entry={"name":name,"size":size,"checksum":f.get("checksum")};out["files"].append(entry)
            if size>10_000_000 or size>budget or not name.lower().endswith((".csv",".tsv",".txt",".md",".zip")):continue
            try:
                assert f["checksum"].startswith("md5:")
                u="https://zenodo.org/api/records/7546169/files/"+urllib.parse.quote(name,safe="")+"/content"
                b,_=fetch(u,size);budget-=len(b)
                assert len(b)==size and hashlib.md5(b).hexdigest()==f["checksum"][4:]
                entry.update(status="HASH_VERIFIED",sha256=hashlib.sha256(b).hexdigest())
                if name.lower().endswith(".zip"):
                    zz=zipfile.ZipFile(io.BytesIO(b));members=zz.infolist()
                    assert sum(x.file_size for x in members)<=100_000_000
                    assert all(not x.filename.startswith(("/","\\")) and ".." not in pathlib.PurePosixPath(x.filename).parts for x in members)
                    entry["members"]=[{"name":x.filename,"bytes":x.file_size} for x in members[:150]]
                    for x in members[:150]:
                        if x.file_size<=2_000_000 and x.filename.lower().endswith((".csv",".tsv",".txt",".md")):
                            try:entry.setdefault("member_schemas",[]).append({"name":x.filename,"schema":table_header(zz.read(x),x.filename)})
                            except Exception as e:entry.setdefault("parse_errors",[]).append({"name":x.filename,"error":type(e).__name__})
                else:entry["schema"]=table_header(b,name)
            except Exception as e:entry.update(status="STOP_FILE",error=repr(e))
    except Exception as e:out.update(status="STOP_MIRROR",error=repr(e))
    return out
def safe_run(fn):
    try:return fn()
    except Exception as e:return {"status":"STOP","error":repr(e)}
def main():
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        x=list(ex.map(safe_run,[roeleke,stidsholt,niga]))
    return {"scope":"bounded public source recovery; no numerical outcome fit","roeleke":x[0],"stidsholt":x[1],"niga":x[2]}
if __name__=="__main__":
    r=main();OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n");print(OUT.read_text())
