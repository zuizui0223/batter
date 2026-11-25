"""Outcome-blind European physical-trait coverage. Bounded GBIF live search; no SDM."""
import csv, collections, gzip, hashlib, json, math, pathlib, time, threading, sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import requests
from pyproj import Transformer
OUT=pathlib.Path("europe_coverage");OUT.mkdir(exist_ok=True)
p=pathlib.Path("occ/physical_trait_crosswalk.csv")
assert hashlib.sha256(p.read_bytes()).hexdigest()=="43bb5284308a9fe732beda51886172cb87268e5d00620eb27956d5808dae809f"
with p.open() as f:rows=list(csv.DictReader(f))
group=collections.defaultdict(list)
for a in rows:
    if a["species_key"] and a["AR"]:group[a["species_key"]].append(a)
traits={k:v[0] for k,v in group.items() if len(v)==1}
assert len(traits)==28
# Country whitelist, fixed before any European spatial coverage output; excludes transcontinental
# countries beyond the regional study definition. No political inference.
countries="AD AL AT BE BA BG BY HR CZ DK EE FI FR DE GR HU IE IT LV LI LT LU MT MD MC ME NL MK NO PL PT RO SM RS SK SI ES SE CH UA GB VA".split()
bbox=(-12,35,32,71)
P=Transformer.from_crs(4326,6933,always_xy=True);I=Transformer.from_crs(6933,4326,always_xy=True)
xmin,ymin=P.transform(bbox[0],bbox[1]);xmax,ymax=P.transform(bbox[2],bbox[3])
base={"taxonKey":list(traits),"country":countries,"hasCoordinate":"true","hasGeospatialIssue":"false","eventDate":"2019-04-17,2023-03-16","occurrenceStatus":"DETECTED","coordinateUncertaintyInMeters":"0.000001,500","basisOfRecord":["HUMAN_OBSERVATION","MACHINE_OBSERVATION","OBSERVATION"]}
LOCAL=threading.local()
def get(params):
    if not hasattr(LOCAL,"s"):
        LOCAL.s=requests.Session();LOCAL.s.headers["User-Agent"]="batter-GVSM-Europe-coverage/1.0"
    for i in range(5):
        try:
            r=LOCAL.s.get("https://api.gbif.org/v1/occurrence/search",params=params,timeout=(20,50))
            if r.status_code==429 or 500<=r.status_code<600:
                time.sleep(min(60,max(2**i,int(r.headers.get("Retry-After","0")) if r.headers.get("Retry-After","").isdigit() else 0)));continue
            r.raise_for_status()
            return r.json()
        except (requests.Timeout,requests.ConnectionError):time.sleep(2**i)
    raise RuntimeError("bounded GBIF retries exhausted")
def polygon(rect):
    x0,y0,x1,y1=rect
    a,b=I.transform(x0,y0);c,d=I.transform(x1,y1)
    return f"POLYGON(({a:.10f} {b:.10f},{c:.10f} {b:.10f},{c:.10f} {d:.10f},{a:.10f} {d:.10f},{a:.10f} {b:.10f}))"
def query(rect,extra):return {**base,"geometry":polygon(rect),**extra}
def count(block):
    bx,by,rect=block
    d=get(query(rect,{"limit":0,"facet":"speciesKey","facetLimit":100}))
    return {"block_x":bx,"block_y":by,"rect":rect,"count":d["count"],"species_counts":{v["name"]:v["count"] for v in next((f["counts"] for f in d.get("facets",[]) if f["field"]=="SPECIES_KEY"),[])}}
def write_report(rep):
    (OUT/"report.json").write_text(json.dumps(rep,indent=2))
    print("EUROPE_REPORT="+json.dumps({k:v for k,v in rep.items() if k!="blocks"}),flush=True)
blocks=[]
for x in range(math.floor(xmin/200000),math.ceil(xmax/200000)):
    for y in range(math.floor(ymin/200000),math.ceil(ymax/200000)):
        rect=(max(xmin,x*200000),max(ymin,y*200000),min(xmax,(x+1)*200000),min(ymax,(y+1)*200000))
        blocks.append((x,y,rect))
full=get(query((xmin,ymin,xmax,ymax),{"limit":0,"facet":"speciesKey","facetLimit":100}))
rep={"stage":"pre-model source coverage; no ecological fit","time":datetime.now(timezone.utc).isoformat(),"bbox":bbox,"country_whitelist":countries,"physical_trait_species":len(traits),"total_record_count":full["count"],"blocks_queried":len(blocks),"limits":{"max_total_records":500000,"max_single_search_records":40000,"workers":3},"limitations":["Only physical-trait species in query; target-group background/effort not acquired here.","Live search; final model requires immutable DOI download and further roost/season/effort QC.","No environmental mask or model."]}
print("EUROPE_INITIAL="+json.dumps(rep),flush=True)
with ThreadPoolExecutor(max_workers=3) as ex:counts=list(ex.map(count,blocks))
rep["blocks"]=counts
upper=[]
for k,t in traits.items():
    n=sum(a["species_counts"].get(k,0) for a in counts)
    b=sum(a["species_counts"].get(k,0)>=5 for a in counts)
    upper.append({"species":t["source_name"],"key":k,"records_upper_bound":n,"blocks_with_5_records_upper_bound":b,"potential_gate":n>=30 and b>=4})
