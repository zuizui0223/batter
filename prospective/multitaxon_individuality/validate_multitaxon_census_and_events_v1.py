#!/usr/bin/env python3
"""Source-backed public Movebank catalog and cross-taxon event QC gates.

Default CI reads only aggregate JSON receipts and runs synthetic CSV parser tests;
original animal tags/coordinates remain absent from the Git repository.
Optional --events-dir reads operator-owned exact CC0 source CSV bytes, matches
original DSpace MD5, and independently derives NONIDENTIFYING animal counts.
No ecological segregation/persistence hypothesis test is performed here.
"""
from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import hashlib
import io
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CENSUS = HERE / "MOVEBANK_PUBLISHED_DATAPACKAGES_CENSUS_2026_10_18.json"
REFERENCE = HERE / "SEVEN_NONBAT_REFERENCE_DATA_SCREEN_V1.json"
EVENT1 = HERE / "FIRST_NONBAT_EVENT_QC_V1.json"
EVENT2 = HERE / "SECOND_NONBAT_EVENT_QC_V1.json"
DOIS = {
    "10.5441/001/1.44cb3946": "Physeter macrocephalus",
    "10.5441/001/1.sg2s0f7q": "Aptenodytes forsteri",
    "10.5441/001/1.313": "Chelonia mydas",
    "10.5441/001/1.719": "Sus scrofa",
}
# "source MD5" is the publisher-provided bitstream checksum. The public receipts
# previously checked complete EXTRACTED text lengths, not raw source MD5.
EVENT_SOURCES = {
    "ff4e0556-ddd6-49c7-8bb1-d5af9107984a": (
        "10.5441/001/1.44cb3946", "56b58e12f0a89c04173c15ad84390cd0", 1436876),
    "4c1e9a5a-9f31-4f45-9ba7-d95f37e2b85b": (
        "10.5441/001/1.sg2s0f7q", "dd8bf3ebd948840d9061e025c31e0604", 6124879),
    "a7e5ec27-e1e2-4863-a864-603e9bf4b59b": (
        "10.5441/001/1.313", "ae8ff26015b7d826a1d9f3b45f01d5cf", 520491),
    "f6a7d086-a4e3-434f-bbce-6ba9022543e3": (
        "10.5441/001/1.313", "7cc8bd6182182941e792606c3c51b724", 9788265),
    "42323c7f-e101-4d2e-9544-0179d9db121c": (
        "10.5441/001/1.719", "ee6a068fd76aa6963e93063603e557e3", 12107941),
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_snapshot() -> None:
    census, refs, e1, e2 = map(load, (CENSUS, REFERENCE, EVENT1, EVENT2))
    records = census["records"]
    assert census["schema_version"] == 1
    assert len(records) == census["summary"]["total_count"] == 437
    assert len({x["uuid"] for x in records}) == 437
    assert len({x["doi"] for x in records}) == 437
    assert all(x["entity_type"] == "Datapackage" for x in records)
    rights = collections.Counter(x["license"] for x in records)
    assert rights == {
        "CC0 1.0 Universal": 376,
        "Attribution 4.0 International": 27,
        "Attribution-NonCommercial 4.0 International": 34,
    }, rights
    assert rights == census["summary"]["license_counts"]
    assert len(refs["data"]) == 7
    expected_animals = {
        "terrestrial_mammal_deer": 135,
        "terrestrial_mammal_pig": 10,
        "bird_white_stork": 108,
        "reptile_galapagos_tortoise": 46,
        "marine_reptile_green_turtle": 33,
        "marine_mammal_sperm_whale": 17,
        "flightless_bird_emperor_penguin": 8,
    }
    assert {x["label"]: x["distinct_animal_id_count"] for x in refs["data"]} == expected_animals
    assert refs["reference_csv_parser_fix"]["status"] == "confirmed"
    tor = next(x for x in refs["data"] if x["label"] == "reptile_galapagos_tortoise")
    assert tor["reference_row_count"] == 47
    assert tor["reference_species_record_rows"]["Chelonoidis sp. (genus-only)"] == 11
    # Genus-only records DO NOT count as a fourth resolved species.
    assert len([x for x in tor["distinct_taxon_names"] if " " in x]) == 3
    assert len(e1["results"]) == 3 and len(e2["results"]) == 2
    d = {}
    for x in e1["results"]:
        assert not x.get("error")
        assert x["complete_file_length_approximation_verified"] is True
        assert x["rows_with_wrong_field_count"] == 0
        assert x["source_ids_not_persisted"] is True
        d[x["original_event_bitstream_id"]] = (
            x["doi"], x["raw_event_row_count"],
            x["valid_geographic_fixes_after_flag_checks"],
            x["source_unique_individuals_with_valid_fixes"],
            x["source_individuals_100_valid_fixes_7_unique_dates"]
        )
    for x in e2["results"]:
        assert not x.get("error")
        assert x["source_completeness_check"] is True
        assert x["malformed_csv_row_count"] == 0
        assert x["source_ID_values_not_committed"] is True
        d[x["source_original_bitstream_id"]] = (
            x["doi"], x["total_data_records"], x["valid_geographic_fixes"],
            x["n_observed_animals_with_valid_fixes"],
            x["n_animals_at_least_100_fixes_and_7_dates"]
        )
    expected = {
        "ff4e0556-ddd6-49c7-8bb1-d5af9107984a": (7159, 7151, 17, 13),
        "4c1e9a5a-9f31-4f45-9ba7-d95f37e2b85b": (18973, 17856, 8, 8),
        "a7e5ec27-e1e2-4863-a864-603e9bf4b59b": (2616, 2565, 1, 1),
        "f6a7d086-a4e3-434f-bbce-6ba9022543e3": (52846, 52846, 32, 32),
        "42323c7f-e101-4d2e-9544-0179d9db121c": (79165, 79165, 10, 10),
    }
    assert set(d) == set(expected) == set(EVENT_SOURCES)
    for key, (_, n, valid, individuals, exposed) in d.items():
        assert (n, valid, individuals, exposed) == expected[key]
        assert EVENT_SOURCES[key][0] == d[key][0]
    assert sum(v[2] for v in d.values()) == 159583
    # 64 stream-local exposures include separate GPS and Argos turtle file:
    # don't claim 64 globally distinct tracking animals.
    assert sum(v[4] for v in d.values()) == 64
    print("PASS 437 published source packages, CC0=376, BY=27, BY-NC=34; 7 reference CSVs with CR-only tortoise guard")
    print("PASS 5 original event-file aggregates: 159,583 valid fixes, source-file-local n>=100 fixes and >=7 days = 64")
    print("NOT a qualified 64-independent-animal ecological cohort or a biological hypothesis test")


def aggregate_file(path: Path) -> dict:
    """Safe aggregate counts from one source CSV, never returning source IDs."""
    n = 0
    bad = 0
    valid = 0
    animals: dict[tuple[str, str], dict] = {}
    missing_required = None
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        header = list(reader.fieldnames or [])
        canonical = {
            "id": next((x for x in ("individual-local-identifier", "individual-id", "animal-id") if x in header), None),
            "sp": next((x for x in ("individual-taxon-canonical-name", "animal-taxon") if x in header), None),
            "dt": "timestamp" if "timestamp" in header else None,
            "lat": next((x for x in ("location-lat", "location_lat") if x in header), None),
            "lon": next((x for x in ("location-long", "location_long") if x in header), None)
        }
        if any(canonical[k] is None for k in ("id", "dt", "lat", "lon")):
            raise ValueError("Required event keys missing: " + str(canonical))
        for row in reader:
            n += 1
            if None in row:  # malformed row surplus fields
                bad += 1
                continue
            animal = row[canonical["id"]]
            date = (row[canonical["dt"]] or "")[:10]
            sp = row[canonical["sp"]] if canonical["sp"] else "unknown"
            if not animal or len(date) != 10:
                continue
            try:
                dt.date.fromisoformat(date)
                lat = float(row[canonical["lat"]])
                lon = float(row[canonical["lon"]])
            except (ValueError, TypeError):
                continue
            if not -90 <= lat <= 90 or not -180 <= lon <= 180:
                continue
            if (row.get("visible") or "").casefold() in ("false", "0"):
                continue
            if (row.get("manually-marked-outlier") or "").casefold() in ("true", "1"):
                continue
            animal_key = (sp, animal)
            stats = animals.setdefault(animal_key, {"n": 0, "days": set()})
            stats["n"] += 1
            stats["days"].add(date)
            valid += 1
    return {
        "raw_rows": n, "malformed_rows": bad, "valid_coordinates": valid,
        "source_file_local_animals": len(animals),
        "n_100_fix_7_day": sum(d["n"] >= 100 and len(d["days"]) >= 7 for d in animals.values()),
        "n_500_fix_14_day": sum(d["n"] >= 500 and len(d["days"]) >= 14 for d in animals.values()),
    }


def test_parser() -> None:
    import tempfile
    # CR-only input; one bat has two fix days but no seven-day support.
    source = (
        "individual-local-identifier,timestamp,location-lat,location-long,visible,manually-marked-outlier,notes\r"
        '001,2026-01-01 10:00:00,1.0,2.0,true,false,"a,quoted,field"\r'
        '001,2026-01-02 10:00:00,1.1,2.1,true,false,"other"\r'
        '002,2026-01-01 10:00:00,1.2,2.2,false,false,"excluded"\r'
        '002,2026-01-02 10:00:00,1.2,2.2,true,true,"excluded"\r'
    )
    with tempfile.TemporaryDirectory() as p:
        dest = Path(p) / "test.csv"
        dest.write_bytes(source.encode("utf-8"))
        got = aggregate_file(dest)
    assert got == {
        "raw_rows": 4, "malformed_rows": 0, "valid_coordinates": 2,
        "source_file_local_animals": 1, "n_100_fix_7_day": 0,
        "n_500_fix_14_day": 0
    }, got
    print("PASS synthetic CR-only CSV, commas in quotes, exclusion flags and no ID output")


def optional_raw_replay(folder: Path) -> None:
    for sid, (doi, md5_expected, size_expected) in EVENT_SOURCES.items():
        f = folder / (sid + ".csv")
        if not f.is_file():
            raise FileNotFoundError(f"Missing original CC0 event source: {sid}.csv")
        if f.stat().st_size != size_expected:
            raise ValueError(f"Original event source size mismatch: {sid}")
        h = hashlib.md5()
        with f.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1048576), b""):
                h.update(chunk)
        if h.hexdigest() != md5_expected:
            raise ValueError(f"Original MD5 mismatch: {sid}")
        result = aggregate_file(f)
        print(json.dumps({"doi": doi, "source_bitstream": sid, "aggregate": result}))
    print("PASS five exact original event source MD5s; no individual IDs or original coordinates written")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--events-dir", type=Path,
                    help="Optional folder with exact original CC0 event files as <bitstream_uuid>.csv")
    args = ap.parse_args()
    test_parser()
    validate_snapshot()
    if args.events_dir is not None:
        optional_raw_replay(args.events_dir)
