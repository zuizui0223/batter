#!/usr/bin/env python3
"""SOURCE METADATA ONLY for published Mormoops v4 3D bat-flight archive.

No numeric coordinates or flight outcomes are opened. This is NOT an analysis.
Mendeley public DOI: 10.17632/mrnvkzrdsd.4
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile

import requests

DSID = "mrnvkzrdsd"
VERSION = 4
ROOT = "https://api.data.mendeley.com/datasets"
ORIGIN = "https://data.mendeley.com/datasets/mrnvkzrdsd/4"
API_HEADERS = {
    "Accept": "application/vnd.mendeley-public-dataset.1+json, application/json",
    "User-Agent": "batter-academic-source-preflight/1.0 (source-only)",
}
FILE_NAMES = {
    "TrackTable_All.mat",
    "Switch_AnalysisTable.mat",
    "RelativeTurningStartTime_AnalysisTable.mat",
    "Echolocation_AnalysisTable.mat",
}
CODE_NAMES = {
    "SwitchAnalysis_GLMMcode.m",
    "RelativeTurningStartTime_GLMMcode.m",
    "EcholocationAnalysis_GLMMcode.m",
}
MAX_SMALL_FILE = 5_000_000  # source header/metadata only; never download audio
TIMEOUT = (10, 28)


def get_json(session, url):
    resp = session.get(url, headers=API_HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def file_list(obj):
    """Mendeley's public files endpoints return a list; allow documented wrappers."""
    if isinstance(obj, list):
        return obj
    for key in ("files", "items", "results"):
        if isinstance(obj, dict) and isinstance(obj.get(key), list):
            return obj[key]
    return []


def read_header(path):
    data = path.read_bytes()
    signature = data[:128]
    try:
        import scipy.io
        info = scipy.io.whosmat(str(path))
        return {"format": "matlab_v5_or_prior",
                "variables": [{"name": n, "shape": list(shape), "class": class_name}
                              for n, shape, class_name in info],
                "numeric_values_opened": False}
    except Exception as exc:
        if data[:8] != b"\x89HDF\r\n\x1a\n":
            return {"format": "unknown_or_unsupported", "reason": type(exc).__name__,
                    "variables": [], "numeric_values_opened": False}
        try:
            import h5py
            with h5py.File(path, "r") as f:
                vars_ = [{"name": k, "shape": list(v.shape) if hasattr(v, "shape") else None,
                          "kind": "dataset" if hasattr(v, "shape") else "group"}
                         for k, v in f.items()]
            return {"format": "matlab_v7_3_hdf5", "variables": vars_,
                    "numeric_values_opened": False}
        except Exception as exc2:
            return {"format": "hdf5_unreadable", "reason": type(exc2).__name__,
                    "variables": [], "numeric_values_opened": False}


def safe_fields_script(text):
    """Only MATLAB field/table syntax names, never execution or numerical summaries."""
    raw = re.findall(r"(?:TrackTable_All|TrackTable|Switch_AnalysisTable|SwitchAnalysisTable|Echolocation_AnalysisTable|"
                     r"RelativeTurningStartTime_AnalysisTable)\.([A-Za-z_]\w*)", text)
    raw += re.findall(r"\b(?:BatID|batID|animalID|batNumber|IndividualID|TrackID|FlightID|SessionID|"
                      r"SwitchID|EventID|Frame|Timestamp|Time|Role|Lead|Follow|Position|X|Y|Z)\b", text)
    return sorted(set(raw))[:120]


