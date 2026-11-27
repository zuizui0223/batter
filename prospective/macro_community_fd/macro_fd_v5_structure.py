"""V5 near-global measured structure, climate and potential-assemblage FD. Aggregate output only."""
import collections as C,hashlib,io,json,logging,math,os,zipfile
from pathlib import Path
import numpy as np
import requests,rasterio
from scipy.sparse import csr_matrix
from pyproj import CRS,Transformer
from macro_fd_v4_global_ranges import wing,read_ranges,metric,REGIONS
from macro_fd_v2_geography import expected_distance

GEDI=("rh-98-a0","cover-a0","pai-a0","pavd-bot-frac")
BIO=(1,4,5,6,12,15)
OUT=Path("macro_fd_v5_result.json")
YNAME=["flight_genus_residual","flight_MPD","size_genus_residual","size_MPD","CWM_AR_z","CWM_log_WL_z"]
FEATURES=["log_range_richness","log_matched_richness","trait_coverage","abs_lat"]+["bio"+str(i) for i in BIO]+["log1p_RH98","cover","log1p_PAI","GEDI_area_support","bottom_half_PAVD_fraction"]
logging.disable(logging.CRITICAL)

def save(out):
    OUT.write_text(json.dumps(out,indent=2,allow_nan=False)+"\n")
    print("V5_STAGE="+out["status"],flush=True)
def download(session,url,path,limit):
    n=0;h=hashlib.sha256()
    with session.get(url,stream=True,timeout=(25,90)) as r:
        if r.status_code!=200:raise RuntimeError("source HTTP "+str(r.status_code))
        size=r.headers.get("Content-Length")
        if size and int(size)>limit:raise ValueError("declared source size limit")
        with path.open("wb") as f:
            for b in r.iter_content(1024*1024):
                if not b:continue
                n+=len(b)
                if n>limit:raise ValueError("stream source size limit")
                h.update(b);f.write(b)
        if size and not r.headers.get("Content-Encoding"):assert n==int(size)
    return {"bytes":n,"sha256":h.hexdigest()}

def axis_overlap(src,dst):
    src=np.asarray(src,float);dst=np.asarray(dst,float)
    assert np.isfinite(src).all() and np.isfinite(dst).all() and np.all(np.diff(src)>0) and np.all(np.diff(dst)>0)
    rows=[];cols=[];v=[]
    for j,(a,b) in enumerate(zip(dst[:-1],dst[1:])):
        lo=max(0,int(np.searchsorted(src,a,side="right")-1))
        hi=min(len(src)-1,int(np.searchsorted(src,b,side="left")))
        for i in range(lo,hi):
            w=max(0.,min(b,src[i+1])-max(a,src[i]))
            if w>0:rows.append(j);cols.append(i);v.append(w)
    return csr_matrix((v,(rows,cols)),shape=(len(dst)-1,len(src)-1))

def edges(t,shape):
    assert t.a>0 and t.e<0 and abs(t.b)<1e-9 and abs(t.d)<1e-9
    return t.c+np.arange(shape[1]+1)*t.a,(t.f+np.arange(shape[0]+1)*t.e)[::-1]

def aggregate(arr,valid,sx,sy,tx,ty):
    assert all(a.shape==valid.shape for a in arr)
    wx=axis_overlap(sx,tx);wy=axis_overlap(sy,ty)
    def area(a):
        return (wx@(wy@a[::-1].astype(float)).T).T[::-1]
    den=area(valid);total=np.outer(np.diff(ty)[::-1],np.diff(tx))
    frac=den/total
    assert np.isfinite(frac).all() and np.min(frac)>=-1e-9 and np.max(frac)<=1+1e-8
    val=[np.divide(area(np.where(valid,a,0.)),den,out=np.full_like(den,np.nan),where=den>0) for a in arr]
    return np.stack(val,axis=-1),np.clip(frac,0,1)

