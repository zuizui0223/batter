"""Fixed-source diagnosis only; no loosening of occurrence admission.
Separate USGS public metadata gate: no waveform downloads or assumed locations.
"""
import collections,hashlib,json,math,pathlib,re,sys
from urllib.parse import quote
import duckdb,requests
OUT=pathlib.Path("continental_attrition");OUT.mkdir(exist_ok=True)
INV=pathlib.Path("fixed/object_inventory.json")
PIN="14692b344c86a9f392f987924921d2c4cc723483a1669d808192d5003b0a3fae"
BASE="https://gbif-public-data.s3.us-east-1.amazonaws.com/"
REGIONS={
 "Europe":{"countries":"AD AL AT BE BA BG BY HR CZ DK EE FI FR DE GR HU IE IT LV LI LT LU MT MD MC ME NL MK NO PL PT RO SM RS SK SI ES SE CH UA GB VA".split(),"bbox":[-12,35,32,71],"expected":219960},
 "North_America":{"countries":["US","CA","MX"],"bbox":[-130,15,-60,51.6],"expected":5514},
 "East_Asia":{"countries":["CN","JP","MN","KP","KR","TW"],"bbox":[73,15,146,51.6],"expected":389}}
report={"stage":"GBIF fixed snapshot source attrition and public monitoring-source metadata diagnosis, no ecological fit","gbif_doi":"10.15468/dl.8yrbe7","inventory_sha256":PIN,"regions":{},"nabat":{},"status":"START","limits":["All exclusions are reported, not replaced by new eligibility rules.","Records missing coordinate uncertainty are not precise coordinates by assumption.","NABat audio detections are not complete surveys, detector-height observations, or true absences. Public metadata access is not proof of usable 1km coordinates."]}
def sha(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def save():
    (OUT/"report.json").write_text(json.dumps(report,indent=2,allow_nan=False))
    print("ATTRITION_REPORT="+json.dumps(report,allow_nan=False),flush=True)
def lit(v):return "'"+str(v).replace("'","''")+"'"
def audit():
    assert sha(INV)==PIN
    objects=json.loads(INV.read_text())
    assert len(objects)==8 and sum(x["size"] for x in objects)==9077637625
    urls=[]
    for o in objects:
        u=BASE+quote(o["key"],safe="/=")
        h=requests.head(u,timeout=(15,30));h.raise_for_status()
        assert int(h.headers["Content-Length"])==o["size"] and h.headers["ETag"].strip('"')==o["etag"].strip('"')
        urls.append(u)
    con=duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs; SET threads=3; SET memory_limit='4GB'; SET preserve_insertion_order=false")
    src="read_parquet(["+",".join(map(lit,urls))+"], hive_partitioning=false)"
    cols={r[0].lower():r[0] for r in con.execute("DESCRIBE SELECT * FROM "+src).fetchall()}
    required=["gbifid","datasetkey","species","specieskey","order","countrycode","decimallatitude","decimallongitude","coordinateuncertaintyinmeters","eventdate","basisofrecord","occurrencestatus","hasgeospatialissues","license"]
    assert set(required)<=set(cols)
    C=lambda k:'"'+cols[k]+'"'
    projection=", ".join(C(k)+" AS "+k for k in required if k!="order")
    checks=[
        ("date","TRY_CAST(eventdate AS DATE) BETWEEN DATE '2019-04-17' AND DATE '2023-03-16'"),
        ("detection","upper(replace(CAST(occurrencestatus AS VARCHAR),' ','')) IN ('PRESENT','DETECTED')"),
        ("observation_basis","upper(replace(CAST(basisofrecord AS VARCHAR),' ','_')) IN ('HUMAN_OBSERVATION','MACHINE_OBSERVATION','OBSERVATION')"),
        ("geospatial_qc","TRY_CAST(hasgeospatialissues AS BOOLEAN)=false"),
        ("named_species_and_record_id","species IS NOT NULL AND specieskey IS NOT NULL AND gbifid IS NOT NULL"),
        ("positive_uncertainty_le_500m","coordinateuncertaintyinmeters BETWEEN 0.000001 AND 500")]
    for name,region in REGIONS.items():
        l,b,r,t=region["bbox"]
        where=C("order")+"='Chiroptera' AND "+C("countrycode")+" IN ("+",".join(map(lit,region["countries"]))+") AND "+C("decimallongitude")+f" BETWEEN {l} AND {r} AND "+C("decimallatitude")+f" BETWEEN {b} AND {t}"
        # Count historical rows without materializing them; materialize only the frozen dates.
        date_filter="TRY_CAST("+C("eventdate")+" AS DATE) BETWEEN DATE '2019-04-17' AND DATE '2023-03-16'"
        n,nd=con.execute("SELECT count(*), count(*) FILTER (WHERE "+date_filter+") FROM "+src+" WHERE "+where).fetchone()
        report["regions"][name]={"historical_coordinate_rows":int(n),"within_frozen_date_rows":int(nd),"status":"DATE_COUNT_READY"};save()
        if nd>4_000_000:raise RuntimeError("within-date audit row budget exceeded: "+str(nd))
        con.execute("CREATE OR REPLACE TEMP TABLE regional AS SELECT "+projection+" FROM "+src+" WHERE "+where+" AND "+date_filter)
        assert con.execute("SELECT count(*) FROM regional").fetchone()[0]==nd
        current="TRUE"
        rows=[{"step":"regional_named_order_with_numeric_coordinates","records":n},{"step":"date","records":nd,"lost_at_step":n-nd}]
        for key,check in checks[1:]:
            current+=" AND ("+check+")"
            nn=con.execute("SELECT count(*) FROM regional WHERE "+current).fetchone()[0]
            rows.append({"step":key,"records":nn,"lost_at_step":rows[-1]["records"]-nn})
        assert rows[-1]["records"]==region["expected"],(name,rows)
        noncoord=" AND ".join("("+c+")" for _,c in checks[:-1])
        uncertainty="CASE WHEN coordinateuncertaintyinmeters IS NULL THEN 'missing' WHEN NOT isfinite(coordinateuncertaintyinmeters) THEN 'nonfinite' WHEN coordinateuncertaintyinmeters<=0 THEN 'nonpositive' WHEN coordinateuncertaintyinmeters<0.000001 THEN 'positive_below_floor' WHEN coordinateuncertaintyinmeters<=500 THEN 'accepted_0_500' WHEN coordinateuncertaintyinmeters<=1000 THEN 'gt500_le1000' WHEN coordinateuncertaintyinmeters<=5000 THEN 'gt1000_le5000' WHEN coordinateuncertaintyinmeters<=10000 THEN 'gt5000_le10000' ELSE 'gt10000' END"
        unc=con.execute("SELECT "+uncertainty+" bucket,count(*),count(DISTINCT specieskey),count(DISTINCT datasetkey) FROM regional WHERE "+noncoord+" GROUP BY 1 ORDER BY 2 DESC").fetchall()
        bysource=con.execute("SELECT CAST(datasetkey AS VARCHAR),count(*) AS n,count(*) FILTER (WHERE coordinateuncertaintyinmeters BETWEEN 0.000001 AND 500),count(*) FILTER (WHERE coordinateuncertaintyinmeters IS NULL),count(DISTINCT specieskey) FROM regional WHERE "+noncoord+" GROUP BY 1 ORDER BY n DESC").fetchall()
        # Coverage under alternative uncertainty definitions is NOT admitted; diagnostic counts only.
        srcs=[{"dataset_key":x[0],"pre_uncertainty_records":x[1],"admitted_records":x[2],"uncertainty_missing":x[3],"species":x[4]} for x in bysource]
        p=OUT/(name+"_provider_attrition.json");p.write_text(json.dumps(srcs,indent=2))
        report["regions"][name]={"steps":rows,"uncertainty_buckets":[{"bucket":v[0],"records":v[1],"species":v[2],"providers":v[3]} for v in unc],"pre_uncertainty_providers":len(srcs),"admitted_providers":sum(x["admitted_records"]>0 for x in srcs),"top_pre_uncertainty_providers":srcs[:5],"provider_table_sha256":sha(p),"original_gate_count_reproduced":True}
        save()
def nabat():
    t=report["nabat"]
    t.update(doi="10.5066/P1HDZNY9",publication_date="2026-10-15",stage="public metadata only",requests=[],public_file_candidates=[])
    urls=[
      "https://data.usgs.gov/datacatalog/metadata/USGS.6ace802b1ba49b69a5819e47.xml",
      "https://www.sciencebase.gov/catalog/item/6ace802b1ba49b69a5819e47?format=json",
      "https://doi.org/10.5066/P1HDZNY9"]
    for i,url in enumerate(urls):
        rec={"url":url}
        try:
            with requests.get(url,timeout=(15,30),stream=True) as r:
                rec.update(http=r.status_code,final_url=r.url,content_type=r.headers.get("Content-Type"))
                if r.status_code!=200:continue
                raw=bytearray()
                for buf in r.iter_content(65536):
                    raw.extend(buf)
                    if len(raw)>5_000_000:raise ValueError("metadata exceeds 5MB budget")
            p=OUT/f"nabat_metadata_{i}.txt";p.write_bytes(raw)
            rec.update(bytes=len(raw),sha256=sha(p))
            s=raw.decode("utf8",errors="replace")
            hits=[x for x in re.findall(r'https?://[^\s"<>]+',s) if re.search(r"manifest|README|nabat|s3\.|amazonaws",x,re.I)]
            t["public_file_candidates"].extend(hits[:30])
            if i==1:
                try:
                    obj=json.loads(s)
                    rec["title"]=obj.get("title")
                    rec["files"]=[{k:f.get(k) for k in ["name","url","size","contentType","checksum"]} for f in obj.get("files",[])]
                    rec["webLinks"]=obj.get("webLinks",[])[:20]
                except (ValueError,AttributeError):pass
            # Field mentions are documentation clues, not an admitted schema.
            rec["mentions"]={k:bool(re.search(k,s,re.I)) for k in ["latitude","longitude","GRTS","coordinate","location","manifest","station","deployment","survey"]}
        except Exception as e:rec["error"]=type(e).__name__+": "+str(e)[:220]
        finally:t["requests"].append(rec);save()
    t["public_file_candidates"]=list(dict.fromkeys(t["public_file_candidates"]))
    t["status"]="METADATA_RETRIEVED_REQUIRES_SCHEMA" if any(x.get("bytes") for x in t["requests"]) else "PUBLIC_METADATA_ACCESS_STOP"
    t["admitted_for_1km_model"]=False
    save()
if __name__=="__main__":
    try:
        try:nabat()
        except Exception as e:report["nabat"].update(status="METADATA_ERROR",error=type(e).__name__+": "+str(e)[:220]);save()
        audit()
        report["status"]="ATTRITION_DIAGNOSIS_COMPLETE";save()
    except Exception as e:
        report.update(status="INCOMPLETE",error=type(e).__name__+": "+str(e)[:300]);save();raise
