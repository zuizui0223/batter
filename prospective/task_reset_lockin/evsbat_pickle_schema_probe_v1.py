#!/usr/bin/env python3
"""Static pickle schema probe for one frozen evsBat R. nippon tracking member."""
from __future__ import annotations
import binascii,json,pickletools,re,struct,urllib.request,zlib

URL="https://ndownloader.figshare.com/files/58421782"
UA="batter-evsbat-pickle-schema-probe/1.0"
OFFSET=34_165_152
CSIZE=101_716
USIZE=461_730
CRC="34bb9458"
PATH="rawdata/chamber/event_camera/R_nippon/particle_tracking_results_kiku_2868_17-3_particle1_lower.pkl"

KEYWORDS=re.compile(r"(?:^|[_\s])(time|timestamp|frame|x|y|z|position|coordinate|track|trajectory|velocity|particle|points|xyz|centroid)(?:$|[_\s])",re.I)

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
    nameb=get_range(OFFSET+30,OFFSET+30+fnl-1)
    name=nameb.decode("utf-8",errors="replace")
    if name!=PATH:raise RuntimeError(f"path mismatch {name}")
    start=OFFSET+30+fnl+exl
    comp=get_range(start,start+CSIZE-1)
    if method!=8:raise RuntimeError(f"unexpected method {method}")
    raw=zlib.decompress(comp,-15)
    if len(raw)!=USIZE:raise RuntimeError(f"usize mismatch {len(raw)}")
    got=f"{binascii.crc32(raw)&0xffffffff:08x}"
    if got!=CRC:raise RuntimeError(f"crc mismatch {got}")
    return raw

def main():
    raw=extract()
    strings=set();globals_=set();opnames=set();protocols=[]
    for op,arg,pos in pickletools.genops(raw):
        opnames.add(op.name)
        if op.name=="PROTO":
            protocols.append(arg)
        if op.name=="GLOBAL" and isinstance(arg,str):
            globals_.add(arg)
        if isinstance(arg,str) and len(arg)<=200 and KEYWORDS.search(arg):
            strings.add(arg)
    out={
      "contract":"EVSBAT_PICKLE_SCHEMA_PROBE_AMENDMENT_V1.md",
      "pickle_executed":False,
      "numeric_values_reported":False,
      "member":{"path":PATH,"uncompressed_bytes":len(raw),"crc32":CRC},
      "protocol_values":protocols,
      "opcode_names":sorted(opnames),
      "global_opcode_arguments":sorted(globals_),
      "structural_keyword_strings":sorted(strings),
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
