"""Public metadata and trait source acquisition only. No fitted ecological outcomes."""
import csv
import hashlib
import io
import json
import pathlib
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone

OUT = pathlib.Path("gedi_source_gate")
OUT.mkdir(exist_ok=True)
report = {"checked_utc": datetime.now(timezone.utc).isoformat(), "stage": "source-only; counts are not eligible model rows", "sources": {}, "errors": {}}

def get(url, data=None, limit=32_000_000):
    headers = {"User-Agent": "batter-gedi-source-gate/1.0", "Accept": "application/json, text/csv, */*"}
    if data is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(data).encode()
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=35) as response:
        raw = response.read(limit+1)
        if len(raw) > limit:
            raise ValueError("response exceeds bounded acquisition limit")
        return raw

def js(url, data=None):
    return json.loads(get(url, data))

def save(name, data):
    (OUT / name).write_bytes(data)
    return {"file": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}

def api(root, href):
    return urllib.parse.urljoin(root, href)

def embedded(d, key):
    return d.get("_embedded", {}).get(key, [])

def link(d, key):
    return d.get("_links", {}).get(key, {}).get("href")

def dryad(doi, target=None):
    root = "https://datadryad.org/"
    d = js(root+"api/v2/datasets/"+urllib.parse.quote("doi:"+doi, safe=""))
    vurl = link(d, "stash:version")
    if not vurl:
        versions = js(api(root, link(d,"stash:versions")))
        items = embedded(versions,"stash:versions")
        if not items:
            raise ValueError("no explicit version metadata")
        v = items[0]
    else:
        v = js(api(root,vurl))
    f = js(api(root,link(v,"stash:files")))
    items = embedded(f,"stash:files")
    result = {"doi": doi, "title": d.get("title"), "version": v.get("versionNumber"), "version_id": v.get("id"), "files": [{"id":i.get("id"),"path":i.get("path"),"size":i.get("size"),"download":link(i,"stash:download")} for i in items]}
    if target:
        matches = [i for i in items if pathlib.PurePosixPath(i.get("path","")).name==target]
        if len(matches)!=1:
            raise ValueError("target not unique in file listing")
        try:
            href=link(matches[0],"stash:download")
            if not href:
                raise ValueError("no authenticated metadata download link")
            raw=get(api(root,href),limit=2_000_000)
            rows=list(csv.reader(io.StringIO(raw.decode("utf-8-sig"))))
            if len(rows)<2 or len(rows[0])<2:
                raise ValueError("not plausible CSV")
            result["raw_trait_csv"]={**save(target,raw),"columns":rows[0],"data_rows":len(rows)-1}
        except Exception as e:
            result["raw_file_error"]=str(e)
            result["next"]="Dryad API requires authentication; do not bypass access controls"
    return result

def gedi():
    params={"collection_concept_id":"C3043630107-ORNL_CLOUD","page_size":2000}
    j=js("https://cmr.earthdata.nasa.gov/search/granules.json?"+urllib.parse.urlencode(params))
    entries=j.get("feed",{}).get("entry",[])
    if not entries:
        raise ValueError("empty CMR inventory")
    result=[]
    for e in entries:
        result.append({"title":e.get("title"),"producer_granule_id":e.get("producer_granule_id"),"links":[l.get("href") for l in e.get("links",[]) if l.get("href")]})
    file=save("gedi_cmr_inventory.json",json.dumps(result,indent=2).encode())
    return {"doi":"10.3334/ORNLDAAC/2339","collection":params["collection_concept_id"],"granules_returned":len(entries),"inventory":file,"profile_candidates":[x["title"] for x in result if re.search("pavd|rh.?98|pai",str(x["title"]),re.I)][:40],"note":"Metadata only: actual raster bytes, authentication, masks and shot counts not checked."}

def euro():
    d=[js("https://api.figshare.com/v2/articles/21777161")]
    out=[]
    for x in d:
        if x.get("id")==21777161:
            a=js("https://api.figshare.com/v2/articles/"+str(x["id"]))
            item={"id":a.get("id"),"title":a.get("title"),"doi":a.get("doi"),"version":a.get("version"),"files":[{"name":f.get("name"),"size":f.get("size"),"downloadUrl":f.get("downloadUrl"),"computed_md5":f.get("computed_md5")} for f in a.get("files",[])]}
            for f in a.get("files",[]):
                if f.get("size",0)>20_000_000 or not f.get("downloadUrl"):
                    continue
                try:
                    raw=get(f["downloadUrl"],limit=20_000_000)
                    md5=hashlib.md5(raw).hexdigest()
                    if f.get("computed_md5") and md5!=f["computed_md5"]:
                        raise ValueError("MD5 mismatch")
                    item.setdefault("acquired",[]).append(save("euro_"+pathlib.PurePath(f["name"]).name,raw))
                except Exception as e:
                    item.setdefault("errors",[]).append(str(e))
            out.append(item)
    if not out:
        return {"figshare_matches":d,"crossref":js("https://api.crossref.org/works/10.1038/s41597-023-02157-4")["message"],"status":"unresolved; inspect linked repository"}
    return out

def gbif():
    match=js("https://api.gbif.org/v1/species/match?name=Chiroptera&rank=ORDER")
    if match.get("rank")!="ORDER" or match.get("matchType")!="EXACT":
        raise ValueError("order match not exact")
    out=[]
    # Count only, no unlicensed bulk records. Bounding polygons intersect GEDI latitude domain.
    for name,box in [("Iberia",(-10,35,4,44)),("Europe_GEDI",(-12,35,30,51.6)),("North_America_GEDI",(-125,25,-65,51.6))]:
        x0,y0,x1,y1=box
        geom=f"POLYGON(({x0} {y0},{x1} {y0},{x1} {y1},{x0} {y1},{x0} {y0}))"
        p={"taxonKey":match["usageKey"],"hasCoordinate":"true","hasGeospatialIssue":"false","year":"2019,2023","geometry":geom,"limit":0}
        url="https://api.gbif.org/v1/occurrence/search?"+urllib.parse.urlencode(p)
        try:
            d=js(url)
            out.append({"region":name,"bbox":box,"query":url,"raw_count":d["count"],"note":"includes all record types/coordinate precision; full DOI download + QC still required"})
        except Exception as e:
            out.append({"region":name,"error":str(e),"query":url})
    return out

for name, func in [
    ("global_traits",lambda: dryad("10.5061/dryad.tmpg4f4xm","conenna_et_al_2021_trait_data_csv.csv")),
    ("euro_traits",euro),
    ("gedi_inventory",gedi),
    ("gbif_counts",gbif),
    ("temperate_height_validation",lambda: dryad("10.5061/dryad.cjsxksn6m")),
    ("amazon_height_validation",lambda: dryad("10.5061/dryad.0vt4b8h2d")),
]:
    try:
        report["sources"][name]=func()
    except Exception as exc:
        report["errors"][name]=str(exc)
report["all_metadata_requests_passed"]=not report["errors"]
(OUT/"source_gate.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in report["sources"].items() if k!="euro_traits"},indent=2)[:45000])
print(json.dumps(report["sources"].get("euro_traits",{}),indent=2)[:18000])
print(json.dumps(report["errors"],indent=2))
