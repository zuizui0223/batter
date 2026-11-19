#!/usr/bin/env python3
"""Targeted original COMBINE nonimputed-reported trait CSV verification.

Fetch ONLY authoritative Figshare file 27703263, not thousands of imputation
files, and verify original MD5 against metadata and a secondary Git mirror.
No raw species data is committed or emitted in GitHub artifact.
"""
import collections
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import urllib.request

API="https://api.figshare.com/v2/articles/13028255/versions/4"
FIG_FILE_ID=27703263
FIG_MD5="d894586c3858620723b1182d8b491d3e"
FIG_SIZE=1612538
MIRROR="https://raw.githubusercontent.com/AleAliSousa/Evo-M1-Trait-Data/main/Soria_etal_2021/Soria_etal_2021_Traitdatareported_snapshot.csv"
MIRROR_BLOB="7e274bac17eba845d93cdd27c1357605af3d710e"
OUT=Path(os.getenv("H1_COMBINE_SOURCE_RECEIPT","/tmp/h1_combine_original_headers.json"))

def get(url,limit=4000000):
    req=urllib.request.Request(url,headers={"User-Agent":"BatCOMBINE-Reported-Source-Audit/1.1","Accept":"text/csv,application/json,application/octet-stream,*/*"})
    with urllib.request.urlopen(req,timeout=35) as r:
        b=r.read(limit+1)
        if len(b)>limit:raise ValueError("source_exceeds_byte_limit")
        return b,r.status

def profile(data):
    records=list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"),newline="")))
    assert len(records)==6263
    assert len(records[0])==60
    bats=[r for r in records if r["order"]=="Chiroptera"]
    assert len(bats)==1342
    isnum=lambda value: value not in ("","NA",None) and _numeric(value)
    group=[r for r in bats if isnum(r["social_group_n"])]
    assert len(group)==45
    fam=collections.Counter(r["family"] for r in group)
    n_one=sum(float(r["social_group_n"])==1 for r in group)
    n_gt1=sum(float(r["social_group_n"])>1 for r in group)
    n_gt5=sum(float(r["social_group_n"])>5 for r in group)
    assert (n_one,n_gt1,n_gt5)==(33,12,3)
    assert fam=={"Pteropodidae":30,"Vespertilionidae":9,
                 "Emballonuridae":3,"Nycteridae":1,
                 "Hipposideridae":1,"Rhinolophidae":1}
    assert all(isnum(r["dphy_invertebrate"]) and isnum(r["dphy_plant"]) and isnum(r["adult_mass_g"]) for r in group)
    assert all(r["family"]=="Pteropodidae" for r in group if float(r["dphy_plant"])>50)
    plants=[r for r in group if float(r["dphy_plant"])>50]
    assert len(plants)==30
    unmatched=[r for r in bats if r["iucn2020_binomial"]=="Not recognised"]
    assert len(unmatched)==7
    return {
      "original_source_rows":len(records),"original_columns":len(records[0]),
      "bat_taxon_rows":len(bats),
      "iucn2020_unrecognized_bat_taxa":len(unmatched),
      "bat_reported_social_group_n":len(group),
      "bat_social_group_n_missing":len(bats)-len(group),
      "reported_group_size_equals_one":n_one,
      "reported_group_size_gt_one":n_gt1,
      "reported_group_size_gt_five":n_gt5,
      "reported_group_size_by_family":dict(sorted(fam.items())),
      "all_reported_45_have_diet_and_mass":True,
      "majority_plant_reported_n":len(plants),
      "majority_plant_exactly_matches_Pteropodidae_in_reported_sample":True,
      "family_adjusted_binary_plant_effect_identified":False,
      "claim_boundary":"group size, not male group formation/social information"
    }
def _numeric(x):
    try:return float(x)==float(x)
    except (ValueError,TypeError):return False

def main():
    out={"status":"STOP_NO_VERIFIED_ORIGINAL_CONTENT",
         "article_id":13028255,"article_version":4,"file_id":FIG_FILE_ID,
         "reported_source_md5":FIG_MD5,"expected_bytes":FIG_SIZE,
         "original_outcomes_not_fitted":True,"attempts":[]}
    try:
        meta_body,st=get(API)
        meta=json.loads(meta_body)
        source=[f for f in meta.get("files",[]) if f.get("id")==FIG_FILE_ID and f.get("name")=="trait_data_reported.csv"]
        if len(source)!=1:raise ValueError("Figshare metadata no unique reported CSV")
        f=source[0]
        assert f["size"]==FIG_SIZE and f.get("supplied_md5")==FIG_MD5
        out["attempts"].append({"source":"Figshare_v4_metadata","status":st,"result":"PASS"})

        mirror,sm=get(MIRROR)
        gitsha=hashlib.sha1(b"blob "+str(len(mirror)).encode()+b"\x00"+mirror).hexdigest()
        md5=hashlib.md5(mirror).hexdigest()
        if gitsha!=MIRROR_BLOB:raise ValueError("Git mirror blob SHA mismatch")
        if md5!=FIG_MD5 or len(mirror)!=FIG_SIZE:
            raise ValueError("Git mirror does not match official original Figshare MD5/size")
        out["attempts"].append({"source":"GitHub mirror","status":sm,"bytes":len(mirror),
                                 "md5":md5,"git_blob_sha1":gitsha,
                                 "result":"MATCHES_OFFICIAL_FIGSHARE_HASH"})
        out["source_sha256"]=hashlib.sha256(mirror).hexdigest()
        out["official_original_published_md5_verified"]=True
        out["original_reported_source_profile"]=profile(mirror)
        out["status"]="ORIGINAL_PUBLISHED_HASH_MATCH_VIA_MIRROR"
        # The exact Figshare file-stream remains an optional independent
        # origin check. A 403 here is not a false data-schema failure because
        # its authoritative checksum has already authenticated the bytes.
        try:
            actual,st=get(f["download_url"])
            if actual!=mirror:raise ValueError("Original Figshare differs from published-hash-matching mirror")
            out["attempts"].append({"source":"Direct Figshare original","status":st,
                                     "result":"BYTE_IDENTICAL"})
            out["original_download_direct_verified"]=True
            out["status"]="ORIGINAL_DOWNLOAD_AND_MIRROR_BYTE_IDENTICAL"
        except Exception as ex:
            out["attempts"].append({"source":"Direct Figshare original",
                                  "result":"ACCESS_OR_ORIGIN_NOT_VERIFIED",
                                  "exception":type(ex).__name__,
                                  "detail":str(ex)[:170]})
            out["original_download_direct_verified"]=False
    except Exception as e:
        out["attempts"].append({"source":"source_verification",
                                  "exception":type(e).__name__,"detail":str(e)[:180],"result":"STOP"})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False,indent=2))
    if out["status"] not in ("ORIGINAL_PUBLISHED_HASH_MATCH_VIA_MIRROR",
                             "ORIGINAL_DOWNLOAD_AND_MIRROR_BYTE_IDENTICAL"):
        raise SystemExit(2)

if __name__=="__main__":
    main()
