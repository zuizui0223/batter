"""V47 pinned source schema, no localization error values or acoustic outcomes."""
import csv,io,json,hashlib,re,math
from collections import Counter
from pathlib import PurePosixPath
import py7zr,requests
from py7zr.io import BytesIOFactory
from roost_fd_source_audit_v2 import OUT
from airspace_known_position_calibration_v46 import RECORD,NAME,MD5,HEAD
SIZE=25816956
SHA="3503e54e2af1a0f048537e42dad2b35c8d88cabfddee765b1482a121ec96e70c"
TARGETS={
 "calibration_csv":(7,380702,"c6f5bb120d2e4db812af10bd0b6ce63188b00290a38bcfe926f4db1336bf705c"),
 "calibration_readme":(8,6500,"028f9e64d25941535413ba578516115e0b3522d490713c5c6086d48a72dac02b"),
 "calibration_rmd":(9,14505,"1723abbcacdb4548395a5a393cb5b8120cba922248300c062ee4bdf163e7e5f4")}
def sha(b):return hashlib.sha256(b).hexdigest()
def fetch():
    r=requests.get(f"https://zenodo.org/api/records/{RECORD}",headers=HEAD,timeout=(10,30));r.raise_for_status();j=r.json()
    assert int(j["id"])==RECORD and j["metadata"]["doi"]=="10.5281/zenodo.7414956"
    assert j["metadata"]["access_right"]=="open"
    f=[f for f in j["files"] if f["key"]==NAME];assert len(f)==1
    f=f[0];assert f["size"]==SIZE and f["checksum"]=="md5:"+MD5
    data=bytearray()
    with requests.get(f["links"]["self"],headers=HEAD,stream=True,timeout=(15,90)) as r:
        r.raise_for_status()
        for c in r.iter_content(1024*1024):
            data.extend(c);assert len(data)<=SIZE
    b=bytes(data);assert len(b)==SIZE and hashlib.md5(b).hexdigest()==MD5 and sha(b)==SHA
    return b
def extract(b):
    with py7zr.SevenZipFile(io.BytesIO(b),"r") as z:
        infos=z.list()
        assert len(infos)==19 and sum(int(f.uncompressed or 0) for f in infos if not f.is_directory)==49360521
        for f in infos:
            p=PurePosixPath(f.filename.replace("\\","/"))
            assert not p.is_absolute() and ".." not in p.parts and not re.match(r"^[A-Za-z]:",f.filename) and not getattr(f,"is_symlink",False)
            assert p.suffix.lower() not in (".7z",".zip",".tar",".gz",".rar",".xz",".bz2")
        names={}
        for key,(i,n,h) in TARGETS.items():
            f=infos[i]
            assert not f.is_directory and int(f.uncompressed)==n and sha(f.filename.encode())==h
            names[key]=f.filename
        fac=BytesIOFactory(limit=1_000_000)
        z.extract(targets=list(names.values()),factory=fac)
        out={}
        for k,name in names.items():
            p=fac.get(name);p.seek(0);raw=p.read()
            assert len(raw)==TARGETS[k][1]
            out[k]=raw
        return out
def decode(b):
    for encoding in ("utf-8-sig","cp1252","latin1"):
        try:return b.decode(encoding),encoding
        except UnicodeDecodeError:pass
    raise ValueError("encoding")
def field(x):
    s=str(x or "").strip()
    return s if len(s)<=100 and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_. /()%°µμ\[\]\-]*",s) and not re.search(r"\d{4}[-_/]\d",s) else "field_"+sha(s.encode())[:12]
TOKENS={
 "reference":r"true|actual|known|real|reference|measured|speaker|loudspeaker|target",
 "estimate":r"estimat|reconstruct|calculat|localis|localiz|predict|infer",
 "coordinate":r"coord|position|cartesian|spherical|(?:^|[_ .])(?:x|y|z)(?:[1-4]|[_ .]|$)",
 "range":r"dist|range|radius|radial",
 "angle":r"angle|azim|elevat|bearing|inclinat|theta|phi",
 "timing":r"arrival|delay|tdoa|toa|time|lag|onset|sample",
 "microphone":r"mic|array|channel|sensor",
 "signal":r"call|signal|pulse|sweep|repeat|stimulus|trial",
 "quality":r"quality|error|exclude|valid|precision|uncertain|residu|filter",
 "frequency":r"freq|hz|band",
 "amplitude":r"amp|spl|db|intens|pressure",
 "units_geometry":r"unit|geometry|calibrat|speed.of.sound|sound.speed|velocity|metre|meter|centimet|degree|radian"}
def tags(x):return [k for k,p in TOKENS.items() if re.search(p,str(x),re.I)]
def kind(x):
    if x is None:return "missing"
    s=str(x).strip()
    if s.casefold() in ("","na","nan","null","none","#n/a","n/a"):return "missing"
    try:return "numeric_finite" if math.isfinite(float(s)) else "numeric_nonfinite"
    except ValueError:
        if re.fullmatch(r"[-+]?\d+,\d+(?:[eE][-+]?\d+)?",s):return "numeric_decimal_comma"
        return "text"
