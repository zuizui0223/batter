# Public real bat stereo-to-geographic 3D calibration: original-source technical closeout (2026-11-24)

**Research status:** calibration/geometry engineering **SUCCESS**, ecological *physical free-air-volume SDM still NOT RUN*. All original published methods are prior art. This unmerged Draft `batter` PR #103 does not alter `batter/main` JAE, ODSP N2 or esdm E5.

## Evidence and provenance

New independent open publication: Happ et al. (2024), *UAV-Based 3D-Calibration of Thermal Cameras for Bat Flight Monitoring in Large Outdoor Environments*, *Remote Sensing* 16(24):4682, DOI [10.3390/rs16244682](https://doi.org/10.3390/rs16244682). Original author data/code: [christofhapp/batflight3D_publication](https://github.com/christofhapp/batflight3D_publication/tree/v1.0.1), exact author Git tag `v1.0.1`, commit `34d2f56bcee1eab9207890938aedd90a079bfcde`. The author already reconstructs georeferenced 3D bat positions and reports a median calibration error on the order of 1.8m; **this workflow is independent computational verification of published technology, not a claim to the first 3D bat tracking pipeline**.

**Source-only v1 first:** [GitHub Actions #45245008415](https://github.com/zuizui0223/batter/actions/runs/45245008415), artifact 14852634534, original SHA256 and Git object source admission passed without original GPS/pixel outcome inspection:
- Original `Turbine2_Setup4_2022-06-23_21-29/DRONE_SIM_PTS.csv` 4,987 original stereo-drone rows, SHA256 `09193748e2dc21fedffb6f2749cdc251d94f0bd615336cdf52e20f6ee5e87802`.
- Original `Turbine2_Setup4_2022-06-23_21-41/DRONE_SIM_PTS.csv` 6,018 rows, SHA256 `1d35a3c167012e779f8ae3a95c5dcb4fbf4c5652ba7c9988bd12782172b1a5b0`.
- Exact original camera intrinsics/ref source `data/parameters_Turbine2.json`, SHA256 `74a65726d47b677009168e1c8252e6e4e6e19028c46d9bd5792337bc6c572ec5`.
- Source WGS84 drone latitude/longitude, camera pixels x1,y1,x2,y2 and author height field tied by author row; original `height` is **not verified independent AGL or orthometric datum**.

## First pre-frozen V2: entirely heldout *drone* flight

Pre-original-response contract `docs/HAPP_GPS_STEREO_V2_WHOLE_FLIGHT_HOLDOUT_PREOUTCOME_20261124.md` fixed same-camera-setup A-to-B and B-to-A drone **whole-flight** holdout, source intrinsics, GPS WGS84→UTM EPSG:32632 XY, source height channel, OpenCV `SOLVEPNP_SQPNP`, test flight triangulation, no score-driven trimming and median<=3m / 90th percentile<=10m purely **engineering screen**.

[Original V2 measured outcomes CI #45245713999](https://github.com/zuizui0223/batter/actions/runs/45245713999), artifact **14853736946**, source SHA authenticated, source-free synthetic tests **6/6 PASS**, full source numerical opening under frozen protocol. **No original row excluded by malformed/missing numeric source support**:

| Train drone flight | Independently heldout drone flight | Heldout GPS-source rows | Median 3D reconstruction error | p90 error | RMSE |
|---|---|---:|---:|---:|---:|
| 2022-06-23 21:29 | 21:41 | 6,018 | **1.488665m** | 2.144556m | 1.600956m |
| 2022-06-23 21:41 | 21:29 | 4,987 | **1.443724m** | 2.191050m | 1.606243m |

Both independent **flight** directions met the source technical screen (median<=3m, p90<=10m). Each original *frame* is highly autocorrelated with its neighboring drone frames; this is **two heldout flight-level comparisons**, not 11,005 independent sample units or an inferential ecological p-value. Error is relative to **source drone reported GPS truth** and does not account for drone GNSS uncertainty.

## First real bat stereo localizations — and independent code check

**V3 pre-source-bat-pixels freeze** `docs/HAPP_REAL_BAT_THERMAL_STEREO_V3_PRE_SOURCE_OPEN_20261124.md`: train original drone flight A only; from the original author's posted bat-video segment `data/Turbine2_Setup4_2022-06-23_21-41/images/bat_recording/`, re-read hash-verified `IM_PTS_cam1.csv`, `IM_PTS_cam2.csv`, `imagelist.csv`. **No frame exclusion based on recovered flight height**. Use original author published epipolar correspondence routine with `maxDistFromEpiline=6px` and `areaRatio=4`; triangulate only qualified source 2D pairs using drone-trained GPS camera geometry.

[First real-bat V3 CI #45246661410](https://github.com/zuizui0223/batter/actions/runs/45246661410), artifact **14854397314**, **SUCCESS**. Source candidates: 286 left-image point detections, 314 right-image detections, 257 original image timestamps. Author original matching yields **243** accepted stereo 2D pairs, **198** unique image frames with a match, **243** finite triangulated source XYZ points. Two-camera *pixel reprojection* median **0.5133967673 pixels**, p90 **1.1312282546 pixels**. No bat 3D positions were output in the public artifact, only aggregate audit counts.

**Independent V4 reproducibility check after V3 opening:** `docs/HAPP_REAL_BAT_V4_INDEPENDENT_STEREO_MATCHING_AUDIT_20261124.md` fixed an independent **stdlib CSV** source camera image reader, a *different* projective fundamental matrix formula, independently coded author-equivalent epipolar/area and sequential left/right uniqueness constraints, and fresh source stereo triangulation and reprojection. **Neither the original author's stereo matching method nor the V3 source wrapper are imported by this checker**; both share prior original drone-A calibrated P1/P2.

[Independent source-algorithm CI #45247320388](https://github.com/zuizui0223/batter/actions/runs/45247320388), artifact **14853983230**, **SUCCESS** (6 synthetic matching tests PASS). Completely reproduced **243** accepted stereo matches, **198** original frames, **243** numeric XYZ and source reprojection median/p90 with **0.0 pixel discrepancy**. This is an independent **algorithmic replay on the same original author source**, not independent site/species field replication. Original author designed method remains prior art.

## What this DOES NOT prove

The original bat recording is one **published thermal stereo example** from an open **wind-farm** camera placement. Its absolute world XY is referenced to the author GPS drone calibration (UTM32), but true bat 3D error is not independently observed by bat-borne GPS or known surveyed trajectory. A sub-pixel reprojection error is **not** evidence that absolute bat height error is sub-pixel or centimeter level; stereo range/angle calibration can retain metre-scale 3D uncertainty even with good 2D reprojectability. Bat species identity, individual number, acoustic detector q and actual bat altitude above vegetation are unknown. Original drone GPS `height` channel has no independently admitted orthometric/AGL datum.

This dataset **cannot** by itself validate the proposed 3D forest clutter-defined niche. No original source LiDAR co-registered with these real 243 bat XYZ, no certified free-air voxel mask, no species × detector K calibration and no independent unseen forests or independent bat site units. Prior original Münster thermal source separately has **197** finite *local* XYZ positions but no surveyed world registration; it is a *different location/study* and must not be mixed.

## The next actual ecological data gate

To move from proven geometry to a testable, potentially new ecology statement:
1. Admit one original **same-place/time source** with calibrated bat XYZ (or K) and a surveyed classified TLS/LAS vegetation point cloud, matched horizontal/vertical CRS and true **surveyed** reference points (not just a published approximate paper map).
2. For 1–5m clutter features, explicitly propagate physical point-location error (current independent drone calibration median~1.5m, without bat-specific extra error) and a verified air/vegetation/**unknown** visibility mask. A 20cm voxel cannot be biologically resolved just because LiDAR returns are 20cm if animal localization uncertainty is metre-scale.
3. Fit frozen **B0 2D fair background+train learned height prior, B1 true 3D height, B2 3D clutter geometry** under **the same** source detection operator and heldout whole forests/plots. Need multiple source sites and original night/track blocks. If B2 advantage is mixed or lost under plausible source q, retain non-support.

**Scientific claim boundary remains fixed:** raw XYZ source authentic + calibration engineering demonstrated; **ecological discovery not yet**. Continue on unmerged Draft PR #103 without modifying original JAE/ODSP frozen results.
