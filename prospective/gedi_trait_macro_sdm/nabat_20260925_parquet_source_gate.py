"""Official 2026-09-25 NABat manifest, species information and species list.
No raw coordinates, audio, sensitive occurrence rows, or access tokens in outputs.
No assumed precise locations, effort, absences, or original-model admission.
"""
import collections,hashlib,json,pathlib,re,sys
import pyarrow.parquet as pq
import requests
OUT=pathlib.Path("nabat_source_gate");OUT.mkdir(exist_ok=True)
CACHE=pathlib.Path("nabat_public_tables_cache");CACHE.mkdir(exist_ok=True)
ITEM="https://www.sciencebase.gov/catalog/item/6ace802b1ba49b69a5819e47?format=json"
SPECS={
 "README.md":18336,
 "nabat-acoustic-data-species-list-20260925.parquet":24922,
 "nabat-acoustic-data-manifest-20260925.parquet":339365848,
 "nabat-acoustic-data-species-information-20260925.parquet":330795308,
}
R={"stage":"original public NABat tabular schema audit, no ecological fit","doi":"10.5066/P1HDZNY9","metadata_date":"2026-09-25","status":"START","files":{},"tables":{},"limits":["Public table locations must be used at their documented spatial grain; never reconstruct intentionally obscured locations.","A recording-label manifest is not a survey checklist or verified detector uptime. Missing rows do not imply non-detection.","No raw coordinates, species occurrence rows, filenames or signed access URLs in audit artifacts.","No automatic pooling with GBIF, original 20-species admission or biological altitude inference."]}
def save():
    (OUT/"report.json").write_text(json.dumps(R,indent=2,allow_nan=False))
    print("NABAT_GATE="+json.dumps(R,allow_nan=False),flush=True)
def digest(p,kind):
    with p.open("rb") as f:return hashlib.file_digest(f,kind).hexdigest()
def acquire(info):
    name=info["name"];size=SPECS[name];assert int(info["size"])==size
    p=CACHE/name
    # A local cache is admissible only with its own verified original SHA receipt.
    side=CACHE/(name+".receipt.json")
    if p.exists() and side.exists():
        rec=json.loads(side.read_text())
        if p.stat().st_size==size and rec.get("bytes")==size and rec.get("sha256")==digest(p,"sha256"):
            if info.get("checksum"):
                h=info["checksum"];assert digest(p,h["type"].lower())==h["value"]
            return p,{**rec,"cache_hit":True}
    p.unlink(missing_ok=True);side.unlink(missing_ok=True)
    tmp=p.with_suffix(p.suffix+".part");tmp.unlink(missing_ok=True)
    # Use only the publisher's documented file URLs. Never print redirect query strings.
    with requests.get(info["url"],stream=True,timeout=(20,90),headers={"User-Agent":"batter-public-research/1.0","Accept-Encoding":"identity"}) as resp:
        rec={"http":resp.status_code,"bytes_expected":size,"source_file":name}
        R["files"][name]=rec;save()
        resp.raise_for_status()
        n=0;h=hashlib.sha256()
        with tmp.open("wb") as f:
            for chunk in resp.iter_content(4*1024*1024):
                if not chunk:continue
                n+=len(chunk)
                if n>size:raise ValueError("source file exceeds published size: "+name)
                h.update(chunk);f.write(chunk)
        assert n==size,(name,n,size)
        if name.endswith(".parquet"):
            with tmp.open("rb") as f:
                assert f.read(4)==b"PAR1";f.seek(-4,2);assert f.read(4)==b"PAR1"
        if info.get("checksum"):
            chk=info["checksum"];assert digest(tmp,chk["type"].lower())==chk["value"],name
            rec["publisher_checksum_verified"]=True
        else:rec["publisher_checksum_verified"]=None
        rec.update(bytes=n,sha256=h.hexdigest(),cache_hit=False)
        tmp.replace(p);side.write_text(json.dumps(rec))
        return p,rec
def inspect(p):
    q=pq.ParquetFile(p)
    meta=q.metadata;schema=q.schema_arrow
    fields=[]
    for i,f in enumerate(schema):
        fields.append({"name":f.name,"type":str(f.type),"nullable":f.nullable})
    groups={"space":r"lat|lon|coord|grts|grid|site|location|station|geom","time":r"date|time|year|night","taxon":r"species|taxon|label|code|scientific|class","review":r"manual|review|auto|confidence|probab|classifier|verified","event_effort":r"survey|event|project|deployment|detector|duration|effort|start|end|method|monitor","id":r"(^id$|_id$|key$|uuid|guid|filename|file_id|recording)"}
    # Footer null counts are aggregate, not precise records. No value min/max for location or identifiers.
    nulls={};missing_stats=[]
    for i in range(meta.num_columns):
        n=0;ok=True;key=meta.schema.column(i).path
        for j in range(meta.num_row_groups):
            st=meta.row_group(j).column(i).statistics
            if st is None or not st.has_null_count:ok=False;break
            n+=st.null_count
        if ok:nulls[key]=n
        else:missing_stats.append(key)
    return {"rows":meta.num_rows,"row_groups":meta.num_row_groups,"columns":fields,"candidate_columns":{k:[f["name"] for f in fields if re.search(rx,f["name"],re.I)] for k,rx in groups.items()},"footer_null_counts":nulls,"footer_null_count_unavailable":missing_stats}
def main():
    # Live official inventory must contain the exact dated snapshot and published byte lengths.
    m=requests.get(ITEM,timeout=(15,45));m.raise_for_status();j=m.json()
    assert "NABat" in j["title"]
    files={f["name"]:f for f in j["files"]}
    assert set(SPECS)<=set(files)
    assert all(int(files[k]["size"])==v for k,v in SPECS.items())
    R["source_inventory"]=[{"name":k,"size":v,"publisher_checksum":files[k].get("checksum")} for k,v in SPECS.items()]
    R["catalog_title"]=j["title"];save()
    for name in SPECS:
        p,receipt=acquire(files[name])
        R["files"][name]=receipt
        if name=="README.md":
            raw=p.read_text(encoding="utf8")
            # Author documentation, not record data; preserve only lines relevant to semantics.
            # Remove links with query strings rather than publish signed URLs.
            raw=re.sub(r"https?://[^\s<>)]+\?[^\s<>)]+","[URL query omitted]",raw)
            (OUT/"publisher_README.md").write_text(raw)
            terms=r"grts|latitude|longitude|location|coordinate|survey|spatial|precision|grid|manual|classif|species_information|recording|date|project|site|effort|join|file_id|manifest|parquet"
            lines=raw.splitlines()
            selected=[{"line":i+1,"text":line[:500]} for i,line in enumerate(lines) if re.search(terms,line,re.I)]
            R["README_relevant_lines"]=selected[:100]
        else:R["tables"][name]=inspect(p)
        save()
    R["status"]="ORIGINAL_TABLES_SCHEMA_READY_REQUIRES_DOCUMENTED_GRAIN_AND_JOIN_AUDIT";R["admitted_for_1km_model"]=False;save()
if __name__=="__main__":
    try:main()
    except Exception as e:
        R.update(status="INCOMPLETE",error_type=type(e).__name__,error=re.sub(r"https?://[^\s]+","[URL omitted]",str(e))[:250]);save();raise
