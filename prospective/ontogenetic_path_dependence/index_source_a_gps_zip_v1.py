#!/usr/bin/env python3
"""Read only the central directory of Source A GPS data.zip via HTTP Range.

Contract: SOURCE_A_GPS_ARCHIVE_INDEX_AMENDMENT_V1.md
No archive member payload is downloaded or decompressed.
"""
from __future__ import annotations
import json, re, struct, urllib.request, zlib

BASE="https://data.mendeley.com/public-api"
DS="gpcg9m5758"
FID="8bb38dce-f2d5-41b1-bb0e-8454957e8eee"
SIZE=1546850907
MAX_TOTAL=16*1024*1024
UA="batter-source-a-zip-index/1.0"
downloaded=0

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.mendeley-public-dataset.1+json"})
    with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)

def get_range(url,start,end):
    global downloaded
    if start<0 or end<start or end>=SIZE: raise RuntimeError("invalid range")
    n=end-start+1
    if downloaded+n>MAX_TOTAL: raise RuntimeError("range budget exceeded")
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*","Range":f"bytes={start}-{end}"})
    with urllib.request.urlopen(req,timeout=60) as r:
        status=getattr(r,"status",None)
        cr=r.headers.get("Content-Range")
        data=r.read(n+1)
    if len(data)!=n: raise RuntimeError(f"range length mismatch requested={n} got={len(data)} status={status} content-range={cr}")
    downloaded+=len(data)
    return data,{"status":status,"content_range":cr}

def zip64_values(extra,need_uncomp,need_comp,need_off):
    p=0
    z=None
    while p+4<=len(extra):
        tag,ln=struct.unpack_from("<HH",extra,p); p+=4
        dat=extra[p:p+ln]; p+=ln
        if tag==0x0001: z=dat; break
    if z is None:return None,None,None
    q=0
    def take():
        nonlocal q
        if q+8>len(z):raise RuntimeError("truncated zip64 extra")
        v=struct.unpack_from("<Q",z,q)[0];q+=8;return v
    u=take() if need_uncomp else None
    c=take() if need_comp else None
    o=take() if need_off else None
    return u,c,o

def main():
    meta=get_json(f"{BASE}/datasets/{DS}/files/{FID}")
    cdmeta=meta.get("content_details") or {}
    url=cdmeta.get("download_url")
    if not url: raise RuntimeError("no download URL in public file metadata")

    tail_n=min(1024*1024,SIZE)
    tail,range_meta=get_range(url,SIZE-tail_n,SIZE-1)
    eocd_pos=tail.rfind(b"PK\x05\x06")
    if eocd_pos<0: raise RuntimeError("EOCD not found in final 1 MiB")
    if eocd_pos+22>len(tail): raise RuntimeError("truncated EOCD")
    _,disk,cd_disk,n_disk,n_total,cd_size,cd_off,comment_len=struct.unpack_from("<4s4H2IH",tail,eocd_pos)

    zip64=False
    if cd_size==0xffffffff or cd_off==0xffffffff or n_total==0xffff:
        zip64=True
        abs_eocd=SIZE-tail_n+eocd_pos
        loc_abs=abs_eocd-20
        if loc_abs>=SIZE-tail_n:
            locator=tail[loc_abs-(SIZE-tail_n):loc_abs-(SIZE-tail_n)+20]
        else:
            locator,_=get_range(url,loc_abs,loc_abs+19)
        if locator[:4]!=b"PK\x06\x07": raise RuntimeError("ZIP64 locator missing")
        _,disk_start,z64_off,total_disks=struct.unpack("<4sIQI",locator)
        z64,_=get_range(url,z64_off,min(SIZE-1,z64_off+56-1))
        if z64[:4]!=b"PK\x06\x06": raise RuntimeError("ZIP64 EOCD missing")
        vals=struct.unpack_from("<4sQ2H2I4Q",z64,0)
        n_total=vals[7]; cd_size=vals[8]; cd_off=vals[9]

    if cd_size>MAX_TOTAL-downloaded:
        raise RuntimeError(f"central directory {cd_size} bytes exceeds remaining audit budget")
    cd,cd_range_meta=get_range(url,cd_off,cd_off+cd_size-1)

    members=[]
    p=0
    while p<len(cd):
        if cd[p:p+4]!=b"PK\x01\x02":
            raise RuntimeError(f"central directory signature mismatch at {p}")
        fields=struct.unpack_from("<4s6H3I5H2I",cd,p)
        method=fields[4]; crc=fields[7]; comp=fields[8]; uncomp=fields[9]
        fnl,exl,col=fields[10],fields[11],fields[12]
        off=fields[16]
        name_b=cd[p+46:p+46+fnl]
        extra=cd[p+46+fnl:p+46+fnl+exl]
        try:name=name_b.decode("utf-8")
        except UnicodeDecodeError:name=name_b.decode("cp437",errors="replace")
        zu,zc,zo=zip64_values(extra,uncomp==0xffffffff,comp==0xffffffff,off==0xffffffff)
        if zu is not None:uncomp=zu
        if zc is not None:comp=zc
        if zo is not None:off=zo
        members.append({"name":name,"compressed_size":comp,"uncompressed_size":uncomp,"method":method,"crc32":f"{crc:08x}","local_header_offset":off})
        p+=46+fnl+exl+col

    structural=[]
    pair_roots=set()
    for m in members:
        n=m["name"]
        low=n.lower()
        if any(k in low for k in ["allpairs","datainfo_mompup","trees_mompup"]) or (low.endswith(".xlsx") and "pair" in low):
            structural.append(m)
        parts=n.split("/")
        if len(parts)>=2 and re.search(r"pair",parts[0],re.I):
            pair_roots.add(parts[0])
        elif len(parts)>=3 and re.search(r"pair",parts[1],re.I):
            pair_roots.add(parts[1])

    mom_count=sum(1 for m in members if "/mom/" in ("/"+m["name"].lower()))
    pup_count=sum(1 for m in members if "/pup/" in ("/"+m["name"].lower()))
    out={
      "contract":"SOURCE_A_GPS_ARCHIVE_INDEX_AMENDMENT_V1.md",
      "archive_payload_opened":False,
      "published_archive_size":SIZE,
      "bytes_downloaded_for_index":downloaded,
      "range_probe":range_meta,
      "central_directory_range":cd_range_meta,
      "zip64":zip64,
      "member_count":len(members),
      "pair_root_count":len(pair_roots),
      "pair_roots":sorted(pair_roots),
      "mom_member_count":mom_count,
      "pup_member_count":pup_count,
      "structural_members":structural,
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
