#!/usr/bin/env python3
"""Reference utilities for exact restricted randomization inference.

Primary endpoint inputs are treatment-blind family-specific scores:
    A[(animal_id, "A")]
    A[(animal_id, "B")]

The randomization null reassigns which family is OPEN-acquired subject to the
actual four-animal block design. It must NOT use unrestricted independent
sign flips across animals.
"""

from itertools import product


def enumerate_treatment_assignments(rows):
    """Yield allowed maps animal_id -> OPEN family.

    Required keys per row:
      animal_id
      block
      acquisition_start_family

    Conditional on starting-family order, each complete block has:
      - two A-start animals: one A-open, one B-open
      - two B-start animals: one A-open, one B-open
    giving four legal OPEN-family assignments per block.
    """
    blocks = {}
    for row in rows:
        blocks.setdefault(int(row["block"]), []).append(row)

    block_options = []

    for block_id in sorted(blocks):
        block_rows = blocks[block_id]
        by_start = {"A": [], "B": []}

        for row in block_rows:
            start = row["acquisition_start_family"]
            if start not in by_start:
                raise ValueError(f"Block {block_id}: invalid start family {start}")
            by_start[start].append(row["animal_id"])

        if len(by_start["A"]) != 2 or len(by_start["B"]) != 2:
            raise ValueError(
                f"Block {block_id}: expected exactly two A-start and two B-start animals"
            )

        options = []
        for a_pick in range(2):
            for b_pick in range(2):
                assignment = {}
                for start, pick in (("A", a_pick), ("B", b_pick)):
                    ids = by_start[start]
                    assignment[ids[pick]] = "A"
                    assignment[ids[1 - pick]] = "B"
                options.append(assignment)

        block_options.append(options)

    for combo in product(*block_options):
        merged = {}
        for assignment in combo:
            merged.update(assignment)
        yield merged


def delta_a(family_scores, open_family_map):
    """Compute equal-individual OPEN minus CONSTRAINED identity advantage.

    family_scores maps (animal_id, family) -> A_i,f.
    open_family_map maps animal_id -> "A" or "B".
    """
    diffs = []
    animal_ids = sorted(open_family_map)

    for animal_id in animal_ids:
        open_family = open_family_map[animal_id]
        constrained_family = "B" if open_family == "A" else "A"

        a_open = family_scores[(animal_id, open_family)]
        a_constrained = family_scores[(animal_id, constrained_family)]
        diffs.append(a_open - a_constrained)

    return sum(diffs) / len(diffs)


def exact_one_sided_p(rows, family_scores, observed_open_family_map):
    """Return observed Delta_A, exact p, and assignment count."""
    observed = delta_a(family_scores, observed_open_family_map)
    null = []

    for assignment in enumerate_treatment_assignments(rows):
        null.append(delta_a(family_scores, assignment))

    extreme = sum(value >= observed for value in null)
    return observed, extreme / len(null), len(null)


def expected_assignment_count(n_complete_blocks):
    return 4 ** n_complete_blocks


if __name__ == "__main__":
    for blocks in (4, 5, 6):
        n = expected_assignment_count(blocks)
        print(
            f"{blocks} blocks: {n} assignments; "
            f"minimum nonzero exact upper-tail fraction = {1 / n:.6g}"
        )
