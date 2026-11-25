"""Bounded public acquisition of three original height-stratum studies, no response fitting."""
import collections,csv,hashlib,io,json,pathlib,re,time
from urllib.parse import quote,urljoin,urlparse
import requests
OUT=pathlib.Path("vertical_stratum_source_gate");OUT.mkdir(exist_ok=True)
BUDGET=40_000_000
S=requests.Session()
S.headers.update({"User-Agent":"batter-height-stratum-source-audit/1.0","Accept-Encoding":"identity"})
report={"stage":"original source bytes and schema only; no ecological fit","status":"START","sources":{},"limits":["Detector stratum is not animal altitude.","Activity indices and pass counts remain distinct.","No absent label, exact effort, common taxa or study independence asserted from metadata alone.","No raw locations or responses printed or committed."]}
def save():
    (OUT/"report.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print("STRATUM_SOURCE_REPORT="+json.dumps(report,allow_nan=False),flush=True)
def get_json(url):
    r=S.get(url,timeout=(20,45));r.raise_for_status()
    return r.json()
def public_bytes(url,limit):
    assert urlparse(url).scheme=="https" and 0<limit<=BUDGET
    with S.get(url,stream=True,timeout=(20,60)) as r:
        r.raise_for_status()
        if r.headers.get("Content-Type","").lower().startswith("text/html"):
            raise ValueError("HTML instead of numeric source")
        chunks=[];n=0
        for x in r.iter_content(256*1024):
            n+=len(x)
            if n>limit:raise ValueError("source byte budget")
            chunks.append(x)
        return b"".join(chunks)
def inspect_table(raw):
    t=raw.decode("utf-8-sig",errors="strict")
    dialect=csv.Sniffer().sniff(t[:16000],delimiters=",;\t")
    rr=csv.reader(io.StringIO(t),dialect)
    columns=next(rr);assert columns and len(columns)==len(set(columns))
    missing=[0]*len(columns);n=0;bad=0
    # Preserve candidate design field cardinalities, not raw labels or response values.
    design=re.compile(r"species|taxon|sonotype|guild|(^|[_. ])site($|[_. ])|plot|location|transect|season|stratum|habitat|height|layer|night|date|hour|position|tower|detector|effort|duration|recording|treatment|forest|gap|distance|period",re.I)
    sets={i:set() for i,c in enumerate(columns) if design.search(c)}
    units={}
    for row in rr:
        if not row or not any(row):continue
        if len(row)!=len(columns):bad+=1;continue
        n+=1
        for i,v in enumerate(row):
            if v.strip().lower() in ("","na","n/a","nan","null"):missing[i]+=1
            elif i in sets and len(sets[i])<=100_000:sets[i].add(v)
    # Categorical layer levels only, omit potential raw site identifiers or counts.
    levels={}
    for i,ss in sets.items():
        if re.search(r"^(stratum|layer|habitat|height|position|canopy|season|period)$",columns[i],re.I) and len(ss)<=12:
            if all(len(v)<=40 and re.fullmatch(r"[-+0-9A-Za-z ._/]+",v) for v in ss):levels[columns[i]]=sorted(ss)
    return {"rows":n,"columns":columns,"malformed_rows":bad,"missing_by_column":dict(zip(columns,missing)),"design_field_unique_counts":{columns[i]:len(v) for i,v in sets.items()},"candidate_stratum_levels":levels,"delimiter":dialect.delimiter}
def verify(raw,digest,algo):
    if not digest:return False
    if ":" in digest:
        a,digest=digest.split(":",1);algo=a
    algo=str(algo or "").lower().replace("-","")
    if algo not in ("md5","sha1","sha256","sha512"):raise ValueError("unsupported published checksum")
    if hashlib.new(algo,raw).hexdigest()!=str(digest).lower():raise ValueError("published digest mismatch")
    return True
def file_entry(name,raw,size,digest,algo,license_id,source):
    if size is not None and len(raw)!=int(size):raise ValueError("published size mismatch")
    a={"name":name,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),"published_digest":digest,"published_digest_algorithm":algo,"published_digest_verified":verify(raw,digest,algo)}
    if name.lower().endswith((".csv",".tsv",".txt")) and name.lower().endswith((".csv",".tsv")):
        a["table_schema"]=inspect_table(raw)
    # Only output source bytes if explicit permissive reuse licence and small named file.
    lic=str(license_id).lower()
    if any(s in lic for s in ("cc0","cc-by","cc by","mit","creativecommons.org/publicdomain","creativecommons.org/licenses/by/")) and "nc" not in lic and "noncommercial" not in lic and "nd" not in lic and len(raw)<=BUDGET:
        folder=OUT/"verified_public_inputs"/source;folder.mkdir(parents=True,exist_ok=True)
        assert pathlib.Path(name).name==name
        (folder/name).write_bytes(raw);a["archived_permitted_source_bytes"]=True
    else:a["archived_permitted_source_bytes"]=False
    return a
