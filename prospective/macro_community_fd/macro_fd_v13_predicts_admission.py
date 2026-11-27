"""V13 PREDICTS v1.1 source-only admission, no geographical coordinates exported."""
import collections as C,csv,hashlib,io,json,os,re,zipfile
from pathlib import Path
import requests
import pandas as pd
from macro_fd_v4_global_ranges import read_ranges,wing
from macro_fd_v7_multidomain import mapping
from combine_v6b_coverage import acquire,norm

SLUG="the-2016-release-of-the-predicts-database-v1-1"
API="https://data.nhm.ac.uk/api/3/action/package_show"
OUT=Path("macro_fd_v13_result.json")
def save(o):
    OUT.write_text(json.dumps(o,indent=2,allow_nan=False)+"\n");print("V13_STAGE="+o["status"],flush=True)
def download(u,p,cap):
    assert u.startswith("https://")
    h=hashlib.sha256();md=hashlib.md5();n=0
    with requests.get(u,stream=True,timeout=(20,90)) as r:
        if r.status_code!=200:raise ValueError("resource HTTP "+str(r.status_code))
        size=r.headers.get("Content-Length")
        if size and int(size)>cap:raise ValueError("declared size cap")
        with p.open("wb") as f:
            for b in r.iter_content(1024*1024):
                n+=len(b)
                if n>cap:raise ValueError("size cap")
                f.write(b);h.update(b);md.update(b)
        if size and not r.headers.get("Content-Encoding"):assert n==int(size)
    return {"bytes":n,"sha256":h.hexdigest(),"md5":md.hexdigest()}
def canonical(x):return re.sub("[^a-z0-9]","",str(x).lower())
def pick(h,*opts):
    matches=[k for k in h if canonical(k) in opts]
    return matches[0] if len(matches)==1 else None
