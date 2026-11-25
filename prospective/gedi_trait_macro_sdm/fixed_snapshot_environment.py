"""Fixed August GBIF snapshot, all-bat target group; area-weighted environmental support.
Reuse the independently verified WorldCover cell archive; never mix live occurrence rows.
No SDM fit. GVSM return-height quantiles are not PAVD or flight probability.
Raster aggregation routines from common_grid_forest_support_v1.py @7c2b046 and
europe_cell_environment_gate.py @ef20c11 (unchanged calculation, wider input support).
"""
import collections,csv,gzip,hashlib,json,math,pathlib,tempfile,sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np,pandas as pd,requests,rasterio
from rasterio.windows import Window,from_bounds,transform
from pyproj import Transformer
OUT=pathlib.Path("snapshot_environment");OUT.mkdir(exist_ok=True)
P=Pj=Transformer.from_crs(4326,6933,always_xy=True)
I=Ij=Transformer.from_crs(6933,4326,always_xy=True)
def sha(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
p=pathlib.Path("fixed/all_bat_species_cell_source_year.csv.gz")
q=pathlib.Path("prior_common/cell_environment_common_grid.csv.gz")
t=pathlib.Path("traits/physical_trait_crosswalk.csv")
pins={"snapshot_cells":"f0124127cd55b7abe4ee0deab935895e150918fc0b0c6e33942ba1591e89ef53","prior_worldcover":"915cd8ffd2b63fb768c7cd2eba8e9faa5b40ab8ffd92efeb5dc8ea42dafdccc3","physical_traits":"43bb5284308a9fe732beda51886172cb87268e5d00620eb27956d5808dae809f"}
assert sha(p)==pins["snapshot_cells"] and sha(q)==pins["prior_worldcover"] and sha(t)==pins["physical_traits"]
a=pd.read_csv(p,dtype={"species":str,"snapshot_species_key":str,"dataset_key":str,"year":str,"license":str},keep_default_na=False)
K=["cell_x","cell_y"];S=["snapshot_species_key",*K]
assert a.records.sum()==219960 and len(a[S].drop_duplicates())==23489
u=a[K].drop_duplicates().sort_values(K).reset_index(drop=True)
assert len(u)==11006
cells=list(u[K].itertuples(index=False,name=None))
xmin=min(x for x,y in cells)*1000;xmax=(max(x for x,y in cells)+1)*1000
ymin=min(y for x,y in cells)*1000;ymax=(max(y for x,y in cells)+1)*1000
west,south=I.transform(xmin,ymin);east,north=I.transform(xmax,ymax)
report={"stage":"fixed-source environment support, no ecological fit","snapshot_doi":"10.15468/dl.8yrbe7","input_sha256":pins,"cells":len(cells),"source_records":int(a.records.sum()),"source_species_cells":len(a[S].drop_duplicates()),"source_windows":{}}
def checkpoint():
    (OUT/"report.json").write_text(json.dumps(report,indent=2))
    print("SNAPSHOT_ENV_REPORT="+json.dumps({k:v for k,v in report.items() if k not in {"source_windows","worldcover_tiles"}}),flush=True)
levels=[10,25,50,75,90,98];clim=["bio1","bio4","bio5","bio6","bio12","bio15"]
def read_stack(specs,group):
    arrays=[];grid=None
    for label,url,scale,offset,expected_nodata,declared in specs:
        with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",GDAL_HTTP_TIMEOUT="75",GDAL_HTTP_MAX_RETRY="2",CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif"):
            with rasterio.open(url) as src:
                assert src.crs.to_epsg()==4326 and src.count==1 and src.transform.b==0 and src.transform.d==0 and src.transform.a>0 and src.transform.e<0
                if expected_nodata is not None:assert src.nodata==expected_nodata
                if declared:assert math.isclose(src.scales[0],scale,abs_tol=1e-8) and math.isclose(src.offsets[0],offset,abs_tol=1e-6)
                else:assert math.isclose(src.transform.a,.01,abs_tol=1e-7)
                w=from_bounds(west,south,east,north,transform=src.transform)
                c0=max(0,math.floor(w.col_off)-1);c1=min(src.width,math.ceil(w.col_off+w.width)+1)
                r0=max(0,math.floor(w.row_off)-1);r1=min(src.height,math.ceil(w.row_off+w.height)+1)
                w=Window(c0,r0,c1-c0,r1-r0);tr=transform(w,src.transform);g=(tr,int(w.height),int(w.width))
                if grid is None:grid=g
                else:assert g==grid,label
                raw=src.read(1,window=w,masked=True)
                valid=~np.ma.getmaskarray(raw)&np.isfinite(raw.data)
                val=np.where(valid,raw.data.astype("float32")*scale+offset,np.nan).astype("float32")
                arrays.append(val)
                report["source_windows"][label]={"url":url,"shape":[int(w.height),int(w.width)],"transform":list(tr),"window":[c0,r0,c1-c0,r1-r0],"source_shape":[src.height,src.width],"scale":scale,"offset":offset,"source_nodata":src.nodata,"native_valid":int(valid.sum()),"encoded_bytes_sha256":hashlib.sha256(np.ascontiguousarray(raw.data).tobytes()).hexdigest(),"valid_mask_sha256":hashlib.sha256(np.ascontiguousarray(valid).tobytes()).hexdigest(),"converted_array_sha256":hashlib.sha256(val.tobytes()).hexdigest()}
                print("WINDOW_READY",label,g[1:],flush=True)
    stack=np.stack(arrays,axis=0);del arrays
    tr,h,w=grid
    xe=tr.c+np.arange(w+1)*tr.a;ye=tr.f+np.arange(h+1)*tr.e
    xx,_=Pj.transform(xe,np.zeros_like(xe));_,yy=Pj.transform(np.zeros_like(ye),ye)
    assert np.all(np.diff(xx)>0) and np.all(np.diff(yy)<0)
    valid=np.isfinite(stack).all(axis=0)
    if group=="RH":report["native_profile_order_error_pixels"]=int((valid&np.any(np.diff(stack,axis=0)<0,axis=0)).sum())
    result=np.full((len(cells),len(specs)),np.nan,dtype=float);area=np.zeros(len(cells));overlap=np.zeros(len(cells),int)
    yn=-yy
    for i,(cx,cy) in enumerate(cells):
        x0,x1=cx*1000,(cx+1)*1000;y0,y1=cy*1000,(cy+1)*1000
        j0=max(0,int(np.searchsorted(xx,x0,side="right")-1));j1=min(w,int(np.searchsorted(xx,x1,side="left")))
        i0=max(0,int(np.searchsorted(yn,-y1,side="right")-1));i1=min(h,int(np.searchsorted(yn,-y0,side="left")))
        if i0>=i1 or j0>=j1:continue
        wx=np.maximum(0,np.minimum(x1,xx[j0+1:j1+1])-np.maximum(x0,xx[j0:j1]))
        wy=np.maximum(0,np.minimum(y1,yy[i0:i1])-np.maximum(y0,yy[i0+1:i1+1]))
        weights=wy[:,None]*wx[None,:]
        mask=valid[i0:i1,j0:j1]&(weights>0)
        W=weights[mask];area[i]=W.sum()/1e6;overlap[i]=int(mask.sum())
        if .95<=area[i]<=1.000001:
            result[i]=np.sum(stack[:,i0:i1,j0:j1][:,mask].astype(float)*W[None,:],axis=1)/W.sum()
    return result,area,overlap
