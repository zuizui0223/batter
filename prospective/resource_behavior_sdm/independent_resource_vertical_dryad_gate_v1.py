"""Official Dryad metadata-only eligibility gate for two INDEPENDENT bat studies.

2026 Trujillo: same-study 3D GPS (MSL), movement states and land cover.
2018 Capaverde: directly measured fruit and insect availability + bat captures.
This tool NEVER downloads GPS, raster, XLSX or biological source rows.
Source files/versions are publisher verified; these two studies are not
joined as though they contained matching animals, sites or times.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import urllib.parse
import urllib.request

API_HOST = "https://datadryad.org"
MAX_JSON_BYTES = 2_000_000
MAX_PAGES = 20

SOURCES = {
    "chrotopterus_2026": {
        "doi": "10.5061/dryad.7d7wm38c0",
        "role": "independent_3d_habitat_and_behavior",
        "paper": "10.1111/1365-2656.70391",
        "expected": {
            "Chrotopterus_auritus_Movement_Ecology_Analysis.zip",
            "Landscape_data.zip",
            "Movement_data.zip",
            "Raw_movement_data.zip",
            "README.md",
        },
        "published_scope": {
            "n_individuals": 17,
            "n_trajectories": 57,
            "n_field_landscapes": 3,
            "height_reference": "source raw GPS height.above.msl, not ground-relative",
            "resource_status": "10-m land cover and landscape configuration; not measured prey biomass",
            "interpolated_rows_are_independent_fixes": False,
        },
    },
    "ducke_bats_2018": {
        "doi": "10.5061/dryad.9rb48c5",
        "role": "independent_measured_food_and_local_bat_distribution",
        "paper": "10.1111/btp.12546",
        "expected": {"Bats_Ducke_data_metadata.xlsx"},
        "published_scope": {
            "n_plots": 49,
            "n_bat_species": 52,
            "n_bat_captures": 1138,
            "net_hours": 7056,
            "resource_status": "measured fruiting plants and light-trapped insects at plots",
            "height_reference": "terrain elevation, NOT individual flight altitude",
            "same_source_as_chrotopterus_2026": False,
        },
    },
}

PASS = "DRYAD_ORIGINAL_PUBLIC_METADATA_VERSION_FILELIST_VERIFIED"


def _official(url):
    if not isinstance(url, str) or not url:
        raise ValueError("DRYAD_URL_EMPTY")
    parsed = urllib.parse.urlparse(urllib.parse.urljoin(API_HOST,url))
    if (parsed.scheme != "https" or parsed.hostname != "datadryad.org"
            or parsed.username or parsed.password or not parsed.path.startswith("/api/v2/")):
        raise ValueError("DRYAD_NON_OFFICIAL_API_PATH")
    return parsed.geturl()


def _entry(doi):
    return API_HOST + "/api/v2/datasets/" + urllib.parse.quote("doi:"+doi, safe="")


def fetch_json(url):
    url=_official(url)
    req=urllib.request.Request(url,headers={"Accept":"application/json","User-Agent":"batter-3d-resource-independent-source-gate/1.0"})
    with urllib.request.urlopen(req,timeout=40) as response:
        if response.status!=200 or _official(response.url)!=url:
            raise RuntimeError("DRYAD_REDIRECT_OR_NON200")
        content=response.read(MAX_JSON_BYTES+1)
    if len(content)>MAX_JSON_BYTES:
        raise RuntimeError("DRYAD_JSON_TOO_LARGE")
    parsed=json.loads(content.decode("utf-8"))
    if not isinstance(parsed,dict):
        raise RuntimeError("DRYAD_EXPECTED_OBJECT")
    return parsed


def _link(obj,key):
    href=obj.get("_links",{}).get(key,{}).get("href")
    return _official(href)


def _file_id(item):
    href=item.get("_links",{}).get("self",{}).get("href")
    path=urllib.parse.urlparse(_official(href)).path
    match=re.fullmatch(r"/api/v2/files/(\d+)",path)
    if not match:
        raise RuntimeError("DRYAD_FILE_LINK_NOT_PUBLIC_ID")
    fid=int(match.group(1))
    top=item.get("id")
    if top is not None and top!=fid:
        raise RuntimeError("DRYAD_FILE_ID_CONFLICT")
    return fid


def audit_one(key,fetch=fetch_json):
    if key not in SOURCES:
        raise ValueError("UNKNOWN_FROZEN_CANDIDATE")
    x=SOURCES[key]
    ds=fetch(_entry(x["doi"]))
    if str(ds.get("identifier","")).lower()!="doi:"+x["doi"].lower():
        raise RuntimeError("DRYAD_PUBLISHER_DOI_MISMATCH")
    version=fetch(_link(ds,"stash:version"))
    file_url=_link(version,"stash:files")
    seen_ids=set()
    seen_paths=set()
    data=[]
    pages=0
    expected_total=None
    while file_url:
        pages+=1
        if pages>MAX_PAGES:
            raise RuntimeError("DRYAD_TOO_MANY_FILE_PAGES")
        listing=fetch(file_url)
        count=listing.get("total")
        if type(count) is not int or count<1:
            raise RuntimeError("DRYAD_TOTAL_FILE_COUNT_INVALID")
        if expected_total is None:
            expected_total=count
        elif count!=expected_total:
            raise RuntimeError("DRYAD_FILE_COUNT_CHANGED")
        batch=listing.get("_embedded",{}).get("stash:files")
        if not isinstance(batch,list):
            raise RuntimeError("DRYAD_NO_PUBLIC_FILE_LIST")
        for item in batch:
            if not isinstance(item,dict):
                raise RuntimeError("DRYAD_FILE_RECORD_NOT_OBJECT")
            fid=_file_id(item)
            name=item.get("path")
            size=item.get("size")
            if not isinstance(name,str) or not name.strip() or type(size) is not int or size<0:
                raise RuntimeError("DRYAD_INVALID_FILENAME_OR_SIZE")
            if fid in seen_ids or name in seen_paths:
                raise RuntimeError("DRYAD_DUPLICATE_ID_OR_PATH")
            seen_ids.add(fid)
            seen_paths.add(name)
            digest_type=item.get("digestType")
            digest=item.get("digest")
            if digest is not None and (not isinstance(digest,str) or len(digest)>128):
                raise RuntimeError("DRYAD_BAD_ORIGINAL_DIGEST")
            data.append({"source_file_name":name,"original_file_id":fid,
                         "size_bytes":size,"digest_type":digest_type,"digest":digest,
                         "original_data_values_read":False})
        nxt=listing.get("_links",{}).get("next",{})
        file_url=_official(nxt["href"]) if isinstance(nxt,dict) and isinstance(nxt.get("href"),str) else None
    if not data or expected_total!=len(data):
        raise RuntimeError("DRYAD_INCOMPLETE_FILE_INVENTORY")
    if set(seen_paths)!=x["expected"]:
        raise RuntimeError("DRYAD_FROZEN_EXPECTED_FILE_INVENTORY_MISMATCH")
    declared=ds.get("storageSize")
    total=sum(item["size_bytes"] for item in data)
    if type(declared) is int and declared!=total:
        raise RuntimeError("DRYAD_STORAGE_SIZE_DISAGREEMENT")
    return {"dataset":key,"status":PASS,"doi":x["doi"],"paper":x["paper"],
            "source_role":x["role"],"original_dataset_version_id":version.get("id"),
            "original_dataset_version_number":version.get("versionNumber"),
            "source_files":sorted(data,key=lambda z:z["source_file_name"]),
            "original_file_count":len(data),"listed_storage_bytes":total,
            "metadata_pages":pages,"original_biological_rows_opened":False,
            "original_gps_or_captures_opened":False,
            "empirical_height_resource_joint_gain":None,
            "published_scope_not_recomputed":x["published_scope"]}


def audit_both(fetch=fetch_json):
    results=[]
    for key in SOURCES:
        try:
            results.append(audit_one(key,fetch))
        except Exception as exc:
            results.append({"dataset":key,"status":"DRYAD_ORIGINAL_METADATA_SOURCE_STOP",
                            "doi":SOURCES[key]["doi"],
                            "reason":(type(exc).__name__+":"+str(exc))[:240],
                            "original_biological_rows_opened":False,
                            "empirical_height_resource_joint_gain":None})
    return {"schema":"batter.independent_3d_and_food_source_registry.v1",
            "cross_dataset_observational_join_allowed":False,
            "results":results,
            "n_metadata_pass":sum(x["status"]==PASS for x in results),
            "n_candidates":len(results),
            "new_empirical_3d_plus_food_gain":None}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="prospective/resource_behavior_sdm/independent_resource_vertical_dryad_metadata_v1.json")
    opts=ap.parse_args()
    obj=audit_both()
    dst=pathlib.Path(opts.out);dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    for item in obj["results"]:
        print("INDEPENDENT_DRYAD_META",item["dataset"],item["status"],flush=True)
        if "reason" in item:
            print("INDEPENDENT_DRYAD_STOP_REASON",item["reason"],flush=True)
    return 0 if obj["n_metadata_pass"]==obj["n_candidates"] else 3

if __name__=="__main__":
    raise SystemExit(main())
