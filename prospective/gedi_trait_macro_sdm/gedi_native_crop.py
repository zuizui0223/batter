"""Crop authoritative GEDI COGs on the native grid; refuse missing credentials or ambiguous band names."""
import json, math, os, pathlib, re, sys, hashlib
OUT=pathlib.Path("gedi_native");OUT.mkdir(exist_ok=True)
REGION=(-10,35,4,44)
DOI="10.3334/ORNLDAAC/2339"
METRICS=[f"pavd-{z}-{z+5}" for z in range(0,80,5)]+["rh-98-a0","pai-a0","cover-a0"]
def save(report):
    (OUT/"manifest.json").write_text(json.dumps(report,indent=2))
    print("GEDI_NATIVE_STATUS="+json.dumps(report),flush=True)
def main():
    report={"doi":DOI,"bbox_wgs84":REGION,"status":"BLOCKED_NO_EARTHDATA_SECRET","metrics":METRICS}
    if not (os.getenv("EARTHDATA_TOKEN") or (os.getenv("EARTHDATA_USERNAME") and os.getenv("EARTHDATA_PASSWORD"))):
        save(report);return 2
    try:
        import earthaccess, requests, rasterio, numpy as np
        from rasterio.windows import Window, from_bounds, transform as window_transform
        from rasterio.warp import transform_bounds
        auth=earthaccess.login(strategy="environment",persist=False)
        if not auth.authenticated:raise RuntimeError("Earthdata authentication failed")
        cmr=requests.get("https://cmr.earthdata.nasa.gov/search/granules.json",params={"collection_concept_id":"C3043630107-ORNL_CLOUD","page_size":2000},timeout=60);cmr.raise_for_status()
        entries=cmr.json()["feed"]["entry"]
        urls={}
        for e in entries:
            for metric in METRICS:
                if not e["title"].endswith(f"gediv002_{metric}_vf_20190417_20230316_1000m.tif"):continue
                candidates=[l["href"] for l in e.get("links",[]) if l.get("href","").startswith("https://") and l["href"].endswith(".tif") and not l.get("inherited") and "/data#" in l.get("rel","")]
                if len(set(candidates))!=1:raise ValueError("ambiguous authenticated COG URL for "+metric)
                urls[metric]=candidates[0]
        if set(urls)!=set(METRICS):raise ValueError("incomplete exact CMR metrics")
        fs=earthaccess.get_fsspec_https_session()
        ref_grid=None;manifest=[];profile=None;dest=OUT/"gedi_iberia_native.tif"
        for j,metric in enumerate(METRICS):
            with rasterio.open(urls[metric],opener=fs.open) as src:
                if src.crs.to_epsg()!=6933:raise ValueError("unexpected native CRS")
                grid=(src.width,src.height,tuple(src.transform),str(src.crs))
                if ref_grid is None:
                    ref_grid=grid
                    bounds=transform_bounds("EPSG:4326",src.crs,*REGION,densify_pts=21)
                    w=from_bounds(*bounds,transform=src.transform)
                    c0=math.floor(w.col_off);r0=math.floor(w.row_off);c1=math.ceil(w.col_off+w.width);r1=math.ceil(w.row_off+w.height)
                    w=Window(c0,r0,c1-c0,r1-r0)
                    profile={"driver":"GTiff","height":int(w.height),"width":int(w.width),"count":2*len(METRICS),"dtype":"float32","nodata":-9999.0,"crs":src.crs,"transform":window_transform(w,src.transform),"compress":"deflate","tiled":True,"blockxsize":256,"blockysize":256}
                    with rasterio.open(dest,"w",**profile):pass
                elif grid!=ref_grid:raise ValueError("non-identical source grids")
                # Do NOT infer band order. Require semantic names in raster description/tags.
                lookup={}
                for i,desc in enumerate(src.descriptions,1):
                    tags=src.tags(i)
                    labels=[desc or "",tags.get("name",""),tags.get("long_name",""),tags.get("DESCRIPTION","")]
                    labels={str(x).lower().strip().replace(" ","_") for x in labels}
                    if labels.intersection({"mean","arithmetic_mean"}):lookup["mean"]=i
                    if labels.intersection({"countf","shot_count","count","number_of_shots"}):lookup["countf"]=i
                if set(lookup)!={"mean","countf"}:
                    report["unresolved_band_metadata"]={"metric":metric,"descriptions":src.descriptions}
                    raise ValueError("band meanings not explicitly identified; use official named-band GEE route or validate band order")
                arrays=[]
                for name in ("mean","countf"):
                    arr=src.read(lookup[name],window=w,masked=True).astype("float32")
                    invalid=np.ma.getmaskarray(arr)|~np.isfinite(arr.data)|(arr.data<0)
                    arrays.append(np.where(invalid,-9999.0,arr.data).astype("float32"))
                with rasterio.open(dest,"r+") as dst:
                    for k,name in enumerate(("mean","countf")):
                        index=2*j+k+1;dst.write(arrays[k],index);dst.set_band_description(index,metric+"_"+name)
                eligible=(arrays[0]>=0)&(arrays[1]>=10)
                manifest.append({"metric":metric,"valid_mean_pixels":int((arrays[0]>=0).sum()),"pixels_count_at_least_10":int(eligible.sum()),"band_indexes":lookup})
        # Joint support across 16 layers and baseline scalars; never treat no shots as zero vegetation.
        with rasterio.open(dest) as src:
            joint=np.ones((src.height,src.width),dtype=bool)
            for j in range(len(METRICS)):joint&=(src.read(2*j+1)>=0)&(src.read(2*j+2)>=10)
            report["native_grid"]={"crs":str(src.crs),"transform":list(src.transform),"width":src.width,"height":src.height,"joint_valid_pixels":int(joint.sum())}
        with dest.open("rb") as f:report["sha256"]=hashlib.file_digest(f,"sha256").hexdigest()
        report.update({"status":"NATIVE_GEDI_CROP_READY","sources":manifest,"bytes":dest.stat().st_size})
        save(report);return 0
    except Exception as e:
        # Never log secret tokens, signed URLs or raw authentication error payloads.
        report.update({"status":"BLOCKED_EXTRACTION","error_type":type(e).__name__})
        if (OUT/"gedi_iberia_native.tif").exists():(OUT/"gedi_iberia_native.tif").unlink()
        save(report);return 1
if __name__=="__main__":sys.exit(main())
