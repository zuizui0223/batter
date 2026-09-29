#!/usr/bin/env python3
from __future__ import annotations

import csv, io, json, math, sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from post_freeze_extensions.behavior_proxy_inventory.run_v1 import SOURCES,get,canon

CONTRACT=ROOT/"post_freeze_extensions/tag_burden_identity/contract_v1.json"
IDENTITY=ROOT/"post_freeze_extensions/tag_burden_identity/input/result_v1.json"
OUT=ROOT/"post_freeze_extensions/tag_burden_identity/result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/tag_burden_identity/RESULT_V1.md"


def rankdata(x):
    x=np.asarray(x,dtype=float)
    order=np.argsort(x,kind="mergesort")
    ranks=np.empty(len(x),dtype=float)
    i=0
    while i<len(x):
        j=i+1
        while j<len(x) and x[order[j]]==x[order[i]]:
            j+=1
        ranks[order[i:j]]=0.5*((i+1)+j)
        i=j
    return ranks


def corr_from_ranks(a,b):
    a=np.asarray(a,dtype=float);b=np.asarray(b,dtype=float)
    ac=a-a.mean();bc=b-b.mean()
    den=math.sqrt(float(np.dot(ac,ac)*np.dot(bc,bc)))
    return float(np.dot(ac,bc)/den) if den>0 else None


def spearman(a,b):
    return corr_from_ranks(rankdata(a),rankdata(b))


def trait_map(panel):
    data=get(SOURCES[panel]["reference"],panel,"reference")
    rd=csv.DictReader(io.StringIO(data.decode("utf-8-sig"),newline=""))
    out={}
    for raw in rd:
        r={canon(k):("" if v is None else str(v).strip()) for k,v in raw.items() if k is not None}
        try:
            animal=float(r.get("animal_mass",""))
            tag=float(r.get("tag_mass",""))
            if not (math.isfinite(animal) and animal>0 and math.isfinite(tag) and tag>0):
                continue
        except Exception:
            continue
        ids={
            r.get("animal_id",""),
            r.get("individual_local_identifier",""),
            r.get("individual_id",""),
            r.get("tag_local_identifier","")
        }
        rec={"animal_mass":animal,"tag_mass":tag,"relative_tag_burden":tag/animal}
        for iid in ids:
            if iid:
                out[str(iid)]=rec
    return out


def panel_rows(panel,identity):
    traits=trait_map(panel)
    rows=[]
    for r in identity["primary"]["panels"][panel]["individuals"]:
        iid=str(r["individual"])
        if iid not in traits:
            continue
        rows.append({
            "individual":iid,
            "calibrated_centered_identity":float(r["calibrated_centered_identity"]),
            **traits[iid]
        })
    return rows


def panel_test(rows,B,seed):
    x=np.array([r["relative_tag_burden"] for r in rows],dtype=float)
    y=np.array([r["calibrated_centered_identity"] for r in rows],dtype=float)
    xr=rankdata(x);yr=rankdata(y)
    obs=corr_from_ranks(xr,yr)
    obs_abs=abs(obs)
    rng=np.random.default_rng(int(seed))
    ge=0
    vals=np.empty(int(B),dtype=float)
    for i in range(int(B)):
        rho=corr_from_ranks(xr[rng.permutation(len(xr))],yr)
        vals[i]=abs(rho)
        ge += int(abs(rho)>=obs_abs-1e-15)
    mass_rho=spearman([r["animal_mass"] for r in rows],y)
    return {
        "n":len(rows),
        "relative_burden_min":float(x.min()),
        "relative_burden_median":float(np.median(x)),
        "relative_burden_max":float(x.max()),
        "signed_spearman_rho":obs,
        "absolute_spearman_rho":obs_abs,
        "two_sided_permutation_p":(1+ge)/(int(B)+1),
        "null_abs_rho_mean":float(vals.mean()),
        "null_abs_rho_q95":float(np.quantile(vals,0.95)),
        "secondary_animal_mass_signed_rho":mass_rho,
        "individuals":rows
    }


