"""Real inputs only; no ecological fitting from biased pilot records."""
import csv, hashlib, io, json, os, pathlib, re, collections, sys
import requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
OUT=pathlib.Path("macro_inputs"); OUT.mkdir(exist_ok=True)
session=requests.Session()
session.headers["User-Agent"]="batter-macro-sdm-source-QC/1.0 (research)"
report={"stage":"real-input QC; not model outcomes","utc":datetime.now(timezone.utc).isoformat(),"errors":{}}
def get(url, **kw):
    r=requests.get(url,timeout=60,**kw);r.raise_for_status();return r
def save(name,raw):
    (OUT/name).write_bytes(raw)
    return {"file":name,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
def tab(raw):
    text=raw.decode("utf-8-sig")
    dialect=csv.Sniffer().sniff(text[:8192],delimiters=",;\t")
    return list(csv.DictReader(io.StringIO(text),dialect=dialect))
def schema(rows):
    return {"rows":len(rows),"columns":list(rows[0]) if rows else [],"example":rows[:2]}
def traits():
    j=get("https://api.figshare.com/v2/articles/21777161/versions/2").json()
    assert j.get("doi")=="10.6084/m9.figshare.21777161.v2"
    tables={}
    for f in j["files"]:
        name=f["name"]
        if name not in {"03_morphology.csv","04_acoustic_signature.csv","06_foraging_habitat.csv","07_roost_type.csv","Taxon.csv","Trait_description.csv"}:continue
        raw=get(f["download_url"]).content
        assert len(raw)==f["size"] and hashlib.md5(raw).hexdigest()==f["computed_md5"], name
        rows=tab(raw)
        tables[name]={"provenance":save(name,raw),**schema(rows)}
        if name=="Trait_description.csv":
            tables[name]["wing_definitions"]=[x for x in rows if re.search(r"aspect ratio|wing loading|wing area|wing span|wingspan|forearm|wing load",str(x),re.I)]
        if name=="03_morphology.csv":
            # inspect possible long-format categorical fields; exact mapping follows the data dictionary
            tables[name]["categorical"]={k:collections.Counter(str(x.get(k,"")) for x in rows).most_common(40) for k in rows[0] if re.search(r"trait|unit|taxon|species|sex|method|age",k,re.I)}
    return tables
def occurrence():
    # Bounded deterministic API smoke test; no inference from ordered/paginated subset.
    base="https://api.gbif.org/v1/occurrence/search"
    key=get("https://api.gbif.org/v1/species/match",params={"name":"Chiroptera","rank":"ORDER"}).json()
    assert key["matchType"]=="EXACT" and key["rank"]=="ORDER"
    tiles=[(x,y) for x in range(-10,4,2) for y in range(36,44,2)]
    def one(tile):
        x,y=tile
        p={"taxonKey":key["usageKey"],"hasCoordinate":"true","hasGeospatialIssue":"false","eventDate":"2019-04-17,2023-03-16","geometry":f"POLYGON(({x} {y},{x+2} {y},{x+2} {y+2},{x} {y+2},{x} {y}))","limit":300}
        d=get(base,params=p).json()
        fields=["key","species","speciesKey","decimalLongitude","decimalLatitude","coordinateUncertaintyInMeters","eventDate","basisOfRecord","datasetKey","occurrenceStatus","license","issues"]
        rec=[{k:a.get(k) for k in fields} for a in d["results"]]
        return {"tile":tile,"count":d["count"],"returned":len(rec),"records":rec}
    with ThreadPoolExecutor(max_workers=3) as ex: result=list(ex.map(one,tiles))
    records={a["key"]:a for t in result for a in t["records"]}
    eligible=[a for a in records.values() if a["species"] and a["occurrenceStatus"]=="PRESENT" and isinstance(a["coordinateUncertaintyInMeters"],(int,float)) and 0<a["coordinateUncertaintyInMeters"]<=500 and a["basisOfRecord"] in ("HUMAN_OBSERVATION","MACHINE_OBSERVATION","OBSERVATION")]
    return {"tile_counts":[{k:v for k,v in t.items() if k!="records"} for t in result],"retrieved_unique":len(records),"strict_pilot_rows":len(eligible),"strict_pilot_species":len(set(a["species"] for a in eligible)),"species_counts":dict(collections.Counter(a["species"] for a in eligible)),"artifact":save("gbif_pilot.json",json.dumps(list(records.values())).encode()),"note":"First page per 2-degree tile; not a representative sample or DOI-pinned analytical dataset."}
def gedi():
    token=bool(os.getenv("EARTHDATA_TOKEN")); userpass=bool(os.getenv("EARTHDATA_USERNAME") and os.getenv("EARTHDATA_PASSWORD"))
    result={"token_configured":token,"user_password_configured":userpass}
    if not (token or userpass):return {**result,"status":"BLOCKED_NO_EARTHDATA_SECRET"}
    # Official login and authenticated HTTPS stream. Never print credentials or signed URLs.
    import earthaccess, rasterio
    from rasterio.windows import Window
    from rasterio.warp import transform
    try:
        auth=earthaccess.login(strategy="environment",persist=False)
        if not auth.authenticated:return {**result,"status":"BLOCKED_AUTH_FAILED"}
        granules=earthaccess.search_data(concept_id="C3043630107-ORNL_CLOUD",count=1000)
        selected={}
        for g in granules:
            for link in g.data_links(access="external"):
                m=re.search(r"pavd-(\d+)-(\d+)_vf_20190417_20230316_1000m\.tif$",link)
                if m:selected[int(m.group(1))]=link
        result["profile_layers"]=len(selected)
        if set(selected)!=set(range(0,80,5)):return {**result,"status":"BLOCKED_INCOMPLETE_PROFILE"}
        fs=earthaccess.get_fsspec_https_session()
        windows=[]
        for height,url in sorted(selected.items()):
            with rasterio.open(url,opener=fs.open) as src:
                x,y=transform("EPSG:4326",src.crs,[-4.0],[40.0]);row,col=src.index(x[0],y[0])
                data=src.read(window=Window(col-5,row-5,11,11),masked=True)
                windows.append({"height":height,"crs":str(src.crs),"shape":list(data.shape),"band_names":list(src.descriptions),"valid_pixels_per_band":[int(a.count()) for a in data],"band_medians":[float(a.compressed().mean()) if a.count() else None for a in data]})
        result["windows"]=windows;result["status"]="READ_16_REAL_RASTER_WINDOWS"
    except Exception as e:result["status"]="BLOCKED_RASTER_READ";result["error_type"]=type(e).__name__
    return result
for name,fn in [("traits",traits),("gbif_pilot",occurrence),("gedi",gedi)]:
    try:report[name]=fn()
    except Exception as e:report["errors"][name]=type(e).__name__+": "+str(e)[:400] if name!="gedi" else type(e).__name__
report["gbif_credentials_present"]=bool((os.getenv("GBIF_USERNAME") or os.getenv("GBIF_USER")) and (os.getenv("GBIF_PASSWORD") or os.getenv("GBIF_PWD")) and os.getenv("GBIF_EMAIL"))
(OUT/"input_report.json").write_text(json.dumps(report,indent=2),encoding="utf8")
print(json.dumps(report,indent=2))
