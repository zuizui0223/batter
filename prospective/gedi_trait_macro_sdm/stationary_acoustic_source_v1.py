"""Source-only official public ScienceBase inventory and bounded table/schema audit."""
import csv,hashlib,io,json,pathlib,re,urllib.parse,collections
import requests
O=pathlib.Path("stationary_acoustic_gate");O.mkdir(exist_ok=True)
R={"stage":"independent stationary acoustic original source audit","status":"START","sources":{},"limits":["No absence inferred from missing detections; no raw locations or identities exported.","No raw audio, biological fit, or primary SDM admission."]}
S=requests.Session();S.headers["User-Agent"]="batter-source-audit/1.0 (research)"
MAXFILE=25*1024**2;MAXTOTAL=120*1024**2;total=0;file_count=0
def save():
    (O/"report.json").write_text(json.dumps(R,indent=2,allow_nan=False)+"\n")
    print("STATIONARY_SOURCE_REPORT="+json.dumps(R,allow_nan=False),flush=True)
def allowed(u):
    p=urllib.parse.urlparse(u)
    return p.scheme=="https" and bool(p.hostname) and (p.hostname.endswith(".usgs.gov") or p.hostname=="usgs.gov" or p.hostname in ("sciencebase.gov","www.sciencebase.gov") or p.hostname=="doi.org" or p.hostname.endswith(".amazonaws.com"))
