#!/usr/bin/env python3
from __future__ import annotations

import hashlib, json, os, re, sqlite3, tempfile, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"prospective/rousettus_social_seeding/sqlite_schema_preflight_v1.json"
OUT_MD=ROOT/"prospective/rousettus_social_seeding/SQLITE_SCHEMA_PREFLIGHT_RESULT_V1.md"

FILES={
  "june":{"url":"https://datadryad.org/downloads/file_stream/3182077","file_stream_id":3182077,"display_size":"121.79 MB"},
  "july":{"url":"https://datadryad.org/downloads/file_stream/3182078","file_stream_id":3182078,"display_size":"115.77 MB"},
  "december":{"url":"https://datadryad.org/downloads/file_stream/3182076","file_stream_id":3182076,"display_size":"47.51 MB"},
}
CANDIDATES={
  "june":["6399","6411","6414","6428","6635"],  # 6641 excluded as source-coded pup
  "july":["6640"],
  "december":["6824","6991","6993"],
}
TAG_TOKENS=("tag","animal","bat","individual")
TIME_TOKENS=("time","timestamp","date","datetime")
ROOST_TOKENS=("roost","cave","colony","site")
COORD_TOKENS=("lon","lat","x","y","east","north","utm","coord","location")

def q(name:str)->str:
    return '"' + name.replace('"','""') + '"'

def download(url:str,path:Path):
    req=urllib.request.Request(url,headers={"User-Agent":"batter-rousettus-sqlite-schema-preflight-v1/1.0"})
    h=hashlib.sha256()
    n=0
    with urllib.request.urlopen(req,timeout=300) as r, path.open("wb") as f:
        final_url=r.geturl()
        content_type=r.headers.get("Content-Type")
        content_length=r.headers.get("Content-Length")
        while True:
            b=r.read(1024*1024)
            if not b: break
            f.write(b); h.update(b); n+=len(b)
    return {"bytes":n,"sha256":h.hexdigest(),"final_url":final_url,
            "content_type":content_type,"content_length_header":content_length}

def table_info(con,table):
    return [{"cid":r[0],"name":r[1],"type":r[2],"notnull":r[3],"default":r[4],"pk":r[5]}
            for r in con.execute(f"PRAGMA table_info({q(table)})")]

def token_cols(cols,tokens):
    return [c["name"] for c in cols if any(t in c["name"].lower() for t in tokens)]

def scalar(con,sql,params=()):
    try:
        r=con.execute(sql,params).fetchone()
        return None if r is None else r[0]
    except Exception:
        return None

def candidate_coverage(con,table,tag_col,time_cols,candidates):
    out={}
    for tag in candidates:
        cnt=scalar(con,f"SELECT COUNT(*) FROM {q(table)} WHERE CAST({q(tag_col)} AS TEXT)=?",(tag,))
        if not cnt: continue
        rec={"rows":int(cnt)}
        for tc in time_cols[:4]:
            mn=scalar(con,f"SELECT MIN({q(tc)}) FROM {q(table)} WHERE CAST({q(tag_col)} AS TEXT)=?",(tag,))
            mx=scalar(con,f"SELECT MAX({q(tc)}) FROM {q(table)} WHERE CAST({q(tag_col)} AS TEXT)=?",(tag,))
            rec.setdefault("time_fields",{})[tc]={"min":None if mn is None else str(mn),"max":None if mx is None else str(mx)}
        out[tag]=rec
    return out

