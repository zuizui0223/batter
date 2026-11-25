"""Bounded public link diagnosis for NABat's dated Parquet release.
Only official public file endpoints and paths explicitly returned by metadata.
No sign-in, token guessing, or bypass of access restrictions.
"""
import hashlib,html,json,pathlib,re
from urllib.parse import urlparse,urljoin
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
    except Exception as e:a["error"]=type(e).__name__
    finally:R["probes"].append(a);save()
    return a
def main():
    x=requests.get(ITEM,timeout=(15,40));x.raise_for_status();j=x.json()
    f=[v for v in j["files"] if v.get("name","").endswith(".parquet") and "20260925" in v["name"]]
    assert len(f)==3
    R["inventory_fields"]=[{"name":v["name"],"size":v["size"],"metadata_keys":sorted(v),"url_fields":[{"key":k,"url":safe(w)} for k,w in v.items() if isinstance(w,str) and w.startswith("https://")]} for v in f]
    save()
    for v in f:
        urls=[v["url"]]
        for k,w in v.items():
            if isinstance(w,str) and w.startswith("https://") and k.lower() in {"downloadurl","downloaduri","directurl","directdownloadurl","url"}:urls.append(w)
        for u in dict.fromkeys(urls):
            a=probe(u,v["size"])
            if a.get("confirmed_file_range"):break
    R["status"]="FILE_RANGE_ROUTE_READY" if any(a.get("confirmed_file_range") for a in R["probes"]) else "PUBLIC_LINK_TRANSPORT_UNRESOLVED"
    save()
if __name__=="__main__":
    try:main()
    except Exception as e:R.update(status="INCOMPLETE",error_type=type(e).__name__);save();raise
