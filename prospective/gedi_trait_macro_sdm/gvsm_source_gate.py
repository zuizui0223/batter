"""Alternative GVSM proxy input only; not a PAVD measurement or an SDM fit."""
import hashlib, json, pathlib, math, sys
import numpy as np, rasterio, requests
from rasterio.windows import from_bounds, Window, transform
OUT=pathlib.Path("gvsm_source");OUT.mkdir(exist_ok=True)
BASE="https://data.source.coop/geoai-ucph/gvsm/mosaics/2020/"
LEVELS=(10,25,50,75,90,98)
BBOX=(-10,35,4,44)
report={"stage":"alternative vertical structure source-only","doi":"10.31223/X5M22F","year":2020,"levels":LEVELS,"bbox":BBOX,"warning":"RH is predicted cumulative lidar return-height quantile, not PAVD or true flyable volume. Mosaic averages quantiles from 10-m predictions, not quantiles of pooled waveforms.","layers":{},"errors":{}}
arrays=[];grid=None
for rh in LEVELS:
    name=f"RH{rh}_Q1.tif";url=BASE+name
    try:
        with requests.get(url,headers={"Range":"bytes=0-16383"},stream=True,timeout=(20,60)) as response:
            response.raise_for_status()
            raw=response.raw.read(16384)
            magic=raw[:4] in (b"II*\x00",b"MM\x00*",b"II+\x00",b"MM\x00+")
            if response.status_code!=206 or not magic:raise ValueError("not verified TIFF HTTP range access")
            probe={"http":response.status_code,"range":response.headers.get("Content-Range"),"header_sha256":hashlib.sha256(raw).hexdigest()}
        with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",GDAL_HTTP_TIMEOUT="90",GDAL_HTTP_MAX_RETRY="2",CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif"):
            with rasterio.open(url) as src:
                if src.crs.to_epsg()!=4326 or src.count!=1 or not math.isclose(src.transform.a,0.01,abs_tol=1e-7) or src.nodata!=32767:
                    raise ValueError("source schema differs from catalog")
                w=from_bounds(*BBOX,transform=src.transform)
                c0=math.floor(w.col_off);r0=math.floor(w.row_off);c1=math.ceil(w.col_off+w.width);r1=math.ceil(w.row_off+w.height)
                w=Window(c0,r0,c1-c0,r1-r0)
                t=transform(w,src.transform);shape=(int(w.height),int(w.width))
                g=(str(src.crs),list(t),shape)
                if grid is None:grid=g
                elif grid!=g:raise ValueError("layer grid mismatch")
                a=src.read(1,window=w,masked=True).astype("float32")
                valid=~np.ma.getmaskarray(a)&np.isfinite(a.data)
                m=np.where(valid,a.data/10,np.nan).astype("float32") # decimetres -> m; retain negative low RH
                arrays.append(m)
                p=OUT/(name.replace(".tif","_iberia.tif"))
                with rasterio.open(p,"w",driver="GTiff",height=shape[0],width=shape[1],count=1,crs=src.crs,transform=t,dtype="float32",nodata=-9999,compress="deflate",tiled=True) as dst:
                    dst.write(np.where(valid,m,-9999),1);dst.set_band_description(1,f"predicted_mean_RH{rh}_m")
                report["layers"][str(rh)]={**probe,"url":url,"source_shape":[src.height,src.width],"source_dtype":src.dtypes[0],"valid_pixels":int(valid.sum()),"height_quantiles_m":np.quantile(m[valid],[0,.05,.5,.95,1]).tolist() if valid.any() else [],"crop_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"crop_bytes":p.stat().st_size}
                print("GVSM_LAYER="+json.dumps({"rh":rh,**report["layers"][str(rh)]}),flush=True)
    except Exception as exc:
        report["errors"][str(rh)]=type(exc).__name__+": "+str(exc)[:500]
if len(arrays)==len(LEVELS) and not report["errors"]:
    a=np.stack(arrays)
    common=np.all(np.isfinite(a),axis=0)
    crossings=common & np.any(np.diff(a,axis=0)<0,axis=0)
    canopy=common & (a[-1]>5)
    report.update({"grid":grid,"joint_valid_pixels":int(common.sum()),"profile_order_violations":int(crossings.sum()),"valid_canopy_gt5m":int(canopy.sum()),"canopy_order_violations":int((canopy&crossings).sum()),"status":"REAL_GVSM_CROPS_READY"})
else:report["status"]="INCOMPLETE"
(OUT/"manifest.json").write_text(json.dumps(report,indent=2))
print("GVSM_REPORT="+json.dumps(report),flush=True)
sys.exit(int(report["status"]!="REAL_GVSM_CROPS_READY"))