def bounded(u,limit,headers=None):
    if not allowed(u):return {"status":"STOP_UNVERIFIED_HOST"},None
    try:
        with S.get(u,headers=headers or {},timeout=(15,60),stream=True,allow_redirects=True) as r:
            d={"http":r.status_code,"content_type":r.headers.get("content-type"),"content_length":r.headers.get("content-length")}
            if r.status_code in (401,403):return {**d,"status":"ACCESS_DENIED_STOP"},None
            if not r.ok or not allowed(r.url):return {**d,"status":"HTTP_OR_HOST_STOP"},None
            chunks=[];n=0
            for q in r.iter_content(65536):
                n+=len(q)
                if n>limit:return {**d,"status":"SIZE_CAP_STOP"},None
                chunks.append(q)
            b=b"".join(chunks)
            return {**d,"status":"READ","bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()},b
    except Exception as e:return {"status":"TRANSPORT_STOP","error_type":type(e).__name__},None
def schema(raw,partial=False):
    try:
        txt=raw.decode("utf-8-sig")
        if txt.lstrip().startswith(("<!DOCTYPE","<html","<HTML")):return {"status":"HTML_NOT_TABLE"}
        dialect=csv.Sniffer().sniff(txt[:8192],delimiters=",;\t")
        reader=csv.reader(io.StringIO(txt),dialect)
        cols=next(reader);n=0;ragged=0;nonempty=[0]*len(cols)
        for row in reader:
            n+=1
            if len(row)!=len(cols):ragged+=1;continue
            for i,v in enumerate(row):nonempty[i]+=int(bool(v.strip()))
        fields={kind:[c for c in cols if re.search(pattern,c,re.I)] for kind,pattern in {
            "site":r"site|station|detector|location|plot",
            "date":r"date|night|start|end|time|year",
            "effort":r"effort|operat|duration|hours|minutes|uptime|deploy|survey|recording",
            "coordinates":r"lat|lon|easting|northing|coord|utm|grid",
            "species_or_label":r"species|taxon|label|classif|identif|scientific|bat|call",
            "counts":r"count|detect|pass|presence|absence|number|activity",
            "review":r"manual|review|vet|valid|confidence|quality|protocol|method",
            "height":r"height|elev|canopy|stratum|microphone"}.items()}
        return {"status":"TABLE_SCHEMA_ONLY","partial_prefix":partial,"columns":cols,"rows_read":n,"ragged_rows":ragged,"nonempty_counts":dict(zip(cols,nonempty)),"design_fields":fields}
    except Exception as e:return {"status":"TABLE_PARSE_STOP","error_type":type(e).__name__}
def item(id):
    d,b=bounded("https://www.sciencebase.gov/catalog/item/"+id+"?format=json",2*1024**2)
    if b is None:return d,None
    try:
        j=json.loads(b);assert j.get("id")==id
        return d,j
    except Exception as e:return {**d,"status":"ITEM_JSON_STOP","error_type":type(e).__name__},None
def inspect(id):
    global total,file_count
    rec,j=item(id);out={"id":id,"metadata":rec,"files":[]}
    if j is None:return out,[]
    out.update(title=j.get("title"),has_children=j.get("hasChildren"),file_inventory=[{"name":f.get("name"),"size":f.get("size"),"contentType":f.get("contentType")} for f in j.get("files",[])])
    for f in j.get("files",[]):
        n=str(f.get("name") or "");u=f.get("url");sz=f.get("size")
        if not u or file_count>=30 or total>=MAXTOTAL:continue
        if not re.search(r"\.(csv|tsv|txt|md|xml)$",n,re.I):continue
        if not isinstance(sz,int):
            try:sz=int(sz)
            except:continue
        if sz<0:continue
        partial=sz>MAXFILE and bool(re.search(r"manifest.*\.csv$",n,re.I))
        if sz>MAXFILE and not partial:continue
        if not partial and sz>MAXTOTAL-total:continue
        file_count+=1
        result,b=bounded(u,65536 if partial else min(MAXFILE,MAXTOTAL-total),{"Range":"bytes=0-65535"} if partial else None)
        r={"name":n,"catalog_size":sz,"transfer":result}
        if b is not None:
            total+=len(b)
            if partial and result["http"]!=206:r["status"]="RANGE_NOT_HONORED_STOP"
            elif not partial and len(b)!=sz:r["status"]="SIZE_MISMATCH_STOP"
            elif re.search(r"\.(csv|tsv)$",n,re.I):r["schema"]=schema(b,partial)
            else:
                # Documentation excerpt limited to lines about design/column semantics, no coordinate rows.
                try:
                    t=b.decode("utf-8-sig")
                    r["documentation_design_lines"]=[s[:400] for s in t.splitlines() if re.search(r"\b(effort|night|non.?detect|detector|deployment|species|manual|review|site|station|grid|coordinate|height|duration)\b",s,re.I) and not re.search(r"[-+]?\d{2,3}\.\d{3,}",s)][:40]
                except UnicodeError:r["status"]="DOCUMENTATION_DECODE_STOP"
        out["files"].append(r)
    kids=[]
    if j.get("hasChildren"):
        # Official ScienceBase public child query for verified parent.
        url="https://www.sciencebase.gov/catalog/items?"+urllib.parse.urlencode({"parentId":id,"format":"json","max":10})
        c,b=bounded(url,2*1024**2);out["children_query"]=c
        if b is not None:
            try:
                data=json.loads(b)
                kids=[i["id"] for i in data.get("items",[]) if re.fullmatch(r"[0-9a-f]{24}",str(i.get("id","")))]
                out["child_inventory"]=[{"id":i.get("id"),"title":i.get("title")} for i in data.get("items",[])]
            except Exception as e:out["children_parse_error"]=type(e).__name__
    return out,kids
for name,parent,doi,known in [
    ("washington_parks","681d4453d4be0209b5cbb5b1","10.5066/P149M8V5",["682b943fd4be024992ebd7ba","682b942fd4be024992ebd7b5"]),
    ("nabat_october_2026","6ace802b1ba49b69a5819e47","10.5066/P1HDZNY9",[])]:
    obj={"doi":doi,"items":[]};R["sources"][name]=obj
    v,kids=inspect(parent);obj["items"].append(v);save()
    for i in list(dict.fromkeys(known+kids))[:10]:
        v,_=inspect(i);obj["items"].append(v);save()
R.update(status="SOURCE_GATE_FINISHED_NO_FIT",total_table_document_bytes=total,files_attempted=file_count)
save()
