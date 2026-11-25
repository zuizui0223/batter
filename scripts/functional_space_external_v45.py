"""V45 official public API source recovery; bounded read-only, no outcome analysis."""
import concurrent.futures as cf,csv,hashlib,io,json,pathlib,re,struct,urllib.parse,zipfile
from bayer_field_join_v17 import fetch
from acoustic_foraging_source_v35 import inspect_csv
OUT=pathlib.Path("results/functional_space_external_v45.json")
Z="https://repository.zalf.de";D="https://datadryad.org"
UUID="98e9cf64-cd23-43c8-a9bf-c6c23831c4cf"
TITLE="Flexibility of social foraging behaviour in an insectivorous bat"
def url_same(u,base):
    u=urllib.parse.urljoin(base+"/",str(u))
    p=urllib.parse.urlsplit(u);b=urllib.parse.urlsplit(base)
    assert p.scheme=="https" and p.hostname==b.hostname and not p.username and not p.password
    assert not re.search(r"token|signature|credential|auth|secret|x-amz",p.query,re.I)
    return u
def get(u,limit=5_000_000):
    b,final=fetch(u,limit)
    return b,{"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}
def js(u):
    b,r=get(u);return json.loads(b),r
def links(x,base):
    out=[]
    for l in x.get("links",[]):
        if not isinstance(l,dict):continue
        row={k:l.get(k) for k in ("name","link_type","mime","extension","identifier")}
        u=l.get("url")
        if u:
            try:row["url"]=url_same(u,base)
            except Exception:row["external_or_restricted_url"]=True
        out.append(row)
    return out
def obj(d,key):
    v=d.get(key,d.get("resource",d))
    assert isinstance(v,dict)
    return v
def summary(x,base):
    row={k:x.get(k) for k in ("pk","id","uuid","title","name","alternate","resource_type","subtype","license","is_published","is_approved","perms","download_format","can_be_downloaded","store_type") if k in x}
    row["keys"]=sorted(x)
    row["links"]=links(x,base)
    for k in ("download_url","detail_url"):
        if x.get(k):
            try:row[k]=url_same(x[k],base)
            except Exception:row[k+"_external_or_restricted"]=True
    a=x.get("attribute_set")
    if isinstance(a,list):row["attribute_fields"]=[{k:v.get(k) for k in ("attribute","attribute_label","attribute_type","description")} for v in a if isinstance(v,dict)]
    return row
def ccby(x):
    return bool(re.search(r"cc[-_ ]?by(?:[-_ ]?4)?|attribution\s*4|creativecommons.org/licenses/by/4",json.dumps(x,ensure_ascii=False),re.I)) and not re.search(r"by[-_ ]?nc|by[-_ ]?nd|by[-_ ]?sa",json.dumps(x),re.I)
def dbf_fields(b):
    if len(b)<32:raise ValueError("short DBF")
    n=struct.unpack_from("<I",b,4)[0];h=struct.unpack_from("<H",b,8)[0]
    assert 32<=h<=len(b)
    fields=[]
    for i in range(32,h-1,32):
        if b[i]==13:break
        if i+32>h:break
        fields.append({"name":b[i:i+11].split(b"\0")[0].decode("ascii",errors="replace"),"type":chr(b[i+11]),"width":b[i+16],"decimals":b[i+17]})
    return {"records_declared":n,"fields":fields}
def inspect(b,name):
    if b.startswith(b"PK\x03\x04"):
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            m=z.infolist();assert len(m)<=200
            assert sum(x.file_size for x in m)<=100_000_000
            assert all(not x.filename.startswith(("/","\\")) and ".." not in pathlib.PurePosixPath(x.filename).parts for x in m)
            row={"members":[{"name":x.filename,"size":x.file_size} for x in m],"table_schemas":[]}
            for x in m:
                if x.file_size>8_000_000:continue
                suf=pathlib.PurePosixPath(x.filename).suffix.lower()
                try:
                    if suf==".dbf":a=dbf_fields(z.read(x))
                    elif suf in (".csv",".tsv"):a=inspect_csv(z.read(x))
                    else:continue
                    row["table_schemas"].append({"name":x.filename,"schema":a})
                except Exception as e:row["table_schemas"].append({"name":x.filename,"parse_error":type(e).__name__})
            return row
    if name.lower().endswith((".csv",".tsv")):return inspect_csv(b)
    return {"format":"other_or_unsupported","bytes":len(b)}
def roeleke():
    out={"doi":"10.4228/ZALF.DK.112","status":"REVIEW_REQUIRED"}
    d,r=js(Z+"/api/v2/resources/916/");x=obj(d,"resource")
    out["map_receipt"]=r;out["map"]=summary(x,Z)
    assert str(x.get("uuid","")).lower()==UUID or x.get("title")==TITLE,"resource identity mismatch"
    assert x.get("resource_type")=="map","not map"
    d,r=js(Z+"/api/v2/maps/916/datasets/?page_size=50")
    out["relation_receipt"]=r;out["relation_keys"]=sorted(d) if isinstance(d,dict) else ["list"]
    layers=d if isinstance(d,list) else d.get("datasets",d.get("results",[]))
    assert isinstance(layers,list) and len(layers)<=50
    out["linked_count"]=len(layers);out["layers"]=[];budget=20_000_000
    for a in layers:
        if not isinstance(a,dict):continue
        v=summary(a,Z);out["layers"].append(v)
        pk=a.get("pk",a.get("id"))
        if not isinstance(pk,int) and not (isinstance(pk,str) and pk.isdigit()):continue
        try:
            t,r=js(Z+"/api/v2/datasets/"+str(pk)+"/");z=obj(t,"dataset")
            v["detail"]=summary(z,Z);v["detail_receipt"]=r
            assert str(z.get("pk",z.get("id")))==str(pk)
            # Only direct downloadable source layers; no credential use or basemap exports.
            if not ccby(z.get("license")) or not z.get("is_published") or "download_resourcebase" not in (z.get("perms") or []) or not z.get("download_url"):
                v["download_status"]="NOT_ADMITTED_DOWNLOAD";continue
            if budget<=0:break
            u=url_same(z["download_url"],Z)
            b,rr=get(u,min(10_000_000,budget));budget-=len(b)
            v["download_receipt"]={**rr,"checksum_status":"export SHA256 only; no publisher digest"}
            v["export_schema"]=inspect(b,urllib.parse.urlsplit(u).path)
            v["download_status"]="PUBLIC_EXPORT_INSPECTED"
        except Exception as e:v["download_status"]="STOP_LAYER";v["error"]=repr(e)[:300]
    out["status"]="MAP_AND_LINKED_DATASET_METADATA"
    return out
def dryad():
    doi="10.5061/dryad.mgqnk993n";out={"doi":doi,"status":"REVIEW_REQUIRED"}
    d,r=js(D+"/api/v2/datasets/"+urllib.parse.quote("doi:"+doi,safe=""))
    assert str(d.get("identifier","")).lower() in (doi,"doi:"+doi)
    assert "nyctalus aviator" in d.get("title","").lower()
    out.update(title=d["title"],license=d.get("license"),version=d.get("versionNumber"),dataset_receipt=r)
    l=d.get("_links",{})
    out["link_names"]=sorted(l)
    # Official dataset response supplies current version or versions relation.
    v=l.get("stash:version",l.get("version"))
    if v:
        version,r=js(url_same(v["href"],D));out["version_receipt"]=r
    else:
        v=l.get("stash:versions",l.get("versions"))
        assert v,"no version link"
        a,r=js(url_same(v["href"],D));out["version_list_receipt"]=r
        rows=a.get("_embedded",{}).get("stash:versions",a.get("_embedded",{}).get("versions",[]))
        assert isinstance(rows,list) and rows
        version=max(rows,key=lambda v:int(v.get("versionNumber",0)))
        if not version.get("_links",{}).get("stash:files"):
            version,r=js(url_same(version["_links"]["self"]["href"],D))
    out["version_number"]=version.get("versionNumber")
    files=version.get("_links",{}).get("stash:files",version.get("_links",{}).get("files"))
    assert files,"no official file list link"
    a,r=js(url_same(files["href"],D));out["file_list_receipt"]=r
    f=a.get("_embedded",{}).get("stash:files",a.get("_embedded",{}).get("files",[]))
    assert isinstance(f,list) and len(f)<=100
    out["files"]=[];budget=20_000_000
    for x in f:
        name=x.get("path",x.get("filename",""));size=x.get("size")
        entry={k:x.get(k) for k in ("path","filename","size","mimeType","digest","digestType","status")}
        out["files"].append(entry)
        if not isinstance(size,int) or size>min(10_000_000,budget) or not str(name).lower().endswith((".csv",".tsv",".zip",".txt")):continue
        download=x.get("_links",{}).get("stash:download",x.get("_links",{}).get("download"))
        if not download:continue
        try:
            b,rr=get(url_same(download["href"],D),size);budget-=len(b);assert len(b)==size
            dg=x.get("digest");alg=str(x.get("digestType","")).lower().replace("-","")
            if dg:
                assert alg in ("md5","sha1","sha256","sha512")
                assert hashlib.new(alg,b).hexdigest().lower()==str(dg).lower()
            entry["receipt"]={**rr,"publisher_digest_verified":bool(dg)}
            entry["schema"]=inspect(b,str(name))
            entry["download_status"]="PUBLIC_FILE_INSPECTED"
        except Exception as e:entry["download_status"]="STOP_FILE";entry["error"]=repr(e)[:300]
    out["status"]="PRIMARY_ARCHIVE_INVENTORY"
    return out
def guarded(f):
    try:return f()
    except Exception as e:return {"status":"STOP","error":repr(e)[:500]}
def main():
    with cf.ThreadPoolExecutor(max_workers=2) as ex:a=list(ex.map(guarded,[roeleke,dryad]))
    return {"scope":"official documented public API recovery; no behavioral outcomes","roeleke":a[0],"niga_reserve":a[1],"stidsholt":{"status":"STOP_AUTOMATED_RETRIEVAL","reason":"public file listing failed; official file API documents OAuth2; no credentials used"}}
if __name__=="__main__":
    r=main();OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n");print(OUT.read_text())
