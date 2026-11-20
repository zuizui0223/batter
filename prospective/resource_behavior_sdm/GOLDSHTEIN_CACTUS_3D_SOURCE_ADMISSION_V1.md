# Independent candidate: original cactus resource × 3D bat foraging source

2026-11-20. **This is an original-source metadata gate, not a bat resource/height fit.**

## Scientific lead and original archive

Goldshtein et al. (2020), *Current Biology* DOI https://doi.org/10.1016/j.cub.2020.07.079; original published Mendeley Data DOI https://doi.org/10.17632/jxghjjsttw.1, version 1, CC BY 4.0. This is a distinct species and study from the NeoBat source record and Movebank Congo/Panama vertical-identity cohorts.

The **paper**, not yet the archived column schema, documents GPS tracking **17** lesser long-nosed bats (*Leptonycteris yerbabuenae*), independent aerial reconstruction of **~3,600 cacti** at foraging sites of **8** bats (mean **2.9 ± 2.1 nights per bat**), cactus flower counts, and GPS altitude corrected to **height above ground**. Published GPS height SD is approximately 11 m. A 2-D resource-availability observation and a 3-D flight measurement thus exist in the **same field research programme**, making this a higher-priority admission candidate than crossjoining unrelated NeoBat and batter populations.

The published authors have *already demonstrated* resource partitioning and compared an experience-based (reinforcement-learning-inspired) foraging simulator with alternative models. Those are prior art, never a new batter finding.

## Primary new research question if source files qualify

Does independent cactus resource opportunity, conditioned on horizontal cell, time, terrain and coarse kinematics, improve **out-of-night conditional height prediction** on the **same held-out GPS events**? Compare at minimum horizontal + state-only V1 against V2 (add independently measured flower resource), and a fixed matched survey-block resource permutation null. Estimate effects at the bat/night level, not GPS fix/cactus level. A local conditional height signal is **not** regional species-occupancy M3 or global generalization.

**Response-leakage prohibition:** The original paper defines cactus visits using BOTH 15-m horizontal proximity AND **altitude <20 m**. It would be circular to use these visit/foraging labels as independent predictors of held-out height. Activity states must be from x-y-time-only kinematics defined before heights open, or independently video-verified visits with annotation blinded to GPS height. The original paper's video provides a potentially independent modality, but matching video events/tags requires actual archived keys.

## Stop-first source intake

1. Official immutable publisher dataset metadata, version, file names, original file IDs and SHA256 when available; one official public API source attempt only. Never replace with an unauthenticated web mirror. Python gate and pure synthetic tests are provided; no original animal/cactus bytes are fetched.
2. Only if metadata passes: independently inspect released file *headers* to verify per-fix animal ID, timestamp, x-y, numeric altitude, height reference, and per-cactus x-y flower observations with collection date; if any missing, STOP_NO_ROW_LEVEL_RESOURCE_HEIGHT_JOIN. The original title alone does not prove row-level release.
3. Freeze usable population: resource mapping is targeted to 8 animals' foraging areas, not a random species-wide landscape. No new inferred resource absence outside mapped regions. Check whether flower counts and GPS fixes actually coincide temporally and whether survey effort/detection is reported.
4. Freeze height error and threshold sensitivity **before** reading new height patterns. Apparent conditional gains from 11-m SD vertical GPS error may exceed biological effect; avoid inventing an altitude-calibrated policy.
5. Separate bat-heldout generalization from heldout nights in *seen* bats. A cold-start individual cannot use another individual's fitted policy. Predeclare availability/background and randomization within same cactus-survey blocks; not NeoBat partner-species degree rewiring because this is a single cactus resource complex.

## Status

- Independent source publication and source DOI: VERIFIED from publicly published records.
- Official immutable original Mendeley file list/schema: NOT YET verified (attempt implemented).
- Same-event GPS altitude × flower-count input table: NOT VERIFIED.
- Resource-conditioned bat vertical heldout increment: NULL / NOT ESTIMATED.
- Independent out-of-population replication: NULL / NOT ESTIMATED.

This source is a **candidate to test the 5-D model**, not an empirical positive result. Keep frozen JAE/BE manuscript untouched; maintain batter PR #102 as DRAFT.
