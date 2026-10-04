#!/usr/bin/env python3
"""Strict string-only metadata probe of the first 8 MiB of Figshare pickle files."""
from __future__ import annotations
import json,re,urllib.request

FILES={
 "kiku":{"id":55033988,"url":"https://ndownloader.figshare.com/files/55033988"},
 "yubi":{"id":55033991,"url":"https://ndownloader.figshare.com/files/55033991"},
}
UA="batter-task-reset-pickle-string-metadata/1.0"
N=8*1024*1024

PATTERNS=[
 re.compile(rb"Env[0-9]+_Bat[A-Za-z]+_no[^\x00\r\n ,;]{1,80}(?:\.csv)?"),
 re.compile(rb"Env[0-9]+"),
 re.compile(rb"Bat[A-Za-z]+"),
]
LITERALS=[b"kiku",b"yubi",b"Rhinolophus",b"Miniopterus",b"species",b"environment",b"trial",b"filename"]

def get_prefix(url):
 req=urllib.request.Request(url,headers={"User-Agent":UA,"Range":f"bytes=0-{N-1}","Accept":"application/octet-stream"})
 with urllib.request.urlopen(req,timeout=90) as r:
  status=getattr(r,"status",None); cr=r.headers.get("Content-Range"); data=r.read(N)
 if status!=206 or not cr:
  raise RuntimeError(f"range not honored: status={status} content-range={cr}")
 return data

def main():
 out={"contract":"PICKLE_STRING_METADATA_AMENDMENT_V1.md","numeric_arrays_decoded":False,"pickle_executed":False,"files":{}}
 for label,spec in FILES.items():
  b=get_prefix(spec["url"])
  tokens=set()
  for pat in PATTERNS:
   for m in pat.finditer(b):
    try:tokens.add(m.group(0).decode("utf-8","strict"))
    except Exception:pass
  for lit in LITERALS:
   start=0
   while True:
    i=b.find(lit,start)
    if i<0:break
    tokens.add(lit.decode())
    start=i+1
  out["files"][label]={"file_id":spec["id"],"prefix_bytes":len(b),"whitelisted_tokens":sorted(tokens)}
 print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
