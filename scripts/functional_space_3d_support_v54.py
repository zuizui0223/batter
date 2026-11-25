"""V54 structural support for conditional vertical entropy, not an ecological outcome fit."""
import hashlib,io,json,pathlib,itertools
import numpy as np
import pandas as pd
from acoustic_buzz_geometry_v36 import URL,SHA,KEY,numeric
from bayer_field_join_v17 import fetch
OUT=pathlib.Path("results/functional_space_3d_support_v54.json")
XYZ=["x (m)","y (m)","z (m)"]
MINUS=["-dx (m)","-dy (m)","-dz (m)"]
PLUS=["+dx (m)","+dy (m)","+dz (m)"]
GRID=5.
OFFSETS=list(itertools.product((0.,.5),repeat=3))
def q(x):
    a=np.asarray(x,float);a=a[np.isfinite(a)]
    return np.quantile(a,[0,.05,.5,.95,1]).tolist() if len(a) else []
def geometry(x,lo,hi,imp,offset):
    c=np.floor(x/GRID-np.array(offset)).astype(np.int64)
    a=np.floor((x-lo)/GRID-np.array(offset)).astype(np.int64)
    b=np.floor((x+hi)/GRID-np.array(offset)).astype(np.int64)
    contained=np.all((a==c)&(b==c),axis=1)
    rad=np.floor(np.linalg.norm(x,axis=1)/5).astype(np.int64)
    precision=np.floor(imp).astype(np.int64)
    keys=np.column_stack([c[:,:2],rad,precision])
    return keys,c[:,2],contained
def groups(keys,z,mask):
    if int(mask.sum())<6:return 0,0
    k=keys[mask];z=z[mask]
    _,lab=np.unique(k,axis=0,return_inverse=True)
    n=0;positions=0
    for i in np.unique(lab):
        a=z[lab==i]
        if len(a)>=6 and np.count_nonzero(np.unique(a,return_counts=True)[1]>=2)>=2:
            n+=1;positions+=len(a)
    return n,positions
def test():
    x=np.array([[1,1,4],[1,1,4],[1,1,4],[1,1,6],[1,1,6],[1,1,6]],float)
    # Independent geometric group test (radial strata may split this example).
    k=np.zeros((6,4),int);z=np.array([0,0,0,1,1,1])
    assert groups(k,z,np.ones(6,bool))==(1,6)
    assert groups(k,z,np.array([1,1,1,1,1,0],bool))==(0,0)
    _,_,m=geometry(x,np.zeros_like(x),np.zeros_like(x),np.ones(6),[0,0,0]);assert m.all()
    _,_,m=geometry(x,np.full_like(x,3),np.full_like(x,3),np.ones(6),[0,0,0]);assert not m.any()
def summarize(rows,control):
    rr=[r for r in rows if not control or r["type"]=="C"]
    nights={}
    for r in rr:nights[r["date"]]=nights.get(r["date"],0)+1
    sizes=sorted(nights.values())
    qualifying=sum(v>=10 for v in sizes)
    return {"trajectories":len(rr),"groups":sum(r["groups"] for r in rr),"positions":sum(r["positions"] for r in rr),"date_groups":len(sizes),"date_group_track_counts":sizes,"date_groups_ge10":qualifying,"gate":bool(sum(v for v in sizes if v>=10)>=100 and qualifying>=5)}
