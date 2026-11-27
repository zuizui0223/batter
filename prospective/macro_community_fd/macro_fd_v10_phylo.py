"""V10 time-calibrated partition of V9 geography prediction. Aggregate output only."""
import collections as C,hashlib,io,json,math,re,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import requests
from Bio import Phylo
from pyproj import Transformer
from macro_fd_v4_global_ranges import read_ranges,wing,REGIONS,META,blob
from combine_v6b_coverage import acquire,norm,COARSE
from macro_fd_v7_multidomain import mapping
from macro_fd_v5_structure import check_overlap,edges,climate,gedi,weights
from macro_fd_v9_strategy import predict,STRATA

ROOT=Path(__file__).resolve().parent
OUT=Path("macro_fd_v10_result.json")
URL="https://github.com/MegaPast2Future/PHYLACINE_1.2/releases/download/v1.2.1/PHYLACINE_1.2.1.zip"
TREE_SHA="85fbb088e559c6b9d6b2db21b8830b4dd994bb81aa09e512d676b642b545d7c1"
TREE_BYTES=132041786
AGES=[5,10,20,40]
INDICES=[25+50*k for k in range(20)]
SEED=20261127
NREP=199
DESIGNS=["spatial_5","spatial_10","region_transfer"]

def save(out):
    OUT.write_text(json.dumps(out,indent=2,allow_nan=False)+"\n")
    print("V10_STAGE="+out["status"],flush=True)

def tree_source(out):
    p=Path("phylacine_release.zip");n=0;h=hashlib.sha256()
    with requests.get(URL,stream=True,timeout=(30,90)) as r:
        out["tree_http_status"]=r.status_code
        r.raise_for_status()
        with p.open("wb") as f:
            for b in r.iter_content(1024*1024):
                n+=len(b);assert n<=110*1024**2
                h.update(b);f.write(b)
    assert n==106362537,"release byte size"
    with zipfile.ZipFile(p) as z:
        hits=[i for i in z.infolist() if Path(i.filename).name=="Complete_phylogeny.nex"]
        assert len(hits)==1 and hits[0].file_size==TREE_BYTES,"tree archive member"
        b=z.read(hits[0]) # ZipFile read verifies member CRC.
        assert len(b)==TREE_BYTES and hashlib.sha256(b).hexdigest()==TREE_SHA,"tree member hash"
    p.unlink()
    out["tree_source"]={"release_bytes":n,"release_sha256":h.hexdigest(),"member":hits[0].filename,"member_bytes":len(b),"member_sha256":TREE_SHA,"indices_zero_based":INDICES}
    # NEXUS tree records are semicolon terminated. No other tree blocks selected.
    s=b.decode("utf-8-sig");del b
    assert s.lstrip().upper().startswith("#NEXUS")
    stmts=s.split(";");del s
    def is_tree(v):return re.match(r"\s*(?:tree|utree)\s+",v,re.I) is not None
    records=[v for v in stmts if is_tree(v)]
    trans=[v for v in stmts if re.match(r"\s*translate\b",v,re.I)]
    assert len(records)==1000 and len(trans)<=1,"NEXUS inventory"
    out["tree_source"]["tree_count"]=len(records);out["tree_source"]["translation_present"]=bool(trans)
    selected="#NEXUS\nBegin trees;\n"+"".join(v+";\n" for v in trans)+"".join(records[i]+";\n" for i in INDICES)+"End;\n"
    del stmts,records,trans
    trees=list(Phylo.parse(io.StringIO(selected),"nexus"))
    assert len(trees)==20,"selected tree count"
    return trees

def partition_tree(tree,allnames,rosters):
    dep={tree.root:0.};parents={tree.root:None};tips={}
    todo=[tree.root]
    while todo:
        c=todo.pop()
        if not c.clades:
            assert c.name is not None
            n=norm(str(c.name).strip("'\""))
            assert n not in tips,"duplicate normalized tip"
            tips[n]=c
        for k in c.clades:
            l=k.branch_length
            assert l is not None and np.isfinite(l) and l>=0,"branch length"
            parents[k]=c;dep[k]=dep[c]+l;todo.append(k)
    assert len(tips)==5831,"full tree tip count"
    assert set(allnames)<=set(tips),"positive range label missing"
    height=max(dep[tips[n]] for n in allnames)
    spread=height-min(dep[tips[n]] for n in allnames)
    assert height>40 and spread<=.05,"positive current tips not contemporaneous"
    labels_by_age={}
    for age in AGES:
        cut=height-age
        a={}
        for n in allnames:
            c=tips[n]
            assert dep[c]>=cut
            while parents[c] is not None and dep[parents[c]]>=cut-1e-10:c=parents[c]
            a[n]=id(c)
        labels_by_age[age]=a
    for x,y in zip(AGES,AGES[1:]):
        groups=C.defaultdict(set)
        for n in allnames:groups[labels_by_age[x][n]].add(labels_by_age[y][n])
        assert all(len(v)==1 for v in groups.values()),"nonnested partitions"
    out={}
    for tag,names in rosters.items():
        out[tag]={str(age):np.unique([labels_by_age[age][n] for n in names],return_inverse=True)[1] for age in AGES}
    return out,{"tips":len(tips),"positive_tip_depth":height,"positive_tip_spread":spread}

