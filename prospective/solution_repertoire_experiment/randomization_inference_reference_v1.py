#!/usr/bin/env python3
"""Reference enumerator for the exact primary randomization space.

The final biological endpoint and data schema must be frozen separately.

The real analysis must call enumerate_treatment_assignments() and RECOMPUTE
donor pools and Delta_A for every yielded assignment. Do not sign-flip
precomputed individual contrasts.
"""

from itertools import product


def enumerate_treatment_assignments(rows):
    """Yield allowed OPEN-family maps conditional on block and start-family."""
    blocks = {}
    for row in rows:
        blocks.setdefault(row["block"], []).append(row)

    block_options = []
    for block_id in sorted(blocks):
        block_rows = blocks[block_id]
        by_start = {"A": [], "B": []}
        for row in block_rows:
            by_start[row["acquisition_start_family"]].append(row["animal_id"])

        if len(by_start["A"]) != 2 or len(by_start["B"]) != 2:
            raise ValueError(
                f"Block {block_id}: expected two A-start and two B-start animals"
            )

        opts = []
        for a_pick in range(2):
            for b_pick in range(2):
                assignment = {}
                for start, pick in [("A", a_pick), ("B", b_pick)]:
                    ids = by_start[start]
                    assignment[ids[pick]] = "A"
                    assignment[ids[1 - pick]] = "B"
                opts.append(assignment)
        block_options.append(opts)

    for combo in product(*block_options):
        merged = {}
        for assignment in combo:
            merged.update(assignment)
        yield merged


def expected_assignment_count(n_complete_blocks):
    return 4 ** n_complete_blocks


if __name__ == "__main__":
    for b in (4, 5, 6):
        n = expected_assignment_count(b)
        print(
            f"{b} blocks: {n} assignments; "
            f"minimum exact nonzero tail fraction = {1/n:.6g}"
        )
