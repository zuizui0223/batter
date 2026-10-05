#!/usr/bin/env python3
"""Static structural-string inventory for one frozen evsBat pickle."""
from __future__ import annotations
import binascii,collections,json,pickletools,string,struct,urllib.request,zlib

URL="https://ndownloader.figshare.com/files/58421782"
UA="batter-evsbat-pickle-structural-strings/2.0"
OFFSET=34_165_152
CSIZE=101_716
USIZE=461_730
CRC="34bb9458"
PATH="rawdata/chamber/event_camera/R_nippon/particle_tracking_results_kiku_2868_17-3_particle1_lower.pkl"

def get_range(start,end):
    req=urllib.request.Request(URL,headers={"User-Agent":UA,"Range":f"bytes={start}-{end}","Accept":"application/octet-stream"})
    with urllib.request.urlopen(req,timeout=90) as r:
        status=getattr(r,"status",None);cr=r.headers.get("Content-Range");b=r.read(end-start+2)
    if status!=206 or not cr or len(b)!=end-start+1:
        raise RuntimeError(f"range failure {status} {cr} {len(b)}")
    return b

def extract():
    h=get_range(OFFSET,OFFSET+29)
    f=struct.unpack("<4s5H3I2H",h)
    if f[0]!=b"PK\x03\x04":raise RuntimeError("bad local header")
    method=f[3];fnl=f[9];exl=f[10]
    name=get_range(OFFSET+30,OFFSET+30+fnl-1).decode("utf-8",errors="replace")
    if name!=PATH:raise RuntimeError(f"path mismatch {name}")
    start=OFFSET+30+fnl+exl
    comp=get_range(start,start+CSIZE-1)
    raw=zlib.decompress(comp,-15) if method==8 else comp
    if len(raw)!=USIZE:raise RuntimeError(f"usize mismatch {len(raw)}")
    got=f"{binascii.crc32(raw)&0xffffffff:08x}"
    if got!=CRC:raise RuntimeError(f"crc mismatch {got}")
    return raw

def printable_short(s):
    return isinstance(s,str) and len(s)<=120 and all(ch in string.printable for ch in s)

def main():
    raw=extract()
    cnt=collections.Counter()
    events=[]
    for op,arg,pos in pickletools.genops(raw):
        if printable_short(arg):
            cnt[arg]+=1
            if len(events)<200:
                events.append({"opcode":op.name,"string":arg})
    out={
      "contract":"EVSBAT_PICKLE_STRUCTURAL_STRINGS_AMENDMENT_V2.md",
      "pickle_executed":False,
      "numeric_values_reported":False,
      "member":{"path":PATH,"uncompressed_bytes":len(raw),"crc32":CRC},
      "unique_string_count":len(cnt),
      "strings":[{"string":s,"count":n} for s,n in sorted(cnt.items())],
      "first_200_string_events":events,
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
