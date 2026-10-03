#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, io, json, re, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"prospective/rousettus_social_seeding/public_source_preflight_v1.json"
OUT_MD=ROOT/"prospective/rousettus_social_seeding/PUBLIC_SOURCE_PREFLIGHT_RESULT_V1.md"

REPO="EmmLourie/Information-transfer-analysis"
COMMIT="1d7edbdbb87d9df048ab42a0b425a1966d491e86"
FILES={
 "visitors":("data_R/Tags_manipulated_and_visiting.csv","48a2ed7b76d27402daf9544a1d9836165b7c0e44"),
 "individuals":("data_R/ind_info.csv","992637c190c2918bb6a95d8eb31235df8ea313c4"),
 "field":("data_R/Field_Manipulation_Table.csv","781f419a599e39f9aaf862b03ff0854a14719ec0"),
 "analysis":("data_R/Ficus_Sycamorus_Experiment_Analysis.Rmd","089de09fc57bfdc2b475c80c1eb9cae0c24c2096"),
 "sharing":("Sharing_Information_Trees.Rmd","91bd598d2cf2543814aab89b4fb42ac496b0abe5"),
}
EXPECTED_SMEARED={"6485","6637","6654","6639"}
EXPECTED_NAIVE={"6399","6411","6414","6635","6428","6641","6640","6991","6824","6993"}

def git_blob_sha(data:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def get(path,sha):
    url=f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/{path}"
    req=urllib.request.Request(url,headers={"User-Agent":"batter-rousettus-source-preflight/1.0"})
    with urllib.request.urlopen(req,timeout=120) as r:
        data=r.read()
    obs=git_blob_sha(data)
    if obs!=sha:
        raise RuntimeError(f"{path}: git blob sha {obs} != {sha}")
    return data

def rows(data):
    return list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))

def main():
    data={k:get(*v) for k,v in FILES.items()}
    visitors=rows(data["visitors"])
    ind=rows(data["individuals"])
    analysis=data["analysis"].decode("utf-8",errors="replace")
    sharing=data["sharing"].decode("utf-8",errors="replace")

    m=re.search(r'tag_smeared\s*<-\s*c\(([^\)]*)\)',analysis)
    if not m:
        raise RuntimeError("could not find tag_smeared source definition")
    smeared=set(re.findall(r'"(\d+)"',m.group(1)))

    visitor_ids={str(r.get("tags","")).strip() for r in visitors if str(r.get("tags","")).strip()}
    naive=visitor_ids-smeared

    age_by_tag={}
    for r in ind:
        tag=str(r.get("TAG","")).strip()
        age=str(r.get("age","")).strip()
        if not tag:
            continue
        age_by_tag.setdefault(tag,set())
        if age:
            age_by_tag[tag].add(age)

    pups={t for t in naive if "pup" in {x.lower() for x in age_by_tag.get(t,set())}}
    missing_age=sorted(t for t in naive if not age_by_tag.get(t))
    independent=naive-pups

    source_pup_warning=("remove pups" in sharing.lower() and "attached to their mothers" in sharing.lower())

    field=rows(data["field"])
    row_inconsistencies=[]
    for r in field:
        try:
            nt=int(r["n_total"]) if r.get("n_total") not in ("","NA",None) else None
            nn=int(r["n_naive"]) if r.get("n_naive") not in ("","NA",None) else None
            nm=int(r["No_manipulated_bats"]) if r.get("No_manipulated_bats") not in ("","NA",None) else None
        except Exception:
            continue
        if None not in (nt,nn,nm) and nt!=nn+nm:
            row_inconsistencies.append({
              "date_manipulation":r.get("date_manipulation"),
              "Cave_roost":r.get("Cave_roost"),
              "No_manipulated_bats":nm,"n_naive":nn,"n_total":nt,
            })

    checks={
      "visitor_count_14":len(visitor_ids)==14,
      "smeared_ids_exact":smeared==EXPECTED_SMEARED,
      "naive_visitor_ids_exact":naive==EXPECTED_NAIVE,
      "naive_visitor_count_10":len(naive)==10,
      "explicit_pup_exact_6641":pups=={"6641"},
      "independent_candidate_count_9":len(independent)==9,
      "source_pup_warning_present":source_pup_warning,
    }
    payload={
      "schema_version":1,
      "classification":"public source tables/code only; no raw route geometry opened",
      "external_repo":REPO,"commit":COMMIT,
      "file_blob_shas":{k:v[1] for k,v in FILES.items()},
      "visitor_ids":sorted(visitor_ids),
      "smeared_visitor_ids":sorted(smeared),
      "naive_visitor_ids":sorted(naive),
      "age_values_by_naive_visitor":{t:sorted(age_by_tag.get(t,set())) for t in sorted(naive)},
      "explicit_pup_naive_visitors":sorted(pups),
      "naive_visitors_missing_age_metadata":missing_age,
      "independent_naive_candidate_ids":sorted(independent),
      "field_table_internal_count_inconsistencies":row_inconsistencies,
      "checks":checks,
      "pass":all(checks.values()),
      "route_geometry_opened":False,
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    lines=["# Rousettus public-source preflight v1","",
      "**PUBLIC SMALL TABLES + SOURCE CODE ONLY. No raw ATLAS route geometry opened.**","",
      f"Visitor rows / unique visitor IDs: **{len(visitors)} / {len(visitor_ids)}**",
      f"Directly smeared visitors: **{len(smeared)}** — {', '.join(sorted(smeared))}",
      f"Naive target visitors: **{len(naive)}** — {', '.join(sorted(naive))}",
      f"Explicit pup among naive visitors: **{', '.join(sorted(pups)) or 'none'}**",
      f"Independent naive candidates before raw-track support: **{len(independent)}**",
      f"Naive visitors with no age row in pinned ind_info: **{', '.join(missing_age) or 'none'}**","",
      "Field-table count inconsistencies are recorded in the JSON but not used for canonical experiment n.","",
      f"Preflight: **{'PASS' if payload['pass'] else 'FAIL'}**",""]
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps({"pass":payload["pass"],"naive_n":len(naive),"pups":sorted(pups),"candidate_n":len(independent),"missing_age":missing_age,"field_inconsistencies":row_inconsistencies},sort_keys=True))

if __name__=="__main__":
    main()
