#!/usr/bin/env python3
"""Outcome-blind structural audit for frozen Myotis Zenodo files."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import pathlib
import statistics
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
OUTJ = HERE / "MYOTIS_STRUCTURE_RESULT_V1.json"
OUTM = HERE / "MYOTIS_STRUCTURE_RESULT_V1.md"

BASE = "https://zenodo.org/records/4946256/files/"
FILES = {
    "control1": {
        "name": "control_experiment__1_data.txt",
        "md5": "db9c7b38579435d9f63ef6b4973d6825",
    },
    "flighttime": {
        "name": "dataset_tc.csv",
        "md5": "c6b1e0310d98c364e14a79dae4a27360",
    },
}


def download(name):
    url = BASE + name + "?download=1"
    req = urllib.request.Request(
        url, headers={"User-Agent": "batter-myotis-structure-audit/1.0"}
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        return response.read()


def md5(data):
    return hashlib.md5(data).hexdigest()


def control_treatment(row):
    nl = float(row["noiselevel"])
    tr = row["transducer"].strip()
    if nl == 20:
        return "no_noise"
    if nl == 94 and tr == "h":
        return "noise_target"
    if nl == 94 and tr == "a":
        return "noise_above"
    if nl == 94 and tr == "s":
        return "noise_side"
    return "ANOMALY"


def audit_control(data):
    text = data.decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(text), delimiter="\t"))
    required = [
        "sl_rms",
        "transducer",
        "noiselevel",
        "animal",
        "trialno",
        "nl_rec",
        "date",
    ]
    if not rows:
        raise RuntimeError("control1 file is empty")
    if list(rows[0].keys()) != required:
        raise RuntimeError(f"unexpected control header: {list(rows[0].keys())}")

    animals = sorted({row["animal"] for row in rows})
    dates = sorted({row["date"] for row in rows})
    treatments = sorted({control_treatment(row) for row in rows})
    anomaly_rows = sum(control_treatment(row) == "ANOMALY" for row in rows)

    trial_call_counts = {}
    cell_trials = {}
    for row in rows:
        condition = control_treatment(row)
        trial_key = (
            row["animal"],
            row["date"],
            condition,
            row["trialno"],
        )
        trial_call_counts[trial_key] = trial_call_counts.get(trial_key, 0) + 1
        cell_key = (row["animal"], row["date"], condition)
        cell_trials.setdefault(cell_key, set()).add(row["trialno"])

    call_counts = list(trial_call_counts.values())
    required_conditions = [
        "no_noise",
        "noise_target",
        "noise_above",
        "noise_side",
    ]
    required_cell_counts = [
        len(cell_trials.get((animal, date, condition), set()))
        for animal in animals
        for date in dates
        for condition in required_conditions
    ]

    expected_cells = len(animals) * len(dates) * len(required_conditions)
    observed_cells = sum(x > 0 for x in required_cell_counts)

    passed = (
        len(animals) == 5
        and len(dates) == 3
        and anomaly_rows == 0
        and observed_cells == expected_cells
        and required_cell_counts
        and min(required_cell_counts) >= 4
        and call_counts
        and min(call_counts) == 5
        and max(call_counts) == 5
    )

    return {
        "header": required,
        "n_rows": len(rows),
        "animals": animals,
        "n_animals": len(animals),
        "dates": dates,
        "n_dates": len(dates),
        "treatments": treatments,
        "anomaly_rows": anomaly_rows,
        "trial_count_per_required_cell": {
            "min": min(required_cell_counts) if required_cell_counts else None,
            "median": (
                statistics.median(required_cell_counts)
                if required_cell_counts
                else None
            ),
            "max": max(required_cell_counts) if required_cell_counts else None,
        },
        "calls_per_trial": {
            "min": min(call_counts) if call_counts else None,
            "median": statistics.median(call_counts) if call_counts else None,
            "max": max(call_counts) if call_counts else None,
        },
        "required_cells": expected_cells,
        "observed_required_cells": observed_cells,
        "verdict": (
            "PASS_CONTROL1_STRUCTURE"
            if passed
            else "STOP_CONTROL1_STRUCTURE"
        ),
    }


def audit_flight(data):
    text = data.decode("utf-8-sig")
    dialect = csv.Sniffer().sniff(text[:4096])
    rows = list(csv.DictReader(io.StringIO(text), dialect=dialect))
    if not rows:
        raise RuntimeError("dataset_tc file is empty")

    header = list(rows[0].keys())
    required = {"bat_num", "noise_sphere", "time_flight_s", "daynumber"}
    missing = sorted(required - set(header))

    bats = sorted({row["bat_num"] for row in rows})
    noise = sorted(
        {row["noise_sphere"] for row in rows},
        key=lambda x: float(x),
    )
    days = sorted(
        {row["daynumber"] for row in rows},
        key=lambda x: float(x),
    )

    counts = {}
    daysets = {}
    invalid_time = 0
    for row in rows:
        try:
            value = float(row["time_flight_s"])
            if not (value > 0):
                invalid_time += 1
        except Exception:
            invalid_time += 1

        key = (row["bat_num"], row["noise_sphere"])
        counts[key] = counts.get(key, 0) + 1
        daysets.setdefault(key, set()).add(row["daynumber"])

    common = []
    for bat in bats:
        if all(
            counts.get((bat, condition), 0) >= 5
            and len(daysets.get((bat, condition), set())) >= 2
            for condition in noise
        ):
            common.append(bat)

    passed = (
        not missing
        and len(noise) == 5
        and len(common) >= 3
        and invalid_time == 0
    )

    return {
        "header": header,
        "n_rows": len(rows),
        "bats": bats,
        "n_bats": len(bats),
        "noise_levels": noise,
        "n_noise_levels": len(noise),
        "days": days,
        "common_support_bats": common,
        "n_common_support_bats": len(common),
        "invalid_or_nonpositive_time_rows": invalid_time,
        "cell_trial_counts": {
            f"{bat}|{condition}": counts.get((bat, condition), 0)
            for bat in bats
            for condition in noise
        },
        "cell_day_counts": {
            f"{bat}|{condition}": len(
                daysets.get((bat, condition), set())
            )
            for bat in bats
            for condition in noise
        },
        "verdict": (
            "PASS_FLIGHTTIME_STRUCTURE"
            if passed
            else "STOP_FLIGHTTIME_STRUCTURE"
        ),
    }


def main():
    result = {"source_record": 4946256, "files": {}}
    raw = {}

    for key, spec in FILES.items():
        data = download(spec["name"])
        checksum = md5(data)
        if checksum != spec["md5"]:
            raise SystemExit(
                f"STOP checksum {spec['name']}: {checksum}"
            )
        raw[key] = data
        result["files"][key] = {
            "name": spec["name"],
            "md5": checksum,
            "bytes": len(data),
        }

    result["control1"] = audit_control(raw["control1"])
    result["flighttime"] = audit_flight(raw["flighttime"])

    OUTJ.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    )

    lines = [
        "# Myotis masking structural audit result v1",
        "",
        "## Source",
        "",
        "- Zenodo record: 4946256",
        "- frozen checksums: PASS",
        "",
        "## Control experiment 1",
        "",
        f"- animals: {result['control1']['animals']}",
        f"- dates: {result['control1']['dates']}",
        f"- treatments: {result['control1']['treatments']}",
        (
            "- trials/cell min/median/max: "
            + str(result["control1"]["trial_count_per_required_cell"])
        ),
        (
            "- calls/trial min/median/max: "
            + str(result["control1"]["calls_per_trial"])
        ),
        f"- verdict: **{result['control1']['verdict']}**",
        "",
        "## Main-experiment flight time",
        "",
        f"- bats: {result['flighttime']['bats']}",
        f"- source noise conditions: {result['flighttime']['noise_levels']}",
        (
            "- common-support bats: "
            + str(result["flighttime"]["common_support_bats"])
        ),
        (
            "- common-support n: "
            + str(result["flighttime"]["n_common_support_bats"])
        ),
        (
            "- invalid/nonpositive flight-time rows: "
            + str(result["flighttime"]["invalid_or_nonpositive_time_rows"])
        ),
        f"- verdict: **{result['flighttime']['verdict']}**",
        "",
        "## Boundary",
        "",
        "No source-level or flight-time values are reported here.",
    ]
    OUTM.write_text("\n".join(lines) + "\n")
    print(OUTM.read_text())


if __name__ == "__main__":
    main()
