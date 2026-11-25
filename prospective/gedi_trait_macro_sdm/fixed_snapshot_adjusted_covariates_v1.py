"""Extend verified V7 covariates to fixed A cells; no ecological model.
Terrain and LC100 aggregation functions copied from original successful implementations.
"""
import collections,hashlib,json,math,pathlib
from concurrent.futures import ThreadPoolExecutor
import numpy as np,pandas as pd,requests,rasterio
from rasterio.io import MemoryFile
from rasterio.windows import Window,from_bounds
from pyproj import Transformer
ROOT=pathlib.Path(__file__).resolve().parent
OUT=pathlib.Path("fixed_adjusted_covariates");OUT.mkdir(exist_ok=True)
K=["cell_x","cell_y"]
def sha(p):
    with pathlib.Path(p).open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def load(p):return json.loads(pathlib.Path(p).read_text())
def write():
    (OUT/"report.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
def save():
    write()
    print("FIXED_ADJUSTED_ENV_REPORT="+json.dumps({k:v for k,v in report.items() if k not in ("sources","terrain_new_report")},allow_nan=False),flush=True)
I=Transformer.from_crs(6933,4326,always_xy=True)
P=Transformer.from_crs(4326,6933,always_xy=True)
receipt=load(ROOT/"BASELINE_LC100_ALTERNATIVE_RECEIPT_V1.json")
assert receipt["status"]=="LC100_ALTERNATIVE_CHALLENGE_COMPLETE" and all(receipt["audit"]["checks"].values())
prep=load("fixed_adjusted_support/report.json")
p=pathlib.Path("fixed_adjusted_support/candidate_cells.csv.gz")
assert prep["status"]=="PAIR_SUPPORT_READY" and sha(p)==prep["candidate_cells_sha256"]
candidate=pd.read_csv(p)
assert len(candidate)==1763 and not candidate.duplicated(K).any()
old_t=pathlib.Path("prior_terrain/cell_covariates.csv.gz")
old_l=pathlib.Path("prior_alternative/baseline_lc100/cell_covariates.csv.gz")
tp=receipt["source_reports"]["terrain"];lp=receipt["source_reports"]["leaf"]
assert sha(old_t)==tp["output_sha256"] and sha(old_l)==lp["output_sha256"]
old_t_report=load(old_t.parent/"report.json")
old_l_report=load(old_l.parent/"report.json")
assert old_t_report["output_sha256"]==tp["output_sha256"] and old_l_report["output_sha256"]==lp["output_sha256"]
a=pd.read_csv(old_t);b=pd.read_csv(old_l)
assert len(a)==len(b)==1796 and not a.duplicated(K).any() and not b.duplicated(K).any()
assert a.terrain_support.astype(str).str.lower().eq("true").all() and b.leaf_support.astype(str).str.lower().eq("true").all()
old=a.merge(b,on=K,validate="one_to_one")
assert len(old)==1796
reuse=candidate.merge(old,on=K,how="inner",validate="one_to_one")
new=candidate.merge(old[K],on=K,how="left",indicator=True,validate="one_to_one")
u=new.loc[new._merge.eq("left_only"),K].copy().reset_index(drop=True)
assert len(reuse)==1635 and len(u)==128
cells=list(u[K].itertuples(index=False,name=None))
PIN=prep["candidate_cells_sha256"]
common={"stage":"fixed A covariate extension, no ecological fit","candidate_cells_sha256":PIN,"candidate_cells":1763,"reused_cells":len(reuse),"new_cells":len(u),"old_table_sha256":{"terrain":sha(old_t),"LC100":sha(old_l)},"source_blobs":{"terrain":"512f7cf97439f67b7df4d9d7157002de46d24b7e","LC100":"980a8f8a3d002feca7243bebea29dfaf3d643152"}}
report={**common,"status":"START","sources":[]}
def fetch(url,params=None,limit=128_000_000):
    with requests.get(url,params=params,headers={"User-Agent":"batter-macro-baseline/1.0","Accept-Encoding":"identity"},stream=True,timeout=(15,60)) as r:
        r.raise_for_status()
        buf=bytearray()
        for chunk in r.iter_content(512*1024):
            buf.extend(chunk)
            if len(buf)>limit:raise ValueError("bounded payload budget exceeded")
        return bytes(buf),{"http":r.status_code,"bytes":len(buf),"sha256":hashlib.sha256(buf).hexdigest(),"etag":r.headers.get("ETag"),"content_type":r.headers.get("Content-Type")}
def guarded(fn,task):
    try:return fn(task)
    except requests.HTTPError as e:return {"status":"HTTP_STOP","http":e.response.status_code if e.response is not None else None,"task":str(task[0])},[]
    except Exception as e:return {"status":"SCHEMA_OR_TRANSPORT_STOP","error_type":type(e).__name__,"error":str(e)[:170] if not isinstance(e,requests.RequestException) else "transport failure","task":str(task[0])},[]
def terrain():
    report.update(source="Copernicus DEM GLO-30 public 2021 DSM",source_semantics="surface elevation, not bare-earth; area-weighted mean and SD",source_documentation="https://copernicus-dem-30m.s3.amazonaws.com/readme.html")
    base="https://copernicus-dem-30m.s3.amazonaws.com/"
    raw,meta=fetch(base+"tileList.txt",limit=8_000_000)
    report["tile_list"]=meta
    tiles={x.strip().strip("/") for x in raw.decode().splitlines() if x.strip()}
    assert len(tiles)>10000
    groups=collections.defaultdict(list)
    for i,(x,y) in enumerate(cells):
        l,b=I.transform(x*1000,y*1000);r,t=I.transform((x+1)*1000,(y+1)*1000)
        # Geographic raster tile centres can straddle nominal degree boundaries.
        for lat in range(math.floor(b-.001),math.floor(t+.001)+1):
            for lon in range(math.floor(l-.001),math.floor(r+.001)+1):
                groups[(lat,lon)].append(i)
    def task(q):
        (lat,lon),idx=q
        ns=("N" if lat>=0 else "S")+f"{abs(lat):02d}"
        ew=("E" if lon>=0 else "W")+f"{abs(lon):03d}"
        name=f"Copernicus_DSM_COG_10_{ns}_00_{ew}_00_DEM"
        if name not in tiles:return {"status":"NOT_DISTRIBUTED","tile":name,"cells":len(idx)},[]
        body,md=fetch(base+name+"/"+name+".tif")
        result=[]
        with MemoryFile(body) as mem,mem.open() as s:
            assert s.count==1 and s.crs.to_epsg()==4326 and s.transform.a>0 and s.transform.e<0 and s.transform.b==s.transform.d==0
            assert math.isclose(s.scales[0],1,abs_tol=1e-8) and math.isclose(s.offsets[0],0,abs_tol=1e-8)
            for i in idx:
                x,y=cells[i];l,b=I.transform(x*1000,y*1000);r,t=I.transform((x+1)*1000,(y+1)*1000)
                L,B,R,T=max(l,s.bounds.left),max(b,s.bounds.bottom),min(r,s.bounds.right),min(t,s.bounds.top)
                if L>=R or B>=T:continue
                z=from_bounds(L,B,R,T,s.transform)
                c0=max(0,math.floor(z.col_off));c1=min(s.width,math.ceil(z.col_off+z.width))
                r0=max(0,math.floor(z.row_off));r1=min(s.height,math.ceil(z.row_off+z.height))
                if c0>=c1 or r0>=r1:continue
                a=s.read(1,window=Window(c0,r0,c1-c0,r1-r0),masked=True)
                xs=s.transform.c+np.arange(c0,c1+1)*s.transform.a;ys=s.transform.f+np.arange(r0,r1+1)*s.transform.e
                xx,_=P.transform(xs,np.zeros_like(xs));_,yy=P.transform(np.zeros_like(ys),ys)
                wx=np.maximum(0,np.minimum((x+1)*1000,xx[1:])-np.maximum(x*1000,xx[:-1]))
                wy=np.maximum(0,np.minimum((y+1)*1000,yy[:-1])-np.maximum(y*1000,yy[1:]))
                weights=wy[:,None]*wx[None,:]
                valid=~np.ma.getmaskarray(a)&np.isfinite(a.data)&(weights>0)
                w=weights[valid];v=a.data[valid].astype(float)
                result.append((i,float(w.sum()),float(w@v),float(w@(v*v))))
            return {**md,"status":"READ","tile":name,"cells":len(idx),"transform":list(s.transform),"shape":[s.height,s.width]},result
    assert len(groups)<=600
    ans=np.zeros((len(u),3))
    with ThreadPoolExecutor(max_workers=3) as ex:
        for j,(md,result) in enumerate(ex.map(lambda q:guarded(task,q),sorted(groups.items()))):
            report["sources"].append(md)
            for i,w,s,v in result:ans[i]+=[w,s,v]
            if (j+1)%30==0:print("DEM_TILES",j+1,len(groups),flush=True);save()
    den=ans[:,0];ok=(den>=950000)&(den<=1000001)
    mean=np.full(len(u),np.nan);sd=mean.copy()
    mean[ok]=ans[ok,1]/den[ok]
    var=ans[ok,2]/den[ok]-mean[ok]**2
    assert np.all(var>=-1e-4)
    sd[ok]=np.sqrt(np.maximum(var,0))
    u["terrain_valid_fraction"]=den/1e6;u["surface_elev_mean_m"]=mean;u["surface_elev_sd_m"]=sd;u["terrain_support"]=ok
    report.update(status="TERRAIN_COMPLETE" if all(x["status"] in ("READ","NOT_DISTRIBUTED") for x in report["sources"]) else "TERRAIN_PARTIAL_SUPPORT",valid_cells=int(ok.sum()),tiles=len(groups),successful_tiles=sum(x["status"]=="READ" for x in report["sources"]),overlapping_area_cells=int((den>1000001).sum()),missing_tiles=sum(x["status"]=="NOT_DISTRIBUTED" for x in report["sources"]))
NAME="PROBAV_LC100_global_v3.0.1_2019-nrt_Discrete-Classification-map_EPSG-4326.tif"
MD5="6898fbe3fb46a1110cd65e3a81ed7624"
BUDGET=2_100_000_000
DOI="10.5281/zenodo.3939050"
CLASSES={
 "lc100_broadleaf_class_fraction":[112,114,122,124],
 "lc100_needleleaf_class_fraction":[111,113,121,123],
 "lc100_mixed_class_fraction":[115,125],
 "lc100_other_forest_class_fraction":[116,126]}
KNOWN=[20,30,40,50,60,70,80,90,100,200,*[x for v in CLASSES.values() for x in v]]
def acquire():
    response=requests.get("https://zenodo.org/api/records/3939050",timeout=(20,60))
    response.raise_for_status();doc=response.json()
    assert doc.get("doi")==DOI and doc.get("metadata",{}).get("access_right") in ("open",None)
    f=[v for v in doc["files"] if v["key"]==NAME];assert len(f)==1
    f=f[0];size=int(f["size"]);assert 0<size<=BUDGET and f["checksum"]=="md5:"+MD5
    # Official record file endpoint; no authorization supplied or bypass.
    url="https://zenodo.org/records/3939050/files/"+NAME+"?download=1"
    report["source_metadata"]={"record_id":doc["id"],"size":size,"checksum":f["checksum"],"url":url,"license":doc.get("metadata",{}).get("license")};save()
    p=pathlib.Path(NAME)
    m=hashlib.md5();h=hashlib.sha256();n=0;next_log=200_000_000
    with requests.get(url,headers={"Accept-Encoding":"identity"},stream=True,timeout=(20,120)) as r:
        r.raise_for_status()
        if r.status_code!=200 or "text/html" in r.headers.get("Content-Type","").lower():raise ValueError("not original raster download")
        with p.open("wb") as out:
            for b in r.iter_content(2**20):
                if not b:continue
                n+=len(b)
                if n>size or n>BUDGET:raise ValueError("download exceeds published size")
                m.update(b);h.update(b);out.write(b)
                if n>=next_log:print("LC100_DOWNLOAD_BYTES",n,size,flush=True);next_log+=200_000_000
    assert n==size and m.hexdigest()==MD5,"published source integrity check failed"
    report["download"]={"bytes":n,"md5":m.hexdigest(),"sha256":h.hexdigest(),"full_published_md5_verified":True};save()
    return p

def lc100_new():
    global report
    report={**common,"stage":"LC100 missing-cell extension only","status":"START","source_doi":DOI,"source_variant":"LC100_2019_DISCRETE_NOT_DLT","classes":CLASSES}
    p=acquire()
    assert report["download"]["sha256"]==lp["download"]["sha256"],"LC100 source differs from prior full raster"
    I=Transformer.from_crs(6933,4326,always_xy=True);P=Transformer.from_crs(4326,6933,always_xy=True)
    ans=np.full((len(u),1+len(CLASSES)),np.nan,float);codes=collections.Counter()
    masks=hashlib.sha256()
    with rasterio.open(p) as s:
        assert s.count==1 and s.crs.to_epsg()==4326 and s.transform.a>0 and s.transform.e<0 and s.transform.b==s.transform.d==0
        assert .0008<=s.transform.a<=.0012 and .0008<=-s.transform.e<=.0012,"unexpected native nominal 100m grid"
        assert math.isclose(s.scales[0],1,abs_tol=1e-8) and math.isclose(s.offsets[0],0,abs_tol=1e-8)
        report["raster"]={"shape":[s.height,s.width],"crs":str(s.crs),"transform":list(s.transform),"dtype":s.dtypes[0],"nodata":s.nodata,"scale":float(s.scales[0]),"offset":float(s.offsets[0])};save()
        for i,row in enumerate(u.itertuples(index=False)):
            x,y=int(row.cell_x),int(row.cell_y)
            l,b,r,t=I.transform(x*1000,y*1000)[0],I.transform(x*1000,y*1000)[1],I.transform((x+1)*1000,(y+1)*1000)[0],I.transform((x+1)*1000,(y+1)*1000)[1]
            if l<s.bounds.left or r>s.bounds.right or b<s.bounds.bottom or t>s.bounds.top:continue
            w=from_bounds(l,b,r,t,s.transform)
            c0=max(0,math.floor(w.col_off));c1=min(s.width,math.ceil(w.col_off+w.width))
            r0=max(0,math.floor(w.row_off));r1=min(s.height,math.ceil(w.row_off+w.height))
            if c1<=c0 or r1<=r0:continue
            z=s.read(1,window=Window(c0,r0,c1-c0,r1-r0),masked=True)
            xs=s.transform.c+np.arange(c0,c1+1)*s.transform.a;ys=s.transform.f+np.arange(r0,r1+1)*s.transform.e
            xx,_=P.transform(xs,np.zeros_like(xs));_,yy=P.transform(np.zeros_like(ys),ys)
            wx=np.maximum(0,np.minimum((x+1)*1000,xx[1:])-np.maximum(x*1000,xx[:-1]))
            wy=np.maximum(0,np.minimum((y+1)*1000,yy[:-1])-np.maximum(y*1000,yy[1:]))
            area=wy[:,None]*wx[None,:]
            assert abs(area.sum()-1e6)<1e-3,"native projected area accounting"
            a=z.data;obs=~np.ma.getmaskarray(z)&np.isfinite(a)&(area>0)
            cv,ct=np.unique(a[obs],return_counts=True)
            assert np.isin(cv,KNOWN+[0,255]).all(),"unpublished class codes"
            codes.update({str(int(k)):int(n) for k,n in zip(cv,ct)})
            valid=obs&np.isin(a,KNOWN)
            den=float(area[valid].sum());ans[i,0]=den/1e6
            masks.update(np.ascontiguousarray(a).tobytes());masks.update(np.ascontiguousarray(valid).tobytes())
            if .95<=den/1e6<=1.000001:
                ans[i,1:]=[float(area[valid&np.isin(a,cl)].sum())/den for cl in CLASSES.values()]
                assert (ans[i,1:]>=0).all() and ans[i,1:].sum()<=1.000001
        report["selected_window_value_mask_sha256"]=masks.hexdigest()
    u["leaf_valid_fraction"]=ans[:,0]
    for j,k in enumerate(CLASSES,1):u[k]=ans[:,j]
    u["leaf_support"]=np.isfinite(ans).all(1)&(ans[:,0]>=.95)&(ans[:,0]<=1.000001)

    report.update(status="LC100_NEW_CELLS_COMPLETE",valid_cells=int(u.leaf_support.sum()),observed_codes=dict(codes),original_DLT_acquired=False)
    save()
try:
    save()
    terrain()
    tr=report
    assert tr["tile_list"]["sha256"]==tp["tile_list"]["sha256"]
    original_tiles={v["tile"]:v["sha256"] for v in old_t_report["sources"] if v["status"]=="READ"}
    assert len(original_tiles)==220
    known=[v for v in tr["sources"] if v["status"]=="READ" and v["tile"] in original_tiles]
    assert all(v["sha256"]==original_tiles[v["tile"]] for v in known),"previous DSM tile bytes changed"
    tr["previous_tiles_reverified"]=len(known)
    tr["new_tiles_read"]=sum(v["status"]=="READ" and v["tile"] not in original_tiles for v in tr["sources"])
    (OUT/"terrain_new_report.json").write_text(json.dumps(tr,indent=2,allow_nan=False)+"\n")
    lc100_new()
    lr=report
    (OUT/"lc100_new_report.json").write_text(json.dumps(lr,indent=2,allow_nan=False)+"\n")
    cols=K+["terrain_valid_fraction","surface_elev_mean_m","surface_elev_sd_m","terrain_support","leaf_valid_fraction",*CLASSES.keys(),"leaf_support"]
    assert all(c in reuse for c in cols) and all(c in u for c in cols)
    joined=pd.concat([reuse[cols],u[cols]],ignore_index=True).sort_values(K).reset_index(drop=True)
    assert len(joined)==1763 and joined[K].equals(candidate.sort_values(K).reset_index(drop=True))
    both=joined.terrain_support.astype(str).str.lower().eq("true")&joined.leaf_support.astype(str).str.lower().eq("true")
    q=OUT/"cell_covariates.csv.gz"
    joined.to_csv(q,index=False,compression={"method":"gzip","mtime":0})
    report={**common,"status":"COVARIATES_COMPLETE" if both.all() else "COVARIATES_PARTIAL","output_sha256":sha(q),"terrain_valid":int(joined.terrain_support.astype(str).str.lower().eq("true").sum()),"leaf_valid":int(joined.leaf_support.astype(str).str.lower().eq("true").sum()),"both_valid":int(both.sum()),"terrain_new_report_sha256":sha(OUT/"terrain_new_report.json"),"lc100_new_report_sha256":sha(OUT/"lc100_new_report.json"),"new_terrain_tiles":tr["tiles"],"previous_terrain_tiles_reverified":len(known),"new_terrain_tiles_read":tr["new_tiles_read"],"LC100_full_sha256_reverified":lr["download"]["sha256"]}
    save()
except Exception as e:
    report.update(status="SOURCE_STOP",error_type=type(e).__name__,error=str(e)[:200] if not isinstance(e,requests.RequestException) else "source transport failure")
    save();raise
