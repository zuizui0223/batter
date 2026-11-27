"""V18: public ChirosetEurope manifest and bounded direct WAV spectral feasibility."""
import collections as C, hashlib, io, json, re, zipfile
from pathlib import Path
import numpy as np,pandas as pd,requests
from scipy.io import wavfile
from scipy.signal import spectrogram
OUT=Path("macro_fd_v18_result.json")
RECORD=20773227
MANIFEST="ChirosetEurope_manifest_v1.csv"
MD5="f0f02664000c0b0e4f44102106401585"
AUDIO_MD5="603c022cf4526f9df3df3ad2f8324942"
MAX_NET=128*1024**2
MAX_MEMBER=8*1024**2
def save(o):
    OUT.write_text(json.dumps(o,indent=2,allow_nan=False)+"\n")
    print("GLOBAL_V18_REPORT="+json.dumps(o,allow_nan=False),flush=True)
def public_download(url,expected,limit):
    assert url.startswith("https://zenodo.org/")
    with requests.get(url,stream=True,timeout=(20,60)) as r:
        if r.status_code!=200:raise ValueError("public manifest HTTP "+str(r.status_code))
        b=bytearray()
        for v in r.iter_content(1024*256):
            b.extend(v)
            if len(b)>limit:raise ValueError("manifest transfer cap")
    assert len(b)==expected and hashlib.md5(b).hexdigest()==MD5
    return bytes(b)
class RangeReader(io.RawIOBase):
    def __init__(self,url,size,session):
        super().__init__();assert url.startswith("https://zenodo.org/")
        self.url=url;self.size=size;self.session=session;self.pos=0;self.bytes=0;self.calls=0
    def readable(self):return True
    def seekable(self):return True
    def tell(self):return self.pos
    def seek(self,n,whence=0):
        p=n if whence==0 else (self.pos+n if whence==1 else self.size+n if whence==2 else -1)
        if p<0:raise ValueError("negative seek")
        self.pos=p;return p
    def read(self,n=-1):
        if self.pos>=self.size:return b""
        n=min(self.size-self.pos,n if n>=0 else self.size-self.pos)
        if n==0:return b""
        if self.bytes+n>MAX_NET:raise ValueError("remote ZIP network budget")
        start=self.pos;end=start+n-1
        with self.session.get(self.url,headers={"Range":f"bytes={start}-{end}","Accept-Encoding":"identity"},stream=True,timeout=(20,60)) as r:
            self.calls+=1
            if r.status_code!=206:raise ValueError("public archive byte range HTTP "+str(r.status_code))
            if r.headers.get("Content-Range")!=f"bytes {start}-{end}/{self.size}":raise ValueError("unexpected Content-Range")
            if r.headers.get("Content-Encoding","identity")!="identity":raise ValueError("unexpected content encoding")
            b=bytearray()
            for z in r.iter_content(65536):
                b.extend(z);self.bytes+=len(z)
                if len(b)>n or self.bytes>MAX_NET:raise ValueError("range size mismatch")
            if len(b)!=n:raise ValueError("short range")
        self.pos+=n;return bytes(b)
