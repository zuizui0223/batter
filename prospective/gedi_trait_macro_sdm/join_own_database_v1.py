"""Build an authenticated Iberian species-cell/vertical-environment input database; no ecological fit."""
import collections,csv,gzip,hashlib,json,math,pathlib
import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import reproject,Resampling
from pyproj import Transformer
P=pathlib.Path("prior_occurrences"); C=pathlib.Path("prior_climate"); L=pathlib.Path("prior_landcover"); G=pathlib.Path("prior_gvsm")
OUT=pathlib.Path("own_database"); OUT.mkdir(exist_ok=True)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(p,expected):
    got=digest(p)
    if got!=expected:raise ValueError("source digest mismatch: "+p.name)
    return got
def load(p):return json.loads(p.read_text())
om=load(P/"coverage_report.json");cm=load(C/"climate_manifest.json");lm=load(L/"manifest.json");gm=load(G/"manifest.json")
pins={"occurrence_physical_trait_join.csv":"aabef6ce174ec097be5afe159656f5dda49911d3b1dbd46368a90ae3df405ac7","gbif_iberia_qc_search.jsonl.gz":"7ad294e5b6a92b38b434b9cdaa30fa23242e0ab96ece9c3ab6399986405b1d7d","physical_trait_crosswalk.csv":"43bb5284308a9fe732beda51886172cb87268e5d00620eb27956d5808dae809f"}
for name,sha in pins.items():
    assert om["files"][name]["sha256"]==sha
    check(P/name,sha)
assert om["complete_pagination"] and om["raw_retrieved"]==26018
levels=[10,25,50,75,90,98]
gpin={10:"90c58aa1e834d2564ce6d0ebecd3a22459585f90c2142c7c30c07102846f76a5",25:"83a98654a7d48bfe92a7e930b6a714217cfcf1c3beb3c71c9d65b82dea7ead00",50:"e450b51bd803e4cb5ff590ea34ac2abf08ebb7942540f453f5759887edfbd81a",75:"ad2bdedc090900dc9e93d43f730c92eadc0886dd5c72defd3c54732fdc90f4ca",90:"07a2a0bcde62d4d9e5731dd2ba6cca800d54e21700ee20cd400b3c303b53b53d",98:"8d46055ba839feeb0eefae21e69470812f49db3286a4358e11cfabc2f9348296"}
cpin={"bio1":"08ee9f1402d8be90a4f246eeb123e645152897351323fbe1442e399a68dbba2f","bio4":"03ca2fd97b4b1b8257e82e8fe7378c2b34f714e9c41019417e561209aafae974","bio5":"0b845f0d5dffae47b9c990542eea71ff0406e09bc9c593dd0648903ecdd1459c","bio6":"d428c1153dd7acb73353b460e85b3f3d2c87650bd52dc02e1a66b2721784884b","bio12":"edc256e5bbf65900df3af55795f0907f1ea360527aa8e95476b973ba2b44bd9d","bio15":"7b5660770f64f92427410de6039eaed972250dc6a0fe3db65ecd5876a7ed5a04"}
lp=L/"worldcover_class_fractions_1km.tif"; lpin="364ce79eb4b5c18f0c1117d88ad9a07b6186888190cfa20bdb3502f30e1411fe"
assert lm["crop_sha256"]==lpin;check(lp,lpin)
def grid_read(path,band=1):
    with rasterio.open(path) as src:
        a=src.read(band,masked=True).astype("float32").filled(np.nan)
        return a,(src.crs,src.transform,src.height,src.width)
with rasterio.open(lp) as src:
    dstgrid=(src.crs,src.transform,src.height,src.width)
    assert src.crs.to_epsg()==6933 and src.transform.a==1000 and src.transform.e==-1000
    assert src.transform.c%1000==0 and src.transform.f%1000==0
    assert src.count==12 and src.descriptions[0]=="class_10_fraction"
    lc=src.read(masked=True).astype("float32").filled(np.nan)
crs,transform,H,W=dstgrid
climates={}
for name,sha in cpin.items():
    assert cm["metrics"][name]["crop_sha256"]==sha
    p=C/(name+"_encoded_1km.tif");check(p,sha)
    a,g=grid_read(p);assert g==dstgrid
    info=cm["metrics"][name]
    climates[name]=(a*float(info["declared_scale"])+float(info["declared_offset"])).astype("float32")
