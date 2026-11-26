"""New public survey sources only; no biological fit or missing effort imputation."""
import hashlib,io,json,pathlib,re,csv,urllib.parse
import requests,openpyxl
O=pathlib.Path("stratified_survey_gate");O.mkdir(exist_ok=True)
R={"status":"START","sources":{},"limits":["Only official public API metadata/file links; no alternative routes on access denial.","No biological response fitting, no raw coordinates or site identifiers in reports.","Acoustic strata and mist-net capture strata are separate estimands. Guild labels are not species."]}
S={"Ellerbrok2022":"10.5061/dryad.m0cfxpp66","PortoSupi2025":"10.5061/dryad.m905qfvg5","Farneda2019":"10.5061/dryad.f735q5p"}
BASE="https://datadryad.org"
total=0
def save():
    s=json.dumps(R,allow_nan=False)
    (O/"report.json").write_text(s+"\n")
    print("STRATIFIED_SURVEY_REPORT="+s,flush=True)
def get(url,cap=10000000):
    global total
    assert urllib.parse.urlparse(url).scheme=="https" and urllib.parse.urlparse(url).hostname=="datadryad.org"
    with requests.get(url,timeout=(15,45),stream=True,allow_redirects=False) as q:
        if q.status_code in (401,403):raise PermissionError("HTTP "+str(q.status_code))
        if 300<=q.status_code<400:raise ValueError("Redirect_not_followed")
        q.raise_for_status()
        n=bytearray()
        for chunk in q.iter_content(65536):
            n.extend(chunk)
            if len(n)>cap or total+len(n)>30000000:raise ValueError("byte_cap")
        total+=len(n)
        return bytes(n)
def api(href):
    return json.loads(get(urllib.parse.urljoin(BASE,href),2000000))
def link(d,name):
    v=d.get("_links",{}).get(name,{})
    return v.get("href") if isinstance(v,dict) else None
def schema(raw,name):
    ext=pathlib.Path(name).suffix.lower()
    if ext==".xlsx":
        w=openpyxl.load_workbook(io.BytesIO(raw),read_only=True,data_only=True)
        return {"sheets":[{"sheet":s.title,"rows":s.max_row,"columns":s.max_column,"header":[str(v)[:100] if v is not None else "" for v in next(s.iter_rows(min_row=1,max_row=1,values_only=True))]} for s in w]}
    if ext in {".csv",".tsv"}:
        raw=raw.decode("utf-8-sig")
        rows=list(csv.reader(io.StringIO(raw),delimiter="\t" if ext==".tsv" else ","))
        return {"rows_including_header":len(rows),"columns":rows[0] if rows else [],"ragged":sum(len(r)!=len(rows[0]) for r in rows) if rows else 0}
    if ext in {".txt",".md",".rmd",".r"}:
        t=raw.decode("utf-8-sig",errors="replace")
        # Do not emit entire document or private identifiers.
        return {"lines":len(t.splitlines()),"keywords":{k:len(re.findall(k,t,re.I)) for k in ["strat","canopy","height","effort","date","night","species","guild","site","capture","record"]},"publisher_code_executed":False}
    return {"unsupported_format":ext}
def main():
    for label,doi in S.items():
        r={"doi":doi,"status":"START","inventory":[],"files":[]};R["sources"][label]=r
        try:
            d=api("/api/v2/datasets/"+urllib.parse.quote("doi:"+doi,safe=""))
            r["title"]=d.get("title")
            r["license"]=d.get("license")
            h=link(d,"stash:version")
            assert h,"missing version metadata link"
            v=api(h)
            r["version"]=v.get("versionNumber");r["version_id"]=v.get("id")
            h=link(v,"stash:files");assert h,"missing file listing link"
            f=api(h);items=f.get("_embedded",{}).get("stash:files",[])
            assert isinstance(items,list) and len(items)<=100
            r["inventory"]=[{k:x.get(k) for k in ["id","path","size","digest","digestType"]} for x in items]
            r["status"]="METADATA_READY";save()
            for x in items:
                name=x.get("path","")
                if pathlib.Path(name).suffix.lower() not in {".xlsx",".csv",".tsv",".txt",".md",".rmd",".r"}:continue
                size=int(x.get("size") or 0)
                if not 0<size<=10000000:continue
                h=link(x,"stash:download")
                if not h:continue
                # The published API href is the sole download route.
                raw=get(urllib.parse.urljoin(BASE,h));assert len(raw)==size
                digest=x.get("digest");dt=str(x.get("digestType","")).lower().replace("-","")
                if digest and dt in {"md5","sha1","sha256","sha512"}:assert hashlib.new(dt,raw).hexdigest().lower()==digest.lower()
                r["files"].append({"name":name,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),"schema":schema(raw,name)})
                save()
            r["status"]="TABULAR_SCHEMA_READY" if r["files"] else "NO_ADMITTED_TABLES"
        except PermissionError as e:r.update(status="ACCESS_DENIED_STOP",reason=str(e))
        except requests.HTTPError as e:r.update(status="HTTP_STOP",http=e.response.status_code if e.response is not None else None)
        except Exception as e:r.update(status="SOURCE_OR_SCHEMA_STOP",error_type=type(e).__name__,reason=str(e)[:150])
        save()
    R["status"]="SOURCE_GATE_COMPLETE_NO_FIT";save()
if __name__=="__main__":main()
