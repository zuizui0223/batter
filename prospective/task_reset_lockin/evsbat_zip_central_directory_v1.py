#!/usr/bin/env python3
"""Read only ZIP central-directory metadata from evsBat rawdata.zip."""
from __future__ import annotations
import json, struct, urllib.request

URL="https://ndownloader.figshare.com/files/58421782"
SIZE=5957619580
UA="batter-evsbat-zip-central-dir/1.0"

def rng(start,end):
    req=urllib.request.Request(URL,headers={"User-Agent":UA,"Range":f"bytes={start}-{end}","Accept":"application/octet-stream"})
    with urllib.request.urlopen(req,timeout=90) as r:
        status=getattr(r,"status",None); cr=r.headers.get("Content-Range"); b=r.read(end-start+2)
    if status!=206 or not cr or len(b)!=end-start+1:
        raise RuntimeError(f"range failure {start}-{end}: status={status} cr={cr} len={len(b)}")
    return b

def u16(b,o): return struct.unpack_from("<H",b,o)[0]
def u32(b,o): return struct.unpack_from("<I",b,o)[0]
def u64(b,o): return struct.unpack_from("<Q",b,o)[0]

def main():
    tail_n=min(131072,SIZE)
    tail_start=SIZE-tail_n
    tail=rng(tail_start,SIZE-1)
    sig=b"PK\x05\x06"
    p=tail.rfind(sig)
    if p<0: raise RuntimeError("EOCD not found")
    eocd_abs=tail_start+p
    entries=u16(tail,p+10)
    cd_size=u32(tail,p+12)
    cd_off=u32(tail,p+16)

    zip64=False
    if entries==0xFFFF or cd_size==0xFFFFFFFF or cd_off==0xFFFFFFFF:
        zip64=True
        # ZIP64 locator should immediately precede EOCD.
        loc_sig=b"PK\x06\x07"
        lp=tail.rfind(loc_sig,0,p)
        if lp<0: raise RuntimeError("ZIP64 locator not found")
        z64_off=u64(tail,lp+8)
        z64=rng(z64_off,z64_off+55)
        if z64[:4]!=b"PK\x06\x06": raise RuntimeError("ZIP64 EOCD sig mismatch")
        entries=u64(z64,32)
        cd_size=u64(z64,40)
        cd_off=u64(z64,48)

    if cd_size>100_000_000: raise RuntimeError(f"central directory unexpectedly large {cd_size}")
    cd=rng(cd_off,cd_off+cd_size-1)
    members=[]; o=0
    while o<len(cd):
        if cd[o:o+4]!=b"PK\x01\x02":
            raise RuntimeError(f"central header mismatch at {o}")
        method=u16(cd,o+10)
        crc=u32(cd,o+16)
        csize=u32(cd,o+20); usize=u32(cd,o+24)
        fnl=u16(cd,o+28); exl=u16(cd,o+30); cml=u16(cd,o+32)
        nameb=cd[o+46:o+46+fnl]
        name=nameb.decode("utf-8",errors="replace")
        extra=cd[o+46+fnl:o+46+fnl+exl]
        # Resolve ZIP64 sizes when 32-bit sentinels appear, using central metadata only.
        if csize==0xFFFFFFFF or usize==0xFFFFFFFF:
            q=0
            while q+4<=len(extra):
                hid,sz=struct.unpack_from("<HH",extra,q); q+=4
                data=extra[q:q+sz]; q+=sz
                if hid==1:
                    z=0
                    if usize==0xFFFFFFFF:
                        usize=struct.unpack_from("<Q",data,z)[0]; z+=8
                    if csize==0xFFFFFFFF:
                        csize=struct.unpack_from("<Q",data,z)[0]; z+=8
                    break
        members.append({
          "name":name,"compressed_size":int(csize),"uncompressed_size":int(usize),
          "compression_method":int(method),"crc32":f"{crc:08x}",
          "is_directory":name.endswith("/")
        })
        o+=46+fnl+exl+cml

    if o!=len(cd): raise RuntimeError(f"central directory parse end {o}!={len(cd)}")
    out={
      "contract":"EVSBAT_ZIP_CENTRAL_DIRECTORY_AMENDMENT_V1.md",
      "archive_member_contents_opened":False,
      "zip64":zip64,
      "entry_count_declared":int(entries),
      "entry_count_parsed":len(members),
      "central_directory_offset":int(cd_off),
      "central_directory_size":int(cd_size),
      "members":members,
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