def inspect_db(path:Path,campaign:str,dl):
    with path.open("rb") as f:
        header=f.read(16)
    if header!=b"SQLite format 3\x00":
        return {"download":dl,"sqlite_header_ok":False,"decision":"NOT_SQLITE"}

    con=sqlite3.connect(f"file:{path}?mode=ro",uri=True)
    try:
        tables=[r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        views=[r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")]
        schemas={}
        plausible=[]
        candidate_hits={}
        for t in tables:
            cols=table_info(con,t)
            names=[c["name"] for c in cols]
            tag_cols=token_cols(cols,TAG_TOKENS)
            time_cols=token_cols(cols,TIME_TOKENS)
            roost_cols=token_cols(cols,ROOST_TOKENS)
            coord_cols=token_cols(cols,COORD_TOKENS)
            schemas[t]={
              "columns":cols,
              "tag_like_columns":tag_cols,
              "time_like_columns":time_cols,
              "roost_like_columns":roost_cols,
              "coordinate_like_columns":coord_cols,
            }
            if tag_cols and time_cols:
                plausible.append(t)
                best={}
                for tcand in tag_cols[:6]:
                    cov=candidate_coverage(con,t,tcand,time_cols,CANDIDATES[campaign])
                    if len(cov)>len(best):
                        best=cov
                        best_tag=tcand
                if best:
                    candidate_hits[t]={"tag_column":best_tag,"candidate_coverage":best}
        pragmas={
          "user_version":scalar(con,"PRAGMA user_version"),
          "application_id":scalar(con,"PRAGMA application_id"),
          "page_count":scalar(con,"PRAGMA page_count"),
          "page_size":scalar(con,"PRAGMA page_size"),
        }
        return {
          "download":dl,"sqlite_header_ok":True,
          "tables":tables,"views":views,"schemas":schemas,
          "plausible_tag_time_tables":plausible,
          "candidate_hits":candidate_hits,
          "pragmas":pragmas,
        }
    finally:
        con.close()

def main():
    payload={
      "schema_version":1,
      "study_id":"rousettus-social-seeding-sqlite-schema-preflight-v1",
      "classification":"raw-file identity + SQLite schema + tag/time coverage only; coordinate numeric values unopened",
      "route_geometry_opened":False,
      "coordinate_numeric_values_opened":False,
      "campaigns":{},
    }
    retrieval_ok=True
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        for campaign,spec in FILES.items():
            path=td/f"{campaign}.sqlite"
            try:
                dl=download(spec["url"],path)
                res=inspect_db(path,campaign,dl)
            except Exception as e:
                retrieval_ok=False
                res={"retrieval_error":f"{type(e).__name__}: {e}"}
            payload["campaigns"][campaign]={**spec,**res}

    # Require all three SQLite files and at least one candidate hit in each campaign
    gate={}
    for campaign,x in payload["campaigns"].items():
        hits=set()
        for tbl,v in x.get("candidate_hits",{}).items():
            hits.update(v.get("candidate_coverage",{}).keys())
        gate[campaign]={
          "sqlite_ok":bool(x.get("sqlite_header_ok")),
          "candidate_ids_expected":CANDIDATES[campaign],
          "candidate_ids_seen":sorted(hits),
          "all_expected_candidates_seen":set(CANDIDATES[campaign]).issubset(hits),
          "tag_time_table_exists":bool(x.get("plausible_tag_time_tables")),
        }
    payload["gate"]=gate
    payload["schema_preflight_pass"]=all(
      g["sqlite_ok"] and g["all_expected_candidates_seen"] and g["tag_time_table_exists"]
      for g in gate.values()
    )
    payload["next_step"]="x-y structural support preflight only" if payload["schema_preflight_pass"] else "STOP before coordinate opening"

    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    lines=["# Rousettus SQLite schema preflight v1","",
      "**RAW FILE IDENTITY + SQLITE SCHEMA + TAG/TIME COVERAGE ONLY. Coordinate numeric values and route geometry remain unopened.**","",
      "| campaign | sqlite | tag/time table | expected candidate IDs seen | gate |",
      "|---|---|---|---|---|"]
    for c,g in gate.items():
        lines.append(f"| {c} | {'yes' if g['sqlite_ok'] else 'no'} | {'yes' if g['tag_time_table_exists'] else 'no'} | {len(g['candidate_ids_seen'])}/{len(g['candidate_ids_expected'])} | {'PASS' if all([g['sqlite_ok'],g['tag_time_table_exists'],g['all_expected_candidates_seen']]) else 'FAIL'} |")
    lines += ["",f"Schema preflight: **{'PASS' if payload['schema_preflight_pass'] else 'FAIL'}**",
              f"Next step: **{payload['next_step']}**",""]
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps({"pass":payload["schema_preflight_pass"],"gate":gate,"next_step":payload["next_step"]},sort_keys=True))

if __name__=="__main__":
    main()
