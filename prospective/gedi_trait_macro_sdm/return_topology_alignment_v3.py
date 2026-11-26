"""Full-depth EPT patch return topology. Not actual empty volume or flight feasibility."""
import collections, hashlib, io, itertools, json, math, pathlib, sys
import laspy, numpy as np, requests
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from pyproj import Transformer

PROJECTS={
 "NH1":("NH_Coastal_1_2019","67441"),
 "NH2":("NH_Coastal_2_2019","67394"),
 "WA1":("WA_DNR_3DEP_Processing_1_2019","73306")}
ID=sys.argv[1];project,inport=PROJECTS[ID]
BASE="https://s3-us-west-2.amazonaws.com/usgs-lidar-public/"+project+"/"
OUT=pathlib.Path("return_topology_v3")/ID;OUT.mkdir(parents=True,exist_ok=True)
CACHE=pathlib.Path("return_topology_v3_cache")/ID;CACHE.mkdir(parents=True,exist_ok=True)
R={"project":project,"metadata_source":"https://www.fisheries.noaa.gov/inport/item/"+inport,"source_url":BASE+"ept.json","status":"START","transfers":[],"patches":[],"claim_boundary":"Point-return avoidance proxy; unobserved voxels unknown; not bat passability."}
S=requests.Session()
BUDGET=250*1024**2
class Stop(Exception):pass
def need(ok,msg):
    if not ok:raise Stop(msg)
def save():
    p=OUT/"report.json"
    p.write_text(json.dumps(R,indent=2,allow_nan=False)+"\n")
    print("RETURN_TOPOLOGY_STATUS="+R["status"],flush=True)
def get(path,limit):
    key=hashlib.sha256(path.encode()).hexdigest()
    p=CACHE/key
    if p.exists():return p.read_bytes()
    need(len(R["transfers"])<1200,"node/metadata count budget")
    left=BUDGET-sum(x.get("bytes",0) for x in R["transfers"])
    limit=min(limit,left)
    need(limit>0,"project byte budget")
    entry={"path":path}
    R["transfers"].append(entry)
    try:
        with S.get(BASE+path,timeout=(15,60),stream=True,allow_redirects=False) as r:
            entry["http"]=r.status_code
            need(r.status_code==200,"HTTP "+str(r.status_code)+" for "+path)
            parts=[];n=0
            for chunk in r.iter_content(65536):
                n+=len(chunk)
                if n>limit:raise Stop("object/project byte budget")
                parts.append(chunk)
        b=b"".join(parts);entry.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
        p.write_bytes(b);return b
    except requests.RequestException as e:raise Stop("transport "+type(e).__name__) from e
def getjson(path):
    return json.loads(get(path,8*1024**2))
def node_bounds(key,bb):
    d,i,j,k=map(int,key.split("-"))
    need(0<=d<=40 and all(0<=u<2**d for u in (i,j,k)),"hierarchy key")
    lo=np.asarray(bb[:3]);hi=np.asarray(bb[3:]);w=(hi-lo)/2**d
    a=lo+w*np.array([i,j,k]);return a,a+w
def intersect(key,bb,box):
    a,b=node_bounds(key,bb);return bool(a[0]<=box[2] and b[0]>=box[0] and a[1]<=box[3] and b[1]>=box[1])
def enumerate_nodes(bb,box):
    pages=["0-0-0-0"];visited=set();nodes={}
    while pages:
        p=pages.pop()
        if p in visited:continue
        visited.add(p)
        data=getjson("ept-hierarchy/"+p+".json")
        need(isinstance(data,dict) and p in data,"hierarchy page schema")
        for k,n in data.items():
            need(isinstance(n,int) and n>=-1,"hierarchy count")
            if not intersect(k,bb,box):continue
            if n==-1:
                need(k!=p,"self-referencing hierarchy page")
                pages.append(k)
            elif n:
                need(k not in nodes or nodes[k]==n,"conflicting node count")
                nodes[k]=n
        need(len(nodes)<=1200,"intersecting nodes budget")
    return sorted(nodes.items(),key=lambda v:tuple(map(int,v[0].split("-"))))
