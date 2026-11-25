"""Pre-model input audit only; public GBIF search acquisition <=100k, not DOI-pinned final data."""
import csv, collections, hashlib, io, json, math, pathlib, re, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import requests
from pyproj import Transformer
OUT=pathlib.Path("iberia_inputs");OUT.mkdir(exist_ok=True)
P=pathlib.Path("prior_inputs");Q=pathlib.Path("prior_diagnosis")
BASE="https://api.gbif.org/v1/"
HEADERS={"User-Agent":"batter-gedi-iberia-input-QC/1.0"}
def get(path,params=None):
    url=BASE+path
    for i in range(4):
        try:
            r=requests.get(url,params=params,headers=HEADERS,timeout=45)
            if r.status_code==429 or 500<=r.status_code<600:
                time.sleep(2**i);continue
            r.raise_for_status();return r.json()
        except (requests.ConnectionError,requests.Timeout):
            time.sleep(2**i)
    raise RuntimeError("GBIF request failed after bounded retries: "+path)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def table(path):
    s=path.read_text(encoding="utf-8-sig")
    return list(csv.DictReader(io.StringIO(s),dialect=csv.Sniffer().sniff(s[:8192],delimiters=",;\t")))
def positive(x):
    try:
        v=float(x)
        return v if math.isfinite(v) and v>0 else None
    except (ValueError,TypeError):return None
def norm(s):return " ".join(str(s).replace("_"," ").split())
def present(r):
    # GBIF Nov 2026 release: PRESENT -> DETECTED, ABSENT -> NOT_DETECTED.
    # Same biological criterion, no inclusion of non-detections.
    return str(r.get("occurrenceStatus","")).upper() in {"PRESENT","DETECTED"}
def valid(r):
    u=r.get("coordinateUncertaintyInMeters")
    return bool(r.get("species")) and present(r) and isinstance(u,(float,int)) and 0<u<=500 and r.get("basisOfRecord") in {"HUMAN_OBSERVATION","MACHINE_OBSERVATION","OBSERVATION"}
