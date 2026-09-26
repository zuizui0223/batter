#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path
import urllib.request

from pyproj import Transformer

from batter.analysis import build_events, leave_one_session_out, md5_bytes


URL = "https://datarepository.movebank.org/server/api/core/bitstreams/2d629393-4266-4f85-88db-001faeab669d/content"
EXPECTED_SIZE = 1926056
EXPECTED_MD5 = "570872ab7aba674b9bdc2f2ee6044a71"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results/individual_vertical_strategy_v1.json"))
    args = parser.parse_args()

    request = urllib.request.Request(URL, headers={"User-Agent": "batter-v1/0.1"})
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
    events, preflight = build_events(
        rows,
        projector=transformer.transform,
        cell_size_m=5000.0,
        gap_hours=4.0,
        exclude_marked_outliers=True,
        min_session_fixes=50,
    )
    result = leave_one_session_out(events, alpha=0.5, minimum_scored_fixes=50)
    payload = {
        "study_id": "batter-individual-vertical-strategy-v1",
        "source": {"bytes": len(data), "md5": digest},
        "preflight": preflight,
        "primary_endpoint": "mean log P_self(z|x,y) - log P_other_individuals(z|x,y)",
        "analysis": result,
        "claim_boundary": {
            "vertical_use_not_verified_foraging": True,
            "height_is_above_msl_not_ground": True,
            "fixes_are_not_independent_replicates": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "individuals": len(preflight["individuals"]),
        "retained_sessions": preflight["retained_sessions"],
        "eligible_individual_count": result["eligible_individual_count"],
        "equal_individual_mean_gain_nats_per_fix": result["equal_individual_mean_gain_nats_per_fix"],
        "positive_individual_fraction": result["positive_individual_fraction"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
