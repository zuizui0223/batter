#!/usr/bin/env python3
"""Self-test for restricted solution-repertoire randomization structure."""

from randomization_inference_reference_v1 import (
    enumerate_treatment_assignments,
    expected_assignment_count,
)


def fake_rows(n_blocks):
    rows = []
    for block in range(1, n_blocks + 1):
        rows.extend([
            {"block": block, "animal_id": f"{block}_A1", "acquisition_start_family": "A"},
            {"block": block, "animal_id": f"{block}_A2", "acquisition_start_family": "A"},
            {"block": block, "animal_id": f"{block}_B1", "acquisition_start_family": "B"},
            {"block": block, "animal_id": f"{block}_B2", "acquisition_start_family": "B"},
        ])
    return rows


def main():
    for n_blocks in (4, 5, 6):
        rows = fake_rows(n_blocks)
        assignments = list(enumerate_treatment_assignments(rows))
        assert len(assignments) == expected_assignment_count(n_blocks)

        for assignment in assignments:
            for block in range(1, n_blocks + 1):
                block_rows = [r for r in rows if r["block"] == block]
                for start in ("A", "B"):
                    ids = [
                        r["animal_id"] for r in block_rows
                        if r["acquisition_start_family"] == start
                    ]
                    labels = [assignment[i] for i in ids]
                    assert sorted(labels) == ["A", "B"]

    print("PASS: restricted assignment enumeration")


if __name__ == "__main__":
    main()
