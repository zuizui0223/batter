#!/usr/bin/env python3
"""Original-source-only audit of publicly posted Münster 3D bat flight tracks.

Reads ZIP listing, source README *method/coordinate* lines and, only where
clearly text headers, source column headers + physical row counts. Does not
parse any bat x/y/z coordinates, height summaries, movement outcomes, or
clutter/model scores. Exact Zenodo MD5 hashes are required.
"""
from __future__ import annotations

from hashlib import md5,sha256
from io import BytesIO,StringIO
import csv,json,re
from pathlib import Path,PurePosixPath
from urllib.request import urlopen,Request
from zipfile import ZipFile,BadZipFile

RECORD="7797077"
BASE=f"https://zenodo.org/records/{RECORD}/files/"
SOURCES={
    "3DTracks.zip":"648c3effc18d43731f6ac267493046b9",
    "README.md":"b91d8cb9113e470af3108c4b6c5eb0b6",
}
DOWNLOAD_MAX=150_000
UNCOMPRESSED_TOTAL_MAX=10_000_000
SOURCE_MEMBER_MAX=5_000_000
SOURCE_MEMBER_MAX_COUNT=200
TRACK_COLUMNS_PATTERN=re.compile(
    r"\b(x|y|z|xyz|easting|northing|height|altitude|time|track|flight|id)\b",
    re.IGNORECASE
)
README_DESIGN_TERMS=re.compile(
    r"coordinate|reference|origin|position|tracking|track|3d|xyz|UTM|EPSG|"
    r"location|lamppost|forest|camera|DLT|calibra|thermal|site|datum",
    re.IGNORECASE
)


def source_url(name):
    from urllib.parse import quote
    return BASE+quote(name)+"?download=1"


def fetch_exact_source(name, expected_md5):
    req=Request(source_url(name), headers={
        "User-Agent":"batter-published-3d-track-source-audit/1.0"
    })
    with urlopen(req,timeout=120) as response:
        raw=response.read(DOWNLOAD_MAX+1)
    if not 0<len(raw)<=DOWNLOAD_MAX:
        raise ValueError("original source outside frozen byte cap")
    h=md5(raw).hexdigest()
    if h!=expected_md5:
        raise ValueError("original Zenodo author MD5 mismatch")
    return raw


def safe_member_metadata(raw):
    if not raw.startswith(b"PK"):
        raise ValueError("source expected ZIP file")
    with ZipFile(BytesIO(raw)) as z:
        files=[info for info in z.infolist() if not info.is_dir()]
        if not 0<len(files)<=SOURCE_MEMBER_MAX_COUNT:
            raise ValueError("source ZIP must contain bounded number of files")
        if sum(info.file_size for info in files)>UNCOMPRESSED_TOTAL_MAX:
            raise ValueError("ZIP uncompressed total exceeds declared source cap")
        if any(info.file_size>SOURCE_MEMBER_MAX for info in files):
            raise ValueError("ZIP individual source file exceeds cap")
        if len({i.filename for i in files})!=len(files):
            raise ValueError("ZIP has duplicated file entry paths")

        members=[]
        for info in files:
            path=PurePosixPath(info.filename)
            if path.is_absolute() or ".." in path.parts or "\\" in info.filename:
                raise ValueError("unsafe source ZIP member path")
            suffix=path.suffix.lower()
            item={
                "member":info.filename,"compressed_bytes":info.compress_size,
                "uncompressed_bytes":info.file_size,
                "file_extension":suffix,
                "raw_original_xyz_coordinates_opened":False,
            }
            # Only explicitly named textual headers; a numeric first row
            # is NOT printed, parsed or used to infer flying height.
            if suffix in (".csv",".tsv",".txt"):
                with z.open(info) as f:
                    first=f.readline(4096)
                    if first and len(first)<4096:
                        try:
                            line=first.decode("utf-8-sig")
                        except UnicodeDecodeError:
                            line=first.decode("latin-1")
                        delim="\t" if suffix==".tsv" else ","
                        header=next(csv.reader(StringIO(line),delimiter=delim))
                        if header and len(header)>=3 and (
                            all(not h.strip().replace(".","",1).replace("-","",1).isdigit()
                                for h in header[:3])
                            and any(TRACK_COLUMNS_PATTERN.search(h) for h in header)
                        ):
                            item["textual_column_headers_only"]=[h[:90] for h in header[:60]]
                            item["source_has_explicit_named_position_or_track_column"]=True
            members.append(item)
        return {
            "source_zip_member_count":len(files),
            "source_zip_total_uncompressed_bytes":sum(i.file_size for i in files),
            "source_members":members,
            "original_numeric_flight_locations_opened":False,
        }


def readme_design_lines(raw):
    txt=raw.decode("utf-8-sig",errors="replace")
    selected=[]
    for line in txt.splitlines():
        if README_DESIGN_TERMS.search(line):
            selected.append(line.strip()[:500])
    return selected[:35]


def run():
    receipt={
        "status":"public_original_tracking_source_stop",
        "original_data_record_url":f"https://zenodo.org/records/{RECORD}",
        "original_bat_flight_xyz_values_opened":False,
        "author_source_DOI":"10.5281/zenodo.7797077",
    }
    try:
        zip_raw=fetch_exact_source("3DTracks.zip",SOURCES["3DTracks.zip"])
        readme_raw=fetch_exact_source("README.md",SOURCES["README.md"])
        receipt.update({
            "source_original_checksums":{
                "3DTracks.zip":{"md5":md5(zip_raw).hexdigest(),
                                "sha256":sha256(zip_raw).hexdigest(),
                                "bytes":len(zip_raw)},
                "README.md":{"md5":md5(readme_raw).hexdigest(),
                             "sha256":sha256(readme_raw).hexdigest(),
                             "bytes":len(readme_raw)}
            },
            "README_original_design_and_coordinate_lines":readme_design_lines(readme_raw),
            **safe_member_metadata(zip_raw)
        })
        receipt["status"]="original_track_archive_and_readme_structurally_authenticated"
    except Exception as exc:
        receipt["status"]="original_archive_access_or_structure_stop"
        receipt["source_stop_exception"]=type(exc).__name__
        receipt["source_stop_reason"]=str(exc)[:300]
    return receipt


def main():
    receipt=run()
    out=Path("results/muenster_3dtracks_source_gate_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(receipt,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
