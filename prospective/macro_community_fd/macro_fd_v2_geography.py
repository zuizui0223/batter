"""V2: continental recorded-assemblage trait geography, fixed label permutations."""
import collections as C, json, math
from pathlib import Path
import numpy as np
import pandas as pd
import requests
from macro_fd_v1 import source,traits,yes,mpd,K,JOIN,DOM

METRICS=DOM+["sensory_minus_flight"]
SEED=20261127
NREP=10000

def unit_weights(f,ix,D,grain,pooled,tag):
    d=f[["snapshot_species_key","dataset_key","year",*K]].copy()
    d["period"]=d.year.astype(int)//5
    if pooled:d["dataset_key"]="pooled"
    d=d.drop_duplicates(["snapshot_species_key",*K,"dataset_key","period"])
    d["gx"]=d.cell_x//grain;d["gy"]=d.cell_y//grain
    n=len(ix);records=[];drop=C.Counter();taxa=set()
    candidate=0;med=[]
    for (provider,period,gx,gy),q in d.groupby(["dataset_key","period","gx","gy"],sort=True):
        candidate+=1
        nf=len(q[K].drop_duplicates())
        counts=q.groupby("snapshot_species_key").size()
        ok=counts.index.isin(ix)
        cover=float(ok.mean());inc=float(counts[ok].sum()/counts.sum())
        if nf<5:drop["fine_cells_lt5"]+=1;continue
        if ok.sum()<3:drop["complete_taxa_lt3"]+=1;continue
        if min(cover,inc)<.8:drop["coverage_lt80pct"]+=1;continue
        ids=np.array([ix[k] for k in counts.index[ok]])
        taxa.update(ids.tolist());med.append([len(counts),nf,len(q),cover,inc])
        block=(int(gx)*grain//200,int(gy)*grain//200)
        W=[]
        for p in [np.ones(len(ids)),counts[ok].to_numpy(float)]:
            p=p/p.sum();w=np.outer(p,p);np.fill_diagonal(w,0);w/=w.sum()
            full=np.zeros((n,n));full[np.ix_(ids,ids)]=w
            assert np.allclose(full,full.T) and np.allclose(np.diag(full),0) and abs(full.sum()-1)<1e-10
            assert np.allclose(np.einsum("ij,ijc->c",full,D),mpd(ids,p,D))
            W.append(full)
        records.append((provider,int(period),block,np.array(W)))
    stat={"candidate_units":candidate,"eligible_units":len(records),"excluded":dict(drop),"taxa":len(taxa),"providers":len({v[0] for v in records}),"blocks":len({v[2] for v in records})}
    if med:stat["median_support"]=dict(zip(["richness","fine_cells","species_cell_incidences","richness_coverage","incidence_coverage"],np.median(med,axis=0).tolist()))
    admitted=len(records)>=50 and stat["blocks"]>=15 and stat["taxa"]>=10 and (pooled or stat["providers"]>=10)
    stat["status"]="admitted" if admitted else "insufficient_support"
    if not admitted:return stat,[]
    g=C.defaultdict(list)
    for s,p,b,w in records:g[(s,p,b)].append(w)
    bb=C.defaultdict(list)
    for (s,p,b),v in g.items():bb[b].append(np.mean(v,axis=0))
    blocks=np.array([np.mean(v,axis=0) for b,v in sorted(bb.items())])
    mat=blocks.mean(0)
    assert np.allclose(mat.sum((1,2)),1) and np.allclose(blocks.sum((2,3)),1)
    stat["strata"]=len(g);stat["scored_blocks"]=len(blocks)
    return stat,[(tag+"_equal",mat[0],blocks[:,0]),(tag+"_incidence",mat[1],blocks[:,1])]

def expected_distance(D,groups):
    E=np.zeros_like(D);n=len(D)
    assert sorted(sum([list(g) for g in groups],[]))==list(range(n))
    for i,g in enumerate(groups):
        g=np.array(g);m=len(g)
        for j,h in enumerate(groups):
            h=np.array(h)
            if i==j:
                if m>1:
                    a=D[g][:,g].sum((0,1))/(m*(m-1))
                    for s in g:
                        for t in g:
                            if s!=t:E[s,t]=a
            else:
                a=D[g][:,h].mean((0,1))
                E[np.ix_(g,h)]=a
    assert np.allclose(E,E.transpose(1,0,2))
    return E

def permutations(groups,n):
    rng=np.random.default_rng(SEED)
    out=np.tile(np.arange(n),(NREP,1))
    for g in groups:
        g=np.array(g)
        if len(g)>1:
            out[:,g]=g[np.argsort(rng.random((NREP,len(g))),axis=1)]
        assert np.all(np.sort(out[:,g],axis=1)==np.sort(g))
    assert np.all(np.sort(out,axis=1)==np.arange(n))
    return out

def add_metric(x):
    return np.concatenate((x,(x[...,3]-x[...,1])[...,None]),axis=-1)

def null_results(cases,D,groups):
    if not cases:return {}
    n=len(D);E=expected_distance(D,groups);perms=permutations(groups,n)
    mats=np.array([m for _,m,_ in cases]);M=mats.reshape(len(mats),-1)
    obs=add_metric(np.einsum("kij,ijc->kc",mats,D))
    ex=add_metric(np.einsum("kij,ijc->kc",mats,E))
    sims=[]
    for i in range(0,NREP,128):
        pp=perms[i:i+128];pD=D[pp[:,:,None],pp[:,None,:]]
        scores=(pD.transpose(0,3,1,2).reshape(-1,n*n)@M.T).reshape(len(pp),4,len(mats)).transpose(0,2,1)
        sims.append(add_metric(scores))
    sims=np.concatenate(sims)
    assert sims.shape==(NREP,len(cases),5)
    out={}
    for k,(name,m,blocks) in enumerate(cases):
        sim=sims[:,k];mean=sim.mean(0);sd=sim.std(0)
        err=mean-ex[k];assert np.all(np.abs(err)<=7*sd/np.sqrt(NREP)+1e-9)
        bd=add_metric(np.einsum("bij,ijc->bc",blocks,D-E));excess=obs[k]-ex[k]
        assert np.allclose(bd.mean(0),excess)
        omit=(bd.sum(0)-bd)/(len(bd)-1)
        out[name]={"observed":obs[k].tolist(),"analytic_null_mean":ex[k].tolist(),"simulated_null_mean":mean.tolist(),"excess":excess.tolist(),"null_sd":sd.tolist(),"q025":np.quantile(sim,.025,axis=0).tolist(),"q975":np.quantile(sim,.975,axis=0).tolist(),"rank_le":np.mean(sim<=obs[k]+1e-12,axis=0).tolist(),"negative_blocks":np.sum(bd<0,axis=0).tolist(),"positive_blocks":np.sum(bd>0,axis=0).tolist(),"blocks":len(bd),"delete_one_block_mean_range":[omit.min(0).tolist(),omit.max(0).tolist()]}
    return out

def main():
    out={"stage":"continental macro trait geography conditional on reported assemblages","metric_order":METRICS,"seed":SEED,"null_draws":NREP}
    try:
        p=source(out)
        dtype={k:str for k in JOIN if k not in K}
        e=pd.read_csv(p["environment"],dtype=dtype,keep_default_na=False,low_memory=False)
        a=pd.read_csv(p["flags"],dtype=dtype,keep_default_na=False,low_memory=False)
        assert e.records.sum()==a.records.sum()==219960 and len(e[K].drop_duplicates())==11006 and e.snapshot_species_key.nunique()==39
        assert not e.duplicated(JOIN).any() and not a.duplicated(JOIN).any()
        ix,D=traits(p["physical"],p["crosswalk"],e,out)
        assert len(ix)==27 and np.allclose(out["trait_roster"]["uniform_pair_reference"],[54/26]*4)
        names=out["trait_roster"]["species"];gs=C.defaultdict(list)
        for i,v in enumerate(names):gs[v.split()[0].casefold()].append(i)
        groups=list(gs.values())
        out["genus_group_sizes"]=sorted(map(len,groups),reverse=True)
        f=e.merge(a[JOIN+["records","flag_explicit_captive","flag_roost_context"]].rename(columns={"records":"audit_records"}),on=JOIN,how="outer",validate="one_to_one",indicator=True)
        assert f._merge.eq("both").all() and f.records.eq(f.audit_records).all() and f.flag_explicit_captive.sum()==0 and f.flag_roost_context.sum()==684
        f["clean_records"]=f.records-f.flag_roost_context
        assert f.clean_records.ge(0).all()
        f=f[f.clean_records.gt(0)&f.dataset_key.ne("")&f.year.str.fullmatch(r"20[0-9]{2}")&f.license.isin(["CC_BY_4_0","CC0_1_0","CC_BY_NC_4_0"])].copy()
        forest=f[yes(f.forest_profile_support)].copy()
        out["support"]={k:{"clean_records":int(v.clean_records.sum()),"cells":len(v[K].drop_duplicates()),"species_labels":int(v.snapshot_species_key.nunique()),"providers":int(v.dataset_key.nunique())} for k,v in [("all",f),("forest",forest)]}
        out["units"]={};cases=[]
        for grain in [100,200]:
            for n,d in [("all",f),("forest",forest)]:
                for pool in [False,True]:
                    tag=f"{n}_{grain}_{'pooled' if pool else 'provider'}"
                    stat,v=unit_weights(d,ix,D,grain,pool,tag)
                    out["units"][tag]=stat;cases.extend(v)
        out["unrestricted_null"]=null_results(cases,D,[list(range(len(ix)))])
        out["genus_conditioned_null"]=null_results(cases,D,groups)
        ng=out["genus_conditioned_null"]
        check=[]
        for grain in [100,200]:
            k=f"all_{grain}_provider"
            e=ng.get(k+"_equal");i=ng.get(k+"_incidence")
            check.append(bool(e and i and e["excess"][-1]<0 and e["rank_le"][-1]<=.025 and i["excess"][-1]<0 and e["negative_blocks"][-1]/e["blocks"]>=.6 and i["negative_blocks"][-1]/i["blocks"]>=.6))
        out["primary_screen"]={"by_grain":check,"pass":all(check)}
        out["status"]="completed"
    except Exception as e:
        out.update(status="stopped",error_type=type(e).__name__,error="transport error" if isinstance(e,requests.RequestException) else str(e)[:180])
    Path("macro_fd_v2_result.json").write_text(json.dumps(out,indent=2,allow_nan=False)+"\n")
    print("MACRO_FD_V2_REPORT="+json.dumps(out,allow_nan=False),flush=True)
if __name__=="__main__":main()
