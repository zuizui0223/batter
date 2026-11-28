"""V19 bounded source admission for reported acoustic traits. Aggregate only."""
import collections as C, hashlib, io, json, re, zipfile
from urllib.parse import quote,urljoin,urlparse
from pathlib import Path
import pandas as pd,numpy as np,requests
from macro_fd_v4_global_ranges import wing
from macro_fd_v15_batamp_admission import verify
OUT=Path("macro_fd_v19_result.json")
PHYL="db6f0a5584ef5b0d899770d231476c6589cb16b8"
S=requests.Session()
def save(o):
    OUT.write_text(json.dumps(o,indent=2,allow_nan=False)+"\n")
    print("GLOBAL_V19_REPORT="+json.dumps(o,allow_nan=False),flush=True)
def get(url,cap,rec,stage,expected=None,md5=None):
    assert url.startswith("https://")
    with S.get(url,stream=True,timeout=(15,35)) as r:
        rec[stage+"_http"]=r.status_code
        if r.status_code!=200:raise ValueError(stage+" HTTP "+str(r.status_code))
        buf=bytearray()
        for x in r.iter_content(65536):
            buf.extend(x)
            if len(buf)>cap:raise ValueError(stage+" size cap")
        b=bytes(buf)
    if expected is not None and len(b)!=int(expected):raise ValueError(stage+" declared size mismatch")
    if md5 is not None and hashlib.md5(b).hexdigest()!=md5:raise ValueError(stage+" MD5 mismatch")
    rec[stage+"_receipt"]={"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest(),"md5":hashlib.md5(b).hexdigest()}
    return b
def api(url,rec,stage):return json.loads(get(url,2*1024**2,rec,stage))
def norm(x):return re.sub(r"[\s_]+","_",str(x).strip().lower())
def table(b):
    for enc in ("utf-8-sig","cp1252"):
        try:
            d=pd.read_csv(io.BytesIO(b),encoding=enc,sep=None,engine="python",dtype=str,keep_default_na=False)
            if d.shape[1]>1:return d
        except (UnicodeError,pd.errors.ParserError):pass
    raise ValueError("unresolved text-table format")
def summarize(d,names,wn):
    o={"rows":len(d),"columns":[str(k) for k in d.columns],"numeric_positive_coverage":{}}
    namecols=[]
    for k in d:
        v=d[k].str.strip();x=pd.to_numeric(v,errors="coerce")
        if re.search("freq|duration|bandwidth|fmax|fmin|startf|endf|peak|slope|wing|mass|forearm|aspect",str(k),re.I):
            valid=np.isfinite(x)&x.gt(0)
            o["numeric_positive_coverage"][str(k)]={"positive":int(valid.sum()),"missing_or_non_numeric":int(x.isna().sum()),"median":float(x[valid].median()) if valid.any() else None}
        key=re.sub("[^a-z]","",str(k).lower())
        if key not in {"species","scientificname","taxon","taxonname","binomial","latin","speciesname","scientificnameiucn","speciesbinomial"}:continue
        a=v.map(norm);ok=a.str.fullmatch(r"[a-z-]+_[a-z-]+");p=set(a[ok])
        namecols.append({"column":str(k),"exact_binomial_rows":int(ok.sum()),"unique_exact_labels":len(p),"duplicate_exact_rows":int(ok.sum())-len(p),"positive_range_matches":len(p&names),"wing_matches":len(p&wn)})
    o["name_candidates"]=namecols
    return o
def dryad(doi,files,names,wn):
    rec={"doi":doi,"status":"START","files":{}}
    base="https://datadryad.org"
    try:
        d=api(base+"/api/v2/datasets/"+quote("doi:"+doi,safe=""),rec,"dataset")
        assert d.get("identifier","") in ("doi:"+doi,doi)
        links=d.get("_links",{})
        def href(obj,key):
            v=obj.get("_links",{}).get(key,{});u=v.get("href")
            if not u:raise ValueError("missing catalog link "+key)
            u=urljoin(base,u);assert urlparse(u).netloc=="datadryad.org";return u
        if "stash:version" in links:
            ver=api(href(d,"stash:version"),rec,"version")
        else:
            vs=api(href(d,"stash:versions"),rec,"versions")
            a=vs.get("_embedded",{}).get("stash:versions",[])
            if not a:raise ValueError("version inventory unavailable")
            ver=max(a,key=lambda v:int(v.get("versionNumber",v.get("id",0))))
        fl=api(href(ver,"stash:files"),rec,"file_inventory")
        a=fl.get("_embedded",{}).get("stash:files",[])
        rec["inventory"]=[{"path":v.get("path"),"size":v.get("size"),"digest":v.get("digest"),"digestType":v.get("digestType")} for v in a]
        for fname in files:
            cand=[v for v in a if Path(v.get("path","")).name==fname]
            if len(cand)!=1:rec["files"][fname]={"status":"not_unique_in_catalog"};continue
            v=cand[0];fr={};rec["files"][fname]=fr
            u=href(v,"stash:download")
            try:
                b=get(u,2*1024**2,fr,"download",v.get("size"))
                digest=v.get("digest");dt=str(v.get("digestType","")).lower().replace("-","")
                if digest and dt in ("md5","sha1","sha256"):assert hashlib.new(dt,b).hexdigest()==digest
                if fname.lower().endswith(".csv"):fr["table"]=summarize(table(b),names,wn)
                else:
                    # Documentation only, restrict to trait/header semantics, not raw records.
                    txt=b.decode("utf-8",errors="replace")
                    fr["trait_definition_lines"]=[line[:300] for line in txt.splitlines() if re.search(r"frequency|duration|FMAXE|trait.data|wing loading|aspect ratio|imput",line,re.I)][:35] if fname.lower().startswith("readme") else []
                fr["status"]="VERIFIED"
            except Exception as e:fr["status"]="STOP";fr["error"]=str(e)[:150] if isinstance(e,ValueError) else type(e).__name__
        rec["status"]="COMPLETE_CENSUS" if any(v.get("status")=="VERIFIED" and "table" in v for v in rec["files"].values()) else "STOP"
    except Exception as e:rec["status"]="STOP";rec["error"]=str(e)[:150] if isinstance(e,ValueError) else type(e).__name__
    return rec
def euro(names,wn):
    rec={"doi":"10.6084/m9.figshare.21777161.v2","status":"START","files":{}}
    try:
        j=api("https://api.figshare.com/v2/articles/21777161/versions/2",rec,"metadata")
        assert j["doi"]==rec["doi"]
        rec["inventory"]=[{"name":v["name"],"size":v["size"],"id":v["id"],"md5":v.get("computed_md5")} for v in j["files"]]
        for v in j["files"]:
            n=v["name"]
            if v["size"]>20*1024**2 or not re.search(r"zip$|xlsx$|acoustic|trait.description|taxon",n,re.I):continue
            fr={};rec["files"][n]=fr
            try:
                b=get(v.get("downloadUrl") or v.get("download_url"),20*1024**2,fr,"download",v["size"],v.get("computed_md5"))
                if n.lower().endswith(".zip"):
                    with zipfile.ZipFile(io.BytesIO(b)) as z:
                        f=z.infolist();assert len(f)<=300 and sum(x.file_size for x in f)<=100*1024**2
                        fr["members"]=[{"name":Path(x.filename).name,"size":x.file_size} for x in f if not x.is_dir()]
                        fr["tables"]={}
                        for x in f:
                            if x.file_size<=20*1024**2 and re.search(r"acoustic|trait.description|taxon",Path(x.filename).name,re.I) and x.filename.lower().endswith(".csv"):
                                fr["tables"][Path(x.filename).name]=summarize(table(z.read(x)),names,wn)
                elif n.lower().endswith(".xlsx"):
                    w=pd.ExcelFile(io.BytesIO(b),engine="openpyxl")
                    fr["sheets"]=w.sheet_names
                    fr["tables"]={k:summarize(w.parse(k,dtype=str,keep_default_na=False),names,wn) for k in w.sheet_names if re.search(r"acoustic|trait.description|taxon",k,re.I)}
                elif n.lower().endswith(".csv"):fr["table"]=summarize(table(b),names,wn)
                fr["status"]="VERIFIED"
            except Exception as e:fr["status"]="STOP";fr["error"]=str(e)[:150] if isinstance(e,ValueError) else type(e).__name__
        rec["status"]="COMPLETE_CENSUS" if any(v.get("status")=="VERIFIED" for v in rec["files"].values()) else "STOP"
    except Exception as e:rec["status"]="STOP";rec["error"]=str(e)[:150] if isinstance(e,ValueError) else type(e).__name__
    return rec
def main():
    o={"stage":"global reported acoustic traits admission","status":"START","limits":["source compilations not independent experiments","no imputation, no ecological fit","exact name coverage not taxonomic reconciliation","schema census, not validated acoustic trait semantics"]}
    try:
        o["range_metadata"]=verify(Path("phylacine"),PHYL,"Data/Ranges/Spatial_metadata.csv")
        assert o["range_metadata"]["git_blob"]=="f2538374945f602f7c148d1a534be491895cd6e1"
        d=pd.read_csv("phylacine/Data/Ranges/Spatial_metadata.csv")
        names=set(d.loc[(d["Order.1.2"]=="Chiroptera")&(d["Number.Cells.Current.Range"]>0),"Binomial.1.2"].str.lower());assert len(names)==1141
        w=wing(o);wn=names&set(w.index);assert len(wn)==264
        o["sources"]={}
        for k,doi,files in [("conenna","10.5061/dryad.tmpg4f4xm",["conenna_et_al_2021_trait_data_csv.csv","conenna_et_al_2021_trait_references_list.txt","README.txt"]),("giacomini","10.5061/dryad.c59zw3rnt",["Covariates.csv","README.md"])]:
            o["sources"][k]=dryad(doi,files,names,wn);o["status"]="SOURCE_CENSUS";save(o)
        o["sources"]["eurobatrait"]=euro(names,wn)
        o["status"]="COMPLETE_CENSUS";save(o)
    except Exception as e:o["last_status"]=o["status"];o["status"]="STOP";o["error"]=type(e).__name__;save(o)
if __name__=="__main__":main()
