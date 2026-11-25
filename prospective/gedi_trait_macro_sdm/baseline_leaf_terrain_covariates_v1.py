"""Acquire leaf-composition and surface-topography covariates on frozen pilot cells.
No bat-response fitting in this script. Public numeric source data only."""
import collections,hashlib,io,json,math,pathlib,sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np,pandas as pd,requests,rasterio
from rasterio.io import MemoryFile
from rasterio.warp import transform_bounds,reproject,Resampling
from rasterio.transform import from_origin
from rasterio.windows import Window,from_bounds,transform as win_transform
from pyproj import Transformer
MODE=sys.argv[1];assert MODE in ("leaf","terrain")
OUT=pathlib.Path("baseline_"+MODE);OUT.mkdir(exist_ok=True)
SRC=pathlib.Path("pilot/species_cell_source_year_environment.csv.gz")
PIN="5bd65cd8c56bac84c033a4972064622c172554a676d198868ef0776c49a2786b"
def sha(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
assert sha(SRC)==PIN
K=["cell_x","cell_y"]
roster=sorted(["5218524","5218507","2432439","5218522","2432359","5218471","5218464","2432389","2432416","2432655","2432614","2432470","9754263","2432564"])
f=pd.read_csv(SRC,dtype={"species_key":str,"dataset_key":str,"year":str,"license":str},keep_default_na=False,low_memory=False)
f=f[f.forest_profile_support.astype(str).str.lower().eq("true")&f.species_key.isin(roster)&f.dataset_key.ne("")&f.year.str.fullmatch(r"20[0-9]{2}")]
u=f[K].drop_duplicates().sort_values(K).reset_index(drop=True)
assert len(u)==1796
cells=list(u.itertuples(index=False,name=None))
I=Transformer.from_crs(6933,4326,always_xy=True)
P=Transformer.from_crs(4326,6933,always_xy=True)
report={"stage":"frozen pilot baseline covariate acquisition, no model","mode":MODE,"input_sha256":PIN,"candidate_cells":len(u),"status":"START","sources":[]}
def save():
    (OUT/"report.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print("BASELINE_ENV_REPORT="+json.dumps({k:v for k,v in report.items() if k!="sources"},allow_nan=False),flush=True)
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
def leaf():
    url="https://copernicus.discomap.eea.europa.eu/arcgis/rest/services/GioLandPublic/HRL_DominanteLeafType_2018/ImageServer"
    report.update(doi="10.2909/7b28d3c1-b363-4579-9141-bdd09d073fd8",service=url,source_version="2018 V01 R00 (superseded)",source_semantics="0 non-tree, 1 broadleaved, 2 coniferous; other codes excluded; no RGB render")
    raw,meta=fetch(url,{"f":"json"},limit=3_000_000)
    m=json.loads(raw)
    if "error" in m:raise ValueError("public image service metadata error")
    (OUT/"service_metadata.json").write_bytes(raw)
    report["service_metadata"]={**meta,"name":m.get("name"),"description":str(m.get("description",""))[:200],"bandCount":m.get("bandCount"),"pixelType":m.get("pixelType"),"pixelSizeX":m.get("pixelSizeX"),"pixelSizeY":m.get("pixelSizeY"),"spatialReference":m.get("spatialReference"),"extent":m.get("extent"),"maxImageWidth":m.get("maxImageWidth"),"maxImageHeight":m.get("maxImageHeight"),"hasColormap":m.get("hasColormap")}
    save()
    assert m.get("bandCount")==1 and m.get("pixelType") in ("U8","U16","S16","U4","U2"),"service not a single-band integer image"
    assert math.isclose(abs(float(m["pixelSizeX"])),10,abs_tol=1e-5) and math.isclose(abs(float(m["pixelSizeY"])),10,abs_tol=1e-5),"unexpected native pixel size"
    # Exact native EEA grid alignment from service extent; if metadata absent, fail closed.
    ext=m["extent"];ox=float(ext["xmin"]);oy=float(ext["ymax"])
    def task(x):
        k,idx=x
        p=u.iloc[idx]
        x0=int(p.cell_x.min())*1000;x1=(int(p.cell_x.max())+1)*1000
        y0=int(p.cell_y.min())*1000;y1=(int(p.cell_y.max())+1)*1000
        l,b,r,t=transform_bounds("EPSG:6933","EPSG:3035",x0,y0,x1,y1,densify_pts=21)
        l=ox+10*(math.floor((l-30-ox)/10));r=ox+10*(math.ceil((r+30-ox)/10))
        b=oy+10*(math.floor((b-30-oy)/10));t=oy+10*(math.ceil((t+30-oy)/10))
        w=int(round((r-l)/10));h=int(round((t-b)/10))
        assert 0<w<=min(int(m.get("maxImageWidth") or 4096),4096) and 0<h<=min(int(m.get("maxImageHeight") or 4096),4096)
        body,md=fetch(url+"/exportImage",{"f":"image","bbox":",".join(map(str,[l,b,r,t])),"bboxSR":"3035","imageSR":"3035","size":f"{w},{h}","format":"tiff","interpolation":"RSP_NearestNeighbor","renderingRule":json.dumps({"rasterFunction":"None"})},limit=35_000_000)
        if not body.startswith((b"II",b"MM")):raise ValueError("service did not return numeric TIFF")
        with MemoryFile(body) as mem,mem.open() as s:
            assert s.count==1 and s.crs is not None and s.crs.to_epsg()==3035
            assert s.width==w and s.height==h and s.transform.b==s.transform.d==0
            assert abs(s.transform.a-10)<1e-5 and abs(s.transform.e+10)<1e-5
            assert max(abs(a-b) for a,b in zip(s.bounds,(l,b,r,t)))<.1
            z=s.read(1,masked=True);a=z.data
            finite=~np.ma.getmaskarray(z)&np.isfinite(a)
            codes,nn=np.unique(a[finite],return_counts=True)
            if not np.all(np.isin(codes,[0,1,2,254,255])):raise ValueError("non-class numeric image codes")
            valid=finite&np.isin(a,[0,1,2])
            dt=from_origin(x0,y1,1000,1000);sh=((y1-y0)//1000,(x1-x0)//1000)
            def warp(v):
                o=np.full(sh,np.nan,np.float64)
                reproject(v.astype(np.float32),o,src_transform=s.transform,src_crs=s.crs,dst_transform=dt,dst_crs="EPSG:6933",dst_nodata=np.nan,resampling=Resampling.average)
                return o
            den=warp(valid);bl=warp(valid&(a==1));co=warp(valid&(a==2))
            vals=[]
            for i,row in p.iterrows():
                rr=int(y1//1000-row.cell_y-1);cc=int(row.cell_x-x0//1000)
                d=float(den[rr,cc]);v1=float(bl[rr,cc]);v2=float(co[rr,cc])
                if math.isfinite(d) and math.isfinite(v1) and math.isfinite(v2):
                    assert -.000001<=d<=1.000001 and -.000001<=v1 and -.000001<=v2 and v1+v2<=d+.000001
                    vals.append((i,d,v1,v2))
            return {**md,"task":str(k),"status":"READ_NUMERIC_DLT","shape":[h,w],"transform":list(s.transform),"codes":{str(int(a)):int(b) for a,b in zip(codes,nn)},"cells":len(idx)},vals
    groups=collections.defaultdict(list)
    # 5km grouping for conservative server size and output geometry.
    for i,(x,y) in enumerate(cells):groups[(x//5,y//5)].append(i)
    tasks=sorted(groups.items())
    # Pilot is deterministic geography-only, not an outcome-based site selection.
    pre=sorted(tasks,key=lambda x:hashlib.sha256(str(x[0]).encode()).hexdigest())[0]
    meta,vals=guarded(task,pre);report["sources"].append(meta);report["preflight"]=meta
    if meta["status"]!="READ_NUMERIC_DLT":
        report["status"]="LEAF_PUBLIC_NUMERIC_PREFLIGHT_STOP";save();return
    ans=np.full((len(u),3),np.nan)
    for i,d,a,b in vals:ans[i]=[d,a,b]
    with ThreadPoolExecutor(max_workers=3) as ex:
        for j,(md,vals) in enumerate(ex.map(lambda q:guarded(task,q),[q for q in tasks if q[0]!=pre[0]])):
            report["sources"].append(md)
            for i,d,a,b in vals:ans[i]=[d,a,b]
            if (j+1)%50==0:print("LEAF_WINDOWS",j+1,len(tasks),flush=True);save()
    den=ans[:,0];ok=np.isfinite(ans).all(1)&(den>=.95)&(den<=1.000001)
    u["leaf_valid_fraction"]=den
    u["broadleaf_fraction"]=np.where(ok,ans[:,1]/np.where(den>0,den,np.nan),np.nan)
    u["conifer_fraction"]=np.where(ok,ans[:,2]/np.where(den>0,den,np.nan),np.nan)
    u["leaf_support"]=ok
    report.update(status="LEAF_COMPLETE" if all(x["status"]=="READ_NUMERIC_DLT" for x in report["sources"]) else "LEAF_PARTIAL_SUPPORT",valid_cells=int(ok.sum()),attempted_windows=len(report["sources"]),successful_windows=sum(x["status"]=="READ_NUMERIC_DLT" for x in report["sources"]))
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
try:
    save()
    if MODE=="leaf":leaf()
    else:terrain()
    if "valid_cells" in report:
        p=OUT/"cell_covariates.csv.gz";u.to_csv(p,index=False,compression={"method":"gzip","mtime":0})
        report["output_sha256"]=sha(p)
    save()
except Exception as e:
    report.update(status="SOURCE_STOP",error_type=type(e).__name__,error=str(e)[:200] if not isinstance(e,requests.RequestException) else "public service transport/HTTP failure",http_status=e.response.status_code if isinstance(e,requests.HTTPError) and e.response is not None else None)
    save();raise
