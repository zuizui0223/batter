"""V23: audit published European protocol workbook; no observation or biological outcome."""
import collections as C,hashlib,io,json,re,zipfile
from pathlib import Path
import requests,openpyxl
OUT=Path("macro_fd_v23_result.json")
RID=15346727
NAME="Bat Monitoring Protocols - European countries - v.1.0.0..xlsx"
MD5="52993a33c834441c9fbee9decbdc6030"
STRONG=re.compile(r"canop(?:y|ies)|understor(?:e)?y|(?:microphone|recorder|detector|sensor|recording)\s*(?:placement|installation)?\s*height|(?:multiple|different|two|three|several)\s+heights?|height[- ]stratified|vertical\s+strat",re.I)
WEAK=re.compile(r"ground[- ]level|above\s+ground|height|altitude|elevation",re.I)
ACOUSTIC=re.compile(r"acoustic|ultraso(?:und|nic)|bat\s*detector|echolocation|audio",re.I)
ACCESS=re.compile(r"data\s*(?:availability|access|sharing|repository|download)|open\s*data|public\s*data|database|website|url|link",re.I)
HEADER=re.compile(r"^(?:country|countries|country name|project(?: name| id| title)?|programme(?: name| id| title)?|program(?: name| id| title)?|monitoring (?:programme|program|project|protocol)(?: name)?|protocol(?: name| id| title)?|monitoring method|method|monitoring technique|technique|data access|data availability|data sharing|website|url|link)$",re.I)
NAME_HEADER=re.compile(r"^(?:country|countries|country name|project(?: name| id| title)?|programme(?: name| id| title)?|program(?: name| id| title)?|monitoring (?:programme|program|project|protocol)(?: name)?|protocol(?: name| id| title)?)$",re.I)
URL_HEADER=re.compile(r"^(?:website|url|link)$",re.I)
def save(o):
    OUT.write_text(json.dumps(o,indent=2,allow_nan=False)+"\n")
    print("GLOBAL_V23_REPORT="+json.dumps(o,allow_nan=False),flush=True)
def get(url,cap,rec,stage):
    assert url.startswith("https://zenodo.org/")
    with requests.get(url,stream=True,timeout=(15,60)) as r:
        rec[stage+"_http"]=r.status_code
        if r.status_code!=200:raise ValueError(stage+" HTTP "+str(r.status_code))
        b=bytearray()
        for x in r.iter_content(65536):
            b.extend(x)
            if len(b)>cap:raise ValueError(stage+" byte cap")
    return bytes(b)
def val(c):
    return str(c.value).strip() if c.value is not None else ""
def header(s):
    return re.sub(r"\s+"," ",s.strip().rstrip(":"))
def main():
    o={"stage":"European monitoring protocol source registry","status":"START","doi":"10.5281/zenodo.15346727","limits":["protocol metadata only","text flags not paired-height observations","absence of a term is not evidence of no height sampling","no contact details, survey locations or raw records exported","no ecology fit"]}
    try:
        b=get(f"https://zenodo.org/api/records/{RID}",2*1024**2,o,"metadata")
        j=json.loads(b);assert int(j["id"])==RID
        f=[x for x in j["files"] if x["key"]==NAME]
        assert len(f)==1 and f[0]["checksum"]=="md5:"+MD5
        f=f[0]
        raw=get(f["links"].get("content") or f["links"]["self"],2*1024**2,o,"workbook")
        assert len(raw)==f["size"] and hashlib.md5(raw).hexdigest()==MD5
        o["workbook"]={"bytes":len(raw),"md5":MD5,"sha256":hashlib.sha256(raw).hexdigest()}
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            assert len(z.infolist())<=1000 and sum(x.file_size for x in z.infolist())<=100*1024**2 and z.testzip() is None
            assert not any("vbaproject" in x.filename.lower() for x in z.infolist())
        wb=openpyxl.load_workbook(io.BytesIO(raw),read_only=True,data_only=True,keep_links=False)
        o["sheets"]={};overall=C.Counter()
        for s in wb:
            assert s.max_row<=10000 and s.max_column<=1000 and s.max_row*s.max_column<=2000000
            rows=[list(x) for x in s.iter_rows()]
            headers=[]
            for i,row in enumerate(rows[:30]):
                for k,c in enumerate(row):
                    h=header(val(c))
                    if HEADER.fullmatch(h):headers.append((i,k,h))
            meta_cols={}
            # Only exact header names from one candidate header row. No guessing from generic name fields.
            if headers:
                cnt=C.Counter(i for i,k,h in headers);best=min(cnt,key=lambda i:(-cnt[i],i))
                if cnt[best]>=2:
                    meta_cols={k:h for i,k,h in headers if i==best and (NAME_HEADER.fullmatch(h) or URL_HEADER.fullmatch(h))}
                else:best=None
            else:best=None
            strong=[];weak=0;acoust=0;access=0;nonempty=0;terms=C.Counter();rowflags=C.Counter()
            for i,row in enumerate(rows):
                a=[val(c) for c in row]
                nonempty+=sum(bool(x) for x in a)
                # Do not expose arbitrary text values (contact and coordinates may be present).
                hits=[]
                hasac=any(ACOUSTIC.search(x) for x in a)
                hasaccess=any(ACCESS.search(x) for x in a)
                hasweak=any(WEAK.search(x) for x in a)
                acoust+=hasac;access+=hasaccess;weak+=hasweak
                for k,x in enumerate(a):
                    for m in STRONG.finditer(x):
                        term=m.group(0).casefold();terms[term]+=1
                        hits.append({"column":k+1,"term":term})
                if not hits:continue
                rowflags["strong_rows"]+=1
                rowflags["strong_and_acoustic_rows"]+=int(hasac)
                rowflags["strong_and_access_rows"]+=int(hasaccess)
                if len(strong)<80:
                    q={"row":i+1,"term_cells":hits[:16],"acoustic_text_same_row":bool(hasac),"access_text_same_row":bool(hasaccess)}
                    if best is not None and i>best:
                        labels={}
                        for k,h in meta_cols.items():
                            x=a[k]
                            if not x or len(x)>180 or "@" in x or re.search(r"\b(?:email|phone|contact person)\b",x,re.I):continue
                            if NAME_HEADER.fullmatch(h) and not re.search(r"https?://",x):labels[h]=x
                            elif URL_HEADER.fullmatch(h) and re.fullmatch(r"https?://[^\s]+",x) and "?" not in x:labels[h]=x
                        q["explicit_labels"]=labels
                    strong.append(q)
            o["sheets"][s.title]={"dimensions":[s.max_row,s.max_column],"nonempty_cells":nonempty,"header_matches":[{"row":i+1,"column":k+1,"field":h} for i,k,h in headers[:60]],"strong_term_counts":dict(terms),"strong_rows":int(rowflags["strong_rows"]),"strong_and_acoustic_rows":int(rowflags["strong_and_acoustic_rows"]),"strong_and_access_rows":int(rowflags["strong_and_access_rows"]),"weak_height_rows":weak,"acoustic_rows":acoust,"access_text_rows":access,"flagged_rows":strong}
            overall.update({"strong_rows":rowflags["strong_rows"],"strong_and_acoustic_rows":rowflags["strong_and_acoustic_rows"],"strong_and_access_rows":rowflags["strong_and_access_rows"]})
        o["totals"]=dict(overall);o["status"]="REGISTRY_CENSUS_COMPLETE";save(o)
    except Exception as e:
        o["status"]="STOP";o["error_type"]=type(e).__name__
        if isinstance(e,ValueError):o["validation"]=str(e)[:150]
        save(o)
if __name__=="__main__":main()