gv=[(f"RH{z}","https://data.source.coop/geoai-ucph/gvsm/mosaics/2020/"+f"RH{z}_Q1.tif",.1,0,32767,False) for z in levels]
chelsa=[(k,f"https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_{k}_1981-2010_V.2.1.tif",.1,-273.15 if k in {"bio1","bio5","bio6"} else 0,None,True) for k in clim]
classes=[10,20,30,40,50,60,70,80,90,95,100];cover=[f"worldcover_class_{v}_fraction" for v in classes]
# Old archive contributes only environmental values on exactly identical grid cells.
prior=pd.read_csv(q)
assert len(prior)==2982 and not prior.duplicated(K).any()
u=u.merge(prior[K+cover+["valid_area_m2"]],on=K,how="left",validate="one_to_one")
reuse=np.isfinite(u[cover]).all(axis=1)&u.valid_area_m2.between(950000,1050000)&(u[cover].sum(axis=1)-1).abs().lt(1e-4)
area=np.zeros((len(cells),len(classes)),dtype=float)
area[reuse]=u.loc[reuse,cover].to_numpy()*u.loc[reuse,"valid_area_m2"].to_numpy()[:,None]
report["reused_verified_worldcover_cells"]=int(reuse.sum())
u=u.drop(columns=cover+["valid_area_m2"])
tile_cells=collections.defaultdict(list);bbox={}
for i,(x,y) in enumerate(cells):
    if reuse.iloc[i]:continue
    l,b=I.transform(x*1000,y*1000);r,t=I.transform((x+1)*1000,(y+1)*1000);bbox[i]=(l,b,r,t)
    for lat in range(math.floor(b/3)*3,math.ceil(t/3)*3,3):
        for lon in range(math.floor(l/3)*3,math.ceil(r/3)*3,3):tile_cells[(lat,lon)].append(i)
