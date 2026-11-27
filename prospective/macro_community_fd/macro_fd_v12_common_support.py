"""V12 fixed common-support comparison of strategy and wing climate portability."""
import collections as C,hashlib,json,io
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Transformer
from macro_fd_v4_global_ranges import read_ranges,wing,REGIONS
from combine_v6b_coverage import acquire,COARSE
from macro_fd_v7_multidomain import mapping
from macro_fd_v5_structure import check_overlap,edges,climate,weights
from macro_fd_v9_strategy import predict,project,STRATA
from macro_fd_v10_phylo import tree_source,partition_tree,portfolio,AGES,INDICES,DESIGNS,SEED,NREP
from macro_fd_v11_wing_phylogeography import geography,codes,gram

ROOT=Path(__file__).resolve().parent
OUT=Path("macro_fd_v12_result.json")
MODELS={"N":0,"D":5,"B":11}
METRICS=["strategy","wing","mass","strategy_projected"]
DOMAINS=["strategy","wing","mass"]

def save(out):
    OUT.write_text(json.dumps(out,indent=2,allow_nan=False)+"\n")
    print("V12_STAGE="+out["status"],flush=True)

def domain(s):
    return np.stack([s[...,:12].sum(-1),s[...,12:14].mean(-1),s[...,14]],axis=-1)

def loss(actual,pred):
    assert np.allclose(pred[:,:12].sum(1),1)
    return np.c_[domain((actual-pred)**2),((actual[:,:12]-project(pred[:,:12]))**2).sum(1)]

def rel(a,b):
    a=np.asarray(a);b=np.asarray(b)
    return [float(x/y) if y>1e-12 else None for x,y in zip(a,b)]

def summarize(sc,reg,block,mask):
    w=weights(reg,block,mask);m=np.einsum("i,imk->mk",w[mask],sc[mask])
    bg=C.defaultdict(list)
    for i in np.flatnonzero(mask):bg[reg[i],int(block[i])].append(i)
    gain=np.array([(sc[v,1]-sc[v,2]).mean(0) for v in bg.values()])
    bw=np.array([w[v].sum() for v in bg.values()])
    d=m[1]-m[2];assert np.allclose(bw@gain,d)
    return {"cells":int(mask.sum()),"region_blocks":len(bg),"mse":dict(zip(MODELS,m.tolist())),
       "B_D":d.tolist(),"B_N":(m[0]-m[2]).tolist(),"D_N":(m[0]-m[1]).tolist(),
       "relative_B_D":rel(d,m[1]),"positive_blocks":(gain>0).sum(0).tolist()}

