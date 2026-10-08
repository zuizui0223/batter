# Official Zenodo 2026 categorical gate — final corrected execution receipt

## Evidence status
**Source categorical metadata only, no physiological angle, flight trajectory or acoustic measurement values opened.** This records the latest correction of an earlier INVALID no-download/zero-bat result; it is not a new biological result.

- Source DOI: 10.5281/zenodo.20927789
- Source URL: https://zenodo.org/records/20927789
- Corrected GitHub Actions [run 37772600093](https://github.com/zuizui0223/batter/actions/runs/37772600093): **success**. Head `a2e43558ea...`. The schema and source were corrected to use the official file link rather than assume an unavailable link type.
- Confirmed categorical only: `M. daubentonii` compiled partial CSV **21,249 frame rows / 5 batID labels / 39 distinct filenames / 5 labels in ≥3 filenames**.
- Confirmed categorical only: `P. pygmaeus` **60,416 frame rows / 4 batID labels / 56 distinct filenames / 4 labels in ≥3 filenames**.
- The source reader initially erroneously produced **zero** counts on a skipped-download path. That earlier result must NEVER be interpreted as zero biological animals, and it was corrected without opening any physiological values.
- At the author-verified per-species biological cohort level, 4 bats are explicitly selected in `code/config_03_lcs_UCLOUD.json`. The extra fifth categorical `mdau` label is not independently verified as a fifth eligible physical bat.
- The two compact exports include `earTipSep, dist2target, batID, filename, ...`, **not individual left/right ear gaze vectors or 3D head/flight heading**. Thus the previously frozen individual ear-to-heading primary cannot be executed, even if a fifth bat is eventually verified.
- There are no independently documented two stimulus/task contexts in the chosen source subset for cross-context personal sensorimotor prediction.

**Final scientific result: STOP_INSUFFICIENT_VERIFIED_WITHIN_SPECIES_BIOLOGICAL_N_AND_MISSING_TARGET_VECTOR.** The source is genuinely available, and the categorical support is nonzero. This is not evidence that individual ear control fails to exist.

## Science-program decision
Do NOT reopen the small-CSV data to fit some replacement earTipSep personal residual just to produce a positive endpoint. Do NOT pool 4+4 bats of different species into a homogeneous biological population. Prior published PNAS target-focused hearing is the correct source of its already demonstrated acoustic finding. The original JAE vertical-niche manuscript remains scientifically separate and unaffected.
