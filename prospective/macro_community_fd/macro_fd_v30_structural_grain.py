"""Adjusted strict provider/block sensitivity, original pair construction from blob 1ca160c5a1fe179e2f721ec3f4753a28a05d7e59."""
import hashlib,itertools,json,pathlib,collections,math
import numpy as np
import pandas as pd
from scipy.special import expit
from scipy.optimize import minimize

SRC=pathlib.Path("pilot/species_cell_source_year_environment.csv.gz")
OUT=pathlib.Path("macro_fd_v30_result.json")
PIN="5bd65cd8c56bac84c033a4972064622c172554a676d198868ef0776c49a2786b"
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==PIN
d=pd.read_csv(SRC,dtype={"species_key":str,"dataset_key":str,"year":str,"license":str},keep_default_na=False,low_memory=False)
K=["cell_x","cell_y"];SK=["species_key",*K];G=["dataset_key","year","bx","by"]
roster=sorted(["5218524","5218507","2432439","5218522","2432359","5218471","5218464","2432389","2432416","2432655","2432614","2432470","9754263","2432564"])
baseline=["bio1","bio4","bio5","bio6","bio12","bio15",*[f"worldcover_class_{i}_fraction" for i in [10,20,30,40,50]],"GVSM_area_mean_RH98_m"]
features=baseline+["R50"]
assert int(d.records.sum())==20784 and len(d[SK].drop_duplicates())==4854
f=d.loc[d.forest_profile_support.astype(str).str.lower().eq("true")].copy()
assert int(f.records.sum())==8811 and len(f[SK].drop_duplicates())==2977
geo=[]
for k,v in f[SK].drop_duplicates().groupby("species_key"):
    b=v.groupby([v.cell_x//200,v.cell_y//200]).size()
    if len(v)>=30 and b.ge(5).sum()>=4:geo.append(k)
assert sorted(geo)==roster
f=f[f.species_key.isin(roster)&f.dataset_key.ne("")&f.year.str.fullmatch(r"20[0-9]{2}")].copy()
assert (f.bx==f.cell_x//200).all() and (f.by==f.cell_y//200).all()
f[features+["AR"]]=f[features+["AR"]].apply(pd.to_numeric,errors="raise")
assert np.isfinite(f[features+["AR"]].to_numpy()).all()
ct=f[K+features].drop_duplicates().sort_values(K).reset_index(drop=True)
assert not ct.duplicated(K).any()
ar=f[["species_key","AR"]].drop_duplicates().set_index("species_key").loc[roster,"AR"].to_numpy(float)
assert len(ar)==14 and np.std(ar)>0
az=(ar-ar.mean())/ar.std()
# Residual parameterization: species deviations orthogonal to constant and trait.
nsp=len(roster);P=np.eye(nsp)-np.ones((nsp,nsp))/nsp-np.outer(az,az)/nsp
assert np.max(np.abs(P@az))<1e-10 and np.max(np.abs(P@P-P))<1e-10
idx={k:i for i,k in enumerate(roster)}
ct["cell_index"]=np.arange(len(ct))
f=f.merge(ct[K+["cell_index"]],on=K,validate="many_to_one")
f=f.drop_duplicates(["species_key","cell_index",*G]).sort_values([*G,"species_key","cell_index"])
rng=np.random.default_rng(20261125)
comparisons=[];groups=[];gblock=[];gsource=[];sizes=[]
for key,part in f.groupby(G,sort=True):
    by={s:np.sort(v.cell_index.unique()) for s,v in part.groupby("species_key",sort=True)}
    for s,t in itertools.combinations(sorted(by),2):
        a,b=by[s],by[t]
        ca=np.repeat(a,len(b));cb=np.tile(b,len(a))
        keep=ca!=cb;ca,cb=ca[keep],cb[keep]
        if len(ca)==0:continue
        if len(ca)>128:
            sel=np.sort(rng.choice(len(ca),128,replace=False));ca,cb=ca[sel],cb[sel]
        g=len(groups);block=(int(key[2]),int(key[3]));groups.append(g);gblock.append(block);gsource.append(str(key[0]));sizes.append(len(ca))
        comparisons.extend((idx[s],idx[t],int(x),int(y),g) for x,y in zip(ca,cb))
assert comparisons
z=np.asarray(comparisons,dtype=int);sa,sb,ca,cb,gi=z.T
# Anonymize output block order with fixed hash; no geographic labels saved.
blocks=sorted(set(gblock),key=lambda b:hashlib.sha256(f"{b[0]},{b[1]}".encode()).hexdigest())
bi={b:i for i,b in enumerate(blocks)};gb=np.array([bi[b] for b in gblock]);block=gb[gi]
fold=block%5;ng=len(groups);nb=len(blocks);npair=len(z)
size=np.asarray(sizes);groups_per_block=np.bincount(gb,minlength=nb)
w0=1.0/(groups_per_block[block]*size[gi])
assert np.allclose(np.bincount(block,weights=w0,minlength=nb),1)

# Diagnostic, after original pilot: no new hypothesis or primary S1 admission.
# B2 versus B3 in the original is a full-space reparameterization with different ridge penalty.
# Direct trait-only model is needed for prediction to entirely untrained taxa.
source_names=sorted(set(gsource),key=lambda s:hashlib.sha256(s.encode()).hexdigest())
si={s:i for i,s in enumerate(source_names)}
src_group=np.array([si[s] for s in gsource]);src=src_group[gi];sf=src%5
A=np.eye(nsp)[sa]-np.eye(nsp)[sb];D=A@P;trait=A@az
raw=ct[features].to_numpy(float)
report={"stage":"post-pilot robustness and cold-start diagnostic only","original_source_sha256":PIN,"comparisons":len(z),"blocks":nb,"sources":len(source_names),"species":nsp,"primary_sdm_admitted":False,"warning":"Not independent replication of the original pilot; record label prediction conditional on observed source-year-block cells. B2/B3 same slope span, different shrinkage."}
def weights(mask):
    blockn=np.bincount(block[mask],minlength=nb)
    gn=np.bincount(gi[mask],minlength=ng)
    group_live=gn>0
    perblock=np.bincount(gb[group_live],minlength=nb)
    v=1/(perblock[block[mask]]*gn[gi[mask]])
    return v/np.unique(block[mask]).size

ROOT=pathlib.Path(__file__).resolve().parent.parent/"gedi_trait_macro_sdm"
old=json.loads((ROOT/"OBSERVED_LABEL_TRANSFER_RECEIPT_V1.json").read_text())["source_and_block_transfer"]
receipt=json.loads((ROOT/"BASELINE_LC100_ALTERNATIVE_RECEIPT_V1.json").read_text())
assert receipt["status"]=="LC100_ALTERNATIVE_CHALLENGE_COMPLETE" and all(receipt["audit"]["checks"].values())
assert len(z)==31601 and nb==51 and len(ct)==1796 and nsp==14
terrain=["surface_elev_mean_m","surface_elev_sd_m"]
leaf=["lc100_broadleaf_class_fraction","lc100_needleleaf_class_fraction","lc100_mixed_class_fraction","lc100_other_forest_class_fraction"]
for mode,cols,p in [("terrain",terrain,pathlib.Path("prior_terrain/cell_covariates.csv.gz")),("leaf",leaf,pathlib.Path("prior_alternative/baseline_lc100/cell_covariates.csv.gz"))]:
    assert hashlib.sha256(p.read_bytes()).hexdigest()==receipt["source_reports"][mode]["output_sha256"]
    v=pd.read_csv(p)
    assert len(v)==1796 and not v.duplicated(K).any()
    assert v[mode+"_support"].astype(str).str.lower().eq("true").all()
    ct=ct.merge(v[K+cols],on=K,how="left",validate="one_to_one")
assert ct.cell_index.tolist()==list(range(1796))
raw_names=baseline+["R50"]+terrain+leaf
raw=ct[raw_names].to_numpy(float)
assert np.isfinite(raw).all()

# Original pair and baseline construction above is exactly replayed.
import rasterio
from rasterio.windows import Window,transform
from pyproj import Transformer
from macro_fd_v5_structure import aggregate
GRAINS=(1,10,50,100)
MOD=["N","B","F","C10","C50","C100","C10_scaled","C50_scaled","C100_scaled"]
report.update(stage="continental structural information loss under aggregation",status="START",model_order=MOD,limits=["same European 14-species data, not independent reproduction","fine baseline fixed; only R50 is coarsened","wall-to-wall valid source pixels, not observed cells averaged","predicted return-height quantile ratio, not actual bat height","coarse mask differs from local forest mask","no causal claim or global SDM"])
def save():
    OUT.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print("GLOBAL_V30_REPORT="+json.dumps(report,allow_nan=False),flush=True)
def sha(a):return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
def source():
    pins=json.loads((ROOT/"COMMON_GRID_FOREST_RECEIPT_V1.json").read_text())["source_windows"]
    arr=[];grid=None;report["GVSM_windows"]={}
    for n in (10,25,50,75,90,98):
        k="RH"+str(n);p=pins[k]
        with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",GDAL_HTTP_TIMEOUT="75",GDAL_HTTP_MAX_RETRY="2",CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif"):
            with rasterio.open(p["url"]) as s:
                assert s.crs.to_epsg()==4326 and s.count==1 and s.nodata==32767
                assert list(s.shape)==p["source_shape"] and abs(s.transform.a-.01)<1e-8
                w=Window(*p["window"]);t=transform(w,s.transform);m=s.read(1,window=w,masked=True)
                valid=~np.ma.getmaskarray(m)&np.isfinite(m.data)
                v=np.where(valid,m.data.astype("float32")*.1,np.nan).astype("float32")
                assert list(v.shape)==p["shape"] and np.allclose(list(t),p["transform"],rtol=0,atol=1e-10)
                assert sha(m.data)==p["encoded_bytes_sha256"] and sha(valid)==p["valid_mask_sha256"] and sha(v)==p["converted_array_sha256"]
                if grid is None:grid=t,v.shape
                assert grid==(t,v.shape)
                arr.append(v);report["GVSM_windows"][k]={"encoded_bytes_sha256":sha(m.data),"valid_mask_sha256":sha(valid),"converted_array_sha256":sha(v),"shape":list(v.shape)}
        print("V30_RH_VERIFIED",k,flush=True)
    t,(h,w)=grid;pj=Transformer.from_crs(4326,6933,always_xy=True)
    xx=pj.transform(t.c+np.arange(w+1)*t.a,np.zeros(w+1))[0]
    yy=pj.transform(np.zeros(h+1),t.f+np.arange(h+1)*t.e)[1]
    common=np.isfinite(np.stack(arr)).all(0)
    assert common.sum()==4049610
    # Exact native source-window overlap, no interpolation from occurrence cells.
    return np.stack(arr),common,xx,yy
def grained(arr,valid,xx,yy,g):
    keys=ct[K].to_numpy(int)//g
    u,inv=np.unique(keys,axis=0,return_inverse=True)
    vals=np.full((len(u),6),np.nan);frac=np.zeros(len(u))
    for i,(cx,cy) in enumerate(u):
        x0,x1=cx*g*1000,(cx+1)*g*1000;y0,y1=cy*g*1000,(cy+1)*g*1000
        if x0<xx[0] or x1>xx[-1] or y0<yy[-1] or y1>yy[0]:continue
        c0=max(0,np.searchsorted(xx,x0,side="right")-1);c1=min(len(xx)-1,np.searchsorted(xx,x1,side="left"))
        r0=max(0,np.searchsorted(-yy,-y1,side="right")-1);r1=min(len(yy)-1,np.searchsorted(-yy,-y0,side="left"))
        if r0>=r1 or c0>=c1:continue
        wx=np.maximum(0,np.minimum(x1,xx[c0+1:c1+1])-np.maximum(x0,xx[c0:c1]))
        wy=np.maximum(0,np.minimum(y1,yy[r0:r1])-np.maximum(y0,yy[r0+1:r1+1]))
        area=wy[:,None]*wx[None,:]
        mask=valid[r0:r1,c0:c1]&(area>0);W=area[mask]
        frac[i]=W.sum()/(g*1000)**2
        if frac[i]>=(.95 if g==1 else .5) and frac[i]<=1.000001:
            vals[i]=np.sum(arr[:,r0:r1,c0:c1][:,mask].astype(float)*W[None,:],axis=1)/W.sum()
    ok=np.isfinite(vals).all(1)&(np.diff(vals,axis=1)>=-1e-8).all(1)&(vals[:,-1]>5)
    r=np.divide(vals[:,2],vals[:,-1],out=np.full(len(u),np.nan),where=ok)
    out=r[inv]
    report["grain_support"][str(g)]={"coarse_cells":len(u),"admitted_coarse_cells":int(ok.sum()),"candidate_1km_cells":int(np.isfinite(out).sum()),"joint_valid_fraction_quantiles":np.quantile(frac,[0,.25,.5,.75,1]).tolist(),"ratio_quantiles":np.quantile(r[ok],[0,.25,.5,.75,1]).tolist() if ok.any() else None}
    return out,vals[inv]
def objective(b,X,w):
    h=X@b
    return float(w@np.logaddexp(0,-h)+.1*(b@b)),X.T@(-w*expit(-h))+.2*b
def fit(train,test,rs,full=False):
    used=np.unique(np.r_[ca[train],cb[train]])
    bn=baseline+terrain+leaf
    cols=[raw_names.index(k) for k in bn]
    x=raw[:,cols];mu=x[used].mean(0);sd=x[used].std(0);zero=sd<=1e-12;sd[zero]=1
    X=(x-mu)/sd;X[:,zero]=0;v=X[ca]-X[cb]
    B=np.column_stack([(D[:,:,None]*v[:,None,:]).reshape(len(z),-1),trait[:,None]*v])
    s=rs[0][used].std();assert s>0
    mats=[B]
    for j,r in enumerate(rs):
        mats.append(np.column_stack([B,A*((r[ca]-r[cb])/s)[:,None]]))
    if not full:
        for r in rs[1:]:
            scale=r[used].std()
            assert scale>1e-12
            mats.append(np.column_stack([B,A*((r[ca]-r[cb])/scale)[:,None]]))
    ww=weights(train);assert np.isclose(ww.sum(),1)
    scores=[np.full(test.sum(),-math.log(2))]
    for M in mats:
        a=np.ascontiguousarray(M[train]);b=np.ascontiguousarray(M[test]);assert np.isfinite(a).all() and np.isfinite(b).all()
        sol=minimize(objective,np.zeros(a.shape[1]),args=(a,ww),method="L-BFGS-B",jac=True,options={"maxiter":400,"ftol":1e-12,"gtol":1e-7})
        assert sol.success
        scores.append(-np.logaddexp(0,-b@sol.x))
    return np.stack(scores,axis=1)
def summary(sc,fs,kind):
    valid=np.isfinite(sc).all(1);ww=weights(valid);m=ww@sc[valid]
    bw=np.bincount(block[valid],weights=ww,minlength=nb);live=bw>0
    bs=np.column_stack([np.bincount(block[valid],weights=ww*sc[valid,j],minlength=nb) for j in range(len(MOD))])[live]/bw[live,None]
    assert np.allclose(bs.mean(0),m)
    contrasts={}
    for name,a,b in [("fine_minus_baseline","F","B"),("fine_minus_neutral","F","N"),("fine_minus_C100","F","C100"),("fine_minus_C100_scaled","F","C100_scaled"),("C10_minus_B","C10","B"),("C50_minus_B","C50","B"),("C100_minus_B","C100","B")]:
        i,j=MOD.index(a),MOD.index(b);v=bs[:,i]-bs[:,j]
        g=float(v.mean());loo=(v.sum()-v)/(len(v)-1)
        ff=[x["scores"][a]-x["scores"][b] for x in fs]
        contrasts[name]={"gain":g,"positive_blocks":int((v>0).sum()),"positive_folds":sum(q>0 for q in ff),"fold_gains":ff,"delete_one_block_range":[float(loo.min()),float(loo.max())]}
    a=contrasts["fine_minus_C100"];p=bool(contrasts["fine_minus_baseline"]["gain"]>0 and contrasts["fine_minus_neutral"]["gain"]>0 and a["gain"]>0 and a["positive_blocks"]/len(bs)>=.6 and a["positive_folds"]>=math.ceil(.8*len(fs)) and a["delete_one_block_range"][0]>0 and contrasts["fine_minus_C100_scaled"]["gain"]>0)
    return {"status":"scored","comparisons":int(valid.sum()),"blocks":int(live.sum()),"folds":fs,"scores":dict(zip(MOD,m.tolist())),"contrasts":contrasts,"primary_pass":p}
try:
    assert len(z)==31601 and nb==51 and len(ct)==1796 and nsp==14
    expected={v["fold"]:v for v in old["folds"]};assert len(expected)==15
    strictref=np.zeros(len(z),bool);rep=[]
    for k in range(5):
        for h in range(5):
            label=f"block{k+1}_source{h+1}"
            if label not in expected:continue
            te=(fold==k)&(sf==h);tr=(fold!=k)&(sf!=h)
            assert not set(block[tr])&set(block[te]) and not set(src[tr])&set(src[te])
            assert int(te.sum())==expected[label]["comparisons"]
            strictref|=te
            # Whole-support replay of original adjusted model.
            a=fit(tr,te,[raw[:,raw_names.index("R50")]],True)
            rep.append((te,a))
    assert strictref.sum()==29247
    sc=np.full((len(z),3),np.nan)
    for te,a in rep:sc[te]=a
    check=weights(strictref)@sc[strictref]
    ref=json.loads((ROOT/"ADJUSTED_SOURCE_BLOCK_HOLDOUT_RECEIPT_V1.json").read_text())["scores"]
    assert np.allclose(check,[ref["neutral"],ref["TL"],ref["TL+R50"]],atol=2e-7,rtol=0)
    report["strict_original_replay"]={"comparisons":int(strictref.sum()),"scores":check.tolist(),"matched":True}
    report["status"]="SOURCE_ACQUISITION";save()
    a,v,xx,yy=source()
    report["grain_support"]={}
    rs=[]
    for g in GRAINS:
        r,means=grained(a,v,xx,yy,g)
        if g==1:
            assert np.isfinite(r).all() and np.allclose(r,raw[:,raw_names.index("R50")],atol=1e-8,rtol=0)
            assert np.allclose(means[:,-1],raw[:,raw_names.index("GVSM_area_mean_RH98_m")],atol=1e-8,rtol=0)
        rs.append(r)
    del a,v
    avail=np.isfinite(np.stack(rs)).all(0);keep=avail[ca]&avail[cb]
    report["common_support"]={"cells":int(avail.sum()),"comparisons":int(keep.sum()),"fraction":float(keep.mean()),"blocks":int(np.unique(block[keep]).size),"strict_comparisons":int((keep&strictref).sum()),"strict_fraction":float((keep&strictref).sum()/strictref.sum())}
    report["status"]="SUPPORT_COMPLETE";save()
    if keep.mean()<.8 or len(np.unique(block[keep]))<35 or (keep&strictref).sum()/strictref.sum()<.8:
        report["status"]="SUPPORT_STOP";save()
    else:
        report["tests"]={}
        for kind in ("spatial","strict_source_block"):
            sc=np.full((len(z),len(MOD)),np.nan);fs=[]
            for k in range(5):
                for h in ([None] if kind=="spatial" else range(5)):
                    label=f"block{k+1}" if h is None else f"block{k+1}_source{h+1}"
                    if h is not None and label not in expected:continue
                    te=keep&(fold==k);tr=keep&(fold!=k)
                    if h is not None:te&=sf==h;tr&=sf!=h
                    if tr.sum()<300 or te.sum()<10 or len(np.unique(block[tr]))<10 or len(np.unique(block[te]))<3:continue
                    assert not set(block[tr])&set(block[te]) and not set(np.r_[ca[tr],cb[tr]])&set(np.r_[ca[te],cb[te]])
                    if h is not None:assert not set(src[tr])&set(src[te])
                    x=fit(tr,te,rs);sc[te]=x;ss=weights(te)@x
                    fs.append({"fold":label,"comparisons":int(te.sum()),"blocks":int(np.unique(block[te]).size),"scores":dict(zip(MOD,ss.tolist()))})
            scored=np.isfinite(sc).all(1)
            if len(fs)<(5 if kind=="spatial" else 12) or scored.sum()<(keep.sum() if kind=="spatial" else .8*strictref.sum()):
                report["tests"][kind]={"status":"FOLD_SUPPORT_STOP","folds":len(fs),"comparisons":int(scored.sum())}
            else:report["tests"][kind]=summary(sc,fs,kind)
        report["primary_pass"]=all(x.get("primary_pass",False) for x in report["tests"].values())
        report["status"]="COMPLETE";save()
except Exception as e:
    report["last_status"]=report["status"];report["status"]="STOP";report["error_type"]=type(e).__name__;save()