def api_download(session, f, tmp_dir):
    # Public API describes dataset/{id}/files/{uuid}/file_downloaded as 307 signed redirect.
    f_id = f.get("id")
    if not f_id:
        raise ValueError("missing authenticated-safe public file identifier")
    name = f.get("filename") or f.get("name")
    meta = f.get("content_details") or {}
    url = (meta.get("download_url") if isinstance(meta, dict) else None)
    if not url:
        url = f"{ROOT}/{DSID}/files/{f_id}/file_downloaded?version={VERSION}"
    if not url.startswith("https://"):
        raise ValueError("non-HTTPS source refused")
    out = tmp_dir / re.sub(r"[^A-Za-z0-9_.-]", "_", name)
    with session.get(url, headers={"User-Agent": API_HEADERS["User-Agent"]},
                     stream=True, timeout=TIMEOUT, allow_redirects=True) as response:
        response.raise_for_status()
        sz = 0
        hasher = hashlib.sha256()
        with out.open("wb") as sink:
            for b in response.iter_content(65536):
                if not b:
                    continue
                sz += len(b)
                if sz > MAX_SMALL_FILE:
                    raise ValueError("file exceeds 5MB safe structural-only cap")
                hasher.update(b)
                sink.write(b)
    return out, hasher.hexdigest(), sz


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="MORMOOPS_V4_STRUCTURAL_RECEIPT_V1.json")
    args = p.parse_args()
    receipt = {
        "evidence_tier": "SOURCE_ONLY_NO_NUMERIC_BAT_OUTCOMES_OPENED",
        "dataset": ORIGIN,
        "dataset_doi": "10.17632/mrnvkzrdsd.4",
        "version": VERSION,
        "checked_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "STOP_SOURCE_INACCESSIBLE",
        "api_metadata": {},
        "public_files": [],
        "small_file_structure": [],
        "structural_notes": [],
        "warnings": []
    }
    session = requests.Session()
    try:
        metadata = get_json(session, f"{ROOT}/{DSID}?version={VERSION}")
        receipt["api_metadata"] = {
            key: metadata.get(key) for key in ("id", "name", "version", "description")
            if isinstance(metadata, dict) and key in metadata
        }
        files_obj = get_json(session, f"{ROOT}/{DSID}/files?version={VERSION}")
        listed = file_list(files_obj)
        if not listed:
            raise ValueError("public file list API returned no file records")
        receipt["public_files"] = [
            {"name": f.get("filename") or f.get("name"),
             "size": f.get("size") or ((f.get("content_details") or {}).get("size")),
             "uuid": f.get("id"), "media_type": f.get("media_type")}
            for f in listed if isinstance(f, dict)
        ]
    except Exception as exc:
        receipt["warnings"].append("API metadata retrieval stopped: " +
                                   type(exc).__name__ + ": " + str(exc)[:220])
        Path(args.out).write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n")
        print(json.dumps({"status": receipt["status"], "warnings": receipt["warnings"]},
                         ensure_ascii=False))
        return

    found = {x.get("filename") or x.get("name"): x for x in listed
             if isinstance(x, dict)}
    target_present = sorted(FILE_NAMES & set(found))
    receipt["status"] = "STOP_RAW_TRACK_UNAVAILABLE"
    if "TrackTable_All.mat" not in found:
        receipt["warnings"].append("V4 file listing lacks TrackTable_All.mat, identity analysis STOP")
    with tempfile.TemporaryDirectory(prefix="mormoops-v4-structural-") as d:
        directory = Path(d)
        for name in sorted((FILE_NAMES | CODE_NAMES) & set(found)):
            f = found[name]
            announced_size = f.get("size") or (f.get("content_details") or {}).get("size")
            if announced_size and int(announced_size) > MAX_SMALL_FILE:
                receipt["small_file_structure"].append(
                    {"name": name, "status": "SKIP_TOO_LARGE", "announced_size": announced_size})
                continue
            try:
                local, digest, sz = api_download(session, f, directory)
                entry = {"name": name, "status": "DOWNLOADED_FOR_HEADER_ONLY",
                         "sha256": digest, "bytes": sz}
                details = f.get("content_details") or {}
                published_hash = details.get("sha256_hash")
                if published_hash:
                    entry["published_sha256"] = published_hash
                    entry["published_digest_matches"] = published_hash.lower() == digest.lower()
                if name.endswith(".mat"):
                    entry["mat_structural_header"] = read_header(local)
                elif name.endswith(".m"):
                    script = local.read_text("utf-8", errors="replace")
                    entry["possible_table_metadata_field_tokens"] = safe_fields_script(script)
                    entry["script_bytes_executed"] = False
                receipt["small_file_structure"].append(entry)
            except Exception as exc:
                receipt["small_file_structure"].append(
                    {"name": name, "status": "STOP_DOWNLOAD_OR_HEADER",
                     "error": type(exc).__name__ + ": " + str(exc)[:160]})
    track_headers = [
        e for e in receipt["small_file_structure"]
        if e["name"] == "TrackTable_All.mat"
        and e["status"] == "DOWNLOADED_FOR_HEADER_ONLY"
    ]
    if not track_headers:
        receipt["status"] = "STOP_RAW_TRACK_UNAVAILABLE"
    else:
        receipt["status"] = "PASS_SOURCE_STRUCTURAL_ONLY"
        receipt["structural_notes"].append(
            "MAT variable names and shapes alone DO NOT prove persistent biological bat IDs."
        )
        receipt["structural_notes"].append(
            "Separate Gate 2 requires author-documented stable bat ID across bouts AND acoustic track joins."
        )
        receipt["structural_notes"].append(
            "No numeric track, speed, timestamp, role-switching or echolocation outcomes analyzed."
        )

    Path(args.out).write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({
        "status": receipt["status"], "names": [x["name"] for x in receipt["public_files"]],
        "small_file_structure": [
            {"name": x["name"], "status": x["status"],
             "variables": x.get("mat_structural_header", {}).get("variables"),
             "possible_fields": x.get("possible_table_metadata_field_tokens")}
            for x in receipt["small_file_structure"]
        ], "warnings": receipt["warnings"]
    }, ensure_ascii=False))
if __name__ == "__main__":
    main()
