"""V11 cross-trait portability: flight morphology, climate and geography-conditioned clade null."""
import collections as C,hashlib,json,io
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Transformer
from macro_fd_v4_global_ranges import read_ranges,wing,REGIONS,META,blob
from macro_fd_v5_structure import edges,check_overlap,climate,weights
from macro_fd_v9_strategy import predict
from macro_fd_v10_phylo import tree_source,partition_tree,portfolio,AGES,INDICES,DESIGNS,SEED,NREP
from combine_v6b_coverage import norm

ROOT=Path(__file__).resolve().parent
OUT=Path("macro_fd_v11_result.json")
MODELS={"N":0,"D":5,"B":11}
DOM=["flight","AR","log_WL","log_mass"]
def save(out):
    OUT.write_text(json.dumps(out,indent=2,allow_nan=False)+"\n");print("V11_STAGE="+out["status"],flush=True)
def domain(a):
    a=np.asarray(a);return np.concatenate([a[...,:2].mean(-1,keepdims=True),a],axis=-1)
def codes(v):
    # canonical order by first species in fixed roster, not memory addresses.
    d={};return np.array([d.setdefault(int(k),len(d)) for k in v],int)
def quad(a,K,b=None):
    return domain(np.sum(a*(K@(a if b is None else b)),axis=0))
def safe_ratio(x,t):
    return [float(a/b) if abs(b)>1e-12 else None for a,b in zip(x,t)]
def geography(M,reg):
    lab=sorted(list(REGIONS)+["other"])
    n=np.sum(M,axis=1);assert np.all(n>0)
    by=np.stack([M[:,reg==r].sum(1) for r in lab],axis=1)
    assert np.array_equal(by.sum(1),n)
    dom=np.argmax(by,axis=1)
    bins=np.array([int(v).bit_length()-1 for v in n])
    keys=list(zip(dom,bins));u=sorted(set(keys));ix={k:i for i,k in enumerate(u)}
    g=np.array([ix[k] for k in keys],int)
    assert len(g)==len(M)
    return g,{"strata":len(u),"singleton_strata":int((np.bincount(g)==1).sum()),"range_cells_quantiles":np.quantile(n,[0,.25,.5,.75,1]).tolist(),"dominant_region_counts":dict(C.Counter(lab[i] for i in dom)),"range_bin_counts":{str(k):int(v) for k,v in sorted(C.Counter(bins).items())}}
def gram(e,w):
    t=e*np.sqrt(w[:,None]);return t.T@t