def cross_panel(panel_results,B,seed):
    eligible={p:r for p,r in panel_results.items() if r.get("eligible")}
    obs=float(np.mean([r["test"]["absolute_spearman_rho"] for r in eligible.values()]))
    prepared={}
    for p,r in eligible.items():
        rows=r["rows_for_cross"]
        prepared[p]=(rankdata([x["relative_tag_burden"] for x in rows]),rankdata([x["calibrated_centered_identity"] for x in rows]))
    rng=np.random.default_rng(int(seed))
    ge=0
    vals=np.empty(int(B),dtype=float)
    for i in range(int(B)):
        rs=[]
        for p,(xr,yr) in prepared.items():
            rho=corr_from_ranks(xr[rng.permutation(len(xr))],yr)
            rs.append(abs(rho))
        stat=float(np.mean(rs))
        vals[i]=stat
        ge += int(stat>=obs-1e-15)
    return {
        "panel_count":len(eligible),
        "included_panels":sorted(eligible),
        "observed_equal_panel_mean_absolute_rho":obs,
        "permutation_p":(1+ge)/(int(B)+1),
        "null_mean":float(vals.mean()),
        "null_q95":float(np.quantile(vals,0.95))
    }


def main():
    c=json.loads(CONTRACT.read_text())
    identity=json.loads(IDENTITY.read_text())
    panels={}
    for p in c["panels"]:
        rows=panel_rows(p,identity)
        if len(rows)<int(c["panel_test"]["minimum_matched_individuals"]):
            panels[p]={"matched_n":len(rows),"eligible":False,"reason":"below_minimum_matched_n","rows_for_cross":rows}
            continue
        t=panel_test(rows,int(c["panel_test"]["B"]),int(c["panel_test"]["seeds"][p]))
        panels[p]={"matched_n":len(rows),"eligible":True,"test":t,"rows_for_cross":rows}

    cross=cross_panel(panels,int(c["cross_panel_test"]["B"]),int(c["cross_panel_test"]["seed"]))
    supported=cross["permutation_p"]<=0.05
    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "identity_source":c["response"]["authoritative_source"],
        "panels":panels,
        "cross_panel":cross,
        "primary_supported":supported,
        "interpretation":c["interpretation_matrix"]["supported" if supported else "unsupported"],
        "claim_boundary":c["claim_boundary"],
        "submission_claims_unchanged":True
    }
    # Remove duplicated rows_for_cross wrapper but retain rows in test for inspectability.
    for p in panels:
        panels[p].pop("rows_for_cross",None)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    lines=["# Relative tag-burden vs vertical-identity strength v1","",
           "**POST-FREEZE TECHNICAL-CONFOUND TEST.**","",
           f"Cross-panel mean |rho| = **{cross['observed_equal_panel_mean_absolute_rho']:.3f}**",
           f"permutation p = **{cross['permutation_p']:.5f}**","",
           "| panel | n | signed rho | |rho| | p |",
           "|---|---:|---:|---:|---:|"]
    for p,r in panels.items():
        if not r["eligible"]:
            lines.append(f"| {p} | {r['matched_n']} | NA | NA | NA |")
        else:
            t=r["test"]
            lines.append(f"| {p} | {t['n']} | {t['signed_spearman_rho']:+.3f} | {t['absolute_spearman_rho']:.3f} | {t['two_sided_permutation_p']:.4f} |")
    lines += ["","## Interpretation","",payload["interpretation"],""]
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps({
        "cross_mean_abs_rho":cross["observed_equal_panel_mean_absolute_rho"],
        "cross_p":cross["permutation_p"],
        "supported":supported,
        "panels":{p:({"n":r["test"]["n"],"rho":r["test"]["signed_spearman_rho"],"p":r["test"]["two_sided_permutation_p"]} if r["eligible"] else {"n":r["matched_n"],"eligible":False}) for p,r in panels.items()}
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
