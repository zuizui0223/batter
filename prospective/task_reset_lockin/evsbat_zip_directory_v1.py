#!/usr/bin/env python3
"""Range-only ZIP central-directory audit for evsBat rawdata.zip."""
from __future__ import annotations
import json, struct, urllib.request

URL="https://ndownloader.figshare.com/files/58421782"
SIZE=5_957_619_580
UA="batter-evsbat-zip-directory/1.0"
MAX_CD=64*1024*1024

def get_range(start,end):
    req=urllib.request.Request(URL,headers={"User-Agent":UA,"Range":f"bytes={start}-{end}","Accept":"application/octet-stream"})
    with urllib.request.urlopen(req,timeout=90) as r:
        status=getattr(r,"status",None);cr=r.headers.get("Content-Range");b=r.read(end-start+2)
    if status!=206 or not cr or len(b)!=end-start+1:
        raise RuntimeError(f"range failure status={status} cr={cr} n={len(b)} expected={end-start+1}")
    return b

def locate_cd():
    tail_n=min(131072,SIZE)
    start=SIZE-tail_n
    tail=get_range(start,SIZE-1)
    sig=b"PK\x05\x06"
    p=tail.rfind(sig)
    if p<0: raise RuntimeError("EOCD not found")
    e=tail[p:p+22]
    _,disk,cd_disk,n_disk,n_total,cd_size32,cd_off32,comment=struct.unpack("<4s4H2IH",e)
    if cd_size32!=0xffffffff and cd_off32!=0xffffffff and n_total!=0xffff:
        return int(cd_off32),int(cd_size32),int(n_total),False
    loc_sig=b"PK\x06\x07"
    lp=tail.rfind(loc_sig,0,p)
    if lp<0: raise RuntimeError("ZIP64 locator not found")
    loc=tail[lp:lp+20]
    _,disk64,off64,ndisk=struct.unpack("<4sIQI",loc)
    z=get_range(off64,off64+55)
    vals=struct.unpack("<4sQ2H2I4Q",z[:56])
    if vals[0]!=b"PK\x06\x06":raise RuntimeError("bad ZIP64 EOCD")
    _,sz,vm,vn,disk,cd_disk,n_disk64,n_total64,cd_size64,cd_off64=vals
    return int(cd_off64),int(cd_size64),int(n_total64),True

def parse_cd(b):
    pos=0; names=[]
    while pos+46<=len(b):
        if b[pos:pos+4]!=b"PK\x01\x02":
            # central directory may end before auxiliary records
            break
        fields=struct.unpack("<4s6H3I5H2I",b[pos:pos+46])
        flag=fields[3];fnl=fields[10];exl=fields[11];coml=fields[12]
        raw=b[pos+46:pos+46+fnl]
        enc="utf-8" if (flag & 0x800) else "cp437"
        name=raw.decode(enc,errors="replace")
        names.append(name)
        pos+=46+fnl+exl+coml
    return names

def main():
    off,sz,n,zip64=locate_cd()
    if sz<=0 or sz>MAX_CD:raise RuntimeError(f"central directory size disallowed: {sz}")
    cd=get_range(off,off+sz-1)
    names=parse_cd(cd)
    tops=sorted(set(x.split("/",1)[0] for x in names if x))
    relevant=[x for x in names if any(k in x.lower() for k in [
        "rhin","nippon","kiku","bat","weight","mass","subject","individual","metadata","meta","csv"
    ])]
    out={
      "contract":"EVSBAT_ZIP_DIRECTORY_AMENDMENT_V1.md",
      "file_contents_opened":False,
      "zip64":zip64,
      "declared_entry_count":n,
      "parsed_entry_count":len(names),
      "top_level_names":tops,
      "relevant_path_names":relevant,
      "all_path_names":names,
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
