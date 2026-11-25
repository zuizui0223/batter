"""Independent FWS measured GEDI coarse profile validation.
See FWS_MEASURED_PAVD_INDEPENDENT_CONTRACT_V1.md.
Same frozen FWS support and model; real GEDI PAVD replaces GVSM R50.
No raw FWS records, survey positions, or Earthdata credentials in artifacts.
"""
import collections,hashlib,json,logging,math,os,pathlib
import numpy as np,pandas as pd,requests
from scipy.special import expit
from scipy.optimize import minimize
import fws_coarse_profile_diagnostic_v1 as f
logging.disable(logging.CRITICAL)
OUT=pathlib.Path("fws_measured_pavd");OUT.mkdir(exist_ok=True)
R=f.R
R.update(stage="independent 6-km FWS measured GEDI PAVD profile comparison",source_measured_doi="10.3334/ORNLDAAC/2339",status="START",original_SDM_admitted=False,contrast="M minus B; M adds measured PAVD lower fraction; no GVSM in this model")
R["limits"].append("GEDI gridded shot means and different native observation support, not direct volume or individual altitude.")
report=R
K=f.K;CLIM=f.CLIM;LC_COLS=f.LC_COLS
def save():
    def scalar(v):
        if isinstance(v,np.generic):return v.item()
        if isinstance(v,np.ndarray):return v.tolist()
        raise TypeError(type(v).__name__)
    (OUT/"report.json").write_text(json.dumps(R,indent=2,allow_nan=False,default=scalar))
    print("FWS_MEASURED_REPORT="+json.dumps(R,allow_nan=False,default=scalar),flush=True)
def need(ok,label):
    if not ok:raise ValueError(label)

