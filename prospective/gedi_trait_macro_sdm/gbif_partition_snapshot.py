"""GBIF official 2026-08-01 experimental DWCA Parquet, DOI 10.15468/dl.8yrbe7.
Anonymous S3, source partition inventory, fixed query, raw subset and coverage only.
Never merge this August snapshot with November live-search counts.
"""
import collections,csv,gzip,hashlib,json,math,pathlib,sys,time,xml.etree.ElementTree as ET
from datetime import datetime,timezone
from urllib.parse import quote,unquote
import requests,duckdb
from pyproj import Transformer
OUT=pathlib.Path("gbif_fixed_snapshot");OUT.mkdir(exist_ok=True)
BUCKET="https://gbif-public-data.s3.us-east-1.amazonaws.com"
PREFIX="development/2026-08-01-DWCA/p_taxon/"
DOI="10.15468/dl.8yrbe7"
countries="AD AL AT BE BA BG BY HR CZ DK EE FI FR DE GR HU IE IT LV LI LT LU MT MD MC ME NL MK NO PL PT RO SM RS SK SI ES SE CH UA GB VA".split()
BBOX=(-12,35,32,71)
REPORT={"stage":"fixed source extraction, spatial coverage only; no ecological model","snapshot_date":"2026-08-01","doi":DOI,"source_documentation":"https://data-blog.gbif.org/post/extending-parquet-snapshots/","source_prefix":PREFIX,"bbox":BBOX,"countries":countries,"filters":{"order":"Chiroptera","event_dates":["2019-04-17","2023-03-16"],"coordinate_uncertainty_m":[0.000001,500],"occurrence_status":["PRESENT","DETECTED"],"basis":["HUMAN_OBSERVATION","MACHINE_OBSERVATION","OBSERVATION"]},"status":"START","errors":[]}
def save():
    (OUT/"report.json").write_text(json.dumps(REPORT,indent=2))
    print("SNAPSHOT_REPORT="+json.dumps({k:v for k,v in REPORT.items() if k!="objects"}),flush=True)
def list_s3(prefix,delimiter=None):
    token=None;prefixes=[];objects=[];ns={"s":"http://s3.amazonaws.com/doc/2006-03-01/"}
    for _ in range(100):
        q={"list-type":"2","prefix":prefix,"max-keys":1000}
        if delimiter:q["delimiter"]=delimiter
        if token:q["continuation-token"]=token
        r=requests.get(BUCKET+"/",params=q,timeout=40);r.raise_for_status()
        root=ET.fromstring(r.content)
        prefixes.extend(n.findtext("s:Prefix",namespaces=ns) for n in root.findall("s:CommonPrefixes",ns))
        for n in root.findall("s:Contents",ns):
            objects.append({"key":n.findtext("s:Key",namespaces=ns),"size":int(n.findtext("s:Size",namespaces=ns)),"etag":n.findtext("s:ETag",namespaces=ns),"last_modified":n.findtext("s:LastModified",namespaces=ns)})
        if root.findtext("s:IsTruncated",namespaces=ns)!="true":return prefixes,objects
        token=root.findtext("s:NextContinuationToken",namespaces=ns)
        if not token:raise RuntimeError("truncated inventory without continuation token")
    raise RuntimeError("inventory page limit")
