import json, pathlib, re, urllib.request, urllib.parse, os
out=pathlib.Path("gedi_access");out.mkdir(exist_ok=True)
url="https://cmr.earthdata.nasa.gov/search/granules.json?collection_concept_id=C3043630107-ORNL_CLOUD&page_size=2000"
with urllib.request.urlopen(url,timeout=60) as r: entries=json.load(r)["feed"]["entry"]
selected=[]
for e in entries:
    title=e.get("title","")
    if "20190417_20230316_1000m" not in title: continue
    links=[l["href"] for l in e.get("links",[]) if l.get("href","").startswith("https://") and ".tif" in l["href"] and not l.get("inherited")]
    selected.append({"title":title,"links":links})
profile=[x for x in selected if re.search(r"pavd-\d+-\d+_vf_",x["title"])]
result={"full_period_1km":selected,"profile_count":len(profile),"access":[]}
for x in profile[:2]:
    for u in x["links"][:2]:
        try:
            req=urllib.request.Request(u,headers={"Range":"bytes=0-16383","User-Agent":"batter-gedi-access/1"})
            with urllib.request.urlopen(req,timeout=40) as r:
                raw=r.read(16384)
                result["access"].append({"title":x["title"],"url":u,"status":r.status,"content_type":r.headers.get("Content-Type"),"range":r.headers.get("Content-Range"),"tiff_magic":raw[:4] in (b"II*\x00",b"MM\x00*",b"II+\x00",b"MM\x00+"),"bytes_read":len(raw)})
        except Exception as e: result["access"].append({"title":x["title"],"url":u,"error":str(e)})
(out/"inventory.json").write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