def scoring(A,P,Z,reg,rc,design):
    grain=10 if design=="spatial_10" else 5;transfer=design=="region_transfer"
    keys=[tuple(v//grain) for v in rc];un=sorted(set(keys),key=lambda v:hashlib.sha256(str(v).encode()).hexdigest())
    ix={v:i for i,v in enumerate(un)};block=np.array([ix[v] for v in keys])
    split=reg if transfer else block%5;Y=P@Z
    assert np.allclose(Y[:,:12].sum(1),1)
    errs={k:np.empty_like(P) for k in ("D","B")}
    sc=np.full((len(P),3,4),np.nan);invalid=np.zeros((len(P),3),bool);folds=[]
    for k in sorted(set(split)):
        te=split==k;tr=~te
        if len(set(block[te]))<5 or len(set(reg[tr]))<(3 if transfer else 4) or (not transfer and set(reg[tr])!=set(reg)):
            return None,None,{"status":"insufficient_fold_support","fold":str(k)}
        if not transfer:assert not set(block[te])&set(block[tr])
        w=weights(reg,block,tr)
        for i,(m,n) in enumerate(MODELS.items()):
            p=predict(A,P,w,tr,te,n);pred=p@Z
            if m in errs:errs[m][te]=P[te]-p
            assert np.allclose(pred,predict(A,Y,w,tr,te,n),atol=1e-10)
            sc[te,i]=loss(Y[te],pred)
            invalid[te,i]=np.any((pred[:,:12]<-1e-10)|(pred[:,:12]>1+1e-10),axis=1)
        a=summarize(sc,reg,block,te);a["fold"]=str(k);folds.append(a)
    assert np.isfinite(sc).all()
    mask=np.ones(len(P),bool);w=weights(reg,block,mask)
    K=gram(errs["D"],w)-gram(errs["B"],w);Q=gram(P,w)
    out=summarize(sc,reg,block,mask)
    assert np.allclose(domain(np.sum(Z*(K@Z),axis=0)),out["B_D"][:3],atol=1e-10)
    out.update(status="scored",folds=folds,regions={r:summarize(sc,reg,block,reg==r) for r in sorted(set(reg))},
               invalid_fraction=dict(zip(MODELS,(w@invalid).tolist())),
               positive_folds=np.sum(np.array([f["B_D"] for f in folds])>0,axis=0).tolist())
    return K,Q,out

def portability(fit):
    keys=sorted(fit["region_transfer"]["regions"])
    def values(losses):
        vals=np.asarray([rel(v["B_D"],v["mse"]["D"]) for v in losses],float)
        assert np.isfinite(vals).all()
        L=vals[:2].mean(0)-vals[2]
        each=vals[:2]-vals[2]
        return {"relative_gains":vals.tolist(),"loss":L.tolist(),"wing_minus_strategy":float(L[1]-L[0]),
                "wing_minus_projected_strategy":float(L[1]-L[3]),"grain_contrasts":(each[:,1]-each[:,0]).tolist()}
    total=values([fit[d] for d in DESIGNS])
    total["region_contrasts"]={r:values([fit[d]["regions"][r] for d in DESIGNS]) for r in keys}
    total["positive_regions"]=sum(v["wing_minus_strategy"]>0 for v in total["region_contrasts"].values())
    omit={}
    for r in keys:
        agg=[]
        for d in DESIGNS:
            regs=[fit[d]["regions"][s] for s in keys if s!=r]
            a=np.mean([v["mse"]["D"] for v in regs],axis=0);b=np.mean([v["mse"]["B"] for v in regs],axis=0)
            agg.append({"mse":{"D":a},"B_D":a-b})
        omit[r]=values(agg)["wing_minus_strategy"]
    total["omit_region_contrasts"]=omit
    assert np.allclose([fit[d]["mse"]["D"] for d in DESIGNS],[np.mean([fit[d]["regions"][r]["mse"]["D"] for r in keys],axis=0) for d in DESIGNS])
    spatial=all(all(fit[d]["B_D"][i]>0 and fit[d]["B_N"][i]>0 for i in (0,1)) for d in DESIGNS[:2])
    total["screen"]=bool(spatial and total["wing_minus_strategy"]>0 and min(total["grain_contrasts"])>0 and total["positive_regions"]>=4 and min(omit.values())>0 and total["wing_minus_projected_strategy"]>0)
    return total

def quad(Z,K,B=None):
    return domain(np.sum(Z*(K@(Z if B is None else B)),axis=0))

def partition(Z,g,Ks,Qs,fit):
    g=codes(g);G=portfolio(Z,g);R=Z-G
    out={"groups":int(g.max()+1),"reconstruction":{},"gain":{}}
    for d in DESIGNS:
        K=Ks[d];a,b,c=quad(G,K),quad(R,K),2*quad(G,K,R);t=np.asarray(fit[d]["B_D"][:3])
        assert np.allclose(a+b+c,t,atol=1e-9)
        out["gain"][d]={"G":a.tolist(),"R":b.tolist(),"cross":c.tolist(),"total":t.tolist(),"G_fraction":rel(a,t)}
        if d!="region_transfer":
            Q=Qs[d];e=quad(R,Q);base=quad(Z-Z.mean(0),Q)
            assert np.all(e>=-1e-10) and np.all(base>0)
            out["reconstruction"][d]={"loss":e.tolist(),"baseline":base.tolist(),"relative_reduction":(1-e/base).tolist()}
    return out

def random_challenge(Z,g,geo,Q,obs,seed):
    g=codes(g);groups=[np.flatnonzero(geo==s) for s in np.unique(geo)]
    mutable=[ix for ix in groups if len(set(g[ix]))>1]
    rng=np.random.default_rng(seed);losses=[]
    for i in range(NREP):
        v=g.copy()
        for ix in mutable:
            v[ix]=rng.permutation(g[ix]);assert np.array_equal(np.sort(v[ix]),np.sort(g[ix]))
        assert np.array_equal(np.bincount(v),np.bincount(g))
        losses.append(quad(Z-portfolio(Z,v),Q))
    a=np.array(losses);o=np.asarray(obs["reconstruction"]["spatial_5"]["loss"]);q=np.quantile(a,[.025,.5,.975],axis=0)
    return {"n":NREP,"mutable_fraction":sum(len(ix) for ix in mutable)/len(g),"actual_loss":o.tolist(),"random_quantiles":q.tolist(),"rank_le":np.mean(a<=o+1e-12,axis=0).tolist(),"below_q025":(o<q[0]).tolist()}

def cohort(tag,tab,names,X,Z0,allnames,parts,threshold,rc,reg,lat,clim,climcov):
    lookup={n:i for i,n in enumerate(allnames)};ids=[lookup[n] for n in names]
    ix={n:i for i,n in enumerate(tab.index)}
    take=np.array([ix[n] for n in names]);Z=Z0[take]
    M=X[ids];full=X.sum(0);rich=M.sum(0);cov=np.divide(rich,full,out=np.zeros_like(full,float),where=full>0)
    ok=(rich>=5)&(cov>=threshold)
    if tag=="primary":assert int(ok.sum())==9018
    eligible=ok&(climcov>=.5)&np.isfinite(clim).all(1)
    out={"species":len(names),"coverage_threshold":threshold,"range_eligible":int(ok.sum()),"climate_complete":int(eligible.sum()),"regions":{}}
    use=[]
    for r in REGIONS:
        q=eligible&(reg==r);b5=len(np.unique(rc[q]//5,axis=0));b10=len(np.unique(rc[q]//10,axis=0))
        s={"cells":int(q.sum()),"blocks_5":b5,"blocks_10":b10,"matched_species":int(np.any(M[:,q],axis=1).sum()),"median_coverage":float(np.median(cov[q])) if q.any() else None,"admitted":bool(q.sum()>=100 and b5>=10 and b10>=10)}
        out["regions"][r]=s
        if s["admitted"]:use.append(r)
    keep=eligible&np.isin(reg,use);out["cells"]=int(keep.sum());out["admitted_regions"]=use
    if keep.sum()<1000 or len(use)<4:out["status"]="insufficient_support";return out
    P=M[:,keep].T.astype(float);P/=P.sum(1,keepdims=True)
    A=np.c_[np.log(full[keep]),np.log(rich[keep]),cov[keep],np.abs(lat[keep]),climcov[keep],clim[keep]]
    Ks={};Qs={};fit={}
    for d in DESIGNS:
        K,Q,s=scoring(A,P,Z,reg[keep],rc[keep],d);fit[d]=s
        if s["status"]!="scored":out.update(status="insufficient_fold_support",fit=fit);return out
        Ks[d]=K;Qs[d]=Q
    out["fit"]=fit;out["portability"]=portability(fit)
    geo,info=geography(M,reg);out["geo_strata"]=info
    out["trees"]=[]
    for i,p,meta in parts:
        t={"tree_index":i,"meta":meta,"cuts":{str(age):partition(Z,p[tag][str(age)],Ks,Qs,fit) for age in AGES}}
        t["random_20"]=random_challenge(Z,p[tag]["20"],geo,Qs["spatial_5"],t["cuts"]["20"],SEED+i)
        out["trees"].append(t)
    out["tree_summary"]={}
    for age in AGES:
        vals=[t["cuts"][str(age)] for t in out["trees"]]
        out["tree_summary"][str(age)]={d:np.quantile([v["reconstruction"][d]["relative_reduction"] for v in vals],[0,.5,1],axis=0).tolist() for d in ("spatial_5","spatial_10")}
    out["random_reconstruction_pass_counts"]=np.sum([v["random_20"]["below_q025"] for v in out["trees"]],axis=0).tolist()
    out["status"]="scored";return out

def main():
    out={"stage":"V12 common-support functional geography portability","status":"START","metric_order":METRICS,"phylo_domain_order":DOMAINS}
    try:
        check_overlap()
        names,X,shape,crs,T=read_ranges(out);assert len(names)==1141
        w=wing(out);a,b,c=acquire(out);alltab=mapping(a,b,names,w,out)
        tab=alltab.loc[alltab.index.intersection(w.index)];assert len(tab)==234
        m=w.loc[tab.index,["AR","WL_N_m2","mass_g_physical"]].to_numpy(float)
        m[:,1:]=np.log(m[:,1:]);m=(m-m.mean(0))/m.std(0)
        S=np.eye(4)[[STRATA.index(v) for v in tab.stratum]]
        J=(tab[COARSE].to_numpy(float)[:,:,None]*S[:,None,:]).reshape(len(tab),12)
        Z=np.c_[J,m];assert np.allclose(J.sum(1),1) and np.isfinite(Z).all()
        rosters={"primary":tab.index.tolist(),"higher_coverage":tab.index.tolist(),"no_split":tab.index[tab.no_transfer].tolist()}
        out["roster_counts"]={k:len(v) for k,v in rosters.items()}
        out["status"]="TREE_ACQUISITION";save(out);trees=tree_source(out)
        assert out["tree_source"]["release_sha256"]=="6f37526e6b5871d1a24fac5aa868835735359af902e1f555d1d7dfd1c8075e01"
        parts=[]
        for i,t in zip(INDICES,trees):
            p,q=partition_tree(t,names,rosters);parts.append((i,p,q))
        del trees
        rc=np.array(np.unravel_index(np.arange(X.shape[1]),shape)).T;tx,ty=edges(T,shape)
        lon,lat=Transformer.from_crs(crs,4326,always_xy=True).transform(T.c+(rc[:,1]+.5)*T.a,T.f+(rc[:,0]+.5)*T.e)
        reg=np.full(len(rc),"other",dtype="U24")
        for n,(l,h,b,t) in REGIONS.items():
            q=(lon>=l)&(lon<=h)&(lat>=b)&(lat<t);assert np.all(reg[q]=="other");reg[q]=n
        out["status"]="CLIMATE_ACQUISITION";save(out);clim,climcov=climate(out,tx,ty)
        prior=json.loads((ROOT/"MACRO_FD_V5_MEASURED_STRUCTURE_RESULT.json").read_text())
        assert out["climate"]["sha256"]==prior["climate"]["sha256"] and out["climate"]["members"]==prior["climate"]["members"]
        out["cohorts"]={}
        for tag,cut in [("primary",.2),("higher_coverage",.5),("no_split",.2)]:
            out["status"]="COHORT_"+tag;save(out)
            out["cohorts"][tag]=cohort(tag,tab,rosters[tag],X,Z,names,parts,cut,rc,reg,lat,clim,climcov)
        x=out["cohorts"]["primary"];s=out["cohorts"]["no_split"]
        sens=bool(s["status"]=="scored" and s["portability"]["wing_minus_strategy"]>0 and s["portability"]["wing_minus_projected_strategy"]>0)
        out["primary_screen"]={"common":bool(x.get("portability",{}).get("screen",False)),"no_split_direction":sens,"pass":bool(x.get("portability",{}).get("screen",False) and sens)}
        out["status"]="COMPLETE"
    except Exception as e:
        out["last_status"]=out["status"];out["status"]="STOP";out["error_type"]=type(e).__name__
        if isinstance(e,AssertionError):out["validation"]=str(e)[:120]
    save(out);print("GLOBAL_V12_REPORT="+json.dumps(out,allow_nan=False),flush=True)
if __name__=="__main__":main()
