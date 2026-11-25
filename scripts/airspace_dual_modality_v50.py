"""V50: paired visual/acoustic source schema only. No response or coordinate values."""
import csv,io,json,hashlib,re
from collections import Counter
from pathlib import PurePosixPath
from urllib.parse import quote,urljoin,urlparse
from concurrent.futures import ThreadPoolExecutor
import requests,py7zr,numpy as np
from py7zr.io import BytesIOFactory
from scipy.io import whosmat,loadmat
from openpyxl import load_workbook
from roost_fd_source_audit_v2 import OUT
DOI="10.5061/dryad.pc1q122"
BASE="https://datadryad.org"
PINS={
"3D_Tracks.7z":(76056,"0b9cfd8b5959ea8de2bbe932889c9b7a"),
"AudioDetections.7z":(12618,"a5d6ae049208469da6beab9351562043"),
"AudioVideoData.xlsx":(25717,"f29d34ffe0f29ba259a6acbf4f9fa6ef"),
"MatlabCode.7z":(50595,"e454c8d7afb22553b0708ef0207a3339"),
"README.txt":(1290,"e8fac52193799a42b754ea819ccfee96"),
"Scenes.7z":(474555,"473beb5d35ab75f654346d9b5025306f")}
HEAD={"User-Agent":"batter-dual-modality-source-audit/1.0"}
def sha(b):return hashlib.sha256(b).hexdigest()
def get(url):
    r=requests.get(url,headers=HEAD,timeout=(10,30));r.raise_for_status();return r.json()
def link(obj,key):
    return urljoin(BASE,obj["_links"][key]["href"])
def inventory():
    j=get(BASE+"/api/v2/datasets/"+quote("doi:"+DOI,safe=""))
    assert j["identifier"]=="doi:"+DOI
    v=get(link(j,"stash:version"))
    fs=get(link(v,"stash:files"))["_embedded"]["stash:files"]
    out={}
    for f in fs:
        name=f["path"]
        if name not in PINS:continue
        n,md=PINS[name];assert f["size"]==n and f["digest"]==md
        out[name]=f
    assert set(out)==set(PINS)
    return out
def fetch(name,f):
    # Only exact public file link advertised by repository metadata.
    url=link(f,"stash:download")
    assert urlparse(url).scheme=="https"
    n,md=PINS[name];b=bytearray()
    with requests.get(url,headers=HEAD,stream=True,timeout=(15,50)) as r:
        r.raise_for_status()
        for c in r.iter_content(65536):
            b.extend(c);assert len(b)<=n and len(b)<=1_000_000
    b=bytes(b);assert len(b)==n and hashlib.md5(b).hexdigest()==md
    return b
PAT=r"track|traj|frame|time|sync|camera|video|audio|mic|calib|scene|call|detect|flight|species|exp|natural|playback|mist|net|release|trigger|position|coords?|xyz|pulse|silent|nocall|no_call|duration|fps|threshold|angle|range|distance|wav|start|stop|end|index|file|bat"
def tokens(s):
    return sorted(set(x.group(0).lower() for x in re.finditer(PAT,str(s),re.I)))
def field(s):
    s=str(s or "")
    return s if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_./ ()-]{0,75}",s) and not re.search(r"\d{3,}",s) else "field_"+sha(s.encode())[:10]
def doc(b):
    t=b.decode("utf-8-sig",errors="replace");hits=[]
    for j,l in enumerate(t.splitlines(),1):
        tok=tokens(l)
        if tok:hits.append({"line":j,"tokens":tok})
    return {"lines":len(t.splitlines()),"matching_lines":len(hits),"tokens_by_line":hits[:100]}
def matschema(b):
    specs=whosmat(io.BytesIO(b))
    out={"variables":[{"name":field(n),"shape":list(s) if s is not None else None,"class":c} for n,s,c in specs]}
    # Structural fields only. Never summarize numerical payload or string values.
    if any(c in ("struct","cell") for n,s,c in specs):
        d=loadmat(io.BytesIO(b),struct_as_record=True,squeeze_me=False)
        nodes=[];count=0
        def walk(a,p,depth=0):
            nonlocal count
            count+=1
            if count>300 or depth>5:return
            if isinstance(a,(np.ndarray,np.void)):
                dt=a.dtype
                nodes.append({"path":p,"shape":list(a.shape),"dtype_kind":dt.kind,"fields":[field(x) for x in dt.names] if dt.names else []})
                if dt.names:
                    for k in dt.names:walk(a[k],p+"."+field(k),depth+1)
                elif isinstance(a,np.ndarray) and dt.kind=="O":
                    for x in a.ravel()[:8]:walk(x,p+"[]",depth+1)
        for n,x in d.items():
            if not n.startswith("__"):walk(x,field(n))
        out["structural_nodes"]=nodes[:100];out["truncated"]=count>300 or len(nodes)>100
    return out
