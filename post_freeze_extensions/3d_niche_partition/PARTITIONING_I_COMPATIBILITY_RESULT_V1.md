# Partitioning calibration result v1 — I compatibility bounds

## Status

POST-OUTCOME DIAGNOSTIC under `PARTITIONING_CALIBRATION_CONTRACT_V1.md`.

The four authoritative corrected co-use workflow artifacts were reopened without changing encounter sets or endpoints. The frozen dyad medians were resampled with replacement (9,999 replicates; panel-specific frozen seeds), while each panel's completed phase-shift null mean was held fixed.

| panel | dyads | observed excess I (m) | dyad-bootstrap 95% interval (m) | positive upper bound (m) |
|---|---:|---:|---:|---:|
| *Hypsignathus monstrosus* | 22 | -1.983 | -4.808 to +0.985 | +0.985 |
| *Phyllostomus hastatus* 2022 | 10 | -0.947 | -3.207 to +1.918 | +1.918 |
| *P. hastatus* 2023 | 8 | +3.574 | -4.633 to +11.729 | +11.729 |
| *P. hastatus* 2016 | 8 | -0.854 | -3.127 to +1.128 | +1.128 |

## Interpretation

For the three panels that did not support the predeclared upper-tail co-use test, dyad-level resampling constrains the upper endpoint of the compatible panel-level excess to approximately 1–2 m. Thus their null results are not simply compatible with arbitrarily large systematic co-use-dependent vertical separation.

The 2023 panel remains the sole positive result under the original frozen phase-shift test (+3.57 m, one-sided p=0.0231), but the dyad-resampling interval is wide and crosses zero. This does not reverse the original permutation decision; it shows that the positive panel-level signal is heterogeneous across only eight frozen dyads and should remain an exception rather than a general interaction rule.

Across panels, the completed evidence therefore supports a sharper statement: terrain-relative individual vertical-strategy fidelity can persist while systematic additional vertical separation during local co-use is small or unsupported in three panels; the one positive panel is heterogeneous.

These are compatibility intervals, not post-hoc power calculations and not formal equivalence tests.

## Provenance

Authoritative corrected co-use workflow run: 36953712597.

Artifacts reopened:
- Hypsignathus: 11205510244
- P. hastatus 2022: 11204898247
- P. hastatus 2023: 11205525158
- P. hastatus 2016: 11205780190

No encounter, dyad, scope, synchronization tolerance, terrain processing, endpoint definition, or primary statistic was changed.
