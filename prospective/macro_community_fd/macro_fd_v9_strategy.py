"""V9: functional strategy composition prediction and exact genus error decomposition."""
import collections as C, hashlib,json
from pathlib import Path
import numpy as np
from pyproj import Transformer
from macro_fd_v4_global_ranges import read_ranges,wing,REGIONS
from combine_v6b_coverage import acquire,COARSE
from macro_fd_v7_multidomain import mapping
from macro_fd_v5_structure import check_overlap,edges,climate,gedi,weights

ROOT=Path(__file__).resolve().parent
OUT=Path("macro_fd_v9_result.json")
STRATA=["A","Ar","G","S"]
FEATURES=["log_range_richness","log_matched_richness","trait_coverage","abs_lat","bio1","bio4","bio5","bio6","bio12","bio15","GEDI_area_support","climate_area_support","log1p_RH98","cover","log1p_PAI","bottom_half_PAVD_fraction"]
MODELS={"N":0,"B":12,"H":15,"V":16}
METRICS=["joint","genus_portfolio","within_genus_deviation","cross_term","projected_joint","diet_marginal","stratum_marginal"]
CONTRASTS=[("B","N"),("H","B"),("V","H"),("H","N"),("V","N")]

def save(out):
    OUT.write_text(json.dumps(out,indent=2,allow_nan=False)+"\n")
    print("V9_STAGE="+out["status"],flush=True)

def project(x):
    """Euclidean simplex projection, row-wise."""
    u=np.sort(x,axis=1)[:,::-1];v=(np.cumsum(u,axis=1)-1)/np.arange(1,x.shape[1]+1)
    idx=(u>v).sum(1)-1;assert np.all(idx>=0)
    p=np.maximum(x-v[np.arange(len(x)),idx,None],0)
    assert np.allclose(p.sum(1),1) and np.all(p>=0)
    return p

def predict(X,Y,w,tr,te,n):
    y=Y[tr];w=w[tr];assert abs(w.sum()-1)<1e-10
    ym=w@y
    if n==0:return np.repeat(ym[None,:],te.sum(),axis=0)
    x=X[tr,:n];mu=w@x;sd=np.sqrt(w@((x-mu)**2));active=sd>1e-12;sd[~active]=1
    z=(x-mu)/sd;zt=(X[te,:n]-mu)/sd;z[:,~active]=0;zt[:,~active]=0
    a=z.T@(w[:,None]*z)+.1*np.eye(n);b=z.T@(w[:,None]*(y-ym))
    coef=np.linalg.solve(a,b)
    assert np.max(abs(a@coef-b))<1e-9
    return ym+zt@coef

def loss(J,G,R,j,g,r):
    eg=G-g;er=R-r;ej=J-j
    norm=lambda x:(x*x).sum(1)
    q=np.c_[norm(ej),norm(eg),norm(er),2*(eg*er).sum(1),norm(J-project(j)),
           norm(ej.reshape(-1,3,4).sum(2)),norm(ej.reshape(-1,3,4).sum(1))]
    assert np.allclose(q[:,0],q[:,1:4].sum(1),atol=1e-12)
    return q

def summarize(sc,reg,block,mask):
    w=weights(reg,block,mask);mean=np.einsum("i,imk->mk",w[mask],sc[mask])
    names=list(MODELS);groups=C.defaultdict(list)
    for i in np.flatnonzero(mask):groups[reg[i],int(block[i])].append(i)
    vals=np.array([sc[v].mean(0) for v in groups.values()]);bw=np.array([w[v].sum() for v in groups.values()])
    assert np.allclose(np.einsum("i,imk->mk",bw,vals),mean)
    out={"cells":int(mask.sum()),"regions":len(set(reg[mask])),"region_blocks":len(groups),
        "mse":dict(zip(names,mean.tolist())),"contrasts":{}}
    for a,b in CONTRASTS:
        d=vals[:,names.index(b)]-vals[:,names.index(a)];v=bw@d
        assert abs(v[0]-v[1:4].sum())<1e-10
        om=(v-bw[:,None]*d)/(1-bw[:,None]) if len(bw)>1 else None
        out["contrasts"][a+"-"+b]={"gain":v.tolist(),"positive_region_blocks":(d>1e-12).sum(0).tolist(),
            "relative_joint_gain":float(v[0]/mean[names.index(b),0]) if mean[names.index(b),0]>1e-12 else None,
            "delete_one_region_block_range":[om.min(0).tolist(),om.max(0).tolist()] if om is not None else None,
            "genus_gain_over_total":float(v[1]/v[0]) if v[0]>1e-12 else None}
    return out