def fit_errors(A,P,J0,reg,rc,design,prior):
    grain=10 if design=="spatial_10" else 5
    transfer=design=="region_transfer"
    keys=[tuple(v//grain) for v in rc]
    unique=sorted(set(keys),key=lambda v:hashlib.sha256(str(v).encode()).hexdigest())
    ix={v:i for i,v in enumerate(unique)};block=np.array([ix[v] for v in keys])
    split=reg if transfer else block%5
    e0=np.empty_like(P);e1=np.empty_like(P)
    for k in sorted(set(split)):
        te=split==k;tr=~te
        assert len(set(block[te]))>=5 and len(set(reg[tr]))>=(3 if transfer else 4)
        if not transfer:assert not set(block[tr])&set(block[te]) and set(reg[tr])==set(reg)
        w=weights(reg,block,tr)
        for n,err in [(0,e0),(12,e1)]:
            pred=predict(A,P,w,tr,te,n);err[te]=P[te]-pred
            j=predict(A,P@J0,w,tr,te,n)
            assert np.allclose(pred@J0,j,atol=1e-10)
    w=weights(reg,block,np.ones(len(P),bool))
    def gram(p):
        t=p*np.sqrt(w[:,None]);return t.T@t
    m0=float(w@np.sum((e0@J0)**2,axis=1));m1=float(w@np.sum((e1@J0)**2,axis=1))
    target=prior["tests"][design]["mse"]
    assert abs(m0-target["N"][0])<1e-9 and abs(m1-target["B"][0])<1e-9,"V9 MSE replay"
    K=gram(e0)-gram(e1);assert np.allclose(K,K.T,atol=1e-11)
    Q=gram(P)
    total=m0-m1
    assert total>0 and np.isclose(np.sum(J0*(K@J0)),total,atol=1e-10)
    return K,Q,{"N":m0,"B":m1,"gain":total,"blocks":len(unique)}

def prepare(tag,tab,names,X,env,clim,climcov,veg,vegcov,lat,reg,rc,prior):
    ids={n:i for i,n in enumerate(names)};m=X[[ids[n] for n in tab.index]]
    full=X.sum(0);rich=m.sum(0);cov=np.divide(rich,full,out=np.zeros_like(full,float),where=full>0)
    keep=env&(rich>=5)&(cov>=.8)&np.isin(reg,list(REGIONS))
    assert int(keep.sum())==prior["analysis_cells"] and set(reg[keep])==set(prior["admitted_regions"])
    for r in REGIONS:assert int((keep&(reg==r)).sum())==prior["region_support"][r]["cells"]
    S=np.eye(4)[[STRATA.index(v) for v in tab.stratum]]
    J0=(tab[COARSE].to_numpy(float)[:,:,None]*S[:,None,:]).reshape(len(tab),12)
    P=m[:,keep].T.astype(float);P/=P.sum(1,keepdims=True)
    assert np.allclose(P.sum(1),1) and np.allclose(J0.sum(1),1)
    A=np.c_[np.log(full[keep]),np.log(rich[keep]),cov[keep],np.abs(lat[keep]),clim[keep],vegcov[keep],climcov[keep]]
    assert A.shape[1]==12 and np.isfinite(A).all()
    Ks={};Qs={};replay={}
    for design in DESIGNS:
        K,Q,s=fit_errors(A,P,J0,reg[keep],rc[keep],design,prior)
        Ks[design]=K;Qs[design]=Q;replay[design]=s
    return {"J0":J0,"Ks":Ks,"Qs":Qs,"replay":replay,"names":tab.index.tolist(),"n":int(keep.sum())}

def portfolio(J,g):
    ng=int(g.max())+1;cnt=np.bincount(g,minlength=ng);assert np.all(cnt>0)
    a=np.zeros((ng,J.shape[1]));np.add.at(a,g,J)
    return (a/cnt[:,None])[g]

def quadratic(A,K,B=None):
    return float(np.sum(A*(K@(A if B is None else B))))

def partition_result(data,g):
    J=data["J0"];G=portfolio(J,g);R=J-G
    assert np.allclose(G.sum(1),1) and np.allclose(R.sum(1),0)
    cnt=np.bincount(g)
    out={"groups":len(cnt),"singleton_groups":int((cnt==1).sum()),"largest_group":int(cnt.max()),"reconstruction":{},"gains":{}}
    for d in DESIGNS:
        K=data["Ks"][d];Q=data["Qs"][d]
        g0=quadratic(G,K);r0=quadratic(R,K);cross=2*quadratic(G,K,R);total=data["replay"][d]["gain"]
        assert abs(g0+r0+cross-total)<1e-9
        out["gains"][d]={"G":g0,"R":r0,"cross":cross,"J":total,"G_fraction":g0/total}
        if d!="region_transfer":
            err=quadratic(R,Q);base=quadratic(J-J.mean(0),Q);assert err>=-1e-10 and base>0
            out["reconstruction"][d]={"loss":err,"global_roster_mean_loss":base,"relative_reduction":1-err/base}
    return out

def null_challenge(data,g,obs,seed):
    rng=np.random.default_rng(seed);J=data["J0"];K=data["Ks"]["region_transfer"];Q=data["Qs"]["spatial_5"];total=data["replay"]["region_transfer"]["gain"]
    losses=[];gains=[];cnt=np.bincount(g)
    for i in range(NREP):
        v=g[rng.permutation(len(g))]
        assert np.array_equal(np.bincount(v),cnt)
        G=portfolio(J,v)
        losses.append(quadratic(J-G,Q));gains.append(quadratic(G,K)/total)
    a=np.asarray(losses);b=np.asarray(gains);o=obs["reconstruction"]["spatial_5"]["loss"];f=obs["gains"]["region_transfer"]["G_fraction"]
    r={"n":NREP,"observed_loss":o,"random_loss_quantiles":np.quantile(a,[.025,.5,.975]).tolist(),"loss_rank_le":float(np.mean(a<=o+1e-12)),
       "observed_gain_fraction":f,"random_gain_fraction_quantiles":np.quantile(b,[.025,.5,.975]).tolist(),"gain_rank_le":float(np.mean(b<=f+1e-12))}
    r["pass"]=bool(o<r["random_loss_quantiles"][0] and f>r["random_gain_fraction_quantiles"][2] and all(v["G"]>0 and v["G_fraction"]>=.5 for v in obs["gains"].values()))
    return r

def check():
    J=np.array([[1.,0.],[0.,1.],[.5,.5]])
    g=np.array([0,0,1]);G=portfolio(J,g);assert np.allclose(G,.5)
    Q=np.array([[.2,.1,0],[.1,.3,0],[0,0,.2]])
    R=J-G
    assert np.isclose(quadratic(J,Q),quadratic(G,Q)+quadratic(R,Q)+2*quadratic(G,Q,R))
    # Independent direct cell replay for positive semidefinite gram.
    P=np.array([[.5,.5,0],[0,.5,.5]]);w=np.array([.4,.6]);K=P.T@(w[:,None]*P)
    assert np.isclose(quadratic(R,K),w@np.sum((P@R)**2,axis=1))

def summarize(data,trees,tag,families):
    names=data["names"];out={"cells":data["n"],"species":len(names),"V9_replay":data["replay"],"reference":{},"trees":[]}
    for name,g in [("genus",np.unique([v.split("_")[0] for v in names],return_inverse=True)[1]),("family",np.unique([families[v] for v in names],return_inverse=True)[1])]:
        out["reference"][name]=partition_result(data,g)
    for idx,parts,meta in trees:
        r={"tree_index":idx,"tree_meta":meta,"cuts":{}}
        for age in AGES:r["cuts"][str(age)]=partition_result(data,parts[tag][str(age)])
        r["primary_random_challenge"]=null_challenge(data,parts[tag]["20"],r["cuts"]["20"],SEED+idx)
        out["trees"].append(r)
        print("V10_TREE",tag,idx,flush=True)
    out["summary"]={}
    for age in AGES:
        vals=[r["cuts"][str(age)] for r in out["trees"]]
        v={}
        def quant(a):return np.quantile(a,[0,.025,.5,.975,1]).tolist()
        v["groups"]=quant([a["groups"] for a in vals])
        v["G_fraction"]={d:quant([a["gains"][d]["G_fraction"] for a in vals]) for d in DESIGNS}
        v["reconstruction_relative_reduction"]={d:quant([a["reconstruction"][d]["relative_reduction"] for a in vals]) for d in ["spatial_5","spatial_10"]}
        out["summary"][str(age)]=v
    out["primary_passing_trees"]=sum(r["primary_random_challenge"]["pass"] for r in out["trees"])
    out["screen"]=bool(out["primary_passing_trees"]>=18)
    return out

def main():
    out={"stage":"V10 phylogenetic scale of potential strategy geography","status":"START","ages_Ma":AGES,"quantile_order":["min","q025","median","q975","max"],"seed":SEED}
    try:
        check();check_overlap()
        out["status"]="TREE_ACQUISITION";save(out);trees=tree_source(out)
        out["status"]="TREE_VERIFIED";save(out)
        names,X,shape,crs,T=read_ranges(out);assert len(names)==1141
        w=wing(out);a,b,c=acquire(out);tab=mapping(a,b,names,w,out);assert len(tab)==1034 and int(tab.no_transfer.sum())==998
        tabs={"broad":tab,"without_split":tab[tab.no_transfer]}
        rosters={k:t.index.tolist() for k,t in tabs.items()}
        parts=[]
        out["status"]="TREE_PARTITION";save(out)
        for idx,t in zip(INDICES,trees):
            part,meta=partition_tree(t,names,rosters);parts.append((idx,part,meta))
        del trees
        mb=(Path("phylacine")/META).read_bytes();assert blob(mb)=="f2538374945f602f7c148d1a534be491895cd6e1"
        m=pd.read_csv(io.BytesIO(mb));m=m[m["Order.1.2"]=="Chiroptera"]
        families=dict(zip(m["Binomial.1.2"].map(norm),m["Family.1.2"]))
        assert set(names)<=set(families)
        rc=np.array(np.unravel_index(np.arange(X.shape[1]),shape)).T;tx,ty=edges(T,shape)
        pj=Transformer.from_crs(crs,4326,always_xy=True);lon,lat=pj.transform(T.c+(rc[:,1]+.5)*T.a,T.f+(rc[:,0]+.5)*T.e)
        lat0=pj.transform(np.zeros(len(rc)),T.f+rc[:,0]*T.e)[1];lat1=pj.transform(np.zeros(len(rc)),T.f+(rc[:,0]+1)*T.e)[1]
        domain=(np.maximum(lat0,lat1)<=51.6)&(np.minimum(lat0,lat1)>=-51.6)
        reg=np.full(len(rc),"other",dtype="U24")
        for name,(l,h,bottom,t) in REGIONS.items():
            q=(lon>=l)&(lon<=h)&(lat>=bottom)&(lat<t);assert np.all(reg[q]=="other");reg[q]=name
        prior=json.loads((ROOT/"MACRO_FD_V5_MEASURED_STRUCTURE_RESULT.json").read_text())
        v9=json.loads((ROOT/"MACRO_FD_V9_STRATEGY_RESULT.json").read_text())
        out["status"]="CLIMATE_DOWNLOAD";save(out);clim,climcov=climate(out,tx,ty)
        assert out["climate"]["sha256"]==prior["climate"]["sha256"] and out["climate"]["members"]==prior["climate"]["members"]
        veg,vegcov=gedi(out,tx,ty)
        assert out["GEDI"]["common_native_pixels"]==749456
        for k,v in out["GEDI"]["metrics"].items():assert v["sha256"]==prior["GEDI"]["metrics"][k]["sha256"]
        env=domain&(climcov>=.5)&(vegcov>=.5)&np.isfinite(clim).all(1)&np.isfinite(veg).all(1)
        assert int(env.sum())==11435
        out["environment_replay"]=True;out["cohorts"]={}
        for tag,t in tabs.items():
            out["status"]="REPLAY_"+tag;save(out)
            data=prepare(tag,t,names,X,env,clim,climcov,veg,vegcov,lat,reg,rc,v9["cohorts"][tag])
            r=summarize(data,parts,tag,families)
            for d in DESIGNS:
                assert abs(r["reference"]["genus"]["gains"][d]["G_fraction"]-v9["cohorts"][tag]["tests"][d]["contrasts"]["B-N"]["genus_gain_over_total"])<1e-8
            out["cohorts"][tag]=r
        out["primary_screen"]=all(v["screen"] for v in out["cohorts"].values())
        out["status"]="COMPLETE"
    except Exception as e:
        out["last_status"]=out["status"];out["status"]="STOP";out["error_type"]=type(e).__name__
        # Only static validation messages are safe to log; remote failures can contain auth URLs.
        if isinstance(e,AssertionError):out["validation"]=str(e)[:120]
    save(out);print("GLOBAL_V10_REPORT="+json.dumps(out,allow_nan=False),flush=True)
if __name__=="__main__":main()
