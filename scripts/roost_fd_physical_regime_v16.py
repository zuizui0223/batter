"""V16 physical-roost/landing regime morphology diagnostic; all outcomes exploratory."""
import io,json,hashlib,zipfile
import numpy as np
import pandas as pd
from Bio import Phylo
from roost_fd_source_audit_v2 import OUT
from roost_fd_source_audit_v3 import label,quant
from roost_fd_source_audit_v4 import name
from roost_fd_empirical_null_v5 import SEED
from roost_fd_independent_roost_v11 import download
from roost_fd_independent_roost_v12 import readcsv
from roost_fd_independent_euro_v13 import mpd
from roost_fd_independent_roost_v15 import retrieve,wing_table,URL,HASH

EXPOSURES=["rock_cave","stiff_horizontal","low_impact_style"]
NREP=1999

def acquire_landing():
    b,meta=download(URL,25_000_000)
    assert hashlib.sha256(b).hexdigest()==HASH
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        def member(end):
            a=[n for n in z.namelist() if not n.startswith("__MACOSX") and n.endswith(end)]
            assert len(a)==1
            return z.read(a[0])
        d=readcsv(member("Bat landing roosting data.csv"))
        tree=member("ShiRabosky2015.tree")
        f=readcsv(member("Impulse_Ouputs_20230630_NO-Rnaso_SpecAvg.csv"))
    assert len(d)==36
    d["species"]=d.Taxon.map(name);d["source_family"]=d.Family.map(label)
    assert d.species.notna().all() and d.species.is_unique
    assert set(d.Roosting_Regime)=={"stiff-horiz","comp-crev-vert"}
    assert set(d.Landing_Regime)=={"low","high"}
    assert set(d.Roost_All)<={"R/C","CST","CREV","FOL-LT","FOL-UF","EST","TAN"}
    d["rock_cave"]=(d.Roost_All=="R/C").astype(int)
    d["stiff_horizontal"]=(d.Roosting_Regime=="stiff-horiz").astype(int)
    d["low_impact_style"]=(d.Landing_Regime=="low").astype(int)
    return d,f,tree,meta

def stats(A,M,g):
    return np.array([A[g].mean()-A[~g].mean(),mpd(A[g])-mpd(A[~g]),mpd(M[g])-mpd(M[~g])])

def compare(d,exposure):
    A=np.log(d.ar.to_numpy());M=np.log(d.mass.to_numpy());g=d[exposure].to_numpy(bool)
    n=int(g.sum());out={"group_n":n,"other_n":len(g)-n,"status":"insufficient_groups"}
    if min(n,len(g)-n)<5:return out
    o=stats(A,M,g)
    out.update(status="exploratory",AR_geom_mean=[float(np.exp(A[g].mean())),float(np.exp(A[~g].mean()))],
        AR_MPD=[mpd(A[g]),mpd(A[~g])],mass_MPD=[mpd(M[g]),mpd(M[~g])],
        observed=dict(zip(["mean_log_AR","AR_MPD","mass_MPD"],map(float,o))),nulls={})
    for mode in ("unrestricted","family"):
        blocks=[np.arange(len(d))] if mode=="unrestricted" else [np.flatnonzero(d.wing_family.to_numpy()==f) for f in sorted(d.wing_family.unique())]
        mixed=[i for i in blocks if g[i].any() and (~g[i]).any()]
        row={"mixed_families":len(mixed) if mode=="family" else None,"mixed_species":sum(len(i) for i in mixed)}
        if mode=="family" and (len(mixed)<2 or row["mixed_species"]<10):
            row["status"]="insufficient_family_support";out["nulls"][mode]=row;continue
        rng=np.random.default_rng(SEED);sim=[]
        for _ in range(NREP):
            p=g.copy()
            for i in mixed:p[i]=rng.permutation(g[i])
            assert p.sum()==g.sum()
            sim.append(stats(A,M,p))
        sim=np.asarray(sim);mu=sim.mean(axis=0);sd=sim.std(axis=0,ddof=1)
        row["status"]="exploratory";row["statistics"]={}
        for j,k in enumerate(["mean_log_AR","AR_MPD","mass_MPD"]):
            lo=(1+int((sim[:,j]<=o[j]+1e-12).sum()))/(NREP+1)
            hi=(1+int((sim[:,j]>=o[j]-1e-12).sum()))/(NREP+1)
            row["statistics"][k]={"null_mean":float(mu[j]),"null_sd":float(sd[j]),
                "SES":float((o[j]-mu[j])/sd[j]) if sd[j]>1e-12 else None,
                "p_two_sided":min(1.,2*min(lo,hi)) if sd[j]>1e-12 else None}
        out["nulls"][mode]=row
    return out

def predict(train,test,y):
    # Ridge on standardized training covariates; unpenalized intercept.
    mu=train.mean(axis=0);sd=train.std(axis=0);sd=np.where(sd>1e-12,sd,1.)
    X=(train-mu)/sd;Z=(test-mu)/sd
    center=y.mean()
    coef=np.linalg.solve(X.T@X+np.eye(X.shape[1]),X.T@(y-center))
    return center+Z@coef

def transfer(d):
    d=d.copy();d["log_mass"]=np.log(d.mass);y=np.log(d.ar.to_numpy())
    families=sorted(d.wing_family.unique())
    sets={"M0":["log_mass"],**{e:["log_mass",e] for e in EXPOSURES},
          "physical_and_landing":["log_mass","stiff_horizontal","low_impact_style"]}
    err={}
    for key,cols in sets.items():
        X=d[cols].to_numpy(float);loss=[]
        for f in families:
            te=d.wing_family.to_numpy()==f;tr=~te
            yh=predict(X[tr],X[te],y[tr])
            loss.append(float(np.mean((yh-y[te])**2)))
        err[key]=np.array(loss)
    out={"family_blocks":len(families),"families_with_at_least_2_species":int((d.wing_family.value_counts()>=2).sum()),"models":{}}
    for k,v in err.items():
        out["models"][k]={"equal_family_RMSE_log_AR":float(np.sqrt(v.mean())),
          "delta_RMSE_vs_M0":float(np.sqrt(v.mean())-np.sqrt(err["M0"].mean())),
          "families_better_than_M0":int((v<err["M0"]).sum())}
    return out

