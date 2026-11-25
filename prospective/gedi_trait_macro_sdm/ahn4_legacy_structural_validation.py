"""Independent Dutch ALS structural proxy test, no bat ecological fit.
Selective public ZIP64 member extraction, verified CRC and member SHA256.
See AHN_STRUCTURE_VALIDATION_CONTRACT_V1.md.
"""
import collections,hashlib,io,json,math,os,pathlib,re,shutil,sys,time,zipfile
from contextlib import ExitStack
import numpy as np,pandas as pd,requests,rasterio
from rasterio.warp import transform_bounds,reproject,Resampling
from rasterio.windows import Window,from_bounds,transform as win_transform
from rasterio.transform import from_origin
from pyproj import Transformer
from scipy.stats import pearsonr,spearmanr
from sklearn.linear_model import Ridge
OUT=pathlib.Path("ahn_legacy_validation");OUT.mkdir(exist_ok=True)
LOCAL=pathlib.Path("ahn_legacy_local");LOCAL.mkdir(exist_ok=True)
SOURCE=pathlib.Path("fixed/cell_environment_common_grid.csv.gz")
PIN="5fc8ae81149ba9436882f3614b6eac8e51c7e79d0d88aa3c5ba15ccc717331e8"
RECORD=15261042;DOI="10.5281/zenodo.15261042"
report={"stage":"independent ALS structural proxy validation, no bat response fit","source_doi":DOI,"source_environment_sha256":PIN,"status":"START","members":{},"metrics":{},"limitations":["ALS vegetation return count percentiles differ from GVSM full-waveform return-energy quantiles.","AHN4 2020–2022 vs GVSM 2020; acquisition season and canopy change not harmonized.","Selection from actual forest occurrence support, not a national random sample.","No biological occupancy, PAVD or actual flyable volume. Latitude comparison not causal."]}
def sha(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def checkpoint():
    (OUT/"report.json").write_text(json.dumps(report,indent=2,allow_nan=False))
    print("AHN_REPORT="+json.dumps(report,allow_nan=False),flush=True)
class RangeReader(io.RawIOBase):
    """Strict bounded range reader; no fallback to a multi-GB unbounded GET."""
    def __init__(self,url,expected):
        self.url=url;self.expected=expected;self.pos=0;self.block=4*1024*1024
        self.cache=None;self.start=-1;self.transferred=0;self.session=requests.Session()
        self.session.headers.update({"User-Agent":"batter-ahn4-validation/1.0","Accept-Encoding":"identity"})
        self.etag=None
        self._fetch(0,0)
    def readable(self):return True
    def seekable(self):return True
    def tell(self):return self.pos
    def seek(self,off,whence=0):
        if whence==0:p=off
        elif whence==1:p=self.pos+off
        elif whence==2:p=self.expected+off
        else:raise ValueError("invalid whence")
        if p<0:raise ValueError("negative seek")
        self.pos=p;return p
    def _fetch(self,a,b):
        for j in range(3):
            try:
                with self.session.get(self.url,headers={"Range":f"bytes={a}-{b}"},stream=True,timeout=(25,90)) as r:
                    if r.status_code in (429,500,502,503,504):
                        if j==2:raise RuntimeError(f"range HTTP {r.status_code} after bounded retries, bytes {a}-{b}")
                        delay=r.headers.get("Retry-After","")
                        time.sleep(min(60,max(2**(j+2),int(delay) if delay.isdigit() else 0)));continue
                    if r.status_code!=206:
                        raise RuntimeError(f"public range request HTTP {r.status_code}, expected 206")
                    m=re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)",r.headers.get("Content-Range",""))
                    if not m or tuple(map(int,m.groups()))!=(a,b,self.expected):
                        raise RuntimeError("incorrect Content-Range")
                    tag=r.headers.get("ETag")
                    if self.etag is not None and tag!=self.etag:raise RuntimeError("object ETag changed")
                    if tag:self.etag=tag
                    raw=r.raw.read(b-a+2)
                    if len(raw)!=b-a+1:raise RuntimeError("incomplete range")
                    self.transferred+=len(raw)
                    if self.transferred>5_500_000_000:raise RuntimeError("range acquisition budget exceeded")
                    return raw
            except (requests.Timeout,requests.ConnectionError,OSError):
                if j==2:raise
                time.sleep(2**j)
    def read(self,n=-1):
        if n is None or n<0:n=max(0,self.expected-self.pos)
        n=min(n,max(0,self.expected-self.pos))
        if n>64*1024*1024:raise RuntimeError("single remote read exceeds 64MiB")
        parts=[]
        while n:
            if self.cache is None or not(self.start<=self.pos<self.start+len(self.cache)):
                self.start=(self.pos//self.block)*self.block
                self.cache=self._fetch(self.start,min(self.expected-1,self.start+self.block-1))
            i=self.pos-self.start;take=min(n,len(self.cache)-i)
            if take<=0:raise RuntimeError("range read stalled")
            parts.append(self.cache[i:i+take]);self.pos+=take;n-=take
        return b"".join(parts)
def metadata():
    url=f"https://zenodo.org/api/records/{RECORD}"
    r=requests.get(url,timeout=45);r.raise_for_status();a=r.json()
    assert a["id"]==RECORD and a["doi"]==DOI
    files={v["key"]:v for v in a["files"]}
    for k,v in {"4_AHN4.zip":"md5:1709d1e9a001a611502f48d1a55686a3","6_Masks.zip":"md5:af4cd8fb643f71ed9a23674fbe2b250f"}.items():
        assert files[k]["checksum"]==v,k
    report["archives"]={k:{"size":files[k]["size"],"published_checksum":files[k]["checksum"],"url":f"https://zenodo.org/records/{RECORD}/files/{k}?download=1"} for k in ("4_AHN4.zip","6_Masks.zip")}
    return files
def member(z,suffix):
    hit=[i for i in z.infolist() if not i.is_dir() and pathlib.PurePosixPath(i.filename).name.lower()==suffix.lower()]
    if len(hit)!=1:raise ValueError("expected exactly one member: "+suffix+"; matches "+str(len(hit)))
    return hit[0]
def extract(z,i,label,archive):
    p=LOCAL/(label+".tif")
    if i.file_size>2_000_000_000:raise ValueError("member size cap: "+i.filename)
    h=hashlib.sha256();n=0
    with z.open(i) as src,p.open("wb") as dst:
        while True:
            raw=src.read(4*1024*1024)
            if not raw:break
            n+=len(raw);h.update(raw);dst.write(raw)
    assert n==i.file_size
    report["members"][label]={"archive":archive,"member":i.filename,"bytes":n,"compressed_bytes":i.compress_size,"zip_crc32":f"{i.CRC:08x}","sha256":h.hexdigest(),"crc_checked":True}
    print("AHN_MEMBER="+json.dumps({"label":label,**report["members"][label]}),flush=True)
    checkpoint()
    return p
def full_download(url,path,size,md5,budget):
    """A complete public file, no unrestricted range fallback."""
    if size>budget:raise RuntimeError("download exceeds explicit budget")
    for j in range(3):
        h=hashlib.md5();n=0
        try:
            with requests.get(url,stream=True,timeout=(25,120),headers={"User-Agent":"batter-ahn4-validation/1.1","Accept-Encoding":"identity"}) as r:
                r.raise_for_status()
                with path.open("wb") as f:
                    for block in r.iter_content(4*1024*1024):
                        n+=len(block)
                        if n>size:raise RuntimeError("oversized download")
                        h.update(block);f.write(block)
            if n!=size or h.hexdigest()!=md5:raise RuntimeError("full download length/MD5 mismatch")
            return
        except (requests.RequestException,OSError,RuntimeError) as e:
            path.unlink(missing_ok=True)
            if j==2:raise
            print("AHN_FULL_RETRY",j+1,type(e).__name__,str(e)[:180],flush=True)
            time.sleep(2**(j+2))
def inventory(z,archive):
    inv=[{"name":i.filename,"size":i.file_size,"compressed_size":i.compress_size,"crc32":f"{i.CRC:08x}"} for i in z.infolist() if not i.is_dir()]
    path=OUT/(archive+".inventory.json");path.write_text(json.dumps(inv,indent=2))
    report["archives"][archive]["inventory_sha256"]=sha(path)
    print("AHN_ARCHIVE_INVENTORY "+archive+" "+json.dumps(inv)[:18000],flush=True)
def acquire():
    # Explicit secondary release: the original 2023 individual AHN4 GeoTIFFs.
    # Infrastructure masks retain the updated 2025 release.
    metadata()
    paths={}
    archive="6_Masks.zip";info=report["archives"][archive];localmask=LOCAL/archive
    full_download(info["url"],localmask,info["size"],info["published_checksum"].split(":")[1],300_000_000)
    report["archives"][archive]["full_archive_md5_verified"]=True
    with zipfile.ZipFile(localmask) as z:
        inventory(z,archive)
        for k,v in {"brw":"ahn4_10m_mask_building_road_water.tif","power":"ahn4_10m_mask_powerline.tif"}.items():
            paths[k]=extract(z,member(z,v),k,archive)
    localmask.unlink()
    legacy=8422129
    report["source_doi"]="10.5281/zenodo.8422129"
    report["mask_doi"]="10.5281/zenodo.15261042"
    report["release_scope"]="Secondary original 2023 AHN4 individual metric files; not the revised 2025 metric archive."
    report["limitations"].append("Original 2023 metric release may differ from updated 2025 values; no equivalence asserted. Masks from updated release.")
    report["archives"].pop("4_AHN4.zip",None)
    response=requests.get(f"https://zenodo.org/api/records/{legacy}",timeout=45);response.raise_for_status()
    a=response.json();assert a["id"]==legacy and a["doi"]==report["source_doi"]
    files={x["key"]:x for x in a["files"]}
    specs={"H50":("ahn4_10m_perc_50_normalized_height.tif","2406680893fd43d7cb3628f29335fa3e"),"H95":("ahn4_10m_perc_95_normalized_height.tif","af162c4af5a9135ec78bc574f5e5acd4"),"PPR":("ahn4_10m_pulse_penetration_ratio.tif","3c6c50060ab10f583c730c5674aaf9c0")}
    for k,(name,digest) in specs.items():
        info=files[name];assert info["checksum"]=="md5:"+digest
        path=LOCAL/(k+".tif")
        full_download(f"https://zenodo.org/records/{legacy}/files/{name}?download=1",path,info["size"],digest,1_000_000_000)
        report["members"][k]={"source_release":legacy,"file":name,"bytes":info["size"],"md5":digest,"sha256":sha(path),"full_file_md5_verified":True}
        paths[k]=path
        print("AHN_LEGACY_FILE="+json.dumps({"label":k,**report["members"][k]}),flush=True)
        checkpoint()
    return paths
def correlation(x,y):
    if len(x)<3 or np.std(x)<=1e-12 or np.std(y)<=1e-12:return {"pearson":None,"spearman":None}
    return {"pearson":float(pearsonr(x,y).statistic),"spearman":float(spearmanr(x,y).statistic)}
def rmse(y,p):return float(np.sqrt(np.mean((y-p)**2)))
def ridge_predict(x,y,train,test):
    mu=x[train].mean(0);sd=x[train].std(0);sd[sd<1e-12]=1
    return Ridge(alpha=1.0).fit((x[train]-mu)/sd,y[train]).predict((x[test]-mu)/sd)
def summary(frame):
    if not len(frame):return {"cells":0}
    ans={"cells":len(frame),"blocks":len(frame[["bx50","by50"]].drop_duplicates()),"ratio":correlation(frame.R50,frame.ALS_R50),"penetration":correlation(frame.R50,frame.PPR),"height":correlation(frame.GVSM_area_mean_RH98_m,frame.H95)}
    # Mixed waveform/vegetation metrics: descriptive association, not absolute bias.
    return ans
def compare(u,threshold):
    z=u[u.ALS_valid_area_fraction.ge(threshold)&u.H95.gt(5)&u.GVSM_area_mean_RH98_m.gt(5)&u[["H50","H95","PPR","R50"]].notna().all(axis=1)].copy()
    z["ALS_R50"]=z.H50/z.H95
    z["bx50"]=z.cell_x//50;z["by50"]=z.cell_y//50
    ans={"threshold":threshold,"all":summary(z),"south":summary(z[z.south]),"north":summary(z[z.north]),"boundary_cells":int((~z.south&~z.north).sum())}
    blocks=sorted(set(zip(z.bx50,z.by50)),key=lambda b:hashlib.sha256(f"{b[0]},{b[1]}".encode()).hexdigest())
    if len(z)<30 or len(blocks)<10:ans["spatial_cv"]={"status":"INSUFFICIENT_BLOCK_SUPPORT"};return ans
    b={k:i for i,k in enumerate(blocks)}
    fold=np.array([b[k]%5 for k in zip(z.bx50,z.by50)])
    xb=z[["GVSM_area_mean_RH98_m","worldcover_class_10_fraction"]].to_numpy(float);xp=np.column_stack([xb,z.R50])
    y=z.ALS_R50.to_numpy(float);pred=np.full((len(z),2),np.nan)
    for k in range(5):
        tr=fold!=k;te=~tr
        assert tr.any() and te.any()
        pred[te,0]=ridge_predict(xb,y,tr,te);pred[te,1]=ridge_predict(xp,y,tr,te)
    def score(mask):
        n=int(mask.sum());nb=len(z.loc[mask,["bx50","by50"]].drop_duplicates())
        if n<30 or nb<4:return {"status":"INSUFFICIENT_SIDE_SUPPORT","cells":n,"blocks":nb}
        r0=rmse(y[mask],pred[mask,0]);r1=rmse(y[mask],pred[mask,1])
        return {"status":"COMPLETE","cells":n,"blocks":nb,"baseline_RMSE":r0,"profile_RMSE":r1,"gain":r0-r1}
    ans["spatial_cv"]={"all":score(np.ones(len(z),bool)),"south":score(z.south.to_numpy()),"north":score(z.north.to_numpy())}
    tr=z.south.to_numpy();te=z.north.to_numpy()
    # Avoid any training/test block overlap at the geographic boundary.
    northblocks=set(zip(z.loc[te,"bx50"],z.loc[te,"by50"]))
    tr=tr&np.array([b not in northblocks for b in zip(z.bx50,z.by50)])
    if tr.sum()>=30 and te.sum()>=30 and len(set(zip(z.loc[tr,"bx50"],z.loc[tr,"by50"])))>=4 and len(northblocks)>=4:
        p0=ridge_predict(xb,y,tr,te);p1=ridge_predict(xp,y,tr,te)
        r0=rmse(y[te],p0);r1=rmse(y[te],p1)
        ans["south_to_north"]={"train_cells":int(tr.sum()),"test_cells":int(te.sum()),"base_RMSE":r0,"profile_RMSE":r1,"gain":r0-r1}
    else:ans["south_to_north"]={"status":"INSUFFICIENT_DISJOINT_SUPPORT","train_cells":int(tr.sum()),"test_cells":int(te.sum())}
    return ans
def main():
    assert sha(SOURCE)==PIN
    u=pd.read_csv(SOURCE);assert len(u)==11006 and not u.duplicated(["cell_x","cell_y"]).any()
    I=Transformer.from_crs(6933,4326,always_xy=True)
    lon,lat=I.transform((u.cell_x.to_numpy()+.5)*1000,(u.cell_y.to_numpy()+.5)*1000)
    _,lo=I.transform(u.cell_x.to_numpy()*1000,u.cell_y.to_numpy()*1000)
    _,hi=I.transform((u.cell_x.to_numpy()+1)*1000,(u.cell_y.to_numpy()+1)*1000)
    u["lon"]=lon;u["lat"]=lat;u["south"]=hi<=51.6;u["north"]=lo>51.6
    forest=u.forest_profile_support.astype(str).str.lower().eq("true")
    u=u[forest&u.lon.between(3.57,7.11)&u.lat.between(50.77,53.36)].copy().reset_index(drop=True)
    report["candidate_cells"]=len(u);report["candidate_south"]=int(u.south.sum());report["candidate_north"]=int(u.north.sum())
    if len(u)<30:raise ValueError("insufficient preregistered candidate cells")
    checkpoint()
    paths=acquire()
    with ExitStack() as stack:
        src={k:stack.enter_context(rasterio.open(v)) for k,v in paths.items()}
        ref=src["H50"];assert ref.crs.to_epsg()==28992 and ref.count==1
        assert abs(ref.transform.a-10)<1e-6 and abs(ref.transform.e+10)<1e-6
        for k,s in src.items():
            assert s.count==1 and s.crs==ref.crs
            assert abs(s.transform.a-10)<1e-6 and abs(s.transform.e+10)<1e-6 and s.transform.b==0 and s.transform.d==0
            assert abs((s.transform.c-ref.transform.c)/10-round((s.transform.c-ref.transform.c)/10))<1e-6
            assert abs((s.transform.f-ref.transform.f)/10-round((s.transform.f-ref.transform.f)/10))<1e-6
            report["metrics"][k]={"crs":str(s.crs),"shape":[s.height,s.width],"transform":list(s.transform),"dtype":s.dtypes[0],"nodata":float(s.nodata) if s.nodata is not None and math.isfinite(s.nodata) else None,"units":s.units[0]}
        ans=np.full((len(u),4),np.nan)
        failures=collections.Counter()
        # Bounded 10km source windows to avoid loading country-wide fine-resolution arrays.
        for _,part in u.groupby([u.cell_x//10,u.cell_y//10]):
            x0=int(part.cell_x.min())*1000;x1=(int(part.cell_x.max())+1)*1000
            y0=int(part.cell_y.min())*1000;y1=(int(part.cell_y.max())+1)*1000
            l,b,r,t=transform_bounds("EPSG:6933",ref.crs,x0,y0,x1,y1,densify_pts=21)
            ww=from_bounds(l,b,r,t,ref.transform)
            c0=math.floor(ww.col_off)-3;r0=math.floor(ww.row_off)-3;c1=math.ceil(ww.col_off+ww.width)+3;r1=math.ceil(ww.row_off+ww.height)+3
            win=Window(c0,r0,c1-c0,r1-r0);tr=win_transform(win,ref.transform);shape=(int(win.height),int(win.width))
            assert shape[0]*shape[1]<4_000_000
            def read_same(s):
                # All sources share aligned Dutch 10m grid; account for different extents.
                cc=int(round((tr.c-s.transform.c)/10));rr=int(round((s.transform.f-tr.f)/10))
                a=s.read(1,window=Window(cc,rr,shape[1],shape[0]),boundless=True,masked=True)
                data=a.data.astype(np.float32);mask=~np.ma.getmaskarray(a)&np.isfinite(data)
                # Enforce raster footprint explicitly.
                yy=np.arange(rr,rr+shape[0]);xx=np.arange(cc,cc+shape[1])
                inside=(yy[:,None]>=0)&(yy[:,None]<s.height)&(xx[None,:]>=0)&(xx[None,:]<s.width)
                return data,mask&inside,inside
            A={k:read_same(s) for k,s in src.items()}
            h50,m50,_=A["H50"];h95,m95,_=A["H95"];ppr,mp,_=A["PPR"]
            brw,mb,_=A["brw"];power,mo,power_inside=A["power"]
            # The published powerline mask has 1 at powerlines and NoData elsewhere;
            # NoData is interpreted as not a mapped powerline only inside mask footprint.
            if np.any(mb&~np.isin(brw,[0,1])):raise ValueError("unexpected building-road-water mask values")
            if np.any(mo&~np.isin(power,[0,1])):raise ValueError("unexpected powerline mask values")
            physical=m50&m95&mp
            order=(h50>=0)&(h95>=h50)&(h95<=150)&(ppr>=0)&(ppr<=1)
            failures["invalid_or_unordered_10m_pixels"]+=int((physical&~order).sum())
            valid=physical&order&mb&(brw==0)&power_inside&~(mo&(power==1))
            dtr=from_origin(x0,y1,1000,1000);dshape=((y1-y0)//1000,(x1-x0)//1000)
            area=np.zeros(dshape,np.float32)
            reproject(valid.astype(np.float32),area,src_transform=tr,src_crs=ref.crs,dst_transform=dtr,dst_crs="EPSG:6933",resampling=Resampling.average)
            if np.any((area<-.001)|(area>1.001)):raise ValueError("invalid fraction")
            vals=[]
            for a in [h50,h95,ppr]:
                v=np.where(valid,a,-9999).astype(np.float32);o=np.full(dshape,-9999,np.float32)
                reproject(v,o,src_transform=tr,src_crs=ref.crs,src_nodata=-9999,dst_transform=dtr,dst_crs="EPSG:6933",dst_nodata=-9999,resampling=Resampling.average)
                vals.append(np.where(o==-9999,np.nan,o))
            for i,row in part.iterrows():
                rr=int(y1//1000-row.cell_y-1);cc=int(row.cell_x-x0//1000)
                ans[i]=[area[rr,cc],*[v[rr,cc] for v in vals]]
        report["source_pixel_qc_counts"]=dict(failures)
    u[["ALS_valid_area_fraction","H50","H95","PPR"]]=ans
    u["ALS_R50"]=np.where(u.H95.gt(5),u.H50/u.H95,np.nan)
    report["valid_any_als_cells"]=int(u.H95.notna().sum())
    report["support"]={str(t):compare(u,t) for t in [.7,.5,.9]}
    p=OUT/"matched_ahn4_gvsm_cells.csv.gz"
    u[["cell_x","cell_y","lon","lat","south","north","worldcover_class_10_fraction","GVSM_area_mean_RH98_m","R50","ALS_valid_area_fraction","H50","H95","PPR","ALS_R50"]].to_csv(p,index=False,compression={"method":"gzip","mtime":0})
    report["output_sha256"]=sha(p);report["status"]="AHN4_LEGACY_STRUCTURE_PROXY_VALIDATION_COMPLETE"
    checkpoint()
if __name__=="__main__":
    try:main()
    except Exception as e:
        report.update(status="INCOMPLETE",error=type(e).__name__+": "+str(e)[:500]);checkpoint();raise