if len(tile_cells)>250:raise ValueError("tile budget exceeded")
report["new_worldcover_tiles"]=len(tile_cells)
def tile(task):
    (lat,lon),indices=task
    token=f"N{lat:02d}"+("E" if lon>=0 else "W")+f"{abs(lon):03d}"
    name=f"ESA_WorldCover_10m_2021_v200_{token}_Map.tif"
    url="https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/"+name
    h=requests.head(url,timeout=30,allow_redirects=True)
    if h.status_code==404:return {"tile":token,"status":"not_distributed","cells":len(indices)},[]
    h.raise_for_status()
    with tempfile.TemporaryDirectory() as tmp:
        p=pathlib.Path(tmp)/name;d=hashlib.sha256();size=0
        with requests.get(url,stream=True,timeout=(30,90)) as resp:
            resp.raise_for_status()
            with p.open("wb") as f:
                for block in resp.iter_content(1024*1024):
                    size+=len(block)
                    if size>512*1024*1024:raise ValueError("tile acquisition budget exceeded")
                    d.update(block);f.write(block)
            if resp.headers.get("Content-Length") and size!=int(resp.headers["Content-Length"]):raise ValueError("partial source tile")
        partial=[]
        with rasterio.open(p) as src:
            assert src.crs.to_epsg()==4326 and src.count==1 and src.transform.b==0 and src.transform.d==0
            for i in indices:
                l,b,r,t=bbox[i];l=max(l,src.bounds.left);b=max(b,src.bounds.bottom);r=min(r,src.bounds.right);t=min(t,src.bounds.top)
                if l>=r or b>=t:continue
                w=from_bounds(l,b,r,t,transform=src.transform)
                c0=max(0,math.floor(w.col_off)-1);c1=min(src.width,math.ceil(w.col_off+w.width)+1)
                r0=max(0,math.floor(w.row_off)-1);r1=min(src.height,math.ceil(w.row_off+w.height)+1)
                if c0>=c1 or r0>=r1:continue
                cols=np.arange(c0,c1);rs=np.arange(r0,r1)
                x0,_=P.transform(src.transform.c+cols*src.transform.a,np.zeros(len(cols)))
                x1,_=P.transform(src.transform.c+(cols+1)*src.transform.a,np.zeros(len(cols)))
                _,y0=P.transform(np.zeros(len(rs)),src.transform.f+rs*src.transform.e)
                _,y1=P.transform(np.zeros(len(rs)),src.transform.f+(rs+1)*src.transform.e)
                x,y=cells[i]
                gx=(np.floor((x0+x1)*.5/1000)==x);gy=(np.floor((y0+y1)*.5/1000)==y)
                if not gx.any() or not gy.any():continue
                a=src.read(1,window=Window(c0,r0,c1-c0,r1-r0),masked=True)
                v=a.data[gy,:][:,gx];ok=~np.ma.getmaskarray(a)[gy,:][:,gx]
                weights=(y0-y1)[gy,None]*(x1-x0)[None,gx]
                areas=[float(weights[ok&(v==c)].sum()) for c in classes]
                partial.append((i,areas))
        return {"tile":token,"status":"read","cells":len(indices),"bytes":size,"sha256":d.hexdigest()},partial
