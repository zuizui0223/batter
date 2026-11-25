"""AHN4 geometry-only repair: exact native intersections + original target-cell comparison.
Original acquisition/compare functions are blob-pinned. No bat response fitting.
"""
import collections,hashlib,json,math,pathlib,subprocess,sys
from contextlib import ExitStack
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import Window,from_bounds,transform as window_transform
from rasterio.warp import transform_bounds,reproject,Resampling
from rasterio.transform import from_origin
from pyproj import Transformer
import ahn_native_grid_overlap as overlap
import ahn4_structural_validation_v1 as old
ROOT=pathlib.Path(__file__).resolve().parent
PIN="7b220c5451349d0fd46e5d9d5cea6bbd99c0b198"
SOURCE=old.SOURCE
OUT=old.OUT
WINDOWS=OUT/"native_window_checkpoints";WINDOWS.mkdir(exist_ok=True)
# Read canonical member hashes from the previous completed acquisition receipt.
# Validate the receipt before issuing any network requests.
RECEIPT=ROOT/"AHN4_GRID_STOP_RECEIPT_V1.json"
receipt=json.loads(RECEIPT.read_text())
assert receipt["audit"]["run_id"]==45601066021
assert receipt["source_doi"]=="10.5281/zenodo.15261042"
assert set(receipt["members"])==set(overlap.KEYS)
MEMBER_PINS={k:v["sha256"] for k,v in receipt["members"].items()}
assert all(v["crc_checked"] and len(v["sha256"])==64 and all(c in "0123456789abcdef" for c in v["sha256"]) for v in receipt["members"].values())
report=old.report
report.update(stage="independent ALS structural proxy validation, V2 geometry correction only",original_acquisition_and_comparison_blob=PIN,geometry="exact shared native rectangle intersections, then approximate GDAL area-average to EPSG:6933")
report["limitations"].append("Cross-CRS destination aggregation uses GDAL average, not exact geodesic intersections; native rectangle overlaps are integrated before it.")
def sha(p):return old.sha(p)
def checkpoint():old.checkpoint()
def native_window(s,tr,shape):
    h,w=shape;sx=s.transform.c;sv=-s.transform.f
    x0=tr.c;v0=-tr.f;x1=x0+10*w;v1=v0+10*h
    c0=math.floor((x0-sx)/10)-1;c1=math.ceil((x1-sx)/10)+1
    r0=math.floor((v0-sv)/10)-1;r1=math.ceil((v1-sv)/10)+1
    sh=(r1-r0,c1-c0)
    assert sh[0]*sh[1]<4_100_000
    data=np.full(sh,np.nan,np.float32);valid=np.zeros(sh,bool);inside=np.zeros(sh,bool)
    a=max(c0,0);b=min(c1,s.width);c=max(r0,0);d=min(r1,s.height)
    if a<b and c<d:
        z=s.read(1,window=Window(a,c,b-a,d-c),masked=True)
        sl=(slice(c-r0,d-r0),slice(a-c0,b-c0))
        v=z.data.astype(np.float32)
        data[sl]=v;valid[sl]=~np.ma.getmaskarray(z)&np.isfinite(v);inside[sl]=True
    return data,valid,inside,sx+c0*10,sv+r0*10
def source_meta(s):
    return {"crs":str(s.crs),"shape":[s.height,s.width],"transform":list(s.transform),"dtype":s.dtypes[0],"nodata":float(s.nodata) if s.nodata is not None and math.isfinite(s.nodata) else None,"units":s.units[0],"scale":float(s.scales[0]),"offset":float(s.offsets[0])}
