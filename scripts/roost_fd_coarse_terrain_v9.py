"""V9 regional terrain graph pilot: raster compatibility repair only. Never export cave IDs, coordinates or site-level predictions.
Terrain costs are uncalibrated symmetric hypotheses, NOT bat flight resistance.
"""
import json,hashlib,zipfile,sys,re
from pyproj import CRS
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import Window
from rasterio.io import MemoryFile
from scipy import sparse
from scipy.sparse.linalg import spsolve
from scipy.sparse.csgraph import connected_components
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import Ridge
from roost_fd_source_audit_v2 import get,OUT,S
from roost_fd_source_audit_v3 import quant
from roost_fd_source_audit_v4 import wing,cavekeys
from roost_fd_empirical_null_v5 import prepare,build_dist,SEED,NREP
from roost_fd_study_wing_v7 import study_wing
DEM="https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/data/60s/60s_surface_elev_gtif/ETOPO_2022_v1_60s_N90W180_surface.tif"
CLIM="https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_10m_bio.zip"
AX=[("flight",["logar","logwl"],[]),("resource",["logmass","diet"],["diet"])]
FIELDS=["logar","logwl","logmass","diet"]
LAND=["Canopy.cov","Tree.dens","Freshwater.dist","Nighlight"]
BASE=["log_n","coverage","abs_lat","bio1","bio4","bio12","bio15"]+LAND
TERRAIN=["mean_elev","relief","slope_median","slope90","nonnegative_fraction"]
GRAPH=["logR_uniform","logR_shuffle"]

def acquire(url,path,maxbytes):
    h=hashlib.sha256();n=0
    with S.get(url,stream=True,timeout=(20,60)) as r:
        r.raise_for_status()
        with path.open("wb") as f:
            for b in r.iter_content(1024*1024):
                n+=len(b)
                if n>maxbytes:raise ValueError("download bound exceeded")
                h.update(b);f.write(b)
    return {"bytes":n,"sha256":h.hexdigest(),"url":url}

def raster_metadata(src,kind):
    # Verify actual horizontal CRS, including compound horizontal+vertical CRS.
    # Never assume that to_epsg()==4326 is the sole valid representation.
    if src.crs is None:raise ValueError(kind+" missing CRS")
    crs=CRS.from_wkt(src.crs.to_wkt())
    horizontal=crs.to_2d()
    b=src.bounds;t=src.transform
    meta={"crs":crs.to_string(),"horizontal_crs":horizontal.to_string(),
          "epsg":src.crs.to_epsg(),"width":src.width,"height":src.height,
          "bounds":[float(b.left),float(b.bottom),float(b.right),float(b.top)],
          "pixel_size":[float(t.a),float(t.e)],"nodata":str(src.nodata),
          "horizontal_wgs84":bool(horizontal.equals(CRS.from_epsg(4326),ignore_axis_order=True))}
    # Geographic x/y (longitude/latitude) with rectilinear north-up transform.
    valid=(meta["horizontal_wgs84"] and horizontal.is_geographic
           and t.a>0 and t.e<0 and abs(t.b)<1e-10 and abs(t.d)<1e-10
           and b.left>=-181 and b.right<=181 and b.bottom>=-91 and b.top<=91
           and b.right-b.left>300 and b.top-b.bottom>100)
    meta["compatible"]=bool(valid)
    return meta

def coarse(site):
    # Only public coordinates, further quantized; never output.
    lat=float(site[2]);lon=float(site[3])
    return (round(lat*4)/4,round(lon*4)/4)

def sample_grid(src,lon,lat):
    """Read one local raster window; all computations on private in-memory arrays."""
    lon=np.asarray(lon);lat=np.asarray(lat);shape=lon.shape
    r,c=rasterio.transform.rowcol(src.transform,lon.ravel(),lat.ravel())
    r=np.asarray(r);c=np.asarray(c)
    good=(r>=0)&(r<src.height)&(c>=0)&(c<src.width)
    out=np.full(len(r),np.nan)
    if good.any():
        rr=r[good];cc=c[good]
        r0=int(rr.min());c0=int(cc.min())
        a=src.read(1,window=Window(c0,r0,int(cc.max())-c0+1,int(rr.max())-r0+1),masked=True)
        out[good]=np.ma.asarray(a[rr-r0,cc-c0],dtype=float).filled(np.nan)
    return out.reshape(shape)

def climate(bios,center):
    lat,lon=center;d=1/6
    yy,xx=np.meshgrid(lat+np.array([-d,0,d]),lon+np.array([-d,0,d]),indexing="ij")
    result={}
    for n,ds in bios.items():
        v=sample_grid(ds,xx,yy);v=v[np.isfinite(v)]
        result["bio"+str(n)]=float(np.median(v)) if len(v) else np.nan
    return result

