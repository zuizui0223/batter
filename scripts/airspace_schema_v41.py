"""V41 pinned small-file structure audit. No outcome values or track rows emitted."""
import csv,io,json,re,hashlib,math
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import PurePosixPath
from urllib.parse import quote
import requests
from openpyxl import load_workbook
from roost_fd_source_audit_v2 import OUT

ITEMS={
 "omalley_csv":("figshare",26124277,3,"3D tracks dataset.csv",4179540,"6297ff243a4398fe72ca4b4ce9802724"),
 "omalley_R":("figshare",26124277,3,"Flight behaviour script.R",38278,"ade51bc626346e5390fe084d4e6ea01d"),
 "nagy_3d":("figshare",31112509,1,"Nagy et al_Raw Data_3D bat detections.xlsx",214729,"902b9d000f03e1180d9578df7aaeff4d"),
 "barre_csv":("zenodo",10149959,None,"data_bats_barre et al 2023.csv",3186436,"60ce63b79fd8a5b9bc4771997de97839")}
HEADERS={"User-Agent":"batter-structural-source-audit-v41/1.0"}
def get(url):
    r=requests.get(url,headers=HEADERS,timeout=(10,30));r.raise_for_status();return r.json()
def fetch(spec):
    kind,i,v,name,size,md5=spec
    if kind=="figshare":
        j=get(f"https://api.figshare.com/v2/articles/{i}/versions/{v}")
        files=[f for f in j["files"] if f["name"]==name]
        assert len(files)==1
        f=files[0];assert f["size"]==size and (f.get("computed_md5") or f.get("supplied_md5"))==md5
        url=f["downloadUrl"]
    else:
        j=get(f"https://zenodo.org/api/records/{i}")
        files=[f for f in j["files"] if f["key"]==name]
        assert len(files)==1
        f=files[0];assert f["size"]==size and f["checksum"]=="md5:"+md5
        url=f["links"]["self"]
    buf=bytearray()
    with requests.get(url,headers=HEADERS,stream=True,timeout=(15,60)) as r:
        r.raise_for_status()
        for c in r.iter_content(1024*1024):
            buf.extend(c)
            if len(buf)>size or len(buf)>5_000_000:raise ValueError("size cap")
    b=bytes(buf)
    assert len(b)==size and hashlib.md5(b).hexdigest()==md5
    return b
def normalized(x):return re.sub(r"[^a-z0-9]","",str(x or "").strip().casefold())
def tags(x):
    q=normalized(x);ans=[]
    if re.search(r"(?:^x$|^y$|^z$|^xcoord|^ycoord|^zcoord|^coordx|^coordy|^coordz|^posx|^posy|^posz|^latitude|^longitude|^easting|^northing|^utm|^lat$|^lon$|^height|altitude|elevation)",q):ans.append("position")
    if re.search(r"time|frame|timestamp|datetime|^date$|^fps$|^second|^duration|^dt$",q):ans.append("time")
    if re.search(r"site|location|plot|turbine|station|survey|^night|^farm",q):ans.append("site")
    if re.search(r"track|trajectory|flightid|passid|sequence|^id$|^flight$",q):ans.append("track")
    if re.search(r"animal|individual|batid|batname|tagid|species",q):ans.append("animal")
    if re.search(r"lidar|canopy|chm|dsm|dtm|dem|road|vegetation|obstacle|calibrat|camera|^crs$|epsg|georefer|distance|^dist|width|slope|buffer|volume|shell|radius",q):ans.append("geometry")
    if re.search(r"speed|velocity|angle|orient|cross|risk|buzz|height|altitude",q):ans.append("behavior")
    return ans
def field(x):
    s=str(x or "").strip()
    if len(s)<=100 and re.fullmatch(r"[A-Za-z][A-Za-z0-9_./()%° -]*",s) and not re.search(r"\d{4}[-_/]\d|(?:lat|lon)[ _-]?\d",s,re.I):return s
    return "field_"+hashlib.sha256(s.encode()).hexdigest()[:12]
