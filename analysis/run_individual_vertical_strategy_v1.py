#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, io, itertools, json, math, re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"analysis/individual_vertical_strategy_contract_v1.json"
OUT=ROOT/"results/individual_vertical_strategy_result_v1.json"

def canon(x: str) -> str:
    return re.sub(r"_+","_",x.strip().lower().replace("-","_").replace(" ","_")).strip("_")

def download(url: str) -> bytes:
    req=Request(url,headers={"User-Agent":"batter-individual-vertical-strategy-v1/1.0"})
    with urlopen(req,timeout=90) as r:  # noqa: S310
        return r.read()

def parse_dt(s: str) -> datetime:
    v=s.strip()
    if v.endswith("Z"):
        v=v[:-1]+"+00:00"
    dt=datetime.fromisoformat(v)
    if dt.tzinfo is None:
        dt=dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def edges(values):
    out=[]
    for v in values:
        if v=="-inf": out.append(-math.inf)
        elif v=="inf": out.append(math.inf)
        else: out.append(float(v))
    return out

def zbin(v: float, e):
    import bisect
    return bisect.bisect_right(e[1:-1],v)

def smooth(counts,alpha):
    a=np.asarray(counts,dtype=float)+float(alpha)
    return a/a.sum()

def safe_log(x):
    return math.log(max(float(x),1e-15))

def load_events(c):
    raw=download(c["source"]["content_url"])
    if len(raw)!=int(c["source"]["size_bytes"]):
        raise RuntimeError("source size mismatch")
    if hashlib.md5(raw).hexdigest()!=c["source"]["md5"]:
        raise RuntimeError("source md5 mismatch")
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    if reader.fieldnames is None:
        raise RuntimeError("missing header")
    fields=[canon(x) for x in reader.fieldnames]
    rows=[]
    transformer=Transformer.from_crs("EPSG:4326",c["frozen_geometry"]["crs"],always_xy=True)
    allowed=set(c["frozen_geometry"]["eligible_cells"])
    e=edges(c["frozen_geometry"]["z_edges_m"])
    for rr in reader:
        r={canon(str(k)):("" if v is None else str(v)) for k,v in rr.items() if k is not None}
        iid=(r.get("individual_local_identifier") or r.get("individual_id") or "").strip()
        if not iid: continue
        try:
            lon=float(r["location_long"]); lat=float(r["location_lat"])
            h=float(r[c["source"]["axis"]])
            if not all(math.isfinite(v) for v in (lon,lat,h)): continue
            x,y=transformer.transform(lon,lat)
            cell=f"{math.floor(x/int(c['frozen_geometry']['cell_size_m']))}:{math.floor(y/int(c['frozen_geometry']['cell_size_m']))}"
            if cell not in allowed: continue
            t=parse_dt(r["timestamp"])
        except Exception:
            continue
        rows.append((iid,t,cell,zbin(h,e)))
    if len(list(reader))>0:
        raise RuntimeError("unexpected parser state")
    return raw,rows,len(e)-1,fields

def split_events(rows,c):
    by={}
    for x in rows: by.setdefault(x[0],[]).append(x)
    if len(by)!=int(c["source"]["expected_individuals"]):
        raise RuntimeError(f"individual count {len(by)} != expected")
    halves={}
    minimum=int(c["temporal_split"]["minimum_eligible_events_each_half"])
    for iid,vals in sorted(by.items()):
        vals=sorted(vals,key=lambda x:(x[1],x[2],x[3]))
        cut=len(vals)//2
        early=vals[:cut]; late=vals[cut:]
        if len(early)<minimum or len(late)<minimum:
            raise RuntimeError(f"{iid} underpowered: early={len(early)} late={len(late)}")
        halves[iid]={"early":early,"late":late}
    return halves

def build_models(halves,k,alpha,lam):
    ids=sorted(halves)
    # Raw early counts by individual/cell and marginal.
    by_i_cell={}; marginal={}
    cells=sorted({x[2] for h in halves.values() for x in h["early"]})
    for iid in ids:
        by_i_cell[iid]={}
        marginal[iid]=np.zeros(k,dtype=float)
        for _,_,cell,z in halves[iid]["early"]:
            by_i_cell[iid].setdefault(cell,np.zeros(k,dtype=float))[z]+=1
            marginal[iid][z]+=1

    # Equal-individual species prior, not event-pooled.
    species_cond={}
    for cell in cells:
        ps=[]
        for iid in ids:
            if cell in by_i_cell[iid]:
                ps.append(smooth(by_i_cell[iid][cell],alpha))
        if ps:
            species_cond[cell]=np.mean(np.stack(ps),axis=0)
    species_marg=np.mean(np.stack([smooth(marginal[i],alpha) for i in ids]),axis=0)

    ind_cond={}; ind_marg={}
    for iid in ids:
        ind_cond[iid]={}
        for cell,p0 in species_cond.items():
            counts=by_i_cell[iid].get(cell,np.zeros(k,dtype=float))
            n=float(counts.sum())
            if n==0:
                ind_cond[iid][cell]=p0.copy()
            else:
                ind_cond[iid][cell]=(counts + float(lam)*p0)/(n+float(lam))
        counts=marginal[iid]
        n=float(counts.sum())
        ind_marg[iid]=(counts+float(lam)*species_marg)/(n+float(lam))
    return ids,species_cond,species_marg,ind_cond,ind_marg

