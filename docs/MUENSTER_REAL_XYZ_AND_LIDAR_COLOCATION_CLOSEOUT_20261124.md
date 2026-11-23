# Real public 3D bat flight source admission and physical-air-volume blocker (2026-11-24)

**State:** Authenticated **genuine XYZ** now available and source-numerically validated for Münster thermal flight tracks. **No validated field vegetation/clutter relationship, no field 3D air-volume SDM and no forest-heldout prediction.** This distinction is essential; software CI success is not ecological confirmation.

## Verified original sources

Heim et al., original publicly released Zenodo DOI [10.5281/zenodo.7797077](https://doi.org/10.5281/zenodo.7797077), version `7797077`; original `3DTracks.zip` exactly MD5 `648c3effc18d43731f6ac267493046b9`, SHA256 `1f30d61e66eec1ad078ad114070ae25a543fc7fb86cbae03e52f9a0ee6ff0010`, **61,487 bytes**, plus original `README.md` SHA256 `649314b28364bb99794a49962f33ff9b6e88f9919ebc8d84f62d05e25ef51746`. The publication *Guild-specific response of bats to motion-triggered LED lighting of bicycle trails* (Heim et al. 2024, [DOI 10.1111/csp2.13116](https://doi.org/10.1111/csp2.13116)) describes a Münster Germany 1.5km corridor near Dortmund–Ems canal and forest Große Lodden, five fixed lamppost detector sites, with stereo thermal 3D tracks on **October 18–19, 2022** during lights-off periods. The general acoustic counts from five stations and these local stereo 3D tracks are **not interchangeable** and the thermal files lack independent bat species IDs.

The strict source-only ZIP and README admission [Actions #45204604633](https://github.com/zuizui0223/batter/actions/runs/45204604633), artifact **14834325184**, verified original MD5 and structure **before any numeric bat XYZ was examined**. ZIP includes **18 published members**: 16 XYZ CSV files and two images. Original filename `_uninterrupted` variants duplicate the *same bat-file/target*; source files include night-specific `lamp_xyzpts.csv` local landmarks.

Original frozen V2 strict 3-column numeric import [Actions #45205629303](https://github.com/zuizui0223/batter/actions/runs/45205629303) returned **source-format STOP** before reporting scientific data. Why: each source CSV starts with first-row field names `pt1_X,pt1_Y,pt1_Z`, and the two `bat8` normal/variant files contain **`pt2_X,pt2_Y,pt2_Z`** as additional 3 XYZ columns. The successive source-only grammar/type/header diagnostics (e.g. [#45206599640](https://github.com/zuizui0223/batter/actions/runs/45206599640)) established this *without numerical coordinates*; no 3D bat height profile was used to revise the parser. This distinction and all original scientific source STOP receipts remain frozen.

Under the separately documented v2.3 schema correction [preoutcome contract](MUENSTER_THERMAL_3D_TRACKS_V2_3_SCHEMA_CORRECTED_PREOUTCOME_20261124.md), original full XYZ rows were first parsed and the numeric original-source **geometry QC** succeeded [Actions #45207678824](https://github.com/zuizui0223/batter/actions/runs/45207678824), artifact **14833363665**. The source totals, counting only canonical non-`uninterrupted` files and only full finite `(X,Y,Z)` triples, are:

| Original night | Unique bat filename ID | Nonempty pt1/pt2 coordinate streams | Finite local XYZ triples |
|---|---:|---:|---:|
| 18 Oct 2022 | 8 | **9** | **157** |
| 19 Oct 2022 | 3 | **3** | **40** |
| **Total** | **11** | **12** | **197** |

A second `pt2` stream in `night18_bat8` numerically explains the 9+3 **source coordinate target streams**; independent biological identity of pt2 as a ninth animal in the first night was **not verified by the header alone**. Individual XYZ rows are not independent animals; no unlocalised `NaN` was interpreted as zero activity or an AGL value. Physical XYZ source unit scale, local z datum and sample timing are unverified. Original lamp source XYZ files are **not surveyed GPS world control points**.

For reproducibility, an **independent** NumPy CSV numeric reader (not importing source v2.3 parsing logic) re-downloaded the exact author ZIP and reproduced both finite 157+40 and target-stream 9+3 counts exactly [Actions #45209312899](https://github.com/zuizui0223/batter/actions/runs/45209312899), artifact **14836165000**; its four source-free tests passed. This is independent **code arithmetic** validation on the same original release, not a second ecological dataset.

## Registration: a genuinely blocking field-data requirement, not a code bug

The previously committed `src/batter/air_volume_sdm_v1.py` defines a true cubic-metre air volume with a source-certified `air/vegetation/unknown` mask, detector observation operator K and source effort. Its synthetic source-free 11 tests passed [#45098038864](https://github.com/zuizui0223/batter/actions/runs/45098038864); no real point-cloud overlay was made.

Added `src/batter/air_volume_registration_v1.py` with a **proper 3D Kabsch rotation + translation**, an independently justified source-local-unit-to-metre scale, projected horizontal world CRS and surveyed vertical datum, plus a **heldout surveyed control point** and QC threshold. At least 3 independent noncollinear fiducial correspondences plus 1 independent validation fiducial are required; simply measuring a single lamppost through many frames does not satisfy three independent world ties. **All 8 source-free registration tests passed** in [Actions #45208774650](https://github.com/zuizui0223/batter/actions/runs/45208774650). This proves only that the method properly succeeds/stops with known-truth synthetic controls, **not** that the real Münster track XYZ are registered.

The openly published NRW [3D-Messdaten NW classified airborne LiDAR source](https://www.opengeodata.nrw.de/produkte/geobasis/hm/3dm_l_las/) covers Münster in principle (statewide ALS, variable tile dates, 4–10 returns per m²), but we have **not verified the original tracking camera/streetlamp geodetic tie points, source local scale, exact LAS tile, scan date, vertical datum, local vegetation-return classifier or scanner ray visibility**. ALS point returns without visibility cannot be reclassified into all unobserved free-air voxels. Approximate original paper map location near Große Lodden does not justify metre-scale 3D registration.

**Current field admissibility:** 
- **GATE A1 source numeric local XYZ:** PASS (197 finite, 12 source streams).
- **GATE A2 correct source true-bat species and independent field sampling:** HOLD (thermal streams do not establish individual or species IDs; 2 nights, insufficient independent forests).
- **GATE B source local→LiDAR 3D datum/rigid transform and certified free-air:** **STOP** (independently surveyed fiducials and map control unavailable).
- **GATE C known q + independent-forest 2D/3D holdout forecast:** NOT RUN (no source K/effort/local registered LiDAR).

No radiating "clutter preference" results, geographic movement metrics, 3D flight height AGL or validated 3D bat SDM may be derived from these coordinates until Gate B/C are met.

## Concrete next external data requirement

**First preference:** request restricted original Hermans et al. 2023 **co-registered LiDAR + bat XYZ** public-access approval from DataverseNL [DOI 10.34894/CHW0HB](https://doi.org/10.34894/CHW0HB). The original Hermans work already combined those observations to characterize vegetation distances; to make a novel prediction, obtain original site/night/device IDs and calibration/sensitivity K and pre-register entire-forest holdout B0 fair 2D+train height allocation / B1 height-only 3D / B2 3D vegetation proximity. Nothing has been requested or received by this code branch; **all 9 original files remain access restricted**.

**Second preference, Münster:** original study authors/site survey would need to supply (i) the original night18/night19 3D stereo camera/lamppost fiducials in a surveyed projected world CRS and height datum; (ii) independent metre scale/calibration and >=1 heldout control, (iii) exact forest site and date plus corresponding NRW classified LAZ tile & scan geometry, (iv) per-track source time resolution and separate original species/guild labels, and (v) thermal detection/localisation efficiency vs clutter/distance. Even with those, only 2 nights/one corridor do not establish multi-forest external transfer.

This source-gating outcome **moves the practical project forward** from an exclusively synthetic model to a real, independently replayed 3D tracking source and a precise list of failed registration/observability requirements, **not yet** to a real 3D bat-habitat result. Previous frozen `batter/main` JAE, ODSP-N2, esdm-E5 and PR #306–308 remain untouched. Continue only on the same prospective Draft PR #103 until the qualified new dataset is acquired. 
