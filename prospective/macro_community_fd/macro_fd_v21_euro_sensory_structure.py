"""V21: conditional flight–sensory covariance and measured coarse vegetation."""
import collections as C,hashlib,json
from pathlib import Path
import numpy as np
from pyproj import Transformer
from macro_fd_v20b_euro_free_flight import source,dist
from macro_fd_v4_global_ranges import read_ranges,wing
from macro_fd_v7_multidomain import expected
from macro_fd_v5_structure import edges,check_overlap,climate,gedi
from macro_fd_v16_batamp_structure import ENV_HASH,CLIM_HASH,keyfold
OUT=Path("macro_fd_v21_result.json")
RESP=["K_genus_residual","K_raw","wing_MPD","acoustic_MPD","acoustic_MPD_genus_residual"]
def save(o):
    OUT.write_text(json.dumps(o,indent=2,allow_nan=False)+"\n")
    print("GLOBAL_V21_REPORT="+json.dumps(o,allow_nan=False),flush=True)
def weights(block,mask):
    ix=np.flatnonzero(mask);by=C.defaultdict(list)
    for i in ix:by[block[i]].append(i)
    w=np.zeros(len(mask))
    for v in by.values():w[v]=1/(len(by)*len(v))
    assert np.isclose(w.sum(),1)
    return w
