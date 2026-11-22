"""Rousettus author-GitHub release: original source-KEY-only join audit.

This is NOT a Dryad-identical mirror: publisher Dryad byte sizes differ.
Read only predeclared key indices from four pinned Github CSV objects.
No outcome (visitation count, visited, foraging duration) values are accessed
or written. No bat IDs, bat locations, tree coordinates or per-row output
is persisted; only aggregate structural support / exact literal overlaps.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

REPOSITORY="EmmLourie/Information-transfer-analysis"
COMMIT="1d7edbdbb87d9df048ab42a0b425a1966d491e86"
# Byte count and git-blob SHA come from author-maintained repository at this ref.
ALLOW={
  "Field_Manipulation_Table.csv":(291,"781f419a599e39f9aaf862b03ff0854a14719ec0"),
  "Tags_manipulated_and_visiting.csv":(1371,"48a2ed7b76d27402daf9544a1d9836165b7c0e44"),
  "visits_to_f.sycamorus.csv":(197784,"5d43cfc5ff6fafd7ad8b259cda96d270011fda1e"),
  "Ficus syc Neot.csv":(62,"0c650594bbf12afe6d862a35c76be8ef45e6d864"),
}
KEYS={
  "Field_Manipulation_Table.csv":("date_manipulation","Cave_roost"),
  "Tags_manipulated_and_visiting.csv":("tags","date_manipulation","Cave origin"),
  "visits_to_f.sycamorus.csv":("TAG","date_global","cave_origin","X_tree","Y_tree"),
  "Ficus syc Neot.csv":("Species","loc","X","Y"),
}
NA={"","NA","NaN","nan","null","NULL","N/A"}
PASS="ROUS_AUTHOR_PINNED_SOURCE_KEYS_VERIFIED_NOT_DRYAD_EQUIVALENT"


def download_pinned_author_file(name, expected):
    if name not in ALLOW or expected!=ALLOW[name][0]:
        raise ValueError("NONALLOWLISTED_AUTHOR_OR_SIZE")
    url=f"https://raw.githubusercontent.com/{REPOSITORY}/{COMMIT}/data_R/{quote(name)}"
    req=Request(url,headers={"User-Agent":"batter-source-keys-only/1.0"})
    with urlopen(req,timeout=35) as response:
        parsed=urlparse(response.url)
        if parsed.scheme!="https" or parsed.netloc!="raw.githubusercontent.com":
            raise RuntimeError("AUTHOR_GIT_REDIRECT_HOST_MISMATCH")
        if response.status!=200:
            raise RuntimeError("AUTHOR_GIT_GET_NOT_OK")
        raw=response.read(expected+1)
    if len(raw)!=expected:
        raise RuntimeError("AUTHOR_GIT_LENGTH_MISMATCH")
    return raw


def key_rows_only(name, raw):
    """Select indexed keys without materializing any outcome column values."""
    reader=csv.reader(io.StringIO(raw.decode("utf-8-sig"),newline=""))
    header=next(reader,None)
    if not header or len(header)!=len(set(header)):
        raise RuntimeError("AUTHOR_GIT_CSV_HEADER_INVALID")
    fields=KEYS[name]
    if not all(key in header for key in fields):
        raise RuntimeError("AUTHOR_GIT_CSV_JOIN_KEY_MISSING_"+name)
    indices=tuple(header.index(k) for k in fields)
    rows=[]
    for row in reader:
        if len(row)!=len(header):
            raise RuntimeError("AUTHOR_GIT_CSV_ROW_WIDTH_STOP_"+name)
        rows.append(tuple(row[i].strip() for i in indices))
    if not rows:
        raise RuntimeError("AUTHOR_GIT_CSV_EMPTY_"+name)
    return header,rows


def key_stats(fetch=download_pinned_author_file):
    matrix={}
    for name,(n,expected_sha) in ALLOW.items():
        raw=fetch(name,n)
        if not isinstance(raw,bytes) or len(raw)!=n:
            raise RuntimeError("AUTHOR_GIT_BYTE_LENGTH_STOP_"+name)
        git_sha=hashlib.sha1(b"blob "+str(n).encode()+b"\0"+raw).hexdigest()
        if git_sha != expected_sha:
            raise RuntimeError("AUTHOR_GIT_BLOB_SHA_MISMATCH_"+name)
        header,keys=key_rows_only(name,raw)
        matrix[name]=keys
    manip=matrix["Field_Manipulation_Table.csv"]
    tags=matrix["Tags_manipulated_and_visiting.csv"]
    visits=matrix["visits_to_f.sycamorus.csv"]
    trees=matrix["Ficus syc Neot.csv"]

    valid=lambda x:x not in NA
    manip_dates={r[0] for r in manip if valid(r[0])}
    tag_dates={r[1] for r in tags if valid(r[1])}
    manip_caves={r[1] for r in manip if valid(r[1])}
    tag_caves={r[2] for r in tags if valid(r[2])}
    visit_caves={r[2] for r in visits if valid(r[2])}
    tag_ids={r[0] for r in tags if valid(r[0])}
    visit_ids={r[0] for r in visits if valid(r[0])}
    tree_xy={(r[2],r[3]) for r in trees if valid(r[2]) and valid(r[3])}
    visit_xy={(r[3],r[4]) for r in visits if valid(r[3]) and valid(r[4])}
    joint_tagdate={(r[0],r[1]) for r in tags if valid(r[0]) and valid(r[1])}
    joint_visitdate={(r[0],r[1]) for r in visits if valid(r[0]) and valid(r[1])}
    # Date strings and tree XY tested as literal strings, never coerced.
    # "Nonzero" is a support observation, not a valid event-level join yet.
    return {
      "schema":"batter.rous_author_source_key_audit.v1",
      "status":PASS,
      "author_repository":REPOSITORY,
      "commit_sha":COMMIT,
      "source_version_identical_to_Dryad":False,
      "source_rows_by_file":{n:len(matrix[n]) for n in sorted(ALLOW)},
      "source_git_blob_sha_by_file":{n:ALLOW[n][1] for n in sorted(ALLOW)},
      "required_key_columns":{n:list(KEYS[n]) for n in sorted(ALLOW)},
      "join_key_support":{
         "manipulated_dates":len(manip_dates),
         "tag_dates":len(tag_dates),
         "literal_shared_manipulation_dates":len(manip_dates & tag_dates),
         "manipulation_caves":len(manip_caves),
         "tag_caves":len(tag_caves),
         "visit_caves":len(visit_caves),
         "literal_shared_manipulation_tag_caves":len(manip_caves & tag_caves),
         "literal_shared_tag_visit_caves":len(tag_caves & visit_caves),
         "tag_table_unique_individual_labels":len(tag_ids),
         "visit_table_unique_individual_labels":len(visit_ids),
         "literal_shared_individual_labels":len(tag_ids & visit_ids),
         "literal_shared_individual_date_pairs":len(joint_tagdate & joint_visitdate),
         "tree_table_unique_literal_XY_pairs":len(tree_xy),
         "visit_table_unique_literal_tree_XY_pairs":len(visit_xy),
         "literal_shared_tree_XY_pairs":len(tree_xy & visit_xy),
      },
      "source_rows_or_identifier_values_persisted":False,
      "original_animal_identifiers_persisted":False,
      "original_tree_coordinates_persisted":False,
      "biology_response_columns_read":False,
      "actual_event_level_join_validated":False,
      "height_above_ground_measurement":None,
      "resource_supply_measurement":None,
      "new_2d_effect_estimate":None,
      "new_5d_effect_estimate":None,
    }


def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--out",default="prospective/resource_behavior_sdm/rous_author_source_key_receipt.json")
    args=arg.parse_args()
    target=Path(args.out)
    target.parent.mkdir(parents=True,exist_ok=True)
    try:
        result=key_stats()
    except Exception as exc:
        result={
          "schema":"batter.rous_author_source_key_audit.v1",
          "status":"ORIGINAL_AUTHOR_SOURCE_KEY_STOP",
          "error":str(exc)[:240],
          "biology_response_columns_read":False,
          "original_animal_identifiers_persisted":False,
          "new_5d_effect_estimate":None,
        }
    target.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("ROUS_AUTHOR_KEY",result["status"],flush=True)
    if "join_key_support" in result:
        print("STRUCTURAL_AGGREGATES",json.dumps(result["join_key_support"],sort_keys=True),flush=True)
    else:
        print("STOP_REASON",result["error"],flush=True)
    return 0 if result["status"]==PASS else 3


if __name__=="__main__":
    raise SystemExit(main())