def dryad(source,doi,expected):
    a={"doi":doi,"provider":"Dryad","status":"START","files":[]};report["sources"][source]=a
    api="https://datadryad.org/api/v2/datasets/"+quote("doi:"+doi,safe="")
    d=get_json(api)
    a["metadata_title"]=d.get("title");a["metadata_identifier"]=d.get("identifier");a["license"]=d.get("license")
    links=d.get("_links",{});v=links.get("stash:version",{})
    if not isinstance(v,dict) or not v.get("href"):raise ValueError("missing official version link")
    va=urljoin(api,v["href"]);version=get_json(va)
    a["version"]=version.get("versionNumber",version.get("id"));a["version_url"]=va
    license_id=version.get("license") or d.get("license") or ""
    a["license"]=license_id
    links=version.get("_links",{});fl=links.get("stash:files",{})
    if not isinstance(fl,dict) or not fl.get("href"):raise ValueError("missing version file listing link")
    page=get_json(urljoin(va,fl["href"]))
    files=page.get("_embedded",{}).get("stash:files",[])
    a["public_file_inventory"]=[{"path":x.get("path"),"size":x.get("size"),"digest":x.get("digest"),"digestType":x.get("digestType")} for x in files]
    fs={pathlib.PurePosixPath(x["path"]).name:x for x in files if x.get("path")}
    a["expected_files"]=expected
    if any(k not in fs for k in expected):raise ValueError("expected named source table absent")
    budget=BUDGET
    for name in expected:
        f=fs[name];size=int(f["size"]);assert 0<size<=budget
        link=f.get("_links",{}).get("stash:download",{}).get("href")
        if not link:raise ValueError("no official file download link")
        raw=public_bytes(urljoin(va,link),budget);budget-=len(raw)
        a["files"].append(file_entry(name,raw,size,f.get("digest"),f.get("digestType"),license_id,source));save()
    a["status"]="SCHEMA_READY_REQUIRES_DESIGN_AUDIT"
def zenodo():
    source="gomes_2020";a={"doi":"10.5281/zenodo.4265167","provider":"Zenodo","status":"START","files":[]};report["sources"][source]=a
    d=get_json("https://zenodo.org/api/records/4265167")
    if d.get("doi")!=a["doi"]:raise ValueError("unexpected Zenodo DOI")
    md=d.get("metadata",{});a["metadata_title"]=md.get("title");a["license"]=md.get("license")
    a["public_file_inventory"]=[{"key":v["key"],"size":v["size"],"checksum":v.get("checksum")} for v in d.get("files",[])]
    files=[v for v in d.get("files",[]) if pathlib.PurePosixPath(v["key"]).suffix.lower() in (".csv",".tsv",".r",".txt",".md") and v["size"]<=BUDGET]
    if not any(v["key"].lower().endswith((".csv",".tsv")) for v in files):raise ValueError("no original numeric table")
    budget=BUDGET
    for f in sorted(files,key=lambda z:z["key"]):
        name=f["key"];size=int(f["size"]);assert 0<size<=budget and pathlib.Path(name).name==name
        link=f.get("links",{}).get("content") or f.get("links",{}).get("self")
        if not link:raise ValueError("no official public file link")
        raw=public_bytes(link,budget);budget-=len(raw)
        a["files"].append(file_entry(name,raw,size,f.get("checksum"),None,a["license"],source));save()
    a["status"]="SCHEMA_READY_REQUIRES_DESIGN_AUDIT"
cases=[("erasmy_2022",lambda:dryad("erasmy_2022","10.5061/dryad.cjsxksn6m",["species_act.csv","guildact.csv","README_verticalstrat_models.txt"])),("yoh_2024",lambda:dryad("yoh_2024","10.5061/dryad.0vt4b8h2d",["Auto_UC_species_clean.csv","README.md"])),("gomes_2020",zenodo)]
for key,fn in cases:
    try:fn()
    except requests.HTTPError as e:
        code=e.response.status_code if e.response is not None else None
        report["sources"][key].update(status="PUBLIC_ACCESS_STOP" if code in (401,403,429) else "SOURCE_HTTP_STOP",http_status=code,error_type=type(e).__name__)
    except Exception as e:
        report["sources"][key].update(status="SOURCE_OR_SCHEMA_STOP",error_type=type(e).__name__,error=str(e)[:150] if not isinstance(e,requests.RequestException) else "transport failure")
    save()
report["n_schema_ready"]=sum(v["status"]=="SCHEMA_READY_REQUIRES_DESIGN_AUDIT" for v in report["sources"].values())
report["status"]="SOURCE_GATE_COMPLETE_NO_FIT";report["multistudy_model_admitted"]=False
save()
