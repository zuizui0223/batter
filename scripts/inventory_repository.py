#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request

HANDLE = "10255/move.1055"
REPOSITORY = "https://datarepository.movebank.org"
PID_URL = f"{REPOSITORY}/server/api/pid/find?id={urllib.parse.quote(HANDLE, safe='')}"


def fetch_json(url: str):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "batter-repository-inventory/0.1",
            "Accept": "application/hal+json, application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        data = response.read()
        final_url = response.geturl()
    payload = json.loads(data.decode("utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("non-object repository JSON")
    return payload, data, final_url


def link(payload, name):
    value = payload.get("_links", {}).get(name, {})
    return str(value.get("href", "")) if isinstance(value, dict) else ""


def embedded(payload, name):
    value = payload.get("_embedded", {}).get(name, [])
    return [x for x in value if isinstance(x, dict)] if isinstance(value, list) else []


def checksum(bitstream):
    value = bitstream.get("checkSum") or bitstream.get("checksum") or {}
    if not isinstance(value, dict):
        return "", ""
    return (
        str(value.get("checkSumAlgorithm") or value.get("algorithm") or ""),
        str(value.get("value") or ""),
    )


def inventory():
    item, item_raw, item_url = fetch_json(PID_URL)
    bundles_url = link(item, "bundles")
    bundles_payload, bundles_raw, bundles_url = fetch_json(bundles_url)
    files = []
    metadata_hashes = {
        "item": hashlib.sha256(item_raw).hexdigest(),
        "bundles": hashlib.sha256(bundles_raw).hexdigest(),
    }
    for bundle in embedded(bundles_payload, "bundles"):
        bundle_name = str(bundle.get("name", ""))
        bitstreams_url = link(bundle, "bitstreams")
        if not bitstreams_url:
            continue
        bs_payload, bs_raw, _ = fetch_json(bitstreams_url)
        key = str(bundle.get("uuid") or bundle.get("id") or bundle_name)
        metadata_hashes[f"bitstreams:{key}"] = hashlib.sha256(bs_raw).hexdigest()
        for bs in embedded(bs_payload, "bitstreams"):
            ctype, csum = checksum(bs)
            files.append({
                "bundle_name": bundle_name,
                "bitstream_id": str(bs.get("uuid") or bs.get("id") or ""),
                "filename": str(bs.get("name") or ""),
                "description": str(bs.get("description") or ""),
                "mime_type": str(bs.get("mimeType") or bs.get("mime_type") or ""),
                "size_bytes": bs.get("sizeBytes"),
                "checksum_type": ctype,
                "checksum": csum,
                "content_url": link(bs, "content"),
            })
    files.sort(key=lambda x:(x["bundle_name"],x["filename"],x["bitstream_id"]))
    return {
        "inventory_id":"batter-movebank-repository-inventory-v1",
        "handle":HANDLE,
        "resolved_item_url":item_url,
        "metadata_sha256":metadata_hashes,
        "file_count":len(files),
        "files":files,
        "bitstream_content_fetched":False,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=inventory()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "file_count":result["file_count"],
        "files":[
            {k:f[k] for k in ("bundle_name","filename","bitstream_id","size_bytes","checksum_type","checksum","content_url")}
            for f in result["files"]
        ],
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
