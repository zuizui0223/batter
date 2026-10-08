#!/usr/bin/env python3
"""Strict categorical-only source support probe: Zenodo 20927789.

Read ONLY batID, filename, dataStructNr, recTimePosix, inCluster/isExcluded,
without logging or interpreting physiological measurement values.
NO new bat sensorimotor effect/estimate. See frozen categorical gate document.
"""
from __future__ import annotations
import argparse, collections, datetime as dt, hashlib, json, re

import requests

ID="20927789"
API="https://zenodo.org/api/records/20927789"
PREFIX="https://zenodo.org/"
ROOT="10.5281/zenodo.20927789"
SOURCE_FILES={
 "mdau":"mdau_basement_config_UCLOUD_01_collect_20241008_203617_processed_20251112_szred_lcs_20251114_PARTIALLY_export.csv",
 "ppyg":"ppyg_config_UCLOUD_01_collect_20241008_122450_processed_20251112_szred_lcs_20251114_export.csv",
}
LIMIT=16 * 1024 * 1024
KEYS=("batID","filename","dataStructNr","recTimePosix","inCluster","isExcluded")
UA={"User-Agent":"batter-academic-categorical-support/1.0"}
TIMEOUT=(12,55)

def ids_only(requested, expected):
    if expected != ROOT:
        raise ValueError("wrong Zenodo source")
    return {"evidence":"STRUCTURAL_CATEGORICAL_ONLY_NO_EAR_OR_FLIGHT_VALUES",
            "source_doi":expected,"recid":ID,
            "performed_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
            "raw_measurements_opened":False,
            "results":{},"status":"STOP_SOURCE_INACCESSIBLE"}

def check_csv_header(header):
    if header[:2] == bytes([31,139]):
        raise ValueError("binary compressed CSV is not a header")
    text=header.decode("utf-8-sig",errors="strict").strip("\r\n")
    if any(ord(ch)<32 and ord(ch) not in (9,10,13) for ch in text):
        raise ValueError("non-text CSV header")
    delim=max(("|",",","\t",";"),key=lambda k:text.count(k))
    cols=text.split(delim)
    if len(cols)<3 or "batID" not in cols or "filename" not in cols:
        raise ValueError("required categorical source headers unavailable")
    indices={k:cols.index(k) for k in KEYS if k in cols}
    return delim,indices,cols

