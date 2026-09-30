# Pteropus terrain-leak diagnostic contract v1

## Status

**FROZEN BEFORE ANY TERRAIN-DERIVED OUTCOME IS OPENED.**

This diagnostic is post-outcome with respect to the already known *Pteropus poliocephalus* MSL-centered PASS. It is therefore a confound diagnostic, not a new prospective replication.

## Motivation

The source-native vertical field is `height-above-msl`. *Pteropus poliocephalus* also has exceptionally strong prospective horizontal individuality under the frozen 5-km occupancy metric. Fine-scale individual use of ridges, valleys or other terrain within a 5-km cell could therefore generate a repeatable MSL-height distribution even after session-median centering.

The diagnostic asks whether the previously observed centered vertical identity survives explicit subtraction of local terrain elevation.

## Frozen source

- taxon: *Pteropus poliocephalus*
- Movebank DOI: `10.5441/001/1.5bd6pq55`
- event source: the exact raw source already pinned by the small-panel receipt
- expected raw SHA256: `13829a97110f3eff191c9066fd5bf7d20f5d1c7e26e152e6c733079fb4e179dc`
- frozen repeat individuals: `403, 588, 657, 684`
- frozen session universe: exactly the sessions in `post_freeze_extensions/small_panel_generality/height_opening_receipt_v1.json`
- session rule, event threshold, 5-km grid and common-support rule are unchanged

## Frozen terrain source

Primary terrain covariate is the public Skadi/SRTM1 HGT product served from the `elevation-tiles-prod` S3 bucket.

- horizontal datum / tile indexing: WGS84 geographic
- elevation reference: WGS84/EGM96 geoid
- nominal grid: 1 arc-second
- interpolation: bilinear over the four surrounding HGT samples
- void value: -32768
- void rule: if any bilinear corner is void, use the nearest finite sample in a frozen 7 x 7 pixel window centered on the nearest grid node; if no finite sample exists, STOP the complete diagnostic rather than dropping an event
- no vertical value, terrain-adjusted value or terrain-only response may be used to select events, sessions, individuals, grids or bins

The script must derive the necessary one-degree tiles from the frozen event coordinates and record every downloaded tile URL, byte count and SHA256 in the result.

## Primary response: terrain-relative height proxy

For every frozen event:

`terrain_relative_proxy = height_above_msl - SRTM1_terrain_elevation`.

This is called a terrain-relative proxy rather than true AGL because GPS/source vertical error and DEM error remain.

Within each frozen session, subtract that session's median terrain-relative proxy. Bin the centered values using the already-frozen centered-height edges:

`(-inf, -400, -200, -100, -50, 0, 50, 100, 200, 400, +inf)`.

Then replay the small-panel estimator unchanged:

- same 5-km horizontal cells;
- same self and other training-session definitions;
- same equal-session / equal-individual construction;
- same common-cell weighting;
- >=50 supported target events;
- equal target sessions within individual, then equal individuals;
- same whole-session identity-permutation family;
- B = 9,999;
- seed = `20261001071`.

### Primary PASS rule

Terrain-relative centered individuality is supported only if:

1. calibrated excess > 0; and
2. one-sided `p(null >= observed) <= 0.05`.

No alternative threshold is permitted.

## Secondary diagnostic: terrain-only identity

Replace the vertical response with SRTM1 terrain elevation itself, then median-center terrain elevation within each frozen session and apply the same centered bins and estimator.

- B = 9,999
- seed = `20261001072`
- PASS rule identical to the primary response

This secondary endpoint asks whether individuals carry repeatable fine-scale terrain-elevation distributions even after the 5-km common-cell standardization.

## Required validation

Before either terrain-derived result is accepted, the script must replay the original source-native MSL-centered small-panel result with the original seed and recover, to numerical tolerance:

- calibrated excess approximately `+0.16873`;
- one-sided p approximately `0.0001`;
- four evaluable individuals.

A mismatch is a hard STOP.

## Frozen interpretation table

| Terrain-relative proxy | Terrain-only | Interpretation |
|---|---|---|
| PASS | FAIL | *Pteropus* replication is robust to the tested terrain pathway; no evidence that terrain distribution alone carries the signal. |
| PASS | PASS | *Pteropus* retains centered flight-height individuality after terrain subtraction, while terrain use is also individually repeatable. The replication remains robust, but horizontal-terrain organization is an additional axis. |
| FAIL | PASS | The original MSL-centered PASS is compatible with fine-scale terrain leakage. *Pteropus* must not be used as robust evidence of terrain-independent centered vertical individuality. |
| FAIL | FAIL | The MSL-centered PASS is not robust to terrain adjustment, but the failed terrain-only endpoint does not identify terrain as the cause. *Pteropus* must be removed from the robust-replication count and treated as unresolved. |

A terrain-relative FAIL cannot be rescued by changing DEM product, interpolation, grid size, session definition, bins, event threshold, or individual subset.

## Claim boundary

This diagnostic can strengthen or weaken the interpretation of the existing *Pteropus* PASS. It cannot make the existing small-panel programme prospective again, and it cannot validate the post-hoc resource-anchoring hypothesis.
