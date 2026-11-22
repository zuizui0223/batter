# Goldshtein 2020 Mendeley v1 upload: source-admission audit, 2026-11-22


**LATER 2026-11-22 SOURCE SUPPLEMENT — SUPERSEDES LEGACY-XLS LIMITATION BELOW:** A custom read-only, hash-locked BIFF8 reader now decoded original open flowers.xls; **414** original source cacti, **327** drone-census (121 monitored with 1,016 numeric daily records, 206 unmeasured daily, never imputed zero), **87** additional manual. Crucially, although drone mapped cacti are spatially separate from the *eight per-bat cactus catalogs*, the original bat GPS tracks actually pass near the independently observed drone cactus sites. Provisional Sonora UTC−7 local evening/morning alignment gives **227** GPS fixes within 15m of a cactus with direct dated flower count, **99** height-blind proximity episodes on **5 bats/6 candidate nights**; 22 episodes have positive source flower observations. This is direct *spatial+temporal source eligibility* and NOT feeding events. A frozen GPS GGA vs independent drone altitude audit found 499 ≤15m source pairs and **−86.51m median GGA-minus-drone-alt**, while the NMEA geoid separation field is blank. **Raw altitude and drone alt are not qualified AGL**; survey effort and authored calendar semantics remain unresolved. [New full result](GOLDSHTEIN_REAL_LEGACY_BLOOM_GPS_NIGHT_SOURCE_QC_20261122.md). The earlier statements that legacy XLS was unparsed or actual GPS never approached its flowers are historical and superseded. Strict field height effect remains NOT ESTIMATED.


