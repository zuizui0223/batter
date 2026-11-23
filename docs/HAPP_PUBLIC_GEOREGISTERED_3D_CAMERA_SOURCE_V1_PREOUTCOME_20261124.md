# Open GPS-calibrated thermal bat 3D v1 — genuine geographic source admission, no field outcomes (2026-11-24)

## Why this source is on the same main research line
The Münster source in `docs/MUENSTER_REAL_XYZ_AND_LIDAR_COLOCATION_CLOSEOUT_20261124.md` contains **197 authentic local 3D coordinates**, but no independently surveyed world controls. An **independent publication** now offers a potentially executable solution to this *measurement-calibration* bottleneck, not yet a bat×LiDAR forest niche.

Happ, Schmid & Häckel (2024), *UAV-Based 3D-Calibration of Thermal Cameras for Bat Flight Monitoring in Large Outdoor Environments*, *Remote Sensing* 16(24):4682, DOI **10.3390/rs16244682**. The author reports two German wind-farm locations and median georeferencing calibration error ~1.8m using drone GPS flight tracks. That **published result is PRIOR ART**; replicating it is a technical pipeline test, never a new ecological finding.

Original author open code+data at `christofhapp/batflight3D_publication`, exact tag `v1.0.1`, commit **`34d2f56bcee1eab9207890938aedd90a079bfcde`**. Public README explicitly states that `DRONE_SIM_PTS.csv` contains time, two synchronized camera image pixel locations `x1,y1,x2,y2` and drone GPS `lat,lon,height`. The author code `batflight3d.py` uses synchronized drone 2D image positions + GPS for camera calibration and stereo triangulation. Source `data/parameters_Turbine2.json` contains thermal camera intrinsics, as well as a real GPS reference coordinate, and `animal_flightpath_example.py` documents one recorded bat thermal stereo segment in `Turbine2_Setup4_2022-06-23_21-41/images/bat_recording`. This is actual observational metadata, not a bat XYZ source yet.

### Frozen source candidates
- **Turbine2, Setup4**, two consecutive *calibration drone* flights:
  - `data/Turbine2_Setup4_2022-06-23_21-29/DRONE_SIM_PTS.csv`; original Git blob SHA1 **`9114254bde93b1ecae3d2a4df45b9219216fac0c`** (540,128 bytes).
  - `data/Turbine2_Setup4_2022-06-23_21-41/DRONE_SIM_PTS.csv`; original Git blob SHA1 **`ec6435a2cc8370696a68892e839a5b387d9d64e1`** (649,690 bytes).
  - `data/parameters_Turbine2.json`; original Git blob **`60315eacc821d266ebebe373b348bcb125cb3ad3`** (1,084 bytes).
- The source also includes one real bat video segment and source image-coordinate `IM_PTS_cam1.csv`, `IM_PTS_cam2.csv`; however, **no original bat XYZ, species IDs or original bat-specific q** is yet source-admitted and no score is authorized.
- The study includes two geographic turbine systems but **Setup4's paired flights are one camera deployment at one turbine**, not independent forest sites. No vegetation LiDAR data matching this source has been located.

### V1 metadata-only gate, before reading drone GPS and calibration score
1. GitHub Actions clone public original `v1.0.1` at exact commit; use source commit hash, actual Git blob SHA and file byte sizes. **Stop** on a mismatch; no moving branch name source substitutions.
2. Read only column/header names and row widths/counts of two original GPS+pixels CSV; field definitions `nr,datetime,x1,y1,x2,y2,lat,lon,height` required. Read source camera-intrinsic array shapes and reference coordinate **existence** only (not per-flight GPS route), and bat_recording file **names/sizes** and code presence. No numeric GPS/pixel/animal rows inspected or scored in V1.
3. Require both drone files >=20 data rows, both camera pixel pairs and GPS coordinates in exactly one original source row, at least 1 valid intrinsic calibration per camera and original reference. Fail closed on unknown source fields/duplicate source headers. Source geometry/response remains unviewed. A source with author-published GPS altitude is **not automatically LiDAR-orthometric z**; vertical datum must remain unknown without independent source documentation.
4. A separate **V2 scoring contract must be committed before opening source drone GPS**. Proposed technical endpoint: train source stereo camera pose on one drone flight and **predict 3D GPS locations from image positions on the other flight** under same camera setup, in both directions, with original-source uncertainty honestly retained. No flight-point pseudo-independent ecological p-values; flight is the independent experimental unit. If one direction fails, do NOT drop it to make transfer positive. No bat XYZ, vegetation, LiDAR or clutter effect may be inferred from drone accuracy.
5. If author setup moved between flights, document that as transfer failure, not calibration rescue; source file names are the frozen independent split.

### Claim ceiling
Positive technical camera reprojection and 3D tracking transfer would show *working geographic 3D camera reconstruction from independent GPS calibration in a wind-farm setup*, already demonstrated in the author's 2024 paper. It **does not** establish bat air-volume use intensity, species niche, forest clutter, cross-habitat transfer, inverse observation K, or verify the Münster camera setup. The scientific Gate B/C for the 3D forest SDM remains unmet until independent calibrated forest LiDAR and bat tracking share the same world coordinates.

All work on unmerged Draft PR #103; canonical `batter/main` JAE, ODSP N2, esdm E5 unchanged.
