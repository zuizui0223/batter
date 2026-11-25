"""Outcome-blind environment support audit on actual already acquired European cells.
Not a fitted model, not absolute habitat use. WorldCover uses equal-area pixel-centre assignment.
"""
import collections,csv,gzip,hashlib,json,math,pathlib,tempfile,os,sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np,requests,rasterio
from rasterio.windows import from_bounds,Window
from pyproj import Transformer
P=Transformer.from_crs(4326,6933,always_xy=True)
I=Transformer.from_crs(6933,4326,always_xy=True)
OUT=pathlib.Path("europe_cell_environment");OUT.mkdir(exist_ok=True)
SRC=pathlib.Path("europe/complete_species_cell_source_year.csv.gz")
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=="a3bac38f1961240a235e351207b1497712585fc9d2f8506ab0209d28019354b9"
with gzip.open(SRC,"rt",encoding="utf8") as f: rows=list(csv.DictReader(f))
species_cells=collections.defaultdict(int);cell_species=collections.defaultdict(set)
for a in rows:
    c=(int(a["cell_x"]),int(a["cell_y"]))
    species_cells[(a["species_key"],*c)]+=int(a["records"])
    cell_species[c].add(a["species_key"])
assert len(species_cells)==4854
cells=sorted(cell_species)
geo=[I.transform((x+.5)*1000,(y+.5)*1000) for x,y in cells]
clim={"bio1","bio4","bio5","bio6","bio12","bio15"}
levels=[10,25,50,75,90,98]
report={"stage":"environment support audit of 26 completely retrieved species, southern-central rectangle; no fitted model","input_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),"species_cells":len(species_cells),"unique_cells":len(cells),"raw_source_records":sum(species_cells.values()),"source_rect":"[-12,35,30,51.6]; no country filter in archived occurrence query","sources":{},"errors":{}}
def save_report():
    (OUT/"report.json").write_text(json.dumps(report,indent=2))
    print("EUROPE_CELL_ENVIRONMENT="+json.dumps(report),flush=True)
def sample_layer(url,label,scale=1.0,expected_nodata=None):
    """One read per bounding tile window, rather than a remote request for each point."""
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",GDAL_HTTP_TIMEOUT="60",GDAL_HTTP_MAX_RETRY="2",CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif"):
        with rasterio.open(url) as src:
            assert src.count==1 and src.crs.to_epsg()==4326
            if expected_nodata is not None:assert src.nodata==expected_nodata
            ix=[src.index(x,y) for x,y in geo]
            blockh,blockw=src.block_shapes[0]
            groups=collections.defaultdict(list)
            for i,(r,c) in enumerate(ix):
                if 0<=r<src.height and 0<=c<src.width:groups[(r//blockh,c//blockw)].append((i,r,c))
            result=np.full(len(cells),np.nan,dtype=np.float32)
            # Merge requested raster blocks into a single bounding window per 2x2 block group.
            bins=collections.defaultdict(list)
            for (r,c),vv in groups.items():bins[(r//2,c//2)].extend(vv)
            for vv in bins.values():
                r0=(min(r for _,r,_ in vv)//blockh)*blockh;c0=(min(c for _,_,c in vv)//blockw)*blockw
                r1=min(src.height,(max(r for _,r,_ in vv)//blockh+1)*blockh);c1=min(src.width,(max(c for _,_,c in vv)//blockw+1)*blockw)
                a=src.read(1,window=Window(c0,r0,c1-c0,r1-r0),masked=True)
                for i,r,c in vv:
                    v=a[r-r0,c-c0]
                    if not np.ma.is_masked(v) and np.isfinite(v):result[i]=float(v)*scale
            report["sources"][label]={"url":url,"source_grid":[str(src.crs),list(src.transform),src.height,src.width],"nodata":src.nodata,"declared_scale":src.scales[0],"declared_offset":src.offsets[0],"source_unit":src.units[0],"valid_cells":int(np.isfinite(result).sum()),"sample_sha256":hashlib.sha256(result.tobytes()).hexdigest()}
            return result,ix
G=[];native=None;native_grid=None
for z in levels:
    label="RH"+str(z)
    try:
        a,ix=sample_layer("https://data.source.coop/geoai-ucph/gvsm/mosaics/2020/"+label+"_Q1.tif",label,.1,32767)
        g=report["sources"][label]["source_grid"]
        if native_grid is None:native_grid=g;native=ix
        else:assert g==native_grid
        G.append(a)
        print("LAYER_DONE",label,report["sources"][label]["valid_cells"],flush=True)
    except Exception as e:report["errors"][label]=type(e).__name__+": "+str(e)[:220]
if len(G)!=len(levels):
    report["status"]="BLOCKED_GVSM_LAYER";save_report();sys.exit(1)
G=np.stack(G,axis=1)
# WorldCover original tree-class area fraction, identical 30% threshold to Iberian protocol.
classes=[10,20,30,40,50,60,70,80,90,95,100]
tile_cells=collections.defaultdict(list);bbox={}
for i,(x,y) in enumerate(cells):
    l,b=I.transform(x*1000,y*1000);r,t=I.transform((x+1)*1000,(y+1)*1000)
    bbox[i]=(l,b,r,t)
    for lat in range(math.floor(b/3)*3,math.ceil(t/3)*3,3):
        for lon in range(math.floor(l/3)*3,math.ceil(r/3)*3,3):
            tile_cells[(lat,lon)].append(i)
assert len(tile_cells)<160
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
area=np.zeros((len(cells),len(classes)),dtype=float)
report["worldcover_tiles"]=[]
def guarded(task):
    try:return tile(task)
    except Exception as e:return {"tile":str(task[0]),"status":"failed","cells":len(task[1]),"error":type(e).__name__+": "+str(e)[:200]},[]
with ThreadPoolExecutor(max_workers=3) as ex:
    for meta,parts in ex.map(guarded,sorted(tile_cells.items())):
        report["worldcover_tiles"].append(meta)
        for i,a in parts:area[i]+=a
        print("WORLDCOVER_TILE="+json.dumps(meta),flush=True)
total=area.sum(axis=1);lcvalid=(total>=950000)&(total<=1050000)
fraction=np.full_like(area,np.nan);fraction[lcvalid]=area[lcvalid]/total[lcvalid,None]
gvvalid=np.isfinite(G).all(axis=1)&(np.diff(G,axis=1)>=0).all(axis=1)
h=G[:,-1]
forest=lcvalid&(fraction[:,0]>=.3)
primary=gvvalid&forest&(h>5)
# Actual source failures remain nonadmitted; do not confuse unavailable tile with nonforest.
report["worldcover_failed_tiles"]=sum(x["status"]=="failed" for x in report["worldcover_tiles"])
report["worldcover_missing_tiles"]=sum(x["status"]=="not_distributed" for x in report["worldcover_tiles"])
report["worldcover_valid_unique_cells"]=int(lcvalid.sum())
report["gvsm_valid_unique_cells"]=int(gvvalid.sum())
report["joint_forest_unique_cells"]=int(primary.sum())
report["forest_tree_fraction_threshold"]=.3
report["training_domain_note"]="GVSM north of 51.6 degrees is model extrapolation, not equivalent training coverage; this archive stays within the narrower source rectangle."
idx={c:i for i,c in enumerate(cells)}
passed=collections.defaultdict(lambda:collections.defaultdict(set));allc=collections.defaultdict(set)
for (s,x,y),n in species_cells.items():
    allc[s].add((x,y))
    if primary[idx[(x,y)]]:passed[s][(x//200,y//200)].add((x,y))
coverage=[]
for s,v in allc.items():
    n=sum(map(len,passed[s].values()));nb=sum(len(c)>=5 for c in passed[s].values())
    coverage.append({"species_key":s,"pre_environment_cells":len(v),"forest_profile_cells":n,"blocks_ge5":nb,"passes_forest_gate":n>=30 and nb>=4})
coverage.sort(key=lambda a:-a["forest_profile_cells"])
report["species_coverage"]=coverage
report["species_passing_forest_profile_gate"]=sum(a["passes_forest_gate"] for a in coverage)
report["forest_profile_species_cells"]=sum(a["forest_profile_cells"] for a in coverage)
with (OUT/"species_cell_environment.csv").open("w",newline="",encoding="utf8") as f:
    w=csv.writer(f);w.writerow(["species_key","cell_x","cell_y","records","native_rh_row","native_rh_col",*[f"RH{z}_m" for z in levels],*[f"worldcover_class_{c}_fraction" for c in classes],"valid_area_m2","forest_profile_support","R50"])
    for (s,x,y),n in sorted(species_cells.items()):
        i=idx[(x,y)];w.writerow([s,x,y,n,*native[i],*G[i],*fraction[i],total[i],bool(primary[i]),float(G[i,2]/h[i]) if primary[i] else ""])
report["output_sha256"]=hashlib.sha256((OUT/"species_cell_environment.csv").read_bytes()).hexdigest()
report["status"]="ACTUAL_FOREST_PROFILE_SUPPORT_READY" if report["worldcover_failed_tiles"]==0 else "PARTIAL_FOREST_SUPPORT_LOWER_BOUND"
report["admission"]=False
report["limitations"]=["This archive has 26 completely retrieved physical-trait species and at most 14 passing pre-environment coverage; not the wider continental run.","No background, climate, terrain or final source-level effort/roost/season/DOI gate in this step.","No SDM, no selection or trait-effect inference. GVSM RH is a predicted waveform profile, not PAVD or air volume.","WorldCover class fractions are 10m source-pixel equal-area centre assignments; cells with <95% valid source area excluded."]
save_report()
