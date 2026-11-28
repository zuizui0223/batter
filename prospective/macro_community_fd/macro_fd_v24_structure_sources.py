"""V24: bounded new source admission; no ecological model or raw metadata export."""
import collections as C, hashlib, io, json, re, zipfile
from pathlib import Path
from urllib.parse import quote,urljoin,urlparse
import numpy as np,pandas as pd,openpyxl,requests
from macro_fd_v23_protocol_registry import STRONG,ACOUSTIC,WEAK
OUT=Path("macro_fd_v24_result.json")
S=requests.Session()
def save(o):
    OUT.write_text(json.dumps(o,indent=2,allow_nan=False)+"\n")
    print("GLOBAL_V24_REPORT="+json.dumps(o,allow_nan=False),flush=True)
def get(url,limit,r,tag,size=None,md5=None,sha=None):
    assert url.startswith("https://")
    with S.get(url,stream=True,timeout=(15,50)) as q:
        r[tag+"_http"]=q.status_code
        if q.status_code!=200:raise ValueError(tag+" HTTP "+str(q.status_code))
        a=bytearray()
        for b in q.iter_content(65536):
            a.extend(b)
            if len(a)>limit:raise ValueError(tag+" cap")
    a=bytes(a)
    if size is not None:assert len(a)==int(size)
    if md5:assert hashlib.md5(a).hexdigest()==md5
    if sha:assert hashlib.sha256(a).hexdigest()==sha
    r[tag+"_receipt"]={"bytes":len(a),"md5":hashlib.md5(a).hexdigest(),"sha256":hashlib.sha256(a).hexdigest()}
    return a
def zfiles(rid,r):
    j=json.loads(get(f"https://zenodo.org/api/records/{rid}",2*1024**2,r,"metadata"));assert int(j["id"])==rid
    r["inventory"]=[{"name":x["key"],"bytes":x["size"],"checksum":x["checksum"]} for x in j["files"]]
    return {x["key"]:x for x in j["files"]}
def zget(f,name,md5,r,limit,tag):
    x=f[name];assert x["checksum"]=="md5:"+md5
    u=x["links"].get("content") or x["links"]["self"]
    assert u.startswith("https://zenodo.org/")
    return get(u,limit,r,tag,x["size"],md5)
def registry():
    r={"status":"START","record":20067652}
    try:
        f=zfiles(20067652,r)
        b=zget(f,"Bat Monitoring Protocols - European countries - v.1.1.0..xlsx","6ed99d8f1449ff819c63f761cb0565f5",r,2*1024**2,"workbook")
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            assert len(z.infolist())<1000 and sum(x.file_size for x in z.infolist())<100*1024**2 and z.testzip() is None
            assert not any("vbaproject" in x.filename.lower() for x in z.infolist())
        w=openpyxl.load_workbook(io.BytesIO(b),read_only=False,data_only=True,keep_links=False)
        r["sheets"]={}
        for s in w:
            assert s.max_row*s.max_column<2000000
            rows=list(s.iter_rows())
            def txt(c):return str(c.value).strip() if c.value is not None else ""
            fields=[txt(c) for c in rows[0]] if rows else []
            h=[x.casefold().strip().rstrip(":") for x in fields]
            actual=0;strong=0;weak=0;terms=C.Counter();methods=C.Counter();countries=set();country=None;fixed=0;links=0
            isforage="foraging" in s.title.casefold()
            # Metadata only; no contact fields or raw excerpts.
            for i,row in enumerate(rows):
                a=[txt(c) for c in row]
                if not any(a):continue
                actual+=1
                safe=[x for k,x in enumerate(a) if k>=len(h) or not re.search(r"contact|e-mail|email|phone|institution|collaborator",h[k],re.I)]
                found=[m.group(0).casefold() for x in safe for m in STRONG.finditer(x)]
                strong+=bool(found);terms.update(found);weak+=any(WEAK.search(x) for x in safe)
                if i==0 or not isforage or h.count("country")!=1 or h.count("method")!=1:continue
                c=a[h.index("country")];country=c or country
                m=a[h.index("method")]
                if not m:continue
                assert len(m)<=250 and "@" not in m
                methods[m]+=1
                if country:countries.add(country)
                ac=bool(ACOUSTIC.search(m));fx=bool(re.search(r"static|stationary|fixed|passive|automati[cs]|point|recorder",m,re.I))
                if ac and fx:fixed+=1
                for k in [i for i,x in enumerate(h) if x in ("link","data repository","website","url")]:
                    v=row[k].hyperlink.target if row[k].hyperlink and row[k].hyperlink.target else a[k]
                    p=urlparse(v)
                    if p.scheme in ("http","https") and p.netloc and not p.username and not p.password:
                        links+=1;break
            r["sheets"][s.title]={"dimensions":[s.max_row,s.max_column],"nonempty_rows_including_headers":actual,"header_fields":[x for x in fields if x and len(x)<150 and "@" not in x],"strong_height_rows":strong,"weak_height_rows":weak,"height_terms":dict(terms)}
            if isforage:
                r["foraging"]={"method_rows":sum(methods.values()),"countries":len(countries),"method_counts":dict(methods),"acoustic_fixed_flags":fixed,"rows_with_public_url":links,"comparison_v1":{"method_rows":73,"countries":20,"acoustic_fixed_flags":46}}
        r["status"]="COMPLETE_CENSUS"
    except Exception as e:r["status"]="STOP";r["error"]=str(e)[:150] if isinstance(e,ValueError) else type(e).__name__
    return r