def retained_mask(X,Y,x,y,cls,withheld):
    # LAS subfield views can expose uint8, not bool. Never use their
    # bitwise complement directly as an indexing array.
    withheld=np.asarray(withheld,dtype=bool)
    cls=np.asarray(cls,dtype=int)
    keep=(np.abs(X-x)<40)&(np.abs(Y-y)<40)&(~withheld)&(~np.isin(cls,[7,18]))
    need(keep.dtype==np.dtype(bool) and keep.shape==X.shape,"boolean row mask")
    return keep
def acquire(meta,ctr):
    lon,lat=Transformer.from_crs(3857,4326,always_xy=True).transform(*ctr)
    utm=32600+int((lon+180)//6)+1 if lat>=0 else 32700+int((lon+180)//6)+1
    f=Transformer.from_crs(3857,utm,always_xy=True);inv=Transformer.from_crs(utm,3857,always_xy=True)
    x,y=f.transform(*ctr);corn=np.array([inv.transform(x+a,y+b) for a,b in itertools.product([-41,41],repeat=2)])
    box=[float(corn[:,0].min()),float(corn[:,1].min()),float(corn[:,0].max()),float(corn[:,1].max())]
    nodes=enumerate_nodes(meta["bounds"],box)
    need(bool(nodes),"no intersecting nodes")
    pieces=[];counts=collections.Counter();total=0
    for key,n in nodes:
        b=get("ept-data/"+key+".laz",10*1024**2)
        need(b[:4]==b"LASF","not LASF")
        a=laspy.read(io.BytesIO(b))
        need(len(a.points)==n,"decoded count mismatch")
        total+=n
        X=np.asarray(a.x);Y=np.asarray(a.y)
        take=(X>=box[0])&(X<=box[2])&(Y>=box[1])&(Y<=box[3])
        if not take.any():continue
        X,Y=f.transform(X[take],Y[take]);Z=np.asarray(a.z)[take]
        cls=np.asarray(a.classification)[take].astype(int)
        keep=retained_mask(X,Y,x,y,cls,np.asarray(a.withheld,dtype=bool)[take])
        arr=np.column_stack((X[keep]-x,Y[keep]-y,Z[keep],cls[keep]))
        if len(arr):pieces.append(arr)
        counts.update(cls[keep].tolist())
    a=np.concatenate(pieces) if pieces else np.empty((0,4))
    return a,{"utm_epsg":utm,"center_wgs84":[lon,lat],"nodes":len(nodes),"decoded_points":total,"retained_padded_points":len(a),"classification_counts":{str(k):int(v) for k,v in sorted(counts.items())}}
def support(a,record):
    ground=a[a[:,3]==2];other=a[a[:,3]!=2]
    if len(ground)<4:return None,"too few ground returns"
    T=cKDTree(ground[:,:2]);gx,gy=np.meshgrid(np.arange(-31.5,32,1),np.arange(-31.5,32,1),indexing="ij")
    gd,idx=T.query(np.column_stack([gx.ravel(),gy.ravel()]))
    record["max_center_ground_distance_m"]=float(gd.max())
    if gd.max()>3:return None,"ground distance gate"
    other=other[(abs(other[:,0])<32)&(abs(other[:,1])<32)]
    if not len(other):return None,"no nonground returns"
    d,idx=T.query(other[:,:2])
    record["max_return_ground_distance_m"]=float(d.max())
    if d.max()>3:return None,"obstacle ground distance gate"
    a=other.copy();a[:,2]-=ground[idx,2]
    record["nonground_return_density_m2"]=len(a)/4096
    q=a[a[:,2]>=5]
    cover=len(np.unique(np.floor(q[:,:2]+32).astype(int),axis=0))/4096
    record["return_above5m_column_fraction"]=cover
    if len(a)/4096<2 or cover<.25:return None,"return density/above5m gate"
    return a,None
def vox(a,res):
    shape=(int(64/res),int(64/res),int(28/res))
    q=a[(a[:,2]>=2)&(a[:,2]<30),:3]
    ind=np.floor((q+np.array([32,32,-2]))/res).astype(int)
    v=np.zeros(shape,dtype=bool)
    if len(ind):v[tuple(ind.T)]=True
    return v
def dist(v):
    return ndi.distance_transform_edt(~v) if v.any() else np.full(v.shape,np.inf)
STRUCT=ndi.generate_binary_structure(3,1)
def metrics(v,res,radius,dt=None):
    if dt is None:dt=dist(v)*res
    free=dt>radius
    lab,n=ndi.label(free,structure=STRUCT)
    count=np.bincount(lab.ravel(),minlength=n+1);count[0]=0
    def frac(labels):
        labels=np.asarray(labels);return float(count[labels[labels>0]].sum()/v.size)
    def cross(x,y):return frac(np.intersect1d(np.unique(x),np.unique(y)))
    return [float(free.mean()),float(count.max()/v.size),cross(lab[0],lab[-1]),cross(lab[:,0],lab[:,-1]),frac(np.unique(lab[:,:,0]))]
METRICS=["candidate_fraction","largest_component_fraction","x_crossing_component_fraction","y_crossing_component_fraction","bottom_connected_fraction"]
def curves(v,res,radii):
    dt=dist(v)*res
    return np.array([metrics(v,res,r,dt) for r in radii])
def null(v,rng):
    p=np.zeros_like(v)
    for k in range(v.shape[2]):
        n=int(v[:,:,k].sum());a=np.zeros(v.shape[0]*v.shape[1],bool)
        if n:a[rng.choice(len(a),n,replace=False)]=True
        p[:,:,k]=a.reshape(v.shape[:2])
    need(np.array_equal(p.sum((0,1)),v.sum((0,1))),"null layer count")
    return p
def synthetic():
    # Check exact row selection for uint8 flags, including a one-point node.
    X=np.array([0.,0.,0.,0.,41.,0.]);Y=np.zeros(6)
    cls=np.array([1,2,7,18,1,1]);w=np.array([0,1,0,0,0,0],dtype=np.uint8)
    k=retained_mask(X,Y,0.,0.,cls,w)
    need(k.tolist()==[True,False,False,False,False,True],"uint8 mask regression")
    need(X[k].tolist()==[0.,0.],"row selection regression")
    for flag,expected in [(0,True),(1,False)]:
        k=retained_mask(np.array([0.]),np.array([0.]),0.,0.,np.array([2]),np.array([flag],dtype=np.uint8))
        need(k.tolist()==[expected],"single point regression")
    v=np.zeros((16,16,8),bool);v[8,:,:]=True
    a=curves(v,1,[0,1,2]);need(a[0,2]==0 and a[0,3]>0,"plane crossing check")
    need(np.all(np.diff(a,axis=0)<=1e-12),"radius monotonicity")
    n=null(v,np.random.default_rng(88));need(np.isclose(n.mean(),v.mean()),"null count")
def analyze(a,pidx):
    v=vox(a,1);radii=[0,1,2];obs=curves(v,1,radii)
    need(np.all(np.diff(obs,axis=0)<=1e-12),"radius monotonicity")
    rng=np.random.default_rng(np.random.SeedSequence([20261126,list(PROJECTS).index(ID),pidx]))
    sims=np.stack([curves(null(v,rng),1,radii) for _ in range(100)])
    half=a[rng.choice(len(a),len(a)//2,replace=False)]
    half_curve=curves(vox(half,1),1,radii)
    coarse=curves(vox(a,2),2,[0,2])
    return {"radii_m":radii,"metric_order":METRICS,"observed":obs.tolist(),"null_mean":sims.mean(0).tolist(),"null_q025":np.quantile(sims,.025,axis=0).tolist(),"null_q975":np.quantile(sims,.975,axis=0).tolist(),"observed_minus_null":(obs-sims.mean(0)).tolist(),"null_replicates":100,"layer_counts":v.sum((0,1)).tolist(),"half_point_curve":half_curve.tolist(),"coarse_2m_curve_radii_0_2":coarse.tolist()}
def unit_check(a,info):
    g=a[a[:,3]==2]
    T=cKDTree(g[:,:2])
    d,ix=T.query(np.array([[0.,0.],[-20.,-20.],[-20.,20.],[20.,-20.],[20.,20.]]))
    crs=info["utm_epsg"]
    tr=Transformer.from_crs(4326,crs,always_xy=True)
    x,y=tr.transform(*info["center_wgs84"])
    inv=Transformer.from_crs(crs,4326,always_xy=True)
    rows=[];errors=[]
    for i in sorted(set(ix.tolist())):
        q=g[i];lon,lat=inv.transform(x+q[0],y+q[1])
        row={"lon":lon,"lat":lat,"raw_z":float(q[2])};rows.append(row)
        try:
            resp=S.get("https://epqs.nationalmap.gov/v1/json",params={"x":lon,"y":lat,"wkid":4326,"units":"Meters","includeDate":"true"},timeout=(10,25),allow_redirects=False)
            row["http"]=resp.status_code
            if resp.status_code in (401,403):break
            if resp.status_code!=200:continue
            row["sha256"]=hashlib.sha256(resp.content).hexdigest()
            j=resp.json();z=float(j["value"]);res=float(j["resolution"])
            row.update(dem_m=z,resolution_m=res)
            if np.isfinite(z) and np.isfinite(res) and 0<res<=10 and abs(z)>=20 and abs(z)<10000:
                errors.append([abs(float(q[2])-z),abs(float(q[2])*1200/3937-z)])
        except (ValueError,KeyError,requests.RequestException,TypeError) as e:row["error_type"]=type(e).__name__
    med=np.median(errors,axis=0).tolist() if len(errors)>=3 else None
    chosen=None
    if med is not None:
        if med[0]<=3 and med[1]>=10:chosen="metre"
        elif med[1]<=3 and med[0]>=10:chosen="us_survey_foot"
    if ID=="WA1" and chosen=="us_survey_foot":raise Stop("WA metre lineage contradicted")
    if ID=="WA1" and chosen is None:chosen="metre_metadata_only"
    return {"method":"EPQS DEM unit consistency, not independent survey accuracy","points":rows,"distinct_valid":len(errors),"median_absolute_error_m":med,"hypothesis":chosen}

import rasterio
from rasterio.windows import Window
R.update(stage="forest-screened new plots and interlayer registration V3",selection_frozen=False,screening=[])
WC_BASE="https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/"
CLASSES={10,20,30,40,50,60,70,80,90,95,100}
def tile_key(lon,lat):
    a=int(math.floor(lat/3)*3);b=int(math.floor(lon/3)*3)
    return ("N" if a>=0 else "S")+f"{abs(a):02d}"+("E" if b>=0 else "W")+f"{abs(b):03d}"
def forest_screen(bb):
    prev=[(bb[0]+u*(bb[3]-bb[0]),bb[1]+v*(bb[4]-bb[1])) for u,v in itertools.product([.25,.5,.75],repeat=2)]
    inv=Transformer.from_crs(3857,4326,always_xy=True);candidates=[]
    for j,(u,v) in enumerate(itertools.product([.10,.26,.42,.58,.74,.90],repeat=2),1):
        ctr=[bb[0]+u*(bb[3]-bb[0]),bb[1]+v*(bb[4]-bb[1])]
        lon,lat=inv.transform(*ctr);utm=(32600 if lat>=0 else 32700)+int((lon+180)//6)+1
        f=Transformer.from_crs(3857,utm,always_xy=True);g=Transformer.from_crs(utm,4326,always_xy=True)
        x,y=f.transform(*ctr);old=np.array([f.transform(*p) for p in prev])
        rec={"position_index":j,"extent_fraction":[u,v],"center_wgs84":[lon,lat],"nearest_original_candidate_m":float(np.linalg.norm(old-[x,y],axis=1).min())};R["screening"].append(rec)
        if rec["nearest_original_candidate_m"]<500:
            rec["status"]="EXCLUDE_OLD_CANDIDATE_PROXIMITY";continue
        ll=[g.transform(x+i,y+k) for i,k in itertools.product(np.arange(-28,29,8),repeat=2)]
        need(len(ll)==64,"forest sampling stencil")
        groups=collections.defaultdict(list)
        for i,(ln,lt) in enumerate(ll):groups[tile_key(ln,lt)].append((i,ln,lt))
        values=np.full(64,-1,dtype=np.int16);sources=[]
        for tok,items in sorted(groups.items()):
            url=WC_BASE+"ESA_WorldCover_10m_2021_v200_"+tok+"_Map.tif"
            try:
                with rasterio.open(url) as src:
                    need(src.crs.to_epsg()==4326 and src.count==1 and src.transform.a>0 and src.transform.e<0 and src.transform.b==0 and src.transform.d==0,"WorldCover grid")
                    rc=[src.index(ln,lt) for _,ln,lt in items]
                    need(all(0<=rr<src.height and 0<=cc<src.width for rr,cc in rc),"WorldCover tile range")
                    r0=min(rr for rr,cc in rc);r1=max(rr for rr,cc in rc);c0=min(cc for rr,cc in rc);c1=max(cc for rr,cc in rc)
                    data=src.read(1,window=Window(c0,r0,c1-c0+1,r1-r0+1),masked=True)
                    for (i,_,_),(rr,cc) in zip(items,rc):
                        q=data[rr-r0,cc-c0]
                        if not np.ma.is_masked(q) and int(q) in CLASSES:values[i]=int(q)
                    sources.append({"tile":tok,"url":url,"shape":[src.height,src.width],"transform":list(src.transform),"window":[r0,r1,c0,c1]})
            except rasterio.errors.RasterioIOError:
                rec.update(status="STOP_WORLDCOVER_TRANSPORT",tile=tok);save();raise Stop("WorldCover access/coverage failure")
        n=int((values>=0).sum());trees=int((values==10).sum())
        rec.update(valid_samples=n,tree_samples=trees,tree_fraction=trees/n if n else None,sample_sha256=hashlib.sha256(values.astype("<i2").tobytes()).hexdigest(),sources=sources)
        if n>=61 and trees/n>=.80:rec["status"]="FOREST_SCREEN_PASS";candidates.append((j,ctr))
        else:rec["status"]="FOREST_SCREEN_STOP"
    R.update(selection_frozen=True,forest_candidate_count=len(candidates),frozen_candidate_indices=[j for j,_ in candidates]);save();return candidates
def periodic_counts(q):
    return np.stack([np.sum(q&np.roll(q,1,axis=a),axis=(0,1)) for a in (0,1)])
def shifted(q,rng):
    t=np.empty_like(q)
    for k in range(q.shape[2]):t[:,:,k]=np.roll(q[:,:,k],tuple(rng.integers([q.shape[0],q.shape[1]])),axis=(0,1))
    need(np.array_equal(t.sum((0,1)),q.sum((0,1))),"shift layer counts")
    need(np.array_equal(periodic_counts(t),periodic_counts(q)),"shift adjacency")
    return t
def periodic_metrics(q):
    lab,n=ndi.label(q,structure=STRUCT);count=np.bincount(lab.ravel(),minlength=n+1).astype(np.int64);count[0]=0
    parent=np.arange(n+1,dtype=int)
    def root(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    for l,r in ((lab[0],lab[-1]),(lab[:,0],lab[:,-1])):
        m=(l>0)&(r>0)
        if m.any():
            for x,y in np.unique(np.column_stack([l[m],r[m]]),axis=0):
                x=root(int(x));y=root(int(y))
                if x!=y:parent[y]=x
    roots=np.array([root(i) for i in range(n+1)],int);merged=np.bincount(roots,weights=count,minlength=n+1);nb=int(q.sum())
    lower=np.unique(roots[lab[:,:,0]]);upper=np.unique(roots[lab[:,:,-1]]);through=np.intersect1d(lower[lower>0],upper[upper>0])
    return [float((q[:,:,1:]&q[:,:,:-1]).mean()),float(merged.max()/nb) if nb else 0.,float(merged[through].sum()/nb) if nb else 0.]
def finite_metrics(q):
    l,n=ndi.label(q,structure=STRUCT);c=np.bincount(l.ravel(),minlength=n+1);c[0]=0
    def cross(a,b):
        u=np.intersect1d(np.unique(a),np.unique(b));return float(c[u[u>0]].sum()/q.size)
    return [float(q.mean()),float(c.max()/q.size),cross(l[0],l[-1]),cross(l[:,0],l[:,-1])]
def summary(o,s):
    a=np.asarray(s);return {"observed":list(o),"null_mean":a.mean(0).tolist(),"null_q025":np.quantile(a,.025,axis=0).tolist(),"null_q975":np.quantile(a,.975,axis=0).tolist(),"observed_minus_null_mean":(np.asarray(o)-a.mean(0)).tolist()}
def test_new():
    synthetic()
    q=np.zeros((5,5,4),bool);q[0,2,1]=q[-1,2,1]=True
    need(finite_metrics(q)[1]==1/q.size and periodic_metrics(q)[1]==1.,"periodic seam test")
    q=np.zeros((5,5,4),bool);q[2,2,0]=q[2,2,-1]=True
    need(periodic_metrics(q)[1]==.5 and periodic_metrics(q)[2]==0.,"no vertical wrap")
    q=np.zeros((5,5,4),bool);q[2,2,:]=True
    need(periodic_metrics(q)[0]==1/25 and periodic_metrics(q)[2]==1.,"vertical edge and through test")
    shifted(q,np.random.default_rng(17))
def test_patch(a,j):
    v=vox(a,1);dt=dist(v);rng=np.random.default_rng(np.random.SeedSequence([20261126,3,list(PROJECTS).index(ID),j]));out={}
    for radius in (1,2):
        q=dt>radius;obs=periodic_metrics(q);fo=finite_metrics(q);shift_sim=[];perm_sim=[]
        for _ in range(100):
            shift_sim.append(periodic_metrics(shifted(q,rng)));perm_sim.append(finite_metrics(null(q,rng)))
        out[str(radius)]={"candidate_fraction":float(q.mean()),"shift_metric_order":["vertical_neighbor_edge_fraction","periodic_largest_given_candidate_fraction","periodic_bottom_to_top_given_candidate_fraction"],"finite_metric_order":["candidate_fraction","largest_component_fraction","x_crossing_fraction","y_crossing_fraction"],"shift_null_periodic":summary(obs,shift_sim),"permutation_null_finite":summary(fo,perm_sim)}
    return out
def main():
    test_new();R["synthetic_checks_passed"]=True
    meta=getjson("ept.json");need(meta.get("dataType")=="laszip" and str(meta.get("srs",{}).get("horizontal"))=="3857","unsupported format/CRS")
    R["ept_metadata"]={k:meta.get(k) for k in ["bounds","boundsConforming","points","span","dataType","srs","version"]};bb=meta["boundsConforming"]
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",GDAL_HTTP_TIMEOUT="30",GDAL_HTTP_MAX_RETRY="0"):
        cand=forest_screen(bb)
    passed=0
    for j,ctr in cand:
        rec={"position_index":j};R["patches"].append(rec);a,info=acquire(meta,ctr);rec.update(info)
        if len(a[a[:,3]==2])<4:rec.update(status="SUPPORT_STOP",reason="too few ground returns");save();continue
        unit=unit_check(a,info);rec["vertical_unit_audit"]=unit
        if unit["hypothesis"]!="metre":rec.update(status="STOP_UNIT_NOT_CONFIRMED");save();continue
        a,reason=support(a,rec)
        if reason:rec.update(status="SUPPORT_STOP",reason=reason);save();continue
        rec.update(status="COMPLETE_GEOMETRY_ONLY",results=test_patch(a,j));passed+=1
        print("RETURN_V3_PATCH="+json.dumps({"project":ID,"index":j,"r2":rec["results"]["2"]}),flush=True);R["passing_patches"]=passed;save()
        if passed==6:break
    R.update(status="COMPLETE_GEOMETRY_ONLY",passing_patches=passed);save()
if __name__=="__main__":
    try:main()
    except Exception as e:
        R.update(status="STOP_SOURCE_OR_QC",error_type=type(e).__name__,reason=str(e)[:250] if isinstance(e,Stop) else "unexpected runtime");save()
        if not isinstance(e,Stop):raise
