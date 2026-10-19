#!/usr/bin/env python3
"""Validate broader, TITLE+SUBJECT GPS/GSM screen and eight source reference pilots.

The older strict screen counts 182 literal GPS subject tags + 16 excerpt-only
packages. This is a SEPARATE broad screen: 212 GPS/GSM title/subject hints.
Neither establishes actually viable event-level GPS tracking or n populations.
"""
from __future__ import annotations
import hashlib
import json
import re
from collections import Counter,defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
SOURCE=HERE/"MOVEBANK_PUBLISHED_DATAPACKAGES_CENSUS_2026_10_18.json"
TRIAGE=HERE/"MOVEBANK_437_METADATA_SENSOR_TRIAGE_V1.json"
PILOTS=HERE/"REFERENCE_TABLE_EIGHT_CLADE_PILOT_2026_10_19.json"
BLOB="fc69fc259c641f813848a819a4eb736886acba58"
GPS=re.compile(r"(?:^|[^a-z])gps(?:$|[^a-z])|\bgsm\s*telemetry\b|\bglobal\s+positioning\b",re.I)
SAT=re.compile(r"\bargos\b|\bsatellite\s+telemetry\b|\bsatellite[- ]track",re.I)
LIGHT=re.compile(r"\bgeolocator\b|\blight[- ]level\b|\bsolar geolocation\b",re.I)
LOCAL=re.compile(r"home range|territorial|forag|rest|breed|nest|feeding|habitat use|residen|resource selection",re.I)
MIGRATION=re.compile(r"migration|geolocator|light.level",re.I)
EXPECTED_CLASSES={"gps_only":186,"mixed_gps_other":26,"coarse_sat_no_gps":74,
                  "light_no_gps_sat":56,"unresolved_sensor":95}
EXPECTED_LICENSE={"CC0 1.0 Universal":376,"Attribution 4.0 International":27,
                  "Attribution-NonCommercial 4.0 International":34}
PILOT_NAMES=("tapir","elephant","tortoise","deer","gull","vulture","pigeon","bat")
PILOT_N=(82,14,46,135,15,10,35,22)


def read(path:Path)->dict:
    return json.loads(path.read_text(encoding="utf-8"))


def gitblob(path:Path)->str:
    data=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()


def classify(source:dict)->dict:
    src=" ".join([source["title"] or "",*(source["subjects"] or [])])
    gps=bool(GPS.search(src));sat=bool(SAT.search(src))
    light=bool(LIGHT.search(src));local=bool(LOCAL.search(src))
    migration=bool(MIGRATION.search(src))
    cls=("mixed_gps_other" if sat or light else "gps_only") if gps else (
        "coarse_sat_no_gps" if sat else "light_no_gps_sat" if light else "unresolved_sensor")
    rights=source["license"]
    score=(30 if gps else 0)+(8 if rights=="CC0 1.0 Universal" else
           4 if rights=="Attribution 4.0 International" else 0)
    score+=(7 if local else 0)-(2 if migration else 0)
    score-=(10 if sat and not gps else 0)+(15 if light and not gps else 0)
    return dict(doi=source["doi"],uuid=source["uuid"],source_license=rights,
                source_issue_date=source["date"],sensor_metadata_class=cls,
                gps_gsm_keyword=gps,satellite_argos_keyword=sat,
                light_geolocator_keyword=light,ecological_local_context_keyword=local,
                migratory_keyword=migration,priority_for_source_file_audit=score,
                eligible_verified=False,exclusion_reason_if_any=None,
                source_tracking_event_row_count=None,
                source_animal_ID_count_from_main_GPS=None,
                independent_population_count=None,taxon_identity_validated=False)


def check():
    assert gitblob(SOURCE)==BLOB
    source=read(SOURCE);triage=read(TRIAGE);pilot=read(PILOTS)
    assert len(source["records"])==437
    assert source["summary"]["unique_doi"]==437
    assert triage["schema_version"]==1
    assert triage["input_git_blob_sha1"]==BLOB
    assert len(triage["records"])==437
    actual={row["doi"]:row for row in triage["records"]}
    assert len(actual)==437
    classes=Counter();licenses=Counter();pair=defaultdict(Counter)
    n_gps=n_cc0=n_ecology=0
    for row in source["records"]:
        expected=classify(row)
        assert actual[row["doi"]]==expected, "Broader screen changed at DOI "+str(row["doi"])
        cls=expected["sensor_metadata_class"]
        classes[cls]+=1;licenses[expected["source_license"]]+=1
        pair[cls][expected["source_license"]]+=1
        n_gps+=expected["gps_gsm_keyword"]
        n_cc0+=expected["gps_gsm_keyword"] and expected["source_license"]=="CC0 1.0 Universal"
        n_ecology+=expected["gps_gsm_keyword"] and expected["ecological_local_context_keyword"]
    summary=triage["summary"]
    assert classes==EXPECTED_CLASSES==summary["sensor_class_counts"]
    assert licenses==EXPECTED_LICENSE==summary["source_license_counts"]
    assert {k:dict(v) for k,v in pair.items()}==summary["sensor_by_source_rights"]
    assert n_gps==212==summary["explicit_gps_gsm_keyword_packages"]
    assert n_cc0==158==summary["gps_gsm_hints_and_CC0"]
    assert summary["gps_gsm_hints_and_other_rights"]==54
    assert n_ecology==63==summary["gps_metadata_with_local_ecology_keyword"]
    assert summary["distinct_confirmed_primary_populations"]==0
    assert summary["original_animal_tracking_main_files_examined_from_this_registry"]==0
    assert pilot["n_pilot_packages"]==8==summary["pilot_reference_metadata_dois_checked"]
    assert [r["case_name"] for r in pilot["records"]]==list(PILOT_NAMES)
    assert [r["distinct_source_animal_ids"] for r in pilot["records"]]==list(PILOT_N)
    for p in pilot["records"]:
        assert p["dataset_doi"] in actual
        assert p["source_rights"]==actual[p["dataset_doi"]]["source_license"]
        assert p["reference_source_text_length"]>0
        assert p["eligibility_status"]=="reference_verified_only_not_GPS_event_confirmed"
    print("PASS exact original 437 DOI packages, 376 CC0 / 27 BY / 34 BY-NC")
    print("PASS broader TITLE+SUBJECT screen GPS-only 186, mixed 26, coarse 74, light 56, unresolved 95")
    print("PASS 212 broad GPS/GSM hints, 158 CC0, 8 real original reference-CSV pilots")
    print("NOT animal-GPS event eligibility, biological independent n, source session data or empirical ecology")


if __name__=="__main__":
    check()
