#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, io, json, os, re, sqlite3, urllib.error, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"prospective/rousettus_social_seeding/raw_schema_preflight_v1.json"
OUT_MD=ROOT/"prospective/rousettus_social_seeding/RAW_SCHEMA_PREFLIGHT_RESULT_V1.md"
TMP=Path(os.environ.get("RUNNER_TEMP","/tmp"))/"rousettus_dryad_preflight"
TMP.mkdir(parents=True,exist_ok=True)

FILES={
  "june":{"id":3182077,"filename":"Syc_Manipulation_June2020_Filtered.sqlite","kind":"sqlite","candidate_tags":["6399","6411","6414","6635","6428"]},
  "july":{"id":3182078,"filename":"Syc_Manipulation_July2020_Filtered.sqlite","kind":"sqlite","candidate_tags":["6640"]},
  "december":{"id":3182076,"filename":"Syc_Manipulation_Dec2020_Filtered.sqlite","kind":"sqlite","candidate_tags":["6991","6824","6993"]},
  "trees":{"id":3182081,"filename":"manipulations_trees_locations.csv","kind":"csv"},
}
UA="Mozilla/5.0 (compatible; batter-route-schema-preflight/1.0)"

def candidate_urls(file_id:int):
    return [
      f"https://datadryad.org/downloads/file_stream/{file_id}",
      f"https://datadryad.org/api/v2/files/{file_id}/download",
    ]

def looks_blocked(prefix:bytes)->bool:
    x=prefix[:4096].lower()
    return (b"<html" in x or b"<!doctype" in x or b"validating" in x or b"cloudflare" in x)

def download(spec,key):
    errors=[]
    for url in candidate_urls(spec["id"]):
        path=TMP/spec["filename"]
        if path.exists(): path.unlink()
        try:
            req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
            with urllib.request.urlopen(req,timeout=300) as resp:
                h=hashlib.sha256()
                total=0
                first=b""
                with path.open("wb") as fh:
                    while True:
                        chunk=resp.read(1024*1024)
                        if not chunk: break
                        if not first: first=chunk[:4096]
                        if total==0 and looks_blocked(first):
                            raise RuntimeError("received HTML/security challenge instead of file")
                        fh.write(chunk); h.update(chunk); total+=len(chunk)
            if spec["kind"]=="sqlite":
                magic=path.open("rb").read(16)
                if magic!=b"SQLite format 3\x00":
                    raise RuntimeError(f"not SQLite magic: {magic!r}")
            elif total==0:
                raise RuntimeError("empty CSV")
            return {"ok":True,"path":str(path),"url":url,"bytes":total,"sha256":h.hexdigest()}
        except Exception as e:
            errors.append({"url":url,"error":repr(e)})
            try:
                path.unlink()
            except FileNotFoundError:
                pass
    return {"ok":False,"errors":errors}

def qident(name:str)->str:
    return '"' + name.replace('"','""') + '"'

def choose_cols(cols):
    low={c:c.lower() for c in cols}
    def best(patterns,exclude=()):
        scored=[]
        for c,l in low.items():
            if any(x in l for x in exclude): continue
            score=sum(1 for p in patterns if re.search(p,l))
            if score: scored.append((score,-len(c),c))
        return max(scored)[2] if scored else None
    return {
      "tag":best([r"^tag$",r"tag.*id",r"animal.*id",r"individual.*id",r"^id$"],exclude=("quality","grid")),
      "time":best([r"timestamp",r"localization.*time",r"^time$",r"datetime",r"date.*time"]),
      "x":best([r"^x$",r"utm.*x",r"easting",r"location.*x"],exclude=("index",)),
      "y":best([r"^y$",r"utm.*y",r"northing",r"location.*y"],exclude=("quality",)),
      "lat":best([r"latitude",r"^lat$"]),
      "lon":best([r"longitude",r"^lon$",r"^long$"]),
    }

