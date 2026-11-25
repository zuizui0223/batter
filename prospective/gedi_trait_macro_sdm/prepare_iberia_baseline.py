"""Baseline climate input only, outcome-blind. No SDM and no substitute for GEDI profiles."""
import hashlib,json,math,pathlib,sys
from datetime import datetime,timezone
import numpy as np
import rasterio
from rasterio.windows import from_bounds,Window,transform
from rasterio.warp import transform_bounds,reproject,Resampling
from rasterio.transform import from_origin
OUT=pathlib.Path("iberia_baseline");OUT.mkdir(exist_ok=True)
BBOX=(-10,35,4,44)
METRICS={"bio1":"annual_mean_temperature","bio4":"temperature_seasonality","bio5":"warmest_month_max_temperature","bio6":"coldest_month_min_temperature","bio12":"annual_precipitation","bio15":"precipitation_seasonality"}
# This grid matches the preliminary zero-origin EPSG:6933 occurrence indexing, not an assertion of the GEDI native origin.
xmin,ymin,xmax,ymax=transform_bounds("EPSG:4326","EPSG:6933",*BBOX,densify_pts=21)
left=math.floor(xmin/1000)*1000;bottom=math.floor(ymin/1000)*1000;right=math.ceil(xmax/1000)*1000;top=math.ceil(ymax/1000)*1000
T=from_origin(left,top,1000,1000);W=(right-left)//1000;H=(top-bottom)//1000
NODATA=-9999.0
URL="https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_{}_1981-2010_V.2.1.tif"
report={"stage":"baseline climate acquisition only; no ecological results","checked_utc":datetime.now(timezone.utc).isoformat(),"crs":"EPSG:6933","transform":list(T),"shape":[H,W],"grid_origin":"provisional zero origin; rerun to exact GEDI grid after raster acquisition","climatology":"1981-2010","metrics":{},"errors":{}}
def digest(path):
    with path.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def grid(path,data,name):
    with rasterio.open(path,"w",driver="GTiff",height=H,width=W,count=1,crs="EPSG:6933",transform=T,dtype="float32",nodata=NODATA,compress="deflate",tiled=True,blockxsize=256,blockysize=256) as dst:
        dst.write(data,1);dst.set_band_description(1,name)
def main():
    common=np.ones((H,W),dtype=bool)
    for metric,name in METRICS.items():
        try:
            url=URL.format(metric)
            with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",GDAL_HTTP_TIMEOUT="60",GDAL_HTTP_MAX_RETRY="2",CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif"):
                with rasterio.open(url) as src:
                    if src.count!=1 or src.crs.to_epsg()!=4326:raise ValueError("unexpected source schema")
                    bounds=transform_bounds("EPSG:6933",src.crs,left,bottom,right,top,densify_pts=21)
                    w=from_bounds(*bounds,transform=src.transform)
                    c0=math.floor(w.col_off)-2;r0=math.floor(w.row_off)-2;c1=math.ceil(w.col_off+w.width)+2;r1=math.ceil(w.row_off+w.height)+2
                    window=Window(c0,r0,c1-c0,r1-r0)
                    a=src.read(1,window=window,masked=True)
                    valid=~np.ma.getmaskarray(a)&np.isfinite(a.data)
                    # Preserve raw encoded values; report actual source scale/offset and units.
                    # If source omits scaling metadata, do not invent values in physical units.
                    raw=np.where(valid,a.data,NODATA).astype("float32")
                    scale=src.scales[0];offset=src.offsets[0]
                    units=src.units[0]
                    metadata={"url":url,"crs":str(src.crs),"source_shape":[src.height,src.width],"source_transform":list(src.transform),"source_dtype":src.dtypes[0],"source_nodata":src.nodata,"declared_scale":scale,"declared_offset":offset,"declared_units":units,"source_tags":src.tags(1),"window":[c0,r0,c1-c0,r1-r0],"raw_window_sha256":hashlib.sha256(raw.tobytes()).hexdigest()}
                    dst=np.full((H,W),NODATA,np.float32)
                    reproject(raw,dst,src_transform=transform(window,src.transform),src_crs=src.crs,src_nodata=NODATA,dst_transform=T,dst_crs="EPSG:6933",dst_nodata=NODATA,resampling=Resampling.bilinear)
            ok=(dst!=NODATA)&np.isfinite(dst);common&=ok
            if not ok.any():raise ValueError("no valid climate cells")
            p=OUT/(metric+"_encoded_1km.tif");grid(p,dst,metric+"_encoded")
            report["metrics"][metric]={**metadata,"meaning":name,"valid_cells":int(ok.sum()),"encoded_quantiles":np.quantile(dst[ok],[0,.05,.5,.95,1]).tolist(),"crop_bytes":p.stat().st_size,"crop_sha256":digest(p)}
            print("BASELINE_METRIC="+json.dumps({"metric":metric,**report["metrics"][metric]}),flush=True)
        except Exception as exc:
            report["errors"][metric]=type(exc).__name__+": "+str(exc)[:400]
    report["joint_climate_cells"]=int(common.sum()) if not report["errors"] else None
    report["status"]="CLIMATE_CROPS_READY_ENCODING_QC_REQUIRED" if not report["errors"] else "INCOMPLETE"
    (OUT/"climate_manifest.json").write_text(json.dumps(report,indent=2))
    print("BASELINE_REPORT="+json.dumps(report),flush=True)
    return int(bool(report["errors"]))
if __name__=="__main__":sys.exit(main())