def score(X,Y,rc,woody,grain,nd,nb):
    block=[tuple(x//grain) for x in rc];fold=keyfold(block)
    sc=np.full((len(Y),4,Y.shape[1]),np.nan);fs=[]
    for k in range(5):
        te=fold==k;tr=~te
        if len({block[i] for i in np.flatnonzero(te)})<3 or tr.sum()<50:continue
        assert not {block[i] for i in np.flatnonzero(te)}&{block[i] for i in np.flatnonzero(tr)}
        w=weights(block,tr)[tr];a=X[tr];mu=w@a
        sd=np.sqrt(w@((a-mu)**2));active=sd>1e-12;sd[~active]=1
        z=(a-mu)/sd;zt=(X[te]-mu)/sd;z[:,~active]=0;zt[:,~active]=0
        y=Y[tr];ym=w@y
        pred=[np.tile(ym,(te.sum(),1))]
        for n in (nd,nb,X.shape[1]):
            q=z[:,:n];b=np.linalg.solve(q.T@(w[:,None]*q)+.1*np.eye(n),q.T@(w[:,None]*(y-ym)))
            assert np.max(np.abs(q.T@(w[:,None]*(q@b-y+ym))+.1*b))<1e-8
            pred.append(ym+zt[:,:n]@b)
        sc[te]=np.stack([(v-Y[te])**2 for v in pred],axis=1)
        a=np.einsum("i,ijk->jk",weights(block,te)[te],sc[te])
        fs.append({"fold":k,"cells":int(te.sum()),"blocks":len({block[i] for i in np.flatnonzero(te)}),"V_B":(a[2]-a[3]).tolist(),"V_N":(a[0]-a[3]).tolist()})
    out={"grain":grain,"folds":fs,"status":"insufficient_fold_support"}
    if len(fs)!=5 or not np.isfinite(sc).all():return out
    w=weights(block,np.ones(len(Y),bool))
    a=np.einsum("i,ijk->jk",w,sc)
    by=C.defaultdict(list)
    for i,b in enumerate(block):by[b].append(i)
    diff=np.array([(sc[v,2]-sc[v,3]).mean(0) for v in by.values()])
    g=diff.mean(0);assert np.allclose(g,a[2]-a[3])
    loo=(g*len(diff)-diff)/(len(diff)-1)
    relative=np.divide(g,a[2],out=np.zeros_like(g),where=a[2]>0)
    out.update(status="scored",MSE=dict(zip(("N","D","B","V"),a.tolist())),V_B=g.tolist(),V_N=(a[0]-a[3]).tolist(),relative_V_B=relative.tolist(),blocks=len(by),positive_blocks=(diff>0).sum(0).tolist(),positive_folds=sum(f["V_B"][0]>0 for f in fs),delete_one_block_range=[loo.min(0).tolist(),loo.max(0).tolist()])
    out["primary_pass"]=bool(g[0]>0 and (a[0]-a[3])[0]>0 and out["positive_folds"]>=4 and out["positive_blocks"][0]/len(by)>=.6 and loo[:,0].min()>0)
    out["subgroups"]={}
    for label,ok in [("woody",woody),("other",~woody)]:
        if ok.any():
            d=np.einsum("i,ijk->jk",weights(block,ok)[ok],sc[ok])
            out["subgroups"][label]={"cells":int(ok.sum()),"blocks":len({block[i] for i in np.flatnonzero(ok)}),"V_B":(d[2]-d[3]).tolist(),"V_N":(d[0]-d[3]).tolist()}
    return out
def main():
    o={"stage":"measured vegetation and conditional flight–sensory covariance","status":"START","response_order":RESP,"limits":["potential range assemblages, not surveyed cooccurrence","same V20b species and range data","genus-conditioned distance expectation not full phylogenetic correction","coarse vegetation allocation not actual flight space","known lineage composition used as covariate","no causal partitioning or occupancy claim"]}
    try:
        aa=source(o);assert len(aa)==36
        names,R,shape,crs,T=read_ranges(o);w=wing(o)
        nm=sorted(set(names)&set(w.index)&set(aa.index))
        pin=json.loads(Path("prospective/macro_community_fd/MACRO_FD_V20B_FREE_FLIGHT_RESULT.json").read_text())
        assert nm==pin["roster_support"]["trait_names"] and len(nm)==23
        ids=[names.index(n) for n in nm]
        a=aa.loc[nm].to_numpy(float);v=w.loc[nm,["AR","WL_N_m2"]].to_numpy(float)
        W=dist(np.c_[v[:,0],np.log(v[:,1])]);A=dist(np.log(a))
        E=expected(A,nm)
        assert E.shape==A.shape and np.allclose(E,E.T) and np.allclose(np.diag(E),0)
        groups=sorted(set(n.split("_")[0] for n in nm))
        mat=np.array([[int(n.startswith(g+"_")) for g in groups] for n in nm])
        rc=np.array(np.unravel_index(np.arange(R.shape[1]),shape)).T
        rev=Transformer.from_crs(crs,4326,always_xy=True)
        lon,lat=rev.transform(T.c+(rc[:,1]+.5)*T.a,T.f+(rc[:,0]+.5)*T.e)
        _,a0=rev.transform(np.zeros(len(rc)),T.f+rc[:,0]*T.e);_,a1=rev.transform(np.zeros(len(rc)),T.f+(rc[:,0]+1)*T.e)
        full=R.sum(0);sub=R[ids];k=sub.sum(0);cov=np.divide(k,full,out=np.zeros_like(full,float),where=full>0)
        base=(lon>=-12)&(lon<=40)&(lat>=35)&(lat<=72)&(k>=5)&(cov>=.3)
        assert base.sum()==934
        yall=[]
        for p in sub[:,base].T:
            q=np.outer(p,p).astype(float);np.fill_diagonal(q,0);q/=q.sum()
            mw=np.sum(q*W);ma=np.sum(q*A);me=np.sum(q*E)
            L=q*(W-mw);K=np.sum(L*A);res=np.sum(L*(A-E))
            assert abs(res-(K-np.sum(L*E)))<1e-12
            yall.append([res,K,mw,ma,ma-me])
        yall=np.array(yall)
        o["before_environment"]={"species":len(nm),"cells":int(base.sum()),"exact_genus_residual_mean_cell_weight":float(yall[:,0].mean())}
        check_overlap();tx,ty=edges(T,shape)
        o["status"]="CLIMATE_ACQUISITION";save(o);clim,cc=climate(o,tx,ty);assert o["climate"]["sha256"]==CLIM_HASH
        o["status"]="GEDI_ACQUISITION";save(o);veg,vc=gedi(o,tx,ty)
        assert {k:v["sha256"] for k,v in o["GEDI"]["metrics"].items()}==ENV_HASH
        keep=base&(np.maximum(a0,a1)<=51.6)&(np.minimum(a0,a1)>=-51.6)&(cc>=.5)&(vc>=.5)&np.isfinite(clim).all(1)&np.isfinite(veg).all(1)&(veg[:,2]>0)
        rr=rc[keep];Y=yall[keep[base]]
        o["post_environment"]={"cells":int(keep.sum()),"blocks2":len({tuple(x//2) for x in rr}),"blocks4":len({tuple(x//4) for x in rr})}
        if len(Y)<100 or o["post_environment"]["blocks2"]<25 or o["post_environment"]["blocks4"]<15:o["status"]="ENVIRONMENT_SUPPORT_STOP";save(o);return
        genus=sub[:,keep].T@mat/k[keep,None]
        D=np.c_[np.log(full[keep]),np.log(k[keep]),cov[keep],np.abs(lat[keep]),cc[keep],vc[keep],genus]
        B=np.c_[D,clim[keep],np.log1p(veg[keep,0]),veg[keep,1],np.log1p(veg[keep,2])]
        X=np.c_[B,veg[keep,3]]
        assert np.isfinite(X).all() and np.isfinite(Y).all()
        woody=(veg[keep,0]>5)&(veg[keep,1]>=.3)
        o["post_environment"]["woody_cells"]=int(woody.sum())
        o["means"]={k:float(v) for k,v in zip(RESP,Y.mean(0))}
        o["tests"]={str(g):score(X,Y,rr,woody,g,D.shape[1],B.shape[1]) for g in (2,4)}
        o["primary_pass"]=all(v.get("primary_pass",False) for v in o["tests"].values())
        o["status"]="COMPLETE";save(o)
    except Exception as e:
        o["last_status"]=o["status"];o["status"]="STOP";o["error_type"]=type(e).__name__
        save(o)
if __name__=="__main__":main()
