# Nyctalus dist_start semantics audit result v1

## Status

**NONVERTICAL PROVENANCE / SEMANTICS AUDIT. No numeric Height or other vertical-derived field was read.**

Authoritative workflow:
- run: `36699874368`
- head: `69407faa6aab7a4744a2dd78ac6c29a63ae5c57e`
- artifact: `11088623740`
- digest: `sha256:605000276bdad1f2365cb36a10f7aef7f7873fdcd8a10907361717644331caa7`

## Result

The source field `dist_start` is numerically consistent with Euclidean distance from the first x-y position of each source track.

Best unit conversion:
- source `dist_start × 1000` = metres

Agreement:
- Pearson r = **0.9999959**
- median absolute error = **0.463 m**
- mean absolute error = **1.946 m**
- median relative error = **0.000355**
- 95th percentile relative error = **0.000437**

For **93.46%** of tracks with retained `dist_start`, the first record has `dist_start=0` to numerical tolerance.

## Interpretation

`dist_start` can be treated as a source-provided radial distance-from-track-start variable, in kilometres.

The source study reports that common noctules emerge from tree roosts and then travel across the landscape, so distance from track start is a plausible central-place / flight-stage proxy. It is not itself proof that every first GPS point is exactly the daytime roost.

Any vertical mechanism test using this field must therefore use language such as **distance from track start / central-place proxy**, not verified roost distance.
