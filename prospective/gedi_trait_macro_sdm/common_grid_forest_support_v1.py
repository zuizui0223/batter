"""Common-grid area-weighted climate/profile and source support, no model fit."""
import hashlib, itertools, json, math, pathlib
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import Window, from_bounds, transform
from pyproj import Transformer
P=pathlib.Path("census"); E=pathlib.Path("cell_environment"); T=pathlib.Path("traits")
OUT=pathlib.Path("common_forest_support");OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
paths={"census":P/"complete_species_cell_source_year.csv.gz","environment":E/"species_cell_environment.csv","traits":T/"physical_trait_crosswalk.csv"}
pins={"census":"a3bac38f1961240a235e351207b1497712585fc9d2f8506ab0209d28019354b9","environment":"89b63e7229447377064d189c8532b232640192cf343d43cb24260dcc3e97c5e5","traits":"43bb5284308a9fe732beda51886172cb87268e5d00620eb27956d5808dae809f"}
for k,p in paths.items():assert sha(p)==pins[k],k
a=pd.read_csv(paths["census"],dtype={"species_key":str,"dataset_key":str,"year":str,"license":str},keep_default_na=False)
e=pd.read_csv(paths["environment"],dtype={"species_key":str})
t=pd.read_csv(paths["traits"],dtype={"species_key":str},keep_default_na=False)
t["AR"]=pd.to_numeric(t.AR,errors="coerce");t["WL_N_m2"]=pd.to_numeric(t.WL_N_m2,errors="coerce")
t=t[t.species_key.ne("")&t.AR.gt(0)].copy();t=t[~t.species_key.duplicated(keep=False)]
assert len(t)==28 and len(e)==4854 and a.records.sum()==20784 and len(a[["species_key","cell_x","cell_y"]].drop_duplicates())==4854
K=["cell_x","cell_y"];S=["species_key",*K]
assert not e.duplicated(S).any()
assert a.groupby(S).records.sum().sort_index().equals(e.set_index(S).records.sort_index())
cover=[f"worldcover_class_{v}_fraction" for v in [10,20,30,40,50,60,70,80,90,95,100]]
# Reuse exact WorldCover fractions; check that every source species receives the same cell data.
cols=K+cover+["valid_area_m2","native_rh_row","native_rh_col","forest_profile_support"]
u=e[cols].drop_duplicates()
assert len(u)==2982 and not u.duplicated(K).any()
u=u.sort_values(K).reset_index(drop=True)
cells=list(u[K].itertuples(index=False,name=None));Pj=Transformer.from_crs(4326,6933,always_xy=True);Ij=Transformer.from_crs(6933,4326,always_xy=True)
xmin=min(x for x,y in cells)*1000;xmax=(max(x for x,y in cells)+1)*1000
ymin=min(y for x,y in cells)*1000;ymax=(max(y for x,y in cells)+1)*1000
west,south=Ij.transform(xmin,ymin);east,north=Ij.transform(xmax,ymax)
report={"stage":"area-weighted common-grid source support, no model","input_sha256":pins,"cells":len(cells),"source_records":int(a.records.sum()),"source_species_cells":len(e),"source_domain":"[-12,35,30,51.6]; no country filter; already acquired archive only","source_windows":{}}
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
g,ga,go=read_stack(gv,"RH");c,ca,co=read_stack(chelsa,"climate")
for j,z in enumerate(levels):u[f"GVSM_area_mean_RH{z}_m"]=g[:,j]
for j,k in enumerate(clim):u[k]=c[:,j]
u["GVSM_joint_valid_area_fraction"]=ga;u["CHELSA_joint_valid_area_fraction"]=ca;u["GVSM_native_overlap_pixels"]=go;u["CHELSA_native_overlap_pixels"]=co
ordered=np.isfinite(g).all(axis=1)&(np.diff(g,axis=1)>=-1e-8).all(axis=1)
valid_cover=np.isfinite(u[cover]).all(axis=1)&u.valid_area_m2.between(950000,1050000)&(u[cover].sum(axis=1)-1).abs().lt(1e-4)
valid_env=ordered&np.isfinite(c).all(axis=1)&valid_cover
forest=valid_env&u[cover[0]].ge(.3)&(g[:,-1]>5)
u=u.rename(columns={"forest_profile_support":"prior_nearest_forest_support"});u["common_environment_support"]=valid_env;u["forest_profile_support"]=forest
u["R50"]=np.where(forest,g[:,2]/np.where(g[:,-1]>5,g[:,-1],np.nan),np.nan)
# Keep source-year and license provenance; no original precise points or inference of absence.
j=a.merge(u,on=K,how="left",validate="many_to_one").merge(t[["species_key","source_name","AR","WL_N_m2"]],on="species_key",how="left",validate="many_to_one")
assert len(j)==len(a) and j.AR.notna().all() and j.forest_profile_support.notna().all()
j["bx"]=j.cell_x//200;j["by"]=j.cell_y//200
f=j[j.forest_profile_support].copy()
keys=["dataset_key","year","bx","by"]
def summary(df):
    v=df[S+["bx","by"]].drop_duplicates()
    out=[]
    for k,x in v.groupby("species_key"):
        b=x.groupby(["bx","by"]).size();n=len(x);nb=int(b.ge(5).sum())
        out.append({"species_key":k,"species":str(t.loc[t.species_key.eq(k),"source_name"].iloc[0]),"cells":n,"blocks_ge5":nb,"coverage_pass":n>=30 and nb>=4})
    return sorted(out,key=lambda x:(-x["cells"],x["species"]))
