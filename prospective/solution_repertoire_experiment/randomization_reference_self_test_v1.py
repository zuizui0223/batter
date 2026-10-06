#!/usr/bin/env python3
"""Self-test for restricted randomization inference v1."""

from randomization_inference_reference_v1 import (
    delta_a,
    enumerate_treatment_assignments,
    exact_one_sided_p,
    expected_assignment_count,
)


def synthetic_rows(n_blocks):
    rows = []
    for b in range(1, n_blocks + 1):
        rows.extend([
            {"block": b, "animal_id": f"b{b}_1", "acquisition_start_family": "A"},
            {"block": b, "animal_id": f"b{b}_2", "acquisition_start_family": "A"},
            {"block": b, "animal_id": f"b{b}_3", "acquisition_start_family": "B"},
            {"block": b, "animal_id": f"b{b}_4", "acquisition_start_family": "B"},
        ])
    return rows


def assert_assignment_balance(rows, assignment):
    blocks = {}
    for row in rows:
        blocks.setdefault(row["block"], []).append(row)

    for block_rows in blocks.values():
        for start in ("A", "B"):
            ids = [
                row["animal_id"]
                for row in block_rows
                if row["acquisition_start_family"] == start
            ]
            assert len(ids) == 2
            vals = sorted(assignment[i] for i in ids)
            assert vals == ["A", "B"]


def main():
    rows = synthetic_rows(4)
    assignments = list(enumerate_treatment_assignments(rows))

    assert len(assignments) == 256
    assert len(assignments) == expected_assignment_count(4)
    assert len({tuple(sorted(a.items())) for a in assignments}) == 256

    for assignment in assignments:
        assert_assignment_balance(rows, assignment)

    observed = assignments[0]

    # Null sanity check: identical family scores -> Delta_A = 0 for every assignment.
    zero_scores = {}
    for row in rows:
        i = row["animal_id"]
        zero_scores[(i, "A")] = 0.0
        zero_scores[(i, "B")] = 0.0

    obs0, p0, n0 = exact_one_sided_p(rows, zero_scores, observed)
    assert obs0 == 0.0
    assert p0 == 1.0
    assert n0 == 256

    # Extreme constructed alternative: each animal's observed OPEN family gets score 1,
    # its constrained family gets 0. The observed assignment should be uniquely maximal.
    strong_scores = {}
    for row in rows:
        i = row["animal_id"]
        open_family = observed[i]
        constrained = "B" if open_family == "A" else "A"
        strong_scores[(i, open_family)] = 1.0
        strong_scores[(i, constrained)] = 0.0

    obs, p, n = exact_one_sided_p(rows, strong_scores, observed)
    assert abs(obs - 1.0) < 1e-12
    assert abs(p - 1 / 256) < 1e-12
    assert n == 256

    # Five blocks -> 1,024 legal assignments.
    rows20 = synthetic_rows(5)
    assert sum(1 for _ in enumerate_treatment_assignments(rows20)) == 1024
    assert expected_assignment_count(5) == 1024

    print("PASS: restricted randomization reference v1")


if __name__ == "__main__":
    main()
