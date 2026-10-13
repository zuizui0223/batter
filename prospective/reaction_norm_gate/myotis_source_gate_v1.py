#!/usr/bin/env python3
"""Post-publication Myotis data acquisition gate and *exploratory* scalar contrast forecast.

No dataset is bundled or downloaded. Inventory scans ZIP metadata/CSV headers only.
Analyse requires independently verified, manually mapped canonical CSV.
This cannot estimate ultrasound latency, individual 3-D trajectories, or causal effects.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import math
import posixpath
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean


class SourceGateError(ValueError):
    """A mandatory source eligibility or provenance condition was not met."""


MOVING = {
    (0.08, 0.5): "easy", (0.08, 1.0): "easy", (0.08, 1.3): "easy",
    (0.24, 0.5): "easy", (0.24, 1.0): "difficult", (0.24, 1.5): "difficult",
}
COLS = ("bat_id", "session_date", "trial_id", "distance_m", "speed_m_s",
        "buzz_ii_valid", "buzz_ii_ms")
SHRINK = 0.5  # fixed before any trial-level outcomes from external data are opened
MAX_ARCHIVE_FILES = 4000
MAX_UNCOMPRESSED_BYTES = 3_000_000_000
MAX_CSV_HEADER_BYTES = 65536


def _safe_archive_name(name: str) -> bool:
    return (bool(name) and not name.startswith(("/", "\\"))
            and "\\" not in name and ":" not in name
            and all(p not in ("", ".", "..") for p in name.rstrip("/").split("/")))


def _csv_columns_binary(handle):
    line = handle.readline(MAX_CSV_HEADER_BYTES + 1)
    if len(line) > MAX_CSV_HEADER_BYTES:
        return [], "HEADER_TOO_LONG"
    try:
        s = line.decode("utf-8-sig")
    except UnicodeDecodeError:
        return [], "HEADER_NOT_UTF8_INSPECT_MANUALLY"
    delim = max((",", ";", "\t"), key=s.count)
    if s.count(delim) < 1:
        return [], "DELIMITER_UNKNOWN"
    header = next(csv.reader([s], delimiter=delim), [])
    return [v.strip()[:200] for v in header[:150]], "UTF8_HEADER_ONLY"


def audit_archive(archive: Path | str) -> dict:
    archive = Path(archive)
    if not archive.is_file():
        raise SourceGateError("ZIP file not found")
    try:
        z = zipfile.ZipFile(archive)
    except (zipfile.BadZipFile, OSError) as e:
        raise SourceGateError("Not a readable ZIP archive") from e
    with z:
        infos = [x for x in z.infolist() if not x.is_dir()]
        if not infos or len(infos) > MAX_ARCHIVE_FILES:
            raise SourceGateError("Unsafe/empty archive file count")
        total = sum(i.file_size for i in infos)
        if total > MAX_UNCOMPRESSED_BYTES:
            raise SourceGateError("Archive exceeds declared uncompressed scan budget")
        results = []
        for info in infos:
            if not _safe_archive_name(info.filename):
                raise SourceGateError("Unsafe ZIP path: " + info.filename[:160])
            ext = posixpath.splitext(info.filename)[1].lower()
            record = {"path": info.filename, "uncompressed_bytes": info.file_size,
                      "crc32": f"{info.CRC:08x}", "extension": ext}
            if ext in (".csv", ".tsv") and info.file_size:
                with z.open(info, "r") as h:
                    columns, status = _csv_columns_binary(h)
                record.update({"columns": columns, "header_status": status})
            elif ext in (".mat", ".rds", ".rdata", ".xlsx", ".xls", ".h5", ".hdf5"):
                record["header_status"] = "BINARY_SCHEMA_NOT_INSPECTED"
            results.append(record)
    return {
        "archive_type": "zip", "sha256": hashlib.sha256(archive.read_bytes()).hexdigest()
        if archive.stat().st_size <= 100_000_000 else "SKIPPED_ZIP_SHA_ARCHIVE_OVER_100MB",
        "file_count": len(results), "total_uncompressed_bytes": total,
        "raw_data_schema_status": "HOLD_NOT_MAPPED",
        "metadata_only": True,
        "outcome_values_accessed": False,
        "note": "Headers and filenames only; not approval for bat-level data analysis. Map source variables and confirm ID, date, device, challenge and missingness.",
        "files": results,
    }


def _as_date(s: str) -> dt.date:
    try:
        d = dt.date.fromisoformat(s)
        if d.isoformat() != s:
            raise ValueError(s)
        return d
    except ValueError as e:
        raise SourceGateError("session_date must be ISO YYYY-MM-DD") from e


def _number(s: str, field: str) -> float:
    try:
        x = float(s)
    except (TypeError, ValueError) as e:
        raise SourceGateError(f"Invalid numeric {field}: {s!r}") from e
    if not math.isfinite(x):
        raise SourceGateError(f"Nonfinite numeric {field}")
    return x


def _classify(distance: str, speed: str) -> tuple[str, tuple[float, float]]:
    d, v = _number(distance, "distance_m"), _number(speed, "speed_m_s")
    if d == 0 and v == 0:
        return "stationary", (0., 0.)
    ds = (round(d, 3), round(v, 3))
    if abs(d-ds[0]) > 1e-5 or abs(v-ds[1]) > 1e-5 or ds not in MOVING:
        raise SourceGateError("Condition not one of six paper motion regimes (m, m/s): " + str((d, v)))
    return MOVING[ds], ds



# Exact 2x2 factorial subset of the six published moving-target regimes.
# This decomposes a four-cell response surface; it is *not* a bat flight law.
FACTORIAL_2X2_CELLS = (
    (0.08, 0.5), (0.08, 1.0), (0.24, 0.5), (0.24, 1.0),
)
FACTORIAL_AXES = ("speed", "distance", "speed_x_distance")


def factorial_2x2_coefficients(four_cells: dict) -> dict:
    """Effect-coded coefficients from fixed displacement × speed support.

    Let A=(.08,.5), B=(.08,1.0), C=(.24,.5), D=(.24,1.0).
    With speed x and displacement z both coded -1/+1, cell means obey
    mean + b_speed*x + b_distance*z + b_interaction*x*z.
    The four coefficients are just an invertible descriptive re-expression.
    """
    missing = set(FACTORIAL_2X2_CELLS) - set(four_cells)
    if missing:
        raise SourceGateError(f"Factorial stimulus cell(s) not observed: {sorted(missing)}")
    a, b, c, d = (four_cells[key] for key in FACTORIAL_2X2_CELLS)
    if not all(isinstance(v, (float, int)) and math.isfinite(v)
               for v in (a, b, c, d)):
        raise SourceGateError("Four factorial cell means must be finite")
    return {
        "mean": (a + b + c + d) / 4,
        "speed": (-a + b - c + d) / 4,
        "distance": (-a - b + c + d) / 4,
        "speed_x_distance": (a - b - c + d) / 4,
    }


def analyse_canonical(csv_path: Path | str) -> dict:
    """Deterministic contrast forecasting. Distinct bats, not trials, are biological n.

    Assumes humans independently verified each canonical column against the
    author's dataset. Four physical bats must have matched days 1-4 and each
    original within-day regime. No post hoc dropping of bat days/conditions.
    """
    path = Path(csv_path)
    if not path.is_file():
        raise SourceGateError("Canonical file not found")
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    trials = set()
    exposure = defaultdict(set)
    all_rows = 0
    invalid_count = 0
    valid_count = 0
    bats = set()
    with path.open("r", newline="", encoding="utf-8-sig") as h:
        reader = csv.DictReader(h)
        if not reader.fieldnames or not set(COLS).issubset(set(reader.fieldnames)):
            raise SourceGateError("Canonical schema absent. Required: " + ", ".join(COLS))
        for row in reader:
            all_rows += 1
            bat = (row.get("bat_id") or "").strip()
            trial = (row.get("trial_id") or "").strip()
            if not bat or not trial:
                raise SourceGateError("Missing physical bat or trial ID")
            date = _as_date((row.get("session_date") or "").strip())
            key = (bat, date, trial)
            if key in trials:
                raise SourceGateError("Duplicate trial per physical bat and date")
            trials.add(key)
            bats.add(bat)
            category, condition = _classify(row.get("distance_m"), row.get("speed_m_s"))
            exposure[(bat, date)].add(condition)
            valid = (row.get("buzz_ii_valid") or "").strip()
            if valid not in ("0", "1"):
                raise SourceGateError("buzz_ii_valid must be explicitly 0 or 1")
            measured = (row.get("buzz_ii_ms") or "").strip()
            if valid == "0":
                if measured:
                    raise SourceGateError("Invalid buzz is incorrectly assigned a numeric value")
                invalid_count += 1
                continue
            if not measured:
                raise SourceGateError("Valid buzz must have observed duration")
            duration = _number(measured, "buzz_ii_ms")
            if duration <= 0:
                raise SourceGateError("Measured buzz II duration must be positive, not filled zero")
            valid_count += 1
            if category != "stationary":
                data[bat][date][condition].append(math.log1p(duration))
    if len(bats) != 4:
        raise SourceGateError(f"Need exactly four matched physical bats; got {len(bats)}")

    dates = {}
    for bat in sorted(bats):
        bdates = sorted(date for b, date in exposure if b == bat)
        if len(bdates) < 4:
            raise SourceGateError(f"{bat}: fewer than 4 distinct dated sessions")
        dates[bat] = bdates
        for day in bdates[:4]:
            full = set(MOVING)
            missing = full - exposure[(bat, day)]
            if missing:
                raise SourceGateError(f"{bat} {day}: missing original treatment(s) {sorted(missing)}")
            # Each physical treatment must have enough actual valid buzzes.
            # Pooling all "easy" or "difficult" rows can reweight treatments
            # after differential trial dropout, distorting personal effects.
            for regime in MOVING:
                n = len(data[bat][day][regime])
                if n < 2:
                    raise SourceGateError(
                        f"{bat} {day}: <2 valid Buzz II trials in physical regime "
                        f"{regime} ({n})")

    def delta(bat, date):
        # Two-stage equal-treatment estimand: first average each published
        # regime's valid trials, then weight the 4 easy and 2 difficult
        # regimes equally WITHIN their fixed classes.
        by_treatment = {
            condition: mean(data[bat][date][condition]) for condition in MOVING
        }
        difficult = mean(by_treatment[c] for c, level in MOVING.items()
                         if level == "difficult")
        easy = mean(by_treatment[c] for c, level in MOVING.items()
                    if level == "easy")
        return difficult - easy

    train = {b: mean(delta(b, d) for d in dates[b][:2]) for b in sorted(bats)}
    pooled = mean(train.values())  # equal-bat training, no future data
    forecasts = []
    by_bat = []
    for bat in sorted(bats):
        own = train[bat]
        pred_shared = pooled
        pred_personal = pooled + SHRINK*(own - pooled)
        tmp = []
        for day in dates[bat][2:4]:
            actual = delta(bat, day)
            item = {"date": day.isoformat(), "observed_log_contrast": actual,
                    "shared_prediction": pred_shared, "personal_prediction": pred_personal,
                    "mse_shared": (actual-pred_shared)**2,
                    "mse_personal": (actual-pred_personal)**2}
            tmp.append(item)
            forecasts.append({"bat_id": bat, **item})
        by_bat.append({"bat_id": bat, "train_beta": own,
                       "train_personal_deviation": own-pooled,
                       "n_test_days": len(tmp),
                       "mse_shared": mean(t["mse_shared"] for t in tmp),
                       "mse_personal": mean(t["mse_personal"] for t in tmp),
                       "forecast_gain": mean(t["mse_shared"]-t["mse_personal"] for t in tmp)})
    # A pre-original-outcome *secondary* readout: isolate speed and distance
    # contrasts with a physical 2x2 subset rather than conflate them in a
    # broad four-easy versus two-difficult summary. Main endpoint unchanged.
    def four_cell_coeff(bat, date):
        return factorial_2x2_coefficients({
            cell: mean(data[bat][date][cell]) for cell in FACTORIAL_2X2_CELLS
        })

    secondary_train = {
        bat: {axis: mean(four_cell_coeff(bat, day)[axis]
                         for day in dates[bat][:2])
              for axis in FACTORIAL_AXES}
        for bat in sorted(bats)
    }
    secondary_group = {
        axis: mean(secondary_train[bat][axis] for bat in sorted(bats))
        for axis in FACTORIAL_AXES
    }
    secondary_bats = []
    secondary_heldout = []
    for bat in sorted(bats):
        personal = {
            axis: secondary_group[axis] + SHRINK * (
                secondary_train[bat][axis] - secondary_group[axis])
            for axis in FACTORIAL_AXES
        }
        bat_days = []
        for day in dates[bat][2:4]:
            observed = four_cell_coeff(bat, day)
            mse_group = mean((observed[axis] - secondary_group[axis])**2
                             for axis in FACTORIAL_AXES)
            mse_personal = mean((observed[axis] - personal[axis])**2
                                for axis in FACTORIAL_AXES)
            row = {
                "bat_id": bat, "date": day.isoformat(),
                "observed_coefficients": {axis: observed[axis] for axis in FACTORIAL_AXES},
                "shared_prediction": dict(secondary_group),
                "personal_prediction": personal,
                "mse_group": mse_group, "mse_personal": mse_personal,
            }
            bat_days.append(row)
            secondary_heldout.append(row)
        secondary_bats.append({
            "bat_id": bat, "train_coefficients": secondary_train[bat],
            "n_test_days": len(bat_days),
            "mse_group": mean(r["mse_group"] for r in bat_days),
            "mse_personal": mean(r["mse_personal"] for r in bat_days),
            "forecast_gain": mean(r["mse_group"]-r["mse_personal"] for r in bat_days),
        })
    secondary_result = {
        "scope": "SECONDARY_EXPLORATORY_PHYSICAL_2X2_NO_NEW_P_VALUES",
        "physical_cells": [list(v) for v in FACTORIAL_2X2_CELLS],
        "effect_coding": "distance_m .08=-1,.24=+1; speed_m_s .5=-1,1.0=+1",
        "dimensions": list(FACTORIAL_AXES),
        "n_bats": len(bats), "n_test_bat_days": 2*len(bats),
        "training_days": "first two dated sessions per bat",
        "held_out_days": "third and fourth dated sessions per bat",
        "train_group_coefficients": secondary_group,
        "equal_bat_mse_group": mean(x["mse_group"] for x in secondary_bats),
        "equal_bat_mse_personal": mean(x["mse_personal"] for x in secondary_bats),
        "improved_bats": sum(x["forecast_gain"] > 0 for x in secondary_bats),
        "by_bat": secondary_bats,
        "held_out": secondary_heldout,
        "limitations": [
            "Only four biological bats; correlated successive days and device effects not identified",
            "Four cell means algebraically re-expressed, not a mechanistic or unique control law",
            "Each outcome conditions on valid Buzz II and may reflect nonrandom selection",
            "Limited factorial support; faster stimulus changes exposure duration as well as speed",
            "Secondary endpoint exploratory, not confirmation and not selectable after outcomes",
        ],
    }

    return {
        "status": "EXPLORATORY_POST_PUBLICATION",
        "dataset_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "source_schema_note": "Canonical CSV must be mapped and independently validated against deposited original; no claim of verified source schema solely from this script",
        "endpoint": "log1p(Buzz II duration in ms): equal-physical-regime-weight mean of two difficult moving regimes minus mean of four easy moving regimes, conditional on recorded valid buzz II",
        "time_zero_note": "NOT dynamic CI onset model: static burst-duration contrast. Stationary mock onset ignored.",
        "treatment_groups": {str(k): v for k,v in MOVING.items()},
        "method": "days 1-2 train, days 3-4 held out for each bat; shrink 0.5 fixed; >=2 valid buzzes per each of six moving regimes per bat-day, equal regime weights within treatment class, equal bat + equal day; no inferential p-value",
        "n_rows_including_invalid": all_rows,
        "n_valid_buzz": valid_count,
        "n_invalid_buzz": invalid_count,
        "n_bats": len(bats),
        "n_train_bat_days": 2*len(bats),
        "n_test_bat_days": 2*len(bats),
        "train_group_beta": pooled,
        "shrink_coefficient": SHRINK,
        "equal_bat_mse_group": mean(x["mse_shared"] for x in by_bat),
        "equal_bat_mse_personal": mean(x["mse_personal"] for x in by_bat),
        "improved_bats": sum(x["forecast_gain"] > 0 for x in by_bat),
        "by_bat": by_bat,
        "held_out": forecasts,
        "factorial_2x2_secondary": secondary_result,
        "limitations": ["Only 4 biological individuals", "Post-publication exploratory, not blind preregistration", "Consecutive days may have learning/carryover", "Conditional on valid Buzz II; missingness and selection need independent inspection", "Cannot claim 3-D trajectories, latency tau_i, acoustic-cue causation, capture success or fitness"],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    for command in ("inventory", "analyse"):
        cmd = sub.add_parser(command)
        cmd.add_argument("path", type=Path)
        cmd.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)
    try:
        obj = audit_archive(args.path) if args.command == "inventory" else analyse_canonical(args.path)
        text = json.dumps(obj, indent=2, ensure_ascii=False)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(text + "\n", encoding="utf-8")
            print(f"Wrote {args.out} ({obj.get('status', obj.get('raw_data_schema_status'))})")
        else:
            print(text)
        return 0
    except SourceGateError as e:
        print("HOLD_SOURCE_GATE: " + str(e), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
