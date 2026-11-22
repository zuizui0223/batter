# Goldshtein original GPS height: independent reference-map + EGM96 non-identification audit (2026-11-22)

**Status: measured SOURCE-DATUM QC only; no valid terrain-relative bat altitude and NO resource→height prediction.** This extends the source upload, the recovered independent 414-cactus legacy flower census, and the previously frozen GGA/drone altitude diagnostic. Earlier source outcomes and source-composition gates remain unchanged.

## Source and reference files

Actual user-uploaded claimed Mendeley v1 ZIP DOI [10.17632/jxghjjsttw.1](https://doi.org/10.17632/jxghjjsttw.1), SHA256:

    069b12e6383fa7d84a1f7164fcfe16b0ce693469a7661262ce1a0ed73e423ebb

No publisher-computed checksum matched independently. The original ZIP has **eight GPS-animal-associated cactus.xlsx maps**, four with an actual column named alt (1,951 individually mapped cactus rows with finite numeric altitude), in addition to the **332 drone alt positions** of the recovered legacy open flowers.xls. The latter drone field is spatially different from the eight GPS-animal cactus maps and the two altitude references must **never** be pooled as if they refer to a single local datum and field.

A source-hash-locked original GPS RMC/GGA time+XY pairing independent of altitude response, and source cactus-map nearest-neighbor geometry (latitude/longitude ≤15m and ≤50m), yielded:

| Original source comparison | Support | 5th | 25th | Median | 75th | 95th |
|---|---:|---:|---:|---:|---:|---:|
| raw GGA altitude minus closest **same-animal cactus-map alt**, ≤15m | 36,082 fixes, 4 bats | −83.02 | −64.70 | **−57.23** | −51.46 | −34.62 |
| Same comparison ≤50m | 48,948 fixes, 4 bats | −83.14 | −64.54 | **−56.86** | −50.42 | −28.46 |
| Prior *separate drone survey altitude* ≤15m | 499 fixes, 5 bats | −211.28 | −102.06 | **−86.51** | −81.61 | −74.21 |

Differences are metres. Within the four source animals having independent cactus-map altitude values, the four individually computed ≤15m difference medians range **−79.35 to −28.20m** (spread **51.15m**). A few bats and temporally autocorrelated fixes generate tens of thousands of lines; n=36,082 is **not n=36,082 independently observed animals/decisions**. The sources have potentially different survey/geodetic altitude conventions, so differences between cactus-map and drone reference values are **not** direct biological height contrasts.

## Independent public geoid grid sensitivity

Independently checked the local, installed [PROJ EGM96 15-minute geoid-grid](https://proj.org/operations/transformations/vgridshift.html) at the **actual source cactus and drone coordinates without emitting them**. Local grid path /usr/share/proj/egm96_15.gtx, SHA256:

    c02a6eb70a7a78efebe5adf3ade626eb75390e170bb8b3f36136a2c28f5326a0

Using the explicitly recorded PROJ vgridshift sign convention (+multiplier=1):
- four bat cactus-alt map coordinates: EGM96 shift 5th/25th/median/75th/95th = **−33.75/−33.41/−32.95/−32.84/−32.82m**;
- 332 drone reference coordinates: **−33.27/−33.26/−33.26/−33.26/−33.26m**.

**EGM96 is NOT the EGM2008 model used in the original paper.** In addition, original NMEA GGA's altitude field is *nominally* metres above mean sea level in the NMEA protocol, but its geoid separation is absent in the source files; the Goldshtein paper describes use of GPS ellipsoid altitude and an EGM2008 + Google Maps elevation subtraction. The source GPS device's actual altitude datum and the drone or bat-map alt datum cannot be independently identified from the existing columns. Simply adding or subtracting the approximate 33m geoid shift does **not** document a valid AGL, nor explain the different bat-specific source-altitude references. A single offset inferred using these recorded bat altitudes is an outcome-informed adjustment, not independent calibration.

**Mathematical boundary:** only if ellipsoidal GPS h, actual EGM2008 undulation N and independent terrain height H have common verified datums is AGL=h−N−H defensible. Which original GGA field represents h or H is not currently source-confirmed. NMEA metadata alone cannot prove which effective reference a particular device implementation emitted. The previous observed median GGA minus drone alt ≈−86.51m is a reference mismatch, **not evidence of underground flight**, and we will not fix it by forcing median height ≥0.

## Reproduction and biological decision

[Original-source GPS/cactus-map/EGM96 audit code](goldshtein_cactus_alt_geoid96_sensitivity_v1.py), [machine-readable aggregate receipt](goldshtein_original_altitude_reference_EGM96_source_QC_20261122.json), and [pure-source-free regression tests](test_goldshtein_cactus_alt_geoid96_sensitivity_v1.py). The original ZIP, maps, individual IDs, cactus XY, source altitudes, timestamps and GPS fixes are **not** committed. The aggregate diagnostic was independently computed in the local source working environment and crosschecked for the original 4-bat, 36,082 ≤15m and 48,948 ≤50m source references. The runnable repo source-specific script requires original ZIP, public EGM96 .gtx with exact SHA and artifact_tool, numpy, scipy, pyproj; GitHub source-free CI does NOT re-fetch or expose original animal data.

Even a valid GGA vertical reference would still require appropriate 3D sampling proposals and same-night resource inclusion from the **121 repeatedly measured drone cacti** (206 others not numerically observed daily). Current 2016 drone source has only **5 bats / 6 candidate bat-night mornings** with 99 XY proximity episodes; these are not 99 independent choices or nectar-drinking events. Monitoring of only flowering cactus subset and exact next-morning date alignment remain unverified. The **full 5D measured resource×within-state-height, field and regional species SDM gains remain NULL**.

**Decision:** Stage A remains a structurally joinable cactus-XY source but STOP until source-corrected GPS AGL and independently surveyed availability are established. Stage B partial real flower observations exist but STOP for the same height/detection/day issues plus missing direct counts for many cacti. Preserve original source-independent Hendel/Ducke positives, closed vertical negative results, protected JAE/BE/batter and esdm mains; PR #102 remains Draft.
