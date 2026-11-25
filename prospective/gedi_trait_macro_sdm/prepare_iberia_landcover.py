"""Public ESA WorldCover 2021 v200 class fractions, not GEDI vegetation profiles."""
import hashlib,json,math,pathlib,sys
import numpy as np,requests,rasterio
from pyproj import Transformer
from rasterio.windows import Window,from_bounds
from rasterio.warp import transform_bounds
from rasterio.transform import from_origin
OUT=pathlib.Path("iberia_landcover");OUT.mkdir(exist_ok=True)
BBOX=(-10,35,4,44)
xmin,ymin,xmax,ymax=transform_bounds("EPSG:4326","EPSG:6933",*BBOX,densify_pts=21)
left=math.floor(xmin/1000)*1000;bottom=math.floor(ymin/1000)*1000;right=math.ceil(xmax/1000)*1000;top=math.ceil(ymax/1000)*1000
T=from_origin(left,top,1000,1000);W=(right-left)//1000;H=(top-bottom)//1000
CLASSES=[10,20,30,40,50,60,70,80,90,95,100]
LUT=np.zeros(256,dtype=np.int8)
for i,c in enumerate(CLASSES,1):LUT[c]=i
A=np.zeros((len(CLASSES)+1,H,W),dtype=np.float64)
P=Transformer.from_crs(4326,6933,always_xy=True)
report={"dataset":"ESA WorldCover 10m 2021 v200","doi":"10.5281/zenodo.7254221","stage":"land-cover area fractions only","grid_transform":list(T),"shape":[H,W],"tiles":[],"errors":{},"note":"Class 10 tree cover land-cover fraction, not canopy density, PAVD, or flight space. Centre assignment with latitude-dependent equal-area pixel weights. Incomplete source coverage stays missing; no ocean zeros inferred."}
def code(lat,lon):
    return f"N{lat:02d}"+("E" if lon>=0 else "W")+f"{abs(lon):03d}"
def read_tile(lat,lon):
    name=f"ESA_WorldCover_10m_2021_v200_{code(lat,lon)}_Map.tif"
    url="https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/"+name
    h=requests.head(url,timeout=30,allow_redirects=True)
    if h.status_code==404:
        return {"tile":name,"status":"not_distributed"}
    h.raise_for_status()
    p=OUT/"temporary_tile.tif"
    with requests.get(url,stream=True,timeout=(30,90)) as resp:
        resp.raise_for_status();d=hashlib.sha256();total=0
        with p.open("wb") as f:
            for block in resp.iter_content(1024*1024):
                total+=len(block)
                if total>512*1024*1024:raise ValueError("source tile exceeds acquisition budget")
                d.update(block);f.write(block)
        if resp.headers.get("Content-Length") and total!=int(resp.headers["Content-Length"]):raise ValueError("incomplete source bytes")
    try:
        with rasterio.open(p) as src:
            if src.crs.to_epsg()!=4326 or src.count!=1 or src.transform.a<=0 or src.transform.e>=0 or src.transform.b or src.transform.d:raise ValueError("unexpected WorldCover source grid")
            # Include complete destination grid footprint, including partial cells at AOI boundary.
            west,south,east,north=transform_bounds("EPSG:6933","EPSG:4326",left,bottom,right,top,densify_pts=21)
            l=max(west,src.bounds.left);rr=min(east,src.bounds.right);b=max(south,src.bounds.bottom);tt=min(north,src.bounds.top)
            if l>=rr or b>=tt:return {"tile":name,"status":"outside"}
            win=from_bounds(l,b,rr,tt,src.transform)
            c0=max(0,math.floor(win.col_off));c1=min(src.width,math.ceil(win.col_off+win.width))
            r0=max(0,math.floor(win.row_off));r1=min(src.height,math.ceil(win.row_off+win.height))
            cols=np.arange(c0,c1)
            x0,_=P.transform(src.transform.c+cols*src.transform.a,np.zeros(len(cols)))
            x1,_=P.transform(src.transform.c+(cols+1)*src.transform.a,np.zeros(len(cols)))
            cx=np.floor(((x0+x1)*.5-left)/1000).astype(np.int64)
            # Constant projected source-pixel x span under equal-area cylindrical projection.
            dx=float(np.median(x1-x0))
            goodx=(cx>=0)&(cx<W)
            cmin=int(cx[goodx].min());cmax=int(cx[goodx].max());nw=cmax-cmin+1
            valid_pixels=0
            for a in range(r0,r1,256):
                z=min(a+256,r1);rows=np.arange(a,z)
                _,y0=P.transform(np.zeros(len(rows)),src.transform.f+rows*src.transform.e)
                _,y1=P.transform(np.zeros(len(rows)),src.transform.f+(rows+1)*src.transform.e)
                cy=np.floor((top-(y0+y1)*.5)/1000).astype(np.int64)
                gy=(cy>=0)&(cy<H)
                if not gy.any():continue
                rmin=int(cy[gy].min());rmax=int(cy[gy].max());nh=rmax-rmin+1
                v=src.read(1,window=Window(c0,a,c1-c0,z-a),masked=True)
                raw=np.asarray(v.data)[gy,:][:,goodx];mask=np.ma.getmaskarray(v)[gy,:][:,goodx]
                codes=LUT[raw];codes[mask]=0
                gid=(cy[gy,None]-rmin)*nw+(cx[None,goodx]-cmin)
                width=nw*nh
                ids=codes.astype(np.int64)*width+gid
                weights=np.broadcast_to(((y0-y1)[gy]*dx)[:,None],ids.shape)
                hist=np.bincount(ids.ravel(),weights=weights.ravel(),minlength=(len(CLASSES)+1)*width).reshape(len(CLASSES)+1,nh,nw)
                # Class zero means invalid/no source; don't add it to valid area.
                A[1:,rmin:rmax+1,cmin:cmax+1]+=hist[1:]
                valid_pixels+=int(np.count_nonzero(codes))
        return {"tile":name,"status":"read","url":url,"source_bytes":total,"source_sha256":d.hexdigest(),"valid_source_pixels":valid_pixels}
    finally:
        p.unlink(missing_ok=True)
