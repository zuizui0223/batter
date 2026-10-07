# Mini-to-Rhino centroid-support preflight v1

## Status

**OUTCOME-BLIND STRUCTURAL PREFLIGHT.**

The exact file-count match failed because Mini has repeated trajectories in cells that Rhino does not match one-for-one. This preflight therefore tests a different estimand fixed before any centroid-level movement outcome is opened:

> Can the two species be compared after collapsing every occupied bat × environment cell to one equal-weight centroid?

This removes unequal within-cell trajectory replication and tests only cross-environment support geometry.

## Structural inputs only

Use public filename metadata only.

No coordinate values or movement features may be downloaded or calculated in this preflight.

Mini source range:
- 55033796–55033850

Rhino source range:
- 55033853–55033985

Filename pattern:
`Env{e}_Bat{b}_no{trial}.csv`.

## Occupancy template

For each species define the binary bat × environment occupancy matrix

[
I_{e,b}=1
]

if at least one source trajectory file exists in that cell.

Mini must have:
- 4 bats;
- 7 environment labels;
- 12 occupied bat × environment cells;
- 19 raw trajectory files total.

## Allowed mapping

Because this is a statistical-support comparison rather than a biological same-configuration comparison, environment identities may be globally permuted.

Evaluate every:
- injective mapping of the four Mini bat labels to four Rhino bat labels;
- bijection of the seven Mini environment labels to the seven Rhino environment labels.

A mapping is feasible if every occupied Mini cell maps to an occupied Rhino cell.

Extra Rhino occupied cells are ignored.

## Gate

Open the matched centroid outcome test only if:
- at least 100 feasible bat × environment mappings exist.

Report:
- feasible mapping count;
- first 20 mappings in deterministic lexical order;
- no behavioural values.

## Next analysis if gate passes

A separately frozen outcome contract will:

1. calculate the same eight movement features for both species;
2. apply one common species-specific standardization:
   - subtract each environment feature mean;
   - divide by species-wide pooled environment-centered SD;
3. collapse each occupied bat × environment cell to one centroid;
4. use the exact 12-cell Mini support pattern;
5. map that support pattern onto Rhino using a deterministic sample of feasible structural mappings;
6. test whether a Rhino-like one-dimensional identity signal remains detectable under Mini-matched centroid support.

No outcome is opened here.
