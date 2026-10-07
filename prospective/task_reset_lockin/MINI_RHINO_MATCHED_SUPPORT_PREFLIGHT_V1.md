# Mini-to-Rhino matched-support preflight v1

## Status

**OUTCOME-BLIND STRUCTURAL PREFLIGHT.**

Purpose:

> Determine whether the known *Rhinolophus nippon* positive-control archive can be reduced to the exact *Miniopterus fuliginosus* trajectory-support pattern before comparing detectability of a one-dimensional individual policy.

This preflight uses only:
- public Figshare file IDs;
- filenames;
- environment labels;
- bat labels;
- trajectory-file counts per bat × environment.

It must not:
- download coordinate values;
- calculate movement features;
- calculate PCA;
- calculate individual identity K;
- inspect any Mini or Rhino behavioural outcome.

## Sources

Same Figshare article used by the existing Teshima programmes.

Filename pattern:
`Env{environment}_Bat{bat}_no{trial}.csv`

Frozen source ID ranges inherited from existing scripts:

- Miniopterus: file IDs 55033796–55033850
- Rhinolophus: file IDs 55033853–55033985

## Mini structural template

Construct the exact count matrix:

[
n^{Mini}_{e,b} = number of source trajectory files
]

for every Mini bat × environment cell.

The total must equal the already-known structural total:
**19 trajectory files**.

## Rhino pool

Construct:

[
n^{Rhino}_{e,b}
]

from filename metadata only.

## Exact support mapping

Mini has four biological bat labels.

For every:
- choice of four Rhino bats from the Rhino candidate set;
- bijection of the four Mini labels to those four Rhino labels;

declare the mapping structurally feasible only if for every Mini cell with positive count:

[
n^{Rhino}_{e,map(b)} ge n^{Mini}_{e,b}.
]

Environment numbers are matched literally (Env1 to Env1, etc.).

For every feasible mapping report:
- Mini→Rhino label mapping;
- number of required trajectory files;
- product of within-cell combinations
  (prod {n^{Rhino}_{e,map(b)} choose n^{Mini}_{e,b}}),
  capped in reporting at 10^12 but computed exactly as Python integer.

## Gate

The matched-support outcome test may open only if:
- at least **4** feasible Mini→Rhino mappings exist;
- at least **100** distinct exact support-matched Rhino trajectory subsets exist across feasible mappings.

These thresholds are frozen before any matched-support movement outcome is calculated.

## Next test if gate passes

A separate contract will freeze:
- number of support-matched Rhino resamples;
- PCA/identity estimator;
- permutation calibration;
- positive-control detection fraction.

No behavioural outcome may be opened in this preflight.
