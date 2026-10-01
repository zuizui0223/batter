# Original-panel terrain-relative 3D geometry contract v1

## Status

POST-OUTCOME TERRAIN-MEDIATION DIAGNOSTIC, FIXED BEFORE ANY DEM ELEVATION VALUE FOR THESE FOUR PANELS IS DECODED.

Native-height centered-shape and 500-m 3D-overlap results are already known. This audit asks a new diagnostic question: does the repeatable vertical geometry within shared 500-m cells persist after subtracting local terrain elevation?

It is not an independent confirmation and cannot rescue or erase the native-space results.

## Fixed panels

Only the four original panels that met the fixed 500-m 3D-overlap structural gate are evaluated:

- Hypsignathus monstrosus
- Phyllostomus hastatus 2022
- Phyllostomus hastatus 2023
- Phyllostomus hastatus 2016

Tadarida and Eidolon are not added because they failed the fixed 500-m structural gate. No panel is selected by terrain outcome.

## Fixed source/session universe

For each panel:
- use the exact raw source and parser already used by the centered-shape audit;
- use the exact target-session universe used by the completed 500-m 3D-overlap analysis;
- do not add sessions after terrain is decoded.

## Terrain source

- DEM source: Mapzen/AWS Terrain Tiles Skadi HGT.
- Tile URL template: https://s3.amazonaws.com/elevation-tiles-prod/skadi/{lat_band}/{tile}.hgt.gz
- grid: 3601 × 3601 signed 16-bit big-endian elevation samples per 1-degree tile;
- sampling: bilinear interpolation at each GPS longitude/latitude;
- void value: -32768; touching a void aborts the panel rather than imputing;
- tile gzip SHA256 and byte counts are frozen in a preflight receipt before any elevation array is decoded.

## Terrain-relative proxy

For each GPS event:

terrain_relative_height = native_height - DEM_terrain_elevation.

Then subtract each session's median terrain_relative_height before applying the same centered-height bins.

For native ellipsoid-height sources, DEM terrain elevation is not in the same vertical datum. Session median-centering removes a constant datum offset within a session, but spatial geoid variation is not explicitly corrected. Therefore the result is a terrain-relative proxy, not measured AGL.

## Geometry estimator

Exactly reuse the frozen 500-m geometry:

- horizontal grid: 500 m;
- centered-height edges: -inf, -400, -200, -100, -50, 0, 50, 100, 200, 400, +inf m;
- vertical smoothing alpha: 0.5;
- pair support: each session contributes >=50 fixes within pairwise-shared 500-m cells;
- O_XY, O_XYZ, O_Z|XY, L_3D and R_3D definitions unchanged;
- primary contrast V_rel = self O_Z|XY - other O_Z|XY;
- H is expected to remain unchanged because x-y is unchanged;
- S_rel = other R_3D - self R_3D is descriptive.

## Structural gate

Use the same gate as the native 3D analysis:
- >=1 evaluable self-session comparison;
- comparisons to >=2 other individuals;
- >=5 evaluable individuals per panel.

If terrain subtraction causes a panel to become structurally non-evaluable, report that outcome and stop; no grid or threshold rescue.

## Calibration

Whole-session identity permutation within the same original cohort/exchangeability strata.

B = 9,999 per panel.

Seeds:
- Hypsignathus: 20261002031
- P. hastatus 2022: 20261002032
- P. hastatus 2023: 20261002033
- P. hastatus 2016: 20261002034

Support requires:
- V_rel - mean(null) > 0
- one-sided p(null >= observed) <= 0.05.

## Predeclared interpretation

### Native V supported; terrain-relative V supported
Individual-specific vertical geometry is terrain-robust under the DEM proxy. This is consistent with a residual vertical strategy within shared horizontal space.

### Native V supported; terrain-relative V not supported
Native x-y-z individuality is terrain-sensitive. Fine-scale terrain/landscape selection can account for the stable pairwise vertical geometry under this endpoint.

### S collapses while V persists
Individuals retain repeatable terrain-relative vertical configurations, but the stronger appearance of between-individual 3D segregation was substantially topographic.

### Both V and S remain
Strongest evidence for a terrain-robust vertical niche dimension, still not proof of competition or resource partitioning.

## Stop rule

After DEM elevation values are decoded:
- no DEM source change;
- no nearest-neighbour/bilinear switch;
- no new grid;
- no new vertical bins;
- no altered pair-support threshold;
- no exclusion of a panel or individual by terrain outcome;
- no alternative terrain-relative definition;
- no raw AGL rescue endpoint.

## Claim ceiling

This audit can distinguish terrain-sensitive realized 3D geometry from terrain-robust residual vertical geometry.

It cannot establish:
- exact canopy-relative height;
- feeding-tree identity;
- competition;
- intentional avoidance;
- adaptive resource partitioning.