def literal(v):return "'"+str(v).replace("'","''")+"'"
def ident(v):return '"'+str(v).replace('"','""')+'"'
def sha(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def main():
    prefixes,_=list_s3(PREFIX,"/")
    REPORT["partition_count"]=len(prefixes)
    REPORT["mammal_partitions"]=[p for p in prefixes if "Mammalia" in unquote(p)]
    # Only select partitions known to contain Chiroptera by taxon path.
    mammal=REPORT["mammal_partitions"]
    explicit=[p for p in mammal if "Chiroptera" in unquote(p)]
    if explicit:
        selected=explicit
        REPORT["partition_rule"]="all explicit Chiroptera partitions"
    else:
        selected=[p for p in mammal if unquote(p.rstrip("/")).split("=")[-1] in ("Animalia_Chordata_Mammalia","Animalia_Chordata_Mammalia__PARTIAL")]
        REPORT["partition_rule"]="Mammalia unpartitioned remainder; order filter required"
    if not selected:raise ValueError("no unambiguous mammal/Chiroptera partition")
    REPORT["selected_partitions"]=selected
    objects=[]
    for p in selected:
        _,oo=list_s3(p)
        objects.extend(o for o in oo if o["key"].endswith(".parquet"))
    objects.sort(key=lambda a:a["key"])
    if not objects or len({o["key"] for o in objects})!=len(objects):raise ValueError("empty or duplicate parquet inventory")
    REPORT["objects"]=objects
    REPORT["source_file_count"]=len(objects);REPORT["source_object_bytes"]=sum(o["size"] for o in objects)
    (OUT/"object_inventory.json").write_text(json.dumps(objects,indent=2))
    REPORT["inventory_sha256"]=sha(OUT/"object_inventory.json")
    REPORT["status"]="INVENTORY_READY";save()
    if len(objects)>300 or REPORT["source_object_bytes"]>80_000_000_000:
        REPORT["status"]="BLOCKED_SOURCE_SCAN_BUDGET";save();return 2
    urls=[BUCKET+"/"+quote(o["key"],safe="/=") for o in objects]
    con=duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs; SET threads=3; SET memory_limit='4GB'; SET preserve_insertion_order=false;")
    # Actual source schema, no guessed column order or taxon-key namespace.
    schema=con.execute("DESCRIBE SELECT * FROM read_parquet("+literal(urls[0])+", hive_partitioning=false)").fetchall()
    cols={r[0].lower():r[0] for r in schema}
    REPORT["schema"]=[{"name":r[0],"type":r[1]} for r in schema]
    (OUT/"schema.json").write_text(json.dumps(REPORT["schema"],indent=2))
    required=["gbifid","datasetkey","species","specieskey","order","countrycode","decimallatitude","decimallongitude","coordinateuncertaintyinmeters","eventdate","basisofrecord","occurrencestatus","hasgeospatialissues","license"]
    if not set(required)<=set(cols):raise ValueError("source schema missing: "+str(sorted(set(required)-set(cols))))
    C=lambda s:ident(cols[s])
    optional=["occurrenceid","eventid","samplingprotocol","establishmentmeans","occurrenceremarks","habitat","individualcount","year","issue","scientificname","taxonkey","taxonomicstatus","recordedby","identificationqualifier","locality","lifeStage","behavior"]
    selected_cols=required+[x.lower() for x in optional if x.lower() in cols and x.lower() not in required]
    projection=", ".join(C(s)+" AS "+ident(s) for s in selected_cols)
    status="upper(replace(CAST("+C("occurrencestatus")+" AS VARCHAR),' ',''))"
    basis="upper(replace(CAST("+C("basisofrecord")+" AS VARCHAR),' ','_'))"
    dates="TRY_CAST("+C("eventdate")+" AS DATE)"
    filters=[
        C("order")+" = 'Chiroptera'",
        C("countrycode")+" IN ("+",".join(map(literal,countries))+")",
        C("decimallongitude")+" BETWEEN -12 AND 32",
        C("decimallatitude")+" BETWEEN 35 AND 71",
        C("coordinateuncertaintyinmeters")+" BETWEEN 0.000001 AND 500",
        dates+" BETWEEN DATE '2019-04-17' AND DATE '2023-03-16'",
        status+" IN ('PRESENT','DETECTED')",
        basis+" IN ('HUMAN_OBSERVATION','MACHINE_OBSERVATION','OBSERVATION')",
        "TRY_CAST("+C("hasgeospatialissues")+" AS BOOLEAN) = false",
        C("species")+" IS NOT NULL",
        C("specieskey")+" IS NOT NULL",
        C("gbifid")+" IS NOT NULL",
    ]
    where=" AND ".join(filters)
    REPORT["sql_filters"]=filters
    REPORT["selected_columns"]=selected_cols
    # Per-file extraction checkpoints; avoid rerunning a large scan from the beginning.
    subset=OUT/"subsets";subset.mkdir(exist_ok=True)
    done=[]
    for i,(obj,url) in enumerate(zip(objects,urls)):
        path=subset/f"part_{i:04d}.parquet"
        sql="COPY (SELECT "+projection+" FROM read_parquet("+literal(url)+", hive_partitioning=false) WHERE "+where+") TO "+literal(path)+" (FORMAT PARQUET, COMPRESSION ZSTD)"
        result=con.execute(sql).fetchone()
        done.append({"object":obj["key"],"rows":int(result[0]),"file":path.name,"sha256":sha(path)})
        REPORT["completed_objects"]=len(done)
        REPORT["extracted_records"]=sum(d["rows"] for d in done)
        (OUT/"checkpoint.json").write_text(json.dumps(done,indent=2))
        print("SNAPSHOT_PART",i+1,len(objects),result[0],flush=True)
    REPORT["subset_manifest_sha256"]=sha(OUT/"checkpoint.json")
    files=[str(subset/d["file"]) for d in done]
    source="read_parquet(["+",".join(map(literal,files))+"], hive_partitioning=false)"
    n,distinct=con.execute("SELECT count(*), count(DISTINCT gbifid) FROM "+source).fetchone()
    if n!=distinct or n!=REPORT["extracted_records"]:raise ValueError("duplicate or missing GBIF IDs")
    REPORT["unique_gbif_ids"]=int(distinct)
    REPORT["dataset_count"]=int(con.execute("SELECT count(DISTINCT datasetkey) FROM "+source).fetchone()[0])
    REPORT["status_counts"]=dict(con.execute("SELECT CAST(occurrencestatus AS VARCHAR),count(*) FROM "+source+" GROUP BY 1").fetchall())
    REPORT["snapshot_species_count"]=int(con.execute("SELECT count(DISTINCT species) FROM "+source).fetchone()[0])
    REPORT["license_counts"]=dict(con.execute("SELECT CAST(license AS VARCHAR), count(*) FROM "+source+" GROUP BY 1").fetchall())
    p=pathlib.Path("occ/physical_trait_crosswalk.csv")
    assert sha(p)=="43bb5284308a9fe732beda51886172cb87268e5d00620eb27956d5808dae809f"
    tr=collections.defaultdict(list)
    with p.open() as f:
        for a in csv.DictReader(f):
            if a["AR"]:tr[" ".join(a["source_name"].split()).casefold()].append(a)
    traits={k:v[0] for k,v in tr.items() if len(v)==1}
    assert len(traits)==28
    P=Transformer.from_crs(4326,6933,always_xy=True)
    all_cells=collections.Counter();trait_cells=collections.defaultdict(lambda:collections.defaultdict(set))
    taxon_names=collections.defaultdict(set);unmatched=collections.Counter()
    for species,key,lon,lat,dataset,year,lic,count in con.execute("SELECT species, CAST(specieskey AS VARCHAR),decimallongitude,decimallatitude,CAST(datasetkey AS VARCHAR),year(TRY_CAST(eventdate AS DATE)),CAST(license AS VARCHAR),count(*) FROM "+source+" GROUP BY ALL").fetchall():
        if not all(map(math.isfinite,(lon,lat))):continue
        x,y=P.transform(lon,lat);cx,cy=math.floor(x/1000),math.floor(y/1000)
        all_cells[(str(species),str(key),cx,cy,str(dataset),int(year),str(lic))]+=int(count)
        name=" ".join(str(species).split()).casefold()
        taxon_names[name].add(str(key))
        if name not in traits:unmatched[str(species)]+=int(count);continue
        trait_cells[name][(cx//200,cy//200)].add((cx,cy))
    # Exact-name provisional only; conflicting snapshot names/keys require taxonomy review.
    out=OUT/"all_bat_species_cell_source_year.csv.gz"
    with gzip.open(out,"wt",encoding="utf-8",newline="") as f:
        w=csv.writer(f);w.writerow(["species","snapshot_species_key","cell_x","cell_y","dataset_key","year","license","records"])
        for row,count in sorted(all_cells.items()):w.writerow([*row,count])
    cov=[]
    for name,t in sorted(traits.items()):
        b=trait_cells[name];cells=sum(map(len,b.values()));blocks=sum(len(x)>=5 for x in b.values())
        cov.append({"species":t["source_name"],"snapshot_species_keys":sorted(taxon_names[name]),"cells":cells,"blocks_ge5":blocks,"provisional_exact_name_pass":cells>=30 and blocks>=4 and len(taxon_names[name])==1})
    REPORT.update({"status":"FIXED_SNAPSHOT_EXTRACTED","target_group_records":sum(all_cells.values()),"target_group_species_cells":len({(k,x,y) for _,k,x,y,*_ in all_cells}),"target_group_cells":len({(x,y) for _,_,x,y,*_ in all_cells}),"output_sha256":sha(out),"physical_traits_geographic_pass":sum(c["provisional_exact_name_pass"] for c in cov),"species_coverage":cov,"unmatched_names":dict(unmatched),"limitations":["Official experimental 2026-08-01 DWCA snapshot (not November live query). Do not combine with November snapshots.","Exact-name trait crosswalk provisional; confirm snapshot COL keys and synonyms.","Missing/ambiguous event dates excluded; snapshot query semantics may differ from interval-based live search.","Source-specific effort, roost/captive status, environment and 20-species forest gate not verified.","Publish snapshot DOI and derived dataset with dataset keys; no SDM fitted."]})
    save();return 0
if __name__=="__main__":
    try:sys.exit(main())
    except Exception as exc:
        REPORT.update(status="INCOMPLETE",error=type(exc).__name__+": "+str(exc)[:300]);save();raise
