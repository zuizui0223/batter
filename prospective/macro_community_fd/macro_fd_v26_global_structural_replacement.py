"""V26: global adjacent-assemblage functional replacement and vertical vegetation contrasts."""
import collections as C,hashlib,json
from pathlib import Path
import numpy as np
from pyproj import Transformer
from macro_fd_v4_global_ranges import read_ranges,wing,REGIONS
from combine_v6b_coverage import acquire,COARSE
from macro_fd_v7_multidomain import mapping
from macro_fd_v5_structure import edges,check_overlap,climate,gedi
from macro_fd_v16_batamp_structure import ENV_HASH,CLIM_HASH
OUT=Path("macro_fd_v26_result.json")
REG={"North_America":413,"East_Asia":414,"South_America":883,"Africa":522}
DOMAIN=["joint","wing","strategy","mass"]
def save(o):
    OUT.write_text(json.dumps(o,indent=2,allow_nan=False)+"\n")
    print("GLOBAL_V26_REPORT="+json.dumps(o,allow_nan=False),flush=True)
def metrics(y):
    # domain losses on globally standardized species trait space, not unitless percent FD
    wing=(y[...,:2]**2).sum(-1)
    strategy=(y[...,2:14]**2).sum(-1)
    mass=y[...,14]**2
    return np.stack([(wing+strategy)/2,wing,strategy,mass],axis=-1)
def decomp(d,z,g):
    raw=d@z;gg=d@g;rr=d@(z-g)
    a,b,c=metrics(raw),metrics(gg),metrics(rr)
    cross=a-b-c
    # independently compute cross term by component inner products
    w=2*(gg[:,:2]*rr[:,:2]).sum(1);st=2*(gg[:,2:14]*rr[:,2:14]).sum(1);m=2*gg[:,14]*rr[:,14]
    assert np.allclose(cross,np.column_stack([(w+st)/2,w,st,m]),atol=1e-10)
    return raw,gg,rr,np.stack([a,b,c,cross],axis=1)