def check_overlap():
    a=np.array([[1.,2.],[3.,4.]])
    v,f=aggregate([a],np.ones_like(a,bool),[0,1,2],[0,1,2],[0,2],[0,2])
    assert np.allclose(v,2.5) and np.allclose(f,1)
    v,f=aggregate([a],np.array([[1,0],[0,0]],bool),[0,1,2],[0,1,2],[0,2],[0,2])
    assert np.allclose(v,1.) and np.allclose(f,.25)

def climate(out,tx,ty):
    p=Path("wc_bio10m.zip")
    receipt=download(requests,"https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_10m_bio.zip",p,100*1024**2)
    arrays=[];ref=None;receipt["members"]={}
    with zipfile.ZipFile(p) as z:
        assert sum(i.file_size for i in z.infolist())<400*1024**2 and z.testzip() is None
        for i in BIO:
            name="wc2.1_10m_bio_"+str(i)+".tif"
            f=[x for x in z.infolist() if Path(x.filename).name==name];assert len(f)==1
            b=z.read(f[0]);receipt["members"][name]=hashlib.sha256(b).hexdigest()
            with rasterio.MemoryFile(b) as mf:
                with mf.open() as s:
                    assert s.count==1 and s.crs.to_epsg()==4326
                    assert abs(s.transform.a-1/6)<1e-8 and abs(s.transform.e+1/6)<1e-8 and s.scales[0]==1 and s.offsets[0]==0
                    grid=(s.shape,s.transform,s.crs)
                    if ref is None:ref=grid
                    assert grid==ref
                    a=s.read(1,masked=True).astype(float).filled(np.nan)
                    arrays.append(a)
    sx,sy=edges(ref[1],ref[0])
    pj=Transformer.from_crs(4326,6933,always_xy=True)
    sx=np.asarray(pj.transform(sx,np.zeros_like(sx))[0]);sy=np.asarray(pj.transform(np.zeros_like(sy),sy)[1])
    valid=np.isfinite(arrays).all(0)
    valid&=(arrays[0]>=-70)&(arrays[0]<=65)&(arrays[1]>=0)&(arrays[2]>=-70)&(arrays[2]<=80)&(arrays[3]>=-100)&(arrays[3]<=65)&(arrays[4]>=0)&(arrays[5]>=0)
    valid&=arrays[2]>=arrays[3]
    values,frac=aggregate(arrays,valid,sx,sy,tx,ty)
    receipt["native_shape"]=list(ref[0]);receipt["common_valid_pixels"]=int(valid.sum());receipt["range_cells_ge50pct"]=int((frac>=.5).sum())
    out["climate"]=receipt
    p.unlink()
    return values.reshape(-1,len(BIO)),frac.ravel()

