#!/usr/bin/env python3
"""Outcome-blind public Mendeley source metadata/file inventory v1.

Reads public dataset metadata and file inventory only.
Does not download file contents.
"""

from __future__ import annotations

import json
import pathlib
import urllib.parse
import urllib.request
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent
OUT_JSON = HERE / "PUBLIC_SOURCE_AUDIT_RESULT_V1.json"
OUT_MD = HERE / "PUBLIC_SOURCE_AUDIT_RESULT_V1.md"

SOURCES = [
    {
        "key": "aharon2017",
        "dataset_id": "f6mvhj5gj9",
        "version": 3,
        "expected_doi": "10.17632/f6mvhj5gj9.3",
        "expected_title_token": "path-integration",
    },
    {
        "key": "ma2025",
        "dataset_id": "964fv73w94",
        "version": 1,
        "expected_doi": "10.17632/964fv73w94.1",
        "expected_title_token": "masking noise",
    },
]

HEADERS = {
    "User-Agent": "batter-public-structure-audit/1.0",
    "Accept": "application/json, application/vnd.mendeley-public-dataset.1+json",
}


def fetch_json(url: str):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = resp.read()
        return json.loads(body.decode("utf-8")), resp.status, dict(resp.headers)


def normalize_doi(meta):
    doi = meta.get("doi")
    if isinstance(doi, dict):
        return doi.get("id") or doi.get("doi")
    return doi


def list_files(dataset_id: str, version: int):
    url = (
        f"https://data.mendeley.com/api/datasets/{dataset_id}/files?"
        + urllib.parse.urlencode({"version": version, "$start": 0, "$limit": 1000})
    )
    data, status, headers = fetch_json(url)
    if isinstance(data, dict):
        rows = data.get("items") or data.get("files") or data.get("results") or data.get("data") or []
    else:
        rows = data or []
    return rows, {"mode": "anonymous_public_api", "status": status, "url": url}, []


def compact_file(row):
    details = row.get("content_details") or {}
    return {
        "id": row.get("id"),
        "filename": row.get("filename") or row.get("name"),
        "description": row.get("description"),
        "folder_id": row.get("folder_id"),
        "size": row.get("size") or details.get("size"),
        "content_type": details.get("content_type") or row.get("content_type"),
        "sha256": details.get("sha256_hash") or row.get("sha256_hash"),
    }


def source_audit(source):
    dataset_id = source["dataset_id"]
    version = source["version"]
    meta_url = f"https://data.mendeley.com/api/datasets/{dataset_id}/snapshot/{version}"

    out = {
        "source": source,
        "metadata": None,
        "metadata_fetch": None,
        "files": [],
        "file_fetch": None,
        "errors": [],
        "verdict": None,
    }

    try:
        meta, status, headers = fetch_json(meta_url)
        out["metadata_fetch"] = {"status": status, "url": meta_url}
        out["metadata"] = {
            "id": meta.get("id"),
            "name": meta.get("name") or meta.get("title"),
            "description": meta.get("description"),
            "version": meta.get("version"),
            "doi": normalize_doi(meta),
            "publish_date": meta.get("publish_date") or meta.get("published_date"),
        }
    except Exception as exc:
        out["errors"].append({"stage": "metadata", "error": repr(exc)})

    try:
        files, info, errors = list_files(dataset_id, version)
        out["file_fetch"] = info
        out["errors"].extend({"stage": "files_fallback", **e} for e in errors)
        rows = files or []
        out["files"] = [compact_file(x) for x in rows if isinstance(x, dict)]
    except Exception as exc:
        out["errors"].append({"stage": "files", "error": repr(exc)})

    meta = out["metadata"] or {}
    doi_ok = str(meta.get("doi") or "").lower() == source["expected_doi"].lower()
    title_ok = source["expected_title_token"].lower() in str(meta.get("name") or "").lower()
    version_ok = str(meta.get("version")) == str(version)

    if doi_ok and title_ok and version_ok and out["files"]:
        out["verdict"] = "PASS_PUBLIC_METADATA_AND_FILE_INVENTORY"
    elif doi_ok and title_ok and version_ok:
        out["verdict"] = "PASS_DATASET_IDENTITY_FILE_INVENTORY_UNRESOLVED"
    else:
        out["verdict"] = "STOP_DATASET_IDENTITY_OR_API_UNRESOLVED"

    return out


def render_md(result):
    lines = [
        "# Public perturbation source audit result v1",
        "",
        "## Status",
        "",
        "**OUTCOME-BLIND METADATA / FILE-INVENTORY AUDIT.**",
        "",
        "No research-data file contents were downloaded by this script.",
        "",
    ]
    for x in result["sources"]:
        s = x["source"]
        m = x.get("metadata") or {}
        lines += [
            f"## {s['key']}",
            "",
            f"- dataset: `{s['dataset_id']}` v{s['version']}",
            f"- expected DOI: `{s['expected_doi']}`",
            f"- fetched title: {m.get('name')}",
            f"- fetched DOI: {m.get('doi')}",
            f"- fetched version: {m.get('version')}",
            f"- file count: {len(x.get('files') or [])}",
            f"- verdict: **{x.get('verdict')}**",
            "",
        ]
        if x.get("files"):
            lines += [
                "| filename | size | content type | sha256 |",
                "|---|---:|---|---|",
            ]
            for f in x["files"]:
                lines.append(
                    f"| {f.get('filename')} | {f.get('size')} | "
                    f"{f.get('content_type')} | {f.get('sha256')} |"
                )
            lines.append("")
        if x.get("errors"):
            lines += ["### Fetch notes", ""]
            for e in x["errors"]:
                lines.append(f"- {e}")
            lines.append("")

    lines += [
        "## Boundary",
        "",
        "This result inventories public structure only.",
        "It does not establish individual persistence, treatment effects, or any biological endpoint.",
        "",
    ]
    return "\n".join(lines)


def main():
    result = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "audit_version": 1,
        "sources": [source_audit(s) for s in SOURCES],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    OUT_MD.write_text(render_md(result) + "\n")
    print(OUT_MD.read_text())


if __name__ == "__main__":
    main()
