#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import io
import json
import math
from pathlib import Path
import urllib.request

from pyproj import Transformer

from batter.analysis import build_events, leave_one_session_out, md5_bytes


URL = "https://datarepository.movebank.org/server/api/core/bitstreams/2d629393-4266-4f85-88db-001faeab669d/content"
EXPECTED_SIZE = 1926056
EXPECTED_MD5 = "570872ab7aba674b9bdc2f2ee6044a71"

PRIMARY_EDGES = (-math.inf, 0.0, 50.0, 100.0, 200.0, 400.0, 800.0, 1600.0, 3200.0, math.inf)
FINE_EDGES = (-math.inf, 0.0, 25.0, 50.0, 100.0, 200.0, 400.0, 800.0, 1600.0, 3200.0, math.inf)
COARSE_EDGES = (-math.inf, 0.0, 100.0, 200.0, 400.0, 800.0, 1600.0, 3200.0, math.inf)


def analyze(rows, transformer, *, cell_size_m, z_edges, exclude_outliers):
    events, preflight = build_events(
        rows,
        projector=transformer.transform,
        cell_size_m=cell_size_m,
        gap_hours=4.0,
        exclude_marked_outliers=exclude_outliers,
        min_session_fixes=50,
        z_edges=z_edges,
    )
    result = leave_one_session_out(
        events,
        alpha=0.5,
        minimum_scored_fixes=50,
        n_z_bins=len(z_edges) - 1,
    )
    return {"preflight": preflight, "analysis": result}


def compact(result):
    analysis = result["analysis"]
    return {
        "eligible_individual_count": analysis["eligible_individual_count"],
        "equal_individual_mean_gain_nats_per_fix": analysis["equal_individual_mean_gain_nats_per_fix"],
        "positive_individual_fraction": analysis["positive_individual_fraction"],
        "individual_results": analysis["individual_results"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results/individual_vertical_strategy_v1.json"))
    args = parser.parse_args()

    request = urllib.request.Request(URL, headers={"User-Agent": "batter-v1/0.2"})
    with urllib.request.urlopen(request, timeout=120) as response:
        data = response.read()
    if len(data) != EXPECTED_SIZE:
        raise RuntimeError(f"source size mismatch: {len(data)} != {EXPECTED_SIZE}")
    digest = md5_bytes(data)
    if digest != EXPECTED_MD5:
        raise RuntimeError(f"source md5 mismatch: {digest}")

    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig")))
    rows = list(reader)
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3035", always_xy=True)

    primary = analyze(
        rows, transformer,
        cell_size_m=5000.0,
        z_edges=PRIMARY_EDGES,
        exclude_outliers=True,
    )

    # These are explicitly post-primary robustness checks. Their configurations
    # are inherited from the already frozen ODSP bat sensitivity family rather
    # than chosen to improve the batter outcome.
    sensitivities = {
        "grid_2500_m": analyze(
            rows, transformer, cell_size_m=2500.0,
            z_edges=PRIMARY_EDGES, exclude_outliers=True,
        ),
        "grid_10000_m": analyze(
            rows, transformer, cell_size_m=10000.0,
            z_edges=PRIMARY_EDGES, exclude_outliers=True,
        ),
        "fine_z_bins": analyze(
            rows, transformer, cell_size_m=5000.0,
            z_edges=FINE_EDGES, exclude_outliers=True,
        ),
        "coarse_z_bins": analyze(
            rows, transformer, cell_size_m=5000.0,
            z_edges=COARSE_EDGES, exclude_outliers=True,
        ),
        "include_source_marked_outliers": analyze(
            rows, transformer, cell_size_m=5000.0,
            z_edges=PRIMARY_EDGES, exclude_outliers=False,
        ),
    }

    payload = {
        "study_id": "batter-individual-vertical-strategy-v1",
        "source": {"bytes": len(data), "md5": digest},
        "primary_endpoint": "mean log P_self(z|x,y) - log P_other_individuals(z|x,y)",
        "primary": primary,
        "post_primary_sensitivities": {
            name: compact(value) for name, value in sensitivities.items()
        },
        "sensitivity_status": "post-primary robustness only; cannot redefine the primary endpoint",
        "claim_boundary": {
            "vertical_use_not_verified_foraging": True,
            "height_is_above_msl_not_ground": True,
            "fixes_are_not_independent_replicates": True,
            "environmental_mechanism_not_yet_modeled": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "output": str(args.output),
        "primary": compact(primary),
        "sensitivities": {name: compact(value) for name, value in sensitivities.items()},
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