def sheet_schema(b):
    w=load_workbook(io.BytesIO(b),read_only=True,data_only=False)
    result=[]
    try:
        for i,s in enumerate(w.worksheets[:20]):
            h=list(next(s.iter_rows(min_row=1,max_row=1,values_only=True),()))
            if not h:continue
            c=[Counter() for _ in h]
            n=0
            for r in s.iter_rows(min_row=2,values_only=True):
                if not any(x is not None for x in r):continue
                n+=1
                for j,v in enumerate(r[:len(h)]):
                    c[j]["missing" if v is None else type(v).__name__]+=1
            result.append({"sheet_index":i,"rows":n,"columns":[{"name":field(x) if isinstance(x,str) else "nontext_header","tags":tokens(x) if isinstance(x,str) else [],"types":dict(c[j])} for j,x in enumerate(h)]})
        return {"sheet_count":len(w.worksheets),"sheets":result}
    finally:w.close()
def archive(b):
    r={"members":[]}
    with py7zr.SevenZipFile(io.BytesIO(b),"r") as z:
        info=z.list();files=[f for f in info if not f.is_directory]
        r["file_count"]=len(files);r["uncompressed_total"]=sum(int(f.uncompressed or 0) for f in files)
        assert len(info)<=1000 and r["uncompressed_total"]<=40_000_000
        targets=[]
        for f in info:
            p=PurePosixPath(f.filename.replace("\\","/"));ext=p.suffix.lower()
            assert not p.is_absolute() and ".." not in p.parts and not re.match(r"^[A-Za-z]:",f.filename) and not getattr(f,"is_symlink",False)
            assert ext not in (".zip",".7z",".rar",".gz",".xz",".tar")
            if f.is_directory:continue
            if ext in (".mat",".m",".txt",".csv",".md") and int(f.uncompressed)<=2_000_000:targets.append(f.filename)
        r["extension_counts"]=dict(Counter(PurePosixPath(f.filename).suffix.lower() for f in files))
        fac=BytesIOFactory(limit=2_000_000)
        if targets:z.extract(targets=targets,factory=fac)
        schemas=Counter();examples={};static=[]
        for f in files:
            p=PurePosixPath(f.filename);ext=p.suffix.lower()
            if f.filename not in targets:continue
            raw=fac.get(f.filename);raw.seek(0);bb=raw.read();assert len(bb)==f.uncompressed
            try:
                if ext==".mat":
                    x=matschema(bb)
                    # Group identical variable names/classes, preserve shapes of representative only.
                    key=json.dumps([(a["name"],a["class"]) for a in x["variables"]],sort_keys=True)
                    schemas[key]+=1
                    if key not in examples:examples[key]={"path_hash":sha(f.filename.encode()),"schema":x}
                elif ext in (".m",".txt",".md"):
                    if len(static)<25:static.append({"path_hash":sha(f.filename.encode()),"name_tokens":tokens(f.filename),"document":doc(bb)})
                elif ext==".csv":
                    rd=csv.reader(io.StringIO(bb.decode("utf-8-sig",errors="replace")));h=next(rd,[])
                    r["members"].append({"path_hash":sha(f.filename.encode()),"csv_headers":[field(x) for x in h],"data_rows":sum(1 for row in rd if row)})
            except Exception as e:
                r["members"].append({"path_hash":sha(f.filename.encode()),"extension":ext,"parser_error":type(e).__name__})
        r["mat_schema_groups"]=[{"count":n,**examples[k]} for k,n in schemas.items()]
        r["static_docs"]=static
        r["extracted_selected_members"]=len(targets)
    return r
def safe(name,f):
    try:
        b=fetch(name,f)
        out={"status":"inspected","size":len(b),"sha256":sha(b),"MD5_verified":True}
        out["audit"]=archive(b) if name.endswith(".7z") else sheet_schema(b) if name.endswith(".xlsx") else doc(b)
        return out
    except requests.HTTPError as e:return {"status":"blocked","error":"HTTPError","http_status":e.response.status_code if e.response is not None else None}
    except Exception as e:
        import traceback
        return {"status":"blocked","error":type(e).__name__,"functions":[x.name for x in traceback.extract_tb(e.__traceback__)[-5:]]}
def main():
    dest=OUT/"audit_v50_dual_modality_schema.json"
    o={"status":"schema_only","numeric_outcomes_analyzed":False,"audio_files_downloaded":False,"source_code_executed":False,"files":{}}
    def save():dest.write_text(json.dumps(o,indent=2,allow_nan=False))
    save()
    try:
        fs=inventory();o["inventory_pins_verified"]=True
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures={n:pool.submit(safe,n,fs[n]) for n in PINS}
            for n,f in futures.items():o["files"][n]=f.result();save()
    except requests.HTTPError as e:o["status"]="inventory_blocked";o["http_status"]=e.response.status_code if e.response is not None else None
    except Exception as e:o["status"]="inventory_blocked";o["error_type"]=type(e).__name__
    save()
    # Keep full structural artifact; console summary bounds repetitive source schemas.
    print(json.dumps(o,indent=2,allow_nan=False))
    return 0 if o["status"]=="schema_only" and any(f["status"]=="inspected" for f in o["files"].values()) else 2
if __name__=="__main__":raise SystemExit(main())