def kind(x):
    if x is None:return "missing"
    if isinstance(x,str):
        s=x.strip()
        if s.casefold() in ("","na","nan","null","none","#n/a"):return "missing"
        try:return "numeric_finite" if math.isfinite(float(s)) else "numeric_nonfinite"
        except (TypeError,ValueError):return "text"
    if isinstance(x,bool):return "bool"
    if isinstance(x,(int,float)):return "numeric_finite" if math.isfinite(float(x)) else "numeric_nonfinite"
    return type(x).__name__
def quant_counts(c):
    vals=sorted(c.values())
    if not vals:return {"distinct":0}
    return {"distinct":len(vals),"min_rows":int(vals[0]),"median_rows":float((vals[(len(vals)-1)//2]+vals[len(vals)//2])/2),"max_rows":int(vals[-1])}
SITE_KEYS={"site","siteid","sitename","plot","plotid","turbine","turbineid","station","stationid","farm","farmid"}
TRACK_KEYS={"track","trackid","trajectory","trajectoryid","flight","flightid","pass","passid","sequence","sequenceid"}
ANIMAL_KEYS={"animal","animalid","individual","individualid","batid","batname","tagid"}
TIME_KEYS={"frame","frameid","framenumber","framenum","time","timestamp","timepoint","timeindex","datetime","seconds","timeinseconds","t"}
NIGHT_KEYS={"night","nightid","surveydate","date","survey","surveyid","session","sessionid"}
def structure(header,rows):
    head=[str(x or "") for x in header];n=len(head)
    q=[normalized(x) for x in head];c=[Counter() for _ in head];rows_count=0;bad=0
    keysets={"site":SITE_KEYS,"track":TRACK_KEYS,"animal":ANIMAL_KEYS,"time_or_frame":TIME_KEYS,"night_or_session":NIGHT_KEYS}
    inds={k:[i for i,v in enumerate(q) if v in keys] for k,keys in keysets.items()}
    chosen={k:i[0] for k,i in inds.items() if len(i)==1}
    kcounts={k:Counter() for k in chosen}
    site_track=Counter();site_night=Counter();site_night_track=Counter();full=Counter()
    combinations={"site_track":site_track,"site_night":site_night,"site_night_track":site_night_track,"site_night_track_time":full}
    for row in rows:
        if not any(kind(v)!="missing" for v in row):continue
        rows_count+=1
        if len(row)!=n:bad+=1;continue
        kk={}
        for i,v in enumerate(row):
            c[i][kind(v)]+=1
        for k,i in chosen.items():
            v=row[i]
            if kind(v) not in ("missing","numeric_nonfinite"):
                kk[k]=str(v).strip();kcounts[k][kk[k]]+=1
        for keys,ctr in [(("site","track"),site_track),(("site","night_or_session"),site_night),(("site","night_or_session","track"),site_night_track),(("site","night_or_session","track","time_or_frame"),full)]:
            if all(k in kk for k in keys):ctr[tuple(kk[k] for k in keys)]+=1
    return {"header_columns":n,"nonempty_data_rows":rows_count,"wrong_width_rows":bad,
       "columns":[{"index":i,"name":field(h),"tags":tags(h),"types":dict(c[i])} for i,h in enumerate(head)],
       "candidate_key_columns":{k:[field(head[i]) for i in a] for k,a in inds.items()},
       "unambiguous_named_key_counts":{k:{"column":field(head[chosen[k]]),**quant_counts(v)} for k,v in kcounts.items()},
       "named_key_combinations":{k:quant_counts(v) for k,v in combinations.items() if v},
       "duplicate_full_key_rows":int(sum(v-1 for v in full.values())) if full else None}
def csv_schema(b):
    text=b.decode("utf-8-sig")
    try:d=csv.Sniffer().sniff(text[:12000],delimiters=",;\t")
    except csv.Error:d=csv.excel
    r=csv.reader(io.StringIO(text,newline=""),d);head=next(r)
    return {"format":"csv","delimiter":repr(d.delimiter),"structure":structure(head,r)}
def xlsx_schema(b):
    w=load_workbook(io.BytesIO(b),read_only=True,data_only=False)
    out=[]
    try:
        for idx,s in enumerate(w.worksheets):
            # Choose a header only by recognized field tokens; do not emit arbitrary cells.
            sample=list(s.iter_rows(min_row=1,max_row=min(12,s.max_row or 12),values_only=True))
            scores=[sum(isinstance(v,str) and bool(tags(v)) and len(v)<100 for v in row) for row in sample]
            i=max(range(len(scores)),key=lambda k:scores[k]) if scores else -1
            d={"sheet_index":idx,"sheet_dimensions":[s.max_row,s.max_column],"header_candidate_row":i+1 if i>=0 and scores[i]>=2 else None}
            if i>=0 and scores[i]>=2:
                d["structure"]=structure(sample[i],s.iter_rows(min_row=i+2,values_only=True))
            else:d["status"]="no_unambiguous_header_in_first_12"
            out.append(d)
        return {"format":"xlsx","sheet_count":len(w.worksheets),"sheets":out}
    finally:w.close()
def code_schema(b):
    lines=b.decode("utf-8-sig",errors="replace").splitlines()
    terms={
     "read":r"\b(?:read\.csv|read_csv|read\.table|read\.delim|read_excel|readRDS|read_sf|st_read|rast|raster|readLAS|load)\s*\(",
     "spatial_registration":r"\b(?:st_transform|st_crs|crs|proj4string|epsg|georeferenc\w*|coordinate\w*|transform\w*)\b",
     "geometry":r"\b(?:lidar|chm|dtm|dsm|dem|canopy\w*|vegetation\w*|road\w*|camera\w*|calibrat\w*|buffer\w*|obstacle\w*|distance\w*|dist\w*|slope\w*)\b",
     "movement":r"\b(?:track\w*|traj\w*|frame\w*|time\w*|speed\w*|height\w*|angle\w*|flight\w*|site\w*)\b"}
    out={}
    for k,p in terms.items():
        rows=[];ct=Counter()
        for j,line in enumerate(lines,1):
            clean=re.sub(r"""'(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*" """.strip(),"",line.split("#",1)[0])
            matches=[x.group(0) for x in re.finditer(p,clean,re.I)]
            if matches:
                tokens=[m.strip().rstrip("(").strip() for m in matches if len(m)<80]
                ct.update(tokens)
                rows.append(j)
        out[k]={"line_count":len(rows),"first_line_numbers":rows[:40],"tokens":dict(ct.most_common(30))}
    return {"format":"R_static_only","lines":len(lines),"terms":out}
def task(k,s):
    try:
        b=fetch(s);ext=PurePosixPath(s[3]).suffix.lower()
        audit=csv_schema(b) if ext==".csv" else xlsx_schema(b) if ext==".xlsx" else code_schema(b)
        return {"status":"inspected","size":len(b),"published_MD5_verified":True,"md5":hashlib.md5(b).hexdigest(),"sha256":hashlib.sha256(b).hexdigest(),"audit":audit}
    except requests.HTTPError as e:return {"status":"blocked","error":"HTTPError","http_status":e.response.status_code if e.response is not None else None}
    except Exception as e:return {"status":"blocked","error":type(e).__name__}
def main():
    out={"status":"source_structure_only","ecological_outcomes_analyzed":False,"third_party_code_executed":False,"files":{}}
    dest=OUT/"audit_v41_airspace_schema.json"
    def save():dest.write_text(json.dumps(out,indent=2,allow_nan=False))
    save()
    with ThreadPoolExecutor(max_workers=3) as pool:
        jobs={k:pool.submit(task,k,s) for k,s in ITEMS.items()}
        for k,f in jobs.items():out["files"][k]=f.result();save()
    print(dest.read_text())
    return 0 if out["files"]["omalley_csv"]["status"]=="inspected" else 2
if __name__=="__main__":raise SystemExit(main())