profile=[];nativegrid=None
for v in levels:
    p=G/f"RH{v}_Q1_iberia.tif";assert gm["layers"][str(v)]["crop_sha256"]==gpin[v];check(p,gpin[v])
    a,g=grid_read(p)
    if nativegrid is None:nativegrid=g
    assert g==nativegrid
    profile.append(a)
profile=np.stack(profile)
native_valid=np.all(np.isfinite(profile),axis=0)
assert int(native_valid.sum())==785595 and not np.any(native_valid & np.any(np.diff(profile,axis=0)<0,axis=0))
# Native crop was limited to the Iberian bbox. Use an outer 2km buffer inward on the target
# grid for the coverage diagnosis, so partially cropped boundary pixels never masquerade
# as full support. All invalid native pixels are explicit zeros in the coverage mask.
def avg(a,nodata=None):
    o=np.full((H,W),np.nan,np.float32)
    reproject(a,o,src_transform=nativegrid[1],src_crs=nativegrid[0],src_nodata=nodata,dst_transform=transform,dst_crs=crs,dst_nodata=np.nan,resampling=Resampling.average)
    return o
coverage=avg(native_valid.astype("float32"))
rh=np.stack([avg(np.where(native_valid,a,np.nan).astype("float32"),np.nan) for a in profile])
# Exact bbox edge containment: transform each destination cell's four corners to geographic
# coordinates (EPSG:6933 cylindrical equal area).
xx=transform.c+np.arange(W+1)*1000; yy=transform.f-np.arange(H+1)*1000
inv=Transformer.from_crs(crs,4326,always_xy=True)
lon,_=inv.transform(xx,np.zeros_like(xx));_,lat=inv.transform(np.zeros_like(yy),yy)
edge=(lon[:-1]>=-10)&(lon[1:]<=4);edge2=(lat[:-1]<=44)&(lat[1:]>=35)
interior=edge2[:,None]&edge[None,:]
order=np.all(np.diff(rh,axis=0)>=-1e-5,axis=0)
gv=interior&np.isfinite(coverage)&(coverage>=.95)&np.all(np.isfinite(rh),axis=0)&order
cl=np.logical_and.reduce([np.isfinite(a) for a in climates.values()])
cover=np.all(np.isfinite(lc[:11]),axis=0)&(lc[11]>=.95)&(lc[11]<=1.05)&(np.abs(lc[:11].sum(axis=0)-1)<1e-4)
valid=gv&cl&cover
forest=valid&(lc[0]>=.3)&(rh[-1]>5)
# Write the gridded environmental table with provenance labels; no source-level locations.
rr,cc=np.where(valid)
env={"cell_x":((transform.c+cc*1000)//1000).astype(int),"cell_y":((transform.f-(rr+1)*1000)//1000).astype(int)}
for k,a in climates.items():env[k]=a[rr,cc]
for j,k in enumerate(levels):env[f"GVSM_mean_RH{k}_m"]=rh[j,rr,cc]
for j,k in enumerate([10,20,30,40,50,60,70,80,90,95,100]):env[f"LC_class_{k}_fraction"]=lc[j,rr,cc]
env["GVSM_valid_footprint_fraction"]=coverage[rr,cc];env["forest_analysis_support"]=forest[rr,cc]
E=pd.DataFrame(env);assert not E.duplicated(["cell_x","cell_y"]).any()
E.to_csv(OUT/"environment_1km.csv.gz",index=False,compression={"method":"gzip","mtime":0})
O=pd.read_csv(P/"occurrence_physical_trait_join.csv",dtype={"species_key":str})
assert len(O)==18779 and O.gbif_key.nunique()==18779
O["cell_x"]=np.floor(O.x6933/1000).astype(int);O["cell_y"]=np.floor(O.y6933/1000).astype(int)
assert O.cell_x.eq(O.provisional_1km_x).all() and O.cell_y.eq(O.provisional_1km_y).all()
O["year"]=pd.to_datetime(O.event_date,utc=True,format="mixed",errors="coerce").dt.year
# Keep source/year effort keys and counts in the artifact, no original record IDs or exact coords.
A=O.groupby(["species_key","species","AR","WL_N_m2","cell_x","cell_y","dataset_key","year","license"],dropna=False).size().rename("records").reset_index()
J=A.merge(E,on=["cell_x","cell_y"],how="inner",validate="many_to_one")
J.to_csv(OUT/"species_cell_environment_source_year.csv.gz",index=False,compression={"method":"gzip","mtime":0})
# Target-group background diagnostic from all eligible archived detections, including unmatched taxa.
proj=Transformer.from_crs(4326,6933,always_xy=True)
B=[]
with gzip.open(P/"gbif_iberia_qc_search.jsonl.gz","rt") as f:
    for line in f:
        a=json.loads(line);u=a.get("coordinateUncertaintyInMeters")
        if not(a.get("species") and str(a.get("occurrenceStatus","")).upper() in {"PRESENT","DETECTED"} and isinstance(u,(int,float)) and 0<u<=500 and a.get("basisOfRecord") in {"HUMAN_OBSERVATION","MACHINE_OBSERVATION","OBSERVATION"}):continue
        x,y=proj.transform(a["decimalLongitude"],a["decimalLatitude"])
        if not math.isfinite(x) or not math.isfinite(y):continue
        B.append((math.floor(x/1000),math.floor(y/1000),str(a.get("speciesKey")),a.get("datasetKey"),str(a.get("eventDate") or "")[:4],a.get("license")))
B=pd.DataFrame(B,columns=["cell_x","cell_y","species_key","dataset_key","year","license"])
assert len(B)==22060
B=B.groupby(list(B.columns),dropna=False).size().rename("records").reset_index()
B=B.merge(E[["cell_x","cell_y","forest_analysis_support"]],on=["cell_x","cell_y"],validate="many_to_one")
B.to_csv(OUT/"target_group_cell_source_year.csv.gz",index=False,compression={"method":"gzip","mtime":0})
def support(df):
    ans=[]
    for (k,s),v in df.groupby(["species_key","species"]):
        cells=v[["cell_x","cell_y"]].drop_duplicates().copy()
        blocks=cells.assign(bx=cells.cell_x//200,by=cells.cell_y//200).groupby(["bx","by"]).size()
        n=len(cells);b=int((blocks>=5).sum())
        ans.append({"species_key":k,"species":s,"cells":n,"blocks_5_cells":b,"provisional_coverage_pass":n>=30 and b>=4})
    return sorted(ans,key=lambda x:(-x["cells"],x["species"]))
allcov=support(J);fcov=support(J[J.forest_analysis_support])
report={"stage":"joined original data; no ecological model; GVSM proxy not PAVD","source_files_sha256":{**pins,**cpin,**{f"RH{k}":v for k,v in gpin.items()},"worldcover":lpin},"shape":[H,W],"climate_valid_cells":int(cl.sum()),"landcover_valid_cells":int(cover.sum()),"gvsm_valid_cells":int(gv.sum()),"gvsm_order_errors_on_supported":int((interior&(coverage>=.95)&np.all(np.isfinite(rh),axis=0)&~order).sum()),"joint_cells":int(valid.sum()),"joint_forest_cells":int(forest.sum()),"input_occurrence_records":len(O),"input_species":O.species_key.nunique(),"joined_records":int(J.records.sum()),"joined_species":int(J.species_key.nunique()),"joined_species_cells":int(J[["species_key","cell_x","cell_y"]].drop_duplicates().shape[0]),"forest_records":int(J.loc[J.forest_analysis_support,"records"].sum()),"forest_species":int(J.loc[J.forest_analysis_support,"species_key"].nunique()),"forest_species_cells":int(J.loc[J.forest_analysis_support,["species_key","cell_x","cell_y"]].drop_duplicates().shape[0]),"target_group_joined_records":int(B.records.sum()),"target_group_cells":int(B[["cell_x","cell_y"]].drop_duplicates().shape[0]),"all_support":allcov,"forest_support":fcov,"provisional_all_species_gate":sum(a["provisional_coverage_pass"] for a in allcov),"provisional_forest_species_gate":sum(a["provisional_coverage_pass"] for a in fcov),"original_PAVD_admission":False,"limitations":["Live GBIF snapshot; no final DOI or source-level effort/roost/captive audit.","GVSM mean height quantiles, not vegetation density or 3D use.","Target group recorded support is not absence or a completed observation-effort model.","No terrain layer or model fit."]}
report["outputs"]={p.name:{"bytes":p.stat().st_size,"sha256":digest(p)} for p in OUT.glob("*.gz")}
(OUT/"own_database_report.json").write_text(json.dumps(report,indent=2)+"\n")
print("OWN_DATABASE_REPORT="+json.dumps(report),flush=True)
