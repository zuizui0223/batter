#!/usr/bin/env python3
"""Central-directory-only inventory for source-declared reversible sensory ZIP."""
from __future__ import annotations
import io,json,re,urllib.error,urllib.request,zipfile,time

URL="https://www.dropbox.com/sh/met5cvcq9nmvxdd/AAAF4saT9FZl01FwWyRgD1pqa?dl=1"
UA="batter-reversible-sensory-archive/1.0"
MAX_BYTES=2_500_000

def op(req,timeout=90):
    last=None
    for a in range(5):
        try:return urllib.request.urlopen(req,timeout=timeout)
        except urllib.error.HTTPError as e:
            last=e
            if e.code not in (429,500,502,503,504):raise
        except urllib.error.URLError as e:last=e
        if a<4:time.sleep(2**a)
    raise last

def fetch_zip():
    req=urllib.request.Request(URL,headers={"User-Agent":UA,"Accept":"application/zip,*/*"})
    with op(req) as r:
        b=r.read(MAX_BYTES+1)
    if len(b)>MAX_BYTES:raise RuntimeError("archive exceeds frozen byte budget")
    return b

def classify(name):
    q=name.lower()
    if any(x in q for x in ["track","trajectory","traj","flight","position","xyz","3d","motion"]):
        return "MOVEMENT_PLAUSIBLE"
    if any(x in q for x in ["call","audio","acoustic","echo","sonar","sound","wav"]):
        return "ACOUSTIC_PLAUSIBLE"
    if any(q.endswith(x) for x in [".m",".py",".txt",".md",".doc",".docx",".pdf"]) or any(x in q for x in ["readme","metadata","info","code"]):
        return "METADATA_OR_CODE"
    return "UNKNOWN"

def hints(name):
    q=name.lower()
    bats=sorted(set(re.findall(r"(?:bat[_\- ]?|b)([1-9][0-9]*)",q)))
    cond=[x for x in ["baseline","control","nomask","no_mask","mask","30cm","10cm","foam","styrofoam"] if x in q]
    nums=re.findall(r"(?<![a-z])([0-9]{1,4})(?![a-z])",q)
    return {"bat_tokens":bats,"condition_tokens":cond,"numeric_tokens":nums[:20]}

def main():
    b=fetch_zip()
    z=zipfile.ZipFile(io.BytesIO(b))
    rows=[]
    for x in z.infolist():
        rows.append({
          "name":x.filename,
          "compressed_size":x.compress_size,
          "uncompressed_size":x.file_size,
          "crc32":f"{x.CRC:08x}",
          "compression_type":x.compress_type,
          "is_dir":x.is_dir(),
          "filename_class":classify(x.filename),
          "filename_hints":hints(x.filename),
        })
    print(json.dumps({
      "contract":"ARCHIVE_INVENTORY_CONTRACT_V1.md",
      "source_url":URL,
      "archive_bytes":len(b),
      "member_bytes_read":0,
      "member_count":len(rows),
      "members":rows
    },indent=2))

if __name__=="__main__":main()