def gedi(out,tx,ty):
    if not os.getenv("EARTHDATA_TOKEN"):raise RuntimeError("existing Earthdata credential unavailable")
    import earthaccess
    auth=earthaccess.login(strategy="environment",persist=False)
    if not auth.authenticated:raise RuntimeError("Earthdata session not authenticated")
    session=earthaccess.get_requests_https_session()
    rr=requests.get("https://cmr.earthdata.nasa.gov/search/granules.json",params={"collection_concept_id":"C3043630107-ORNL_CLOUD","page_size":2000},timeout=45)
    rr.raise_for_status();entries=rr.json()["feed"]["entry"]
    out["GEDI"]={"doi":"10.3334/ORNLDAAC/2339","metrics":{}}
    arr=[];valid=[];ref=None
    for m in GEDI:
        name=f"gediv002_{m}_vf_20190417_20230316_12000m.tif"
        hit=[a for a in entries if a.get("title","").endswith(name)]
        if len(hit)!=1:
            out["GEDI"]["inventory_match"]={"metric":m,"n":len(hit),"related_titles":[a.get("title","") for a in entries if "12000m" in a.get("title","") and ("bot" in a.get("title","") or m in a.get("title",""))][:12]}
            raise ValueError("CMR exact metric not unique")
        e=hit[0];urls=sorted({v["href"] for v in e.get("links",[]) if v.get("href","").startswith("https://") and v["href"].endswith(".tif") and not v.get("inherited") and "/data#" in v.get("rel","")})
        assert len(urls)==1
        out["status"]="GEDI_DOWNLOAD_"+m;save(out)
        p=Path(name);receipt=download(session,urls[0],p,200*1024**2)
        receipt.update(granule_id=e.get("id"),title=e.get("title"));out["GEDI"]["metrics"][m]=receipt
        with rasterio.open(p) as s:
            assert s.crs.to_epsg()==6933 and s.shape==(965,2881) and s.transform.a==12000 and s.transform.e==-12000 and s.count==8
            grid=(s.shape,s.transform,s.crs)
            if ref is None:ref=grid
            assert grid==ref
            lookup={}
            for j,desc in enumerate(s.descriptions,1):
                tags=s.tags(j);labels={str(x).lower().strip().replace(" ","_") for x in [desc or "",tags.get("name",""),tags.get("long_name",""),tags.get("DESCRIPTION","")]}
                if labels&{"mean","arithmetic_mean"}:lookup["mean"]=j
                if labels&{"countf","shot_count","count","number_of_shots"}:lookup["count"]=j
            receipt["descriptions"]=list(s.descriptions);receipt["band_lookup"]=lookup
            assert set(lookup)=={"mean","count"} and len(set(lookup.values()))==2
            assert all(s.scales[j-1]==1 and s.offsets[j-1]==0 for j in lookup.values())
            a,c=s.read([lookup["mean"],lookup["count"]],masked=True).astype(float).filled(np.nan)
            g=np.isfinite(a)&np.isfinite(c)&(a>=0)&(c>=10)&(abs(c-np.rint(c))<1e-5)
            if m in ("cover-a0","pavd-bot-frac"):g&=a<=1
            arr.append(a);valid.append(g);receipt["native_valid"]=int(g.sum())
        p.unlink()
    g=np.logical_and.reduce(valid)
    sx,sy=edges(ref[1],ref[0]);v,f=aggregate(arr,g,sx,sy,tx,ty)
    out["GEDI"].update(common_native_pixels=int(g.sum()),native_shape=list(ref[0]),range_cells_ge50pct=int((f>=.5).sum()))
    return v.reshape(-1,len(GEDI)),f.ravel()

def weights(reg,block,mask):
    ans=np.zeros(len(reg));idx=np.flatnonzero(mask);rr=sorted(set(reg[idx]))
    for r in rr:
        groups=C.defaultdict(list)
        for i in idx[reg[idx]==r]:groups[int(block[i])].append(i)
        for v in groups.values():ans[v]=1/(len(rr)*len(groups)*len(v))
    assert abs(ans.sum()-1)<1e-10
    return ans

def fit(X,Y,reg,block,tr,te):
    w=weights(reg,block,tr)[tr];x=X[tr];y=Y[tr]
    mu=w@x;sd=np.sqrt(w@((x-mu)**2));active=sd>1e-12;sd[~active]=1.
    z=(x-mu)/sd;zt=(X[te]-mu)/sd;z[:,~active]=0;zt[:,~active]=0
    ym=w@y;results=[np.repeat(ym[None,:],te.sum(),axis=0)]
    for n in (X.shape[1]-1,X.shape[1]):
        a=z[:,:n];b=zt[:,:n];coef=np.linalg.solve(a.T@(w[:,None]*a)+.1*np.eye(n),a.T@(w[:,None]*(y-ym)))
        grad=a.T@(w[:,None]*(a@coef-(y-ym)))+.1*coef
        assert np.max(abs(grad))<1e-8
        results.append(ym+b@coef)
    return np.stack([(a-Y[te])**2 for a in results],axis=1)

