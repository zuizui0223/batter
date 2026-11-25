"""Real input integration, no model fitting: Iberia failed the prespecified species coverage gate."""
import pathlib,json,csv,hashlib,collections,math
import numpy as np,rasterio
from pyproj import Transformer
OUT=pathlib.Path("gvsm_iberia_integrated");OUT.mkdir(exist_ok=True)
J=pathlib.Path("occ");G=pathlib.Path("gvsm");C=pathlib.Path("climate");L=pathlib.Path("landcover")
def sha(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
p=J/"occurrence_physical_trait_join.csv"
assert sha(p)=="aabef6ce174ec097be5afe159656f5dda49911d3b1dbd46368a90ae3df405ac7"
with p.open() as f: rows=list(csv.DictReader(f))
assert len(rows)==18779
gm=json.loads((G/"manifest.json").read_text())
cm=json.loads((C/"climate_manifest.json").read_text())
lm=json.loads((L/"manifest.json").read_text())
assert gm["status"]=="REAL_GVSM_CROPS_READY" and cm["status"]=="CLIMATE_CROPS_READY_ENCODING_QC_REQUIRED" and lm["status"]=="LANDCOVER_GRID_READY"
levels=[10,25,50,75,90,98]
clims=["bio1","bio4","bio5","bio6","bio12","bio15"]
paths=[G/f"RH{v}_Q1_iberia.tif" for v in levels]
for v,pth in zip(levels,paths):assert sha(pth)==gm["layers"][str(v)]["crop_sha256"]
for v in clims:assert sha(C/f"{v}_encoded_1km.tif")==cm["metrics"][v]["crop_sha256"]
lp=L/"worldcover_class_fractions_1km.tif";assert sha(lp)==lm["crop_sha256"]
# Unique species x provisional equal-area cells; preserve source count and unique provider count.
cells=collections.defaultdict(list)
for a in rows:cells[(a["species_key"],int(a["provisional_1km_x"]),int(a["provisional_1km_y"]))].append(a)
assert len(cells)==828
keys=list(cells)
coords=[((x+.5)*1000,(y+.5)*1000) for _,x,y in keys]
P=Transformer.from_crs(6933,4326,always_xy=True)
geo=list(P.itransform(coords))
def sample(path,xy,expected_crs):
    with rasterio.open(path) as src:
        assert src.crs.to_epsg()==expected_crs
        ix=[src.index(x,y) for x,y in xy]
        a=np.ma.array(list(src.sample(xy,masked=True)),dtype=float)
        data=a.filled(np.nan)
        if src.nodata is not None:data[data==src.nodata]=np.nan
        for i,(r,c) in enumerate(ix):
            if r<0 or c<0 or r>=src.height or c>=src.width:data[i,:]=np.nan
        return data,ix,(str(src.crs),list(src.transform),src.width,src.height),src.descriptions
# Sample each original GVSM native pixel, not pretend resampling increases information.
gv=[];ref=None;native=None
for path in paths:
    a,ix,grid,desc=sample(path,geo,4326)
    if ref is None:ref=grid;native=ix
    else:assert grid==ref
    gv.append(a[:,0])
gv=np.stack(gv,axis=1)
cl=[];base=None
for v in clims:
    a,ix,grid,desc=sample(C/f"{v}_encoded_1km.tif",coords,6933)
    if base is None:base=grid
    else:assert grid==base
    cl.append(a[:,0])
cl=np.stack(cl,axis=1)
lc,ix,grid,desc=sample(lp,coords,6933)
assert grid==base and desc[0]=="class_10_fraction"
finite_g=np.isfinite(gv).all(axis=1)
monotone=finite_g & (np.diff(gv,axis=1)>=0).all(axis=1)
finite_c=np.isfinite(cl).all(axis=1)
finite_l=np.isfinite(lc).all(axis=1)
h=gv[:,-1];forest=finite_l & (lc[:,0]>=.3)
joint=monotone & finite_c & finite_l
eligible=joint & forest & (h>5)
def val(x):return float(x) if np.isfinite(x) else None
out=[]
for i,key in enumerate(keys):
    k,x,y=key;a=cells[key];q=a[0]
    t={"species_key":k,"species":q["species"],"AR":float(q["AR"]),"WL_N_m2":float(q["WL_N_m2"]),"grid_x":x,"grid_y":y,"block_x":math.floor(x/200),"block_y":math.floor(y/200),"record_count":len(a),"dataset_count":len({v["dataset_key"] for v in a}),"gvsm_native_row":native[i][0],"gvsm_native_col":native[i][1],"longitude":geo[i][0],"latitude":geo[i][1]}
    t.update({f"RH{z}_m":val(gv[i,j]) for j,z in enumerate(levels)})
    t.update({z+"_encoded":val(cl[i,j]) for j,z in enumerate(clims)})
    t.update({name:val(lc[i,j]) for j,name in enumerate(desc)})
    t.update({"joint_environment":bool(joint[i]),"primary_forest_support":bool(eligible[i]),"R50":val(gv[i,2]/h[i]) if eligible[i] else None,"relative_RH90_RH10":val((gv[i,4]-gv[i,0])/h[i]) if eligible[i] else None,"relative_RH75_RH25":val((gv[i,3]-gv[i,1])/h[i]) if eligible[i] else None})
    out.append(t)
with (OUT/"iberia_species_cell_environment.csv").open("w") as f:
    w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
blocks=collections.defaultdict(lambda:collections.defaultdict(set))
for a in out:
    if a["primary_forest_support"]:blocks[a["species"]][(a["block_x"],a["block_y"])].add((a["grid_x"],a["grid_y"]))
coverage=[{"species":k,"cells":sum(map(len,v.values())),"blocks_ge5":sum(len(c)>=5 for c in v.values())} for k,v in blocks.items()]
coverage.sort(key=lambda x:-x["cells"])
report={"stage":"actual environmental join; no model fit","source_species_cell_rows":len(out),"gvsm_valid_rows":int(finite_g.sum()),"gvsm_order_valid_rows":int(monotone.sum()),"climate_valid_rows":int(finite_c.sum()),"landcover_valid_rows":int(finite_l.sum()),"joint_valid_rows":int(joint.sum()),"forest_profile_rows":int(eligible.sum()),"forest_profile_species":len(blocks),"forest_profile_native_species_pixels":len({(a["species_key"],a["gvsm_native_row"],a["gvsm_native_col"]) for a in out if a["primary_forest_support"]}),"species_passing_s1":sum(v["cells"]>=30 and v["blocks_ge5"]>=4 for v in coverage),"coverage":coverage,"result_sha256":sha(OUT/"iberia_species_cell_environment.csv"),"limitations":["No final effort/roost/terrain join, no DOI-pinned GBIF download.","Provisional equal-area grid centre sampled from native GVSM; not independent pixels or conservative aggregation.","Encoded climate values not interpreted as physical units.","GVSM RH not PAVD, forest structure prediction not true flight volume."]}
(OUT/"report.json").write_text(json.dumps(report,indent=2))
print("INTEGRATION_REPORT="+json.dumps(report))
