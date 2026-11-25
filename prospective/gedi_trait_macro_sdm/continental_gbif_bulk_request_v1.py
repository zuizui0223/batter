"""Official GBIF bulk request, validated query only. Never log credentials or raw rows."""
import hashlib,json,os,pathlib,re
import requests
R=pathlib.Path(__file__).resolve().parent
O=pathlib.Path("continental_bulk_request");O.mkdir(exist_ok=True)
q=json.loads((R/"continental_gbif_search_parameters_v1.json").read_text())
candidate=json.loads((R/"continental_gbif_dwca_candidate_v1.json").read_text())
s=requests.Session();s.headers["User-Agent"]="batter-continental-doi/1.0"
base="https://api.gbif.org/v1/"
report={"stage":"query verification and at most one bulk request","scope":"same region and observation criteria, all Chiroptera for target-group support; no ecological fit","status":"START"}
def save():
    (O/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    print("BULK_REQUEST_REPORT="+json.dumps(report),flush=True)
def flat(p):
    if p.get("type")=="and":return [x for y in p["predicates"] for x in flat(y)]
    return [p]
def values(p):
    if p.get("type")=="equals":return p["key"],{str(p["value"]).lower() if isinstance(p["value"],bool) else str(p["value"])}
    if p.get("type")=="in":return p["key"],{str(x) for x in p["values"]}
    if p.get("type")=="or":
        a=[values(x) for x in p["predicates"]]
        if len({x[0] for x in a})!=1:raise ValueError("mixed-field disjunction")
        return a[0][0],set().union(*(v for _,v in a))
    raise ValueError("unexpected membership predicate")
def ring(w):
    m=re.fullmatch(r"\s*POLYGON\s*\(\((.*)\)\)\s*",w,re.I)
    if not m:raise ValueError("geometry not polygon")
    xy=[tuple(map(float,x.split())) for x in m[1].split(",")]
    if len(xy)!=5 or xy[0]!=xy[-1]:raise ValueError("unexpected polygon")
    return xy[:-1]
def check(p):
    want={"TAXON_KEY":{"734"},"COUNTRY":set(q["country"]),"HAS_COORDINATE":{"true"},"HAS_GEOSPATIAL_ISSUE":{"false"},"OCCURRENCE_STATUS":{"DETECTED"},"BASIS_OF_RECORD":set(q["basisOfRecord"])}
    seen={};ranges={};ng=0
    for a in flat(p):
        typ=a.get("type");k=a.get("key")
        if typ=="within":
            b=ring(q["geometry"]);c=ring(a["geometry"])
            if not any(c==b[i:]+b[:i] for i in range(4)):raise ValueError("geometry mismatch")
            ng+=1;continue
        if k in {"EVENT_DATE","COORDINATE_UNCERTAINTY_IN_METERS"}:
            if typ=="equals" and "," in str(a.get("value","")):
                lo,hi=str(a["value"]).split(",")
                z=[("greaterThanOrEquals",lo),("lessThanOrEquals",hi)]
            elif typ in {"greaterThanOrEquals","lessThanOrEquals"}:z=[(typ,str(a["value"]))]
            else:raise ValueError("unrecognized range")
            for op,v in z:
                if (k,op) in ranges:raise ValueError("duplicate range")
                ranges[k,op]=v
        else:
            k,v=values(a)
            if k in seen or k not in want:raise ValueError("duplicate or unexpected field")
            seen[k]=v
    if seen!=want or ng!=1:raise ValueError("membership or geometry mismatch")
    expected={("EVENT_DATE","greaterThanOrEquals"):"2019-04-17",("EVENT_DATE","lessThanOrEquals"):"2023-03-16",("COORDINATE_UNCERTAINTY_IN_METERS","greaterThanOrEquals"):"0.000001",("COORDINATE_UNCERTAINTY_IN_METERS","lessThanOrEquals"):"500"}
    if set(ranges)!=set(expected):raise ValueError("range keys mismatch")
    for k,v in expected.items():
        if k[0]=="EVENT_DATE":
            if ranges[k]!=v:raise ValueError("date conversion requires inspection")
        elif float(ranges[k])!=float(v):raise ValueError("precision mismatch")
    return True
u=os.environ.get("GBIF_USERNAME") or os.environ.get("GBIF_USER")
pw=os.environ.get("GBIF_PASSWORD") or os.environ.get("GBIF_PWD")
report["credentials_present"]={"username":bool(u),"password":bool(pw)}
try:
    check(candidate["predicate"])
    r=s.get(base+"occurrence/search",params={**q,"limit":0},timeout=(15,60))
    report["count_http"]=r.status_code;r.raise_for_status()
    report["all_chiroptera_live_count"]=int(r.json()["count"])
    r=s.get(base+"occurrence/download/request/predicate",params=q,timeout=(15,60))
    report["conversion_http"]=r.status_code;r.raise_for_status()
    z=r.json();p=z.get("predicate",z)
    (O/"server_predicate.json").write_text(json.dumps(p,indent=2)+"\n")
    check(p);report["predicate_check"]="PASS"
except Exception as e:
    report.update(status="STOP_QUERY_VALIDATION",error_type=type(e).__name__,reason=str(e)[:240])
    save();raise SystemExit(0)
body={"format":"DWCA","sendNotification":False,"predicate":p}
(O/"gbif_dwca_request.json").write_text(json.dumps(body,indent=2)+"\n")
report["request_sha256"]=hashlib.sha256((O/"gbif_dwca_request.json").read_bytes()).hexdigest()
if not(u and pw):
    report["status"]="STOP_GBIF_CREDENTIALS_MISSING";save();raise SystemExit(0)
# Do not retry a possibly accepted POST. Creator is only sent to GBIF, never saved.
try:
    r=s.post(base+"occurrence/download/request",json={**body,"creator":u},auth=(u,pw),timeout=(15,90),allow_redirects=False)
    report["request_http"]=r.status_code
    if r.status_code not in (200,201,202):report["status"]="STOP_REQUEST_REJECTED"
    else:
        key=r.text.strip().strip('"')
        if re.fullmatch(r"\d{5,}-\d{12,}",key):
            report.update(status="REQUEST_ACCEPTED_NOT_YET_ADMITTED",download_key=key,download_page="https://www.gbif.org/occurrence/download/"+key)
        else:report["status"]="STOP_AMBIGUOUS_RESPONSE_CHECK_ACCOUNT"
except requests.RequestException as e:
    report.update(status="STOP_AMBIGUOUS_POST_CHECK_ACCOUNT_BEFORE_RETRY",error_type=type(e).__name__)
save()
