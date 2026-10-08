#!/usr/bin/env python3
"""Dryad 2018 / 2022 metadata-only cross-modal bat source gate.

NO raw track coordinates, bat flight outcomes or sonar audio are downloaded.
Calls ONLY DOI-specific Dryad public REST API and API-provided version/file links.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse, quote
import requests

ROOT = "https://datadryad.org"
DOIS = ("10.5061/dryad.v9s4mw6wn", "10.5061/dryad.4f99c46")
HEADERS = {"Accept": "application/json", "User-Agent": "bat-3d-acoustics-source-metadata-only-v1"}
TIMEOUT = (8, 20)
MAX_PAGES = 8
MAX_LINKS = 12


def only_official(href):
    link = urljoin(ROOT, href)
    p = urlparse(link)
    if p.scheme != "https" or p.hostname != "datadryad.org":
        raise ValueError("nonofficial Dryad link refused")
    if not p.path.startswith("/api/v2/"):
        raise ValueError("Dryad metadata API paths only")
    return link


def safe_query(session, url):
    url = only_official(url)
    response = session.get(url, headers=HEADERS, timeout=TIMEOUT)
    if response.status_code != 200:
        return None, {"url": url, "status": response.status_code}
    try:
        return response.json(), {"url": url, "status": 200}
    except ValueError:
        return None, {"url": url, "status": 200, "warning": "non-JSON metadata"}


def extract_links(obj):
    all_links = []
    if isinstance(obj, dict):
        for name, value in (obj.get("_links") or {}).items():
            if not any(tok in name.lower() for tok in ("version", "file", "next")):
                continue
            for candidate in (value if isinstance(value, list) else [value]):
                href = candidate.get("href") if isinstance(candidate, dict) else None
                if href:
                    try:
                        all_links.append((name, only_official(href)))
                    except ValueError:
                        pass
    return all_links


def summarize_files(obj):
    files = []
    objects = []
    if isinstance(obj, list):
        objects = obj
    elif isinstance(obj, dict):
        for field in ("_embedded", "files", "items", "data"):
            arr = obj.get(field)
            if isinstance(arr, list):
                objects.extend(arr)
            if isinstance(arr, dict):
                for child in arr.values():
                    if isinstance(child, list):
                        objects.extend(child)
        if any(k in obj for k in ("filename", "fileName", "path", "file_name")):
            objects.append(obj)
    for item in objects:
        if not isinstance(item, dict):
            continue
        name = item.get("filename") or item.get("fileName") or item.get("file_name") or item.get("path")
        if not name:
            continue
        files.append({
            "name": str(name)[:250],
            "size": item.get("size") or item.get("fileSize") or item.get("size_bytes"),
            "mime": item.get("mimeType") or item.get("mime_type"),
            "file_id": item.get("id"),
        })
    return files


def inspect(session, doi):
    encoded = quote(f"doi:{doi}", safe="")
    address = f"{ROOT}/api/v2/datasets/{encoded}"
    item = {
        "doi": doi, "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "numeric_bat_outcomes_opened": False,
        "audio_or_binary_downloaded": False,
        "http_attempts": [],
        "files": [],
        "eligibility": "STOP_PUBLIC_SOURCE_INACCESSIBLE",
        "notes": []
    }
    queue = [address]
    visited = set()
    rounds = 0
    while queue and len(visited) < MAX_LINKS:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        try:
            data, status = safe_query(session, current)
        except requests.RequestException as e:
            item["http_attempts"].append({"url": current, "error": type(e).__name__})
            break
        except ValueError as e:
            item["notes"].append(str(e)[:100])
            break
        item["http_attempts"].append(status)
        if data is None:
            continue
        item["files"].extend(summarize_files(data))
        links = extract_links(data)
        for name, new_url in links:
            if new_url not in visited and new_url not in queue and len(queue) < MAX_PAGES:
                queue.append(new_url)
        rounds += 1
        if rounds >= MAX_PAGES:
            break
    seen = set()
    unique = []
    for f in item["files"]:
        key = (f["name"], f["file_id"])
        if key not in seen:
            seen.add(key)
            unique.append(f)
    item["files"] = unique
    if not any(x.get("status") == 200 for x in item["http_attempts"]):
        item["notes"].append("No readable DOI-specific public metadata. No alternative data mirrors tried.")
        return item
    if not unique:
        item["eligibility"] = "HOLD_NEEDS_SCHEMA"
        item["notes"].append("API metadata open, but explicit file list could not be read. No raw outcome opening.")
        return item
    names = " ".join(x["name"].lower() for x in unique)
    has_3d = any(word in names for word in (
        "track", "trajectory", "flightpath", "flight_path", "xyz", "coordinates", "3d", "position"
    ))
    has_audio = any(word in names for word in (
        "sound", "echo", "acoustic", "audio", ".wav", ".bin", "pulse", "sonar"
    ))
    if not has_3d and has_audio:
        item["eligibility"] = "STOP_NO_JOINT_3D_AUDIO"
        item["notes"].append("Listed acoustic files but no identified 3D file; cannot test acoustic/spatial joint response.")
    elif has_3d and has_audio:
        item["eligibility"] = "HOLD_NEEDS_SCHEMA"
        item["notes"].append("Possible 3D and acoustic assets, but no verified bat/time join or stable biological IDs.")
    else:
        item["eligibility"] = "HOLD_NEEDS_SCHEMA"
        item["notes"].append("Filename hints insufficient to prove joined bat/time/acoustic/3D source.")
    return item


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="DRYAD_GROUP_ACOUSTIC_3D_SOURCE_RECEIPT_V1.json")
    args = p.parse_args()
    s = requests.Session()
    items = [inspect(s, doi) for doi in DOIS]
    out = {
        "study": "Dryad 2018/2022 group sonar+3D structural access",
        "status": "PUBLIC_FILE_METADATA_ONLY",
        "numeric_values_opened": False,
        "datasets": items,
        "contract": "DRYAD_GROUP_AUDIO_3D_SOURCE_GATE_CONTRACT_V1.md",
    }
    Path(args.out).write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps([{
        "doi": i["doi"], "status": i["eligibility"],
        "files": [f["name"] for f in i["files"]],
        "http_statuses": i["http_attempts"]
    } for i in items], ensure_ascii=False))


if __name__ == "__main__":
    main()
