#!/usr/bin/env python3
"""Validate the WHOLE public Movebank metadata census and format-only seed.

Metadata-only: never claims animal track lengths, physical segregation, true
species diversity, environmental response or any estimated biological effect.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent
CENSUS=ROOT/"MOVEBANK_PUBLISHED_DATAPACKAGES_CENSUS_2026_10_18.json"
PILOT=ROOT/"METADATA_FORMAT_PILOT_SOURCES_V1.json"
RIGHTS={"CC0 1.0 Universal":376,
        "Attribution 4.0 International":27,
        "Attribution-NonCommercial 4.0 International":34}
MODES={"terrestrial_reptile","terrestrial_mammal","flying_bird",
       "flying_seabird","diving_bird","marine_mammal"}


def git_blob(path:Path)->str:
    b=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode("ascii")+b"\0"+b).hexdigest()


def verify()->None:
    c=json.loads(CENSUS.read_text(encoding="utf8"))
    p=json.loads(PILOT.read_text(encoding="utf8"))
    assert c["schema_version"]==p["schema_version"]==1
    r=c["records"]
    assert len(r)==c["summary"]["total_count"]==437
    assert len({x["uuid"] for x in r})==c["summary"]["unique_uuid"]==437
    assert len({x["doi"] for x in r})==c["summary"]["unique_doi"]==437
    assert sum(c["summary"]["license_counts"].values())==437
    assert c["summary"]["license_counts"]==RIGHTS
    assert Counter(x["license"] for x in r)==RIGHTS
    assert c["summary"]["error_count"]==0
    assert len(c["summary"]["page_audit"])==9
    assert sum(x["count"] for x in c["summary"]["page_audit"])==437
    assert sorted(x["page"] for x in c["summary"]["page_audit"])==list(range(9))
    for row in r:
        assert row["entity_type"]=="Datapackage"
        assert row["doi"] and row["doi"].startswith("doi:10.")
        assert row["uuid"] and row["title"] and row["license"]
        assert row["subjects"] is not None
        assert "location_lat" not in row and "individual_local_identifier" not in row
    gps_mentions=sum(bool(re.search(r"\bGPS\b"," ".join(
        [row["title"],*(row["subjects"] or []),row["abstract_prefix"] or ""]),re.I)) for row in r)
    assert gps_mentions==198,("Metadata keyword calculation changed",gps_mentions)
    binomial_candidates=[]
    for row in r:
        labels=[x for x in row["subjects"] if re.match(r"^[A-Z][a-z-]+ [a-z][a-z-]+",x)]
        if labels:
            binomial_candidates.append(labels[0])
    assert len(binomial_candidates)>400
    assert len(set(binomial_candidates))>=200
    print("PASS 437 DOI/UUID records, 376 CC0 / 27 BY / 34 BY-NC source metadata packages")
    print(f"PASS keyword-level GPS mention in {gps_mentions} packages — this is NOT confirmed actual GPS event content")
    print(f"PASS first-binomial metadata guess in {len(binomial_candidates)} packages, "
          f"{len(set(binomial_candidates))} unique strings (NOT validated taxonomic species)")
    assert p["source_catalog_git_blob_sha1"]==git_blob(CENSUS)
    assert p["pilot_count"]==len(p["records"])==15
    by_doi={row["doi"]:row for row in r}
    assert {x["broad_provisional_movement_system"] for x in p["records"]}==MODES
    assert len({x["doi"] for x in p["records"]})==15
    assert len({x["source_license"] for x in p["records"]})==3
    for pilot in p["records"]:
        r=by_doi[pilot["doi"]]
        assert pilot["source_title"]==r["title"]
        assert pilot["source_license"]==r["license"]
        assert pilot["subject_taxon_strings"]==[
            x for x in r["subjects"] if re.match(r"^[A-Z][a-z-]+ [a-z]",x)
        ][:6]
        assert pilot["original_zip_inventory_examined"] is False
        assert pilot["actual_GPS_sensor_confirmed"] is False
        assert pilot["repeated_individual_eligible"] is False
        assert pilot["original_sample_size_verified"] is False
        assert pilot["ecological_contrast_supported"] is False
    print("PASS 15 data-package format/rights checks spanning 6 provisional movement systems and 3 licenses")
    print("STOP inference: no species-level eligibility n, repeated tracks, ecological outcome, or generality test.")


if __name__=="__main__":
    verify()
