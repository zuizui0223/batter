# 2026 flight ear-gaze dataset: pre-outcome individual identity source gate v1

**STRUCTURAL SOURCE / ELIGIBILITY ONLY. No bat kinematic or acoustic measurement values opened.** Separate new independent PNAS source; not an amendment to JAE submission or previously fixed P1–P2, not a replacement of previous 3D individual height results.

## Frozen source provenance
Häfele, Wisniewska, Vesterholm & Jakobsen (2026) PNAS *Echolocating bats sacrifice binaural localization cues for target-focused hearing during high-speed foraging*, DOI **10.1073/pnas.2605701123**, published July 28 2026.
Published author's code: https://github.com/fhaefele/target-focused-hearing-of-echolocating-bats-pnas
Author's compiled dataset v1: https://zenodo.org/records/20927789 DOI **10.5281/zenodo.20927789**. The original authors state the full raw recordings are available on request only, while compiled data are enough to redraw figures.

Important published discovery PRIOR ART: ears orient toward targets during high-speed flight, focusing receiver beams and reducing interaural level difference; **NOT novel if reproduced**. This study does not involve freely flying groups of multiple interacting bats or randomized social-sonar interference. Do not use its within-species flight physiology to demonstrate a social-acoustic replacement for spatial partitioning.

## Source-compatible structural scope
Zenodo v1 explicitly lists compiled CSV exports for three species and a 6.5 MB curve-of-ear-separation CSV:
- earTipSep_SSblin_500mmRange_full_nlme_vms_tm_CIbands_MC.csv (6.5MB; likely model prediction curves, may not have individual bat IDs).
- mdau_basement_config_UCLOUD_01_collect_20241008_203617_processed_20251112_szred_lcs_20251114_PARTIALLY_export.csv (5.6MB).
- ppyg_config_UCLOUD_01_collect_20241008_122450_processed_20251112_szred_lcs_20251114_export.csv (14.9MB).
- full mdau export 31.3MB, mnat 71.2MB; may be too large for source-only preflight, do not pull them until justified.
- small BEAM_INFLIGHT.mat 4.5MB, spectral and beam models only; cannot assume trialwise bat ID.

The title and authors' Figure 1 code identify mnat, mdau, ppyg as different SPECIES; their means are not new biological individual replicates. Source code `figure_02.m` references an in-memory `DATA.h{1}.h.attr.BatID`, but it DOES NOT prove the compiled public CSV exports contain enough persistent ID and bout identity for across-bout prediction.

## Gate 0 — verified original ZIP-free official metadata only
Read Zenodo API `https://zenodo.org/api/records/20927789`, check record DOI and exact v1 record ID; list filename, bytes, MD5/SHA reported by Zenodo and public download URL; record source-code GitHub HEAD.
Refuse silently selecting a different Zenodo version, renaming files, figure reconstruction from plots, or downloading 3GB MATLAB movies. If API blocked, STOP_ZENODO_SOURCE_INACCESSIBLE.

## Gate 1 — schema-only inspection
For **at most** three declared compiled CSVs with size <=16 MiB, request the Zenodo-advertised official content links using a single HTTP GET streamed with <=8192 raw bytes read per file, enough for the first CSV header without reading the numerical rows. Do NOT read numeric variables beyond first header. Record actual status, header string, columns and available row count ONLY if metadata explicitly supplies it.
- Need fields for **stable physical individual bat ID**, independent flight/bout/session ID, 3D position/heading or kinematic state, and ear/pinna orientation relative to prey/call.
- Models/CI prediction curves without source-independent bat ID are INELIGIBLE, regardless of row count.
- Raw 2D/3D coordinate frame counts do not represent independent bats; group by physical bat then independent bouts.
- If file stream or schema unavailable, fail closed; DO NOT try undocumented authenticated URLs or infer table structure from file names.

## Gate 2 — categorical counts only if header explicitly supports ID and bouts
Require >=5 distinct physical individual IDs (not 5 species); each >=3 fully distinct independent bouts with relevant actual original posture/ear measurement, and >=15 total held-out bouts across at least two conditions at comparable task speed/distance. Source must support bat & bout mapping and measurement units. If it fails, STOP_NO_INDEPENDENT_INDIVIDUAL_BOUTS. This is source-based eligibility, not p threshold. No numeric angle, trajectory or ear separation opened at this stage.

## Conditional future numerical question (NOT authorized in this gate)
Can earlier bouts from the SAME bat better predict its next independently held-out ear-to-flight-heading alignment or target-centered receiver-gaze offset than task-distance/speed-matched OTHER bats, given all bats already aim toward prey on average? This is individual-vs-shared control under truly held-out bouts, not a new claim that target gaze occurs. A new outcome contract is required *after* categorical Gate 2 passes and BEFORE any numeric angle/velocity values are opened. Bat-level uncertainty and context adjustment must be frozen with realistic n.

## Rigorous ecological limitation
Even if a stable personally predictive ear/heading residual were supported here, it would not prove learned strategies, social masking protection, prey intake improvement or the maintenance of 3D niche overlap. It would only provide a **new, independent 3D sensorimotor individuality domain** under controlled foraging.

Verdict must be one of STOP_ZENODO_SOURCE_INACCESSIBLE, STOP_CSV_SCHEMA_UNAVAILABLE, STOP_NO_INDEPENDENT_INDIVIDUAL_BOUTS, or PASS_SCHEMA_CANDIDATE. Store no observed physiological values in this structural phase.