def effective(n,u,v,c,source,sink):
    assert np.all(c>0) and not np.any(source&sink)
    L=sparse.coo_matrix((np.r_[c,c,-c,-c],(np.r_[u,v,u,v],np.r_[u,v,v,u])),shape=(n,n)).tocsr()
    f=np.zeros(n);f[source]=1
    inner=~(source|sink)
    if inner.any():f[inner]=spsolve(L[inner][:,inner],-(L@f)[inner])
    j=float((L@f)[source].sum())
    energy=float(np.dot(c,(f[u]-f[v])**2))
    if not np.isfinite(j) or j<=0 or abs(j-energy)>1e-7*max(1,j):raise ValueError("circuit check failed")
    if inner.any() and np.max(abs((L@f)[inner]))>1e-7:raise ValueError("Kirchhoff check failed")
    return 1/j

def graph_test():
    u=np.array([0,1]);v=np.array([1,2]);s=np.array([True,False,False]);t=np.array([False,False,True])
    assert np.isclose(effective(3,u,v,np.ones(2),s,t),2)
    u=np.array([0,0,1,2]);v=np.array([1,2,3,3]);s=np.array([True,False,False,False]);t=np.array([False,False,False,True])
    assert np.isclose(effective(4,u,v,np.ones(4),s,t),1)

def terrain(src,center,radius):
    lat,lon=center;dx=5
    if abs(lat)>75 or abs(lon)+radius/(111*np.cos(np.deg2rad(lat)))+1>=180:return None
    xy=np.arange(-radius,radius+dx,dx)
    Y,X=np.meshgrid(xy,xy,indexing="ij");dist=np.hypot(X,Y)
    disk=dist<=radius
    # Approximate local metric grid; mean over nine subpoints per 5km cell.
    samples=[]
    for oy in (-dx/3,0,dx/3):
        for ox in (-dx/3,0,dx/3):
            samples.append(sample_grid(src,lon+(X+ox)/(111.32*np.cos(np.deg2rad(lat))),lat+(Y+oy)/110.57))
    arr=np.asarray(samples);nonneg=np.isfinite(arr)&(arr>=0)
    counts=nonneg.sum(axis=0);z=np.divide(np.where(nonneg,arr,0).sum(axis=0),counts,
                         out=np.full(X.shape,np.nan),where=counts>=5)
    valid=disk&np.isfinite(z)
    if valid.sum()<25:return None
    ids=np.full(z.shape,-1,int);ids[valid]=np.arange(valid.sum())
    U=[];V=[]
    for a,b in ((ids[:-1,:],ids[1:,:]),(ids[:,:-1],ids[:,1:])):
        good=(a>=0)&(b>=0);U.extend(a[good]);V.extend(b[good])
    u=np.asarray(U,int);v=np.asarray(V,int);n=int(valid.sum())
    if len(u)<10:return None
    adj=sparse.coo_matrix((np.ones(2*len(u)),(np.r_[u,v],np.r_[v,u])),shape=(n,n)).tocsr()
    _,comp=connected_components(adj,directed=False)
    dr=dist[valid];nearest=int(np.argmin(dr))
    if dr[nearest]>15:return None
    keep=comp==comp[nearest];id2=np.full(n,-1,int);id2[keep]=np.arange(keep.sum())
    ok=keep[u]&keep[v];u=id2[u[ok]];v=id2[v[ok]]
    zz=z[valid][keep];dr=dr[keep];n=int(keep.sum())
    source=dr<=15;sink=dr>=radius-dx
    if not source.any() or not sink.any() or n<25 or not len(u):return None
    slopes=abs(zz[u]-zz[v])/(dx*1000)
    c=np.exp(-slopes/.05)
    r=effective(n,u,v,c,source,sink)
    r0=effective(n,u,v,np.ones_like(c),source,sink)
    rng=np.random.default_rng(SEED)
    sh=[np.log(effective(n,u,v,rng.permutation(c),source,sink)) for _ in range(16)]
    return {"mean_elev":float(zz.mean()),"relief":float(np.ptp(np.quantile(zz,[.1,.9]))),
      "slope_median":float(np.median(slopes)),"slope90":float(np.quantile(slopes,.9)),
      "nonnegative_fraction":float(nonneg[:,disk].mean()),"logR_uniform":float(np.log(r/r0)),
      "logR_shuffle":float(np.log(r)-np.mean(sh))}

