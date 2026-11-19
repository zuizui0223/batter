#!/usr/bin/env python3
"""Original-public-CSV eligible Molossus individual-discrimination recalculation.

Input supplied by researcher, NOT committed to GitHub. Requires numpy.
Source: https://doi.org/10.5061/dryad.tqjq2bvvx
This is NOT the same estimand as Lewanzik's 2019 buzz×baseline response.
"""
import argparse
import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

SOURCE_MD5="b4b9970eac190601b4a291725137c110"
SOURCE_URL="https://zenodo.org/records/4953622/files/molossusinddiscrim_data_videoanalysis.csv?download=1"
REQUIRED={"Bat ID","Roost ID","Date","Call Type","Treatment","Prehabituation",
          "Posthabituation","Dishabituation","Rehabituation"}

def load(path):
    md5=hashlib.md5(path.read_bytes()).hexdigest()
    with path.open(encoding="utf-8-sig",newline="") as f:
        rows=list(csv.DictReader(f))
    if not rows or not REQUIRED.issubset(rows[0]):
        raise ValueError("wrong original data headers")
    if len(rows)!=51:
        raise ValueError("published web-visible CSV expected 51 data records")
    for r in rows:
        for key in ("Prehabituation","Posthabituation","Dishabituation","Rehabituation"):
            r[key]=int(r[key])
            if r[key]<0:raise ValueError("negative count")
        if r["Treatment"] not in ("test","control") or r["Call Type"] not in ("search-phase calls","approach calls"):
            raise ValueError("unexpected treatment or call type")
        if 2*r["Posthabituation"]>r["Prehabituation"]:
            raise ValueError("not original paper's 50% habituation gate")
        r["D"]=r["Dishabituation"]-r["Posthabituation"]
    counts=Counter((r["Call Type"],r["Treatment"]) for r in rows)
    if counts[("search-phase calls","test")]!=20 or counts[("search-phase calls","control")]!=14:
        raise ValueError("source search-phase cases do not match paper's 20/14")
    return rows,{"source_md5":md5,"source_bytes_verified":md5==SOURCE_MD5,
                 "published_original_md5":SOURCE_MD5}

def calc(rows,call_type):
    subset=[r for r in rows if r["Call Type"]==call_type]
    by_bat=defaultdict(lambda:{"test":[],"control":[],"roost":None})
    for r in subset:
        x=by_bat[r["Bat ID"]]
        x["roost"]=r["Roost ID"]
        x[r["Treatment"]].append(r["D"])
    matched={}
    for bat,items in by_bat.items():
        if items["test"] and items["control"]:
            matched[bat]={"roost":items["roost"],"d":float(np.mean(items["test"])-np.mean(items["control"]))}
    if not matched:raise ValueError("no matched animals")
    values=np.array([x["d"] for x in matched.values()],dtype=float)
    rng=np.random.default_rng(20261119)
    n=len(values)
    bat_boot=np.mean(rng.choice(values,(20000,n),replace=True),axis=1)
    if n<=17:
        null=np.array(list(itertools.product((-1,1),repeat=n)),dtype=float)@values/n
        p_bat=float(np.mean(np.abs(null)>=abs(values.mean())-1e-12))
    else:p_bat=None
    by_roost=defaultdict(list)
    for v in matched.values():by_roost[v["roost"]].append(v["d"])
    roost_means={k:float(np.mean(v)) for k,v in sorted(by_roost.items())}
    rv=np.array(list(roost_means.values()),dtype=float)
    roost_null=np.array(list(itertools.product((-1,1),repeat=len(rv))),dtype=float)@rv/len(rv)
    roost_boot=np.mean(rng.choice(rv,(20000,len(rv)),replace=True),axis=1)
    leave=[]
    for roost in sorted(by_roost):
        other=[x["d"] for x in matched.values() if x["roost"]!=roost]
        leave.append({"heldout_roost":roost,"remaining_bats":len(other),
                      "mean_training":float(np.mean(other))})
    return {"n_trials":len(subset),"n_individuals":len(by_bat),
            "n_matched_bats":n,"n_matched_roosts":len(by_roost),
            "n_test":sum(x["Treatment"]=="test" for x in subset),
            "n_control":sum(x["Treatment"]=="control" for x in subset),
            "bat_equal_contrast":float(values.mean()),
            "n_positive_bat":int(sum(values>0)),"n_negative_bat":int(sum(values<0)),
            "bat_signflip_p_exploratory":p_bat,
            "bat_bootstrap95":list(map(float,np.quantile(bat_boot,[.025,.975]))),
            "roost_matched_counts":{k:len(v) for k,v in by_roost.items()},
            "roost_mean_contrasts":roost_means,
            "roost_equal_mean":float(rv.mean()),
            "roost_signflip_p_exploratory":float(np.mean(np.abs(roost_null)>=abs(rv.mean())-1e-12)),
            "roost_bootstrap95":list(map(float,np.quantile(roost_boot,[.025,.975]))),
            "roost_leaveout_training_means":leave}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--csv",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    rows,auth=load(args.csv)
    search=calc(rows,"search-phase calls")
    approach=calc(rows,"approach calls")
    result={"status":"REANALYSIS_OF_PUBLISHED_2020_STUDY_NOT_NOVEL_BIOLOGY",
            "source_doi":"10.5061/dryad.tqjq2bvvx",
            "source_url":SOURCE_URL,
            "source_authentication":auth,
            "search":search,"approach":approach,
            "approach_inference":"STOP; <6 matched bats and article's 19 approach trials versus public CSV 17",
            "same_as_lewanzik2019_estimand":False,
            "phylogenetic_meta_analysis_eligible":False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("search",search["n_trials"],"trials",search["n_matched_bats"],"matched bats",
          search["bat_equal_contrast"],"bat mean",search["roost_equal_mean"],"roost mean")
    print("source md5 verified:",auth["source_bytes_verified"])

if __name__=="__main__":
    main()