def main():
    o={"stage":"independent PREDICTS surveyed assemblage source admission","status":"START","doi":"10.5519/j4sh7e0w"}
    try:
        r=requests.get(API,params={"id":SLUG},timeout=45);o["metadata_http_status"]=r.status_code
        if r.status_code!=200:raise ValueError("official metadata HTTP "+str(r.status_code))
        m=r.json();assert m["success"]
        m=m["result"];assert m["name"]==SLUG
        o["package"]={k:m.get(k) for k in ["id","name","title","license_id","license_title","metadata_modified"]}
        rs=m["resources"]
        o["resource_inventory"]=[{k:v.get(k) for k in ["id","name","format","size","hash","description"]} for v in rs]
        def resource(key,required=True):
            v=[x for x in rs if key in (str(x.get("name","")).lower()+" "+str(x.get("url","")).lower()+" "+str(x.get("description","")).lower())]
            if len(v)!=1:
                if required:raise ValueError("resource not unique: "+key)
                return None
            return v[0]
        def find(predicate,label):
            a=[v for v in rs if predicate((str(v.get("name",""))+" "+str(v.get("description",""))+" "+str(v.get("url",""))).lower(),str(v.get("format","")).lower())]
            if len(a)!=1:raise ValueError("resource not unique: "+label)
            return a[0]
        col=find(lambda s,f:"columns.csv" in s or ("description of data extract columns" in s and f=="csv"),"column dictionary")
        db=find(lambda s,f:"database.zip" in s or ("database in zipped csv format" in s and f=="zip"),"database.zip")
        ref=resource("references.csv",False)
        o["status"]="COLUMN_DICTIONARY";save(o)
        rec=download(col["url"],Path("columns.csv"),2*1024**2);o["columns_receipt"]=rec
        for enc in ("utf-8-sig","cp1252"):
            try:d=Path("columns.csv").read_text(encoding=enc);break
            except UnicodeDecodeError:continue
        o["column_dictionary"]=d[:40000]
        if ref is not None:
            o["reference_receipt"]=download(ref["url"],Path("references.csv"),8*1024**2)
        o["status"]="DATABASE_DOWNLOAD";save(o)
        p=Path("predicts.zip");rr=download(db["url"],p,250*1024**2);o["database_receipt"]=rr
        if db.get("size") not in (None,"",0):
            assert rr["bytes"]==int(db["size"]),"catalog size"
        if re.fullmatch("[0-9a-fA-F]{32}",str(db.get("hash",""))):assert rr["md5"]==db["hash"].lower()
        if re.fullmatch("[0-9a-fA-F]{64}",str(db.get("hash",""))):assert rr["sha256"]==db["hash"].lower()
        with zipfile.ZipFile(p) as z:
            members=z.infolist();assert len(members)<=100 and sum(v.file_size for v in members)<=4*1024**3
            o["archive_members"]=[{"name":v.filename,"size":v.file_size,"crc32":f"{v.CRC:08x}"} for v in members if not v.is_dir()]
            candidates=[v for v in members if v.filename.lower().endswith(".csv") and not Path(v.filename).name.startswith(".")]
            v=[v for v in candidates if Path(v.filename).name.lower()=="database.csv"]
            if len(v)!=1:v=candidates
            assert len(v)==1,"database member ambiguous"
            f=v[0]
            with z.open(f) as q:
                head=pd.read_csv(q,nrows=0,encoding="utf-8-sig").columns.tolist()
            o["header"]=head
            order=pick(head,"order","taxonorder","taxonomicorder","ordername","taxonordername")
            family=pick(head,"family","taxonfamily","familyname","taxonfamilyname")
            taxon=pick(head,"taxonname","speciesname","scientificname","taxonnameaccepted","taxonnameentered")
            source=pick(head,"sourceid","datasourceid","source")
            study=pick(head,"studyid","study")
            site=pick(head,"siteid","site","ssbs")
            rank=pick(head,"taxonrank","rank")
            presence=pick(head,"presence","present","presenceabsence")
            if not order and not family:raise ValueError("order/family column not uniquely identified")
            o["selected_fields"]={"order":order,"family":family,"taxon":taxon,"source":source,"study":study,"site":site,"rank":rank,"presence":presence}
            # PHYLACINE known family membership fallback only for census, including current names exact.
            fams={"pteropodidae","phyllostomidae","furipteridae","hipposideridae","vespertilionidae","molossidae","emballonuridae","megadermatidae","natalidae","cistugidae","craseonycteridae","miniopteridae","mormoopidae","mystacinidae","myzopodidae","noctilionidae","nycteridae","rhinolophidae","rhinopomatidae","thyropteridae","rhinonycteridae"}
            ct=0;batrows=0;tabs=[];use=list(dict.fromkeys(k for k in [order,family,taxon,source,study,site,rank,presence] if k))
            o["status"]="BAT_CENSUS";save(o)
            with z.open(f) as q:
                for a in pd.read_csv(q,encoding="utf-8-sig",usecols=use,dtype=str,keep_default_na=False,chunksize=100000):
                    ct+=len(a)
                    mask=a[order].str.strip().str.casefold().eq("chiroptera") if order else a[family].str.strip().str.casefold().isin(fams)
                    b=a[mask];batrows+=len(b)
                    if len(b):tabs.append(b.copy())
            o["full_measurement_rows"]=ct;o["portal_count_matches"]=ct==3278056;o["bat_measurement_rows"]=batrows;o["membership_basis"]="exact order" if order else "exact known family (census only)"
        if not tabs:
            o["status"]="NO_BAT_ROWS";save(o);return
        b=pd.concat(tabs,ignore_index=True)
        for k in ["order","family","rank","presence"]:
            col0=o["selected_fields"][k]
            if col0:o[k+"_counts"]=dict(C.Counter(b[col0]))
        o["field_unique_counts"]={k:int(b[col].nunique()) for k,col in o["selected_fields"].items() if col}
        if not taxon or not study or not site:
            o["status"]="CENSUS_SCHEMA_NOT_ADMITTED";save(o);return
        names,X,shape,crs,T=read_ranges(o);assert len(names)==1141
        w=wing(o);a,s,c=acquire(o);tab=mapping(a,s,names,w,o)
        broad=set(tab.index);wings=set(names)&set(w.index);common=broad&wings
        assert (len(broad),len(wings),len(common))==(1034,264,234)
        b["normalized_name"]=b[taxon].map(norm)
        valid=b.normalized_name.str.fullmatch(r"[a-z]+_[a-z][a-z-]+") 
        if rank:
            o["rank_species_codes"]=sorted(set(b.loc[valid,rank]))
            # only an explicit species rank is accepted when rank field exists
            valid&=b[rank].str.strip().str.casefold().eq("species")
        name_set=set(b.loc[valid,"normalized_name"])
        o["binomial_census"]={"labels":len(name_set),"matched_range":len(name_set&set(names)),"matched_broad":len(name_set&broad),"matched_wing":len(name_set&wings),"matched_common":len(name_set&common),"rows_with_binomial":int(valid.sum())}
        gcols=list(dict.fromkeys(k for k in [source,study,site] if k))
        keyok=b[gcols].ne("").all(axis=1)
        o["missing_study_site_rows"]=int((~keyok).sum())
        o["study_site_candidates"]=int(b.loc[keyok,gcols].drop_duplicates().shape[0])
        # Never classify positive measurements until presence semantics confirmed against original dictionary.
        o["status"]="BAT_CENSUS_COMPLETE_DETECTION_SEMANTICS_PENDING"
    except Exception as e:
        o["last_status"]=o["status"];o["status"]="STOP";o["error_type"]=type(e).__name__
        if isinstance(e,(AssertionError,ValueError)):o["validation"]=str(e)[:180]
    finally:
        save(o);print("GLOBAL_V13_REPORT="+json.dumps(o,allow_nan=False),flush=True)
if __name__=="__main__":main()