sp=summary(f);admitted={x["species_key"] for x in sp if x["coverage_pass"]}
q=f[f.species_key.isin(admitted)&f.dataset_key.ne("")&f.year.str.fullmatch(r"20[0-9]{2}")].copy()
def support(df):
    ss=df.groupby(keys).species_key.nunique();sc=df.groupby(["dataset_key","year",*K]).species_key.nunique()
    return {"strata":int(len(ss)),"multi_species_strata":int(ss.ge(2).sum()),"multi_species_source_year_cells":int(sc.ge(2).sum()),"source_year_cells":int(len(sc))}
def sets(df,ks):
    return {k:set(map(tuple,v[ks].drop_duplicates().itertuples(index=False,name=None))) for k,v in df.groupby("species_key")}
B=sets(q,keys);C=sets(q,["dataset_key","year",*K]);pairs=[]
for x,y in itertools.combinations(sorted(admitted),2):
    common=B.get(x,set())&B.get(y,set())
    pairs.append({"species_a":x,"species_b":y,"shared_source_year_blocks":len(common),"distinct_shared_blocks":len({(s[2],s[3]) for s in common}),"shared_source_year_cells":len(C.get(x,set())&C.get(y,set()))})
pd.DataFrame(pairs).to_csv(OUT/"forest_pair_support.csv",index=False)
u.to_csv(OUT/"cell_environment_common_grid.csv.gz",index=False,compression={"method":"gzip","mtime":0})
j.to_csv(OUT/"species_cell_source_year_environment.csv.gz",index=False,compression={"method":"gzip","mtime":0})
report.update({"joint_RH_cells":int(ordered.sum()),"joint_climate_cells":int(np.isfinite(c).all(axis=1).sum()),"common_environment_cells":int(valid_env.sum()),"forest_cells":int(forest.sum()),"forest_records":int(f.records.sum()),"forest_species_cells":len(f[S].drop_duplicates()),"forest_species":int(f.species_key.nunique()),"species_support":sp,"geographic_pass_species":len(admitted),"nearest_to_area_forest_changes":{"lost":int((u.prior_nearest_forest_support&~forest).sum()),"gained":int((~u.prior_nearest_forest_support&forest).sum())},"forest_source_support_all":support(f),"forest_source_support_geographic_pass":support(q),"pairs":len(pairs),"pairs_ge1_block":sum(x["distinct_shared_blocks"]>=1 for x in pairs),"pairs_ge4_blocks":sum(x["distinct_shared_blocks"]>=4 for x in pairs),"pairs_shared_cell":sum(x["shared_source_year_cells"]>0 for x in pairs),"unique_prior_native_RH_pixels":len(u[["native_rh_row","native_rh_col"]].drop_duplicates()),"original_S1_admission":False,"limits":["GVSM predicted mean return-height quantiles, not PAVD or flight volume.","Area-weighted projected source-pixel overlap, shared native valid area >=95%; no actual vegetation-density measurements.","No terrain/roost/effort model, DOI-pinned download or independent validation. Matched source-year cells are not proven common effort or absences.","26 species narrow rectangle only. No ecological model or trait response fit."]})
report["outputs"]={p.name:{"bytes":p.stat().st_size,"sha256":sha(p)} for p in OUT.iterdir() if p.is_file()}
(OUT/"report.json").write_text(json.dumps(report,indent=2)+"\n")
print("COMMON_FOREST_REPORT="+json.dumps(report),flush=True)
