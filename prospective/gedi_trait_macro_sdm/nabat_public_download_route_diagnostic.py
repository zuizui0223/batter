"""Bounded public link diagnosis for NABat's dated Parquet release.
Only official public file endpoints and paths explicitly returned by metadata.
No sign-in, token guessing, or bypass of access restrictions.
"""
import hashlib,html,json,pathlib,re
from urllib.parse import urlparse,urljoin,quote
import requests
OUT=pathlib.Path("nabat_route_diagnostic");OUT.mkdir(exist_ok=True)
ITEM="https://www.sciencebase.gov/catalog/item/6ace802b1ba49b69a5819e47?format=json"
R={"stage":"public file transport diagnosis, no source counts or ecological fit","doi":"10.5066/P1HDZNY9","status":"START","probes":[]}
def safe(u):
    p=urlparse(u);return p.scheme+"://"+p.netloc+p.path
def save():
    (OUT/"report.json").write_text(json.dumps(R,indent=2))
    print("NABAT_ROUTE_REPORT="+json.dumps(R),flush=True)
def probe(u,expected):
    a={"url":safe(u),"expected_bytes":expected}
    try:
        with requests.get(u,stream=True,timeout=(15,35),headers={"Range":"bytes=0-4095","Accept-Encoding":"identity","User-Agent":"batter-public-research/1.0"}) as q:
            a.update(http=q.status_code,final_url=safe(q.url),content_type=q.headers.get("Content-Type"),content_range=q.headers.get("Content-Range"),content_length=q.headers.get("Content-Length"))
            if q.status_code in (401,403):a["status"]="ACCESS_STOP";return a
            if q.status_code not in (200,206):return a
            v=q.raw.read(4096)
            a["prefix_bytes"]=len(v);a["prefix_sha256"]=hashlib.sha256(v).hexdigest();a["parquet_magic"]=v[:4]==b"PAR1"
            if not a["parquet_magic"]:
                s=v.decode("utf8",errors="replace")
                a["html_title"]=(re.findall(r"<title>(.*?)</title>",s,re.I|re.S) or [""])[0][:140]
                a["html_shell"]=bool(re.search(r"<!doctype html|<html",s,re.I))
                a["public_link_hosts"]=sorted(set(urlparse(html.unescape(x)).netloc for x in re.findall(r"https?://[^\s\"'<>]+",s) if urlparse(html.unescape(x)).netloc))[:15]
            a["confirmed_file_range"]=a["parquet_magic"] and q.status_code==206 and bool(a["content_range"]) and a["content_range"].endswith("/"+str(expected))
            a["confirmed_full_file_header"]=a["parquet_magic"] and q.status_code==200 and a["content_length"]==str(expected)
    except Exception as e:a["error"]=type(e).__name__
    finally:R["probes"].append(a);save()
    return a
def main():
    x=requests.get(ITEM,timeout=(15,40));x.raise_for_status();j=x.json()
    f=[v for v in j["files"] if v.get("name","").endswith(".parquet") and "20260925" in v["name"]]
    assert len(f)==3
    R["inventory_fields"]=[{"name":v["name"],"size":v["size"],"metadata_keys":sorted(v),"url_fields":[{"key":k,"url":safe(w)} for k,w in v.items() if isinstance(w,str) and w.startswith("https://")]} for v in f]
    save()
    # The file-manager and its downloadUri both served the same 4255-byte
    # HTML shell in run 45713866921. Do not repeat those endpoints.
    # Inspect the *published catalog* S3 object descriptors and try only
    # anonymous GETs of explicitly enumerated objects. If access is denied,
    # stop. No credentialed S3 use, guessed object keys or private API calls.
    R["object_descriptors"]=[]
    for v in f:
        urls=[];descriptors=[]
        def add_object(obj):
            if not isinstance(obj,dict):return
            bucket=obj.get("bucket") or obj.get("bucketName")
            key=obj.get("key") or obj.get("objectKey")
            if isinstance(bucket,str) and isinstance(key,str) and re.fullmatch(r"[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]",bucket):
                # Object path must identify the exact public named release.
                if key.endswith("/"+v["name"]) or key==v["name"]:
                    u="https://"+bucket+".s3.amazonaws.com/"+quote(key,safe="/")
                    urls.append(u);descriptors.append({"bucket":bucket,"object_name":v["name"],"explicit_key":True})
            for k,w in obj.items():
                if isinstance(w,str) and k.lower() in {"url","downloadurl","presignedurl","signedurl","publicurl","s3url","uri","downloaduri"}:
                    p=urlparse(w)
                    if p.scheme=="https" and p.hostname and (p.hostname.endswith(".amazonaws.com") or p.hostname=="s3.amazonaws.com"):
                        # Only URLs explicitly returned by official metadata.
                        if p.path.endswith("/"+v["name"]) or p.path.endswith("/"+quote(v["name"])):
                            urls.append(w);descriptors.append({"published_url":safe(w)})
        add_object(v)
        add_object(v.get("s3Object"))
        add_object(v.get("originalMetadata"))
        if isinstance(v.get("s3Object"),str) and v["s3Object"].startswith("s3://"):
            p=urlparse(v["s3Object"])
            if p.path.endswith("/"+v["name"]) and re.fullmatch(r"[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]",p.netloc):
                urls.append("https://"+p.netloc+".s3.amazonaws.com/"+quote(p.path.lstrip("/"),safe="/"))
        R["object_descriptors"].append({"name":v["name"],"descriptor_types":{k:type(v.get(k)).__name__ for k in ["bucket","key","s3Object","originalMetadata"]},"object_keys":sorted(v["s3Object"]) if isinstance(v.get("s3Object"),dict) else [],"descriptors":descriptors,"candidate_routes":len(set(urls))})
        save()
        for u in dict.fromkeys(urls):
            a=probe(u,v["size"])
            if a.get("confirmed_file_range") or a.get("confirmed_full_file_header"):break
    R["status"]="FILE_ROUTE_READY" if any(a.get("confirmed_file_range") or a.get("confirmed_full_file_header") for a in R["probes"]) else "PUBLIC_OBJECT_ROUTE_UNRESOLVED"
    save()
if __name__=="__main__":
    try:main()
    except Exception as e:R.update(status="INCOMPLETE",error_type=type(e).__name__);save();raise
