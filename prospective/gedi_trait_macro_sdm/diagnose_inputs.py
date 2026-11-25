"""Diagnose actual acquired data; no change to the frozen model eligibility criteria."""
import csv, collections, hashlib, io, json, math, os, pathlib, re
import requests
ROOT=pathlib.Path("prior_inputs")
OUT=pathlib.Path("input_diagnostics");OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def get(url,**kw):
    r=requests.get(url,timeout=45,headers={"User-Agent":"batter-macro-input-audit/1.0"},**kw)
    r.raise_for_status();return r
def table(raw):
    s=raw.decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(s),dialect=csv.Sniffer().sniff(s[:8192],delimiters=",;\t")))
def good_num(v):
    try:return math.isfinite(float(v)) and float(v)>0
    except (ValueError,TypeError):return False
def normal(x):return " ".join(str(x).replace("_"," ").split())
report={"stage":"diagnostic only, no ecological fit","errors":{}}
def pilot():
    p=ROOT/"gbif_pilot.json"
    assert sha(p)=="42577b98946a3bbe67c8c6516932dc85e208ce9f40746a715fc305c4f0bcea08"
    rows=json.loads(p.read_text())
    kinds={"HUMAN_OBSERVATION","MACHINE_OBSERVATION","OBSERVATION"}
    tests={"species_named":lambda a:bool(a["species"]),"present":lambda a:a["occurrenceStatus"]=="PRESENT","valid_uncertainty_1_to_500":lambda a:isinstance(a["coordinateUncertaintyInMeters"],(int,float)) and 0<a["coordinateUncertaintyInMeters"]<=500,"observation_basis":lambda a:a["basisOfRecord"] in kinds}
    counts={k:sum(f(a) for a in rows) for k,f in tests.items()}
    combos=collections.Counter("|".join(k for k,f in tests.items() if not f(a)) or "PASS" for a in rows)
    return {"n":len(rows),"each_pass":counts,"joint_failure_patterns":dict(combos),"status_counts":dict(collections.Counter(str(a["occurrenceStatus"]) for a in rows)),"basis_counts":dict(collections.Counter(str(a["basisOfRecord"]) for a in rows)),"uncertainty_missing":sum(a["coordinateUncertaintyInMeters"] is None for a in rows),"unique_species_named":len(set(a["species"] for a in rows if a["species"])),"top_dataset_counts":dict(collections.Counter(str(a["datasetKey"]) for a in rows).most_common(12))}
def proxy():
    p=ROOT/"03_morphology.csv";assert sha(p)=="dfadfbccfbfd2753908e28e9db230dd61fe60d00634d58a018a4dcae91f76920"
    rows=table(p.read_bytes());result={}
    for t in ["AspectRatioIndex","WingLoadingIndex"]:
        ss=[a for a in rows if a["verbatimTraitName"]==t and good_num(a["verbatimTraitValue"])]
        result[t]={"numeric_rows":len(ss),"species":len(set(normal(a["verbatimScientificName"]) for a in ss)),"units":dict(collections.Counter(a["verbatimTraitUnit"] for a in ss)),"methods":dict(collections.Counter(a["verbatimTraitMethod"] for a in ss)),"references":dict(collections.Counter(a["ShortReference"] for a in ss))}
    return result
def physical():
    url="https://zenodo.org/records/7226367/files/life%20history%20traits%20european%20bats.csv?download=1"
    raw=get(url).content
    assert hashlib.md5(raw).hexdigest()=="78e40b4d20ace36632576a141c8e431d"
    (OUT/"physical_wing_traits_original.csv").write_bytes(raw)
    rows=table(raw);columns=list(rows[0])
    return {"doi":"10.5281/zenodo.7226367","sha256":hashlib.sha256(raw).hexdigest(),"rows":len(rows),"columns":columns,"first_record":rows[0],"wing_column_nonempty":{k:sum(bool(str(a.get(k,"")).strip()) for a in rows) for k in columns if re.search("wing|aspect",k,re.I)},"note":"Physical definitions checked against record description; numeric coverage and original source reconciliation still required."}
def api():
    base="https://api.gbif.org/v1/occurrence/search"
    tax=get("https://api.gbif.org/v1/species/match",params={"name":"Chiroptera","rank":"ORDER"}).json()
    assert tax["matchType"]=="EXACT"
    p={"taxonKey":tax["usageKey"],"hasCoordinate":"true","hasGeospatialIssue":"false","eventDate":"2019-04-17,2023-03-16","geometry":"POLYGON((-10 35,4 35,4 44,-10 44,-10 35))","limit":0}
    obs=["HUMAN_OBSERVATION","MACHINE_OBSERVATION","OBSERVATION"]
    cases={"raw":{},"present":{"occurrenceStatus":"PRESENT"},"uncertainty":{"coordinateUncertaintyInMeters":"0.000001,500"},"observations":{"basisOfRecord":obs},"strict":{"occurrenceStatus":"PRESENT","coordinateUncertaintyInMeters":"0.000001,500","basisOfRecord":obs,"facet":"speciesKey","facetLimit":100}}
    result={}
    for k,extra in cases.items():
        d=get(base,params={**p,**extra}).json();result[k]={"count":d["count"],"facets":d.get("facets",[])}
    if result["strict"]["count"]:
        d=get(base,params={**p,**cases["strict"],"limit":300}).json()
        rows=d["results"]
        actual=[a for a in rows if a.get("species") and a.get("occurrenceStatus")=="PRESENT" and isinstance(a.get("coordinateUncertaintyInMeters"),(int,float)) and 0<a["coordinateUncertaintyInMeters"]<=500 and a.get("basisOfRecord") in obs]
        result["strict_returned_sample"]={"n":len(rows),"validated_rows":len(actual),"species":dict(collections.Counter(a["species"] for a in actual))}
        # Only report raw identifiers and scientific-name aggregates; not individual location details in logs.
        fields=["key","species","speciesKey","decimalLongitude","decimalLatitude","coordinateUncertaintyInMeters","eventDate","basisOfRecord","datasetKey","occurrenceStatus","license","issues"]
        (OUT/"strict_sample.json").write_text(json.dumps([{k:a.get(k) for k in fields} for a in actual]))
    return result
for n,f in [("pilot_audit",pilot),("euro_indices",proxy),("physical_traits",physical),("gbif_server_filter",api)]:
    try:report[n]=f()
    except Exception as e:report["errors"][n]=type(e).__name__+": "+str(e)[:300]
report["credential_presence"]={k:bool(os.getenv(k)) for k in ["EARTHDATA_TOKEN","EARTHDATA_USERNAME","EARTHDATA_PASSWORD","GBIF_USER","GBIF_PWD","GBIF_USERNAME","GBIF_PASSWORD","GBIF_EMAIL"]}
(OUT/"diagnosis.json").write_text(json.dumps(report,indent=2))
print("DIAGNOSTIC_JSON="+json.dumps(report))
