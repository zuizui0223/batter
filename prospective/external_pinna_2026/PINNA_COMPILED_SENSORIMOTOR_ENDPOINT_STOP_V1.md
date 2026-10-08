# Physical sample and sensory-versus-kinematic endpoint support — decisive STOP

**SOURCE SCHEMA CHECK ONLY; no physical ear-angle, flight heading, target or reward values inspected.**

## Two orthogonal fail-closed conditions
1. **Independent animal support:** the publicly available author `code/config_03_lcs_UCLOUD.json` (used by `bat_ears_03_lcs.m`) lists `bat_ids` arrays containing exactly 4 individual IDs per each of three species. Thus the previously frozen within-species n≥5 support floor is not met, regardless of frames/recordings.
2. **Missing required multivariate response in the eligible public CSVs:** the corrected, legitimate per-observation source headers are
`earTipSep|dist2target|batID|sdEarTipSep|meanModelConf|reprojectionErrorC1|reprojectionErrorC2|inCluster|dataStructNr|recTimePosix|dist2target_buzzstart|filename|frametime|eyeDist|isExcluded`.
They describe **ear-tip separation, target distance, IDs, frame times and camera measurement quality**. They do NOT contain the individually measured **left/right ear directional vectors, acoustic reception-beam aim, yaw/pitch/head heading or 3-D flight velocity components** necessary to operationalize the originally proposed *individual ear–flight-heading alignment* outcome. A model/CI curve file only includes species, distance and curve fit values, also unusable for personal heading.

Original author code `figure_01.m` and `figure_02.m` generates ear aiming/gaze plots by combining much larger MATLAB source structures and HRTFs (see original PNAS source README, 9.5 GB compiled archive). It is not appropriate to reconstruct missing per-individual angles from the already summarized earTipSep–distance export.

The >2 GB MATLAB source per species or direct author-provided raw 3-D keypoints may contain the needed vectors, but are **not** the validated small-file CSV corpus for this predeclared gate. Do not infer their contents from file titles and do not download multi-GB sources ad hoc after seeing the current STOP. A different registered study with raw data access would be needed.

## Conclusion
`STOP_INSUFFICIENT_WITHIN_SPECIES_N_AND_MISSING_EAR_HEADING_TARGET`.

This is a stronger decision than mere absence of repeated recordings, and is **not a finding that individual sensorimotor differences are absent**. It only means the public compact exports do not support the targeted across-bout within-species identity analysis under our frozen requirements. Additional categorical bat/file counts, if obtained, remain useful for auditing source availability but cannot overturn either fail gate.

No new physiological metrics, classifier scores or p-values were computed. The 2026 PNAS result on target-focused bilateral hearing remains independently valid **prior art**, not a discovery from this branch. Frozen JAE RC2 and PR #72 outcomes unaffected.