def csv_schema(b):
    txt,enc=decode(b)
    try:d=csv.Sniffer().sniff(txt[:16000],delimiters=",;\t")
    except csv.Error:d=csv.excel
    r=csv.reader(io.StringIO(txt,newline=""),d)
    head=next(r);n=len(head);counts=[Counter() for _ in head];distinct=[set() for _ in head];seen=set();dup=0;bad=0;nr=0
    for row in r:
        if not any(kind(x)!="missing" for x in row):continue
        nr+=1
        if len(row)!=n:bad+=1;continue
        v=tuple(row);dup+=int(v in seen);seen.add(v)
        for j,x in enumerate(row):
            c=kind(x);counts[j][c]+=1
            if c!="missing":distinct[j].add(x)
    return {"encoding":enc,"delimiter":repr(d.delimiter),"rows":nr,"column_count":n,"wrong_width_rows":bad,
      "duplicate_header_count":n-len(set(head)),"exact_duplicate_rows":dup,
      "columns":[{"index":j,"name":field(h),"tags":tags(h),"types":dict(counts[j]),"distinct_nonmissing_strings":len(distinct[j])} for j,h in enumerate(head)]},head
def clean_line(s):
    # Documentation/code lineage only: remove literal paths, numeric magnitudes and geographic/identity contexts.
    s=re.sub(r"""["'][^"'\n]*(?:[/\\]|\.wav|\.csv|\.7z)[^"'\n]*["']""","[file]",s,flags=re.I)
    if re.search(r"\b(?:latitude|longitude|address|email|bat.?id|animal.?id|individual.?id|site.?id)\b|https?://|@",s,re.I):return ""
    s=re.sub(r"(?<![A-Za-z_])[-+]?\d+\.\d+(?:[eE][-+]?\d+)?","[num]",s)
    s=re.sub(r"(?<![A-Za-z_])\d{2,}","[num]",s)
    return s.strip()[:300]
def doc_audit(b,headers,code=False):
    txt,enc=decode(b);lines=txt.splitlines();counts=Counter();evidence=[]
    # Recognize field names actually in the source CSV plus geometry and provenance terms.
    names=[h for h in headers if len(h)>1 and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*",h)]
    for j,line in enumerate(lines,1):
        tt=tags(line);hits=[field(h) for h in names if re.search(r"(?<![A-Za-z0-9_])"+re.escape(h)+r"(?![A-Za-z0-9_])",line,re.I)]
        counts.update(tt)
        if not hits and not set(tt)&{"reference","estimate","coordinate","range","angle","timing","microphone","units_geometry","quality"}:continue
        if code and not hits and not re.search(r"dist|tdoa|coord|azim|elevat|mic|angle|position|error|sound.speed|calib|read[._]|filter|group_by|mutate|atan|sin\(|cos\(",line,re.I):continue
        s=clean_line(line)
        if s:evidence.append({"line":j,"fields":hits[:20],"tags":tt,"definition_or_expression":s})
    # Bounded documentation/code lines, not source observation cells.
    return {"encoding":enc,"lines":len(lines),"term_line_counts":dict(counts),"matching_lines":len(evidence),
      "evidence":evidence[:100 if not code else 120]}
def test():
    a,h=csv_schema(b"true_x,estimated_x,trial\n1,2,one\n1,2,one\n")
    assert a["rows"]==2 and a["exact_duplicate_rows"]==1 and a["columns"][0]["types"]=={"numeric_finite":2}
    assert "reference" in tags("true_x") and "estimate" in tags("estimated_x")
def main():
    dest=OUT/"audit_v47_calibration_schema.json"
    o={"status":"structural_schema_only","numeric_calibration_outcomes_analyzed":False,"source_code_executed":False,"media_decoded":False}
    def save():dest.write_text(json.dumps(o,indent=2,allow_nan=False))
    save()
    try:
        test();o["synthetic_checks"]="pass"
        b=fetch();d=extract(b);o["archive_sha256_verified"]=True
        o["files"]={k:{"bytes":len(v),"sha256":sha(v)} for k,v in d.items()}
        c,head=csv_schema(d["calibration_csv"]);o["files"]["calibration_csv"]["schema"]=c;save()
        o["files"]["calibration_readme"]["documentation"]=doc_audit(d["calibration_readme"],head)
        o["files"]["calibration_rmd"]["static_code"]=doc_audit(d["calibration_rmd"],head,True)
    except Exception as e:
        import traceback
        o["status"]="blocked";o["error_type"]=type(e).__name__;o["failure_functions"]=[x.name for x in traceback.extract_tb(e.__traceback__)[-5:]]
    save();print(dest.read_text())
    return 0 if o["status"]=="structural_schema_only" else 2
if __name__=="__main__":raise SystemExit(main())
