#!/usr/bin/env python3
"""Source-reference-qualified lunar common-support gate, no numerical heights.

This code may access GPS native height *presence*, but never parses the numerical
height outcome. The resulting PASS establishes matched-data eligibility only.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import hashlib
import io
import json
import math
from pathlib import Path
import urllib.request

from prospective.lunar_3d.lunar_source_gate_v1 import (
    OUTLIERS, as_utc, canon, classify_fix, local_solar_night, truthy
)

CONTRACTS = (
    "contract/phyllostomus_replication_v1.json",
    "contract/hypsignathus_replication_v1.json",
)
MIN_FIX_NIGHT = 8
MIN_TOTAL_PER_EXPOSURE = 20
MIN_NIGHTS_PER_EXPOSURE = 2
MIN_MATCHED_ANIMALS = 5
CELL_DEG = 0.05
CLOCK_HOURS = 2
MAX_GAP_DAYS = 45

def get_csv(source):
    req = urllib.request.Request(source["url"], headers={"User-Agent": "batter-lunar-source-admission-v3/1.0"})
    with urllib.request.urlopen(req, timeout=240) as r:
        raw = r.read()
    md5 = hashlib.md5(raw).hexdigest()
    if len(raw) != source["size_bytes"] or md5 != source["md5"]:
        raise RuntimeError("source length / md5 mismatch")
    rd = csv.DictReader(io.StringIO(raw.decode("utf-8-sig", errors="replace"), newline=""))
    if len({canon(h) for h in rd.fieldnames or []}) != len(rd.fieldnames or []):
        raise RuntimeError("source header canonicalization collision")
    return [{canon(k): v for k,v in row.items() if k is not None} for row in rd], [canon(h) for h in rd.fieldnames or []]

def build_reference(refs):
    temp = defaultdict(lambda: {"sites": set(), "manipulations": set(), "tags": set()})
    for row in refs:
        animal = str(row.get("animal_id") or row.get("individual_local_identifier") or row.get("individual_id") or "").strip()
        if not animal:
            continue
        site = str(row.get("study_site") or "").strip()
        if site:
            temp[animal]["sites"].add(site)
        manipulation = str(row.get("manipulation_type") or "").strip().lower()
        if manipulation not in ("", "none"):
            temp[animal]["manipulations"].add(manipulation)
        tag = str(row.get("tag_id") or row.get("tag_local_identifier") or "").strip()
        if tag:
            temp[animal]["tags"].add(tag)
    results = {}
    for animal, v in temp.items():
        ok = len(v["sites"]) == 1 and not v["manipulations"]
        results[animal] = {
            "ok": ok, "site": next(iter(v["sites"])) if len(v["sites"]) == 1 else None,
            "mixed_reference_tags": len(v["tags"]) > 1,
            "no_tag_reference": not v["tags"],
            "manipulated": bool(v["manipulations"]),
            "ambiguous_or_missing_site": len(v["sites"]) != 1
        }
    return results

def match_counts(groups):
    qualified = []
    for key, exposures in groups.items():
        viable = {}
        for exp in ("bright", "dark"):
            ns = {night: n for night,n in exposures[exp].items() if n >= MIN_FIX_NIGHT}
            if len(ns) < MIN_NIGHTS_PER_EXPOSURE or sum(ns.values()) < MIN_TOTAL_PER_EXPOSURE:
                break
            viable[exp] = ns
        if len(viable) != 2:
            continue
        min_gap = min(abs((datetime.fromisoformat(x) - datetime.fromisoformat(y)).days)
                      for x in viable["bright"] for y in viable["dark"])
        if min_gap > MAX_GAP_DAYS:
            continue
        qualified.append((key, min_gap, len(viable["bright"]), len(viable["dark"])))
    return qualified

def run_source(contract, gps_rows, gps_headers, refs, ref_headers):
    height = contract["vertical"]["field"]
    if height not in gps_headers:
        return {"source_doi": contract["repository_doi"], "status": "missing_native_height_presence", "height_values_opened": False}
    refmap = build_reference(refs)
    groups = defaultdict(lambda: {"bright": Counter(), "dark": Counter()})
    cache = {}
    reasons = Counter()
    retained_ids = set()
    explicit = any(f in gps_headers for f in OUTLIERS)
    gps_tag_field = next((f for f in ("tag_id", "tag_local_identifier") if f in gps_headers), None)
    seen_record_tags = defaultdict(set)
    for row in gps_rows:
        animal = str(row.get("individual_local_identifier") or row.get("animal_id") or row.get("individual_id") or "").strip()
        if not animal:
            reasons["missing_animal"] += 1
            continue
        meta = refmap.get(animal)
        if not meta:
            reasons["unmapped_animal"] += 1
            continue
        if meta["manipulated"]:
            reasons["manipulated_reference"] += 1
            continue
        if meta["ambiguous_or_missing_site"]:
            reasons["invalid_reference_site"] += 1
            continue
        if explicit and any(truthy(row.get(f)) for f in OUTLIERS):
            reasons["source_outlier"] += 1
            continue
        if not explicit and "visible" in row and str(row.get("visible") or "").strip() and not truthy(row["visible"]):
            reasons["source_outlier"] += 1
            continue
        if not str(row.get(height) or "").strip():
            reasons["missing_height_presence"] += 1
            continue
        try:
            lon, lat = float(row["location_long"]), float(row["location_lat"])
            if not (math.isfinite(lon) and math.isfinite(lat) and -180<=lon<=180 and -90<=lat<=90):
                raise ValueError("invalid location")
            dt = as_utc(row["timestamp"])
        except (KeyError, TypeError, ValueError, OverflowError):
            reasons["invalid_time_or_xy"] += 1
            continue
        exp = classify_fix(dt, lat, lon, cache)
        if exp not in ("bright", "dark"):
            reasons["non_target_exposure_or_twilight"] += 1
            continue
        night = local_solar_night(dt, lon)
        year = night[:4]
        solar_hour = (dt + timedelta(hours=lon/15)).hour
        cell = (math.floor(lat/CELL_DEG), math.floor(lon/CELL_DEG))
        key = (animal, meta["site"], year, *cell, solar_hour//CLOCK_HOURS)
        groups[key][exp][night] += 1
        retained_ids.add(animal)
        tag = str(row.get(gps_tag_field) or "").strip() if gps_tag_field else ""
        if tag:
            seen_record_tags[(animal, year)].add(tag)
        reasons["valid_target_exposure"] += 1
    eligible = match_counts(groups)
    ids = {k[0] for k, *_ in eligible}
    multi_ref_tags = sum(refmap[x]["mixed_reference_tags"] for x in ids)
    missing_ref_tags = sum(refmap[x]["no_tag_reference"] for x in ids)
    mixed_row_tags = sum(len(tagset)>1 and k[0] in ids for k,tagset in seen_record_tags.items())
    max_independent_nights_per_class = max((min(nb,nd) for _,_,nb,nd in eligible),default=0)
    # NO underlying animal IDs or fine spatial sites are exported.
    return {
        "source_doi": contract["repository_doi"],
        "taxon": contract["taxon"],
        "source_md5": contract["source"]["gps"]["md5"],
        "reference_md5": contract["source"]["reference"]["md5"],
        "native_vertical_field": height,
        "native_vertical_semantics": contract["vertical"].get("semantics"),
        "height_values_opened": False,
        "reference_individuals": len(refmap),
        "admitted_individuals_with_target_exposure": len(retained_ids),
        "reference_manipulated_individuals": sum(v["manipulated"] for v in refmap.values()),
        "reference_invalid_site_individuals": sum(v["ambiguous_or_missing_site"] for v in refmap.values()),
        "eligible_matched_strata": len(eligible),
        "eligible_matched_individuals": len(ids),
        "max_nights_per_exposure_in_eligible_stratum": max_independent_nights_per_class,
        "eligible_individuals_with_multiple_reference_tags": multi_ref_tags,
        "eligible_individuals_missing_reference_tags": missing_ref_tags,
        "eligible_individual_years_with_multiple_gps_tags": mixed_row_tags,
        "gps_field_has_explicit_tag_id": bool(gps_tag_field),
        "gps_accuracy_related_fields": sorted(
            f for f in gps_headers if any(x in f for x in ("accuracy","hdop","vdop","dop","satellites","geoid","error_estimate"))
        ),
        "reference_tag_related_fields": sorted(
            f for f in ref_headers if ("tag" in f or "deploy" in f)
        ),
        "excluded_source_row_reasons": dict(sorted(reasons.items())),
        "status": "source_admitted_for_unvalidated_raw_altitude" if len(ids)>=MIN_MATCHED_ANIMALS else "source_stop_insufficient_matched_individuals",
    }

def main():
    outputs = []
    for p in CONTRACTS:
        contract = json.loads(Path(p).read_text(encoding="utf-8"))
        gps, gh = get_csv(contract["source"]["gps"])
        refs, rh = get_csv(contract["source"]["reference"])
        outputs.append(run_source(contract,gps,gh,refs,rh))
    payload = {"analysis": "lunar_source_v3_reference_and_night_admission",
               "height_values_opened": False, "results": outputs}
    out=Path("results/lunar_3d_source_admission_v3.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(payload,indent=2,sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