def responses(x,tr,weighted):
    tr=tr.dropna(subset=FIELDS).sort_values("species").reset_index(drop=True)
    idx=dict(zip(tr.species,np.arange(len(tr))))
    D=np.asarray([build_dist(tr,f,cat) for _,f,cat in AX])
    x=x.copy();x["idx"]=x.species.map(idx)
    groups={};freq=defaultdict(Counter);nr=Counter()
    for k,g in x.groupby("site",sort=False):
        if g.realm.nunique()!=1:continue
        ids=np.sort(g.idx.dropna().astype(int).unique())
        r=g.realm.iloc[0];groups[k]=(len(g),ids,r,g.country.iloc[0])
        freq[r].update(ids.tolist());nr[r]+=1
    rng=np.random.default_rng(SEED);rows=[]
    for k,(N,ids,r,country) in groups.items():
        n=len(ids)
        if n<3 or n/N<.8:continue
        other=freq[r].copy();other.subtract(ids.tolist())
        pool=np.array(sorted(i for i,v in other.items() if v>0),int)
        if len(pool)<max(15,2*n) or nr[r]-1<10:continue
        if weighted:keys=rng.exponential(size=(NREP,len(pool)))/np.array([other[i] for i in pool])[None,:]
        else:keys=rng.random((NREP,len(pool)))
        draw=pool[np.argpartition(keys,n-1,axis=1)[:,:n]]
        i,j=np.triu_indices(n,1);obs=D[:,ids[i],ids[j]].mean(axis=1);exp=D[:,draw[:,i],draw[:,j]].mean(axis=2)
        sd=exp.std(axis=1,ddof=1)
        if not np.all(sd>1e-12):continue
        se=(obs-exp.mean(axis=1))/sd
        rows.append({"site":k,"realm":r,"country":country,"log_n":float(np.log(n)),"coverage":n/N,
                     "flight":float(se[0]),"resource":float(se[1])})
    return rows

def compare(df,block):
    nums=BASE+TERRAIN+GRAPH
    required=nums+["realm","country","flight","resource"]
    d=df.replace([np.inf,-np.inf],np.nan).dropna(subset=required).copy()
    groups=d[block].unique()
    if len(d)<40 or d.country.nunique()<8 or (block=="realm" and len(groups)<3):
        return {"status":"insufficient_common_rows","n":len(d),"countries":int(d.country.nunique()),"blocks":len(groups)}
    y=d[["flight","resource"]].to_numpy()
    preds={k:np.full_like(y,np.nan) for k in ("M0","M1","M2")}
    for g in groups:
        te=(d[block]==g).to_numpy();train=~te
        if train.sum()<20:return {"status":"insufficient_training_block","n":len(d),"blocks":len(groups)}
        # Equal total training weight per country, defined within training folds.
        cnt=d.loc[train,"country"].value_counts()
        w=d.loc[train,"country"].map(1/cnt).to_numpy();w=w/w.mean()
        for k,cols in [("M0",BASE),("M1",BASE+TERRAIN),("M2",nums)]:
            pre=ColumnTransformer([("numeric",StandardScaler(),cols),("realm",OneHotEncoder(handle_unknown="ignore"),["realm"])])
            model=make_pipeline(pre,Ridge(alpha=10))
            model.fit(d.loc[train],y[train],ridge__sample_weight=w)
            preds[k][te]=model.predict(d.loc[te])
    out={"status":"exploratory","n":len(d),"countries":int(d.country.nunique()),"blocks":len(groups),"axes":{}}
    for i,ax in enumerate(["flight","resource"]):
        a={}
        errs={}
        for k,p in preds.items():
            q=pd.DataFrame({"country":d.country.to_numpy(),"block":d[block].to_numpy(),"sq":(p[:,i]-y[:,i])**2})
            errs[k]=q.groupby("country").sq.mean()
            a[k+"_country_equal_RMSE"]=float(np.sqrt(errs[k].mean()))
        for n,b in (("M1","M0"),("M2","M1"),("M2","M0")):
            a[n+"_minus_"+b+"_RMSE"]=a[n+"_country_equal_RMSE"]-a[b+"_country_equal_RMSE"]
            a[n+"_better_countries_than_"+b]=int((errs[n]<errs[b]).sum())
            a[n+"_minus_"+b+"_country_MSE_quantiles"]=quant(errs[n]-errs[b])
        out["axes"][ax]=a
    return out