def dryad():
    r={"status":"START","doi":"10.5061/dryad.9s4mw6mvz"}
    base="https://datadryad.org"
    def api(u,tag):return json.loads(get(u,2*1024**2,r,tag))
    def href(x,k):
        u=x.get("_links",{}).get(k,{}).get("href")
        if not u:raise ValueError("missing catalog "+k)
        u=urljoin(base,u);assert urlparse(u).netloc=="datadryad.org";return u
    try:
        d=api(base+"/api/v2/datasets/"+quote("doi:"+r["doi"],safe=""),"dataset")
        assert d.get("identifier") in ("doi:"+r["doi"],r["doi"])
        if "stash:version" in d.get("_links",{}):v=api(href(d,"stash:version"),"version")
        else:
            vv=api(href(d,"stash:versions"),"versions").get("_embedded",{}).get("stash:versions",[])
            if not vv:raise ValueError("missing versions")
            v=max(vv,key=lambda x:int(x.get("versionNumber",x.get("id",0))))
        fl=api(href(v,"stash:files"),"file_inventory").get("_embedded",{}).get("stash:files",[])
        r["inventory"]=[{"path":x.get("path"),"size":x.get("size"),"digest":x.get("digest"),"digestType":x.get("digestType")} for x in fl]
        def one(n):
            a=[x for x in fl if Path(x.get("path","")).name==n];assert len(a)==1
            x=a[0];digest=x.get("digest");alg=str(x.get("digestType","")).lower().replace("-","")
            b=get(href(x,"stash:download"),2*1024**2,r,n,x.get("size"))
            if digest and alg in ("md5","sha1","sha256"):assert hashlib.new(alg,b).hexdigest()==digest
            return b
        raw=one("Dataset_hegderow_bat_activity_2025.csv")
        rd=one("README.md")
        d=pd.read_csv(io.BytesIO(raw),sep=None,engine="python",dtype=str,keep_default_na=False)
        r["table"]={"rows":len(d),"columns":list(d.columns)}
        req=["hedgerow_ID","study_region","date","device_type","recording_duration","night_length","height","width","foliage_density","trimming_method","woody_plant_diversity","lat_y","long_x"]
        if not set(req)<=set(d):raise ValueError("schema not unique")
        lon=pd.to_numeric(d.long_x,errors="coerce");lat=pd.to_numeric(d.lat_y,errors="coerce")
        dur=pd.to_numeric(d.recording_duration,errors="coerce");night=pd.to_numeric(d.night_length,errors="coerce")
        r["support"]={"hedgerows":int(d.hedgerow_ID.nunique()),"site_date_units":int(d[["hedgerow_ID","date"]].drop_duplicates().shape[0]),"duplicate_site_date_rows":int(d.duplicated(["hedgerow_ID","date"],keep=False).sum()),"finite_geographic_rows":int((np.isfinite(lon)&np.isfinite(lat)&lon.between(-180,180)&lat.between(-90,90)).sum()),"positive_effort_rows":int((np.isfinite(dur)&dur.gt(0)&np.isfinite(night)&night.gt(0)).sum())}
        for k in ["study_region","device_type","height","width","foliage_density","trimming_method","woody_plant_diversity"]:r["support"][k]=dict(C.Counter(d[k]))
        r["candidate_species_fields"]=[k for k in d if re.search(r"bat|pip|myo|ple|nyc|rhin|barb|ept|tad|vesp|mini",k,re.I)]
        r["readme_verified"]=True
        r["status"]="COMPLETE_CENSUS"
    except Exception as e:r["status"]="STOP";r["error"]=str(e)[:150] if isinstance(e,ValueError) else type(e).__name__
    return r