def score(X,Y,reg,rc,grain,transfer=False):
    keys=[tuple(v//grain) for v in rc];unique=sorted(set(keys),key=lambda b:hashlib.sha256(str(b).encode()).hexdigest())
    idx={v:i for i,v in enumerate(unique)};block=np.array([idx[k] for k in keys])
    split=reg if transfer else block%5
    folds=sorted(set(split));sc=np.full((len(Y),3,Y.shape[1]),np.nan);res=[]
    for k in folds:
        te=split==k;tr=~te
        if len(set(block[te]))<5 or len(set(reg[tr]))<(3 if transfer else 4) or (not transfer and set(reg[tr])!=set(reg)):
            return {"status":"insufficient_fold_support","grain":grain,"failed_fold":str(k),"train_regions":len(set(reg[tr])),"test_blocks":len(set(block[te]))}
        if not transfer:assert not set(block[te])&set(block[tr])
        sc[te]=fit(X,Y,reg,block,tr,te)
        v=np.einsum("i,imk->mk",weights(reg,block,te)[te],sc[te])
        res.append({"fold":str(k),"n":int(te.sum()),"blocks":len(set(block[te])),"mse":v.tolist(),"V_B":(v[1]-v[2]).tolist(),"V_N":(v[0]-v[2]).tolist()})
    assert np.isfinite(sc).all()
    w=weights(reg,block,np.ones(len(Y),bool));mean=np.einsum("i,imk->mk",w,sc)
    groups=C.defaultdict(list)
    for i,(r,b) in enumerate(zip(reg,block)):groups[r,int(b)].append(i)
    bd=np.array([np.mean(sc[v,1]-sc[v,2],axis=0) for v in groups.values()])
    bw=np.array([w[v].sum() for v in groups.values()])
    total=bw@bd;om=(total-bw[:,None]*bd)/(1-bw[:,None])
    assert np.allclose(total,mean[1]-mean[2])
    return {"status":"scored","n":len(Y),"blocks":len(unique),"region_blocks":len(groups),"mse":dict(zip(["N","B","V"],mean.tolist())),"V_B":total.tolist(),"B_N":(mean[0]-mean[1]).tolist(),"V_N":(mean[0]-mean[2]).tolist(),"positive_region_blocks":(bd>0).sum(0).tolist(),"delete_one_region_block_range":[om.min(0).tolist(),om.max(0).tolist()],"positive_folds":sum(x["V_B"][0]>0 for x in res),"folds":res}

def main():
    out={"stage":"near-global potential range assemblage FD and measured vegetation","status":"START","response_order":YNAME,"features":FEATURES}
    try:
        check_overlap();w=wing(out);names,X,shape,crs,T=read_ranges(out)
        matched=[i for i,n in enumerate(names) if n in w.index];assert len(names)==1141 and len(matched)==264
        nm=[names[i] for i in matched];Z,D=metric(w.loc[nm,["AR","WL_N_m2","mass_g_physical"]].to_numpy(float))
        gs=C.defaultdict(list)
        for j,n in enumerate(nm):gs[n.split("_")[0]].append(j)
        E=expected_distance(D,list(gs.values()))
        richness=X.sum(0);mt=X[matched].sum(0);cov=np.divide(mt,richness,out=np.zeros_like(mt,float),where=richness>0);eligible=(mt>=5)&(cov>=.20)
        assert int(eligible.sum())==9310
        rc=np.array(np.unravel_index(np.arange(richness.size),shape)).T;tx,ty=edges(T,shape)
        pj=Transformer.from_crs(crs,4326,always_xy=True)
        lon,lat=pj.transform(T.c+(rc[:,1]+.5)*T.a,T.f+(rc[:,0]+.5)*T.e)
        lat0=pj.transform(np.zeros(len(rc)),T.f+rc[:,0]*T.e)[1];lat1=pj.transform(np.zeros(len(rc)),T.f+(rc[:,0]+1)*T.e)[1]
        domain=(np.maximum(lat0,lat1)<=51.6)&(np.minimum(lat0,lat1)>=-51.6)
        reg=np.full(len(rc),"other",dtype="U24")
        for name,(l,h,b,t) in REGIONS.items():
            q=(lon>=l)&(lon<=h)&(lat>=b)&(lat<t);assert np.all(reg[q]=="other");reg[q]=name
        out["range_replay"]={"positive_species":len(names),"matched_species":len(matched),"eligible_cells":int(eligible.sum()),"eligible_whole_GEDI_latitude":int((eligible&domain).sum())}
        out["status"]="CLIMATE_DOWNLOAD";save(out)
        clim,climcov=climate(out,tx,ty);out["status"]="CLIMATE_COMPLETE";save(out)
        veg,vegcov=gedi(out,tx,ty)
        cl=climcov>=.5;ve=vegcov>=.5;woody=(veg[:,0]>5)&(veg[:,1]>=.3)
        cohort=eligible&domain&cl&ve&woody&np.isfinite(clim).all(1)&np.isfinite(veg).all(1)
        out["coverage_by_region"]={};use=[]
        for name in REGIONS:
            r=reg==name;c=cohort&r;nb=len({tuple(a//5) for a in rc[c]})
            s={"V4_eligible":int((eligible&r).sum()),"GEDI_latitude":int((eligible&r&domain).sum()),"climate_ge50":int((eligible&r&domain&cl).sum()),"joint_GEDI_ge50":int((eligible&r&domain&cl&ve).sum()),"woody_complete":int(c.sum()),"blocks_5":nb,"median_GEDI_coverage":float(np.median(vegcov[c])) if c.any() else None,"median_trait_coverage":float(np.median(cov[c])) if c.any() else None,"admitted":bool(c.sum()>=100 and nb>=10)}
            out["coverage_by_region"][name]=s
            if s["admitted"]:use.append(name)
        keep=cohort&np.isin(reg,use);out["analysis_cells"]=int(keep.sum());out["regions_admitted"]=use
        if keep.sum()<1000 or len(use)<4:
            out["status"]="INSUFFICIENT_MACRO_SUPPORT";save(out);return
        p=X[matched][:,keep].T.astype(float);p/=p.sum(1,keepdims=True);den=1-(p*p).sum(1)
        def mpd(d):return np.sum((p@d)*p,axis=1)/den
        f=mpd(D[:,:,1]);s=mpd(D[:,:,2]);ef=mpd(E[:,:,1]);es=mpd(E[:,:,2]);cwm=p@Z
        Y=np.c_[f-ef,f,s-es,s,cwm[:,:2]]
        X0=np.c_[np.log(richness[keep]),np.log(mt[keep]),cov[keep],np.abs(lat[keep]),clim[keep],np.log1p(veg[keep,0]),veg[keep,1],np.log1p(veg[keep,2]),vegcov[keep],veg[keep,3]]
        assert X0.shape[1]==len(FEATURES) and Y.shape[1]==len(YNAME) and np.isfinite(X0).all() and np.isfinite(Y).all()
        out["structure_predictors"]={"bottom_fraction_range":[float(X0[:,-1].min()),float(X0[:,-1].max())],"bottom_fraction_correlation_with_base":np.corrcoef(X0,rowvar=False)[-1,:-1].tolist()}
        out["tests"]={}
        for g in (5,10):
            out["tests"]["spatial_"+str(g)]=score(X0,Y,reg[keep],rc[keep],g)
        out["tests"]["region_transfer"]=score(X0,Y,reg[keep],rc[keep],5,True)
        a,b,c=[out["tests"][v] for v in ("spatial_5","spatial_10","region_transfer")]
        out["primary_screen"]=bool(all(v["status"]=="scored" and v["V_B"][0]>0 and v["V_N"][0]>0 and v["positive_region_blocks"][0]/v["region_blocks"]>=.6 and v["positive_folds"]>=4 for v in [a,b]) and c["status"]=="scored" and c["positive_folds"]>=4 and c["V_N"][0]>0)
        out["status"]="COMPLETE"
    except Exception as exc:
        out["last_status"]=out["status"];out["status"]="STOP";out["error_type"]=type(exc).__name__
        # Deliberately omit exception strings: remote exceptions may include auth-bearing URLs.
    save(out)
    print("GLOBAL_V5_REPORT="+json.dumps(out,allow_nan=False),flush=True)
if __name__=="__main__":main()
