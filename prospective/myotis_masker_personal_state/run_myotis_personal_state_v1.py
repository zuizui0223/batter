#!/usr/bin/env python3
"""Frozen numerical reanalysis for public Myotis masking datasets."""

from __future__ import annotations

import csv
import hashlib
import io
import itertools
import json
import math
import pathlib
import statistics
import sys
import urllib.request

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
STRUCT = HERE / "MYOTIS_STRUCTURE_RESULT_V1.json"
OUTJ = HERE / "MYOTIS_PERSONAL_STATE_RESULT_V1.json"
OUTM = HERE / "MYOTIS_PERSONAL_STATE_RESULT_V1.md"

BASE = "https://zenodo.org/records/4946256/files/"
FILES = {
    "control1": (
        "control_experiment__1_data.txt",
        "db9c7b38579435d9f63ef6b4973d6825",
    ),
    "flighttime": (
        "dataset_tc.csv",
        "c6b1e0310d98c364e14a79dae4a27360",
    ),
}


def download(name):
    req = urllib.request.Request(
        BASE + name + "?download=1",
        headers={"User-Agent": "batter-myotis-primary/1.0"},
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        return response.read()


def check_md5(data, expected):
    got = hashlib.md5(data).hexdigest()
    if got != expected:
        raise RuntimeError(f"checksum mismatch: {got} != {expected}")


def self_history_summary(x):
    """Return overall statistic, individual means, condition means."""
    x = np.asarray(x, dtype=float)
    n, c = x.shape
    if n < 3 or c < 2:
        raise ValueError("insufficient matrix")

    total = x.sum(axis=1)
    a = np.empty((n, c), dtype=float)

    for k in range(c):
        history = (total - x[:, k]) / (c - 1)
        target = x[:, k]
        dist = np.abs(target[:, None] - history[None, :])
        own = np.diag(dist)
        donor = (dist.sum(axis=1) - own) / (n - 1)
        a[:, k] = donor - own

    return {
        "stat": float(a.mean()),
        "individual_means": [float(v) for v in a.mean(axis=1)],
        "condition_means": [float(v) for v in a.mean(axis=0)],
    }


def batch_stats(xb):
    """Vectorized statistic for a batch: xb shape B x n x c."""
    b, n, c = xb.shape
    total = xb.sum(axis=2)
    accum = np.zeros(b, dtype=float)

    for k in range(c):
        history = (total - xb[:, :, k]) / (c - 1)
        target = xb[:, :, k]
        dist = np.abs(target[:, :, None] - history[:, None, :])
        own = np.diagonal(dist, axis1=1, axis2=2)
        donor = (dist.sum(axis=2) - own) / (n - 1)
        accum += (donor - own).sum(axis=1)

    return accum / (n * c)


def exact_condition_permutation(x, reference_col=0, batch_size=4096):
    x = np.asarray(x, dtype=float)
    n, c = x.shape
    observed = self_history_summary(x)["stat"]
    perms = np.asarray(list(itertools.permutations(range(n))), dtype=int)
    pcount = len(perms)
    nassign = pcount ** (c - 1)

    extreme = 0
    done = 0
    iterator = itertools.product(range(pcount), repeat=c - 1)

    while True:
        chunk = list(itertools.islice(iterator, batch_size))
        if not chunk:
            break
        b = len(chunk)
        xb = np.empty((b, n, c), dtype=float)
        xb[:, :, reference_col] = x[:, reference_col][None, :]

        nonref = [k for k in range(c) if k != reference_col]
        idx = np.asarray(chunk, dtype=int)
        for q, k in enumerate(nonref):
            xb[:, :, k] = x[perms[idx[:, q]], k]

        vals = batch_stats(xb)
        extreme += int(np.sum(vals >= observed - 1e-12))
        done += b

    if done != nassign:
        raise RuntimeError(f"assignment count mismatch {done} != {nassign}")

    return {
        "observed": observed,
        "p_one_sided": extreme / nassign,
        "n_assignments": nassign,
        "n_extreme": extreme,
    }


def control_condition(row):
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
    raise ValueError("unexpected control treatment")


def analyze_control(data):
    rows = list(
        csv.DictReader(
            io.StringIO(data.decode("utf-8-sig")),
            delimiter="\t",
        )
    )

    conditions = [
        "no_noise",
        "noise_target",
        "noise_above",
        "noise_side",
    ]
    animals = sorted({row["animal"] for row in rows})
    dates = sorted({row["date"] for row in rows})

    trial_values = {}
    for row in rows:
        key = (
            row["animal"],
            row["date"],
            control_condition(row),
            row["trialno"],
        )
        trial_values.setdefault(key, []).append(float(row["sl_rms"]))

    for values in trial_values.values():
        if len(values) != 5:
            raise RuntimeError("trial does not contain exactly five calls")

    trial_mean = {
        key: float(np.mean(values))
        for key, values in trial_values.items()
    }

    day_values = {}
    for (animal, date, condition, trial), value in trial_mean.items():
        day_values.setdefault((animal, condition, date), []).append(value)

    cell = np.empty((len(animals), len(conditions)), dtype=float)
    for i, animal in enumerate(animals):
        for k, condition in enumerate(conditions):
            by_day = []
            for date in dates:
                values = day_values.get((animal, condition, date), [])
                if len(values) < 4:
                    raise RuntimeError("control support drift")
                by_day.append(float(np.mean(values)))
            cell[i, k] = float(np.mean(by_day))

    residual = cell - cell.mean(axis=0, keepdims=True)
    descriptive = self_history_summary(residual)
    exact = exact_condition_permutation(residual, reference_col=0)

    return {
        "animals": animals,
        "conditions": conditions,
        "statistic": exact["observed"],
        "p_one_sided": exact["p_one_sided"],
        "n_assignments": exact["n_assignments"],
        "n_extreme": exact["n_extreme"],
        "individual_mean_advantage": {
            animal: descriptive["individual_means"][i]
            for i, animal in enumerate(animals)
        },
        "condition_mean_advantage": {
            condition: descriptive["condition_means"][k]
            for k, condition in enumerate(conditions)
        },
        "positive_individuals": int(
            sum(v > 0 for v in descriptive["individual_means"])
        ),
        "verdict": (
            "SUPPORTED"
            if exact["observed"] > 0
            and exact["p_one_sided"] <= 0.05
            else "UNSUPPORTED"
        ),
    }


def analyze_flight(data, structural):
    text = data.decode("utf-8-sig")
    dialect = csv.Sniffer().sniff(text[:4096])
    rows = list(csv.DictReader(io.StringIO(text), dialect=dialect))

    bats = list(structural["flighttime"]["common_support_bats"])
    noise = sorted(
        {row["noise_sphere"] for row in rows},
        key=lambda x: float(x),
    )
    if len(noise) != 5:
        raise RuntimeError("noise-level support drift")

    grouped = {}
    for row in rows:
        if row["bat_num"] not in bats:
            continue
        value = float(row["time_flight_s"])
        if not value > 0:
            raise RuntimeError("nonpositive flight time")
        key = (
            row["bat_num"],
            row["noise_sphere"],
            row["daynumber"],
        )
        grouped.setdefault(key, []).append(math.log(value))

    cell = np.empty((len(bats), len(noise)), dtype=float)
    for i, bat in enumerate(bats):
        for k, condition in enumerate(noise):
            days = sorted(
                {
                    day
                    for (b, c, day) in grouped
                    if b == bat and c == condition
                },
                key=lambda x: float(x),
            )
            if len(days) < 2:
                raise RuntimeError("flight day support drift")
            day_medians = [
                float(np.median(grouped[(bat, condition, day)]))
                for day in days
            ]
            cell[i, k] = float(np.mean(day_medians))

    residual = cell - cell.mean(axis=0, keepdims=True)
    descriptive = self_history_summary(residual)

    reference_col = next(
        (
            k
            for k, condition in enumerate(noise)
            if abs(float(condition) - 20.0) < 1e-12
        ),
        None,
    )
    if reference_col is None:
        raise RuntimeError("no source no-noise condition")

    exact = exact_condition_permutation(
        residual,
        reference_col=reference_col,
    )

    return {
        "bats": bats,
        "conditions": noise,
        "statistic": exact["observed"],
        "p_one_sided": exact["p_one_sided"],
        "n_assignments": exact["n_assignments"],
        "n_extreme": exact["n_extreme"],
        "individual_mean_advantage": {
            bat: descriptive["individual_means"][i]
            for i, bat in enumerate(bats)
        },
        "condition_mean_advantage": {
            condition: descriptive["condition_means"][k]
            for k, condition in enumerate(noise)
        },
        "positive_individuals": int(
            sum(v > 0 for v in descriptive["individual_means"])
        ),
        "verdict": (
            "CONTROLLED_SMALL_N_MOVEMENT_SUPPORT"
            if exact["observed"] > 0
            and exact["p_one_sided"] <= 0.05
            else "UNSUPPORTED"
        ),
    }


def main():
    if not STRUCT.exists():
        print("WAIT_STRUCTURE_RESULT")
        return

    structural = json.loads(STRUCT.read_text())
    if structural["control1"]["verdict"] != "PASS_CONTROL1_STRUCTURE":
        raise SystemExit("STOP: control1 structural gate failed")
    if structural["flighttime"]["verdict"] != "PASS_FLIGHTTIME_STRUCTURE":
        raise SystemExit("STOP: flight-time structural gate failed")

    raw = {}
    for key, (name, expected) in FILES.items():
        data = download(name)
        check_md5(data, expected)
        raw[key] = data

    result = {
        "source_record": 4946256,
        "control1": analyze_control(raw["control1"]),
        "flighttime": analyze_flight(raw["flighttime"], structural),
    }

    OUTJ.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    )

    c = result["control1"]
    f = result["flighttime"]
    lines = [
        "# Myotis masking personal-state result v1",
        "",
        "## Control experiment 1 — acoustic control",
        "",
        f"- A_control1: **{c['statistic']:+.6f}**",
        f"- exact p: **{c['p_one_sided']:.8f}**",
        f"- exact assignments: {c['n_assignments']}",
        (
            f"- positive individuals: "
            f"{c['positive_individuals']}/{len(c['animals'])}"
        ),
        f"- verdict: **{c['verdict']}**",
        "",
        "Individual mean advantages:",
    ]
    for animal, value in c["individual_mean_advantage"].items():
        lines.append(f"- {animal}: {value:+.6f}")

    lines += [
        "",
        "Condition mean advantages:",
    ]
    for condition, value in c["condition_mean_advantage"].items():
        lines.append(f"- {condition}: {value:+.6f}")

    lines += [
        "",
        "## Main experiment — landing-time behavior",
        "",
        f"- A_flighttime: **{f['statistic']:+.6f}**",
        f"- exact p: **{f['p_one_sided']:.8f}**",
        f"- exact assignments: {f['n_assignments']}",
        (
            f"- positive individuals: "
            f"{f['positive_individuals']}/{len(f['bats'])}"
        ),
        f"- verdict: **{f['verdict']}**",
        "",
        "Individual mean advantages:",
    ]
    for bat, value in f["individual_mean_advantage"].items():
        lines.append(f"- bat {bat}: {value:+.6f}")

    lines += [
        "",
        "## Claim boundary",
        "",
        (
            "The acoustic endpoint tests persistent relative acoustic-control "
            "organization across noise-source geometry."
        ),
        (
            "The flight-time endpoint tests small-N relative landing-performance "
            "organization across masking levels."
        ),
        (
            "Neither endpoint establishes the origin of individuality or the "
            "wild vertical-individuality bridge."
        ),
    ]

    OUTM.write_text("\n".join(lines) + "\n")
    print(OUTM.read_text())


if __name__ == "__main__":
    main()