def river():
    r={"status":"START","record":10893096,"limits":["one opportunistic expedition, not nationwide independent sampling","accepted classifier labels not final expert-vetted labels","no height pairs","not a detection calibrated survey"]}
    try:
        f=zfiles(10893096,r)
        raw=zget(f,"Green.Colorado_Bats.csv","0b30365712fd920df1d87dcadd2c0f00",r,20*1024**2,"csv")
        rd=zget(f,"README.md","9f1615dd89ac2a9b5af325ef497894c5",r,64*1024,"readme")
        d=pd.read_csv(io.BytesIO(raw),sep=None,engine="python",dtype=str,keep_default_na=False)
        r["table"]={"rows":len(d),"columns":list(d.columns)}
        req=["Bat_day","Latitude","Longitude","SppAccp","Fc mean","Dur mean"]
        if not set(req)<=set(d):raise ValueError("exact source fields missing")
        lon=pd.to_numeric(d.Longitude,errors="coerce");lat=pd.to_numeric(d.Latitude,errors="coerce")
        coords=np.isfinite(lon)&np.isfinite(lat)&lon.between(-180,180)&lat.between(-90,90)
        day=d.Bat_day.str.strip()
        labels=d.SppAccp.str.strip();known=~labels.str.casefold().isin(["","na","n/a","noid","nan","noise","none"])
        # Candidate classifier label census, not definitive taxa.
        fc=pd.to_numeric(d["Fc mean"],errors="coerce");du=pd.to_numeric(d["Dur mean"],errors="coerce")
        spectral=np.isfinite(fc)&fc.gt(0)&np.isfinite(du)&du.gt(0)
        q=coords&day.ne("")
        r["support"]={"valid_coordinate_rows":int(coords.sum()),"site_day_units":int(pd.DataFrame({"lat":lat[q],"lon":lon[q],"day":day[q]}).drop_duplicates().shape[0]),"day_strings":int(day[day.ne("")].nunique()),"accepted_nonempty_label_rows":int(known.sum()),"accepted_label_counts":dict(C.Counter(labels[known])),"both_positive_call_features":int(spectral.sum()),"labeled_georeferenced_positive_features":int((q&known&spectral).sum())}
        # Count per-label day support, no dates or locations printed.
        r["label_day_support"]={str(k):{"rows":len(v),"distinct_day_strings":int(v.Bat_day.nunique())} for k,v in d.loc[q&known&spectral].groupby("SppAccp")}
        r["status"]="COMPLETE_CENSUS"
    except Exception as e:r["status"]="STOP";r["error"]=str(e)[:150] if isinstance(e,ValueError) else type(e).__name__
    return r
def main():
    o={"stage":"independent structural and updated protocol source admission","status":"START","limits":["no ecological fit","aggregate schema and support only","no personal or raw location information","no restricted access bypass"]}
    for k,fn in [("registry",registry),("hedgerows",dryad),("river",river)]:
        o[k]=fn();o["status"]="CENSUS_"+k.upper();save(o)
    o["status"]="COMPLETE_SOURCE_AUDIT";save(o)
if __name__=="__main__":main()
