#!/usr/bin/env python3
"""Audit a published 2025 Costa Rican bat social-call playback experiment.

Never commits or uploads source bat IDs. Only aggregated contrasts saved.
Published source: Gamba-Rios et al., Biology Letters, 10.1098/rsbl.2025.0042
Data: 10.5061/dryad.6djh9w1d3, author GitHub repository (pinned Git blob)
NOT an independent replication of 2019 feeding-buzz×receiver-density H1.
"""
import argparse
import csv
import hashlib
import io
import json
import math
import statistics
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

SOURCE_URL="https://raw.githubusercontent.com/morceglo/Predator-recognition/main/data.csv"
GITHUB_API="https://api.github.com/repos/morceglo/Predator-recognition/contents/data.csv"
SOURCE_BLOB="b8a119df0204ed0beb90b971c97f60cafbdb74cd"
SOURCE_SIZE=9979
FIELDS=["bat","experiment","order","treatment","bat_type","period","response"]
RECORDED_RESPONDERS=38
TOTAL_TESTED=117
PUBLISHED_SOCIAL_GROUPS=33

def source_bytes():
    request=urllib.request.Request(SOURCE_URL,headers={"User-Agent":"H1-Open-Data-Source-Reanalysis/1.0"})
    try:
        with urllib.request.urlopen(request,timeout=25) as fh:
            payload=fh.read(11000)
    except Exception:
        import base64
        request=urllib.request.Request(GITHUB_API,headers={"User-Agent":"H1-Open-Data-Source-Reanalysis/1.0","Accept":"application/vnd.github+json"})
        with urllib.request.urlopen(request,timeout=25) as fh:
            j=json.loads(fh.read())
        payload=base64.b64decode(j["content"])
    actual=hashlib.sha1(b"blob "+str(len(payload)).encode()+b"\x00"+payload).hexdigest()
    if actual!=SOURCE_BLOB or len(payload)!=SOURCE_SIZE:
        raise ValueError("Original Git source has changed: block analysis")
    return payload

def parse(payload):
    text=payload.decode("utf-8-sig")
    reader=csv.DictReader(io.StringIO(text,newline=""),delimiter=";")
    if reader.fieldnames!=FIELDS:raise ValueError("Original columns changed")
    raw=list(reader)
    if len(raw)!=228:raise ValueError("Expected 228 original source rows")
    bats=defaultdict(dict)
    for row in raw:
        ident=row["bat"];t=row["treatment"];p=row["period"]
        if t not in ("predator","non-predator") or p not in ("before","during","after"):
            raise ValueError("Unexpected original source labels")
        if row["order"] not in ("NP-P","P-NP"):raise ValueError("Unrecognized stimulus order")
        if row["bat_type"] not in ("control","frugivorous","insectivorous","carnivorous"):
            raise ValueError("Unrecognized emitted bat type")
        count=int(row["response"])
        if count<0:raise ValueError("negative call count")
        g=bats[ident]
        if t not in g:g[t]={"order":row["order"],"bat_type":row["bat_type"]}
        if p in g[t]:raise ValueError("duplicate 30s period")
        g[t][p]=count
    if len(bats)!=RECORDED_RESPONDERS:raise ValueError("Not exactly 38 responsive source individuals")
    records=[]
    for ident,g in bats.items():
        if set(g)!={"predator","non-predator"}:raise ValueError("Incomplete within-bat condition pair")
        for t in g:
            if not set(["before","during","after"]).issubset(g[t]):raise ValueError("Incomplete time phase")
        P=g["predator"];N=g["non-predator"]
        if P["order"]!=N["order"] or P["bat_type"]!="carnivorous":
            raise ValueError("Within-bat playback provenance mismatch")
        d=(
          math.log1p(P["during"])-math.log1p(P["before"])
          -(math.log1p(N["during"])-math.log1p(N["before"]))
        )
        records.append({"order":P["order"],"np_type":N["bat_type"],
                        "primary":d,
                        "raw_difference":(P["during"]-P["before"])-(N["during"]-N["before"]),
                        "during_log_diff":math.log1p(P["during"])-math.log1p(N["during"]),
                        "after_minus_before_relative":(
                         math.log1p(P["after"])-math.log1p(P["before"])
                         -math.log1p(N["after"])+math.log1p(N["before"])),
                        "pre_pred":P["before"],"during_pred":P["during"],
                        "pre_nonpred":N["before"],"during_nonpred":N["during"]})
    if Counter(r["order"] for r in records)!={"NP-P":22,"P-NP":16}:
        raise ValueError("Presentation order roster changed")
    if Counter(r["np_type"] for r in records)!={"control":14,"frugivorous":12,"insectivorous":12}:
        raise ValueError("Nonpredator category roster changed")
    return records