def measured_grid(cells,fs,session):
    import rasterio
    from rasterio.windows import Window
    report.update(doi="10.3334/ORNLDAAC/2339",concept_id="C3043630107-ORNL_CLOUD",period="2019-04-17/2023-03-16",sources={})
    cells=cells[["cell_x","cell_y"]].drop_duplicates().sort_values(["cell_x","cell_y"]).reset_index(drop=True)
    need(len(cells)==241,"frozen candidate cells")
    report["target_grain_m"]=6000
    metrics=[f"pavd-{z}-{z+5}" for z in range(0,80,5)]+["rh-98-a0","pai-a0","cover-a0"]
    response=requests.get("https://cmr.earthdata.nasa.gov/search/granules.json",params={"collection_concept_id":report["concept_id"],"page_size":2000},timeout=45)
    response.raise_for_status()
    entries=response.json()["feed"]["entry"]
    urls={}
    for m in metrics:
        name=f"gediv002_{m}_vf_20190417_20230316_1000m.tif"
        hits=[e for e in entries if e.get("title","").endswith(name)]
        need(len(hits)==1,"CMR inventory "+m)
        e=hits[0]
        links=sorted({l["href"] for l in e.get("links",[]) if l.get("href","").startswith("https://") and l["href"].endswith(".tif") and not l.get("inherited") and "/data#" in l.get("rel","")})
        need(len(links)==1,"CMR data link "+m)
        urls[m]=links[0]
        report["sources"][m]={"cmr_granule_id":e.get("id"),"title":e.get("title")}
    report["candidate_cells"]=len(cells);report["inventory_complete"]=True;save()
    with session.get(urls[metrics[0]],headers={"Range":"bytes=0-16383"},stream=True,timeout=(30,45)) as r:
        report["first_http_status"]=r.status_code
        magic=next(r.iter_content(chunk_size=16384),b"")[:4]
        report["tiff_magic"]=magic in (b"II*\x00",b"MM\x00*",b"II+\x00",b"MM\x00+")
        need(r.status_code==206 and report["tiff_magic"],"authenticated range")
    report["status"]="AUTHENTICATED_TIFF_RANGE_OK";save()
    ref=None;overlaps=None;native=None;values=[];counts=[]
    for m in metrics:
        report["current_metric"]=m;save()
        with rasterio.open(urls[m],opener=fs.open) as s:
            need(s.crs.to_epsg()==6933 and s.transform.a==1000 and s.transform.e==-1000 and s.transform.b==s.transform.d==0 and s.count==8,"native grid")
            g=(s.width,s.height,tuple(s.transform),str(s.crs))
            if ref is None:
                ref=g;overlaps=[];keys=set()
                for x,y in cells.itertuples(index=False,name=None):
                    l,b,r,t=x*6000,y*6000,(x+1)*6000,(y+1)*6000
                    c0=math.floor((l-s.transform.c)/1000);c1=math.ceil((r-s.transform.c)/1000)
                    r0=math.floor((s.transform.f-t)/1000);r1=math.ceil((s.transform.f-b)/1000)
                    q=[]
                    for i in range(r0,r1):
                        for j in range(c0,c1):
                            xl=s.transform.c+1000*j;yt=s.transform.f-1000*i
                            a=max(0,min(r,xl+1000)-max(l,xl))*max(0,min(t,yt)-max(b,yt-1000))/36e6
                            if a>0 and 0<=i<s.height and 0<=j<s.width:q.append(((i,j),a));keys.add((i,j))
                    overlaps.append(q)
                native=sorted(keys);ix={k:i for i,k in enumerate(native)}
                overlaps=[[(ix[k],w) for k,w in q] for q in overlaps]
                report["native_grid"]={"width":s.width,"height":s.height,"transform":list(s.transform),"crs":str(s.crs),"native_pixels":len(native)}
            need(g==ref,"grid mismatch")
            meta=report["sources"][m]
            meta["descriptions"]=list(s.descriptions)
            lookup={}
            for j,desc in enumerate(s.descriptions,1):
                tags=s.tags(j)
                labels={str(x).lower().strip().replace(" ","_") for x in [desc or "",tags.get("name",""),tags.get("long_name",""),tags.get("DESCRIPTION","")]}
                if labels.intersection({"mean","arithmetic_mean"}):lookup["mean"]=j
                if labels.intersection({"countf","shot_count","count","number_of_shots"}):lookup["countf"]=j
            meta["band_lookup"]=lookup;save()
            need(set(lookup)=={"mean","countf"} and len(set(lookup.values()))==2,"unverified band semantics")
            need(all(s.scales[j-1]==1 and s.offsets[j-1]==0 for j in lookup.values()),"scale/offset")
            vi=np.full(len(native),np.nan);co=np.full(len(native),np.nan)
            tiles=collections.defaultdict(list)
            bh,bw=s.block_shapes[lookup["mean"]-1]
            for j,(i,k) in enumerate(native):tiles[i//bh,k//bw].append((j,i,k))
            for _,qs in sorted(tiles.items()):
                i0=min(i for j,i,k in qs);i1=max(i for j,i,k in qs)
                k0=min(k for j,i,k in qs);k1=max(k for j,i,k in qs)
                a=s.read([lookup["mean"],lookup["countf"]],window=Window(k0,i0,k1-k0+1,i1-i0+1),masked=True).astype(float).filled(np.nan)
                for j,i,k in qs:vi[j],co[j]=a[:,i-i0,k-k0]
            good=np.isfinite(vi)&np.isfinite(co)&(vi>=0)&(co>=10)&(np.abs(co-np.rint(co))<1e-5)
            values.append(vi);counts.append(co)
            meta["native_valid_ge10"]=int(good.sum());meta["sample_sha256"]=hashlib.sha256(np.stack([vi,co]).tobytes()).hexdigest()
            print("GEDI_METRIC_COMPLETE",m,int(good.sum()),flush=True)
    vs=np.stack(values,axis=1);cs=np.stack(counts,axis=1)
    native_good=(np.isfinite(vs)&np.isfinite(cs)&(vs>=0)&(cs>=10)&(np.abs(cs-np.rint(cs))<1e-5)).all(1)
    # Preserve full cohort; mask jointly across all 19 layers, not separately.
    result=[]
    for q in overlaps:
        valid=[(i,w) for i,w in q if native_good[i]]
        area=sum(w for i,w in valid)
        a=np.full(len(metrics),np.nan);minc=np.nan
        if area>=.95 and area<=1.000001:
            ix=[i for i,w in valid];w=np.array([w for i,w in valid]);a=w@vs[ix]/area;minc=float(cs[ix].min())
        result.append([*a,area,minc])
    out=cells.join(pd.DataFrame(result,columns=metrics+["joint_valid_area_fraction","minimum_native_shot_count"]))
    total=out[metrics[:16]].sum(axis=1,min_count=16)
    out["PAVD_lower_fraction"]=out[metrics[:2]].sum(axis=1,min_count=2)/total.where(total>0)
    out["PAVD_centroid_m"]=(out[metrics[:16]].to_numpy()@np.arange(2.5,80,5))/total.where(total>0)
    out["gedi_support"]=out["PAVD_lower_fraction"].notna()&out["rh-98-a0"].gt(5)&out["joint_valid_area_fraction"].ge(.95)
    native_good25=native_good&(cs>=25).all(1)
    out["joint_valid_area_fraction_25"]=[sum(w for i,w in q if native_good25[i]) for q in overlaps]
    # Recalculate 25-shot sensitivity covariates on their own shared support;
    # report counts only; no secondary ecological fit.
    sens_support=0
    for q in overlaps:
        v=[(i,w) for i,w in q if native_good25[i]]
        a=sum(w for i,w in v)
        if .95<=a<=1.000001:
            j=[i for i,w in v];w=np.array([w for i,w in v])
            avg=w@vs[j]/a
            sens_support+=int(avg[:16].sum()>0 and avg[16]>5)
    report["gedi_coverage"]={"candidate_cells":len(out),"native_pixels":len(native),"joint_native_ge10":int(native_good.sum()),"joint_native_ge25":int(native_good25.sum()),"eligible_cells_ge10":int(out.gedi_support.sum()),"eligible_cells_ge25":int(sens_support),"native_count_threshold":10,"joint_area_threshold":.95}
    # No per-cell values or observation locations are exported. Hash the
    # deterministic table to support reproducibility of the measured fit.
    report["gedi_cell_table_sha256"]=hashlib.sha256(out.to_csv(index=False).encode()).hexdigest()
    report["status"]="MEASURED_GEDI_GRID_READY";save()
    return out


def fit(ct,z,gb,gr,taxa,u):
    sa,sb,ca,cb,gi=z.T
    blocks=sorted(set(gb),key=lambda b:hashlib.sha256(f"{b[0]},{b[1]}".encode()).hexdigest())
    bm={b:i for i,b in enumerate(blocks)};gbi=np.array([bm[b] for b in gb]);block=gbi[gi]
    routes=np.array(gr);proute=routes[gi];fold=block%5
    A=np.eye(len(taxa))[sa]-np.eye(len(taxa))[sb]
    raw=ct.merge(u,on=K,validate="one_to_one").sort_values("ci")[CLIM+LC_COLS+["RH98","PAI","cover","PAVD_lower_fraction"]].to_numpy(float)
    assert np.isfinite(raw).all();assert len(z)<=200000,("pair memory budget",len(z))
    def wgt(m):
        ng=np.bincount(gi[m],minlength=len(gb));bg=np.bincount(gbi[ng>0],minlength=len(blocks))
        w=1/(ng[gi[m]]*bg[block[m]]*len(np.unique(block[m])))
        assert np.isclose(w.sum(),1);return w
    def obj(p,X,w):
        h=X@p
        return float(w@np.logaddexp(0,-h)+.1*(p@p)),X.T@(-w*expit(-h))+.2*p
    scores=np.full((len(z),2),np.nan);folds=[];skips={}
    for k in range(5):
        te=(fold==k);tr=(fold!=k)&~np.isin(proute,np.unique(proute[te]))
        taxa_train=np.unique(np.r_[sa[tr],sb[tr]])
        te=te&np.isin(sa,taxa_train)&np.isin(sb,taxa_train)
        if tr.sum()<300 or len(taxa_train)<6 or len(np.unique(block[tr]))<6 or len(np.unique(proute[tr]))<8 or te.sum()<10 or len(np.unique(block[te]))<1:
            skips[str(k+1)]={"train_pairs":int(tr.sum()),"train_taxa":len(taxa_train),"train_blocks":len(np.unique(block[tr])),"train_routes":len(np.unique(proute[tr])),"test_pairs":int(te.sum())};continue
        assert not set(proute[tr])&set(proute[te]) and not set(block[tr])&set(block[te])
        use=np.unique(np.r_[ca[tr],cb[tr]]);sd=raw[use].std(0);zero=sd<=1e-12;sd[zero]=1
        D=(raw[ca]-raw[cb])/sd;D[:,zero]=0
        base=(A[:,:,None]*D[:,:-1][:,None,:]).reshape(len(z),-1);profile=np.column_stack([base,A*D[:,-1,None]])
        out=[]
        for X in (base,profile):
            Xtr=np.ascontiguousarray(X[tr]);w=wgt(tr)
            f=minimize(obj,np.zeros(X.shape[1]),args=(Xtr,w),method="L-BFGS-B",jac=True,options={"maxiter":400,"ftol":1e-12,"gtol":1e-7})
            assert f.success or np.max(np.abs(f.jac))<1e-6
            out.append(-np.logaddexp(0,-X[te]@f.x))
        scores[te]=np.stack(out,axis=1)
        folds.append({"fold":k+1,"train_pairs":int(tr.sum()),"test_pairs":int(te.sum()),"train_routes":len(np.unique(proute[tr])),"test_routes":len(np.unique(proute[te])),"test_blocks":len(np.unique(block[te])),"scores":dict(zip(["B","M"],map(float,wgt(te)@scores[te])))})
    ok=np.isfinite(scores).all(1);scored_blocks=len(np.unique(block[ok]))
    R["evaluation_support"]={"scored_comparisons":int(ok.sum()),"fraction":float(ok.mean()),"scored_blocks":scored_blocks,"scored_taxa":len(np.unique(np.r_[sa[ok],sb[ok]])),"scored_routes":len(np.unique(proute[ok])),"completed_folds":len(folds),"folds":folds,"skips":skips}
    if len(folds)<3 or scored_blocks<8:R["status"]="STOP_INSUFFICIENT_DISJOINT_SCORED_SUPPORT";save();return
    w=wgt(ok);mean=w@scores[ok];delta=scores[ok,1]-scores[ok,0]
    den=np.bincount(block[ok],weights=w,minlength=len(blocks));live=den>0
    bg=np.bincount(block[ok],weights=w*delta,minlength=len(blocks))[live]/den[live]
    boot=np.random.default_rng(20261126).choice(bg,size=(2000,len(bg)),replace=True).mean(1)
    R["result"]={"neutral":-math.log(2),"baseline":float(mean[0]),"profile":float(mean[1]),"profile_gain":float(mean[1]-mean[0]),"profile_minus_neutral":float(mean[1]+math.log(2)),"positive_blocks":int((bg>0).sum()),"conditional_block_bootstrap_95":np.quantile(boot,[.025,.975]).tolist(),"block_quantiles":np.quantile(bg,[.05,.5,.95]).tolist()}
    R["status"]="COMPLETE_DESCRIPTIVE_INDEPENDENT_MEASURED_PAVD_DIAGNOSTIC";save()

def main():
    f.save=save
    d=f.source_rows()
    assert len(d)==8816 and len(d[K].drop_duplicates())==241
    _,_,_,_,_,s=f.labels_and_pairs(d);R["pre_environment_comparison_support"]=s;save()
    assert f.passes(s) and s["comparisons"]==10480 and s["comparison_blocks"]==24
    if not os.getenv("EARTHDATA_TOKEN"):
        R["status"]="STOP_NO_EARTHDATA_SECRET";save();return
    import earthaccess
    auth=earthaccess.login(strategy="environment",persist=False)
    need(auth.authenticated,"earthaccess session")
    fs=earthaccess.get_fsspec_https_session()
    session=earthaccess.get_requests_https_session()
    u=measured_grid(d[K],fs,session)
    u=u[u.gedi_support].copy()
    d1=d.merge(u[K],on=K,validate="many_to_one")
    _,_,_,_,_,s=f.labels_and_pairs(d1);R["measured_only_comparison_support"]=s;save()
    if not f.passes(s):
        R["status"]="STOP_INSUFFICIENT_MEASURED_SUPPORT";save();return
    # Use precisely the frozen LC100 and climate source methods at the
    # measured-support cells, before any biological score is inspected.
    lc,la=f.landcover(u)
    forest=np.isfinite(lc).all(1)&(lc[:,:4].sum(1)>=.30)
    R["forest_support_after_measured"]={"landcover_valid":int(np.isfinite(lc).all(1).sum()),"forest_cells":int(forest.sum())}
    for j,k in enumerate(LC_COLS):u[k]=lc[:,j]
    u=u[forest].copy()
    d2=d1.merge(u[K],on=K,validate="many_to_one")
    _,_,_,_,_,s=f.labels_and_pairs(d2);R["measured_and_forest_comparison_support"]=s;save()
    if not f.passes(s):
        R["status"]="STOP_INSUFFICIENT_MEASURED_FOREST_SUPPORT";save();return
    cl=[(k,f"https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_{k}_1981-2010_V.2.1.tif",.1,-273.15 if k in {"bio1","bio5","bio6"} else 0,None,True) for k in CLIM]
    c,ca=f.stack_to_cells(u,cl,"climate")
    for j,k in enumerate(CLIM):u[k]=c[:,j]
    u=u[np.isfinite(c).all(1)].copy()
    u=u.rename(columns={"rh-98-a0":"RH98","pai-a0":"PAI","cover-a0":"cover"})
    R["common_environment_cells"]=len(u);save()
    d3=d2.merge(u[K],on=K,validate="many_to_one")
    ct,z,gb,gr,taxa,s=f.labels_and_pairs(d3);R["forest_comparison_support"]=s;save()
    if not f.passes(s):
        R["status"]="STOP_INSUFFICIENT_COMMON_SUPPORT";save();return
    fit(ct,z,gb,gr,taxa,u)
if __name__=="__main__":
    try:main()
    except Exception as e:
        # Never log signed URLs or raw exception text from authenticated I/O.
        R.update(status="INCOMPLETE",error_type=type(e).__name__);save();raise SystemExit(1)
    finally:f.src.P.unlink(missing_ok=True)