def score(halves,ids,species_cond,species_marg,ind_cond,ind_marg):
    matrix=np.full((len(ids),len(ids)),np.nan)
    target_event_n={}
    total=[]; marginal_adv=[]; spatial_inc=[]
    for j,target in enumerate(ids):
        events=[x for x in halves[target]["late"] if x[2] in species_cond]
        target_event_n[target]=len(events)
        base_cond=np.mean([safe_log(species_cond[cell][z]) for _,_,cell,z in events])
        base_marg=np.mean([safe_log(species_marg[z]) for _,_,_,z in events])
        for i,source in enumerate(ids):
            lp=np.mean([safe_log(ind_cond[source][cell][z]) for _,_,cell,z in events])
            matrix[i,j]=lp-base_cond
        own_cond=np.mean([safe_log(ind_cond[target][cell][z]) for _,_,cell,z in events])
        own_marg=np.mean([safe_log(ind_marg[target][z]) for _,_,_,z in events])
        total.append(own_cond-base_cond)
        marginal_adv.append(own_marg-base_marg)
        spatial_inc.append(own_cond-own_marg)
    return matrix,target_event_n,np.asarray(total),np.asarray(marginal_adv),np.asarray(spatial_inc)

def exact_identity_test(matrix):
    n=matrix.shape[0]
    obs=float(np.mean([matrix[i,i] for i in range(n)]))
    vals=[]
    ge=0
    total=0
    for perm in itertools.permutations(range(n)):
        stat=float(np.mean([matrix[perm[j],j] for j in range(n)]))
        vals.append(stat)
        ge += int(stat>=obs-1e-15)
        total += 1
    arr=np.asarray(vals)
    return {
        "observed_diagonal_mean_gain":obs,
        "permutation_count":total,
        "one_sided_p":ge/total,
        "null_mean":float(arr.mean()),
        "null_q05":float(np.quantile(arr,0.05)),
        "null_q95":float(np.quantile(arr,0.95))
    }

def run_lambda(halves,k,c,lam):
    alpha=float(c["probability_model"]["jeffreys_alpha"])
    ids,sc,sm,ic,im=build_models(halves,k,alpha,lam)
    matrix,event_n,total,marg,spatial=score(halves,ids,sc,sm,ic,im)
    test=exact_identity_test(matrix)
    positive_total=int(np.sum(total>0))
    positive_marg=int(np.sum(marg>0))
    positive_spatial=int(np.sum(spatial>0))
    self_top1=0
    for j in range(len(ids)):
        if matrix[j,j] > np.max(np.delete(matrix[:,j],j)):
            self_top1+=1
    primary_pass=bool(test["one_sided_p"]<=0.05 and positive_total>=6)
    if primary_pass and positive_spatial>=5:
        category="individual_specific_spatial_vertical_strategy"
    elif primary_pass and positive_spatial<5 and positive_marg>=5:
        category="individual_specific_marginal_altitude_state_without_stable_spatial_map"
    elif primary_pass:
        category="individual_specificity_supported_but_decomposition_mixed"
    else:
        category="no_stable_individual_specificity_supported"
    return {
        "lambda":lam,
        "individual_ids":ids,
        "late_event_counts":event_n,
        "source_by_target_gain_matrix":matrix.tolist(),
        "individual_total_identity_advantage":{iid:float(total[i]) for i,iid in enumerate(ids)},
        "individual_marginal_identity_advantage":{iid:float(marg[i]) for i,iid in enumerate(ids)},
        "individual_within_spatial_increment":{iid:float(spatial[i]) for i,iid in enumerate(ids)},
        "positive_total_identity_count":positive_total,
        "positive_marginal_identity_count":positive_marg,
        "positive_spatial_increment_count":positive_spatial,
        "self_map_strict_top1_count":self_top1,
        "identity_permutation_test":test,
        "primary_pass":primary_pass,
        "category":category
    }

def main():
    c=json.loads(CONTRACT.read_text())
    raw,rows,k,fields=load_events(c)
    if len(raw)==0: raise RuntimeError("empty source")
    if len(rows)>int(c["source"]["expected_rows"]):
        raise RuntimeError("eligible rows cannot exceed source rows")
    halves=split_events(rows,c)
    primary_lambda=int(c["probability_model"]["shrinkage_equivalent_events"])
    primary=run_lambda(halves,k,c,primary_lambda)
    sens={str(lam):run_lambda(halves,k,c,int(lam)) for lam in c["sensitivities"]["shrinkage_lambda"]}
    result={
        "schema":"batter.individual_vertical_strategy.result.v1",
        "source_md5":hashlib.md5(raw).hexdigest(),
        "source_row_count":int(c["source"]["expected_rows"]),
        "eligible_frozen_cell_event_count":len(rows),
        "individual_count":len(halves),
        "primary":primary,
        "sensitivities":sens,
        "sensitivities_cannot_replace_primary":True,
        "original_odsp_result_unchanged":True,
        "interpretation_boundary":c["claim_boundary"]
    }
    result["fingerprint"]=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
