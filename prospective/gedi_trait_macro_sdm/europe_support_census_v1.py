"""Bounded existing-source continental-domain coverage census; no outcome fit."""
import collections,csv,hashlib,json,math,pathlib,time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import requests
from pyproj import Transformer
P=pathlib.Path("prior_occurrences");OUT=pathlib.Path("europe_support");OUT.mkdir(exist_ok=True)
p=P/"physical_trait_crosswalk.csv"
assert hashlib.sha256(p.read_bytes()).hexdigest()=="43bb5284308a9fe732beda51886172cb87268e5d00620eb27956d5808dae809f"
traits=list(csv.DictReader(p.open(encoding="utf-8")))
bykey=collections.defaultdict(list)
for t in traits:
    if t["species_key"] and t["AR"] and math.isfinite(float(t["AR"])) and float(t["AR"])>0:bykey[t["species_key"]].append(t)
traits={k:v[0] for k,v in bykey.items() if len(v)==1}
assert len(traits)==28
params={"hasCoordinate":"true","hasGeospatialIssue":"false","eventDate":"2019-04-17,2023-03-16","geometry":"POLYGON((-12 35,30 35,30 51.6,-12 51.6,-12 35))","occurrenceStatus":"DETECTED","coordinateUncertaintyInMeters":"0.000001,500","basisOfRecord":["HUMAN_OBSERVATION","MACHINE_OBSERVATION","OBSERVATION"]}
URL="https://api.gbif.org/v1/occurrence/search"
def get(q):
    for i in range(4):
        try:
            r=requests.get(URL,params=q,headers={"User-Agent":"batter-own-database-support/1.0"},timeout=45)
            if r.status_code==429 or 500<=r.status_code<600:
                time.sleep(2**i);continue
            r.raise_for_status();return r.json()
        except (requests.ConnectionError,requests.Timeout):time.sleep(2**i)
    raise RuntimeError("GBIF request failed after bounded retries")
def count(k):
    try:return k,int(get({**params,"taxonKey":k,"limit":0})["count"]),None
    except Exception as e:return k,None,type(e).__name__+": "+str(e)[:150]
ks=sorted(traits,key=int)
with ThreadPoolExecutor(max_workers=3) as ex:counts=list(ex.map(count,ks))
report={"stage":"continental-domain coverage only; not fitted SDM","query":params,"checked_utc":datetime.now(timezone.utc).isoformat(),"scope":"fixed Europe_GEDI rectangle includes neighboring non-European land; no country filtering","species_count":len(ks),"budget":{"per_species_complete":6000,"total_complete":120000},"species":[]}
planned=0
for k,n,err in counts:
    s={"species_key":k,"species":traits[k]["source_name"],"query_count":n}
    if err:s.update(status="COUNT_ERROR",error=err)
    elif n==0:s.update(status="NO_MATCHING_RECORDS")
    elif n>6000:s.update(status="COUNT_ONLY_HIGH_VOLUME")
    elif planned+n>120000:s.update(status="COUNT_ONLY_BUDGET")
    else:s.update(status="PLANNED_COMPLETE");planned+=n
    report["species"].append(s)
report["planned_complete_records"]=planned
(OUT/"coverage_report.json").write_text(json.dumps(report,indent=2))
print("EUROPE_COUNTS="+json.dumps(report),flush=True)
proj=Transformer.from_crs(4326,6933,always_xy=True)
def valid(r,k):
    u=r.get("coordinateUncertaintyInMeters")
    return bool(r.get("species")) and str(r.get("speciesKey"))==k and str(r.get("occurrenceStatus","")).upper() in {"PRESENT","DETECTED"} and isinstance(u,(int,float)) and 0<u<=500 and r.get("basisOfRecord") in {"HUMAN_OBSERVATION","MACHINE_OBSERVATION","OBSERVATION"}
def acquire(s):
    if s["status"]!="PLANNED_COMPLETE":return s,[]
    k=s["species_key"];n=s["query_count"]
    unique={};rows=[]
    try:
        for off in range(0,n,300):
            d=get({**params,"taxonKey":k,"limit":300,"offset":off})
            if d["count"]!=n:raise RuntimeError("live count drift")
            for r in d["results"]:
                if r.get("key") is None or r["key"] in unique:raise RuntimeError("missing/duplicate record key")
                unique[r["key"]]=1
                if not valid(r,k):continue
                lon=r.get("decimalLongitude");lat=r.get("decimalLatitude")
                if not isinstance(lon,(int,float)) or not isinstance(lat,(int,float)):continue
                if not(-12<=lon<=30 and 35<=lat<=51.6):raise ValueError("outside query bounds")
                x,y=proj.transform(lon,lat)
                if not math.isfinite(x) or not math.isfinite(y):continue
                rows.append((k,math.floor(x/1000),math.floor(y/1000),str(r.get("datasetKey") or ""),str(r.get("eventDate") or "")[:4],str(r.get("license") or "")))
        if len(unique)!=n:raise RuntimeError("incomplete pagination")
        cells={(r[1],r[2]) for r in rows};blocks=collections.Counter((x//200,y//200) for x,y in cells);b=sum(v>=5 for v in blocks.values())
        s.update(status="COMPLETE_LIVE_QUERY",raw_records=len(unique),eligible_records=len(rows),unique_1km_cells=len(cells),blocks_5_cells=b,provisional_coverage_pass=len(cells)>=30 and b>=4)
        return s,rows
    except Exception as e:
        s.update(status="NONADMISSION",error=type(e).__name__+": "+str(e)[:180]);return s,[]
with ThreadPoolExecutor(max_workers=3) as ex:
    results=list(ex.map(acquire,report["species"]))
report["species"]=[s for s,_ in results]
import gzip
cells=collections.Counter(row for _,rows in results for row in rows)
with gzip.open(OUT/"complete_species_cell_source_year.csv.gz","wt",encoding="utf-8",newline="") as f:
    w=csv.writer(f);w.writerow(["species_key","cell_x","cell_y","dataset_key","year","license","records"])
    for row,n in sorted(cells.items()):w.writerow([*row,n])
report.update({"completed_species":sum(s["status"]=="COMPLETE_LIVE_QUERY" for s in report["species"]),"complete_query_records":sum(s.get("raw_records",0) for s in report["species"]),"eligible_records":sum(s.get("eligible_records",0) for s in report["species"]),"complete_species_cells":sum(s.get("unique_1km_cells",0) for s in report["species"]),"provisional_coverage_pass_species":sum(s.get("provisional_coverage_pass",False) for s in report["species"]),"count_only_high_volume_species":sum(s["status"]=="COUNT_ONLY_HIGH_VOLUME" for s in report["species"]),"original_S1_admission":False,"limits":["Count-only high-volume species are deferred, not failed biological coverage.","No raster, effort, terrain, roost, season or final DOI audit; no PAVD support.","No inference about occurrence, selection or trait effects."]})
report["output_sha256"]=hashlib.sha256((OUT/"complete_species_cell_source_year.csv.gz").read_bytes()).hexdigest()
(OUT/"coverage_report.json").write_text(json.dumps(report,indent=2)+"\n");print("EUROPE_SUPPORT_REPORT="+json.dumps(report),flush=True)
