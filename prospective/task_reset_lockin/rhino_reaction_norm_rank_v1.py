#!/usr/bin/env python3
import importlib.util,json,math
from collections import Counter
from pathlib import Path
import numpy as np
H=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location("F",H/"flight_intensity_scalar_v1.py")
F=importlib.util.module_from_spec(sp);sp.loader.exec_module(F)
RANKS=[1,2,3]; LAMS=[.01,.1,1.,10.,100.]; SEEDS=[1101,1102,1103,1104,1105]
MAXITER=500; TOL=1e-10; B=9999; BSEED=20261007901
def data():
 r,envs=F.load_scalar_rows(); bats=sorted(set(x["bat"] for x in r)); q=[]
 for e in envs:
  for b in bats:
   v=[x["flight_intensity"] for x in r if x["env"]==e and x["bat"]==b]
   if v:q.append({"bat":b,"env":int(e),"y":float(np.mean(v))})
 if len(q)!=25:raise RuntimeError(len(q))
 return q,bats,envs
def obj(q,mu,U,V,bi,ei,lam):
 z=sum((x["y"]-(mu[ei[x["env"]]]+float(U[bi[x["bat"]]]@V[ei[x["env"]]])))**2 for x in q)
 return float(z+lam*(np.sum(U*U)+np.sum(V*V)))
def init(q,bats,envs,r,bi,ei):
 mu=np.array([np.mean([x["y"] for x in q if x["env"]==e]) if any(x["env"]==e for x in q) else 0 for e in envs],float)
 M=np.zeros((len(bats),len(envs)))
 for x in q:M[bi[x["bat"]],ei[x["env"]]]=x["y"]-mu[ei[x["env"]]]
 u,s,vt=np.linalg.svd(M,full_matrices=False); rr=min(r,len(s));U=np.zeros((len(bats),r));V=np.zeros((len(envs),r))
 if rr:
  a=np.sqrt(s[:rr]);U[:,:rr]=u[:,:rr]*a;V[:,:rr]=vt[:rr].T*a
 return mu,U,V
def als(q,bats,envs,r,lam,start):
 bi={b:i for i,b in enumerate(bats)};ei={e:i for i,e in enumerate(envs)}
 if start=="svd":mu,U,V=init(q,bats,envs,r,bi,ei)
 else:
  g=np.random.default_rng(start);mu=np.array([np.mean([x["y"] for x in q if x["env"]==e]) if any(x["env"]==e for x in q) else 0 for e in envs]);U=g.normal(0,.1,(len(bats),r));V=g.normal(0,.1,(len(envs),r))
 prev=math.inf; P=np.diag([0.]+[lam]*r)
 for _ in range(MAXITER):
  for b in bats:
   z=[x for x in q if x["bat"]==b]
   if not z:continue
   A=lam*np.eye(r);c=np.zeros(r)
   for x in z:
    v=V[ei[x["env"]]];A+=np.outer(v,v);c+=v*(x["y"]-mu[ei[x["env"]]])
   U[bi[b]]=np.linalg.solve(A,c)
  for e in envs:
   z=[x for x in q if x["env"]==e]
   if not z:continue
   X=np.vstack([np.r_[1.,U[bi[x["bat"]]]] for x in z]);y=np.array([x["y"] for x in z])
   be=np.linalg.solve(X.T@X+P,X.T@y);mu[ei[e]]=be[0];V[ei[e]]=be[1:]
  cur=obj(q,mu,U,V,bi,ei,lam)
  if math.isfinite(prev) and abs(prev-cur)<=TOL*max(1.,abs(prev)):break
  prev=cur
 return {"mu":mu,"U":U,"V":V,"bi":bi,"ei":ei,"obj":obj(q,mu,U,V,bi,ei,lam)}
def fit(q,bats,envs,r,lam):
 a=[]
 for st in ["svd"]+SEEDS:
  try:a.append(als(q,bats,envs,r,lam,st))
  except np.linalg.LinAlgError:pass
 if not a:raise RuntimeError("fit")
 return min(a,key=lambda x:x["obj"])
def pred(m,b,e):return float(m["mu"][m["ei"][e]]+m["U"][m["bi"][b]]@m["V"][m["ei"][e]])
def innercells(q):
 ec=Counter(x["env"] for x in q);bc=Counter(x["bat"] for x in q)
 return [x for x in q if ec[x["env"]]>=3 and bc[x["bat"]]>=3]