def inspect_sqlite(path,candidate_tags):
    uri=f"file:{path}?mode=ro"
    con=sqlite3.connect(uri,uri=True)
    con.row_factory=sqlite3.Row
    tables=[r[0] for r in con.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name")]
    details=[]
    for table in tables:
        cols=[r[1] for r in con.execute(f"pragma table_info({qident(table)})")]
        picked=choose_cols(cols)
        try: n=int(con.execute(f"select count(*) from {qident(table)}").fetchone()[0])
        except Exception: n=None
        d={"table":table,"row_count":n,"columns":cols,"candidate_columns":picked}
        tagcol=picked["tag"]
        if tagcol:
            present={}
            for tag in candidate_tags:
                try:
                    cnt=int(con.execute(
                      f"select count(*) from {qident(table)} where cast({qident(tagcol)} as text)=?",
                      (str(tag),)).fetchone()[0])
                except Exception:
                    cnt=-1
                present[str(tag)]=cnt
            d["candidate_tag_row_counts"]=present
        timecol=picked["time"]
        if timecol:
            try:
                mn,mx=con.execute(
                  f"select min({qident(timecol)}), max({qident(timecol)}) from {qident(table)}"
                ).fetchone()
                d["time_min"]=None if mn is None else str(mn)
                d["time_max"]=None if mx is None else str(mx)
            except Exception as e:
                d["time_range_error"]=repr(e)
        details.append(d)
    con.close()

    eligible=[d for d in details if d["candidate_columns"].get("tag") and d["candidate_columns"].get("time") and (
        (d["candidate_columns"].get("x") and d["candidate_columns"].get("y")) or
        (d["candidate_columns"].get("lat") and d["candidate_columns"].get("lon"))
    )]
    tags_found={}
    for tag in candidate_tags:
        tags_found[tag]=any(d.get("candidate_tag_row_counts",{}).get(tag,0)>0 for d in eligible)
    return {"tables":details,"trajectory_candidate_tables":[d["table"] for d in eligible],"candidate_tags_found":tags_found}

def inspect_csv(path):
    data=Path(path).read_bytes()
    txt=data.decode("utf-8-sig",errors="replace")
    rr=list(csv.DictReader(io.StringIO(txt)))
    return {"columns":list(rr[0].keys()) if rr else [],"row_count":len(rr),"rows":rr[:20]}

def main():
    payload={
      "schema_version":1,
      "study_id":"rousettus-social-seeding-raw-schema-preflight-v1",
      "classification":"Dryad retrieval + schema/tag/date presence only; no route similarity or self-vs-other geometry opened",
      "dryad_doi":"10.5061/dryad.51c59zwgp",
      "files":{},
      "route_geometry_opened":False,
    }
    all_sqlite=True
    for key,spec in FILES.items():
        got=download(spec,key)
        item={"file_id":spec["id"],"filename":spec["filename"],"retrieval":{k:v for k,v in got.items() if k!="path"}}
        if got["ok"]:
            if spec["kind"]=="sqlite":
                item["schema"]=inspect_sqlite(got["path"],spec["candidate_tags"])
                if not item["schema"]["trajectory_candidate_tables"]:
                    all_sqlite=False
            else:
                item["csv"]=inspect_csv(got["path"])
        else:
            if spec["kind"]=="sqlite": all_sqlite=False
        payload["files"][key]=item

    payload["all_three_sqlite_retrieved_and_structurally_identifiable"]=bool(all_sqlite and all(payload["files"][k]["retrieval"]["ok"] for k in ("june","july","december")))
    payload["may_open_xy_support_preflight"]=payload["all_three_sqlite_retrieved_and_structurally_identifiable"] and payload["files"]["trees"]["retrieval"]["ok"]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    lines=["# Rousettus raw-schema preflight v1","",
      "**DRYAD RETRIEVAL + SQLITE SCHEMA/TAG/DATE PRESENCE ONLY. No route geometry outcome opened.**","",
      "| source | retrieved | bytes | trajectory table(s) |",
      "|---|---|---:|---|"]
    for key,x in payload["files"].items():
        tabs=", ".join(x.get("schema",{}).get("trajectory_candidate_tables",[])) if "schema" in x else "CSV"
        lines.append(f"| {key} | {'yes' if x['retrieval']['ok'] else 'no'} | {x['retrieval'].get('bytes','')} | {tabs} |")
    lines += ["",f"May open x-y support preflight: **{payload['may_open_xy_support_preflight']}**",""]
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps({
      "retrieved":{k:v["retrieval"]["ok"] for k,v in payload["files"].items()},
      "trajectory_tables":{k:v.get("schema",{}).get("trajectory_candidate_tables",[]) for k,v in payload["files"].items() if "schema" in v},
      "tags_found":{k:v.get("schema",{}).get("candidate_tags_found",{}) for k,v in payload["files"].items() if "schema" in v},
      "may_open_xy_support_preflight":payload["may_open_xy_support_preflight"]
    },sort_keys=True))

if __name__=="__main__":
    main()
