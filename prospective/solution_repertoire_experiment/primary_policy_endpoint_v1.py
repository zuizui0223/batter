#!/usr/bin/env python3
"""Reference implementation of the frozen solution-repertoire primary endpoint v1."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

import numpy as np

FEATURE_NAMES = [
    "median_speed",
    "p90_speed",
    "median_abs_vertical_speed",
    "p90_abs_vertical_speed",
    "median_abs_horizontal_turn_rate",
    "p90_abs_horizontal_turn_rate",
    "path_efficiency",
    "vertical_range",
]


def route_features(arr: np.ndarray) -> np.ndarray | None:
    """Return the frozen 8-feature vector, or None if the flight is invalid.

    arr columns: time, x, y, z.
    """
    arr = np.asarray(arr, dtype=float)
    if arr.ndim != 2 or arr.shape[1] != 4:
        raise ValueError("expected N x 4 array: time,x,y,z")

    arr = arr[np.all(np.isfinite(arr), axis=1)]
    if len(arr) < 100:
        return None

    order = np.argsort(arr[:, 0], kind="mergesort")
    arr = arr[order]

    _, first_idx = np.unique(arr[:, 0], return_index=True)
    arr = arr[np.sort(first_idx)]

    if len(arr) < 100:
        return None

    t = arr[:, 0]
    xyz = arr[:, 1:4]
    duration = float(t[-1] - t[0])
    if not (np.isfinite(duration) and duration > 0):
        return None

    dxyz = np.diff(xyz, axis=0)
    seg = np.linalg.norm(dxyz, axis=1)
    path = float(np.sum(seg[np.isfinite(seg)]))
    if not (np.isfinite(path) and path > 0):
        return None

    dt = np.diff(t)
    posdt = dt > 0
    if int(np.sum(posdt)) < 50:
        return None

    dxyzp = dxyz[posdt]
    dtp = dt[posdt]
    speed = np.linalg.norm(dxyzp, axis=1) / dtp
    vz = np.abs(dxyzp[:, 2] / dtp)

    dx = dxyz[:, 0]
    dy = dxyz[:, 1]
    hmag = np.hypot(dx, dy)
    heading = np.full(len(dt), np.nan, dtype=float)
    good = (dt > 0) & (hmag > 0) & np.isfinite(hmag)
    heading[good] = np.arctan2(dy[good], dx[good])

    turns = []
    for k in range(len(heading) - 1):
        if not (np.isfinite(heading[k]) and np.isfinite(heading[k + 1])):
            continue
        dt_turn = 0.5 * (dt[k] + dt[k + 1])
        if not (np.isfinite(dt_turn) and dt_turn > 0):
            continue
        dtheta = math.atan2(
            math.sin(heading[k + 1] - heading[k]),
            math.cos(heading[k + 1] - heading[k]),
        )
        turns.append(abs(dtheta) / dt_turn)

    turns = np.asarray(turns, dtype=float)
    if len(turns) == 0:
        return None

    net = float(np.linalg.norm(xyz[-1] - xyz[0]))
    efficiency = net / path
    vertical_range = float(np.max(xyz[:, 2]) - np.min(xyz[:, 2]))

    feats = np.asarray(
        [
            np.median(speed),
            np.percentile(speed, 90),
            np.median(vz),
            np.percentile(vz, 90),
            np.median(turns),
            np.percentile(turns, 90),
            efficiency,
            vertical_range,
        ],
        dtype=float,
    )

    if not np.all(np.isfinite(feats)):
        return None
    return feats


def standardize_probe_rows(rows: Sequence[dict]) -> List[dict]:
    """Treatment-blind within-family z standardization of the 8 features."""
    out = []
    families = sorted({row["family"] for row in rows})

    for family in families:
        rr = [row for row in rows if row["family"] == family]
        if len(rr) < 2:
            raise ValueError(f"family {family}: insufficient rows")

        mat = np.vstack([np.asarray(row["features"], dtype=float) for row in rr])
        if mat.shape[1] != 8:
            raise ValueError("expected eight frozen features")

        mu = mat.mean(axis=0)
        sd = mat.std(axis=0, ddof=1)

        if np.any(~np.isfinite(sd)) or np.any(sd <= 0):
            raise ValueError(f"family {family}: zero/nonfinite feature SD")

        for row in rr:
            z = (np.asarray(row["features"], dtype=float) - mu) / sd
            q = dict(row)
            q["z8"] = z
            q["I"] = float(np.mean(z[:4]))
            q["M"] = float(np.mean(np.asarray([-z[0], z[4], z[5], z[6], z[7]])))
            out.append(q)

    return out


def endpoint_eligible_animals(rows: Sequence[dict], planned_probe_count: int) -> List[str]:
    if planned_probe_count <= 0 or planned_probe_count % 2 != 0:
        raise ValueError("planned_probe_count must be positive and even")

    families = sorted({row["family"] for row in rows})
    if len(families) != 2:
        raise ValueError("primary requires exactly two matched families")

    animals = sorted({row["animal_id"] for row in rows})
    eligible = []

    for animal in animals:
        ok = True
        for family in families:
            rr = [
                row for row in rows
                if row["animal_id"] == animal and row["family"] == family
            ]
            orders = sorted(row["probe_order"] for row in rr)
            if len(rr) != planned_probe_count:
                ok = False
                break
            if orders != list(range(1, planned_probe_count + 1)):
                ok = False
                break
        if ok:
            eligible.append(animal)

    return eligible


def family_identity_scores(rows: Sequence[dict], planned_probe_count: int) -> Dict[Tuple[str, str], float]:
    """Return A_(animal,family) from early->late common-OPEN identity."""
    eligible = endpoint_eligible_animals(rows, planned_probe_count)
    if len(eligible) < 3:
        raise ValueError("need at least three endpoint-eligible animals")

    rows = [row for row in rows if row["animal_id"] in eligible]
    zrows = standardize_probe_rows(rows)
    half = planned_probe_count // 2
    families = sorted({row["family"] for row in zrows})

    scores = {}

    for family in families:
        early_centroid = {}
        for animal in eligible:
            rr = [
                row for row in zrows
                if row["family"] == family
                and row["animal_id"] == animal
                and row["probe_order"] <= half
            ]
            if len(rr) != half:
                raise ValueError("early probe support drift")
            early_centroid[animal] = np.mean(
                np.vstack([[row["I"], row["M"]] for row in rr]),
                axis=0,
            )

        for animal in eligible:
            late = [
                row for row in zrows
                if row["family"] == family
                and row["animal_id"] == animal
                and row["probe_order"] > half
            ]
            if len(late) != half:
                raise ValueError("late probe support drift")

            donors = [x for x in eligible if x != animal]
            if len(donors) < 2:
                raise ValueError("need at least two donor individuals")

            vals = []
            for row in late:
                theta = np.asarray([row["I"], row["M"]], dtype=float)
                dself = float(np.linalg.norm(theta - early_centroid[animal]))
                dother = float(np.mean([
                    np.linalg.norm(theta - early_centroid[donor])
                    for donor in donors
                ]))
                vals.append(dother - dself)

            scores[(animal, family)] = float(np.mean(vals))

    return scores


def treatment_delta(
    family_scores: Mapping[Tuple[str, str], float],
    open_family_map: Mapping[str, str],
) -> Tuple[float, Dict[str, float]]:
    individual = {}

    for animal, open_family in sorted(open_family_map.items()):
        constrained_family = "B" if open_family == "A" else "A"
        individual[animal] = (
            family_scores[(animal, open_family)]
            - family_scores[(animal, constrained_family)]
        )

    return float(np.mean(list(individual.values()))), individual
