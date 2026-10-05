#!/usr/bin/env python3
"""Central-directory metadata for evsBat R. nippon tracking pickle members only."""
from __future__ import annotations
import json,re,struct,urllib.request

URL="https://ndownloader.figshare.com/files/58421782"
SIZE=5_957_619_580
UA="batter-evsbat-external-policy-member-metadata/1.0"
MAX_CD=64*1024*1024
IDS={"2670","2681","2860","2868","2899"}
PAT=re.compile(r"^rawdata/chamber/event_camera/R_nippon/particle_tracking_results_kiku_(2670|2681|2860|2868|2899)_.+\.pkl$")

def get_range(start,end):
    req=urllib.request.Request(URL,headers={"User-Agent":UA,"Range":f"bytes={start}-{end}","Accept":"application/octet-stream"})
    with urllib.request.urlopen(req,timeout=90) as r:
        status=getattr(r,"status",None);cr=r.headers.get("Content-Range");b=r.read(end-start+2)
    if status!=206 or not cr or len(b)!=end-start+1:
        raise RuntimeError(f"range failure status={status} cr={cr} got={len(b)} expected={end-start+1}")
    return b

def locate_cd():
    tail_n=min(131072,SIZE)
    start=SIZE-tail_n
    tail=get_range(start,SIZE-1)
    p=tail.rfind(b"PK\x05\x06")
    if p<0:raise RuntimeError("EOCD not found")
    e=tail[p:p+22]
    _,disk,cd_disk,n_disk,n_total,cd_size32,cd_off32,comment=struct.unpack("<4s4H2IH",e)
    if cd_size32!=0xffffffff and cd_off32!=0xffffffff and n_total!=0xffff:
        return int(cd_off32),int(cd_size32),int(n_total)
    lp=tail.rfind(b"PK\x06\x07",0,p)
    if lp<0:raise RuntimeError("ZIP64 locator not found")
    _,disk64,off64,ndisk=struct.unpack("<4sIQI",tail[lp:lp+20])
    z=get_range(off64,off64+55)
    vals=struct.unpack("<4sQ2H2I4Q",z[:56])
    if vals[0]!=b"PK\x06\x06":raise RuntimeError("bad ZIP64 EOCD")
    return int(vals[-1]),int(vals[-2]),int(vals[-3])

def parse_zip64_extra(extra,need_usize,need_csize,need_off):
    pos=0; payload=None
    while pos+4<=len(extra):
        hid,sz=struct.unpack("<HH",extra[pos:pos+4]);data=extra[pos+4:pos+4+sz]
        if hid==0x0001:
            payload=data;break
        pos+=4+sz
    if payload is None:
        if need_usize or need_csize or need_off:raise RuntimeError("missing ZIP64 extra")
        return None,None,None
    pos=0;u=c=o=None
    if need_usize:
        u=struct.unpack("<Q",payload[pos:pos+8])[0];pos+=8
    if need_csize:
        c=struct.unpack("<Q",payload[pos:pos+8])[0];pos+=8
    if need_off:
        o=struct.unpack("<Q",payload[pos:pos+8])[0];pos+=8
    return u,c,o

def parse_cd(b):
    pos=0;out=[]
    while pos+46<=len(b):
        if b[pos:pos+4]!=b"PK\x01\x02":break
        f=struct.unpack("<4s6H3I5H2I",b[pos:pos+46])
        flag=f[3];method=f[4];crc=f[7];csize=f[8];usize=f[9]
        fnl=f[10];exl=f[11];coml=f[12];off=f[16]
        raw=b[pos+46:pos+46+fnl]
        extra=b[pos+46+fnl:pos+46+fnl+exl]
        enc="utf-8" if flag&0x800 else "cp437"
        name=raw.decode(enc,errors="replace")
        if PAT.match(name):
            zu,zc,zo=parse_zip64_extra(extra,usize==0xffffffff,csize==0xffffffff,off==0xffffffff)
            if zu is not None:usize=zu
            if zc is not None:csize=zc
            if zo is not None:off=zo
            ident=PAT.match(name).group(1)
            out.append({"path":name,"individual_id":ident,"compression_method":int(method),
                        "crc32":f"{crc:08x}","compressed_size":int(csize),
                        "uncompressed_size":int(usize),"local_header_offset":int(off)})
        pos+=46+fnl+exl+coml
    return out

def main():
    off,sz,n=locate_cd()
    if not (0<sz<=MAX_CD):raise RuntimeError(f"bad central-directory size {sz}")
    rows=parse_cd(get_range(off,off+sz-1))
    counts={}
    for i in sorted(IDS):counts[i]=sum(r["individual_id"]==i for r in rows)
    smallest=min(rows,key=lambda r:(r["uncompressed_size"],r["path"])) if rows else None
    out={"contract":"EVSBAT_EXTERNAL_POLICY_PREFLIGHT_V1.md","payloads_opened":False,
         "declared_zip_entries":n,"candidate_member_count":len(rows),
         "counts_by_individual":counts,"smallest_candidate":smallest,
         "candidate_members":rows}
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