**This is original user-upload ZIP structural/XY evidence, not a new 3D resource × height fit.** Claimed published DOI: [10.17632/jxghjjsttw.1](https://doi.org/10.17632/jxghjjsttw.1). SHA256 of the actual uploaded ZIP:

    069b12e6383fa7d84a1f7164fcfe16b0ce693469a7661262ce1a0ed73e423ebb

The upload resolves the old local API HTTP401 obstacle but the exact bytes have **not** been independently matched to a publisher-provided checksum. It is user-provided source with traceable hash, not independently authenticated publisher equivalence. No source coordinates, animal IDs, plant IDs, precise dates, unaggregated records or height outcomes are committed.

## Verified inventory

55 outer ZIP entries, 389,648,949 bytes uncompressed. Nineteen NMEA-GeoTag files from **17 animal directories**, eight same-directory cactus position spreadsheets, 13 XLSX spreadsheets overall, one legacy OLE2 Excel open flowers.xls, MATLAB scripts and a nested Foraging model ZIP dominated by **simulation** MAT outputs. Nested simulation values are not observed food resource fields.

Spreadsheet inspection used artifact_tool. The eight cactus-position XLSX first worksheets contain **2,483 rows with lat/lon coordinates**; the published approximately 3,600 mapped cactus positions **do not equal** 2,483 supplied XLSX records. Four tables contain an altitude column and four tables a column named openFlowers/open flowers. In the four undated flower columns 225 source rows have a positive count and 160 have no count. **None of the eight cactus location tables has its own observation-date field.** Do not set missing flower counts to zero or invent remaining cactus positions.

Video Analysis.xlsx has 2,726 observation rows, 32 distinct Excel-converted dates, 35 distinct local numeric cactus labels, numOfFlowers, and a bat field with only two distinct nonempty values, not verified GPS tag IDs. Only **nine calendar dates** overlap any GPS RMC date (**six** are shared with the eight mapped animals' RMC dates, which span 25 UTC dates and 33 bat×UTC-date pairs); this is mere programme-wide *date equality*, not a verified shared plant/field/individual key or a same-night direct nectar count. RMC date uses UTC; video local dates/timezone are not yet audited. The separate date-bearing nectar spreadsheets have no same-date overlap under straightforward Excel serial-date interpretation. The video table has 2,406 nonempty bat-column entries but just two distinct values; **zero** of those values directly equals one of the eight GPS mapped-animal tag strings. The 72 video cactus-folder labels and original video filenames also contain **no direct mapped-GPS-tag identifier match**. This is a strict *literal-key check only*: an unpublished crosswalk could still exist; overlapping local cactus numbers are not a safe shared ID. The legacy open flowers.xls exists but its sheet/row schema was **not decoded** by the supported XLSX parser, so a quantitative flower join is not disproven: it remains unknown.

## Original GPS geometry, without opening a height outcome

Across all 19 NMEA files: 315,929 GGA sentences, 205,166 valid positive-fix GGA lines with numeric metre altitude fields, 205,166 valid RMC position reports across 34 UTC dates, and 110,763 invalid RMC reports. Merely confirming the presence and metre unit of an altitude field does NOT validate **height above ground**. Raw NMEA GGA is not already terrain-corrected AGL.

Within the eight GPS folders with cactus XLSX maps: **137,267 raw valid RMC lines** in 10 NMEA files; **105,580** timestamp/XY-deduplicated source fixes (31,687 repeated records removed); all eight mapped animals have two or more unique GPS UTC dates, and four have three or more. For each bat separately, cactus lat/lon coordinates were projected to a local planar frame and a convex hull constructed from **all mapped cactus points**. Exactly **42,562/105,580 (40.3%)** distinct GPS position/time fixes fall inside those *mapped-cactus convex hulls*. This is a real **spatial overlap diagnostic**, NOT survey footprint or ecological availability. A separately implemented SciPy-Delaunay calculation of all mapped-cactus polygons and unique valid source GPS fixes reproduced **42,562 inside / 105,580 total exactly** without reading altitude. Survey polygons, unbiased cactus absence coverage and map sampling frames are not established by a convex hull.

The original MATLAB script movementAnalasys.m directly builds a convex hull of **visited cactus** positions for one of its own area/density metrics, which would be **response-conditioned** if reused as an independent surveyed habitat footprint. The same original script requires absent dataInfo.xlsx, redBlueGradientColor.xlsx and per-bat dataCacti.mat files. The accompanying compressed GPSdata_CorrectedLowSample.mat exposes per-bat aggregate visit/distance histogram variable names, not a qualified original per-fix corrected AGL series. Authors' terrain reference / sensor correction must be independently recovered; the original scripts were not executed and no GPS GGA altitude numbers were analyzed here.

## Reproducibility and claim STOPs

The new [source-hash-pinned XY-only reader](goldshtein_original_xy_source_audit_20261122.py) uses artifact_tool for XLSX and only RMC XY/time for geospatial overlap, never GGA height, visit labels or individual source outputs. The [anonymized source structural receipt](goldshtein_original_source_structural_receipt_20261122.json) records all counts and explicit unresolved inputs.

| Admission | Decision |
|---|---|
| Actual uploaded archive reads and matches the newly recorded uploaded SHA | PASS for local use; independently publisher-digest-authenticated = false |
| Same-animal geographic cactus map and raw NMEA GPS XY | PASS structurally for eight mapped animals |
| Spatial coverage evidence for an unbiased cactus-opportunity reference | **STOP:** mapped-cactus convex hull is not independent survey polygon |
| GPS **terrain-relative** per-fix AGL calibration | **STOP:** raw GPS GGA altitude metre fields are not author-verified AGL |
| Independently observed and matched same-cactus, same-night flower amounts, surveyed effort | **STOP:** no full original join established; legacy .xls still unparsed |
| Height-blind behavioral state | **STOP:** published visits use altitude less than 20 m and thus leak the response |

Stage A remains **SOURCE GEOMETRY CANDIDATE ONLY** and Stage B **STOP_NO_VERIFIED_INDEPENDENT_DATED_BLOOM_JOIN**. Both original resource×flight-height heldout effects and the regional bat species SDM remain **NOT ESTIMATED**. This upload materially changes original source accessibility, but **does not prove food determines flight height**.

Next minimum source needs: a defensible independently surveyed mapping boundary and true GPS terrain/datum correction for Stage A; only then freeze a same-support heldout conditional-height comparison. For Stage B, a verified census table with direct flower numbers, cactus/field/night keys and sampling effort is necessary; incomplete surveys require a new predeclared design rather than pretending that nonobserved plants carry zero flowers.

All PLOS/Krauel/Cistrone closed tests, earlier Hendel/Ducke evidence, seven strict null entries, batter/esdm main and JAE/BE frozen releases remain unchanged. PR #102 stays Draft.
