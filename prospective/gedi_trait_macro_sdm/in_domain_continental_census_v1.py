"""Coverage only, not fitted SDM. Frozen independent North America / East Asia regions."""
import collections,csv,gzip,hashlib,html,io,json,math,pathlib,re,sys,zipfile
from urllib.parse import quote,urljoin
import duckdb,requests
from pyproj import Transformer
OUT=pathlib.Path("continental_extension");OUT.mkdir(exist_ok=True)
INV=pathlib.Path("fixed/object_inventory.json")
PIN="14692b344c86a9f392f987924921d2c4cc723483a1669d808192d5003b0a3fae"
BASE="https://gbif-public-data.s3.us-east-1.amazonaws.com/"
regions={"North_America":{"countries":["US","CA","MX"],"bbox":[-130,15,-60,51.6]},"East_Asia":{"countries":["CN","JP","MN","KP","KR","TW"],"bbox":[73,15,146,51.6]}}
report={"stage":"independent in-domain source and coverage census only","gbif_doi":"10.15468/dl.8yrbe7","trait_article_doi":"10.3389/fevo.2022.1031548","regions":regions,"status":"START","trait_source":{},"coverage":{},"limits":["Occurrence data are recorded detections, not occupancy/effort or height use.","Provisional spatial coverage before environment/trait/roost screening.","No cross-study or continental ecological fit."]}
def sha(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def save():
    (OUT/"report.json").write_text(json.dumps(report,indent=2))
    print("CONTINENTAL_REPORT="+json.dumps(report),flush=True)
def literal(x):return "'"+str(x).replace("'","''")+"'"
def try_traits():
    url="https://www.frontiersin.org/journals/ecology-and-evolution/articles/10.3389/fevo.2022.1031548/full"
    t=report["trait_source"];t.update(status="DISCOVERING_PUBLISHER_SUPPLEMENT",url=url,published_taxa=152,published_families=15)
    candidates=[]
    try:
        q=requests.get(url,timeout=(15,40));t["article_http"]=q.status_code
        q.raise_for_status()
        h=html.unescape(q.text).replace("\\/","/")
        for u in re.findall(r"""(?:https?://[^"'<>\s\\]+|/files/[^"'<>\s\\]+|/articles/[^"'<>\s\\]+)""",h):
            if re.search(r"1031548.{0,100}(?:s00[1-9]|supplementary).{0,120}\.(?:pdf|xlsx|xls|docx|zip|csv)(?:\?|$)",u,re.I):
                candidates.append(urljoin(url,u))
    except requests.RequestException as e:t["article_error"]=type(e).__name__
    # Published Frontiers supplementary naming conventions, only admitted after actual byte signature.
    if not candidates:
        for ext in ("pdf","xlsx","docx","zip"):
            candidates.append(f"https://www.frontiersin.org/files/Articles/1031548/fevo-10-1031548-HTML/image_m/fevo-10-1031548-s001.{ext}")
    candidates=list(dict.fromkeys(candidates))[:8]
    t["attempted"]=[];t["files"]=[]
    for i,u in enumerate(candidates):
        entry={"url":u}
        try:
            with requests.get(u,stream=True,timeout=(15,30)) as rr:
                entry["http"]=rr.status_code
                if rr.status_code!=200:continue
                raw=bytearray()
                for v in rr.iter_content(65536):
                    raw.extend(v)
                    if len(raw)>15_000_000:raise ValueError("supplement cap")
            v=bytes(raw)
            if v.startswith(b"%PDF"):
                typ="pdf"
            elif v[:2]==b"PK":
                with zipfile.ZipFile(io.BytesIO(v)) as zz:
                    ns=zz.namelist()
                    typ="xlsx" if "xl/workbook.xml" in ns else "docx" if "word/document.xml" in ns else "zip"
            else:entry["error"]="unrecognized original file signature";continue
            p=OUT/f"publisher_supplement_{i+1}.{typ}";p.write_bytes(v)
            rec={"url":u,"file":p.name,"type":typ,"bytes":len(v),"sha256":sha(p)}
            # Inspect tables, do not infer or merge ambiguous numeric columns.
            if typ=="xlsx":
                import openpyxl
                w=openpyxl.load_workbook(p,read_only=True,data_only=True)
                rec["sheets"]=[{"sheet":s.title,"rows":s.max_row,"columns":s.max_column,"first_rows":[[str(x) if x is not None else "" for x in row] for row in s.iter_rows(min_row=1,max_row=min(4,s.max_row),values_only=True)]} for s in w]
            elif typ=="docx":
                from docx import Document
                doc=Document(p)
                rec["tables"]=[{"rows":len(x.rows),"columns":len(x.columns),"first_rows":[[c.text[:150] for c in y.cells] for y in x.rows[:3]]} for x in doc.tables]
            elif typ=="pdf":
                import pymupdf
                doc=pymupdf.open(p)
                rec["pages"]=len(doc);rec["first_page_excerpt"]=doc[0].get_text()[:2200]
            else:
                with zipfile.ZipFile(p) as z:rec["members"]=z.namelist()[:50]
            t["files"].append(rec)
            # A real, inspected supplement is preserved; complete source-table semantics still require review.
            if len(t["files"])>=3:break
            if not any("s002" in x or "s003" in x for x in candidates):break
        except Exception as e:entry["error"]=type(e).__name__+": "+str(e)[:160]
        finally:t["attempted"].append(entry)
    t["status"]="ORIGINAL_SUPPLEMENT_BYTES_READY_SCHEMA_REVIEW" if t["files"] else "NO_VERIFIED_PUBLIC_SUPPLEMENT"
    save()
def main():
    assert sha(INV)==PIN
    objects=json.loads(INV.read_text())
    assert len(objects)==8 and sum(x["size"] for x in objects)==9077637625
    urls=[]
    for o in objects:
        u=BASE+quote(o["key"],safe="/=")
        h=requests.head(u,timeout=(15,30));h.raise_for_status()
        assert int(h.headers["Content-Length"])==o["size"] and h.headers["ETag"].strip('"')==o["etag"].strip('"')
        urls.append(u)
    report["source_inventory_sha256"]=PIN;report["verified_original_objects"]=len(urls)
    con=duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs; SET threads=3; SET memory_limit='4GB'; SET preserve_insertion_order=false")
    source="read_parquet(["+",".join(map(literal,urls))+"], hive_partitioning=false)"
    cols={r[0].lower():r[0] for r in con.execute("DESCRIBE SELECT * FROM "+source).fetchall()}
    required=["gbifid","datasetkey","species","specieskey","order","countrycode","decimallatitude","decimallongitude","coordinateuncertaintyinmeters","eventdate","basisofrecord","occurrencestatus","hasgeospatialissues","license"]
    assert set(required)<=set(cols)
    C=lambda s:'"'+cols[s]+'"'
    common=" AND ".join([C("order")+"='Chiroptera'",C("coordinateuncertaintyinmeters")+" BETWEEN 0.000001 AND 500","TRY_CAST("+C("eventdate")+" AS DATE) BETWEEN DATE '2019-04-17' AND DATE '2023-03-16'","upper(replace(CAST("+C("occurrencestatus")+" AS VARCHAR),' ','')) IN ('PRESENT','DETECTED')","upper(replace(CAST("+C("basisofrecord")+" AS VARCHAR),' ','_')) IN ('HUMAN_OBSERVATION','MACHINE_OBSERVATION','OBSERVATION')","TRY_CAST("+C("hasgeospatialissues")+" AS BOOLEAN)=false",C("species")+" IS NOT NULL",C("specieskey")+" IS NOT NULL",C("gbifid")+" IS NOT NULL"])
    P=Transformer.from_crs(4326,6933,always_xy=True)
    for region,v in regions.items():
        l,b,r,t=v["bbox"];f=common+" AND "+C("countrycode")+" IN ("+",".join(map(literal,v["countries"]))+") AND "+C("decimallongitude")+f" BETWEEN {l} AND {r} AND "+C("decimallatitude")+f" BETWEEN {b} AND {t}"
        # Store the exact eligible subset on the runner; omit recorder names and free-text locations.
        cols2=["gbifid","species","specieskey","decimallongitude","decimallatitude","datasetkey","eventdate","license","countrycode"]
        part=OUT/(region+"_eligible_records.parquet")
        con.execute("COPY (SELECT "+",".join(C(k)+" AS "+k for k in cols2)+" FROM "+source+" WHERE "+f+") TO "+literal(part)+" (FORMAT PARQUET,COMPRESSION ZSTD)")
        local="read_parquet("+literal(part)+")"
        n,nu,sp,ds=con.execute("SELECT count(*),count(DISTINCT gbifid),count(DISTINCT specieskey),count(DISTINCT datasetkey) FROM "+local).fetchone()
        assert n==nu
        if n>3_000_000:raise ValueError("region row budget exceeded")
        data=collections.Counter();cells=collections.defaultdict(lambda:collections.defaultdict(set));names=collections.defaultdict(set)
        query="SELECT species,CAST(specieskey AS VARCHAR),decimallongitude,decimallatitude,CAST(datasetkey AS VARCHAR),year(TRY_CAST(eventdate AS DATE)),CAST(license AS VARCHAR),count(*) FROM "+local+" GROUP BY ALL"
        cur=con.execute(query)
        while True:
            batch=cur.fetchmany(50000)
            if not batch:break
            for name,key,lon,lat,dskey,yr,license,count in batch:
                x,y=P.transform(lon,lat)
                assert math.isfinite(x) and math.isfinite(y)
                cx,cy=math.floor(x/1000),math.floor(y/1000)
                data[(name,key,cx,cy,dskey,int(yr),license)]+=int(count)
                cells[key][(cx//200,cy//200)].add((cx,cy));names[key].add(name)
        assert sum(data.values())==n
        # Do not upload precise raw locations; publish only aggregated support and lineage.
        p=OUT/(region+"_all_bat_species_cell_source_year.csv.gz")
        with gzip.open(p,"wt",encoding="utf8",newline="") as g:
            w=csv.writer(g);w.writerow(["species","snapshot_species_key","cell_x","cell_y","dataset_key","year","license","records"])
            for key,count in sorted(data.items(),key=lambda x:tuple(map(str,x[0]))):w.writerow([*key,count])
        summaries=[]
        for k,bb in sorted(cells.items()):
            ncell=sum(map(len,bb.values()));nb=sum(len(cc)>=5 for cc in bb.values())
            summaries.append({"species_names":sorted(names[k]),"key":k,"cells":ncell,"blocks_ge5":nb,"geographic_pass":ncell>=30 and nb>=4 and len(names[k])==1})
        pp=OUT/(region+"_species_coverage.json");pp.write_text(json.dumps(summaries,indent=2))
        report["coverage"][region]={"unique_records":n,"species_keys":sp,"providers":ds,"species_cells":sum(x["cells"] for x in summaries),"unique_cells":len({(k[2],k[3]) for k in data}),"geographic_pass_species_before_trait_filter":sum(x["geographic_pass"] for x in summaries),"coverage_table_sha256":sha(pp),"cell_source_year_sha256":sha(p),"raw_subset_sha256":sha(part),"trait_gate":"not yet evaluated"}
        part.unlink();save()
    try:try_traits()
    except Exception as e:report["trait_source"].update(status="SUPPLEMENT_ERROR",error=type(e).__name__+": "+str(e)[:220])
    report["status"]="REGIONAL_COVERAGE_COMPLETE_NO_MODEL";save()
if __name__=="__main__":
    try:main()
    except Exception as e:
        report.update(status="INCOMPLETE",error=type(e).__name__+": "+str(e)[:250]);save();raise
