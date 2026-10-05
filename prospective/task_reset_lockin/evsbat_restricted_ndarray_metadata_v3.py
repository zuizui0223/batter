#!/usr/bin/env python3
"""Restricted NumPy-only metadata load for one frozen evsBat tracking pickle."""
from __future__ import annotations
import binascii,io,json,pickle,struct,urllib.request,zlib
import numpy as np

URL="https://ndownloader.figshare.com/files/58421782"
UA="batter-evsbat-restricted-ndarray-metadata/3.0"
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

class RestrictedNumpyUnpickler(pickle.Unpickler):
    def find_class(self,module,name):
        allowed={
          ("numpy.core.multiarray","_reconstruct"):np.core.multiarray._reconstruct,
          ("numpy","ndarray"):np.ndarray,
          ("numpy","dtype"):np.dtype,
        }
        key=(module,name)
        if key not in allowed:
            raise pickle.UnpicklingError(f"forbidden global {module}.{name}")
        return allowed[key]

def main():
    raw=extract()
    obj=RestrictedNumpyUnpickler(io.BytesIO(raw)).load()
    if not isinstance(obj,np.ndarray):
        raise RuntimeError(f"top-level object is not ndarray: {type(obj)!r}")
    out={
      "contract":"EVSBAT_RESTRICTED_NDARRAY_METADATA_AMENDMENT_V3.md",
      "restricted_globals_only":True,
      "numeric_values_reported":False,
      "top_level_type":"numpy.ndarray",
      "ndim":int(obj.ndim),
      "shape":[int(x) for x in obj.shape],
      "dtype":str(obj.dtype),
      "size":int(obj.size),
      "c_contiguous":bool(obj.flags.c_contiguous),
      "f_contiguous":bool(obj.flags.f_contiguous),
      "floating_dtype":bool(np.issubdtype(obj.dtype,np.floating)),
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