def main():
    # Expand slightly to cover complete cells at the boundary, and process only distributed tiles.
    west,south,east,north=transform_bounds("EPSG:6933","EPSG:4326",left,bottom,right,top,densify_pts=21)
    for lat in range(math.floor(south/3)*3,math.ceil(north/3)*3,3):
        for lon in range(math.floor(west/3)*3,math.ceil(east/3)*3,3):
            try:
                item=read_tile(lat,lon);report["tiles"].append(item);print("LC_TILE="+json.dumps(item),flush=True)
            except Exception as exc:
                report["errors"][code(lat,lon)]=type(exc).__name__+": "+str(exc)[:300]
    if report["errors"]:
        report["status"]="INCOMPLETE_SOURCE_READ"
    else:
        cover=A[1:].sum(axis=0)
        # Centre assignment at 10m is approximate; reject coverage below 95% or implausible >105%.
        ok=(cover>=950000)&(cover<=1050000)
        nodata=-9999.0
        p=OUT/"worldcover_class_fractions_1km.tif"
        with rasterio.open(p,"w",driver="GTiff",height=H,width=W,count=len(CLASSES)+1,crs="EPSG:6933",transform=T,dtype="float32",nodata=nodata,compress="deflate",tiled=True,blockxsize=256,blockysize=256) as dst:
            for i,c in enumerate(CLASSES,1):
                arr=np.full((H,W),nodata,np.float32);arr[ok]=(A[i][ok]/cover[ok]).astype(np.float32)
                dst.write(arr,i);dst.set_band_description(i,f"class_{c}_fraction")
            dst.write((cover/1e6).astype(np.float32),len(CLASSES)+1);dst.set_band_description(len(CLASSES)+1,"valid_area_fraction")
        with p.open("rb") as f:report["crop_sha256"]=hashlib.file_digest(f,"sha256").hexdigest()
        report.update({"status":"LANDCOVER_GRID_READY" if ok.any() else "NO_VALID_GRID_CELLS","cells_valid":int(ok.sum()),"cells_tree_fraction_at_least_0_3":int((ok&(A[1]>=.3*cover)).sum()),"crop_bytes":p.stat().st_size})
    (OUT/"manifest.json").write_text(json.dumps(report,indent=2))
    print("LC_REPORT="+json.dumps(report),flush=True)
    return int(report["status"]!="LANDCOVER_GRID_READY")
if __name__=="__main__":sys.exit(main())