def scoring(A,P,Z,reg,rc,design):
    grain=10 if design=="spatial_10" else 5;transfer=design=="region_transfer"
    keys=[tuple(v//grain) for v in rc];un=sorted(set(keys),key=lambda v:hashlib.sha256(str(v).encode()).hexdigest())
    ix={v:i for i,v in enumerate(un)};block=np.array([ix[v] for v in keys])
    split=reg if transfer else block%5
    if len(set(split))!=(len(set(reg)) if transfer else 5):raise ValueError("fold count")
    errs={k:np.empty_like(P) for k in MODELS};sc=np.full((len(P),3,4),np.nan);Y=P@Z;folds=[]
    for k in sorted(set(split)):
        te=split==k;tr=~te
        if len(set(block[te]))<5 or len(set(reg[tr]))<(3 if transfer else 4) or (not transfer and set(reg[tr])!=set(reg)):
            return None,None,{"status":"insufficient_fold_support","fold":str(k)}
        if not transfer:assert not set(block[te])&set(block[tr])
        wt=weights(reg,block,tr)
        for i,(m,n) in enumerate(MODELS.items()):
            p=predict(A,P,wt,tr,te,n);e=P[te]-p;errs[m][te]=e
            assert np.allclose(p@Z,predict(A,Y,wt,tr,te,n),atol=1e-10)
            sc[te,i]=domain((e@Z)**2)
        w=weights(reg,block,te)[te];v=np.einsum("i,imk->mk",w,sc[te])
        folds.append({"fold":str(k),"cells":int(te.sum()),"blocks":len(set(block[te])),"mse":dict(zip(MODELS,v.tolist())),"B_D":(v[1]-v[2]).tolist(),"B_N":(v[0]-v[2]).tolist()})
    assert np.isfinite(sc).all()
    w=weights(reg,block,np.ones(len(P),bool));v=np.einsum("i,imk->mk",w,sc)
    groups=C.defaultdict(list)
    for i,(r,b) in enumerate(zip(reg,block)):groups[r,int(b)].append(i)
    bg=np.array([(sc[q,1]-sc[q,2]).mean(0) for q in groups.values()]);bw=np.array([w[q].sum() for q in groups.values()])
    delta=v[1]-v[2];assert np.allclose(bw@bg,delta)
    om=(delta-bw[:,None]*bg)/(1-bw[:,None]);nf=sum(a["B_D"][0]>0 for a in folds);nb=int((bg[:,0]>0).sum())
    K=gram(errs["D"],w)-gram(errs["B"],w);Q=gram(P,w)
    assert np.allclose(quad(Z,K),delta,atol=1e-10)
    out={"status":"scored","mse":dict(zip(MODELS,v.tolist())),"D_N":(v[0]-v[1]).tolist(),"B_D":delta.tolist(),"B_N":(v[0]-v[2]).tolist(),"relative_B_D":safe_ratio(delta,v[1]),"folds":folds,"region_blocks":len(groups),"positive_region_blocks":(bg>0).sum(0).tolist(),"positive_folds":nf,"delete_one_region_block_range":[om.min(0).tolist(),om.max(0).tolist()]}
    out["screen"]=bool(delta[0]>0 and v[0,0]>v[2,0] and nf>=4 and (transfer or nb/len(groups)>=.6))
    return K,Q,out
def part(Z,g,Ks,Qs,fit):
    g=codes(g);G=portfolio(Z,g);R=Z-G;cnt=np.bincount(g)
    out={"groups":len(cnt),"singletons":int((cnt==1).sum()),"largest":int(cnt.max()),"gains":{},"reconstruction":{}}
    for d in DESIGNS:
        K=Ks[d];a,b,c=quad(G,K),quad(R,K),2*quad(G,K,R);t=np.asarray(fit[d]["B_D"])
        assert np.allclose(a+b+c,t,atol=1e-9)
        out["gains"][d]={"G":a.tolist(),"R":b.tolist(),"cross":c.tolist(),"total":t.tolist(),"G_fraction":safe_ratio(a,t)}
        if d!="region_transfer":
            q=Qs[d];e=quad(R,q);base=quad(Z-Z.mean(0),q)
            assert np.min(e)>-1e-10 and np.all(base>0)
            out["reconstruction"][d]={"loss":e.tolist(),"baseline":base.tolist(),"relative_reduction":(1-e/base).tolist()}
    return out
def challenge(Z,g,geo,K,Q,obs,seed,geo_conditioned,total):
    g=codes(g);strata=geo if geo_conditioned else np.zeros(len(g),int)
    groups=[np.flatnonzero(strata==s) for s in np.unique(strata)]
    mutable=[ix for ix in groups if len(set(g[ix]))>1]
    fraction=sum(len(ix) for ix in mutable)/len(g)
    rng=np.random.default_rng(seed);a=[];b=[]
    for _ in range(NREP):
        v=g.copy()
        for ix in mutable:
            v[ix]=rng.permutation(g[ix]);assert np.array_equal(np.sort(v[ix]),np.sort(g[ix]))
        assert np.array_equal(np.bincount(v),np.bincount(g))
        G=portfolio(Z,v);a.append(quad(Z-G,Q));b.append(quad(G,K))
    a,b=np.array(a),np.array(b);o=np.array(obs["reconstruction"]["spatial_5"]["loss"]);f=np.array(obs["gains"]["region_transfer"]["G"])
    oq=np.quantile(a,[.025,.5,.975],axis=0);fq=np.quantile(b,[.025,.5,.975],axis=0)
    # Compare gain rather than fraction; identical ranks when total positive.
    out={"n":NREP,"mutable_species_fraction":fraction,"observed_loss":o.tolist(),"null_loss_quantiles":oq.tolist(),"loss_rank_le":np.mean(a<=o+1e-12,axis=0).tolist(),"observed_G":f.tolist(),"null_G_quantiles":fq.tolist(),"G_rank_le":np.mean(b<=f+1e-12,axis=0).tolist()}
    out["observed_flight_G_fraction"]=float(f[0]/total) if total>1e-12 else None
    out["null_flight_G_fraction_quantiles"]=(fq[:,0]/total).tolist() if total>1e-12 else None
    out["pass"]=bool(total>1e-12 and fraction>=.5 and o[0]<oq[0,0] and f[0]>fq[2,0])
    return out
def check():
    p=np.array([[.5,.5,0],[0,.25,.75]]);Z=np.array([[0.,1.,2.],[1.,0.,3.],[3.,2.,1.]])
    Q=gram(p,np.array([.4,.6]));g=np.array([0,0,1]);G=portfolio(Z,g);R=Z-G
    assert np.allclose(quad(Z,Q),quad(G,Q)+quad(R,Q)+2*quad(G,Q,R))
    assert np.allclose(quad(R,Q),domain(np.array([.4,.6])@((p@R)**2)))
def cohort(threshold,M,Z,names,geo,parts,family,full,rc,reg,lat,clim,climcov):
    rich=M.sum(0);cov=np.divide(rich,full,out=np.zeros_like(full,float),where=full>0)
    ok=(rich>=5)&(cov>=threshold)
    if threshold==.2:assert int(ok.sum())==9310
    valid=ok&(climcov>=.5)&np.isfinite(clim).all(1)
    out={"species":len(names),"coverage_threshold":threshold,"range_eligible":int(ok.sum()),"climate_complete":int(valid.sum()),"regions":{}}
    use=[]
    for r in REGIONS:
        q=valid&(reg==r);b5=len(np.unique(rc[q]//5,axis=0));b10=len(np.unique(rc[q]//10,axis=0))
        s={"cells":int(q.sum()),"blocks_5":b5,"blocks_10":b10,"species":int(np.any(M[:,q],axis=1).sum()),"median_coverage":float(np.median(cov[q])) if q.any() else None,"admitted":bool(q.sum()>=100 and b5>=10 and b10>=10)}
        out["regions"][r]=s
        if s["admitted"]:use.append(r)
    keep=valid&np.isin(reg,use);out["cells"]=int(keep.sum());out["admitted_regions"]=use
    if keep.sum()<1000 or len(use)<4:out["status"]="insufficient_support";return out
    P=M[:,keep].T.astype(float);P/=P.sum(1,keepdims=True);assert np.allclose(P.sum(1),1)
    A=np.c_[np.log(full[keep]),np.log(rich[keep]),cov[keep],np.abs(lat[keep]),climcov[keep],clim[keep]]
    assert A.shape[1]==11 and np.isfinite(A).all()
    Ks={};Qs={};fit={}
    for d in DESIGNS:
        K,Q,s=scoring(A,P,Z,reg[keep],rc[keep],d);fit[d]=s
        if s["status"]!="scored":out.update(status="insufficient_fold_support",fit=fit);return out
        Ks[d]=K;Qs[d]=Q
    out["fit"]=fit;out["climate_screen"]=all(v["screen"] for v in fit.values())
    out["reference"]={k:part(Z,np.unique(g,return_inverse=True)[1],Ks,Qs,fit) for k,g in [("genus",[n.split("_")[0] for n in names]),("family",[family[n] for n in names])]}
    out["trees"]=[]
    for idx,pt,meta in parts:
        t={"tree_index":idx,"tree_meta":meta,"cuts":{str(age):part(Z,pt[str(age)],Ks,Qs,fit) for age in AGES}}
        g=pt["20"];o=t["cuts"]["20"];total=fit["region_transfer"]["B_D"][0]
        t["unrestricted"]=challenge(Z,g,geo,Ks["region_transfer"],Qs["spatial_5"],o,SEED+idx,False,total)
        t["geo_conditioned"]=challenge(Z,g,geo,Ks["region_transfer"],Qs["spatial_5"],o,SEED+idx,True,total)
        t["pass"]=bool(t["unrestricted"]["pass"] and t["geo_conditioned"]["pass"] and all(x["total"][0]>0 and x["G"][0]>0 and x["G_fraction"][0]>=.5 for x in o["gains"].values()))
        out["trees"].append(t);print("V11_TREE",threshold,idx,flush=True)
    out["passing_trees"]=sum(t["pass"] for t in out["trees"])
    out["screen"]=bool(out["climate_screen"] and out["passing_trees"]>=18)
    out["status"]="scored"
    return out
def main():
    out={"stage":"V11 cross-source wing trait phylogeographic portability","status":"START","domain_order":DOM}
    try:
        check();check_overlap()
        out["status"]="TREE_ACQUISITION";save(out);trees=tree_source(out)
        assert out["tree_source"]["release_sha256"]=="6f37526e6b5871d1a24fac5aa868835735359af902e1f555d1d7dfd1c8075e01"
        names,X,shape,crs,T=read_ranges(out);assert len(names)==1141
        w=wing(out);ids=[i for i,n in enumerate(names) if n in w.index];assert len(ids)==264
        nm=[names[i] for i in ids];M=X[ids];Z=w.loc[nm,["AR","WL_N_m2","mass_g_physical"]].to_numpy(float)
        Z[:,1:]=np.log(Z[:,1:]);Z=(Z-Z.mean(0))/Z.std(0);assert np.isfinite(Z).all()
        parts=[]
        for i,t in zip(INDICES,trees):
            a,b=partition_tree(t,names,{"wing":nm});parts.append((i,a["wing"],b))
        del trees
        mb=(Path("phylacine")/META).read_bytes();assert blob(mb)=="f2538374945f602f7c148d1a534be491895cd6e1"
        a=pd.read_csv(io.BytesIO(mb));a=a[a["Order.1.2"]=="Chiroptera"];family=dict(zip(a["Binomial.1.2"].map(norm),a["Family.1.2"]))
        rc=np.array(np.unravel_index(np.arange(X.shape[1]),shape)).T;tx,ty=edges(T,shape)
        lon,lat=Transformer.from_crs(crs,4326,always_xy=True).transform(T.c+(rc[:,1]+.5)*T.a,T.f+(rc[:,0]+.5)*T.e)
        reg=np.full(len(rc),"other",dtype="U24")
        for name,(l,h,b,t) in REGIONS.items():
            q=(lon>=l)&(lon<=h)&(lat>=b)&(lat<t);assert np.all(reg[q]=="other");reg[q]=name
        geo,info=geography(M,reg);out["geographic_null_strata"]=info
        out["status"]="CLIMATE_ACQUISITION";save(out);clim,climcov=climate(out,tx,ty)
        prior=json.loads((ROOT/"MACRO_FD_V5_MEASURED_STRUCTURE_RESULT.json").read_text())
        assert out["climate"]["sha256"]==prior["climate"]["sha256"] and out["climate"]["members"]==prior["climate"]["members"]
        out["cohorts"]={}
        for tag,cut in [("primary",.2),("higher_coverage",.5)]:
            out["status"]="COHORT_"+tag;save(out)
            out["cohorts"][tag]=cohort(cut,M,Z,nm,geo,parts,family,X.sum(0),rc,reg,lat,clim,climcov)
        out["primary_screen"]=out["cohorts"]["primary"].get("screen",False);out["status"]="COMPLETE"
    except Exception as e:
        out["last_status"]=out["status"];out["status"]="STOP";out["error_type"]=type(e).__name__
        if isinstance(e,AssertionError):out["validation"]=str(e)[:120]
    save(out);print("GLOBAL_V11_REPORT="+json.dumps(out,allow_nan=False),flush=True)
if __name__=="__main__":main()