def run():
    test()
    b,_=fetch(URL,3186436)
    assert len(b)==3186436 and hashlib.sha256(b).hexdigest()==SHA and hashlib.md5(b).hexdigest()=="60ce63b79fd8a5b9bc4771997de97839"
    d=pd.read_csv(io.BytesIO(b),sep=";",dtype=str,keep_default_na=False,encoding="utf-8-sig")
    d.columns=d.columns.str.strip()
    o={"scope":"structural feasibility of conditional vertical entropy only; no mark-magnitude outcome","test":"PASS","source_sha256":SHA,"rows":len(d)}
    cols=XYZ+MINUS+PLUS+["Imprecision","buzz_proba","mean_buzz_proba"]
    if any(c not in d for c in KEY+cols):
        o.update(status="STOP_FIELDS",missing_fields=[c for c in KEY+cols if c not in d]);return o
    assert len(d)==15346 and d.date.nunique()==9 and d.id_site.nunique()==29 and not (d.groupby("id_site").date.nunique()>1).any()
    assert not d[KEY].eq("").any(axis=1).any()
    for c in cols:d[c],_=numeric(d[c])
    valid=d.buzz_proba.between(0,1);missing=d.buzz_proba.eq(999)
    assert int(valid.sum())==10192 and int(missing.sum())==5154 and (valid|missing).all()
    o["score_valid_rows"]=int(valid.sum());o["missing_placeholder_rows"]=int(missing.sum())
    finite=d[XYZ+MINUS+PLUS+["Imprecision"]].notna().all(axis=1)&d.Imprecision.gt(0)
    centers=d[XYZ+["Imprecision"]].notna().all(axis=1)&d.Imprecision.gt(0)
    o["valid_center_geometry_rows"]=int((valid&centers).sum())
    o["valid_nominal_width_geometry_rows"]=int((valid&finite).sum())
    o["nominal_total_width_quantiles_m"]={axis:q((d[minus].abs()+d[plus].abs())[valid&finite]) for axis,minus,plus in zip(("x","y","z"),MINUS,PLUS)}
    rec=0;eligible=0;per=[{"center":[],"contained":[]} for _ in OFFSETS]
    totals=[{"center_positions":0,"contained_positions":0} for _ in OFFSETS]
    for _,g in d.groupby(KEY,sort=False):
        v=g[g.buzz_proba.between(0,1)]
        if not len(v):continue
        y=g.mean_buzz_proba.to_numpy(float)
        if not np.isfinite(y).all() or y.min()<0 or y.max()>1 or np.ptp(y)>1e-8:continue
        if abs(v.buzz_proba.mean()-y[0])>1e-6:continue
        rec+=1
        c=v[XYZ+["Imprecision"]].notna().all(axis=1)&v.Imprecision.gt(0)
        p=v[c]
        if len(p)<6:continue
        eligible+=1
        x=p[XYZ].to_numpy(float);lo=p[MINUS].abs().to_numpy(float);hi=p[PLUS].abs().to_numpy(float);imp=p.Imprecision.to_numpy(float)
        width_ok=np.isfinite(lo).all(axis=1)&np.isfinite(hi).all(axis=1)
        # Fill unknown widths only for center-only geometry; such positions never pass containment.
        lo=np.where(np.isfinite(lo),lo,0.);hi=np.where(np.isfinite(hi),hi,0.)
        for i,off in enumerate(OFFSETS):
            keys,z,contained=geometry(x,lo,hi,imp,off)
            contained &= width_ok
            totals[i]["center_positions"]+=len(p);totals[i]["contained_positions"]+=int(contained.sum())
            for kind,mask in (("center",np.ones(len(p),bool)),("contained",contained)):
                n,pos=groups(keys,z,mask)
                if n:per[i][kind].append({"type":str(g.typeSite.iloc[0]),"date":str(g.date.iloc[0]),"groups":n,"positions":pos})
    o["reconstructed_trajectory_means"]=rec
    if rec!=1301:o["status"]="STOP_RECONCILIATION";return o
    o["trajectories_with_at_least6_valid_centers"]=eligible
    o["origins"]=[]
    for i,off in enumerate(OFFSETS):
        a={"offset":list(off),**totals[i]}
        for kind in ("center","contained"):
            a[kind]={"all":summarize(per[i][kind],False),"C_literal":summarize(per[i][kind],True)}
        o["origins"].append(a)
    o["passing_origins_all"]=sum(a["contained"]["all"]["gate"] for a in o["origins"])
    o["passing_origins_C_literal"]=sum(a["contained"]["C_literal"]["gate"] for a in o["origins"])
    o["support_gate"]=bool(o["passing_origins_all"]>=6)
    o["status"]="COMPLETE_STRUCTURAL_ONLY";return o
if __name__=="__main__":
    try:r=run()
    except Exception as e:r={"status":"STOP","error_type":type(e).__name__}
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(r,indent=2,allow_nan=False)+"\n");print(OUT.read_text())
