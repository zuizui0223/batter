# Terrain geometry matters, but is not a causal account of individuality

**Audit date:** 15 October 2026  
**Status:** exact source-locked *arithmetic and interpretation* of original successful tracking workflows. Not a new GPS/DEM download, a re-estimation of animal distributions, independent analysis, null/permutation test or preregistered comparison.

## Ecological question

Can stable personal patterns of flight-height use be distinguished from the vertical structure of the landscape? The original source offers a valuable **paired processing contrast**: identical eligible original tracking-session material evaluated using source-native altitude and, separately, the **native GPS-height minus interpolated digital terrain elevation** (a terrain-relative proxy). These transformations must not be treated as a randomized change of natural topography.

## Four matched original 500-m panels (two species)

| Panel | Eligible bat n | Original altitude field | V_native | V_rel | ΔV (rel − native) | S_native | S_rel | ΔS (rel − native) |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| *Hypsignathus monstrosus* | 8 | ellipsoid | +0.1707 | +0.0419 | **−0.1288** | +0.1029 | −0.0158 | **−0.1188** |
| *Phyllostomus hastatus* 2022 | 5 | MSL | +0.0660 | +0.0996 | +0.0336 | −0.0166 | −0.0090 | +0.0076 |
| *P. hastatus* 2023 | 6 | ellipsoid | +0.0542 | +0.0769 | +0.0227 | −0.0039 | +0.0163 | +0.0202 |
| *P. hastatus* 2016 | 9 | MSL | +0.1452 | +0.0787 | **−0.0666** | +0.1304 | +0.0289 | **−0.1015** |

All source statistics, including exact native and terrain-relative values, reside in the original successful frozen record. \(V\) is **same-individual minus other-individual common-horizontal conditional vertical-overlap contrast**, whereas \(S\) is **other-individual minus same-individual normalized loss of joint XY–height probability overlap**. The two are not measurements of one shared effect scale. The Δ columns are direct arithmetic differences, **not independently null-calibrated treatment effects**, and carry **no uncertainty interval or p-value**. Original source horizontal overlap contrast \(H\) remained the same to machine precision between the two processing regimes, which confirms the source's XY baseline was not silently switched for this comparison.

**Nontrivial descriptive result:** the sign of the *processing change* is **not universal**: V increased in two panels and decreased in two, and the same is true of S. The panels showing the largest positive native S values — *H. monstrosus* and *P. hastatus* 2016 — showed substantial attenuation after terrain subtraction. In *H. monstrosus*, S even crossed zero. Yet positive original terrain-relative individual fidelity V_rel was **source-supported in all four panels**, while positive additional S_rel segregation was **source-supported in zero of four**, under the later original permutation family. Original co-use and multiplicity sensitivities are separate analysis objects, not new tests contributed here.

## Important vertical datum and biological boundary

- The original GPS field for *H. monstrosus* and *P. hastatus* 2023 is `height_above_ellipsoid`, whereas 2022 and 2016 *P. hastatus* use `height_above_msl` as their **original primary fields**. The preserved source contracts explicitly specify these distinct vertical datums; they must not be treated as calibrated absolute heights on a common vertical reference.
- The terrain-relative variable is **GPS-native height minus a locally interpolated DEM tile elevation**, not a sensor measurement of actual distance above canopy or ground. In ellipsoid-height sources, local vertical-datum/geoid differences can remain if the raster and GPS reference systems differ. The precise correction and residual errors were not independently calibrated, even though subtracting a constant per session can remove additive offsets in a separate source analysis.
- Terrain subtraction may therefore alter distributions because of landscape relief, measurement conventions and/or error; these data **do not isolate a causal topographic mechanism**, and they do not prove that bats learned a terrain-based personal flight rule.
- The native-to-relative delta may depend on the source's support, height bin edges, cohort weights and source-specific instrumentation. It is not an estimate of species-wide trait plasticity, direct behavioral change or ecological fitness benefits.

## What remains scientifically defensible

The strongest **ecological** statement is that the *interpretation* of observed 3D space-use geometry is **terrain-reference sensitive**, yet source-calibrated identity in relative vertical configuration remains detectable in the selected panels. Apparent native-height 3D segregation must not be equated with added terrain-relative segregation, and no inference of zero spatial, dietary, temporal or competition-mediated partitioning follows from the absence of a positive S_rel result.

A future *separate, prospectively planned* dataset with truly harmonized vertical datums, verified task labels, fine terrain/canopy, and identical resource/route conditions could distinguish terrain following, individual patch allocation and stable within-task flight solutions. This work's original published outputs do **not** identify which mechanism is responsible.

## Exact source and reproducibility proof

- Original preserved native 3D summary: `figures/ORIGINAL_NATIVE_3D_OVERLAP_SUMMARY_V1.json`, Git blob `c1d37e42f72f59e5aba364daec9aef68b47778b6`, original workflow **36881187913**.
- Original first-stage terrain geometry: `figures/ORIGINAL_TERRAIN_RELATIVE_3D_SOURCE_V1.json`, Git blob `08631a0dce61cc47e12b2d32642c46b5759fe872`, successful workflow **36946126004**.
- Original second-stage S_rel label-null calibration: `figures/ORIGINAL_TERRAIN_PARTITIONING_CALIBRATION_V1.json`, Git blob `e969698e2a594d2eeca2631d7473e598a8a8f371`, successful workflow **36992380946**.
- The original four vertical-field contracts: `contract/hypsignathus_replication_v1.json` Git blob `1861a0a8ec625d9093919fbcf02b7ec45d3b4a92`; 2022 `contract/phyllostomus_replication_v1.json` Git blob `32e4772b1bb2d4c294c8324ca08ee8783adc12e2`; 2023 `contract/phyllostomus_2023_replication_v1.json` Git blob `0e666bc2fdd0856fd0fb55b4fbda781bc1f70852`; 2016 `contract/phyllostomus_2016_dry_architecture_v1.json` Git blob `a4dff03a800dec98f612e0873c120756a012cf4e`.
- The deterministic source-locked [machine numbers](figures/FROZEN_TERRAIN_DATUM_CONTRAST_V1.json) and [independent arithmetic/checksum gate](validate_terrain_datum_contrast_v1.py) reconstruct all displayed pairs/deltas and verify unchanged horizontal support plus the four distinct recorded altitude-field choices. **No raw GPS/DEM inputs were fetched, and full original numerical replay is still outstanding.**