def main():
    graph_test()
    report={"status":"acquisition","sources":{},"runs":{},"claim_boundary":"Regional 2D land-elevation graph proxy; not entrance-scale, 3D, trait-specific or calibrated."}
    target=OUT/"terrain_v9.json"
    def save():target.write_text(json.dumps(report,indent=2,allow_nan=False))
    save()
    cache=Path("terrain_v9_cache");cache.mkdir(exist_ok=True)
    try:
        o,om=get("occ");l,lm=get("land");t,tm=get("traits");data,wm=wing()
        w,qc=study_wing(data["wingReview_wm_data_final.csv"],"direct_or_formula")
        report["sources"].update(occ=om["sha256"],land=lm["sha256"],traits=tm["sha256"],wing=wm)
        report["wing_complete_species"]=qc["complete_species"]
        report["stage"]="download_dem";save()
        report["sources"]["dem"]=acquire(DEM,cache/"dem.tif",650_000_000);save()
        report["stage"]="download_climate";save()
        report["sources"]["climate"]=acquire(CLIM,cache/"bio.zip",100_000_000);save()
        expected={"dem":"9d27d4b8ea8e76977e2988bca667d7c8fa68b927355feffcddd6b4875a7fd08e",
                  "climate":"00513224583665ec0f2f955a4ec252730c4deb2004cce9e793492a3f26df4dcf"}
        if any(report["sources"][k]["sha256"]!=v for k,v in expected.items()):
            raise ValueError("Raster bytes changed from V8")
        report["stage"]="land_lookup";save()
        lk=cavekeys(l,False);counts=lk.dropna().value_counts();keep=lk.isin(set(counts[counts==1].index))
        lookup={k:{c:pd.to_numeric(v[c],errors="coerce") for c in LAND} for k,(_,v) in zip(lk[keep],l[keep].iterrows())}
        from contextlib import ExitStack
        with ExitStack() as stack:
            report["stage"]="raster_metadata";save()
            dem=stack.enter_context(rasterio.open(cache/"dem.tif"))
            z=stack.enter_context(zipfile.ZipFile(cache/"bio.zip"));bios={}
            report["raster_metadata"]={"dem":raster_metadata(dem,"DEM"),"climate_members":[s for s in z.namelist() if s.lower().endswith(".tif")]}
            save()
            if not report["raster_metadata"]["dem"]["compatible"]:raise ValueError("DEM horizontal CRS or transform")
            for n in (1,4,12,15):
                fn=[s for s in z.namelist() if re.fullmatch(r"wc2[.]1_10m_bio_0?"+str(n)+r"[.]tif",Path(s).name,re.I)]
                if len(fn)!=1:raise ValueError("Unexpected climate file names")
                m=stack.enter_context(MemoryFile(z.read(fn[0])));bios[n]=stack.enter_context(m.open())
                meta=raster_metadata(bios[n],"BIO"+str(n))
                report["raster_metadata"]["bio"+str(n)]=meta;save()
                if not meta["compatible"]:raise ValueError("Climate horizontal CRS or transform")
            report["stage"]="site_responses";save()
            climate_cache={};terrain_cache={}
            for repair,weight in ((True,True),(True,False),(False,True)):
                x,tr,audit=prepare(o,l,t,w,repair);rows=responses(x,tr,weight)
                scenario=("repair" if repair else "strict")+("_weighted" if weight else "_uniform")
                report["stage"]="terrain_and_validation_"+scenario;save()
                report["runs"][scenario]={"eligible_response_rows":len(rows),"radii":{}}
                for radius in (50,100):
                    report["stage"]="terrain_and_validation_"+scenario+"_"+str(radius);save()
                    rr=[]
                    for a in rows:
                        center=coarse(a["site"])
                        if center not in climate_cache:climate_cache[center]=climate(bios,center)
                        if (center,radius) not in terrain_cache:terrain_cache[(center,radius)]=terrain(dem,center,radius)
                        f=terrain_cache[(center,radius)]
                        if f is None:continue
                        # Keep only covariates, grouping labels and response, no location key in frame.
                        v={k:x for k,x in a.items() if k!="site"}
                        rr.append({**v,**f,**climate_cache[center],**lookup[a["site"]],"abs_lat":abs(center[0])})
                    frame=pd.DataFrame(rr,columns=["flight","resource","country","realm"]+BASE+TERRAIN+GRAPH)
                    report["runs"][scenario]["radii"][str(radius)]={"graph_available":len(frame),
                      "missing_by_field":{c:int(frame[c].isna().sum()) for c in BASE+TERRAIN+GRAPH},
                      "country_holdout":compare(frame,"country"),"realm_holdout":compare(frame,"realm")}
                    save()
        report["status"]="completed_exploratory";report["stage"]="complete"
    except Exception as e:
        # Do not print arbitrary exception messages: they may contain site identifiers.
        report["status"]="blocked";report["error_type"]=type(e).__name__
        # File/CRS-only stages have no cave details in their expected error messages.
        if report.get("stage") in {"download_dem","download_climate","raster_metadata"}:
            report["error_detail"]=str(e)[:500]
        import traceback
        report["error_frames"]=[{"function":f.name,"line":f.lineno} for f in traceback.extract_tb(e.__traceback__)]
    save();print(json.dumps(report,indent=2,allow_nan=False))
    return 0 if report["status"]=="completed_exploratory" else 2
if __name__=="__main__":sys.exit(main())
