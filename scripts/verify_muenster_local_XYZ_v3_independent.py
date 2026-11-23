#!/usr/bin/env python3
"""Independent NumPy source XYZ count replay: no production parser imported.

The 197 finite local thermal XYZ point count is a technical source result,
NOT actual bat 3D habitat use, calibrated animal q or LiDAR co-location.
"""
from __future__ import annotations

from hashlib import md5,sha256
from io import BytesIO
from pathlib import Path
from urllib.request import Request,urlopen
from zipfile import ZipFile
import json,re

import numpy as np

DOI="10.5281/zenodo.7797077"
URL="https://zenodo.org/records/7797077/files/3DTracks.zip?download=1"
ORIGINAL_MD5="648c3effc18d43731f6ac267493046b9"
ORIGINAL_SHA256="1f30d61e66eec1ad078ad114070ae25a543fc7fb86cbae03e52f9a0ee6ff0010"
CANONICAL=re.compile(r"^DLTdv5_night(18|19)_bat([0-9]+)_xyzpts\.csv$")

def numpy_author_csv_triple_counts(blob:bytes):
    s=blob.decode("utf-8-sig")
    first=s.splitlines()[0]
    delim=max((",","\t",";"),key=first.count)
    source=np.genfromtxt(
        BytesIO(blob),delimiter=delim,names=True,dtype=float,encoding="utf-8",
        autostrip=True,invalid_raise=True
    )
    source=np.atleast_1d(source)
    names=source.dtype.names
    expected=("pt1_X","pt1_Y","pt1_Z")
    if names not in (expected,expected+("pt2_X","pt2_Y","pt2_Z")):
        raise ValueError("independent source original DLTdv5 header mismatch")
    counts={}
    for prefix in ("pt1", "pt2") if len(names)==6 else ("pt1",):
        selected=np.column_stack([source[f"{prefix}_{c}"] for c in "XYZ"])
        counts[prefix]=int(np.isfinite(selected).all(axis=1).sum())
    return counts


def replay_original():
    with urlopen(Request(URL,headers={
        "User-Agent":"batter-independent-public-thermal-coordinate-audit/1.0",
    }),timeout=120) as request:
        raw=request.read(150_001)
    if (md5(raw).hexdigest()!=ORIGINAL_MD5 or
        sha256(raw).hexdigest()!=ORIGINAL_SHA256):
        raise ValueError("original author ZIP source fingerprint mismatch")
    by_night_canonical={"18":set(),"19":set()}
    by_night_xyz={"18":0,"19":0}
    by_night_streams={"18":0,"19":0}
    sum_valid=0
    with ZipFile(BytesIO(raw)) as original:
        for info in original.infolist():
            if info.is_dir() or not info.filename.endswith(".csv"):
                continue
            basename=info.filename.split("/")[-1]
            match=CANONICAL.fullmatch(basename)
            if not match:continue   # lamp and duplicate _uninterrupted sources
            night,batID=match.groups()
            if batID in by_night_canonical[night]:
                raise ValueError("duplicate canonical original bat filename")
            by_night_canonical[night].add(batID)
            triples=numpy_author_csv_triple_counts(original.read(info))
            for _,n in triples.items():
                if n>0:
                    by_night_xyz[night]+=n
                    by_night_streams[night]+=1
                    sum_valid+=n
    if ({k:len(v) for k,v in by_night_canonical.items()}!={"18":8,"19":3}
        or by_night_streams!={"18":9,"19":3}
        or sum_valid!=197):
        raise RuntimeError("independent original source finite coordinate counts disagree with v2.3")
    return {
        "status":"independent_real_local_XYZ_count_replay_exact",
        "original_source_DOI":DOI,
        "original_source_sha256":ORIGINAL_SHA256,
        "original_CSV_numeric_reader":"NumPy genfromtxt, independent of v2.3 CSV scorer",
        "original_canonical_bat_filenames_by_night":{k:len(v) for k,v in by_night_canonical.items()},
        "original_source_coordinate_target_streams_by_night":by_night_streams,
        "original_finite_XYZ_coordinate_rows_by_night":by_night_xyz,
        "total_finite_XYZ_source_points":sum_valid,
        "source_unit_and_AGL_datum_verified":False,
        "world_control_transform_or_LAS_aligned":False,
        "3D_bat_clutter_niche_fitted":False,
    }


def main():
    path=Path("results/muenster_real_local_xyz_independent_v3.json")
    path.parent.mkdir(parents=True,exist_ok=True)
    receipt=replay_original()
    path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(receipt,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
