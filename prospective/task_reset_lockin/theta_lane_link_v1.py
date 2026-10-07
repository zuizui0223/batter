#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,itertools,json,math
from collections import defaultdict
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location("P",HERE/"rhino_configuration_identity_primary_v1.py")
P=importlib.util.module_from_spec(sp); assert sp.loader is not None; sp.loader.exec_module(P)
sf=importlib.util.spec_from_file_location("F",HERE/"flight_intensity_scalar_v1.py")
F=importlib.util.module_from_spec(sf); assert sf.loader is not None; sf.loader.exec_module(F)

ENVS=[1,2,3]
EXPECTED={(1,"B"):4,(1,"C"):2,(1,"D"):3,(2,"B"):3,(2,"C"):2,(2,"D"):4,(2,"E"):2,(3,"C"):3,(3,"D"):3,(3,"E"):4}
BATS=["B","C","D","E"]

def route_cells():
    traj=P.load_rhino()
    by=defaultdict(list)
    for r in traj:
        if int(r["env"]) not in ENVS or not r["route_valid"]: continue
        c=np.mean(np.asarray(r["route101"],float),axis=0)
        by[(int(r["env"]),str(r["bat"]))].append(c)
    cells=[]
    counts={}
    for k,v in sorted(by.items()):
        if len(v)>=2:
            counts[k]=len(v)
            cells.append({"env":k[0],"bat":k[1],"c":np.mean(np.vstack(v),axis=0)})
    if set(counts)!=set(EXPECTED) or any(counts[k]!=EXPECTED[k] for k in EXPECTED):
        raise RuntimeError(f"route-valid support drift counts={counts}")
    return cells

def theta_profiles():
    rows,envs=F.load_scalar_rows()
    out={}
    for b in BATS:
        for e0 in ENVS:
            per=[]
            for e in envs:
                if e==e0:continue
                vals=[float(r["flight_intensity"]) for r in rows if r["bat"]==b and r["env"]==e]
                if vals:per.append(float(np.mean(vals)))
            if len(per)<2:raise RuntimeError(f"theta support {b} env {e0}")
            out[(b,e0)]=float(np.mean(per))
    return out

def design(train,theta_assignment,use_theta):
    env_levels=ENVS
    X=[];Y=[]
    for r in train:
        row=[1.0]
        for e in env_levels[1:]:row.append(1.0 if r["env"]==e else 0.0)
        if use_theta:
            source=theta_assignment[r["bat"]]
            row.append(THETA[(source,r["env"])])
        X.append(row);Y.append(r["c"])
    return np.asarray(X,float),np.vstack(Y)

def predrow(r,theta_assignment,use_theta):
    row=[1.0,1.0 if r["env"]==2 else 0.0,1.0 if r["env"]==3 else 0.0]
    if use_theta:
        source=theta_assignment[r["bat"]]
        row.append(THETA[(source,r["env"])])
    return np.asarray(row,float)

def fit_predict(train,target,theta_assignment,use_theta):
    X,Y=design(train,theta_assignment,use_theta)
    if np.linalg.matrix_rank(X)<X.shape[1]:
        return None
    beta=np.linalg.lstsq(X,Y,rcond=None)[0]
    return predrow(target,theta_assignment,use_theta)@beta

def statistic(cells,theta_assignment):
    perbat={}
    details=[]
    for hold in BATS:
        train=[r for r in cells if r["bat"]!=hold]
        targ=[r for r in cells if r["bat"]==hold]
        gains=[]
        for r in targ:
            p0=fit_predict(train,r,theta_assignment,False)
            p1=fit_predict(train,r,theta_assignment,True)
            if p0 is None or p1 is None:continue
            e0=float(np.sum((r["c"]-p0)**2))
            e1=float(np.sum((r["c"]-p1)**2))
            gains.append(e0-e1)
            details.append({"bat":hold,"env":r["env"],"E0":e0,"Etheta":e1,"gain":e0-e1})
        if gains:perbat[hold]=float(np.mean(gains))
    if len(perbat)!=4:return None,perbat,details
    return float(np.mean(list(perbat.values()))),perbat,details

def full_slope(cells):
    amap={b:b for b in BATS}
    X,Y=design(cells,amap,True)
    beta=np.linalg.lstsq(X,Y,rcond=None)[0]
    b=beta[-1]
    return {"b_xyz":b.tolist(),"norm":float(np.linalg.norm(b))}

def main():
    global THETA
    cells=route_cells();THETA=theta_profiles()
    ident={b:b for b in BATS}
    obs,per,details=statistic(cells,ident)
    if obs is None:raise RuntimeError("observed support")
    null=[]; perms=[]
    for p in itertools.permutations(BATS):
        amap=dict(zip(BATS,p))
        g,_,_=statistic(cells,amap)
        if g is None:raise RuntimeError("perm support")
        null.append(g);perms.append({"map":amap,"G":g})
    a=np.asarray(null,float)
    p=float(np.mean(a>=obs-1e-15))
    pos=sum(v>0 for v in per.values())
    supported=bool(obs>0 and p<=.05 and pos>=3)
    out={
      "status":"POST_PRIMARY_CROSS_LEVEL_MECHANISM_DIAGNOSTIC",
      "contract":"THETA_LANE_LINK_CONTRACT_V1.md",
      "n_cells":len(cells),"bats":BATS,
      "observed_gain":obs,"bat_gains":per,"positive_bats":pos,
      "exact_permutations":len(null),"p_one_sided":p,
      "null_mean":float(a.mean()),"null_min":float(a.min()),"null_max":float(a.max()),
      "supported":supported,
      "full_data_slope":full_slope(cells),
      "target_details":details,
      "permutations":perms
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