def categorical_probe(session,source_key,desc):
    filename=SOURCE_FILES[source_key]
    announced=int(desc.get("size") or 0)
    entry={"species_source":source_key, "filename":filename,
           "source_size":announced,"status":"STOP_SOURCE_INACCESSIBLE",
           "record_total":0,"id_count":0,"unique_file_count":0,
           "unique_bat_file_pairs":0,
           "animal_unique_recording_count_distribution":{},
           "anonymous_animal_counts":[],
           "has_two_verified_task_contexts":False,
           "only_categorical_fields_parsed":True,
           "unsupported_individual_claims":True}
    if announced<=0 or announced>LIMIT:
        entry["status"]="STOP_FILE_SIZE_OR_UNKNOWN";return entry
    links=desc.get("links") or {}
    uri=links.get("content") or links.get("self")
    if not uri or not uri.startswith(PREFIX):
        entry["status"]="STOP_OFFICIAL_ZENODO_URL_UNAVAILABLE";return entry
    anon=collections.defaultdict(set)
    file_counts=collections.Counter()
    struct_counts=collections.Counter()
    flag_counts={"inCluster":collections.Counter(),"isExcluded":collections.Counter()}
    seen_key_missing=collections.Counter()
    try:
        with session.get(uri,headers=UA,timeout=TIMEOUT,stream=True) as response:
            entry["http_status"]=response.status_code
            if response.status_code!=200:
                entry["status"]="DOWNLOAD_HTTP_"+str(response.status_code);return entry
            it=response.iter_lines(chunk_size=16384,decode_unicode=False)
            header=next(it,b"")
            delim,ix,cols=check_csv_header(header)
            entry["separator"]=delim
            entry["categorical_header_available"]=list(ix)
            for raw in it:
                if not raw.strip():continue
                # This only separates string fields; no physiological numeric field
                # is converted, measured, summarized, or returned.
                fields=raw.decode("utf-8-sig",errors="replace").rstrip("\r\n").split(delim)
                if len(fields)!=len(cols):
                    entry["status"]="STOP_RAGGED_SOURCE_CSV"
                    entry["bad_row_index"]=entry["record_total"]+1
                    return entry
                entry["record_total"]+=1
                bat=fields[ix["batID"]].strip()
                file=fields[ix["filename"]].strip()
                if not bat or not file:
                    seen_key_missing["bat_or_filename"]+=1
                    continue
                anon[bat].add(file)
                file_counts[file]+=1
                if "dataStructNr" in ix:
                    struct_counts[(file,fields[ix["dataStructNr"]].strip())]+=1
                for flag in ("inCluster","isExcluded"):
                    if flag in ix:flag_counts[flag][fields[ix[flag]].strip()]+=1
        entry["id_count"]=len(anon)
        entry["unique_file_count"]=len(file_counts)
        entry["unique_bat_file_pairs"]=sum(len(q) for q in anon.values())
        entry["number_source_file_structure_groups"]=len(struct_counts)
        entry["missing_id_or_filename_rows"]=seen_key_missing["bat_or_filename"]
        entry["anonymous_animal_counts"]=sorted((len(files) for files in anon.values()),reverse=True)
        entry["animal_unique_recording_count_distribution"]=dict(sorted(
            (str(k),v) for k,v in collections.Counter(map(len,anon.values())).items()))
        entry["eligible_animal_count_at_three_bouts"]=sum(len(q)>=3 for q in anon.values())
        entry["categorical_flag_distributions"]={k:dict(v) for k,v in flag_counts.items()}
        # Each current species has ONE fixed exported source/context; original
        # task-context metadata cannot be inferred solely from filenames.
        entry["status"]="STOP_NO_INDEPENDENT_INDIVIDUAL_BOUTS" if (
            entry["eligible_animal_count_at_three_bouts"]<5
            or entry["unique_bat_file_pairs"]<15
            or not entry["has_two_verified_task_contexts"]
        ) else "PASS_CATEGORICAL_COUNTS_SUBJECT_TO_AUTHORED_ID_DOCUMENTATION"
    except Exception as ex:
        entry["status"]="STOP_READ_ERROR_"+type(ex).__name__
        entry["error"]=str(ex)[:160]
    return entry

def selftest():
    for ch in [b"batID|filename|dataStructNr|inCluster",
               b"batID,filename,dataStructNr,inCluster"]:
        d,ix,c=check_csv_header(ch)
        assert d in ("|",",") and "filename" in ix and len(c)==4
    try:check_csv_header(bytes([31,139])+b"binary")
    except ValueError:pass
    else:raise AssertionError("gzip binary false pass")
    return {"gzip_binary_rejected":True,"pipe_csv_supported":True}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--out",default="PINNA_FLIGHT_CATEGORICAL_RECEIPT_V1.json")
    args=ap.parse_args()
    selftest()
    if args.self_test:
        print(json.dumps(selftest()));return
    rec=ids_only(SOURCE_FILES,ROOT)
    s=requests.Session()
    try:
        resp=s.get(API,timeout=TIMEOUT,headers=UA)
        rec["http_status"]=resp.status_code
        resp.raise_for_status()
        payload=resp.json()
        if str(payload.get("id"))!=ID or str(payload.get("doi"))!=ROOT:
            raise ValueError("Zenodo record DOI/ID mismatch")
        fl={f.get("key"):f for f in payload.get("files",[])}
        for key,name in SOURCE_FILES.items():
            source=fl.get(name)
            rec["results"][key]=categorical_probe(s,key,source) if source else {"status":"STOP_FILE_NOT_LISTED"}
        rec["status"]="STOP_NO_INDEPENDENT_INDIVIDUAL_BOUTS"
    except Exception as ex:
        rec["error"]=type(ex).__name__+":"+str(ex)[:160]
        rec["status"]="STOP_SOURCE_INACCESSIBLE"
    with open(args.out,"w",encoding="utf8") as f:
        json.dump(rec,f,indent=2,sort_keys=True,ensure_ascii=False);f.write("\n")
    print(json.dumps({"status":rec["status"],"results":{
        k:{"status":v["status"],"bat_count":v.get("id_count"),
           "files":v.get("unique_file_count"),"bat_files":v.get("unique_bat_file_pairs"),
           "three_bout_bats":v.get("eligible_animal_count_at_three_bouts")}
        for k,v in rec["results"].items()}},ensure_ascii=False))

if __name__=="__main__":main()
