#!/usr/bin/env python3
from __future__ import annotations
import collections, importlib.util, itertools, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("M",HERE/"cross_species_policy_axis_v1.py")
M=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(M)
P=M.P
NMINI=9999; NMAP=1999

def scalar_cells(raw):
    ft=[r for r in raw if r["feature_valid"]]
    X=np.vstack([r["features"] for r in ft]).astype(float)
    env=np.asarray([r["env"] for r in ft])
    R=np.empty_like(X)
    for e in sorted(set(env.tolist())):
        ix=np.where(env==e)[0]; R[ix]=X[ix]-X[ix].mean(axis=0,keepdims=True)
    sd=R.std(axis=0,ddof=1)
    Z=R/sd
    by=collections.defaultdict(list)
    for i,r in enumerate(ft):
        by[(int(r["env"]),str(r["bat"]))].append(float(np.mean(Z[i,:4])))
    return {k:float(np.mean(v)) for k,v in by.items()}

def template(m):
    cells=sorted(m); bats=sorted({b for e,b in cells}); envs=sorted({e for e,b in cells})
    if len(cells)!=12 or len(bats)!=4 or len(envs)!=7: raise RuntimeError("Mini structure drift")
    return cells,bats,envs

def feasible(mcells,rcent,mbats,menvs):
    rbats=sorted({b for e,b in rcent}); renvs=sorted({e for e,b in rcent}); rc=set(rcent)
    q=[]
    for chosen in itertools.permutations(rbats,4):
        bm=dict(zip(mbats,chosen))
        for ep in itertools.permutations(renvs,7):
            em=dict(zip(menvs,ep))
            if all((em[e],bm[b]) in rc for e,b in mcells): q.append((tuple(chosen),tuple(ep)))
    q=sorted(q)
    if len(q)!=4212: raise RuntimeError(f"mapping drift {len(q)}")
    return q

def mapped_rows(cent,cells):
    return [{"env":e,"bat":b,"x":cent[(e,b)]} for e,b in cells]

def mapped_rhino(rcent,mcells,mbats,menvs,mp):
    chosen,ep=mp; bm=dict(zip(mbats,chosen)); em=dict(zip(menvs,ep))
    return [{"env":e,"bat":b,"x":rcent[(em[e],bm[b])]} for e,b in mcells]

def labelsets(rows,envs):
    return {e:sorted({r["bat"] for r in rows if r["env"]==e}) for e in envs}

def idmap(ls): return {(e,b):b for e,l in ls.items() for b in l}

def permmap(ls,rng):
    out={}
    for e,labs in ls.items():
        p=list(rng.permutation(np.asarray(labs,dtype=object)))
        for a,b in zip(labs,p): out[(e,a)]=str(b)
    return out

def stat(rows,mapping):
    envs=sorted({r["env"] for r in rows}); labels=sorted(set(mapping.values()))
    pb=collections.defaultdict(list)
    for e0 in envs:
        cent={}
        for lab in labels:
            vals=[]
            for e in envs:
                if e==e0: continue
                x=[r["x"] for r in rows if r["env"]==e and mapping.get((e,r["bat"]))==lab]
                if x: vals.append(float(np.mean(x)))
            if len(vals)>=2: cent[lab]=float(np.mean(vals))
        if len(cent)<3: continue
        for r in rows:
            if r["env"]!=e0: continue
            lab=mapping.get((e0,r["bat"]))
            if lab not in cent: continue
            donors=[b for b in cent if b!=lab]
            if len(donors)<2: continue
            ds=abs(r["x"]-cent[lab]); do=float(np.mean([abs(r["x"]-cent[b]) for b in donors]))
            pb[lab].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in pb.items() if v}
    return (float(np.mean(list(bm.values()))),bm) if len(bm)>=3 else (None,bm)

def calibrate(rows,seed,nperm,minvalid):
    envs=sorted({r["env"] for r in rows}); ls=labelsets(rows,envs)
    obs,bm=stat(rows,idmap(ls))
    if obs is None:return {"status":"STOP"}
    rng=np.random.default_rng(seed); null=[]
    for _ in range(nperm):
        q,_=stat(rows,permmap(ls,rng))
        if q is not None:null.append(q)
    a=np.asarray(null,float); p=float((1+np.sum(a>=obs))/(1+len(a)))
    pos=sum(v>0 for v in bm.values())
    return {"K":obs,"bat_means":bm,"positive_bats":pos,"p_one_sided":p,
            "valid_permutations":len(a),"detected":bool(len(a)>=minvalid and obs>0 and p<=.05 and pos>=3)}

def select(feas):
    N=len(feas); out=[]; used=set()
    for j in range(256):
        k=int(math.floor(j*(N-1)/255))
        while k in used and k+1<N:k+=1
        if k in used:k=next(x for x in range(N) if x not in used)
        used.add(k); out.append(k)
    return out

def main():
    mc=scalar_cells(M.load_mini()); rc=scalar_cells(P.load_rhino())
    cells,mbats,menvs=template(mc); feas=feasible(cells,rc,mbats,menvs)
    mini=calibrate(mapped_rows(mc,cells),20261008101,NMINI,9500)
    allk=[]
    for mp in feas:
        q,_=stat(mapped_rhino(rc,cells,mbats,menvs,mp),idmap(labelsets(mapped_rhino(rc,cells,mbats,menvs,mp),menvs)))
        allk.append(q)
    idx=select(feas); cal=[]
    for rank,k in enumerate(idx):
        q=calibrate(mapped_rhino(rc,cells,mbats,menvs,feas[k]),20261008200+rank,NMAP,1900)
        q["mapping_index"]=k; cal.append(q)
    det=sum(q.get("detected",False) for q in cal); frac=det/len(cal)
    cat="ADEQUATE_FOR_RHINO_LIKE_SIGNAL" if frac>=.8 else ("POWER_LIMITED" if frac<.5 else "AMBIGUOUS")
    A=np.asarray(allk,float)
    print(json.dumps({
      "status":"POST_PRIMARY_POWER_DIAGNOSTIC",
      "mini":mini,
      "n_feasible_mappings":len(feas),
      "rhino_all_mapping_K":{"median":float(np.median(A)),"q025":float(np.quantile(A,.025)),
        "q975":float(np.quantile(A,.975)),"fraction_gt_zero":float(np.mean(A>0)),
        "fraction_gt_mini_K":float(np.mean(A>mini["K"]))},
      "calibrated_mapping_count":len(cal),"rhino_detected_mappings":det,
      "rhino_detection_fraction":frac,"support_category":cat
    },indent=2,sort_keys=True))

if __name__=="__main__":main()
