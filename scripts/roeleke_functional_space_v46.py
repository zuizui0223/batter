"""V46 independent noctule archived-track replication. Detected marks, not true feeding area."""
import csv,hashlib,io,json,pathlib,re,urllib.parse,urllib.error
import numpy as np
import pandas as pd
from pyproj import Transformer
from bayer_field_join_v17 import fetch
from hurme_functional_space_v42 import B,SEED,GRIDS,OFFSETS,metric,summarize
from hurme_detected_functional_space_v41 import distribution,quant
from functional_space_external_v45 import url_same,ccby
OUT=pathlib.Path("results/roeleke_functional_space_v46.json")
BASE="https://repository.zalf.de"
MAP_UUID="98e9cf64-cd23-43c8-a9bf-c6c23831c4cf"; LAYER_UUID="cf745ac0-fffa-4758-bb80-7b851927359c"
ASSET=BASE+"/api/v2/assets/414/link"
REQUIRED=["timestamp","individual_local_identifier","tag_local_identifier","site","buzz"]
def js(u):return json.loads(fetch(u,5_000_000)[0])
def layer_check():
    m=js(BASE+"/api/v2/resources/916/")["resource"]
    assert m["uuid"]==MAP_UUID and m["resource_type"]=="map"
    a=js(BASE+"/api/v2/maps/916/datasets/?page_size=50")
    assert isinstance(a,list) and len(a)==1 and a[0]["uuid"]==LAYER_UUID
    d=js(BASE+"/api/v2/datasets/914/")["dataset"]
    assert d["uuid"]==LAYER_UUID and str(d["pk"])=="914"
    assert d["alternate"]=="geonode:foraging_strategies_study" and d["is_published"] and d["is_approved"]
    assert ccby(d["license"]) and "download_resourcebase" in d["perms"]
    links=[x for x in d["links"] if isinstance(x,dict) and x.get("link_type")=="data"]
    assert any(x.get("url")==ASSET for x in links)
    w=[x["url"] for x in links if x.get("name")=="CSV" and x.get("extension")=="csv"]
    assert len(w)==1
    p=urllib.parse.parse_qs(urllib.parse.urlsplit(w[0]).query)
    assert p["typename"]==["geonode:foraging_strategies_study"] and p["srs"]==["EPSG:4326"]
    return d,[("original_asset",ASSET),("dataset_download",d["download_url"]),("wfs_csv",w[0])]
def canonical(s):return re.sub(r"[^a-z0-9]+","_",s.strip().lower()).strip("_")
def parse_csv(b):
    s=b.decode("utf-8-sig",errors="strict")
    if s.lstrip().startswith(("<","{","[")):raise ValueError("not tabular CSV")
    dialect=csv.Sniffer().sniff(s[:40000],delimiters=",;\t")
    d=pd.read_csv(io.StringIO(s),sep=dialect.delimiter,dtype=str,keep_default_na=False)
    header=[canonical(c) for c in d.columns]
    assert len(set(header))==len(header) and len(d)>0
    d.columns=header
    assert all(c in d for c in REQUIRED),"required fields absent"
    return d,dialect.delimiter
def fetch_table(routes,meta):
    receipt=[];budget=20_000_000
    for role,u in routes:
        if budget<=0:break
        x={"route":role}
        try:
            u=url_same(u,BASE);b,final=fetch(u,min(10_000_000,budget));budget-=len(b)
            if role=="original_asset" and b.lstrip().startswith((b"{",b'"')):
                j=json.loads(b)
                if isinstance(j,str):v=j
                else:
                    assert isinstance(j,dict)
                    vs=[j[k] for k in ("url","link","download_url","href") if isinstance(j.get(k),str)]
                    assert len(set(vs))==1,"unresolved public asset link"
                    v=vs[0]
                v=url_same(v,BASE);b,final=fetch(v,min(10_000_000,budget));budget-=len(b)
            x.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),matches_V45_export=hashlib.sha256(b).hexdigest()=="a2a3a9cc02b718e729aba4342a81d0e025c4809234b8dd6b7f88fc1ecc815186")
            d,sep=parse_csv(b)
            x.update(status="CSV_PARSED",rows=len(d),headers=list(d.columns),delimiter=sep)
            receipt.append(x)
            return d,role,receipt
        except Exception as e:
            x.update(status="STOP_ROUTE",error=type(e).__name__+":"+str(e)[:160]);receipt.append(x)
            if isinstance(e,urllib.error.HTTPError) and e.code in (401,403):break
    return None,None,receipt
