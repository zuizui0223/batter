#!/usr/bin/env python3
"""Audit normalized A/B matched-family geometry.

Pure geometry only. No animal data are read.
"""

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = HERE / "matched_family_geometry_v1.json"

TOL = 1e-12


def norm(v):
    return math.sqrt(sum(x * x for x in v))


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def segment_lengths(points):
    return [norm(sub(points[i + 1], points[i])) for i in range(len(points) - 1)]


def turn_angles(points):
    seg = [sub(points[i + 1], points[i]) for i in range(len(points) - 1)]
    out = []
    for a, b in zip(seg[:-1], seg[1:]):
        na, nb = norm(a), norm(b)
        cosang = sum(x * y for x, y in zip(a, b)) / (na * nb)
        cosang = max(-1.0, min(1.0, cosang))
        out.append(math.acos(cosang))
    return out


def route_points(spec, family, route):
    L = float(spec["L"])
    x1 = float(spec["x1"])
    x2 = float(spec["x2"])
    d = float(spec["d"])
    h = int(spec["routes"][route]["h"])
    v = int(spec["routes"][route]["v"])

    s = (0.0, 0.0, 0.0)
    g = (L, 0.0, 0.0)

    if family == "A":
        w1 = (x1, h * d, 0.0)
        w2 = (x2, h * d, v * d)
    elif family == "B":
        w1 = (x1, 0.0, v * d)
        w2 = (x2, h * d, v * d)
    else:
        raise ValueError(family)

    return [s, w1, w2, g]


def route_metrics(points):
    lengths = segment_lengths(points)
    angles = turn_angles(points)
    total = sum(lengths)
    horizontal_abs = sum(
        math.hypot(points[i + 1][1] - points[i][1], 0.0)
        for i in range(len(points) - 1)
    )
    vertical_abs = sum(
        abs(points[i + 1][2] - points[i][2])
        for i in range(len(points) - 1)
    )
    return {
        "segment_lengths": lengths,
        "path_length": total,
        "turn_angles": angles,
        "horizontal_abs": horizontal_abs,
        "vertical_abs": vertical_abs,
    }


def assert_close(a, b, label):
    if abs(a - b) > TOL:
        raise AssertionError(f"{label}: {a} != {b}")


def main():
    spec = json.loads(SPEC.read_text())
    metrics = {}

    for family in ("A", "B"):
        for route in sorted(spec["routes"]):
            pts = route_points(spec, family, route)
            metrics[(family, route)] = route_metrics(pts)

    reference = metrics[("A", "R1")]

    for key, m in metrics.items():
        assert_close(m["path_length"], reference["path_length"], f"{key} path length")
        assert_close(m["horizontal_abs"], reference["horizontal_abs"], f"{key} horizontal demand")
        assert_close(m["vertical_abs"], reference["vertical_abs"], f"{key} vertical demand")

        if len(m["turn_angles"]) != len(reference["turn_angles"]):
            raise AssertionError(f"{key}: turn count mismatch")

        for k, (a, b) in enumerate(zip(sorted(m["turn_angles"]), sorted(reference["turn_angles"]))):
            assert_close(a, b, f"{key} sorted turn angle {k}")

    print("PASS matched family geometry v1")
    print(f"routes audited: {len(metrics)}")
    print(f"normalized path length: {reference['path_length']:.12f}")
    print("segment lengths:", ",".join(f"{x:.12f}" for x in reference["segment_lengths"]))
    print("turn angles rad:", ",".join(f"{x:.12f}" for x in reference["turn_angles"]))
    print(f"total |horizontal| demand: {reference['horizontal_abs']:.12f}")
    print(f"total |vertical| demand: {reference['vertical_abs']:.12f}")


if __name__ == "__main__":
    main()