def keyhash(x):return hashlib.sha256(repr(x).encode()).hexdigest()
def blockkeys(rc,reg,grain):return [(str(r),int(x)//grain,int(y)//grain) for (x,y),r in zip(rc,reg)]
def weights(reg,block,mask):
    w=np.zeros(len(mask));groups=C.defaultdict(lambda:C.defaultdict(list))
    for i in np.flatnonzero(mask):groups[reg[i]][block[i]].append(i)
    for v in groups.values():
        for ix in v.values():w[ix]=1/(len(groups)*len(v)*len(ix))
    assert abs(w.sum()-1)<1e-10
    return w
def score(x,y,reg,rc,ep,grain,transfer=False):
    b=blockkeys(rc,reg,grain);rf=sorted(set(reg))
    if transfer:
        split=np.array(reg);folds=rf
    else:
        lookup={}
        for r in rf:
            k=sorted({v for v in b if v[0]==r},key=keyhash)
            for j,v in enumerate(k):lookup[v]=j%5
        split=np.array([lookup[v] for v in b]);folds=list(range(5))
    sc=np.full((len(y),3,4),np.nan);fs=[]
    for f in folds:
        te=split==f;tr=~te
        if len({b[i] for i in np.flatnonzero(te)})<5 or tr.sum()<100 or len(set(reg[tr]))<(3 if transfer else 4):
            return {"status":"insufficient_fold_support","fold":str(f),"grain":grain,"transfer":transfer}
        assert not set(ep[tr].ravel())&set(ep[te].ravel())
        if not transfer:assert set(reg[tr])==set(reg[te])==set(rf)
        w=weights(reg,b,tr)[tr];a=x[tr];sd=np.sqrt(w@(a*a));sd[sd<1e-12]=1
        u=a/sd;v=x[te]/sd
        pred=[np.zeros((te.sum(),y.shape[1]))]
        for n in (x.shape[1]-1,x.shape[1]):
            U=u[:,:n];B=np.linalg.solve(U.T@(w[:,None]*U)+.1*np.eye(n),U.T@(w[:,None]*y[tr]))
            assert np.max(np.abs(U.T@(w[:,None]*(U@B-y[tr]))+.1*B))<1e-8
            pred.append(v[:,:n]@B)
        sc[te]=np.stack([metrics(y[te]-p) for p in pred],axis=1)
        m=np.einsum("i,ijk->jk",weights(reg,b,te)[te],sc[te])
        fs.append({"fold":str(f),"edges":int(te.sum()),"blocks":len({b[i] for i in np.flatnonzero(te)}),"V_B":(m[1]-m[2]).tolist(),"V_N":(m[0]-m[2]).tolist()})
    assert np.isfinite(sc).all()
    allmask=np.ones(len(y),bool);w=weights(reg,b,allmask);m=np.einsum("i,ijk->jk",w,sc);gain=m[1]-m[2]
    bg=C.defaultdict(list)
    for i,k in enumerate(b):bg[k].append(i)
    bw=np.array([w[v].sum() for v in bg.values()]);diff=np.array([(sc[v,1]-sc[v,2]).mean(0) for v in bg.values()])
    assert np.allclose(bw@diff,gain)
    loo=(gain-bw[:,None]*diff)/(1-bw[:,None])
    r={"status":"scored","grain":grain,"transfer":transfer,"edges":len(y),"blocks":len(bg),"MSE":dict(zip(["N","B","V"],m.tolist())),"V_B":gain.tolist(),"V_N":(m[0]-m[2]).tolist(),"relative_V_B":np.divide(gain,m[1],out=np.zeros_like(gain),where=m[1]>1e-12).tolist(),"positive_blocks":(diff>0).sum(0).tolist(),"positive_folds":sum(v["V_B"][0]>0 for v in fs),"folds":fs,"delete_one_region_block_range":[loo.min(0).tolist(),loo.max(0).tolist()],"regions":{}}
    for tag in rf:
        mask=reg==tag;mm=np.einsum("i,ijk->jk",weights(reg,b,mask)[mask],sc[mask])
        r["regions"][tag]={"edges":int(mask.sum()),"V_B":(mm[1]-mm[2]).tolist(),"V_N":(mm[0]-mm[2]).tolist()}
    r["primary_pass"]=bool((gain[:3]>0).all() and m[0,0]>m[2,0] and r["positive_folds"]>=(3 if transfer else 4) and (transfer or r["positive_blocks"][0]/len(bg)>=.6) and loo[:,0].min()>0)
    return r
def q(x):
    return np.quantile(x,[0,.25,.5,.75,1]).tolist()
def main():
    o={"stage":"global functional replacement across structural transitions","status":"START","domain_order":DOMAIN,"decomposition_order":["raw_squared_contrast","genus_squared_contrast","within_genus_squared_residual","cross_term"],"limits":["potential range assemblages, not observed coexistence","neighbor transitions not temporal turnover or dispersal","same sources as V7/V12, distinct outcome, not independent validation","GEDI bottom-half PAVD fraction is relative vegetation allocation, not navigable air volume","genus expected replacement not complete phylogenetic control","edges share species and endpoints; not independent replicates","coarse diet and stratum source labels not measured flight heights"]}
    try:
        check_overlap();names,X,shape,crs,T=read_ranges(o);assert len(names)==1141
        w=wing(o);a,b,_=acquire(o);tab=mapping(a,b,names,w,o)
        tab=tab.loc[tab.index.intersection(w.index)].sort_index()
        assert len(tab)==234
        nm=tab.index.tolist();ids=[names.index(n) for n in nm];R=X[ids]
        full=X.sum(0);rich=R.sum(0);cov=np.divide(rich,full,out=np.zeros_like(full,float),where=full>0)
        a=w.loc[nm,["AR","WL_N_m2","mass_g_physical"]].to_numpy(float);a[:,1:]=np.log(a[:,1:]);a=(a-a.mean(0))/a.std(0)
        strata=np.eye(4)[[["A","Ar","G","S"].index(v) for v in tab.stratum]]
        J=(tab[COARSE].to_numpy(float)[:,:,None]*strata[:,None,:]).reshape(len(tab),12)
        assert np.allclose(J.sum(1),1)
        J=J-J.mean(0);J/=np.sqrt((J*J).sum(1).mean())
        z=np.column_stack([a[:,:2]/np.sqrt(2),J,a[:,2]])
        assert np.allclose(metrics(z).mean(0),1)
        gn=sorted({n.split("_")[0] for n in nm});H=np.array([[int(n.split("_")[0]==g) for g in gn] for n in nm],float)
        G=H@((H.T@z)/H.sum(0)[:,None]);assert np.allclose(H.T@(z-G),0,atol=1e-10)
        rc=np.array(np.unravel_index(np.arange(R.shape[1]),shape)).T
        rev=Transformer.from_crs(crs,4326,always_xy=True)
        lon,lat=rev.transform(T.c+(rc[:,1]+.5)*T.a,T.f+(rc[:,0]+.5)*T.e)
        _,la=rev.transform(np.zeros(len(rc)),T.f+rc[:,0]*T.e);_,lb=rev.transform(np.zeros(len(rc)),T.f+(rc[:,0]+1)*T.e)
        rg=np.full(len(rc),"other",dtype="U24")
        for r,(l,h,bot,top) in REGIONS.items():
            ok=(lon>=l)&(lon<=h)&(lat>=bot)&(lat<top)
            assert np.all(rg[ok]=="other");rg[ok]=r
        tx,ty=edges(T,shape)
        o["status"]="CLIMATE_ACQUISITION";save(o);clim,cc=climate(o,tx,ty);assert o["climate"]["sha256"]==CLIM_HASH
        o["status"]="GEDI_ACQUISITION";save(o);veg,vc=gedi(o,tx,ty)
        assert {k:v["sha256"] for k,v in o["GEDI"]["metrics"].items()}==ENV_HASH
        keep=(np.maximum(la,lb)<=51.6)&(np.minimum(la,lb)>=-51.6)&(cc>=.5)&(vc>=.5)&(veg[:,0]>5)&(veg[:,1]>=.3)&np.isfinite(clim).all(1)&np.isfinite(veg).all(1)&(rich>=5)&(cov>=.2)&np.isin(rg,list(REG))
        o["cell_support"]={k:int((keep&(rg==k)).sum()) for k in REG};assert o["cell_support"]==REG
        pairs=[]
        for i in np.flatnonzero(keep):
            r,c=rc[i]
            for rr,ccc in ((r,c+1),(r+1,c)):
                if rr>=shape[0] or ccc>=shape[1] or r//5!=rr//5 or c//5!=ccc//5:continue
                j=int(rr*shape[1]+ccc)
                if keep[j] and rg[j]==rg[i]:pairs.append((int(i),j))
        ep=np.array(pairs,int);i,j=ep.T
        p=R[:,i].T/rich[i,None];qq=R[:,j].T/rich[j,None]
        turnover=.5*np.abs(qq-p).sum(1)
        o["neighbor_edges_before_T_gate"]=len(ep)
        ok=turnover>=.05
        ep=ep[ok];t=turnover[ok];d=(qq[ok]-p[ok])/t[:,None];i,j=ep.T
        assert np.allclose(d.sum(1),0) and np.allclose(np.maximum(d,0).sum(1),1)
        rr=rg[i];rowcol=rc[i]
        assert np.array_equal(rg[i],rg[j]) and np.array_equal(rc[i]//5,rc[j]//5) and np.array_equal(rc[i]//10,rc[j]//10)
        raw,gg,y,parts=decomp(d,z,G)
        o["roster"]={"species":len(nm),"genera":len(gn),"cells":int(keep.sum()),"domains":["wing","joint_diet_stratum","mass"]}
        o["edge_support"]={};o["decomposition"]={}
        b5=blockkeys(rowcol,rr,5)
        for r in REG:
            m=rr==r
            a={"edges":int(m.sum()),"endpoint_cells":len(set(ep[m].ravel())),"blocks5":len(set(blockkeys(rowcol[m],rr[m],5))),"blocks10":len(set(blockkeys(rowcol[m],rr[m],10))),"T_quantiles":q(t[m]) if m.any() else None,"high_T_edges":int((m&(t>=.1)).sum()),"high_coverage_both_edges":int((m&(cov[i]>=.5)&(cov[j]>=.5)).sum())}
            o["edge_support"][r]=a
            if m.any():
                v=np.einsum("i,ijk->jk",weights(rr,b5,m)[m],parts[m])
                o["decomposition"][r]={"squared_components":v.tolist(),"residual_over_raw":np.divide(v[2],v[0],out=np.zeros(4),where=v[0]>1e-12).tolist()}
        o["total_edges"]=len(t);o["total_endpoint_cells"]=len(set(ep.ravel()))
        allmask=np.ones(len(t),bool);v=np.einsum("i,ijk->jk",weights(rr,b5,allmask),parts)
        o["decomposition"]["equal_region_block"]={"squared_components":v.tolist(),"residual_over_raw":np.divide(v[2],v[0],out=np.zeros(4),where=v[0]>1e-12).tolist()}
        o["status"]="PAIR_SUPPORT_COMPLETE";save(o)
        if len(t)<500 or not all(v["edges"]>=100 and v["blocks5"]>=10 and v["blocks10"]>=5 for v in o["edge_support"].values()):o["status"]="PAIR_SUPPORT_STOP";save(o);return
        env=np.column_stack([clim,np.abs(lat),np.log1p(full),np.log1p(rich),cov,cc,vc,np.log1p(veg[:,0]),veg[:,1],np.log1p(veg[:,2])])
        xx=np.column_stack([env[j]-env[i],d@H,veg[j,3]-veg[i,3]])
        # Exact log of positive richness endpoints, not log1p, as frozen.
        xx[:,7]=np.log(full[j])-np.log(full[i]);xx[:,8]=np.log(rich[j])-np.log(rich[i])
        assert np.isfinite(xx).all() and np.isfinite(y).all()
        o["feature_order"]=["delta_bio1","delta_bio4","delta_bio5","delta_bio6","delta_bio12","delta_bio15","delta_abs_lat","delta_log_range_richness","delta_log_matched_richness","delta_trait_coverage","delta_climate_area_support","delta_GEDI_area_support","delta_log1p_RH98","delta_cover","delta_log1p_PAI"]+[f"replacement_genus_fraction_{k}" for k in gn]+["delta_bottom_half_PAVD_fraction"]
        assert len(o["feature_order"])==xx.shape[1]
        o["PAVD_absolute_difference_quantiles"]=q(np.abs(xx[:,-1]))
        o["tests"]={"spatial_5":score(xx,y,rr,rowcol,ep,5),"spatial_10":score(xx,y,rr,rowcol,ep,10),"region_transfer":score(xx,y,rr,rowcol,ep,5,True)}
        o["primary_pass"]=all(x.get("primary_pass",False) for x in o["tests"].values());o["status"]="COMPLETE";save(o)
    except Exception as e:
        o["last_status"]=o["status"];o["status"]="STOP";o["error_type"]=type(e).__name__;save(o)
if __name__=="__main__":main()