def prepare(d,role,meta):
    x=d.copy()
    out={"raw_rows":len(x),"headers":list(x.columns),"coordinate_source":None,"archive_clock":"parse ISO8601; naive values share archive clock, UTC interpretation not assumed"}
    pairs=[("location_long","location_lat"),("longitude","latitude"),("lon","lat")]
    found=[p for p in pairs if all(c in x for c in p)]
    if len(found)==1:
        lon,lat=found[0];x["lon"]=pd.to_numeric(x[lon],errors="coerce");x["lat"]=pd.to_numeric(x[lat],errors="coerce");out["coordinate_source"]=list(found[0])
    elif len(found)==0:
        c=[k for k in ("geometry","the_geom","geom") if k in x]
        if len(c)!=1 or (role!="wfs_csv" and str(meta.get("srid","")).upper() not in ("4326","EPSG:4326")):
            return None,out,"STOP_COORDINATE_DEFINITION"
        p=x[c[0]].str.extract(r"(?i)^\s*POINT\s*\(\s*([-+0-9.eE]+)\s+([-+0-9.eE]+)\s*\)\s*$")
        x["lon"]=pd.to_numeric(p[0],errors="coerce");x["lat"]=pd.to_numeric(p[1],errors="coerce");out["coordinate_source"]="WKT POINT lon lat, EPSG:4326"
    else:return None,out,"STOP_AMBIGUOUS_COORDINATES"
    x["t"]=pd.to_datetime(x.timestamp.str.strip(),format="ISO8601",utc=True,errors="coerce")
    x["animal"]=x.individual_local_identifier.str.strip();x["tag"]=x.tag_local_identifier.str.strip();x["site"]=x.site.str.strip()
    x["marks"]=pd.to_numeric(x.buzz.str.strip(),errors="coerce")
    n=x.marks.to_numpy(float)
    goodmark=np.isfinite(n)&(n>=0)&(n==np.floor(n))&(n<2**53)
    valid=x.lon.between(-180,180)&x.lat.between(-86,86)&x.t.notna()&x.animal.ne("")&x.tag.ne("")&x.site.ne("")&goodmark
    dup=x.loc[valid].duplicated(["animal","t"],keep=False)
    valid.loc[dup.index[dup]]=False
    out.update(valid_mark_rows=int(goodmark.sum()),invalid_timestamp_rows=int(x.t.isna().sum()),duplicate_valid_key_rows=int(dup.sum()),complete_unique_rows=int(valid.sum()),complete_unique_fraction=float(valid.mean()),raw_positive_valid_marks=int((goodmark&(n>0)).sum()),retained_positive_fixes=int((valid&x.marks.gt(0)).sum()),raw_valid_mark_total=int(n[goodmark].sum()),retained_mark_total=int(x.loc[valid,"marks"].sum()))
    if valid.mean()<.95:return None,out,"STOP_COMPLETENESS"
    x=x[valid].copy();x["marks"]=x.marks.astype(np.int64)
    out["animals_before_track_gate"]=int(x.animal.nunique());out["tags_before_track_gate"]=int(x.tag.nunique());out["sites_before_track_gate"]=int(x.site.nunique())
    x=x.sort_values(["animal","t"],kind="stable")
    dt=x.groupby("animal").t.diff().dt.total_seconds();p=dt[dt>0]
    out["positive_interval_quantiles_s"]=quant(p)
    out["fraction_interval_14_48"]=float(p.between(14,48).mean()) if len(p) else None
    if not len(p) or not 30<=p.median()<=32:return None,out,"STOP_CADENCE"
    return x,out,"COMPLETE"
def collect(x):
    tr=Transformer.from_crs("EPSG:4326","EPSG:6933",always_xy=True)
    rows=[];excluded={"inconsistent_tag_or_site":0,"below100_fixes":0,"below10_positive_fixes":0}
    for aid,g in x.groupby("animal",sort=True):
        if g.tag.nunique()!=1 or g.site.nunique()!=1:excluded["inconsistent_tag_or_site"]+=1;continue
        g=g.sort_values("t",kind="stable");w=g.marks.to_numpy(np.int64);n=len(g)
        if n<100:excluded["below100_fixes"]+=1;continue
        if (w>0).sum()<10:excluded["below10_positive_fixes"]+=1;continue
        xx,yy=tr.transform(g.lon.to_numpy(),g.lat.to_numpy());xy=np.column_stack([xx,yy]);assert np.isfinite(xy).all()
        dt=g.t.diff().dt.total_seconds()
        br=(dt.isna()|dt.gt(124)|g.t.dt.floor("h").ne(g.t.dt.floor("h").shift())).to_numpy()
        groups=np.split(np.arange(n),np.flatnonzero(br)[1:])
        assert sum(map(len,groups))==n
        cells={}
        for size in GRIDS:
            _,c=np.unique(np.floor(xy/size).astype(np.int64),axis=0,return_inverse=True);cells[size]=c
        rows.append({"animal":aid,"site":g.site.iloc[0],"xy":xy,"cells":cells,"marks":w,"groups":groups})
    support={"eligible_animals":len(rows),"eligible_fixes":sum(len(r["marks"]) for r in rows),"eligible_positive_fixes":sum(int((r["marks"]>0).sum()) for r in rows),"eligible_detected_marks":sum(int(r["marks"].sum()) for r in rows),"excluded_tracks":excluded,"track_fix_quantiles":quant([len(r["marks"]) for r in rows]),"track_mark_quantiles":quant([int(r["marks"].sum()) for r in rows])}
    return rows,support