rep["facet_count_total"]=sum(a["count"] for a in counts)
rep["upper_bound_species_gate"]=sum(a["potential_gate"] for a in upper)
rep["upper_bound_by_species"]=upper
rep["status"]="BLOCK_COUNTS_READY"
write_report(rep)
if rep["facet_count_total"]>500000:
    rep["status"]="BLOCKED_BULK_DOI_REQUIRED_ABOVE_BOUNDED_SEARCH_BUDGET"
    write_report(rep);sys.exit(0)
if rep["upper_bound_species_gate"]<20:
    rep["status"]="COVERAGE_UPPER_BOUND_FAILS_20_SPECIES"
    write_report(rep);sys.exit(0)
fields=["key","species","speciesKey","decimalLongitude","decimalLatitude","coordinateUncertaintyInMeters","eventDate","basisOfRecord","datasetKey","occurrenceStatus","license","issues","occurrenceID","eventID","samplingProtocol","establishmentMeans","countryCode"]
def split(rect,n):
    if n<=40000:return [(rect,n)]
    x0,y0,x1,y1=rect;mx=(x0+x1)/2;my=(y0+y1)/2
    result=[]
    for child in [(x0,y0,mx,my),(mx,y0,x1,my),(x0,my,mx,y1),(mx,my,x1,y1)]:
        d=get(query(child,{"limit":0}))
        result.extend(split(child,d["count"]))
    return result
units=[]
for a in counts:
    if a["count"]:units.extend(split(a["rect"],a["count"]))
pages=[(rect,n,i) for rect,n in units for i in range(0,n,300)]
if len(pages)>2000:
    rep["status"]="BLOCKED_QUERY_BUDGET_DOI_REQUIRED";write_report(rep);sys.exit(0)
def page(task):
    rect,n,offset=task
    d=get(query(rect,{"limit":300,"offset":offset}))
    if d["count"]!=n:raise RuntimeError("live search count drift; cannot certify snapshot")
    if len(d["results"])!=min(300,n-offset):raise RuntimeError("incomplete GBIF page")
    return [{k:a.get(k) for k in fields} for a in d["results"]]
unique={};nretrieved=0
try:
    with ThreadPoolExecutor(max_workers=3) as ex:
        for i,batch in enumerate(ex.map(page,pages)):
            nretrieved+=len(batch)
            for a in batch:
                key=str(a["key"])
                if key in unique and unique[key]!=a:raise RuntimeError("conflicting duplicate key")
                unique[key]=a
            if (i+1)%100==0:print("GBIF_PAGE_PROGRESS",i+1,len(pages),len(unique),flush=True)
except Exception as e:
    rep["status"]="INCOMPLETE_LIVE_ACQUISITION";rep["error"]=str(e)[:300];write_report(rep);raise
def valid(a):
    u=a["coordinateUncertaintyInMeters"]
    return a["species"] and str(a["speciesKey"]) in traits and a["occurrenceStatus"] in ("DETECTED","PRESENT") and a["basisOfRecord"] in ("HUMAN_OBSERVATION","MACHINE_OBSERVATION","OBSERVATION") and isinstance(u,(int,float)) and 0<u<=500 and a["countryCode"] in countries
cells=collections.defaultdict(lambda:collections.defaultdict(set))
eligible=0
with gzip.open(OUT/"europe_physical_trait_search.jsonl.gz","wt",encoding="utf8") as f:
    for a in unique.values():
        f.write(json.dumps(a,ensure_ascii=False)+"\n")
        if not valid(a):continue
        x,y=P.transform(a["decimalLongitude"],a["decimalLatitude"])
        if not (math.isfinite(x) and math.isfinite(y)):continue
        if not (xmin<=x<=xmax and ymin<=y<=ymax):continue
        eligible+=1;k=str(a["speciesKey"]);c=(math.floor(x/1000),math.floor(y/1000));b=(c[0]//200,c[1]//200)
        cells[k][b].add(c)
summary=[]
for k,t in traits.items():
    b=cells[k];n=sum(map(len,b.values()));nb=sum(len(v)>=5 for v in b.values())
    summary.append({"species":t["source_name"],"key":k,"unique_cells":n,"blocks_ge5":nb,"passes_provisional_gate":n>=30 and nb>=4})
with (OUT/"species_spatial_coverage.csv").open("w") as f:
    w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
rep.update({"status":"REAL_EUROPE_SPATIAL_COVERAGE_READY" if len(unique)==full["count"] else "LIVE_COUNT_MISMATCH_NO_COMPLETE_SNAPSHOT","retrieved_rows":nretrieved,"unique_keys":len(unique),"eligible_records":eligible,"unique_species_cells":sum(x["unique_cells"] for x in summary),"provisional_gate_species":sum(x["passes_provisional_gate"] for x in summary),"species_spatial_coverage":summary})
write_report(rep)
