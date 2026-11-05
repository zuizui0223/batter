#!/usr/bin/env python3
"""Rebuild/validate 437 Movebank public Datapackage metadata-screening flags.

No internet, no animal GPS events, no taxonomic inference and no new biological
effect computation. The code verifies exactly the public DSpace census Git blob
and an outcome-unopened pilot queue separated from the previous bat studies.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CENSUS = HERE/"MOVEBANK_PUBLISHED_DATAPACKAGES_CENSUS_2026_10_18.json"
TRIAGE = HERE/"MOVEBANK_METADATA_TRIAGE_V1.json"
SOURCE_BLOB = "fc69fc259c641f813848a819a4eb736886acba58"
LICENSE = {
    "CC0 1.0 Universal": 376,
    "Attribution 4.0 International": 27,
    "Attribution-NonCommercial 4.0 International": 34,
}
GPS_FLAGS = {
    "source_keyword_GPS": 182,
    "source_text_mentions_GPS": 16,
    "GPS_undetermined_from_index": 239,
}


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(data)).encode("ascii")+b"\0"+data).hexdigest()


def check() -> None:
    assert blob(CENSUS)==SOURCE_BLOB,"Original complete public DSpace package crawl changed"
    census=json.loads(CENSUS.read_text(encoding="utf-8"))
    triage=json.loads(TRIAGE.read_text(encoding="utf-8"))
    source=census["records"]
    records=triage["records"]
    assert census["summary"]["total_count"]==437
    assert census["summary"]["unique_doi"]==437
    assert census["summary"]["unique_uuid"]==437
    assert len(source)==len(records)==437
    assert triage["schema_version"]==1
    assert triage["source_census_git_blob_sha1"]==SOURCE_BLOB
    assert triage["identity_and_session_eligibility_verified"]==0
    assert triage["source_event_csv_gps_data_verified"]==0
    assert triage["nonbat_empirical_identity_effects_calculated"]==0
    assert len({x["uuid"] for x in source})==437
    assert len({x["doi"] for x in source})==437
    assert len({x["uuid"] for x in records})==437

    counts=Counter()
    flags=Counter()
    pilots=Counter()
    no_bat=0
    for original,derived in zip(source,records):
        assert original["uuid"]==derived["uuid"]
        assert original["doi"].removeprefix("doi:")==derived["doi"]
        assert original["license"]==derived["license"]
        assert original["title"]==derived["source_title"]
        assert original["date"]==derived["published_date"]
        assert isinstance(derived["source_subject_scientific_tokens"],list)
        assert derived["sensor_metadata_screen"] in GPS_FLAGS
        match=bool(any(re.search(r"\bgps\b",s,re.I) for s in original["subjects"]))
        other=bool(re.search("gps",(original.get("title") or "")+" "+(original.get("abstract_prefix") or ""),re.I))
        actual=("source_keyword_GPS" if match else
                "source_text_mentions_GPS" if other else "GPS_undetermined_from_index")
        assert derived["sensor_metadata_screen"]==actual
        assert derived["subject_argos"]==any(re.search(r"\bargos\b",s,re.I) for s in original["subjects"])
        assert derived["subject_light_level"]==any(re.search(r"geolocator|light.level|solar geolocation",s,re.I) for s in original["subjects"])
        counts[derived["license"]]+=1
        flags[actual]+=1
        if derived["pilot_priority"]:
            pilots[derived["pilot_priority"]]+=1
            assert derived["pilot_group"],"A pilot must have explicit source-context label"
            if derived["pilot_group"]!="bat_benchmark_only":
                no_bat+=1
            assert derived["pilot_priority"] in ("pilot","pilot_sensor_unconfirmed","legacy_check_only")
    assert dict(counts)==LICENSE,(counts,LICENSE)
    assert dict(flags)==GPS_FLAGS,(flags,GPS_FLAGS)
    assert triage["license_counts"]==dict(counts)
    for name,expected in GPS_FLAGS.items():
        field={
            "source_keyword_GPS":"gps_subject_signal",
            "source_text_mentions_GPS":"text_only_GPS_signal",
            "GPS_undetermined_from_index":"GPS_undetermined_from_index",
        }[name]
        assert triage[field]==expected
    assert triage["pilot_nonbat_DOI_packages"]==14==no_bat
    assert triage["pilot_legacy_bat_DOI_packages"]==5==pilots["legacy_check_only"]
    assert sum(pilots.values())==19
    assert pilots["pilot_sensor_unconfirmed"]==1
    print("PASS exact 437 unique original public Movebank Datapackage DOI/UUID metadata sources")
    print("PASS GPS metadata screen: 182 indexed GPS, 16 title/abstract-only, 239 unconfirmed")
    print("PASS original package rights: 376 CC0, 27 BY, 34 BY-NC; 14 nonbat pilot candidates, 5 historical bat benchmarks")
    print("NOT VERIFIED: downloaded GPS events, repeated biological n, valid taxonomic strata or empirical individuality/partitioning")


if __name__=="__main__":
    check()
