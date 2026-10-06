#!/usr/bin/env python3
from __future__ import annotations
import json,re,urllib.request

FILES={
 "kiku":{"id":55033988,"url":"https://ndownloader.figshare.com/files/55033988"},
 "yubi":{"id":55033991,"url":"https://ndownloader.figshare.com/files/55033991"},
}
UA="batter-obstacle-key-probe/1.0"
N=16*1024*1024
WORDS=[
 "obstacle","obstacles","wall","walls","arena","environment","env","layout","geometry",
 "position","positions","coordinate","coordinates","center","centers","centre","centres",
 "radius","diameter","width","height","x","y","z","start","goal","target"
]
PAT_ENV=re.compile(rb"Env[0-9]+")
# Require token boundaries; single-letter x/y/z must be null/pickle-delimited or word-delimited.
PAT_WORDS={w:re.compile(rb"(?i)(?<![A-Za-z0-9_])"+re.escape(w.encode())+rb"(?![A-Za-z0-9_])") for w in WORDS}

def get_prefix(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Range":f"bytes=0-{N-1}","Accept":"application/octet-stream"})
    with urllib.request.urlopen(req,timeout=90) as r:
        status=getattr(r,"status",None);cr=r.headers.get("Content-Range");b=r.read(N)
    if status!=206 or not cr:raise RuntimeError(f"range not honored status={status} cr={cr}")
    return b

def main():
    out={"contract":"PICKLE_OBSTACLE_GEOMETRY_KEY_PROBE_V1.md",
         "pickle_executed":False,"numeric_payload_decoded":False,"files":{}}
    any_geom=False
    for label,spec in FILES.items():
        b=get_prefix(spec["url"])
        hits={}
        for w,pat in PAT_WORDS.items():
            n=len(list(pat.finditer(b)))
            if n:hits[w]=n
        envs=sorted(set(m.group(0).decode() for m in PAT_ENV.finditer(b)))
        geom=[w for w in hits if w in {
          "obstacle","obstacles","wall","walls","arena","layout","geometry","position","positions",
          "coordinate","coordinates","center","centers","centre","centres","radius","diameter","width","height"
        }]
        if geom:any_geom=True
        out["files"][label]={"file_id":spec["id"],"prefix_bytes":len(b),
                             "structural_token_counts":hits,"environment_tokens":envs,
                             "geometry_key_candidates":geom}
    out["verdict"]="GEOMETRY_SCHEMA_CANDIDATE_PRESENT" if any_geom else "STOP_NO_PUBLIC_OBSTACLE_GEOMETRY_SCHEMA"
    print(json.dumps(out,indent=2))

if __name__=="__main__":main()