def spectral(fs,x):
    if x.ndim!=1 or len(x)>fs*30 or len(x)<512:raise ValueError("not admitted mono clip")
    if np.issubdtype(x.dtype,np.signedinteger):x=x.astype(float)/float(-np.iinfo(x.dtype).min)
    elif x.dtype==np.uint8:x=(x.astype(float)-128)/128
    elif np.issubdtype(x.dtype,np.floating):x=x.astype(float)
    else:raise ValueError("unsupported PCM")
    if not np.isfinite(x).all() or np.max(np.abs(x))>1.001:raise ValueError("nonfinite/out-of-range PCM")
    if (np.abs(x)>=.999).mean()>.01 or np.max(np.abs(x))==0:raise ValueError("clipped/silent")
    n=512 if fs>=192000 else 256
    f,t,p=spectrogram(x,fs=fs,window="hann",nperseg=n,noverlap=n//2,detrend=False,scaling="spectrum",mode="psd")
    band=(f>=15000)&(f<=.9*fs/2)
    f=f[band];p=p[band]
    if len(f)<5:raise ValueError("spectral support")
    e=p.sum(0);peak=p.max(0);med=np.median(p,axis=0)
    good=(e>0)&(e>=np.quantile(e,.9))&(peak>=10*np.maximum(med,np.finfo(float).tiny))
    if good.sum()<5:raise ValueError("insufficient spectral frames")
    v=f[p[:,good].argmax(0)]/1000
    return {"peak_khz":float(np.median(v)),"frames":int(good.sum())}
def selftest():
    fs=192000;t=np.arange(fs)/fs;sig=.3*np.sin(2*np.pi*40000*t)
    v=spectral(fs,sig)
    assert abs(v["peak_khz"]-40)<=.4
def main():
    o={"stage":"independent-source acoustic descriptor pilot","status":"START","record":RECORD,"limits":["curated audio library not a survey","spectral peak is not pulse duration or validated characteristic frequency","no ecological model","source overlap possible","no coordinates or raw audio output"]}
    try:
        selftest()
        r=requests.get(f"https://zenodo.org/api/records/{RECORD}",timeout=(20,60))
        o["metadata_http"]=r.status_code
        if r.status_code!=200:raise ValueError("official Zenodo API HTTP "+str(r.status_code))
        j=r.json();assert int(j["id"])==RECORD
        fs={v["key"]:v for v in j["files"]}
        o["files"]={k:{"size":v["size"],"checksum":v["checksum"]} for k,v in fs.items()}
        assert fs[MANIFEST]["checksum"]=="md5:"+MD5 and fs["audio.zip"]["checksum"]=="md5:"+AUDIO_MD5
        def url(f):
            u=f["links"].get("content") or f["links"].get("self")
            assert u.startswith("https://zenodo.org/")
            return u
        raw=public_download(url(fs[MANIFEST]),fs[MANIFEST]["size"],16*1024**2)
        o["manifest_verified"]={"size":len(raw),"md5":hashlib.md5(raw).hexdigest(),"sha256":hashlib.sha256(raw).hexdigest()}
        d=pd.read_csv(io.BytesIO(raw),dtype=str,keep_default_na=False)
        o["columns"]=list(d.columns);o["rows"]=len(d)
        required={"latin","source","group_key","file_name","voc_type","rec_method","sampling_rate","time_expansion_factor","license"}
        if not required<=set(d):raise ValueError("manifest missing required fields")
        for k in required:d[k]=d[k].str.strip()
        o["source_counts"]=dict(C.Counter(d.source))
        o["vocalization_categories"]=dict(C.Counter(d.voc_type))
        o["recording_method_categories"]=dict(C.Counter(d.rec_method))
        o["license_categories"]=dict(C.Counter(d.license))
        o["distinct_species_labels"]=int(d.latin.nunique())
        sr=pd.to_numeric(d.sampling_rate,errors="coerce")
        te=pd.to_numeric(d.time_expansion_factor,errors="coerce")
        gate=d.latin.str.fullmatch(r"[A-Z][a-z]+ [a-z]+")
        o["attrition"]={}
        for key,flag in [
            ("exact_binomial",gate),
            ("explicit_echo",d.voc_type.str.casefold().isin(["echolocation","search-phase echolocation"])),
            ("explicit_field",d.rec_method.str.casefold().eq("field recording")),
            ("sample_rate",sr.ge(96000)),
            ("unexpanded",te.eq(1)),
            ("known_source_group_file",d.source.ne("")&d.group_key.ne("")&d.file_name.ne("")),
            ("permissive_license",d.license.str.upper().isin(["CC0","CC-BY","CC-BY-SA","PDM","CC0 1.0","CC-BY 4.0","CC-BY-SA 4.0"]))
        ]:
            gate=gate&flag
            o["attrition"][key]={"rows":int(gate.sum()),"species":int(d.loc[gate,"latin"].nunique())}
        q=d.loc[gate].copy();q["fs"]=sr.loc[gate].astype(int)
        def rank(*p):return hashlib.sha256("\x1f".join(map(str,p)).encode()).hexdigest()
        q["rank"]=[rank(a,b,c,e) for a,b,c,e in zip(q.latin,q.source,q.group_key,q.file_name)]
        q=q.sort_values("rank").drop_duplicates(["latin","source","group_key"])
        q=q.groupby(["latin","source"],sort=False).head(3)
        q["order"]=q.groupby("latin",sort=False).cumcount()
        q=q.sort_values(["order","rank"]).head(120)
        o["selected"]={"rows":len(q),"species":int(q.latin.nunique()),"source_counts":dict(C.Counter(q.source))}
        o["status"]="MANIFEST_COMPLETE";save(o)
        if not len(q):o["status"]="METADATA_SUPPORT_STOP";save(o);return
        rr=RangeReader(url(fs["audio.zip"]),int(fs["audio.zip"]["size"]),requests.Session())
        records=[];reject=C.Counter()
        try:
            with zipfile.ZipFile(rr) as z:
                by=C.defaultdict(list)
                for v in z.infolist():
                    if not v.is_dir():by[Path(v.filename).name].append(v)
                o["archive_inventory"]={"members":len(z.infolist()),"unique_basenames":len(by)}
                for _,v in q.iterrows():
                    cand=by.get(Path(v.file_name).name,[])
                    if len(cand)!=1:reject["nonunique_or_missing_filename"]+=1;continue
                    m=cand[0]
                    if m.file_size>MAX_MEMBER or m.compress_size>MAX_MEMBER:reject["member_budget"]+=1;continue
                    try:
                        b=z.read(m)
                        fs0,x=wavfile.read(io.BytesIO(b))
                        if fs0!=v.fs:raise ValueError("sample_rate_mismatch")
                        result=spectral(fs0,x)
                        records.append({"species":v.latin,"source":v.source,"group":v.group_key,**result})
                    except (ValueError,zipfile.BadZipFile,EOFError,RuntimeError) as e:
                        if str(e).startswith(("public archive byte range","unexpected Content-Range","remote ZIP network budget","range size","short range","unexpected content encoding")):raise
                        reject[str(e).split("\n")[0][:100] if isinstance(e,ValueError) else type(e).__name__]+=1
        except Exception as e:
            o["archive_error"]=str(e)[:200] if isinstance(e,ValueError) else type(e).__name__
        o["archive_transfer"]={"bytes":rr.bytes,"requests":rr.calls,"whole_archive_md5_verified":False}
        o["rejections"]=dict(reject)
        per={}
        if records:
            df=pd.DataFrame(records)
            for sp,g in df.groupby("species"):
                per[sp]={"records":len(g),"groups":int(g[["source","group"]].drop_duplicates().shape[0]),"sources":int(g.source.nunique()),"median_peak_khz":float(g.peak_khz.median()),"source_group_medians_khz":{str(k):float(v.peak_khz.median()) for k,v in g.groupby("source")}}
        o["valid_clips"]=len(records);o["species_summary"]=per
        o["qualified_species"]=sum(x["groups"]>=3 and x["sources"]>=2 for x in per.values())
        o["status"]="SPECTRAL_FEASIBILITY_PASS" if o["qualified_species"]>=15 else "SPECTRAL_FEASIBILITY_STOP"
        save(o)
    except Exception as e:
        o["last_status"]=o["status"];o["status"]="STOP";o["error_type"]=type(e).__name__
        if isinstance(e,ValueError):o["validation"]=str(e)[:200]
        save(o)
if __name__=="__main__":main()
