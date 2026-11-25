"""Pre-model geographic coverage only. Reuse cancelled full-region run's completed block census.
Acquire each eligible low/moderate-volume species completely, not first pages or count proxies.
Dominant P. pipistrellus gets an explicitly partial coverage witness; not modeling data.
"""
import collections,csv,gzip,hashlib,json,math,pathlib,time,threading
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import requests
from pyproj import Transformer

OUT=pathlib.Path("europe_targeted");OUT.mkdir(exist_ok=True)
prior=json.loads(pathlib.Path("block_prior/report.json").read_text())
assert prior["status"]=="BLOCK_COUNTS_READY"
assert prior["total_record_count"]==314593 and prior["upper_bound_species_gate"]==22
assert len(prior["blocks"])==330
candidates=prior["upper_bound_by_species"]
p=pathlib.Path("occ/physical_trait_crosswalk.csv")
assert hashlib.sha256(p.read_bytes()).hexdigest()=="43bb5284308a9fe732beda51886172cb87268e5d00620eb27956d5808dae809f"
with p.open() as f:trait_rows=list(csv.DictReader(f))
grp=collections.defaultdict(list)
for t in trait_rows:
    if t["species_key"] and t["AR"]:grp[t["species_key"]].append(t)
traits={k:v[0] for k,v in grp.items() if len(v)==1}
assert len(traits)==28
countries=prior["country_whitelist"]
bbox=prior["bbox"]
P=Transformer.from_crs(4326,6933,always_xy=True)
I=Transformer.from_crs(6933,4326,always_xy=True)
xmin,ymin=P.transform(bbox[0],bbox[1]);xmax,ymax=P.transform(bbox[2],bbox[3])
base={"country":countries,"hasCoordinate":"true","hasGeospatialIssue":"false","eventDate":"2019-04-17,2023-03-16","occurrenceStatus":"DETECTED","coordinateUncertaintyInMeters":"0.000001,500","basisOfRecord":["HUMAN_OBSERVATION","MACHINE_OBSERVATION","OBSERVATION"]}
local=threading.local()
def polygon(rect):
    x0,y0,x1,y1=rect;a,b=I.transform(x0,y0);c,d=I.transform(x1,y1)
    return f"POLYGON(({a:.10f} {b:.10f},{c:.10f} {b:.10f},{c:.10f} {d:.10f},{a:.10f} {d:.10f},{a:.10f} {b:.10f}))"
def get(q):
    if not hasattr(local,"s"):
        local.s=requests.Session();local.s.headers["User-Agent"]="batter-Europe-species-coverage/1.0"
    for i in range(4):
        try:
            r=local.s.get("https://api.gbif.org/v1/occurrence/search",params=q,timeout=(15,40))
            if r.status_code==429 or 500<=r.status_code<600:
                delay=r.headers.get("Retry-After","")
                time.sleep(min(60,max(2**i,int(delay) if delay.isdigit() else 0)));continue
            r.raise_for_status();return r.json()
        except (requests.ConnectionError,requests.Timeout):time.sleep(2**i)
    raise RuntimeError("bounded retries exhausted")
def query(k,rect,**kw):return {**base,"taxonKey":k,"geometry":polygon(rect),**kw}
fields=["key","species","speciesKey","decimalLongitude","decimalLatitude","coordinateUncertaintyInMeters","eventDate","basisOfRecord","datasetKey","occurrenceStatus","license","issues","occurrenceID","eventID","samplingProtocol","establishmentMeans","countryCode"]
def valid(a,k,rect):
    u=a.get("coordinateUncertaintyInMeters")
    if not (a.get("species") and str(a.get("speciesKey"))==k and a.get("occurrenceStatus") in ("DETECTED","PRESENT") and a.get("basisOfRecord") in base["basisOfRecord"] and isinstance(u,(int,float)) and 0<u<=500 and a.get("countryCode") in countries):return None
    lon=a.get("decimalLongitude");lat=a.get("decimalLatitude")
    if not isinstance(lon,(int,float)) or not isinstance(lat,(int,float)):return None
    x,y=P.transform(lon,lat)
    if not (math.isfinite(x) and math.isfinite(y)):return None
    if not (rect[0]-0.01<=x<=rect[2]+0.01 and rect[1]-0.01<=y<=rect[3]+0.01):return None
    return math.floor(x/1000),math.floor(y/1000)
def write_table(path,rows):
    with gzip.open(path,"wt",encoding="utf-8",newline="") as f:
        w=csv.writer(f);w.writerow(["species_key","cell_x","cell_y","dataset_key","year","license","records"])
        for row,n in sorted(rows.items()):w.writerow([*row,n])
