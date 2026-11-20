"""Dryad Rousettus 2020 manipulation: ORIGINAL metadata-only source gate.

Only official public Dryad REST v2 dataset/version/file inventory JSON.
NEVER download or parse any original bat, tree or treatment response row.
This is source eligibility, not confirmation of 3D altitude or resource SDM.
"""
from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

DOI = "doi:10.5061/dryad.51c59zwgp"
ENTRY = "https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.51c59zwgp"
HOST = "https://datadryad.org"
MAX_BYTES = 2_000_000
MAX_PAGES = 10
REQUIRED_FILES = (
    "Field_Manipulation_Table.csv",
    "manipulations_trees_locations.csv",
    "Tags_manipulated_and_visiting.csv",
    "Syc_Manipulation_Dec2020_Filtered.sqlite",
    "Syc_Manipulation_July2020_Filtered.sqlite",
    "Syc_Manipulation_June2020_Filtered.sqlite",
)
STATUS = "ROUS_ORIGINAL_DRYAD_VERSION_FILE_METADATA_VERIFIED"


def official_url(href):
    if not isinstance(href, str) or not href:
        raise ValueError("SOURCE_LINK_MISSING")
    url = urljoin(HOST, href)
    p = urlparse(url)
    if (p.scheme != "https" or p.netloc != "datadryad.org"
            or not p.path.startswith("/api/v2/") or p.username or p.password):
        raise ValueError("SOURCE_LINK_NOT_OFFICIAL_DRYAD_API")
    return url


def fetch_json(url):
    target = official_url(url)
    req = Request(target, headers={
        "Accept": "application/json",
        "User-Agent": "batter-resource-behavior-source-metadata/1.0"
    })
    with urlopen(req, timeout=40) as response:
        if official_url(response.url) != target or response.status != 200:
            raise RuntimeError("SOURCE_REDIRECT_OR_HTTP_CHANGED")
        payload = response.read(MAX_BYTES + 1)
        if len(payload) > MAX_BYTES:
            raise RuntimeError("SOURCE_JSON_TOO_LARGE")
    value = json.loads(payload.decode("utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("SOURCE_JSON_NOT_OBJECT")
    return value


def hal_link(doc, key):
    link = doc.get("_links", {}).get(key, {})
    return official_url(link.get("href"))


def audit(fetch=fetch_json):
    ds = fetch(ENTRY)
    if str(ds.get("identifier", "")).lower() != DOI.lower():
        raise RuntimeError("SOURCE_DATASET_DOI_MISMATCH")
    version = fetch(hal_link(ds, "stash:version"))
    url = hal_link(version, "stash:files")
    count = None
    by_path = {}
    page_count = 0
    seen = set()
    while url:
        page_count += 1
        if page_count > MAX_PAGES:
            raise RuntimeError("SOURCE_FILE_PAGE_LIMIT")
        block = fetch(url)
        total = block.get("total")
        if type(total) is not int:
            raise RuntimeError("SOURCE_LIST_TOTAL_MISSING")
        if count is None:
            count = total
        if total != count:
            raise RuntimeError("SOURCE_FILE_TOTAL_CHANGED")
        rows = block.get("_embedded", {}).get("stash:files")
        if not isinstance(rows, list):
            raise RuntimeError("SOURCE_MISSING_FILE_LIST")
        for row in rows:
            item_id, name, nbytes = row.get("id"), row.get("path"), row.get("size")
            if (type(item_id) is not int or not isinstance(name,str)
                    or not name or type(nbytes) is not int or nbytes < 0):
                raise RuntimeError("SOURCE_BAD_FILE_METADATA")
            if item_id in seen or name in by_path:
                raise RuntimeError("SOURCE_DUPLICATE_FILE")
            seen.add(item_id)
            by_path[name] = {
                "file_name": name,
                "size_bytes": nbytes,
                "digest_type": row.get("digestType"),
                "digest": row.get("digest"),
                "original_bytes_read": False,
            }
        nxt = block.get("_links", {}).get("next", {})
        url = official_url(nxt["href"]) if isinstance(nxt,dict) and isinstance(nxt.get("href"),str) else None
    if len(seen) != count:
        raise RuntimeError("SOURCE_FILE_TOTAL_MISMATCH")
    missing = sorted(set(REQUIRED_FILES) - set(by_path))
    if missing:
        raise RuntimeError("SOURCE_REQUIRED_FILES_MISSING:"+",".join(missing))
    for name in REQUIRED_FILES:
        rec=by_path[name]
        if rec["size_bytes"] <= 0:
            raise RuntimeError("SOURCE_REQUIRED_FILE_EMPTY:"+name)
    declared = ds.get("storageSize")
    actual = sum(x["size_bytes"] for x in by_path.values())
    if type(declared) is int and declared != actual:
        raise RuntimeError("SOURCE_DATASET_STORAGE_SIZE_MISMATCH")
    return {
        "schema": "batter.resource_behavior_sdm.dryad_rous_meta.v1",
        "status": STATUS,
        "utc": datetime.now(timezone.utc).isoformat(),
        "dataset_doi": DOI,
        "version_id": version.get("id"),
        "version_number": version.get("versionNumber"),
        "declared_total_file_count": count,
        "file_list_pages": page_count,
        "required_original_file_metadata": [by_path[n] for n in REQUIRED_FILES],
        "original_bat_and_tree_response_rows_opened": False,
        "individual_event_join_demonstrated": False,
        "altitude_source_verified": False,
        "5d_resource_effect": None,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="prospective/resource_behavior_sdm/rous_meta_receipt.json")
    args = parser.parse_args()
    output = pathlib.Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        r = audit()
    except Exception as exc:
        r = {
            "schema": "batter.resource_behavior_sdm.dryad_rous_meta.v1",
            "status": "SOURCE_METADATA_STOP",
            "reason": str(exc)[:250],
            "dataset_doi": DOI,
            "original_bat_and_tree_response_rows_opened": False,
            "altitude_source_verified": False,
            "5d_resource_effect": None,
        }
    output.write_text(json.dumps(r, indent=2, ensure_ascii=False)+"\n",encoding="utf-8")
    print("ROUS_META",r["status"],flush=True)
    return 0 if r["status"] == STATUS else 3


if __name__=="__main__":
    raise SystemExit(main())
