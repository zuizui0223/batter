#!/usr/bin/env python3
"""Recover the exact 2026 historical terrain-geometry source tree (CODE ONLY).

All paths and original git-blob SHA-1 values are pinned in the manifest, and
every retrieved byte stream is cryptographically checked before writing.
No data/DEM download, Python module import, pipeline execution, or statistical
result production occurs here. This is a reproducibility packaging utility.

Usage:
  python .../recover_terrain_source_closure_v1.py --inventory-only
  python .../recover_terrain_source_closure_v1.py --out /tmp/bat-source-closure
  python .../recover_terrain_source_closure_v1.py --out /tmp/bat-source-closure --offline

The generated archive contains only original public repository code, source
contracts and source metadata receipts; no third-party raw tracking files.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
import urllib.request
import zipfile

HERE=Path(__file__).resolve().parent
MANIFEST=HERE/"terrain_source_closure_manifest_v1.json"
EXPECTED_REPO="zuizui0223/batter"
EXPECTED_COMMIT="819acc829d615485b57033f1ddcbebf64b4b49a0"
EXPECTED_RUN=36946126004
SOURCE_BASE=f"https://raw.githubusercontent.com/{EXPECTED_REPO}/{EXPECTED_COMMIT}/"
REQUIRED={
 "post_freeze_extensions/3d_niche_partition/run_original_terrain_geometry_v1.py",
 "post_freeze_extensions/3d_niche_partition/run_v1.py",
 "post_freeze_extensions/3d_niche_partition/run_external_geometry_v1.py",
 "post_freeze_extensions/3d_niche_partition/original_terrain_geometry_contract_v1.json",
 "post_freeze_extensions/3d_niche_partition/original_terrain_dem_preflight_receipt_v1.json",
 "post_freeze_extensions/3d_niche_partition/summary_v1.json",
 "src/batter/analysis.py",
 "scripts/run_new_species_replications.py",
 "scripts/run_cross_panel_estimator_calibration.py",
 "scripts/run_tag_altitude_bias_shape.py",
 "scripts/run_eidolon_independent_replication.py",
 "scripts/run_biological_effect_translation.py",
 "contract/hypsignathus_replication_v1.json",
 "contract/phyllostomus_replication_v1.json",
 "contract/phyllostomus_2023_replication_v1.json",
 "contract/phyllostomus_2016_dry_architecture_v1.json"
}
FORBIDDEN_SUFFIXES={".csv",".tsv",".parquet",".hgt",".tif",".tiff",".gpkg",".gpx",".geojson",".gz"}

def git_blob_sha(content:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(content)).encode()+b"\x00"+content).hexdigest()

def source_entries():
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["schema_version"]==1
    assert manifest["original_repository"]==EXPECTED_REPO
    assert manifest["historical_success_commit"]==EXPECTED_COMMIT
    assert manifest["historical_terrain_workflow_run_id"]==EXPECTED_RUN
    files=manifest["files"]
    assert len(files)==21
    paths=set()
    for entry in files:
        path=entry["path"]
        pure=PurePosixPath(path)
        assert pure.parts and not pure.is_absolute() and ".." not in pure.parts
        assert pure.suffix in {".py",".json",".toml"} and pure.suffix not in FORBIDDEN_SUFFIXES
        assert path not in paths
        paths.add(path)
        assert len(entry["git_blob_sha1"])==40
        assert all(c in "0123456789abcdef" for c in entry["git_blob_sha1"])
    assert REQUIRED <= paths,("Missing required historical source",sorted(REQUIRED-paths))
    assert manifest["raw_input_boundary"].startswith("Do not include")
    return manifest,files

def source_from_historical_commit(path:str)->bytes:
    request=urllib.request.Request(
        SOURCE_BASE+path,
        headers={"User-Agent":"batter-historical-terrain-source-closure-v1/1.0"},
    )
    with urllib.request.urlopen(request,timeout=60) as response:
        assert response.status==200
        content=response.read()
        assert len(content)<1_000_000,(path,"unexpectedly large file")
        return content

def code_static_gate(root:Path,files:list[dict])->None:
    """Parse without importing or running source modules; inspect direct imports."""
    present={x["path"] for x in files}
    for file in files:
        original=root/file["path"]
        content=original.read_bytes()
        got=git_blob_sha(content)
        assert got==file["git_blob_sha1"],(file["path"],got,file["git_blob_sha1"])
        if original.suffix==".py":
            tree=ast.parse(content.decode("utf8"),filename=file["path"])
            for node in ast.walk(tree):
                if isinstance(node,ast.Import):
                    imported=[a.name for a in node.names]
                elif isinstance(node,ast.ImportFrom):
                    imported=[node.module or ""]
                else:continue
                for name in imported:
                    if name.startswith("scripts."):
                        assert name.replace(".","/")+".py" in present,(
                            file["path"],"missing imported local script "+name)
                    if name=="batter.analysis":
                        assert "src/batter/analysis.py" in present
        elif original.suffix==".json":
            json.loads(content.decode("utf8"))
    runner=(root/"post_freeze_extensions/3d_niche_partition/run_original_terrain_geometry_v1.py").read_text("utf8")
    assert 'run_v1.py' in runner and 'run_external_geometry_v1.py' in runner
    assert 'original_terrain_dem_preflight_receipt_v1.json' in runner
    native=json.loads((root/"post_freeze_extensions/3d_niche_partition/summary_v1.json").read_text())
    assert native["study_id"]=="batter-3d-niche-partition-v1"
    assert native["workflow"]["run_id"]==36881187913
    terrain=json.loads((root/"post_freeze_extensions/3d_niche_partition/original_terrain_geometry_contract_v1.json").read_text())
    assert terrain["study_id"]=="batter-original-panel-terrain-3d-geometry-v1"
    p=(root/"pyproject.toml").read_text("utf8")
    for token in ('name = "batter"','numpy>=1.26','pyproj>=3.6'):
        assert token in p
    print("PASS: 21 source files verified byte-for-byte and parsed; native/terrain contracts and historical run IDs intact")

def deterministic_zip(root:Path,items:list[dict],manifest:dict)->Path:
    outfile=root.parent/"terrain_original_3d_source_closure_v1.zip"
    with zipfile.ZipFile(outfile,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        def add(name,raw):
            info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(0o100644<<16)
            z.writestr(info,raw,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
        for item in sorted(items,key=lambda x:x["path"]):
            p=item["path"]
            add("historical_commit_819acc82/"+p,(root/p).read_bytes())
        add("historical_commit_819acc82/RECOVERY_MANIFEST_V1.json",
            (json.dumps(manifest,sort_keys=True,indent=2)+"\n").encode("utf8"))
    with zipfile.ZipFile(outfile) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(items)+1
        for item in items:
            archive=z.read("historical_commit_819acc82/"+item["path"])
            assert git_blob_sha(archive)==item["git_blob_sha1"],item["path"]
    print("SOURCE_ONLY_ARCHIVE",outfile, outfile.stat().st_size,"bytes")
    return outfile

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--inventory-only",action="store_true",help="validate the manifest only, no network")
    ap.add_argument("--offline",action="store_true",help="verify local recovered files without network")
    ap.add_argument("--out",type=Path,default=HERE/"build"/"historical_commit_819acc82")
    args=ap.parse_args()
    manifest,files=source_entries()
    if args.inventory_only:
        print("PASS historical single-commit source inventory",EXPECTED_COMMIT,"files",len(files))
        return
    root=args.out.resolve()
    root.mkdir(parents=True,exist_ok=True)
    for index,item in enumerate(files,1):
        p=item["path"]
        target=root/p
        if args.offline:
            data=target.read_bytes()
        else:
            data=source_from_historical_commit(p)
        got=git_blob_sha(data)
        assert got==item["git_blob_sha1"],(p,"historical Git blob mismatch",got)
        if not args.offline:
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(data)
        print(f"VERIFIED {index:02}/{len(files)} {p}")
    code_static_gate(root,files)
    deterministic_zip(root,files,manifest)
    print("NO GPS/DEM input downloaded. NO live bat data or scientific analysis executed.")

if __name__=="__main__":
    main()
