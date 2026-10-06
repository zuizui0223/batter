#!/usr/bin/env python3
"""Generate restricted randomized assignments for the matched-family experiment.

Run only after capability screening and assignment of opaque animal IDs.
No outcome data are read.

Each complete block of four contains one animal in each cell:
A-open/A-start, A-open/B-start, B-open/A-start, B-open/B-start.
"""

import argparse
import csv
import random
from pathlib import Path

SEED = 202610062035
CELLS = [
    ("A", "A"),
    ("A", "B"),
    ("B", "A"),
    ("B", "B"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", required=True, help="Text file: one opaque eligible animal ID per line")
    ap.add_argument("--out", required=True, help="Output CSV")
    args = ap.parse_args()

    ids = [x.strip() for x in Path(args.ids).read_text().splitlines() if x.strip()]
    if len(ids) % 4 != 0:
        raise SystemExit("STOP: eligible IDs must form complete blocks of four before schedule freeze")
    if len(set(ids)) != len(ids):
        raise SystemExit("STOP: duplicate opaque animal IDs")

    rng = random.Random(SEED)
    rows = []
    for b0 in range(0, len(ids), 4):
        block_ids = ids[b0:b0 + 4]
        cells = CELLS.copy()
        rng.shuffle(cells)
        for animal_id, (open_family, start_family) in zip(block_ids, cells):
            rows.append({
                "block": b0 // 4 + 1,
                "animal_id": animal_id,
                "open_family": open_family,
                "constrained_family": "B" if open_family == "A" else "A",
                "acquisition_start_family": start_family,
                "schedule_seed": SEED,
            })

    out = Path(args.out)
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