def validate_source_schema(src):
    ref=src["H50"]
    report["metrics"]={k:source_meta(s) for k,s in src.items()}
    checkpoint() # preserve actual grids even on subsequent admission stop
    assert ref.crs is not None and ref.crs.to_epsg()==28992
    for k,s in src.items():
        if not(s.count==1 and s.crs==ref.crs and abs(s.transform.a-10)<1e-9 and abs(s.transform.e+10)<1e-9 and abs(s.transform.b)<1e-12 and abs(s.transform.d)<1e-12):
            raise ValueError("unsupported native grid: "+k)
        if not(math.isclose(s.scales[0],1,abs_tol=1e-12) and math.isclose(s.offsets[0],0,abs_tol=1e-12)):
            raise ValueError("unexpected source scale/offset: "+k)
    report["native_origin_offsets_m"]={k:{"x":float(s.transform.c-ref.transform.c),"southward":float(ref.transform.f-s.transform.f),"x_mod10":float((s.transform.c-ref.transform.c)%10),"southward_mod10":float((ref.transform.f-s.transform.f)%10)} for k,s in src.items()}
    report["native_grid_schema"]="PASS_REAL_AFFINES_NOT_SNAPPED"
    checkpoint()
    return ref
def save_windows(u,paths):
    manifest=[];byte_total=0
    with ExitStack() as stack:
        src={k:stack.enter_context(rasterio.open(v)) for k,v in paths.items()}
        ref=validate_source_schema(src)
        # Preserve the same bounded 10km grouping as the original, with native origins.
        for n,(_,part) in enumerate(u.groupby([u.cell_x//10,u.cell_y//10],sort=True)):
            x0=int(part.cell_x.min())*1000;x1=(int(part.cell_x.max())+1)*1000
            y0=int(part.cell_y.min())*1000;y1=(int(part.cell_y.max())+1)*1000
            l,b,r,t=transform_bounds("EPSG:6933",ref.crs,x0,y0,x1,y1,densify_pts=21)
            w=from_bounds(l,b,r,t,ref.transform)
            c0=math.floor(w.col_off)-3;r0=math.floor(w.row_off)-3;c1=math.ceil(w.col_off+w.width)+3;r1=math.ceil(w.row_off+w.height)+3
            win=Window(c0,r0,c1-c0,r1-r0);tr=window_transform(win,ref.transform)
            shape=(int(win.height),int(win.width));assert shape[0]*shape[1]<4_000_000
            payload={"reference_transform":np.asarray(list(tr)[:6],float),"reference_shape":np.asarray(shape,np.int64),"target_bounds":np.asarray([x0,y0,x1,y1],np.int64),"target_indices":part.index.to_numpy(np.int64),"target_cells":part[["cell_x","cell_y"]].to_numpy(np.int64)}
            for k,s in src.items():
                a,m,i,ox,ov=native_window(s,tr,shape)
                payload[k+"_data"]=a;payload[k+"_valid"]=m;payload[k+"_inside"]=i;payload[k+"_origin"]=np.asarray([ox,ov],float)
            p=WINDOWS/f"window_{n:04d}.npz";np.savez_compressed(p,**payload)
            size=p.stat().st_size;byte_total+=size
            manifest.append({"file":p.name,"sha256":sha(p),"bytes":size,"cells":len(part)})
            (WINDOWS/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
            if byte_total>600_000_000:raise ValueError("native crop checkpoint budget exceeded")
            if (n+1)%20==0:print("AHN_NATIVE_WINDOWS_READY",n+1,byte_total,flush=True)
    assert sum(x["cells"] for x in manifest)==len(u)
    report["native_window_checkpoints"]={"count":len(manifest),"bytes":byte_total,"manifest_sha256":sha(WINDOWS/"manifest.json"),"all_candidate_cells":len(u)}
    report["status"]="NATIVE_WINDOWS_READY";checkpoint()
    return manifest
def aggregate(u,manifest):
    from affine import Affine
    ans=np.full((len(u),4),np.nan)
    written=set();diag={"windows":0,"invalid_equivalent_10m_pixels_sum_over_windows":0.,"max_x_intervals":0,"max_y_intervals":0,"valid_fraction_min":None,"valid_fraction_max":None}
    for entry in manifest:
        p=WINDOWS/entry["file"];assert sha(p)==entry["sha256"]
        with np.load(p,allow_pickle=False) as z:
            tr=Affine(*z["reference_transform"]);shape=tuple(map(int,z["reference_shape"]))
            x0,y0,x1,y1=map(int,z["target_bounds"]);indices=z["target_indices"];cells=z["target_cells"]
            assert np.array_equal(u.loc[indices,["cell_x","cell_y"]].to_numpy(),cells)
            layers={k:(z[k+"_data"],z[k+"_valid"],z[k+"_inside"],*map(float,z[k+"_origin"])) for k in overlap.KEYS}
            area,nums,info=overlap.integrate(layers,tr.c,-tr.f,shape)
        diag["windows"]+=1;diag["invalid_equivalent_10m_pixels_sum_over_windows"]+=info["invalid_equivalent_10m_pixels"]
        diag["max_x_intervals"]=max(diag["max_x_intervals"],info["x_intervals"]);diag["max_y_intervals"]=max(diag["max_y_intervals"],info["y_intervals"])
        dtr=from_origin(x0,y1,1000,1000);dshape=((y1-y0)//1000,(x1-x0)//1000)
        def warp(a):
            o=np.full(dshape,np.nan,np.float64)
            reproject(a,o,src_transform=tr,src_crs="EPSG:28992",dst_transform=dtr,dst_crs="EPSG:6933",dst_nodata=np.nan,resampling=Resampling.average)
            return o
        den=warp(area);num=np.stack([warp(a) for a in nums])
        if not np.isfinite(den).all() or not np.isfinite(num).all() or np.any(den<-.000001) or np.any(den>1.000001):raise ValueError("invalid destination common area")
        vals=np.full(num.shape,np.nan);np.divide(num,den[None,:,:],out=vals,where=den[None,:,:]>0)
        for i,(cx,cy) in zip(indices,cells):
            i=int(i);rr=int(y1//1000-cy-1);cc=int(cx-x0//1000)
            assert i not in written and 0<=rr<dshape[0] and 0<=cc<dshape[1]
            written.add(i);ans[i]=[den[rr,cc],*vals[:,rr,cc]]
        if diag["windows"]%20==0:print("AHN_NATIVE_OVERLAP_AGGREGATED",diag["windows"],len(manifest),flush=True)
    assert len(written)==len(u) and np.isfinite(ans[:,0]).all()
    diag["valid_fraction_min"]=float(ans[:,0].min());diag["valid_fraction_max"]=float(ans[:,0].max())
    report["native_overlap_qc"]=diag
    return ans
def acquire_verified_members():
    """Recover already verified source members, with per-member hash checks.
    Keep original acquisition functions unchanged; no invalid cache can enter analysis.
    """
    names={"brw":"ahn4_10m_mask_building_road_water.tif","power":"ahn4_10m_mask_powerline.tif","H50":"ahn4_10m_perc_50_normalized_height.tif","H95":"ahn4_10m_perc_95_normalized_height.tif","PPR":"ahn4_10m_pulse_penetration_ratio.tif"}
    sizes={"brw":86253446,"power":37601958,"H50":647003458,"H95":763217494,"PPR":826610282}
    paths={}
    for k,h in MEMBER_PINS.items():
        p=old.LOCAL/(k+".tif")
        if p.exists():
            actual=sha(p)
            if p.stat().st_size==sizes[k] and actual==h:
                paths[k]=p
                report["members"][k]={"member":names[k],"bytes":sizes[k],"sha256":actual,"verified_cache_hit":True}
            else:
                p.unlink()
    report["reused_source_members"]=sorted(paths)
    checkpoint()
    if len(paths)<5:
        old.metadata()
    missing=[k for k in ("brw","power") if k not in paths]
    if missing:
        import zipfile
        archive="6_Masks.zip";info=report["archives"][archive]
        p=old.LOCAL/archive
        old.full_download(info["url"],p,info["size"],info["published_checksum"].split(":")[1],300_000_000)
        report["archives"][archive]["full_archive_md5_verified"]=True
        with zipfile.ZipFile(p) as z:
            old.inventory(z,archive)
            for k in missing:
                paths[k]=old.extract(z,old.member(z,names[k]),k,archive)
                assert paths[k].stat().st_size==sizes[k] and sha(paths[k])==MEMBER_PINS[k],k
        p.unlink()
    missing=[k for k in ("H50","H95","PPR") if k not in paths]
    if missing:
        import zipfile
        archive="4_AHN4.zip";info=report["archives"][archive]
        url=f"https://zenodo.org/api/records/{old.RECORD}/files/{archive}/content"
        rr=old.RangeReader(url,info["size"])
        report["archives"][archive]["actual_range_url"]=url
        with zipfile.ZipFile(rr) as z:
            old.inventory(z,archive)
            for k in missing:
                paths[k]=old.extract(z,old.member(z,names[k]),k,archive)
                assert paths[k].stat().st_size==sizes[k] and sha(paths[k])==MEMBER_PINS[k],k
        report["archives"][archive]["range_bytes_read"]=rr.transferred
        report["archives"][archive]["full_archive_md5_verified"]=False
        rr.session.close()
    assert set(paths)==set(MEMBER_PINS)
    return paths

def main():
    assert subprocess.check_output(["git","hash-object",str(ROOT/"ahn4_structural_validation_v1.py")],text=True).strip()==PIN
    report["synthetic_tests"]=overlap.synthetic_checks();assert all(report["synthetic_tests"].values())
    report["member_pin_source"]={"receipt":RECEIPT.name,"sha256":sha(RECEIPT),"validated_members":len(MEMBER_PINS)}
    assert sha(SOURCE)==old.PIN
    u=pd.read_csv(SOURCE);assert len(u)==11006 and not u.duplicated(["cell_x","cell_y"]).any()
    I=Transformer.from_crs(6933,4326,always_xy=True)
    lon,lat=I.transform((u.cell_x.to_numpy()+.5)*1000,(u.cell_y.to_numpy()+.5)*1000)
    _,lo=I.transform(u.cell_x.to_numpy()*1000,u.cell_y.to_numpy()*1000)
    _,hi=I.transform((u.cell_x.to_numpy()+1)*1000,(u.cell_y.to_numpy()+1)*1000)
    u["lon"]=lon;u["lat"]=lat;u["south"]=hi<=51.6;u["north"]=lo>51.6
    forest=u.forest_profile_support.astype(str).str.lower().eq("true")
    u=u[forest&u.lon.between(3.57,7.11)&u.lat.between(50.77,53.36)].copy().reset_index(drop=True)
    assert (len(u),int(u.south.sum()),int(u.north.sum()))==(636,318,312)
    report.update(candidate_cells=len(u),candidate_south=int(u.south.sum()),candidate_north=int(u.north.sum()));checkpoint()
    assert set(MEMBER_PINS)==set(overlap.KEYS) and all(len(h)==64 and all(c in "0123456789abcdef" for c in h) for h in MEMBER_PINS.values()), "invalid SHA256 manifest before network acquisition"
    paths=acquire_verified_members()
    for k,p in paths.items():
        assert report["members"][k]["sha256"]==MEMBER_PINS[k] and sha(p)==MEMBER_PINS[k],k
    report["all_five_member_hashes_reverified"]=True;checkpoint()
    manifest=save_windows(u,paths)
    ans=aggregate(u,manifest)
    u[["ALS_valid_area_fraction","H50","H95","PPR"]]=ans
    u["ALS_R50"]=np.where(u.H95.gt(5),u.H50/u.H95,np.nan)
    report["valid_any_als_cells"]=int(u.H95.notna().sum())
    # Unchanged original comparison code and thresholds.
    report["support"]={str(t):old.compare(u,t) for t in [.7,.5,.9]}
    p=OUT/"matched_ahn4_gvsm_cells.csv.gz"
    u[["cell_x","cell_y","lon","lat","south","north","worldcover_class_10_fraction","GVSM_area_mean_RH98_m","R50","ALS_valid_area_fraction","H50","H95","PPR","ALS_R50"]].to_csv(p,index=False,compression={"method":"gzip","mtime":0})
    report["output_sha256"]=sha(p);report["status"]="AHN4_STRUCTURE_PROXY_VALIDATION_COMPLETE"
    checkpoint()
if __name__=="__main__":
    try:main()
    except Exception as e:
        report.update(status="INCOMPLETE",error=type(e).__name__+": "+str(e)[:500]);checkpoint();raise
