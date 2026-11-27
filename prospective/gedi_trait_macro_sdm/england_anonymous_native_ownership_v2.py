"""Anonymous GVSM and ESA WorldCover support, public 5 km NWBS rectangles only."""
import collections,hashlib,json,math,pathlib,re
from contextlib import ExitStack
import numpy as np,pandas as pd,requests,rasterio
from rasterio.windows import Window,from_bounds
from rasterio.warp import transform_bounds,reproject,Resampling
from rasterio.transform import from_origin
from pyproj import Transformer
from shapely.geometry import Polygon,box
O=pathlib.Path("england_anonymous_native_v2");O.mkdir(exist_ok=True)
R={"status":"START","ecological_fit":False,"credentials_used":False,"sources":[],"limitations":["Predicted GVSM return-height quantiles, not measured foliage diversity or PAVD.","GVSM 0.01-degree mixtures, not woodland-only profiles. WorldCover classification resampled nearest to 10m British National Grid for approximate land/tree areas.","No hidden NFI location inferred. No calibrated detection, true altitude or seasonal bat model."]}
GV="https://data.source.coop/geoai-ucph/gvsm/mosaics/2020/"
WC="https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/"
LEV=[10,25,50,75,90,98]
CLASSES=[10,20,30,40,50,60,70,80,90,95,100]
C=["boundingBox_SW_x_coordinate","boundingBox_SW_y_coordinate","boundingBox_NE_x_coordinate","boundingBox_NE_y_coordinate"]
P=Transformer.from_crs(4326,27700,always_xy=True)
S=requests.Session()
def need(x,m):
    if not x:raise ValueError(m)
