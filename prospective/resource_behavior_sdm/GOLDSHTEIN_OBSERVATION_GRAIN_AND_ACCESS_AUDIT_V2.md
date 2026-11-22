# Goldshtein 2020: field observation grain and archive access audit v2

**2026-11-22 source access UPDATE supersedes prior HTTP401-only status:** The user provided the claimed Mendeley v1 outer ZIP. Its exact local bytes are available and SHA256-pinned (069b12e6383fa7d84a1f7164fcfe16b0ce693469a7661262ce1a0ed73e423ebb); publisher byte checksum equivalence is unverified. Eight cactus XY source maps hold 2,483 location rows and 17 animal folders provide 19 NMEA files; 42,562 of 105,580 mapped-animal de-duplicated valid GPS XY records fall within their cactus-point hulls, **NOT an independently surveyed polygon**. Four cactus maps have undated flower fields, the video sheet has dated flower observations with only nine calendar-day intersections across GPS and no verified shared individual/cactus keys, and the legacy open flowers.xls remains unparsed. Raw GPS GGA altitude has metre-unit values, NOT independently corrected AGL; the author's motion analysis references source dataCacti.mat and dataInfo.xlsx absent from the uploaded ZIP. **Stage A INPUT CANDIDATE; MODEL STOP until independent footprint/height corrections; Stage B STOP until actual matched direct flower census.** [Detailed original input audit](GOLDSHTEIN_UPLOADED_ORIGINAL_SOURCE_AUDIT_20261122.md). The previous API failure was real at its earlier date but no longer means the uploaded source is inaccessible. All existing biological height-gain estimates remain NULL.

Date: 2026-11-21. Parent draft PR #102. No new wild-bat empirical model fitted.

## Evidence before original archive can be opened

Original article: Goldshtein et al. 2020 Current Biology DOI https://doi.org/10.1016/j.cub.2020.07.079
Original data archive: https://data.mendeley.com/datasets/jxghjjsttw/1, DOI 10.17632/jxghjjsttw.1, Version 1, CC BY 4.0.
Official live API gate run: https://github.com/zuizui0223/batter/actions/runs/44683043418. The **actual artifact** goldshtein-original-source-metadata-v1 (artifact ID 14604727847) was downloaded/read 2026-11-21, not inferred from the run's red badge. It says SOURCE_METADATA_STOP, HTTP Error 401 Unauthorized; no bat or cactus original rows read and resource-height gain null.

## Field observation units: do not conflate two measurements

Published article describes:
- GPS movement tracking of **17** lesser long-nosed females (*Leptonycteris yerbabuenae*) in May–June 2015–2017.
- Mapped **locations** of approximately **3,600 cacti** in the foraging fields of **8** GPS-tagged bats; these are the animals forming the main behavioral panel (mean 2.9±2.1 tracked nights per bat).
- Repeated daily **open-flower count** observations of **414 cacti across three fields**, of which 327 were mapped by morning drone imaging over several days in 2016, and 87 were from separate manual surveys across 2015–17.
- In the published **simulation** (45 artificial bats in a 1,125-cactus field), flowers at simulated cacti are *sampled from the observed field flower-count distribution*, not continuously measured at all mapped GPS-field cacti on all bat nights.
- Flower opening is night-dependent, and flower abundance is not a constant species-level trait; direct same-night flower counts for all 3,600 mapped positions have **not been verified** in the downloadable source.

**Therefore** the existence of (i) mapped cactus **positions** for eight bats and (ii) an independently surveyed **flower-count distribution** in the wider program does **not** prove a same-place, same-date, per-cactus flower-count/GPS-height join. Until original files are inspected, the stronger "measured FOOD × GPS AGL" precondition is STOP_NO_VERIFIED_DATED_FLOWER_JOIN.

## Response leakage from original published visit definitions

Published "cactus visit" is defined by **horizontal proximity <15 m AND altitude <20 m**. Consequently, neither the author's visit label nor night-specific "core cactus" based on these visits nor height-defined foraging designation is allowed as a predictor of heldout altitude. The paper also describes an x-y-only five-minute straightness index threshold (<0.4), but any additional source- and height-dependent corrections to those labels must be excluded; independently recompute x-y-time kinematics from original fixes if released.

Primary response after qualifying AGL: continuous or pre-frozen coarse AGL height; sensor errors and terrain datum must be audited (published vertical GPS SD about 11m). No model conditioned on a height-defined label is valid.

## Two-stage field estimand, subject to new original files

**Stage A: structural-resource opportunity** — Independently mapped cactus *locations* only; relative cactus neighborhood density / distance within the **verified survey coverage polygon**. This is habitat / stable plant opportunity, **not actual same-night nectar**. Compare on matched original GPS height events:
- baseline: coarse x-y region + night clock + x-y-only movement features and terrain reference;
- plus cactus spatial opportunity (same covariates/heldout fixes).
- hold out entire individuals (8 max eligible), with a separate seen-individual whole-night target and paired survey-block permutation/null; equal animal-night weights.
- avoid occupancy/range extrapolation beyond the originally mapped resource survey region.

**Stage B: temporally matched true flower resource** — permitted ONLY if source files include per-cactus or spatially resolved **dated observed** flower counts and original GPS fixes with matching field/date and independent survey effort. Compare baseline + cactus location vs + observed bloom count, using the same bat-night GPS events, equal degrees of freedom and matched survey-block shuffles. If flowers were only sampled from a statistical distribution in the authors' simulation, keep Stage B NULL (do not rebrand simulated or imputed bloom as empirical FOOD).

**No estimation** is supported yet: original Mendeley file content inaccessible; 3D Stage A/B empirical score null; no species-range SDM, independent external source transfer, individual learned policy, or nectar-choice causality.

## Source-open readiness

A privacy-safe structural original archive ingestion tool, goldshtein_user_archive_structural_gate_v1.py, accepts a user-supplied **official Mendeley ZIP** and reports ONLY source ZIP SHA, anonymized member ordinals/types/sizes and **header-name based candidates**, without reading rows, emitting original coordinates/animal IDs or executing any source code. It cannot declare a join based on hints. Source-independent regression tests enforce URL/source & response-leakage STOP. Real output will need a second source-specific reader after actual file inventory and date/ID/height semantics are known.

Manual published source entry point: https://data.mendeley.com/datasets/jxghjjsttw/1 (Download All). This is a possible user-controlled alternative to blocked machine API, **not proof** that a browser download always works. Do not bypass source permissions or use unverifiable mirrors.

Frozen JAE/BE and main unchanged; retain this as prospective draft.