def describe(rows):
    if not rows:return None
    x=[r["primary"] for r in rows]
    return {
      "n_responder_bats":len(rows),
      "mean_primary_log_contrast":statistics.mean(x),
      "median_primary_log_contrast":statistics.median(x),
      "negative_bats":sum(v<0 for v in x),"positive_bats":sum(v>0 for v in x),
      "zero_bats":sum(v==0 for v in x),
      "mean_raw_count_contrast":statistics.mean(r["raw_difference"] for r in rows),
      "mean_log_during_predator_minus_nonpredator":statistics.mean(r["during_log_diff"] for r in rows),
      "mean_after_minus_before_relative":statistics.mean(r["after_minus_before_relative"] for r in rows),
      "mean_predator_before":statistics.mean(r["pre_pred"] for r in rows),
      "mean_predator_during":statistics.mean(r["during_pred"] for r in rows),
      "mean_nonpredator_before":statistics.mean(r["pre_nonpred"] for r in rows),
      "mean_nonpredator_during":statistics.mean(r["during_nonpred"] for r in rows),
    }

def analyze():
    payload=source_bytes()
    rows=parse(payload)
    out={
      "status":"ORIGINAL_GITHUB_BLOB_VERIFIED_CONDITIONAL_RESPONDER_REANALYSIS",
      "source_doi":"10.5061/dryad.6djh9w1d3",
      "paper_doi":"10.1098/rsbl.2025.0042",
      "original_author_git_blob":SOURCE_BLOB,
      "source_sha256":hashlib.sha256(payload).hexdigest(),
      "original_bytes":len(payload),"original_rows":228,
      "sample_design":{"tested_bats":TOTAL_TESTED,"tested_social_groups":PUBLISHED_SOCIAL_GROUPS,
          "source_recorded_responder_bats":RECORDED_RESPONDERS,
          "source_unrepresented_tested_bats":TOTAL_TESTED-RECORDED_RESPONDERS,
          "social_group_ids_in_source":False,
          "group_cluster_uncertainty":"NOT_IDENTIFIED"},
      "estimand":"within-bat [log1p(during_P)-log1p(before_P)] minus [log1p(during_NP)-log1p(before_NP)]",
      "primary":describe(rows),
      "by_order":{k:describe([r for r in rows if r["order"]==k]) for k in ["NP-P","P-NP"]},
      "by_nonpredator_caller":{
          k:describe([r for r in rows if r["np_type"]==k])
          for k in ["control","frugivorous","insectivorous"]},
      "unknown_groups":"The CSV lacks source bat to 33-group membership; no group-independent formal inference.",
      "original_published_result":"Predator eavesdropping suppresses social calls; demonstrated in original 2025 paper, NOT new.",
      "not_independent_2019_foraging_buzz_moderation_replication":True,
      "not_cross_species_population_law":True,
      "raw_rows_or_subject_identifiers_committed":False,
      "missing_bats_not_imputed":True
    }
    return out

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("/tmp/h1_costa_rica_2025_derived.json"))
    args=p.parse_args()
    out=analyze()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("2025 Costa Rica source SHA256",out["source_sha256"],"n",out["primary"]["n_responder_bats"])
    print("PRIMARY",json.dumps(out["primary"]))
    print("BY_ORDER",json.dumps({k:{"n":v["n_responder_bats"],"mean":v["mean_primary_log_contrast"],"negative":v["negative_bats"]} for k,v in out["by_order"].items()}))
    print("BY_NONPRED",json.dumps({k:{"n":v["n_responder_bats"],"mean":v["mean_primary_log_contrast"],"negative":v["negative_bats"]} for k,v in out["by_nonpredator_caller"].items()}))
