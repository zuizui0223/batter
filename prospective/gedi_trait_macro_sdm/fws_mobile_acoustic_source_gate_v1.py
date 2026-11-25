"""FWS ServCat public source schema audit. Never execute Access macros."""
import collections,csv,hashlib,io,json,pathlib,re,subprocess,sys,time
import requests
OUT=pathlib.Path("fws_acoustic_source");OUT.mkdir(exist_ok=True)
P=pathlib.Path("fws_private.accdb")
URL="https://iris.fws.gov/APPS/ServCat/DownloadFile/266378?Reference=73052"
CAP=500_000_000
R={"stage":"public FWS original mobile acoustic source and schema audit, no ecological fit","official_catalog":"https://catalog.data.gov/dataset/mobile-acoustic-bat-monitoring-data-for-national-wildlife-refuges-in-regions-2-3-and-4","source_url":URL,"reference":73052,"status":"START","tables":{},"limits":["No observed locations or raw source rows exported.","Mobile road-transect records are not stationary detector surveys.","Schema alone does not establish actual effort, positional accuracy, taxon validity, non-detections or model eligibility."]}
def save():
    (OUT/"report.json").write_text(json.dumps(R,indent=2,allow_nan=False))
    print("FWS_ACOUSTIC_REPORT="+json.dumps(R,allow_nan=False),flush=True)
def call(*a,timeout=90):
    return subprocess.run(list(a),check=True,capture_output=True,text=True,encoding="utf8",errors="replace",timeout=timeout).stdout
def acquire():
    try:
        with requests.get(URL,stream=True,timeout=(20,90),headers={"User-Agent":"batter-public-science/1.0","Accept-Encoding":"identity"}) as q:
            R["http"]={"status":q.status_code,"final_host":q.url.split("/")[2],"content_type":q.headers.get("Content-Type"),"etag":q.headers.get("ETag"),"last_modified":q.headers.get("Last-Modified"),"content_length":q.headers.get("Content-Length")}
            save()
            q.raise_for_status()
            n=q.headers.get("Content-Length")
            if n is not None and int(n)>CAP:raise ValueError("public database exceeds fixed byte cap")
            total=0;h=hashlib.sha256()
            with P.open("wb") as p:
                for data in q.iter_content(1024*1024):
                    if not data:continue
                    total+=len(data)
                    if total>CAP:raise ValueError("download cap exceeded")
                    h.update(data);p.write(data)
            with P.open("rb") as p:header=p.read(128)
            assert b"Standard ACE DB" in header or b"Standard Jet DB" in header,"not an Access database"
            if n is not None:assert total==int(n)
            R.update(original_bytes=total,source_sha256=h.hexdigest(),actual_format="ACE" if b"Standard ACE DB" in header else "Jet",status="ORIGINAL_DATABASE_READY")
            save()
    except Exception:
        P.unlink(missing_ok=True);raise
def inspect():
    names=[x.strip() for x in call("mdb-tables","-1",str(P)).splitlines() if x.strip()]
    names=[x for x in names if not x.lower().startswith(("msys","usys"))]
    assert names and len(names)<=200
    R["table_inventory"]=names;R["mdb_version"]=call("mdb-ver",str(P)).strip();save()
    for name in names:
        fields={};n=None
        try:
            # mdb-schema only reads schema; preserve actual column/type definitions.
            schema=call("mdb-schema","-T",name,str(P),"postgres")
            # Capture CREATE TABLE fields without treating defaults as measured values.
            columns=[]
            for line in schema.splitlines():
                a=re.match(r'^\s*["\x60]([^"\x60]+)["\x60]\s+(.+?)(?:,\s*)?$',line)
                if a and not a[1].lower().startswith("constraint"):
                    columns.append({"name":a[1],"sql_type":a[2][:160]})
            n=int(call("mdb-count",str(P),name,timeout=120).strip())
            groups={"coordinate":r"lat|lon|easting|northing|coord|gps|utm|point","date_time":r"date|time|year|night|start|end","taxon":r"species|taxon|sciname|scientific|ident|code|class","effort":r"effort|duration|distance|length|speed|survey|route|transect|detector|weather","identifier":r"id$|^id|key|guid|route|survey|file"}
            fields={"rows":n,"columns":columns,"field_candidates":{k:[v["name"] for v in columns if re.search(p,v["name"],re.I)] for k,p in groups.items()},"schema_sha256":hashlib.sha256(schema.encode()).hexdigest()}
            # When table is reasonably sized, stream rows and count column nulls.
            # No field values emitted, except counts and names. No interpretation of labels.
            if n<=2_000_000:
                proc=subprocess.Popen(["mdb-export",str(P),name],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,encoding="utf8",errors="replace",newline=None) if False else subprocess.Popen(["mdb-export",str(P),name],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,encoding="utf8",errors="replace")
                try:
                    reader=csv.reader(proc.stdout)
                    header=next(reader,[])
                    nulls=[0]*len(header);read_rows=0;malformed=0
                    for row in reader:
                        read_rows+=1
                        if len(row)!=len(header):malformed+=1;continue
                        for j,v in enumerate(row):
                            nulls[j]+=not v.strip()
                    rc=proc.wait(timeout=30)
                    fields.update(export_columns=header,export_rows=read_rows,malformed_rows=malformed,null_or_empty_by_column=dict(zip(header,nulls)),read_exit=rc)
                finally:
                    if proc.poll() is None:proc.kill()
            R["tables"][name]=fields
        except Exception as e:R["tables"][name]={"rows_if_known":n,"error_type":type(e).__name__,"status":"SCHEMA_OR_EXPORT_STOP"}
        print("FWS_TABLE",name,json.dumps(R["tables"][name],ensure_ascii=True),flush=True)
    R["status"]="SCHEMA_READY_REQUIRES_RELATION_AND_EFFORT_AUDIT"
    R["n_tables"]=len(names);R["n_tables_with_rows"]=sum("rows" in v for v in R["tables"].values())
    save()
if __name__=="__main__":
    try:acquire();inspect()
    except Exception as e:
        R.update(status="INCOMPLETE",error_type=type(e).__name__,error=str(e)[:300]);save();raise
    finally:P.unlink(missing_ok=True)