def analyze(rows):
    rng=np.random.default_rng(SEED);observed={};simulated={}
    for r in rows:
        n=len(r["marks"]);rot=np.tile(np.arange(n),(B,1))
        for ix in r["groups"]:
            if len(ix)>1:
                sh=rng.integers(0,len(ix),size=B)
                rot[:,ix]=ix[(np.arange(len(ix))[None,:]+sh[:,None])%len(ix)]
        for kind,w in (("count",r["marks"]),("positive_fix",(r["marks"]>0).astype(int))):
            expected=np.zeros(n)
            for ix in r["groups"]:expected[ix]=float(w[ix].sum())/len(ix)
            rw=w[rot];assert np.all(rw.sum(1)==w.sum())
            for size in GRIDS:
                aa=[];ss=[]
                for off in OFFSETS:
                    _,cc=np.unique(np.floor(r["xy"]/size-np.array(off)).astype(np.int64),axis=0,return_inverse=True)
                    if off==(0.,0.):assert np.array_equal(cc,r["cells"][size])
                    k=int(cc.max())+1
                    ref=distribution(cc,expected,k);q=distribution(cc,w,k)
                    aa.append(metric(q,ref))
                    ss.append(np.asarray([metric(distribution(cc,z,k),ref) for z in rw]))
                key=f"{kind}_{size}m";observed.setdefault(key,[]).append(np.stack(aa));simulated.setdefault(key,[]).append(np.stack(ss))
    out={}
    for key,a in observed.items():
        a=np.stack(a);s=np.stack(simulated[key])
        per=[summarize(rows,a[:,i,:],s[:,i,:,:]) for i in range(4)]
        avg=summarize(rows,a.mean(1),s.mean(1))
        for k in avg:
            avg[k]["passing_origins"]=sum(p[k]["gate"] for p in per)
            avg[k]["origin_robust_gate"]=bool(avg[k]["gate"] and avg[k]["passing_origins"]>=3)
        out[key]={"origins":[{"offset":list(o),"metrics":p} for o,p in zip(OFFSETS,per)],"equal_origin":avg}
    return out

def run():
    result={"scope":"external archived-track detected-mark concentration; unknown actual audio effort","source_doi":"10.4228/ZALF.DK.112","article_doi":"10.1111/oik.07158"}
    try:meta,routes=layer_check()
    except Exception as e:result.update(status="STOP_PERMISSION_OR_IDENTITY",error=repr(e)[:300]);return result
    d,role,receipts=fetch_table(routes,meta);result["source_receipts"]=receipts
    if d is None:result["status"]="STOP_SOURCE";return result
    x,a,status=prepare(d,role,meta);result["structural_audit"]=a;result["status"]=status
    if x is None:return result
    rows,s=collect(x);result["support"]=s
    if len(rows)<6:result["status"]="STOP_LOW_SUPPORT";return result
    result["results"]=analyze(rows)
    def primary(r):
        return {k:r[k+"_1000m"]["equal_origin"]["concentration_log_effective_cell_ratio"] for k in ("count","positive_fix")}
    result["primary"]=primary(result["results"])
    result["replication_gate"]=bool(all(v["origin_robust_gate"] for v in result["primary"].values()))
    sites=sorted(set(r["site"] for r in rows));result["site_summaries"]=[]
    for i,site in enumerate(sites):
        rr=[r for r in rows if r["site"]==site];o={"anonymous_site":i+1,"animals":len(rr),"fixes":sum(len(r["marks"]) for r in rr),"marks":sum(int(r["marks"].sum()) for r in rr)}
        if len(rr)>=6:
            z=analyze(rr);o["primary"]=primary(z)
        else:o["status"]="STOP_LOW_SUPPORT"
        result["site_summaries"].append(o)
    result["status"]="COMPLETE";return result
if __name__=="__main__":
    try:r=run()
    except Exception as e:r={"status":"STOP","error":repr(e)[:500]}
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(r,indent=2,allow_nan=False)+"\n");print(OUT.read_text())
