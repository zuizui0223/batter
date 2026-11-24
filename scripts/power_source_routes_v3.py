"""Public-source metadata/admission audit, not an outcome analysis.
Only official APIs: Dryad public dataset download and Royal Society Figshare collection.
No access-control circumvention. No retries on denied requests.
"""
import hashlib, io, json, pathlib, urllib.request, urllib.parse, zipfile, csv
LIMIT=10_000_000
OUT=pathlib.Path("results/power_source_routes_v3.json")
def get(url,limit=LIMIT):
    req=urllib.request.Request(url,headers={"User-Agent":"batter-research-source-audit/1.0","Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=40) as r:
        raw=r.read(limit+1)
        if len(raw)>limit: raise ValueError("size limit")
        if not raw: raise ValueError("empty response")
        return raw
def digest(b):
    return {"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest(),"md5":hashlib.md5(b).hexdigest()}
def dryad(doi, expected):
    base="https://datadryad.org/api/v2/datasets/"+urllib.parse.quote("doi:"+doi,safe="")
    row={"doi":doi,"official_metadata_url":base}
    try:
        m=json.loads(get(base,1000000))
        row["metadata_title"]=m.get("title")
        row["metadata_identifier"]=m.get("identifier")
        row["metadata_links"]=m.get("_links")
    except Exception as e: row["metadata_error"]=str(e)
    try:
        raw=get(base+"/download")
        row["archive"]=digest(raw)
        z=zipfile.ZipFile(io.BytesIO(raw))
        members={pathlib.PurePosixPath(n).name:n for n in z.namelist() if not n.endswith("/")}
        row["members"]=list(members)
        if not set(expected)<=set(members): raise ValueError("missing expected original filenames")
        row["files"]={}
        for name in expected:
            info=z.getinfo(members[name])
            if info.file_size>LIMIT: raise ValueError("member size limit")
            b=z.read(info)
            f=digest(b); row["files"][name]=f
            if name.endswith(".csv"):
                r=csv.reader(io.StringIO(b.decode("utf-8-sig")))
                f["header"]=next(r); f["data_rows"]=sum(1 for _ in r)
            elif name.endswith(".xls"):
                import xlrd
                wb=xlrd.open_workbook(file_contents=b)
                f["sheets"]=[{"name":s.name,"rows":s.nrows,"cols":s.ncols,
                    "header_text":[[str(s.cell(i,j).value)[:160] for j in range(s.ncols)
                        if s.cell(i,j).ctype==xlrd.XL_CELL_TEXT] for i in range(min(4,s.nrows))]}
                    for s in wb.sheets()]
            elif name.lower().endswith(".md"):
                f["headings"]=[l[:160] for l in b.decode("utf-8-sig").splitlines() if l.startswith("#")][:50]
        row["status"]="SCHEMA_READ"
    except Exception as e:
        row["status"]="SOURCE_STOP"; row["error"]=str(e)
    return row
def figshare():
    url="https://api.figshare.com/v2/collections/6602651/articles"
    row={"collection_doi":"10.6084/m9.figshare.c.6602651","api_url":url,"articles":[]}
    try:
        items=json.loads(get(url,1000000))
        if not isinstance(items,list) or not items: raise ValueError("empty collection")
        for item in items[:20]:
            a={"id":item["id"],"title":item.get("title"),"doi":item.get("doi")}
            row["articles"].append(a)
            try:
                meta=json.loads(get("https://api.figshare.com/v2/articles/"+str(item["id"]),1000000))
                a["files"]=[]
                for f in meta.get("files",[]):
                    info={k:f.get(k) for k in ["id","name","size","computed_md5","supplied_md5","downloadUrl"]}
                    a["files"].append(info)
                    # Only retrieve advertised public files; never use non-public endpoints.
                    if not f.get("downloadUrl") or not 0<f.get("size",0)<=LIMIT: continue
                    try:
                        b=get(f["downloadUrl"])
                        info["received"]=digest(b)
                        if len(b)!=f["size"]: raise ValueError("size mismatch")
                        expected=f.get("computed_md5") or f.get("supplied_md5")
                        if expected and hashlib.md5(b).hexdigest()!=expected: raise ValueError("MD5 mismatch")
                        info["status"]="PUBLIC_FILE_HASH_VERIFIED" if expected else "PUBLIC_FILE_DIGEST_RECORDED"
                        # PDF/Word contents not read until a source-specific extraction protocol.
                    except Exception as e: info["status"]="SOURCE_STOP";info["error"]=str(e)
            except Exception as e: a["error"]=str(e)
        row["status"]="COLLECTION_METADATA_READ"
    except Exception as e: row["status"]="SOURCE_STOP";row["error"]=str(e)
    return row
def main():
    result={"scope":"metadata_schema_and_hash_only",
        "currie":dryad("10.5061/dryad.6q573n631",["Meta-analysis.csv","NABI_data_final.csv","PIV_data.csv","README.md"]),
        "troxell":dryad("10.5061/dryad.1476d70",["Voigtetal_Nathusius_bats_JEXPBIOL_2019.xls"]),
        "supplement":figshare()}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(OUT.read_text())
    if all(result[k]["status"]=="SOURCE_STOP" for k in ["currie","troxell","supplement"]):
        raise SystemExit(1)
if __name__=="__main__": main()