def force_schema(f,d):
    present=set(d.species)
    cols={}
    for c in f:
        z=f[c].map(name)
        if z.notna().sum():
            cols[str(c)]={"valid_binomial_rows":int(z.notna().sum()),"unique_species":int(z.nunique()),"overlap_roster":len(set(z.dropna())&present)}
    return {"rows":len(f),"columns":list(map(str,f.columns)),
        "species_column_candidates":cols,"numeric_counts":{str(c):int(pd.to_numeric(f[c],errors="coerce").notna().sum()) for c in f},
        "status":"schema_only_no_force_response_selected"}

def tree_gls(d,tree_bytes):
    # Exact names after standardized whitespace/case; no fuzzy mapping.
    tree=None;errors=[]
    for fmt in ("newick","nexus"):
        try:
            tree=Phylo.read(io.StringIO(tree_bytes.decode("utf-8-sig")),fmt);break
        except Exception as e:errors.append(type(e).__name__)
    if tree is None:return {"status":"tree_parse_failed","errors":errors}
    tips=tree.get_terminals();m={}
    for tip in tips:
        s=name(tip.name)
        if s:m.setdefault(s,[]).append(tip)
    valid={k:v[0] for k,v in m.items() if len(v)==1}
    matched=[s for s in d.species if s in valid]
    out={"tree_tips":len(tips),"valid_unique_binomial_tips":len(valid),"matched_roster":len(matched),
         "roster":len(d),"rooted_flag":bool(tree.rooted),"status":"incomplete_tree_match"}
    if len(matched)!=len(d):return out
    t=[valid[s] for s in d.species];depth=tree.depths()
    if any(v.branch_length is None or not np.isfinite(v.branch_length) or v.branch_length<0 for v in tree.find_clades() if v is not tree.root):
        out["status"]="invalid_branch_lengths";return out
    C=np.array([[depth[tree.common_ancestor(a,b)] for b in t] for a in t])
    # Tip diagonals need exact root-to-tip depth (common_ancestor of same tip).
    if np.min(np.diag(C))<=0 or np.linalg.eigvalsh(C).min()<-1e-8:
        out["status"]="invalid_covariance";return out
    out["root_to_tip_range"]=[float(np.diag(C).min()),float(np.diag(C).max())]
    # Brownian covariance scaled by overall mean tip depth; fixed lambda off diagonals.
    C=C/np.diag(C).mean();D=np.diag(np.diag(C))
    y=np.log(d.ar.to_numpy());m=np.log(d.mass.to_numpy());out["models"]={}
    for e in EXPOSURES:
        X=np.column_stack([np.ones(len(d)),m,d[e].to_numpy()])
        out["models"][e]={}
        for lam in (0.,.5,1.):
            V=lam*C+(1-lam)*D
            if np.linalg.eigvalsh(V).min()<1e-10:
                out["models"][e][str(lam)]={"status":"singular_covariance"};continue
            VX=np.linalg.solve(V,X);Vy=np.linalg.solve(V,y)
            H=X.T@VX
            if np.linalg.matrix_rank(H)<3:
                out["models"][e][str(lam)]={"status":"singular_design"};continue
            beta=np.linalg.solve(H,X.T@Vy);res=y-X@beta
            s2=float(res@np.linalg.solve(V,res)/(len(y)-3));cov=s2*np.linalg.inv(H)
            out["models"][e][str(lam)]={"log_AR_coefficient":float(beta[2]),"SE":float(np.sqrt(cov[2,2]))}
    out["status"]="exploratory_fixed_lambda"
    return out

def main():
    report={"status":"started","claim_boundary":"Species-level source sample; no causal mediation, no community mechanism."}
    dest=OUT/"audit_v16.json"
    def save():dest.write_text(json.dumps(report,indent=2,allow_nan=False,default=lambda x:int(x) if isinstance(x,np.integer) else float(x)))
    save()
    try:
        d,f,tree,meta=acquire_landing();report["landing_source"]=meta
        raw=retrieve(report,save)
        if raw is None:raise ValueError("wing unavailable")
        t,qc=wing_table(raw)
        j=d.merge(t,on="species",how="left",validate="one_to_one")
        j=j.dropna(subset=["ar","mass","wing_family"]).reset_index(drop=True)
        assert len(j)==25
        report["roster"]={"n":len(j),"families":int(j.wing_family.nunique()),
            "family_label_disagreements":int((j.source_family!=j.wing_family).sum()),
            "exposure_counts":{e:int(j[e].sum()) for e in EXPOSURES},
            "exposure_correlation":j[EXPOSURES].corr().to_dict()}
        report["contrasts"]={e:compare(j,e) for e in EXPOSURES}
        report["transfer"]=transfer(j)
        report["force_schema"]=force_schema(f,j)
        save()
        try:report["phylogeny"]=tree_gls(j,tree)
        except Exception as e:report["phylogeny"]={"status":"blocked","error_type":type(e).__name__}
        report["status"]="completed_exploratory"
    except Exception as e:
        report["status"]="blocked";report["error"]=type(e).__name__+": "+str(e)[:200]
    save();print(dest.read_text())
    return 0 if report["status"]=="completed_exploratory" else 2
if __name__=="__main__":raise SystemExit(main())