def sha(p):
    with open(p,"rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def digest(a):return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
def save():
    text=json.dumps(R,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else str(x))
    (O/"report.json").write_text(text+"\n")
    print("ENGLAND_NATIVE_REPORT="+text,flush=True)
def probe(url):
    r={"url":url};R["sources"].append(r)
    with S.get(url,headers={"Range":"bytes=0-16383","Accept-Encoding":"identity"},stream=True,timeout=(20,60),allow_redirects=False) as q:
        r.update(http=q.status_code,content_range=q.headers.get("Content-Range"),etag=q.headers.get("ETag"),last_modified=q.headers.get("Last-Modified"),retry_after=q.headers.get("Retry-After"))
        need(q.status_code==206,"public COG range access stop "+str(q.status_code))
        need(re.fullmatch(r"bytes 0-16383/[0-9]+",r["content_range"] or "") is not None,"unexpected probe range")
        b=q.raw.read(16384)
        need(len(b)==16384 and b[:4] in (b"II*\x00",b"MM\x00*",b"II+\x00",b"MM\x00+"),"TIFF header")
        r["header_sha256"]=hashlib.sha256(b).hexdigest()
    save()
    return r
def inputs():
    p=pathlib.Path("nwbs")
    f=p/"National Woodland Bat Survey Data 2021-24.csv"
    need(sha(f)=="8556647d60d288a3e98a872afd9a5623f5c6a0d09fae84388e81b2fb47b61bd7","NWBS source pin")
    need(sha(p/"National Woodland Bat Survey Evidence Pack 2021-24.pdf")=="7d24f15b1e4cbae840e393c28fdfeaa784f765074942f7490cd7db528f824c8c","NWBS evidence pin")
    d=pd.read_csv(f)
    need(len(d)==1813 and d.siteNumber.nunique()==310 and d.locationID.nunique()==289 and d.occurrenceID.is_unique,"NWBS census")
    need(d.SRS.eq("EPSG:27700").all() and np.isfinite(d[C]).all().all() and (d[C]%5000==0).all().all(),"disclosed grid schema")
    a=d[(d[C[2]]-d[C[0]]==5000)&(d[C[3]]-d[C[1]]==5000)].copy()
    u=a[["locationID","higherGeography",*C]].drop_duplicates().sort_values("locationID")
    need(len(a)==1298 and a.siteNumber.nunique()==221 and len(u)==208 and u.locationID.nunique()==208 and len(u[C].drop_duplicates())==208 and u.higherGeography.nunique()==8,"fixed 5km roster")
    R["input"]={"rows":len(a),"sites":a.siteNumber.nunique(),"cells":len(u),"regions":u.higherGeography.nunique(),"blocks50":len({((x+2500)//50000,(y+2500)//50000) for x,y in u[C[:2]].itertuples(index=False,name=None)})}
    return u
def win(ds,b,pad=1):
    w=from_bounds(*b,transform=ds.transform)
    c0=max(0,math.floor(w.col_off)-pad);c1=min(ds.width,math.ceil(w.col_off+w.width)+pad)
    r0=max(0,math.floor(w.row_off)-pad);r1=min(ds.height,math.ceil(w.row_off+w.height)+pad)
    return Window(c0,r0,max(0,c1-c0),max(0,r1-r0))
def profile(b):
    base=pathlib.Path("cached_v1")
    old=json.loads((base/"report.json").read_text())
    need(old["status"]=="STOP_SOURCE_OR_QC" and old["reason"]=="conflicting WorldCover tile overlap","V1 archive stop identity")
    need(old["input"]=={"rows":1298,"sites":221,"cells":208,"regions":8,"blocks50":49},"V1 roster")
    levels=[];masks=[];ref=None
    R["cached_profile"]=[]
    for rh in LEV:
        url=GV+f"RH{rh}_Q1.tif"
        src=[x for x in old["sources"] if x["url"]==url];need(len(src)==1 and src[0]["http"]==206,"cached layer identity")
        rec=src[0]
        with np.load(base/f"gvsm_RH{rh}_native_crop.npz",allow_pickle=False) as z:
            raw=z["raw"];valid=z["valid"]
        need(list(raw.shape)==rec["window_shape"]==[535,650] and raw.shape==valid.shape and valid.dtype==np.bool_,"cached crop schema")
        need(digest(raw)==rec["raw_sha256"] and digest(valid)==rec["mask_sha256"],"cached crop digest")
        t=rasterio.Affine(*rec["transform"][:6]);g=(t,raw.shape)
        if ref is None:ref=g
        need(ref==g,"cached common lattice")
        levels.append(raw.astype(np.float32)*.1);masks.append(valid)
        R["cached_profile"].append({"level":rh,"raw_sha256":rec["raw_sha256"],"mask_sha256":rec["mask_sha256"]})
    z=np.stack(levels);m=np.logical_and.reduce(masks);ordered=(np.diff(z,axis=0)>=-1e-7).all(0)
    R["profile_qc"]={"all_layer_valid_pixels":int(m.sum()),"unordered_pixels":int((m&~ordered).sum()),"RH98_out_of_range":int((m&((z[-1]<0)|(z[-1]>100))).sum())}
    need(R["profile_qc"]==old["profile_qc"],"cached profile QC replay")
    m&=ordered&np.isfinite(z).all(0)&(z[-1]>=0)&(z[-1]<=100)
    return z,m,ref[0]
def native_poly(tr,r,c,n):
    a=tr.c+c*tr.a;d=tr.f+r*tr.e;b=a+tr.a;e=d+tr.e
    v=np.linspace(0,1,n+1)[:-1]
    lon=np.r_[a+(b-a)*v,np.full(n,b),b+(a-b)*v,np.full(n,a)]
    lat=np.r_[np.full(n,d),d+(e-d)*v,np.full(n,e),e+(d-e)*v]
    x,y=P.transform(lon,lat);p=Polygon(zip(x,y))
    need(p.is_valid and p.area>0,"projected native polygon")
    return p
def weights(rect,b,z,tr,n):
    w=from_bounds(*b,transform=tr)
    c0=max(0,math.floor(w.col_off)-1);c1=min(z.shape[2],math.ceil(w.col_off+w.width)+1)
    r0=max(0,math.floor(w.row_off)-1);r1=min(z.shape[1],math.ceil(w.row_off+w.height)+1)
    p=box(*rect);a=np.zeros((r1-r0,c1-c0))
    for ri,r in enumerate(range(r0,r1)):
        for ci,c in enumerate(range(c0,c1)):
            a[ri,ci]=p.intersection(native_poly(tr,r,c,n)).area
    need(abs(a.sum()-25e6)<=2500,"native polygon partition area")
    return a,(slice(r0,r1),slice(c0,c1))
def tile_ids(b):
    l,bo,r,t=b
    return [(lat,lon) for lat in range(math.floor(bo/3)*3,math.ceil(t/3)*3,3) for lon in range(math.floor(l/3)*3,math.ceil(r/3)*3,3)]
def tile_name(key):
    lat,lon=key
    return f"ESA_WorldCover_10m_2021_v200_{'N' if lat>=0 else 'S'}{abs(lat):02d}{'E' if lon>=0 else 'W'}{abs(lon):03d}_Map.tif"
INV=Transformer.from_crs(27700,4326,always_xy=True)
def destination_lonlat(rect):
    x=rect[0]+5+10*np.arange(500);y=rect[3]-5-10*np.arange(500)
    xx,yy=np.meshgrid(x,y);lon,lat=INV.transform(xx,yy)
    need(np.isfinite(lon).all() and np.isfinite(lat).all(),"inverse geographic coordinates")
    return lon,lat
def native_indices(t,lon,lat):
    col=(lon-t.c)/t.a;row=(lat-t.f)/t.e
    return np.floor(row).astype(np.int64),np.floor(col).astype(np.int64)
def native_test():
    # Independent expected indices from rasterio's native rowcol; centers and half-open boundaries.
    tr=from_origin(-3,54,.25,.25)
    lon=np.array([-2.875,-2.75,-2.5,-.125]);lat=np.array([53.875,53.75,53.5,51.125])
    a,b=native_indices(tr,lon,lat);c,d=rasterio.transform.rowcol(tr,lon,lat)
    need(np.array_equal(a,c) and np.array_equal(b,d),"native sample synthetic")
    x=np.array([-3.,-3.-1e-9,-3.+1e-9,0.]);y=np.array([51.,51.-1e-9,51.+1e-9,54.])
    need(np.array_equal(np.floor(x/3)*3,[-3,-6,-3,0]) and np.array_equal(np.floor(y/3)*3,[51,48,51,54]),"half-open tile ownership")
def read_cover(rect,b,tiles,hashes):
    lon,lat=destination_lonlat(rect)
    keys_lat=(np.floor(lat/3)*3).astype(int);keys_lon=(np.floor(lon/3)*3).astype(int)
    used=sorted(set(zip(keys_lat.ravel(),keys_lon.ravel())))
    need(set(used)<=set(tiles),"destination tile outside roster")
    dst=np.zeros((500,500),dtype=np.uint8);assigned=np.zeros_like(dst);trans=from_origin(rect[0],rect[3],10,10)
    for key in used:
        s=tiles[key];sel=(keys_lat==key[0])&(keys_lon==key[1]);lo=lon[sel];la=lat[sel]
        rr,cc=native_indices(s.transform,lo,la)
        need((rr>=0).all() and (rr<s.height).all() and (cc>=0).all() and (cc<s.width).all(),"native source index outside owned tile")
        c0,c1=int(cc.min()),int(cc.max())+1;r0,r1=int(rr.min()),int(rr.max())+1
        w=Window(c0,r0,c1-c0,r1-r0);need(w.width*w.height<=2000000,"native sample crop cap")
        a=s.read(1,window=w,masked=True);valid=~np.ma.getmaskarray(a)&np.isin(a.data,CLASSES)
        need(np.isin(a.data[~np.ma.getmaskarray(a)],CLASSES+[0,255]).all(),"unknown native class")
        v=np.where(valid,a.data,0).astype(np.uint8);dst[sel]=v[rr-r0,cc-c0];assigned[sel]+=1
        check=np.linspace(0,len(rr)-1,min(10,len(rr))).astype(int)
        ar,ac=rasterio.transform.rowcol(s.transform,lo[check],la[check])
        need(np.array_equal(rr[check],ar) and np.array_equal(cc[check],ac),"independent native index check")
        R["native_sample_checks"]+=len(check)
        h=hashes[key];h.update(np.array([c0,r0,c1,r1],dtype="<i8").tobytes());h.update(np.ascontiguousarray(a.data).tobytes());h.update(np.ascontiguousarray(valid).tobytes())
    need(np.all(assigned==1),"nonunique destination ownership")
    # V1's independent warped mosaic diagnostic on exactly the same cell; never used in output.
    old=np.zeros_like(dst);conflict=np.zeros_like(dst,dtype=bool)
    if len(tile_ids(b))>1:
        for key in tile_ids(b):
            s=tiles[key];w=win(s,b,2)
            if w.width==0 or w.height==0:continue
            need(w.width*w.height<=2000000,"diagnostic crop cap")
            a=s.read(1,window=w,masked=True);ok=~np.ma.getmaskarray(a)&np.isin(a.data,CLASSES)
            src=np.where(ok,a.data,0).astype(np.uint8);part=np.zeros_like(dst)
            reproject(src,part,src_transform=s.window_transform(w),src_crs=s.crs,src_nodata=0,dst_transform=trans,dst_crs="EPSG:27700",dst_nodata=0,resampling=Resampling.nearest,num_threads=1)
            conflict|=(old>0)&(part>0)&(old!=part);old[part>0]=part[part>0]
        rec=R["old_warp_diagnostic"];rec["multitile_cells"]+=1;rec["cells_with_conflicts"]+=int(conflict.any());rec["conflicting_pixels"]+=int(conflict.sum());rec["differences_vs_native"]+=int((old!=dst).sum());rec["max_conflict_pixels_per_cell"]=max(rec["max_conflict_pixels_per_cell"],int(conflict.sum()))
    return dst,trans,lon,lat
def main():
    native_test()
    R.update(native_sample_checks=0,old_warp_diagnostic={"multitile_cells":0,"cells_with_conflicts":0,"conflicting_pixels":0,"differences_vs_native":0,"max_conflict_pixels_per_cell":0})
    u=inputs()
    rects=[tuple(map(float,row)) for row in u[C].itertuples(index=False,name=None)]
    bounds=[transform_bounds("EPSG:27700","EPSG:4326",*r,densify_pts=21) for r in rects]
    b=(min(x[0] for x in bounds),min(x[1] for x in bounds),max(x[2] for x in bounds),max(x[3] for x in bounds))
    ids=sorted({k for v in bounds for k in tile_ids(v)});need(len(ids)<=12,"WorldCover tile budget")
    R["worldcover_tiles_needed"]=len(ids);save()
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",GDAL_HTTP_MAX_RETRY="0",GDAL_HTTP_TIMEOUT="75",CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",VSI_CACHE="TRUE",VSI_CACHE_SIZE="50000000"):
        z,m,tr=profile(b)
        rows=[];hashes={k:hashlib.sha256() for k in ids}
        with ExitStack() as es:
            tiles={}
            for key in ids:
                url=WC+tile_name(key);rec=probe(url);s=es.enter_context(rasterio.open(url))
                need(s.count==1 and s.crs.to_epsg()==4326 and s.transform.b==s.transform.d==0 and s.transform.a>0 and s.transform.e<0 and abs(s.transform.a-1/12000)<1e-8,"WorldCover native grid")
                previous=json.loads((pathlib.Path("cached_v1")/"report.json").read_text())
                pr=[v for v in previous["sources"] if v["url"]==url]
                need(len(pr)==1 and all(rec.get(k)==pr[0].get(k) for k in ("etag","content_range","header_sha256")),"WorldCover source version mismatch")
                expected=(key[1],key[0],key[1]+3,key[0]+3)
                need((s.height,s.width)==(36000,36000) and np.max(np.abs(np.asarray(s.bounds)-np.asarray(expected)))<=1e-7 and abs(s.transform.e+1/12000)<1e-8,"native tile extent mismatch")
                rec.update(shape=[s.height,s.width],nodata=s.nodata,dtype=s.dtypes[0],native_bounds=list(s.bounds),transform=list(s.transform));tiles[key]=s
            for i,(key,region,*_) in enumerate(u.itertuples(index=False,name=None)):
                rect=rects[i];bb=bounds[i]
                w,ix=weights(rect,bb,z,tr,4);w8,ix8=weights(rect,bb,z,tr,8)
                need(ix==ix8 and np.max(np.abs(w-w8))<25,"native polygon densification sensitivity")
                ok=m[ix]&(w>0);a=float(w[ok].sum())
                need(a<=25002500,"valid area exceeds rectangle")
                mean=(z[:,ix[0],ix[1]][:,ok]@w[ok]/a) if a>0 else np.full(len(LEV),np.nan)
                cover,trans,lon,lat=read_cover(rect,bb,tiles,hashes)
                valid=np.isin(cover,CLASSES);land=valid&(cover!=80);n=int(valid.sum());nl=int(land.sum())
                rr,cc=native_indices(tr,lon,lat)
                need((rr>=0).all() and (rr<m.shape[0]).all() and (cc>=0).all() and (cc<m.shape[1]).all(),"profile native mask index")
                cv=m[rr,cc].astype(np.uint8)
                land_profile=float((land&(cv==1)).sum()/nl) if nl else 0.
                tree=float((cover==10).sum()*.01)
                row={"public_location_sha256":hashlib.sha256(str(key).encode()).hexdigest(),"common_valid_area_fraction":min(a/25e6,1.),"landcover_valid_fraction":n/250000,"profile_fraction_mapped_land":land_profile,"tree_cover_ha":tree,"training_latitude_support":bb[3]<=51.6,"north_extrapolation":bb[1]>51.6}
                row["latitude_boundary"]=not(row["training_latitude_support"] or row["north_extrapolation"])
                for j,rh in enumerate(LEV):row[f"RH{rh}_m"]=float(mean[j]) if np.isfinite(mean[j]) else None
                row["R50"]=float(mean[2]/mean[-1]) if np.isfinite(mean).all() and mean[-1]>5 else None
                for cl in CLASSES:row[f"landcover_{cl}_fraction"]=float((cover==cl).sum()/n) if n else None
                for t in (.5,.7,.9):
                    row[f"passes_{t}"]=bool(a>=1e6 and a/25e6>=t and land_profile>=t and n/250000>=.95 and tree>=100 and row["R50"] is not None)
                rows.append(row)
                pd.DataFrame(rows).to_csv(O/"public_grid_checkpoint.csv",index=False)
                R["checkpoint_cells"]=len(rows);R["checkpoint_sha256"]=sha(O/"public_grid_checkpoint.csv")
                if (i+1)%30==0:print("GRID_PROGRESS",i+1,flush=True)
        R["worldcover_window_hashes"]={tile_name(k):h.hexdigest() for k,h in hashes.items()}
    d=pd.DataFrame(rows);need(len(d)==208 and d.public_location_sha256.is_unique,"output roster")
    R["support"]={}
    reg=np.array(u.higherGeography);blocks=np.asarray([((x[0]+2500)//50000,(x[1]+2500)//50000) for x in rects])
    for t in (.5,.7,.9):
        R["support"][str(t)]={}
        for label,mask in [("all",np.ones(208,dtype=bool)),("training_latitude",d.training_latitude_support.to_numpy()),("north",d.north_extrapolation.to_numpy()),("boundary",d.latitude_boundary.to_numpy())]:
            v=d[f"passes_{t}"].to_numpy()&mask
            n=int(v.sum());nr=len(set(reg[v]));nb=len(set(map(tuple,blocks[v])))
            R["support"][str(t)][label]={"cells":n,"regions":nr,"blocks50":nb,"passes_original_broad_gate":n>=150 and nr>=6 and nb>=12}
    R["coverage_summary"]={k:np.quantile(d[k],[0,.25,.5,.75,1]).tolist() for k in ["common_valid_area_fraction","landcover_valid_fraction","profile_fraction_mapped_land","tree_cover_ha"]}
    d.to_csv(O/"public_grid_environment.csv",index=False)
    R["derived_sha256"]=sha(O/"public_grid_environment.csv");R["status"]="COMPLETE_PREDICTED_PROFILE_SUPPORT_ONLY"
if __name__=="__main__":
    try:main()
    except Exception as e:R.update(status="STOP_SOURCE_OR_QC",error_type=type(e).__name__,reason=str(e)[:300])
    finally:save()