def score(X,J,G,R,reg,rc,woody,grain,transfer=False):
    keys=[tuple(v//grain) for v in rc];unique=sorted(set(keys),key=lambda v:hashlib.sha256(str(v).encode()).hexdigest())
    idx={v:i for i,v in enumerate(unique)};block=np.array([idx[v] for v in keys])
    split=reg if transfer else block%5;folds=sorted(set(split))
    sc=np.full((len(J),len(MODELS),len(METRICS)),np.nan)
    invalid=np.zeros((len(J),len(MODELS)),bool);reports=[]
    for k in folds:
        te=split==k;tr=~te
        if len(set(block[te]))<5 or len(set(reg[tr]))<(3 if transfer else 4) or (not transfer and set(reg[tr])!=set(reg)):
            return {"status":"insufficient_fold_support","grain":grain,"failed_fold":str(k),"test_blocks":len(set(block[te]))}
        if not transfer:assert not set(block[te])&set(block[tr])
        w=weights(reg,block,tr)
        for m,n in enumerate(MODELS.values()):
            pred=predict(X,np.c_[G,R],w,tr,te,n)
            g,r=pred[:,:12],pred[:,12:];j=g+r
            independent=predict(X,J,w,tr,te,n)
            assert np.allclose(j,independent,atol=1e-10) and np.allclose(g.sum(1),1) and np.allclose(r.sum(1),0)
            sc[te,m]=loss(J[te],G[te],R[te],j,g,r)
            invalid[te,m]=np.any((j< -1e-10)|(j>1+1e-10),axis=1)
        s=summarize(sc,reg,block,te);s["fold"]=str(k);s["blocks"]=len(set(block[te]))
        reports.append(s)
    assert np.isfinite(sc).all()
    allmask=np.ones(len(J),bool);out=summarize(sc,reg,block,allmask)
    w=weights(reg,block,allmask)
    out["out_of_simplex_fraction"]=dict(zip(MODELS,(w@invalid).tolist()))
    out["folds"]=reports;out["blocks"]=len(unique)
    out["positive_folds_H_B_joint"]=sum(v["contrasts"]["H-B"]["gain"][0]>0 for v in reports)
    out["subgroups"]={}
    for tag,m in [("woody",woody),("not_woody",~woody)]:
        if m.sum()>0:out["subgroups"][tag]=summarize(sc,reg,block,m)
    a=out["contrasts"]["H-B"]["gain"];n=out["contrasts"]["H-N"]["gain"]
    out["pass"]=bool(a[0]>0 and n[0]>0 and a[1]>0 and a[1]>a[2] and a[4]>0 and out["positive_folds_H_B_joint"]>=4 and (transfer or out["contrasts"]["H-B"]["positive_region_blocks"][0]/out["region_blocks"]>=.6))
    out["status"]="scored";return out

def cohort(tag,tab,X,names,rc,reg,lat,env,clim,climcov,veg,vegcov):
    ix={n:i for i,n in enumerate(names)};ids=[ix[n] for n in tab.index];m=X[ids]
    full=X.sum(0);rich=m.sum(0);cov=np.divide(rich,full,out=np.zeros_like(full,float),where=full>0)
    ok=(rich>=5)&(cov>=.8);assert int(ok.sum())==(9631 if tag=="broad" else 9118)
    D=tab[COARSE].to_numpy(float);S=np.eye(4)[[STRATA.index(v) for v in tab.stratum]]
    J0=(D[:,:,None]*S[:,None,:]).reshape(len(tab),12)
    assert np.allclose(J0.sum(1),1) and np.all(J0>=0)
    _,g=np.unique([n.split("_")[0] for n in tab.index],return_inverse=True)
    cnt=np.bincount(g);a=np.zeros((len(cnt),12));np.add.at(a,g,J0)
    G0=(a/cnt[:,None])[g];assert np.allclose(G0.sum(1),1)
    dom=ok&env;out={"species":len(ids),"genera":len(cnt),"range_eligible":int(ok.sum()),"environment_complete":int(dom.sum()),"region_support":{}}
    use=[]
    woody=(veg[:,0]>5)&(veg[:,1]>=.3)
    for n in REGIONS:
        q=dom&(reg==n);b5=len(np.unique(rc[q]//5,axis=0));b10=len(np.unique(rc[q]//10,axis=0))
        s={"cells":int(q.sum()),"blocks_5":b5,"blocks_10":b10,"woody":int((q&woody).sum()),"matched_species":int(np.any(m[:,q],axis=1).sum()) if q.any() else 0,
            "median_coverage":float(np.median(cov[q])) if q.any() else None,
            "admitted":bool(q.sum()>=100 and b5>=10 and b10>=10)}
        if s["admitted"]:use.append(n)
        out["region_support"][n]=s
    keep=dom&np.isin(reg,use);out["admitted_regions"]=use;out["analysis_cells"]=int(keep.sum());out["woody_cells"]=int((keep&woody).sum())
    if keep.sum()<1000 or len(use)<4:out["status"]="insufficient_support";return out
    P=m[:,keep].T.astype(float);P/=P.sum(1,keepdims=True)
    J=P@J0;G=P@G0;R=J-G
    assert np.allclose(J.sum(1),1) and np.allclose(G.sum(1),1) and np.allclose(R.sum(1),0)
    # Exact independent genus aggregation replay on all cells.
    H=np.eye(len(cnt))[g];assert np.allclose(G,(P@H)@(a/cnt[:,None]))
    A=np.c_[np.log(full[keep]),np.log(rich[keep]),cov[keep],np.abs(lat[keep]),clim[keep],vegcov[keep],climcov[keep],np.log1p(veg[keep,0]),veg[keep,1],np.log1p(veg[keep,2]),veg[keep,3]]
    assert A.shape[1]==len(FEATURES) and np.isfinite(A).all() and np.isfinite(J).all()
    out["predictor_range"]=[A.min(0).tolist(),A.max(0).tolist()]
    out["bottom_fraction_correlations"]=np.corrcoef(A,rowvar=False)[-1,:-1].tolist()
    out["region_observed"]={}
    for n in use:
        q=reg[keep]==n;out["region_observed"][n]={"joint_mean":J[q].mean(0).tolist(),"genus_mean":G[q].mean(0).tolist(),"mean_sq_within_genus_deviation":float((R[q]**2).sum(1).mean()),"zero_joint_categories":int((J[q].sum(0)<1e-12).sum())}
    out["tests"]={f"spatial_{k}":score(A,J,G,R,reg[keep],rc[keep],woody[keep],k) for k in (5,10)}
    out["tests"]["region_transfer"]=score(A,J,G,R,reg[keep],rc[keep],woody[keep],5,True)
    out["screen"]=all(t.get("pass",False) for t in out["tests"].values());out["status"]="scored"
    return out

def main():
    out={"stage":"V9 joint diet-stratum portfolio geography","status":"START","strategy_order":[d+"_"+s for d in COARSE for s in STRATA],"metric_order":METRICS,"features":FEATURES}
    try:
        check_overlap()
        assert np.allclose(project(np.array([[.3,.2,.5],[-1.,2.,0.]])),[[.3,.2,.5],[0,1,0]])
        names,X,shape,crs,T=read_ranges(out);assert len(names)==1141
        w=wing(out);a,b,c=acquire(out);tab=mapping(a,b,names,w,out);assert len(tab)==1034 and int(tab.no_transfer.sum())==998
        rc=np.array(np.unravel_index(np.arange(X.shape[1]),shape)).T;tx,ty=edges(T,shape)
        pj=Transformer.from_crs(crs,4326,always_xy=True);lon,lat=pj.transform(T.c+(rc[:,1]+.5)*T.a,T.f+(rc[:,0]+.5)*T.e)
        lat0=pj.transform(np.zeros(len(rc)),T.f+rc[:,0]*T.e)[1];lat1=pj.transform(np.zeros(len(rc)),T.f+(rc[:,0]+1)*T.e)[1]
        domain=(np.maximum(lat0,lat1)<=51.6)&(np.minimum(lat0,lat1)>=-51.6)
        reg=np.full(len(rc),"other",dtype="U24")
        for name,(l,h,bottom,t) in REGIONS.items():
            q=(lon>=l)&(lon<=h)&(lat>=bottom)&(lat<t);assert np.all(reg[q]=="other");reg[q]=name
        prior=json.loads((ROOT/"MACRO_FD_V5_MEASURED_STRUCTURE_RESULT.json").read_text())
        out["status"]="CLIMATE_DOWNLOAD";save(out);clim,climcov=climate(out,tx,ty)
        assert out["climate"]["sha256"]==prior["climate"]["sha256"] and out["climate"]["members"]==prior["climate"]["members"]
        out["status"]="CLIMATE_HASH_VERIFIED";save(out);veg,vegcov=gedi(out,tx,ty)
        assert out["GEDI"]["common_native_pixels"]==749456
        for k,v in out["GEDI"]["metrics"].items():assert v["sha256"]==prior["GEDI"]["metrics"][k]["sha256"]
        env=domain&(climcov>=.5)&(vegcov>=.5)&np.isfinite(clim).all(1)&np.isfinite(veg).all(1)
        woody=(veg[:,0]>5)&(veg[:,1]>=.3)
        assert int((env&woody).sum())==3090
        out["environment_replay"]=True;out["environment_cells_all_cover"]=int(env.sum());out["cohorts"]={}
        for tag,t in [("broad",tab),("without_split",tab[tab.no_transfer])]:
            out["status"]="COHORT_"+tag;save(out)
            out["cohorts"][tag]=cohort(tag,t,X,names,rc,reg,lat,env,clim,climcov,veg,vegcov)
        x=out["cohorts"]["broad"];y=out["cohorts"]["without_split"]
        sens=bool(y["status"]=="scored" and set(y["admitted_regions"])==set(x["admitted_regions"]) and all(t["status"]=="scored" and t["contrasts"]["H-B"]["gain"][0]>0 and t["contrasts"]["H-B"]["gain"][1]>0 for t in y["tests"].values()))
        out["primary_screen"]={"broad":bool(x.get("screen",False)),"sensitivity":sens,"pass":bool(x.get("screen",False) and sens)}
        out["status"]="COMPLETE"
    except Exception as e:
        out["last_status"]=out["status"];out["status"]="STOP";out["error_type"]=type(e).__name__
        # Do not expose remote exception strings (may contain authenticated URLs).
    save(out);print("GLOBAL_V9_REPORT="+json.dumps(out,allow_nan=False),flush=True)
if __name__=="__main__":main()