def write_csv(path,rows):
    if not rows:raise ValueError("no output rows")
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    raw=P/"gbif_pilot.json"
    assert digest(raw)=="42577b98946a3bbe67c8c6516932dc85e208ce9f40746a715fc305c4f0bcea08"
    pilot=json.loads(raw.read_text())
    physical=Q/"physical_wing_traits_original.csv"
    assert digest(physical)=="d3ebe7656a60b44933f4da1a8302ca800bed07e0864d557698bf322eb7b85f49"
    rows=table(physical)
    assert len(rows)==30
    traits=[]
    for row in rows:
        name=norm(row["Latin names"])
        ar=positive(row["Aspect ratio"]);wl=positive(row["Wingloading"])
        span=positive(row["Wingspan"]);area=positive(row["Wingarea"]);mass=positive(row["Adult body mass"])
        match=get("species/match",{"name":name,"rank":"SPECIES","kingdom":"Animalia","order":"Chiroptera"})
        ok=match.get("matchType")=="EXACT" and match.get("rank")=="SPECIES" and match.get("order")=="Chiroptera"
        key=match.get("acceptedUsageKey") or match.get("usageKey") if ok else None
        traits.append({"source_name":name,"species_key":str(key) if key else "","matched_name":match.get("species") or match.get("canonicalName") or "","match_type":match.get("matchType",""),"taxonomic_status":match.get("status",""),"AR":ar,"WL_N_m2":wl,"span_m":span,"area_m2":area,"body_mass_g":mass,"AR_reconstructed_rounded":span**2/area if span and area else None,"WL_reconstructed_rounded":mass*0.00980665/area if mass and area else None,"source_doi":"10.5281/zenodo.7226367","source_references":row.get("Source","")})
    write_csv(OUT/"physical_trait_crosswalk.csv",traits)
    # Ambiguous accepted-key matches are never silently collapsed.
    hits=collections.defaultdict(list)
    for t in traits:
        if t["species_key"] and t["AR"] is not None:hits[t["species_key"]].append(t)
    keyed={k:v[0] for k,v in hits.items() if len(v)==1}
    names={t["source_name"]:t for t in keyed.values()}
    order=get("species/match",{"name":"Chiroptera","rank":"ORDER"})
    assert order["matchType"]=="EXACT" and order["rank"]=="ORDER"
    params={"taxonKey":order["usageKey"],"hasCoordinate":"true","hasGeospatialIssue":"false","eventDate":"2019-04-17,2023-03-16","geometry":"POLYGON((-10 35,4 35,4 44,-10 44,-10 35))","occurrenceStatus":"DETECTED","coordinateUncertaintyInMeters":"0.000001,500","basisOfRecord":["HUMAN_OBSERVATION","MACHINE_OBSERVATION","OBSERVATION"]}
    q=get("occurrence/search",{**params,"limit":0,"facet":"speciesKey","facetLimit":100})
    n=q["count"]
    assert 0<n<=50000,"bounded Iberian source-only acquisition cap"
    facets=q.get("facets",[])
    matches=[]
    for a in next((f["counts"] for f in facets if f["field"]=="SPECIES_KEY"),[]):
        t=keyed.get(str(a["name"]))
        if t:matches.append({"species_key":str(a["name"]),"trait_name":t["source_name"],"records":a["count"]})
    report={"stage":"real-data coverage; no SDM or ecological outcomes","checked_utc":datetime.now(timezone.utc).isoformat(),"query":params,"public_search_count":n,"physical_source_rows":len(traits),"positive_AR_species":sum(t["AR"] is not None for t in traits),"positive_WL_species":sum(t["WL_N_m2"] is not None for t in traits),"physical_AR_WL_species":sum(t["AR"] is not None and t["WL_N_m2"] is not None for t in traits),"unambiguous_matched_AR_species":len(keyed),"trait_matched_facet_species":len(matches),"trait_matched_facet_records":sum(t["records"] for t in matches),"matched_facet_counts":matches,"old_pilot_rows":len(pilot),"corrected_pilot_eligible_rows":sum(valid(x) for x in pilot),"corrected_pilot_eligible_species":len({x["species"] for x in pilot if valid(x)}),"facets":facets}
    # Record metadata before actual pagination, and preserve original artifact checksums.
    (OUT/"coverage_report.json").write_text(json.dumps(report,indent=2))
    print("PREP_COVERAGE="+json.dumps(report),flush=True)
    fields=["key","species","speciesKey","decimalLongitude","decimalLatitude","coordinateUncertaintyInMeters","eventDate","basisOfRecord","datasetKey","occurrenceStatus","license","issues","occurrenceID","eventID","samplingProtocol","establishmentMeans"]
    def page(offset):
        d=get("occurrence/search",{**params,"limit":300,"offset":offset})
        if d["count"]!=n:raise RuntimeError("GBIF search count changed during pagination; no completed snapshot")
        return [{k:a.get(k) for k in fields} for a in d["results"]]
    # Documented occurrence search limit 300/page and <100,000/query.
    offsets=list(range(0,n,300))
    with ThreadPoolExecutor(max_workers=3) as ex:
        pages=list(ex.map(page,offsets))
    raw_rows=[r for p in pages for r in p]
    unique={str(x["key"]):x for x in raw_rows if x["key"] is not None}
    # Search is live; insist on count/unique agreement. Never treat duplicate/missing rows as complete.
    report.update({"raw_retrieved":len(raw_rows),"unique_record_keys":len(unique),"complete_pagination":len(raw_rows)==n==len(unique)})
    import gzip
    with gzip.open(OUT/"gbif_iberia_qc_search.jsonl.gz","wt",encoding="utf-8") as f:
        for a in unique.values():f.write(json.dumps(a,ensure_ascii=False)+"\n")
    proj=Transformer.from_crs(4326,6933,always_xy=True)
    joined=[]
    eligible=[a for a in unique.values() if valid(a)]
    for a in eligible:
        key=str(a["speciesKey"])
        t=keyed.get(key)
        # No silent name-only match when a distinct current species key is available.
        if not t:continue
        lon,lat=a["decimalLongitude"],a["decimalLatitude"]
        if not isinstance(lon,(int,float)) or not isinstance(lat,(int,float)):continue
        x,y=proj.transform(lon,lat)
        if not math.isfinite(x) or not math.isfinite(y):continue
        joined.append({"gbif_key":a["key"],"species_key":key,"species":a["species"],"source_trait_species":t["source_name"],"AR":t["AR"],"WL_N_m2":t["WL_N_m2"],"dataset_key":a["datasetKey"],"license":a["license"],"event_date":a["eventDate"],"x6933":x,"y6933":y,"provisional_1km_x":math.floor(x/1000),"provisional_1km_y":math.floor(y/1000),"block200km_x":math.floor(x/200000),"block200km_y":math.floor(y/200000)})
    if joined:write_csv(OUT/"occurrence_physical_trait_join.csv",joined)
    # Provisional equal-area grid for sample-size feasibility; not official raster grid until GEDI transform checked.
    cells=collections.defaultdict(set);blocks=collections.defaultdict(lambda:collections.defaultdict(set))
    for a in joined:
        s=a["species_key"];cell=(a["provisional_1km_x"],a["provisional_1km_y"]);block=(a["block200km_x"],a["block200km_y"])
        cells[s].add(cell);blocks[s][block].add(cell)
    counts=[]
    for k,cs in cells.items():
        counts.append({"species":keyed[k]["source_name"],"species_key":k,"unique_1km_cells":len(cs),"blocks_with_at_least_5_cells":sum(len(b)>=5 for b in blocks[k].values()),"meets_provisional_S1":len(cs)>=30 and sum(len(b)>=5 for b in blocks[k].values())>=4})
    counts.sort(key=lambda x:x["unique_1km_cells"],reverse=True)
    if counts:write_csv(OUT/"species_provisional_spatial_coverage.csv",counts)
    report.update({"eligible_occurrences":len(eligible),"eligible_species":len({a["speciesKey"] for a in eligible}),"joined_occurrences":len(joined),"joined_species":len(cells),"joined_unique_species_cells":sum(map(len,cells.values())),"provisional_S1_species":sum(a["meets_provisional_S1"] for a in counts),"species_spatial_coverage":counts,"limitations":["Live occurrence search, no DOI-pinned final download; no roost/captive/season or source-level effort audit yet.","Provisional EPSG:6933 zero-origin grid only; native GEDI grid, per-layer counts and environmental coverage not checked.","Not a fitted SDM; no ecological inference."]})
    report["files"]={p.name:{"bytes":p.stat().st_size,"sha256":digest(p)} for p in OUT.iterdir() if p.is_file() and p.name!="coverage_report.json"}
    (OUT/"coverage_report.json").write_text(json.dumps(report,indent=2))
    print("JOIN_RESULT="+json.dumps(report),flush=True)
if __name__=="__main__":main()