def fetch_species(item):
    k=item["key"];name=item["species"]
    result={"species_key":k,"species":name,"prior_records":item["records_upper_bound"],"prior_block_upper_bound":item["blocks_with_5_records_upper_bound"]}
    if not item["potential_gate"]:
        return {**result,"status":"PRIOR_RECORD_UPPER_BOUND_NONADMISSION"}
    rect=(xmin,ymin,xmax,ymax)
    raw={};rows=collections.Counter()
    try:
        n=int(get(query(k,rect,limit=0))["count"])
        result["live_count"]=n
        if k!="5218465":
            if n>30000:raise RuntimeError("per-species complete-search budget exceeded")
            for offset in range(0,n,300):
                d=get(query(k,rect,limit=300,offset=offset))
                if d["count"]!=n or len(d["results"])!=min(300,n-offset):raise RuntimeError("live count drift or incomplete page")
                for a in d["results"]:
                    if a.get("key") is None or a["key"] in raw:raise RuntimeError("duplicate/missing GBIF key")
                    raw[a["key"]]=({j:a.get(j) for j in fields},rect)
            assert len(raw)==n
            mode="COMPLETE_LIVE_QUERY"
        else:
            # Coverage certificate only. Deterministically take the 24 blocks with smallest
            # positive prior candidate counts >=5. Retrieve at most 300/block; no inference
            # or complete-data claim, and do not combine these with model training data.
            selected=sorted((z for z in prior["blocks"] if z["species_counts"].get(k,0)>=5),
                key=lambda z:(z["species_counts"][k],z["block_x"],z["block_y"]))[:24]
            result["witness_blocks"]=[{"block_x":z["block_x"],"block_y":z["block_y"],"prior_n":z["species_counts"][k]} for z in selected]
            for z in selected:
                d=get(query(k,z["rect"],limit=300))
                if len(d["results"])!=min(300,d["count"]):raise RuntimeError("incomplete witness page")
                for a in d["results"]:
                    if a.get("key") is None:raise RuntimeError("missing GBIF key")
                    if a["key"] not in raw:raw[a["key"]]=({j:a.get(j) for j in fields},z["rect"])
            mode="PARTIAL_COVERAGE_WITNESS_ONLY"
        eligible=0;invalid=0;cells=collections.defaultdict(set)
        with gzip.open(OUT/f"raw_{k}.jsonl.gz","wt",encoding="utf-8") as f:
            for a,rr in raw.values():
                f.write(json.dumps(a,ensure_ascii=False)+"\n")
                c=valid(a,k,rr)
                if c is None:invalid+=1;continue
                eligible+=1;x,y=c;cells[(x//200,y//200)].add(c)
                rows[(k,x,y,str(a["datasetKey"] or ""),str(a["eventDate"] or "")[:4],str(a["license"] or ""))]+=1
        unique_cells=sum(len(v) for v in cells.values());blocks=sum(len(v)>=5 for v in cells.values())
        write_table(OUT/f"cells_{k}.csv.gz",rows)
        result.update({"status":mode,"raw_retrieved":len(raw),"eligible":eligible,"excluded":invalid,"unique_cells":unique_cells,"blocks_ge5":blocks,"provisional_geographic_gate":unique_cells>=30 and blocks>=4,"unique_cells_north_51_6":sum(1 for v in cells.values() for x,y in v if I.transform((x+.5)*1000,(y+.5)*1000)[1]>51.6)})
    except Exception as e:
        result.update({"status":"NONADMISSION_INCOMPLETE","error":type(e).__name__+": "+str(e)[:220]})
    return result
# First acquire smallest species: fastest way to resolve whether the 20-species gate
# can be met. Remaining complete species are still acquired, regardless of outcomes.
todo=sorted(candidates,key=lambda a:(a["records_upper_bound"],a["key"]))
report={"stage":"geographic coverage only, no model","domain_bbox":bbox,"country_whitelist":countries,"candidate_upper_bound":22,"prior_total":314593,"source_sha256":hashlib.sha256(pathlib.Path("block_prior/report.json").read_bytes()).hexdigest(),"start_utc":datetime.now(timezone.utc).isoformat(),"species":[],"limits":["No forest or GVSM mask in this phase.","P. pipistrellus partial witness cannot train an SDM.","North of 51.6 degrees predicted RH extrapolation; independent reporting required.","Complete live searches are not immutable DOI downloads."]}
def checkpoint():
    report["species"].sort(key=lambda a:int(a["species_key"]))
    complete=[a for a in report["species"] if a["status"]=="COMPLETE_LIVE_QUERY"]
    witness=[a for a in report["species"] if a["status"]=="PARTIAL_COVERAGE_WITNESS_ONLY"]
    report.update({"complete_species":len(complete),"complete_records":sum(a["raw_retrieved"] for a in complete),"complete_species_cells":sum(a["unique_cells"] for a in complete),"complete_geographic_pass_species":sum(a["provisional_geographic_gate"] for a in complete),"coverage_witness_pass_species":sum(a["provisional_geographic_gate"] for a in witness),"finished_species":len(report["species"]),"eligible_for_model":False})
    (OUT/"report.json").write_text(json.dumps(report,indent=2))
with ThreadPoolExecutor(max_workers=3) as ex:
    fut=[ex.submit(fetch_species,a) for a in todo]
    for f in as_completed(fut):
        a=f.result();report["species"].append(a);print("SPECIES_COVERAGE="+json.dumps(a),flush=True);checkpoint()
report["status"]="SPECIES_CENSUS_COMPLETE"
checkpoint()
print("TARGETED_EUROPE_REPORT="+json.dumps(report),flush=True)