def choose(q,bats,envs,r):
 c=innercells(q);er={l:[] for l in LAMS}
 for t in c:
  tr=[x for x in q if not(x["bat"]==t["bat"] and x["env"]==t["env"])]
  for l in LAMS:
   p=pred(fit(tr,bats,envs,r,l),t["bat"],t["env"]);er[l].append((t["y"]-p)**2)
 m={l:float(np.mean(v)) for l,v in er.items()};best=min(m.values());return max(l for l,v in m.items() if abs(v-best)<=1e-12),m
def targets(q):
 ec=Counter(x["env"] for x in q);bc=Counter(x["bat"] for x in q);a=[x for x in q if ec[x["env"]]>=4 and bc[x["bat"]]>=4]
 if len(a)!=17 or Counter(x["bat"] for x in a)!=Counter({"A":2,"B":3,"C":4,"D":4,"E":4}):raise RuntimeError("target drift")
 return a
def agg(rows,k):
 bats=sorted(set(x["bat"] for x in rows));d={}
 for b in bats:
  z=[x for x in rows if x["bat"]==b];d[b]={"mse":float(np.mean([(x["y"]-x[k])**2 for x in z])),"mae":float(np.mean([abs(x["y"]-x[k]) for x in z]))}
 return {"equal_bat_mse":float(np.mean([x["mse"] for x in d.values()])),"equal_bat_mae":float(np.mean([x["mae"] for x in d.values()])),"raw_cell_mse":float(np.mean([(x["y"]-x[k])**2 for x in rows])),"per_bat":d}
def boot(rows):
 bats=sorted(set(x["bat"] for x in rows));g=np.random.default_rng(BSEED);v={k:[] for k in ["I1","I2","I3"]}
 for _ in range(B):
  ss=g.choice(np.array(bats,dtype=object),len(bats),replace=True);m={k:[] for k in ["R0","R1","R2","R3"]}
  for b in ss:
   z=[x for x in rows if x["bat"]==b]
   for k in m:m[k].append(float(np.mean([(x["y"]-x[k])**2 for x in z])))
  mm={k:float(np.mean(x)) for k,x in m.items()};v["I1"].append(mm["R0"]-mm["R1"]);v["I2"].append(mm["R1"]-mm["R2"]);v["I3"].append(mm["R2"]-mm["R3"])
 return {k:{"ci95_low":float(np.quantile(a,.025)),"ci95_high":float(np.quantile(a,.975))} for k,a in ((k,np.array(x)) for k,x in v.items())}
def main():
 q,bats,envs=data();rows=[]
 for t in targets(q):
  tr=[x for x in q if not(x["bat"]==t["bat"] and x["env"]==t["env"])];o=[x["y"] for x in tr if x["env"]==t["env"]]
  z={"bat":t["bat"],"env":t["env"],"y":t["y"],"R0":float(np.mean(o)),"lambda":{}}
  for r in RANKS:
   l,_=choose(tr,bats,envs,r);z[f"R{r}"]=pred(fit(tr,bats,envs,r,l),t["bat"],t["env"]);z["lambda"][str(r)]=l
  rows.append(z)
 met={k:agg(rows,k) for k in ["R0","R1","R2","R3"]};inc={"I1":met["R0"]["equal_bat_mse"]-met["R1"]["equal_bat_mse"],"I2":met["R1"]["equal_bat_mse"]-met["R2"]["equal_bat_mse"],"I3":met["R2"]["equal_bat_mse"]-met["R3"]["equal_bat_mse"]};ci=boot(rows);sup={k:inc[k]>0 and ci[k]["ci95_low"]>0 for k in inc}
 cat="ONE_INDIVIDUAL_PARAMETER_SUFFICIENT" if sup["I1"] and not sup["I2"] and not sup["I3"] else "TWO_INDIVIDUAL_PARAMETERS_REQUIRED" if sup["I1"] and sup["I2"] and not sup["I3"] else "AT_LEAST_THREE_PARAMETERS_REQUIRED" if all(sup.values()) else "NO_STABLE_LOW_RANK_REACTION_NORM" if not sup["I1"] else "MIXED_NONMONOTONE_RANK_RESULT"
 print(json.dumps({"status":"POST_PRIMARY_MATHEMATICAL_STRUCTURE_DIAGNOSTIC","n_centroids":len(q),"n_outer_targets":len(rows),"metrics":met,"increments":inc,"bootstrap":ci,"supported":sup,"classification":cat,"outer_predictions":rows},indent=2))
if __name__=="__main__":main()
