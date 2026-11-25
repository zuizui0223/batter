"""Historical Nordic ALS proxy check. No bat-label fitting.
See ECODES_DK15_VALIDATION_CONTRACT_V1.md. All source files are independently checksummed.
"""
import collections,hashlib,json,math,pathlib,re,shutil,sys,tarfile,time
from contextlib import ExitStack
from functools import lru_cache
import numpy as np,pandas as pd,requests,rasterio
from rasterio.windows import Window
from rasterio.transform import from_origin
from rasterio.warp import transform_bounds,reproject,Resampling
from pyproj import Transformer
from scipy.stats import pearsonr,spearmanr
from sklearn.linear_model import Ridge
OUT=pathlib.Path("ecodes_validation");OUT.mkdir(exist_ok=True)
LOCAL=pathlib.Path("ecodes_local");LOCAL.mkdir(exist_ok=True)
CACHE=pathlib.Path("ecodes_download_cache");CACHE.mkdir(exist_ok=True)
SOURCE=pathlib.Path("fixed/cell_environment_common_grid.csv.gz")
PIN="5fc8ae81149ba9436882f3614b6eac8e51c7e79d0d88aa3c5ba15ccc717331e8"
RECORD=5752926
SPECS={"masks":("994af8e8cdeee5f85ee4aedcdff0b0c3",30_000_000),"building_proportion":("2b1f149d954d15346fb63b864b5f0525",100_000_000),"canopy_height":("0fcbae7de6442800f6815d1951fa5cc6",450_000_000),"normalized_z_mean":("3fbbf56ef15a932d63040dd26ef5cbfd",450_000_000),"canopy_openness":("29c230ec59064110b41062881740835c",550_000_000)}
report={"stage":"independent historical northern ALS proxy validation, no ecological fit","doi":"10.5281/zenodo.5752926","publication":"10.5194/essd-14-823-2022","source_environment_sha256":PIN,"ALS_period":"2014-2015","GVSM_year":2020,"status":"START","archives":{},"limitations":["All-return ALS mean height/vegetation P95 is not GVSM RH50/RH98, PAVD, or air volume.","2014-15 ALS vs 2020 GVSM; temporal change and acquisition conditions may affect agreement.","Selected forest-support occurrence cells, not a random sample of Danish forests.","Northern-only historical comparison, no direct south/north error contrast or bat occupancy inference."]}
def sha(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def save():
    (OUT/"report.json").write_text(json.dumps(report,indent=2,allow_nan=False))
    print("ECODES_REPORT="+json.dumps(report,allow_nan=False),flush=True)
def download(name):
    digest,cap=SPECS[name];filename=name+".tar.bz2";p=CACHE/filename
    if p.exists():
        with p.open("rb") as f:cached_md5=hashlib.file_digest(f,"md5").hexdigest()
        if p.stat().st_size<=cap and cached_md5==digest:
            report["archives"][name]={"bytes":p.stat().st_size,"md5":digest,"md5_verified":True,"sha256":sha(p),"url":"verified local cache"}
            print("ECODES_CACHE_HIT",name,p.stat().st_size,flush=True);return p
        p.unlink()
    urls=[f"https://zenodo.org/records/{RECORD}/files/{filename}?download=1",f"https://zenodo.org/api/records/{RECORD}/files/{filename}/content"]
    for i,url in enumerate(urls):
        n=0;h=hashlib.md5()
        try:
            with requests.get(url,stream=True,timeout=(25,120),headers={"User-Agent":"batter-ecodes-nordic-validation/1.0","Accept-Encoding":"identity"}) as resp:
                resp.raise_for_status()
                with p.open("wb") as f:
                    for buf in resp.iter_content(4*1024*1024):
                        if not buf:continue
                        n+=len(buf)
                        if n>cap:raise ValueError("archive cap exceeded")
                        h.update(buf);f.write(buf)
                if resp.headers.get("Content-Length") and int(resp.headers["Content-Length"])!=n:raise ValueError("archive byte count mismatch")
            if h.hexdigest()!=digest:raise ValueError("published MD5 mismatch")
            report["archives"][name]={"bytes":n,"md5":digest,"md5_verified":True,"sha256":sha(p),"url":url}
            print("ECODES_DOWNLOAD",name,n,flush=True);return p
        except (requests.RequestException,OSError,ValueError) as e:
            p.unlink(missing_ok=True)
            if i==len(urls)-1:raise
            print("ECODES_TRANSPORT",name,type(e).__name__,str(e)[:160],flush=True);time.sleep(4)
def cell_bounds(x,y):
    return transform_bounds("EPSG:6933","EPSG:25832",x*1000,y*1000,(x+1)*1000,(y+1)*1000,densify_pts=21)
def extract(name,ids):
    p=download(name);folder=LOCAL/name;folder.mkdir(exist_ok=True)
    files=[];manifest=[];seen=set();n=0
    with tarfile.open(p,"r|bz2") as z:
        for item in z:
            if not item.isfile():continue
            base=pathlib.PurePosixPath(item.name).name
            if not base.lower().endswith((".tif",".tiff")):continue
            n+=1
            m=re.search(r"(\d{4})_(\d{3})\.(?:tif|tiff)$",base,re.I)
            if name=="masks":
                k="inland_water_mask" if "inland_water_mask" in base.lower() else "sea_mask" if "sea_mask" in base.lower() else None
                if k is None:continue
                if m and (int(m[1]),int(m[2])) not in ids:continue
            else:
                k=name
                if not m or (int(m[1]),int(m[2])) not in ids:continue
            if base in seen:raise ValueError("duplicate member basename "+base)
            seen.add(base)
            if item.size>600_000_000:raise ValueError("member budget exceeded")
            out=folder/base
            with z.extractfile(item) as src,out.open("wb") as dst:shutil.copyfileobj(src,dst)
            if out.stat().st_size!=item.size:raise ValueError("member size mismatch")
            files.append((k,out));manifest.append({"layer":k,"member":item.name,"bytes":item.size,"sha256":sha(out)})
    # Keep verified original archives for future repair; no repeated downloads.
    if not files:raise ValueError("no target files extracted for "+name)
    mp=OUT/(name+"_members.json");mp.write_text(json.dumps(manifest,indent=2))
    report["archives"][name].update({"raster_members_total":n,"selected_members":len(files),"manifest_sha256":sha(mp)})
    print("ECODES_EXTRACT",name,n,len(files),flush=True);save()
    return files
def catalog(files):
    # Do not infer footprints from the filename or assume every tile is 100x100.
    # Every actual native grid edge is checked and indexed, including cropped tiles.
    result=collections.defaultdict(lambda:collections.defaultdict(list));wide={}
    inventory=[];shapes=collections.defaultdict(collections.Counter);unusual=[]
    for key,p in files:
        with rasterio.open(p) as s:
            row={"layer":key,"file":p.name,"crs":str(s.crs),"shape":[s.height,s.width],"transform":list(s.transform),"bounds":list(s.bounds),"nodata":s.nodata,"dtype":s.dtypes[0]}
            inventory.append(row)
            assert s.crs.to_epsg()==25832 and s.count==1,row
            assert abs(s.transform.a-10)<1e-7 and abs(s.transform.e+10)<1e-7 and s.transform.b==s.transform.d==0,row
            assert abs(s.transform.c/10-round(s.transform.c/10))<1e-6 and abs(s.transform.f/10-round(s.transform.f/10))<1e-6,row
            assert s.nodata==-9999 or (key.endswith("_mask") and s.nodata is None),row
            l,bt,rr,tt=[int(round(v/10))*10 for v in s.bounds]
            assert rr-l==s.width*10 and tt-bt==s.height*10,row
            shapes[key][f"{s.width}x{s.height}"]+=1
            if not (s.width==s.height==100 and l%1000==0 and bt%1000==0):
                if len(unusual)<12:unusual.append(row)
            # A national mask is handled as a single source. Other extents may be
            # clipped or padded tiles; use their actual bounds, not filename bounds.
            if s.width>1500 or s.height>1500:
                if not key.endswith("_mask") or key in wide:raise ValueError("unexpected wide raster: "+str(row))
                wide[key]=p;continue
            entry=(p,l,bt,rr,tt)
            for i in range(l//1000,math.ceil(rr/1000)):
                for j in range(bt//1000,math.ceil(tt/1000)):result[key][(i,j)].append(entry)
    for name in ["canopy_height","normalized_z_mean","canopy_openness","building_proportion","inland_water_mask","sea_mask"]:
        if name not in result and name not in wide:raise ValueError("missing source layer "+name)
        if name in result and name in wide:raise ValueError("ambiguous national and tiled source: "+name)
    p=OUT/"native_tile_metadata.json.gz"
    import gzip
    with gzip.open(p,"wt",encoding="utf8") as f:json.dump(inventory,f,allow_nan=False)
    report["native_tile_metadata_sha256"]=sha(p)
    report["native_tile_shapes"]={k:dict(v) for k,v in shapes.items()}
    report["native_nonstandard_examples"]=unusual
    report["native_tiles_by_layer"]=dict(collections.Counter(x["layer"] for x in inventory))
    print("ECODES_GRID_QC="+json.dumps({"shapes":report["native_tile_shapes"],"examples":unusual}),flush=True);save()
    return result,wide
@lru_cache(maxsize=192)
def read_tile(p):
    with rasterio.open(p) as src:
        z=src.read(1,masked=True)
        a=z.data.astype("float32")
        a[np.ma.getmaskarray(z)|~np.isfinite(a)|(a==-9999)]=np.nan
        return a
CONFLICTS=collections.Counter()
OVERLAPS=collections.Counter()
def raster_window(name,box,tile_paths,wide):
    l,b,r,t=box;h=(t-b)//10;w=(r-l)//10
    if name in wide:
        with rasterio.open(wide[name]) as s:
            c=int(round((l-s.transform.c)/10));rr=int(round((s.transform.f-t)/10))
            z=s.read(1,window=Window(c,rr,w,h),boundless=True,masked=True,fill_value=-9999)
            a=z.data.astype("float32")
            a[np.ma.getmaskarray(z)|~np.isfinite(a)|(a==-9999)]=np.nan
            # Explicitly exclude boundless padding, including masks with no declared nodata.
            inside=(np.arange(rr,rr+h)[:,None]>=0)&(np.arange(rr,rr+h)[:,None]<s.height)&(np.arange(c,c+w)[None,:]>=0)&(np.arange(c,c+w)[None,:]<s.width)
            a[~inside]=np.nan
            return a
    a=np.full((h,w),np.nan,np.float32);bad=np.zeros((h,w),bool)
    entries=set()
    for i in range(l//1000,math.ceil(r/1000)):
        for j in range(b//1000,math.ceil(t/1000)):entries.update(tile_paths[name].get((i,j),[]))
    for p,L,B,R,T in sorted(entries,key=lambda v:str(v[0])):
        x0=max(l,L);x1=min(r,R);y0=max(b,B);y1=min(t,T)
        if x0>=x1 or y0>=y1:continue
        z=read_tile(p)[(T-y1)//10:(T-y0)//10,(x0-L)//10:(x1-L)//10]
        dst=a[(t-y1)//10:(t-y0)//10,(x0-l)//10:(x1-l)//10]
        flags=bad[(t-y1)//10:(t-y0)//10,(x0-l)//10:(x1-l)//10]
        assert z.shape==dst.shape
        overlap=np.isfinite(dst)&np.isfinite(z)
        conflict=overlap&(dst!=z)
        OVERLAPS[name]+=int(overlap.sum());CONFLICTS[name]+=int(conflict.sum())
        # Identical overlapping pixels are counted once. Conflicting source
        # pixels are excluded, never silently resolved by tile order.
        flags|=conflict
        take=~np.isfinite(dst)&np.isfinite(z)&~flags
        dst[take]=z[take];dst[flags]=np.nan
    return a
def match(u,tiles,wide):
    ans=np.full((len(u),4),np.nan)
    for i,v in u.iterrows():
        x=int(v.cell_x);y=int(v.cell_y)
        l,b,r,t=cell_bounds(x,y)
        # Snap source window to 10m and pad it to cover projected target footprint.
        l=int(math.floor(l/10)*10-20);b=int(math.floor(b/10)*10-20)
        r=int(math.ceil(r/10)*10+20);t=int(math.ceil(t/10)*10+20)
        box=(l,b,r,t)
        A={k:raster_window(k,box,tiles,wide) for k in ["canopy_height","normalized_z_mean","canopy_openness","building_proportion","inland_water_mask","sea_mask"]}
        h=A["canopy_height"]/100;m=A["normalized_z_mean"]/100;o=A["canopy_openness"]/10000
        bp=A["building_proportion"]/10000;water=A["inland_water_mask"];sea=A["sea_mask"]
        # Valid 0 canopy heights are retained; negative mean normalized heights are allowed.
        valid=np.isfinite(h)&np.isfinite(m)&np.isfinite(o)&np.isfinite(bp)&(h>=0)&(h<=150)&(m>=-10)&(m<=150)&(o>=0)&(o<=1)&(bp==0)&(water==1)&(sea==1)
        st=from_origin(l,t,10,10);dt=from_origin(x*1000,(y+1)*1000,1000,1000)
        area=np.zeros((1,1),np.float32)
        reproject(valid.astype(np.float32),area,src_transform=st,src_crs="EPSG:25832",dst_transform=dt,dst_crs="EPSG:6933",resampling=Resampling.average)
        vals=[]
        for a in (h,m,o):
            z=np.full((1,1),-9999,np.float32)
            reproject(np.where(valid,a,-9999).astype(np.float32),z,src_transform=st,src_crs="EPSG:25832",src_nodata=-9999,dst_transform=dt,dst_crs="EPSG:6933",dst_nodata=-9999,resampling=Resampling.average)
            vals.append(float(z[0,0]) if z[0,0]!=-9999 else np.nan)
        ans[i]=[float(area[0,0]),*vals]
        if (i+1)%100==0:print("ECODES_MATCH",i+1,len(u),flush=True)
    return ans
def corr(x,y):
    if len(x)<3 or np.std(x)<=1e-12 or np.std(y)<=1e-12:return {"pearson":None,"spearman":None}
    return {"pearson":float(pearsonr(x,y).statistic),"spearman":float(spearmanr(x,y).statistic)}
def compare(u,threshold):
    z=u[(u.ALS_valid_area_fraction>=threshold)&(u.ALS_canopy_H95_m>5)&u[["ALS_mean_to_H95","R50","GVSM_area_mean_RH98_m","worldcover_class_10_fraction","ALS_openness"]].notna().all(axis=1)].copy()
    blocks=list(zip(z.cell_x//50,z.cell_y//50));unique=sorted(set(blocks),key=lambda x:hashlib.sha256(f"{x[0]},{x[1]}".encode()).hexdigest())
    a={"threshold":threshold,"cells":len(z),"blocks":len(unique),"mean_to_H95_correlation":corr(z.R50,z.ALS_mean_to_H95),"openness_correlation":corr(z.R50,z.ALS_openness),"height_correlation":corr(z.GVSM_area_mean_RH98_m,z.ALS_canopy_H95_m)}
    if len(z)<30 or len(unique)<10:
        a["status"]="INSUFFICIENT_SPATIAL_SUPPORT";return a
    bi={b:i%5 for i,b in enumerate(unique)};fold=np.array([bi[x] for x in blocks]);y=z.ALS_mean_to_H95.to_numpy(float)
    base=z[["GVSM_area_mean_RH98_m","worldcover_class_10_fraction"]].to_numpy(float)
    extended=np.column_stack([base,z.R50]);pred=np.full((len(z),2),np.nan)
    for k in range(5):
        tr=fold!=k;te=~tr
        for j,X in enumerate([base,extended]):
            mu=X[tr].mean(0);sd=X[tr].std(0);sd[sd<1e-12]=1
            pred[te,j]=Ridge(alpha=1).fit((X[tr]-mu)/sd,y[tr]).predict((X[te]-mu)/sd)
    assert np.isfinite(pred).all()
    error=(pred-y[:,None])**2;rmse=np.sqrt(error.mean(0))
    a.update(status="COMPLETE_DESCRIPTIVE",baseline_RMSE=float(rmse[0]),profile_RMSE=float(rmse[1]),RMSE_gain=float(rmse[0]-rmse[1]),positive_blocks=sum(error[np.array([b==v for b in blocks]),0].mean()>error[np.array([b==v for b in blocks]),1].mean() for v in unique))
    a["positive_blocks"]=int(a["positive_blocks"])
    return a
def main():
    assert sha(SOURCE)==PIN
    u=pd.read_csv(SOURCE);assert len(u)==11006 and not u.duplicated(["cell_x","cell_y"]).any()
    I=Transformer.from_crs(6933,4326,always_xy=True)
    lon,lat=I.transform((u.cell_x.to_numpy()+.5)*1000,(u.cell_y.to_numpy()+.5)*1000)
    u["lon"]=lon;u["lat"]=lat
    u=u[u.forest_profile_support.astype(str).str.lower().eq("true")&u.lon.between(8.07,15.20)&u.lat.between(54.56,57.75)].copy().reset_index(drop=True)
    ids=set()
    for x,y in zip(u.cell_x,u.cell_y):
        l,b,r,t=cell_bounds(x,y)
        # Source naming is northing_km/easting_km; include +/-1 tile buffer,
        # then actual raster geotransforms govern spatial matching.
        for ix in range(math.floor(l/1000)-1,math.ceil(r/1000)+2):
            for iy in range(math.floor(b/1000)-1,math.ceil(t/1000)+2):ids.add((iy,ix))
    report["candidate_cells"]=len(u);report["candidate_tile_ids"]=len(ids);save()
    if len(u)<30:raise ValueError("insufficient frozen candidate cells")
    if len(ids)>18000:raise ValueError("target tile budget exceeded")
    files=[]
    for name in SPECS:files.extend(extract(name,ids))
    tiles,wide=catalog(files)
    report["verified_spatial_index_bins"]={k:len(v) for k,v in tiles.items()}
    report["verified_wide_masks"]=sorted(wide);save()
    u[["ALS_valid_area_fraction","ALS_canopy_H95_m","ALS_all_return_mean_height_m","ALS_openness"]]=match(u,tiles,wide)
    u["ALS_mean_to_H95"]=np.where(u.ALS_canopy_H95_m>5,u.ALS_all_return_mean_height_m/u.ALS_canopy_H95_m,np.nan)
    report["overlapping_source_pixel_checks"]=dict(OVERLAPS)
    report["excluded_conflicting_source_pixels"]=dict(CONFLICTS)
    p=OUT/"matched_ecodes_gvsm_cells.csv.gz"
    u[["cell_x","cell_y","lon","lat","worldcover_class_10_fraction","GVSM_area_mean_RH98_m","R50","ALS_valid_area_fraction","ALS_canopy_H95_m","ALS_all_return_mean_height_m","ALS_openness","ALS_mean_to_H95"]].to_csv(p,index=False,compression={"method":"gzip","mtime":0})
    report["matched_output_sha256"]=sha(p);report["status"]="MATCHED_SOURCE_CELLS_READY";save()
    report["support"]={str(t):compare(u,t) for t in [.7,.5,.9]}
    report["status"]="ECODES_STRUCTURE_CHECK_COMPLETE";save()
if __name__=="__main__":
    try:main()
    except Exception as e:
        report.update(status="INCOMPLETE",error=type(e).__name__+": "+str(e)[:500]);save();raise