def guarded(task):
    try:return tile(task)
    except Exception as e:return {"tile":str(task[0]),"status":"failed","cells":len(task[1]),"error":type(e).__name__+": "+str(e)[:200]},[]
report["worldcover_tiles"]=[]
try:
    # Complete raster profile and climate first; common valid area as in original protocol.
    g,ga,go=read_stack(gv,"RH");c,ca,co=read_stack(chelsa,"climate")
    for j,z in enumerate(levels):u[f"GVSM_area_mean_RH{z}_m"]=g[:,j]
    for j,k in enumerate(clim):u[k]=c[:,j]
    u["GVSM_joint_valid_area_fraction"]=ga;u["CHELSA_joint_valid_area_fraction"]=ca;u["GVSM_native_overlap_pixels"]=go
    ordered=np.isfinite(g).all(axis=1)&(np.diff(g,axis=1)>=-1e-8).all(axis=1)
    report["joint_RH_cells"]=int(ordered.sum());report["joint_climate_cells"]=int(np.isfinite(c).all(axis=1).sum())
    report["status"]="RH_CLIMATE_READY";checkpoint()
    with ThreadPoolExecutor(max_workers=3) as ex:
        for meta,parts in ex.map(guarded,sorted(tile_cells.items())):
            report["worldcover_tiles"].append(meta)
            for i,v in parts:area[i]+=v
            print("WORLD_COVER_TILE="+json.dumps(meta),flush=True)
    total=area.sum(axis=1);lcvalid=(total>=950000)&(total<=1050000)
    frac=np.full_like(area,np.nan);frac[lcvalid]=area[lcvalid]/total[lcvalid,None]
    for j,k in enumerate(cover):u[k]=frac[:,j]
    u["valid_area_m2"]=total
    valid=ordered&np.isfinite(c).all(axis=1)&lcvalid
    forest=valid&(frac[:,0]>=.3)&(g[:,-1]>5)
    # Native training-latitude support: whole equal-area cell lies south of 51.6.
    _,lat_hi=I.transform((u.cell_x.to_numpy()+1)*1000,(u.cell_y.to_numpy()+1)*1000)
    _,lat_lo=I.transform(u.cell_x.to_numpy()*1000,u.cell_y.to_numpy()*1000)
    u["training_latitude_support"]=lat_hi<=51.6
    u["north_extrapolation"]=lat_lo>51.6
    u["latitude_boundary_cell"]=~(u.training_latitude_support|u.north_extrapolation)
    u["common_environment_support"]=valid;u["forest_profile_support"]=forest
    u["R50"]=np.where(forest,g[:,2]/np.where(g[:,-1]>5,g[:,-1],np.nan),np.nan)
    u["relative_RH90_RH10"]=np.where(forest,(g[:,4]-g[:,0])/np.where(g[:,-1]>5,g[:,-1],np.nan),np.nan)
    u["relative_RH75_RH25"]=np.where(forest,(g[:,3]-g[:,1])/np.where(g[:,-1]>5,g[:,-1],np.nan),np.nan)
    # Keep ALL Chiroptera as recorded target-group support, and trait-match exact names only.
    tr=pd.read_csv(pathlib.Path("traits/physical_trait_crosswalk.csv"),dtype=str,keep_default_na=False)
    tr["AR"]=pd.to_numeric(tr.AR,errors="coerce");tr["WL_N_m2"]=pd.to_numeric(tr.WL_N_m2,errors="coerce")
    tr=tr[tr.AR.gt(0)&tr.species_key.ne("")].copy()
    norm=lambda v:" ".join(str(v).split()).casefold()
    tr["name_norm"]=tr.source_name.map(norm);tr=tr[~tr.name_norm.duplicated(keep=False)]
    assert len(tr)==28
    a["name_norm"]=a.species.map(norm)
    j=a.merge(u,on=K,how="left",validate="many_to_one").merge(tr[["name_norm","source_name","AR","WL_N_m2","species_key"]].rename(columns={"species_key":"legacy_gbif_species_key"}),on="name_norm",how="left",validate="many_to_one")
    assert len(j)==len(a) and j.records.sum()==219960 and j.common_environment_support.notna().all()
    keys_per_name=j.groupby("name_norm").snapshot_species_key.nunique()
    ambiguous=set(keys_per_name[keys_per_name!=1].index)
    j["provisional_trait_match"]=j.AR.notna()&~j.name_norm.isin(ambiguous)
    j["bx"]=j.cell_x//200;j["by"]=j.cell_y//200
    def coverage(mask):
        z=j[j.provisional_trait_match&mask][["source_name",*S,"bx","by"]].drop_duplicates()
        out=[]
        for n,v in z.groupby("source_name"):
            b=v.groupby(["bx","by"]).size();ncell=len(v);nb=int(b.ge(5).sum())
            out.append({"species":n,"cells":ncell,"blocks_ge5":nb,"pass":ncell>=30 and nb>=4})
        return sorted(out,key=lambda x:-x["cells"])
    cov_all=coverage(j.forest_profile_support)
    cov_south=coverage(j.forest_profile_support&j.training_latitude_support)
    cov_north=coverage(j.forest_profile_support&j.north_extrapolation)
    report.update({"status":"FIXED_SNAPSHOT_ENVIRONMENT_READY" if not any(x["status"]=="failed" for x in report["worldcover_tiles"]) else "PARTIAL_WORLD_COVER_SUPPORT","worldcover_failed_tiles":sum(x["status"]=="failed" for x in report["worldcover_tiles"]),"worldcover_valid_cells":int(lcvalid.sum()),"common_environment_cells":int(valid.sum()),"forest_cells":int(forest.sum()),"forest_target_group_records":int(j.loc[j.forest_profile_support,"records"].sum()),"forest_target_group_species_cells":len(j.loc[j.forest_profile_support,S].drop_duplicates()),"physical_trait_species_support_all":cov_all,"physical_trait_species_support_training_latitude":cov_south,"physical_trait_species_support_north":cov_north,"forest_gate_species_all":sum(x["pass"] for x in cov_all),"forest_gate_species_training_latitude":sum(x["pass"] for x in cov_south),"forest_gate_species_north":sum(x["pass"] for x in cov_north),"admitted_for_model":False,"limitations":["Fixed August snapshot; no mixing November occurrence records. Exact-name taxonomic bridge remains provisional.","Area-weighted GVSM RH quantiles, not physical air volume or measured PAVD. Northern extrapolation kept separate.","No terrain, roost/captive/season or final effort audit; target-group detections not absences. No ecological fit or occupancy estimate."]})
    u.to_csv(OUT/"cell_environment_common_grid.csv.gz",index=False,compression={"method":"gzip","mtime":0})
    j.to_csv(OUT/"all_bat_species_cell_source_year_environment.csv.gz",index=False,compression={"method":"gzip","mtime":0})
    report["output_sha256"]={v.name:sha(v) for v in OUT.glob("*.csv.gz")}
    checkpoint()
except Exception as e:
    report.update(status="INCOMPLETE",error=type(e).__name__+": "+str(e)[:300]);checkpoint();raise
