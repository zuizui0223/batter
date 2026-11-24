"""V10 exploratory conditional geometry using author WingMorph.txt.
Usage: python scripts/carollia_individual_wind_geometry_v10.py /path/WingMorph.txt
No raw source redistribution, no fitted behavioral or metabolic outcome.
"""
import hashlib, itertools, json, pathlib, sys
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
MD5="83c25901480df694ab049016955ce130"
SHA="46fb9c339feb2a9b0a9277aa52dd3e8e25ffd598cd1457a663f96ed8c8a394a4"

def coeffs(m,b,s,model):
    if model=="author":
        return 2.4*(m*9.8)**2/(1.205*np.pi*b*b), .5*1.205*(.02*s+.00285*m**(2/3))
    if model=="reduced":
        return 2*1.2*(m*9.81)**2/(1.2*np.pi*b*b),.5*1.2*s*.08
    raise ValueError(model)

def compute(m,b,s,model="author",lo=5,hi=7,winds=(0,2,4),nt=180,step=.01):
    m,b,s=[np.atleast_1d(np.asarray(t)) for t in (m,b,s)]
    a,c=coeffs(m,b,s,model)
    u=np.linspace(lo,hi,round((hi-lo)/step)+1)
    P=a[:,None]/u+c[:,None]*u**3
    theta=np.arange(nt)*2*np.pi/nt
    out={}
    for w in winds:
        lateral=w*np.sin(theta); along=w*np.cos(theta)
        g=np.sqrt(np.maximum(0,u[None,:]**2-lateral[:,None]**2))
        gp=g+along[:,None]; gm=g-along[:,None]
        gp=np.where((u>=abs(lateral[:,None]))&(gp>0),gp,np.nan)
        gm=np.where((u>=abs(lateral[:,None]))&(gm>0),gm,np.nan)
        radii=[]; bounds=[]
        for pp in P:
            cp=np.where(np.isfinite(gp),pp/gp,np.inf)
            cm=np.where(np.isfinite(gm),pp/gm,np.inf)
            ip=cp.argmin(axis=1); im=cm.argmin(axis=1)
            radii.append(1/(cp.min(axis=1)+cm.min(axis=1)))
            bounds.append(((ip==0).sum()+(ip==len(u)-1).sum()+(im==0).sum()+(im==len(u)-1).sum())/(2*nt))
        R=np.array(radii); area=np.pi*np.mean(R**2,axis=1)
        assert np.isfinite(area).all() and (area>0).all()
        out[w]=dict(radius=R,area=area,bounds=np.array(bounds))
    return out

def q(a):
    return np.quantile(a,[.05,.5,.95]).tolist()

def cv(a):
    return float(a.std(ddof=1)/a.mean()) if len(a)>1 else 0.

def summ(o,mask=None):
    if mask is None: mask=np.ones(len(o[0]["area"]),bool)
    a=o[0]["area"][mask];b=o[4]["area"][mask];r=b/a
    tri=np.triu_indices(len(a),1)
    inv=((a[:,None]-a[None,:])*(b[:,None]-b[None,:])<0)[tri].sum()
    return dict(n=len(a),calm_area_q=q(a),wind4_area_q=q(b),wind4_retention_q=q(r),calm_cv=cv(a),
                wind4_cv=cv(b),retention_cv=cv(r),mean_retention=float(r.mean()),
                rank_calm_wind4=float(spearmanr(a,b).statistic) if len(a)>1 else None,
                rank_absolute_relative=float(spearmanr(b,r).statistic) if len(a)>1 else None,
                rank_inversions=int(inv),pairs=len(tri[0]),boundary_w4_q=q(o[4]["bounds"][mask]))

def overlap(o,w,mask=None):
    r=o[w]["radius"]
    if mask is not None: r=r[mask]
    p=[];cross=0
    for i,j in itertools.combinations(range(len(r)),2):
        a,b=r[i],r[j];t=a-b
        cross+=bool(t.min()<-1e-8 and t.max()>1e-8)
        p.append(np.minimum(a*a,b*b).mean()/np.maximum(a*a,b*b).mean())
    return dict(crossing=cross,pairs=len(p),jaccard_q=q(p))

def main(path):
    raw=path.read_bytes()
    assert hashlib.md5(raw).hexdigest()==MD5 and hashlib.sha256(raw).hexdigest()==SHA
    d=pd.read_csv(path,sep="\t")
    assert len(d)==116 and d.ID.nunique()==116 and d.Sex.value_counts().to_dict()=={"F":59,"M":57}
    assert d.isna().sum().sum()==0 and (d[["B","S","M"]]>0).all().all()
    d["AR"]=d.B**2/d.S;d["WL"]=d.M*9.8/d.S
    mask=~d.ID.str.casefold().duplicated(keep=False).to_numpy()
    assert mask.sum()==114
    x=compute(d.M,d.B,d.S)
    y=compute(d.M,d.B,d.S,lo=2)
    z=compute(d.M,d.B,d.S,model="reduced")
    gm=np.exp(np.log(d[["M","B","S"]]).mean())
    scale=d.M/gm.M
    mass=compute(d.M,gm.B*scale**(1/3),gm.S*scale**(2/3))
    mean=compute(*[d[c].mean() for c in ["M","B","S"]])
    fine=compute(d.M,d.B,d.S,nt=360,step=.005,winds=(0,4))
    err=max(float(np.max(np.abs(fine[w]["area"]/x[w]["area"]-1))) for w in (0,4))
    assert err<1e-4
    r=x[4]["area"]/x[0]["area"]; rm=mass[4]["area"]/mass[0]["area"]
    result={"scope":"exploratory conditional geometry using measured traits, not observed flight or space use",
            "source_doi":"10.5281/zenodo.7126170","source_sha256":SHA,
            "rows":len(d),"case_insensitive_id_collision":["red390","Red390"],"after_exclusion":int(mask.sum()),
            "traits_q":{"AR":q(d.AR),"WL":q(d.WL)},
            "author_primary":summ(x),"author_2_to_7":summ(y),"reduced_5_to_7":summ(z),
            "mass_allometry":summ(mass),"species_mean":summ(mean),
            "exclude_id_collision":summ(x,mask),
            "sex":{s:summ(x,d.Sex.eq(s).to_numpy()) for s in ["F","M"]},
            "wind_profiles":{str(w):{"retention_q":q(x[w]["area"]/x[0]["area"]),"area_cv":cv(x[w]["area"])} for w in (0,2,4)},
            "primary_pairwise":{"calm":overlap(x,0),"wind4":overlap(x,4)},
            "overlap_sensitivity":{"author_2_to_7_w4":overlap(y,4),"reduced_5_to_7_w4":overlap(z,4)},
            "individual_to_mass_only_absolute_w4_q":q(x[4]["area"]/mass[4]["area"]),
            "individual_to_species_mean_absolute_w4_q":q(x[4]["area"]/mean[4]["area"][0]),
            "retention_minus_mass_only_q":q(r-rm),
            "grid_convergence_max_relative_error":err,
            "model_rank_agreement":{"absolute":float(spearmanr(x[4]["area"],z[4]["area"]).statistic),
                                    "relative":float(spearmanr(r,z[4]["area"]/z[0]["area"]).statistic)}}
    p=pathlib.Path("results/carollia_individual_wind_geometry_v10.json")
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,allow_nan=False)+"\n");print(p.read_text())

if __name__=="__main__":
    main(pathlib.Path(sys.argv[1]))
