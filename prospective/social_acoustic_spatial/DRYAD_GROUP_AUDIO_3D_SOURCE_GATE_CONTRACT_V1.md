# Public Dryad/Figshare acoustic + 3-D source-opening contract v1

## Evidence tier
**STRUCTURAL PUBLIC DATA INVENTORY ONLY**. This is a new, separate prospective source route; it does not reopen numerical analysis on any known bat trajectories, change a preregistered threshold, or count published group data as a new independent bat result.

Published source:
- Hase et al. 2022 `Echo reception in group flight by Japanese horseshoe bats`, DOI `10.1098/rsos.211597`, Dryad DOI `10.5061/dryad.v9s4mw6wn`.
- Hase et al. 2018 `Bats enhance their call identities`, DOI `10.1038/s42003-018-0045-3`, Dryad DOI `10.5061/dryad.4f99c46`.

Pre-existing verified web information:
- 2022 article simultaneously reports onboard bat-specific sonar and 3-D flight trajectories under 1 versus 3 bats and wide/narrow rooms, for nine captive adult bats.
- 2018 Dryad download page lists ONLY `SoundFile.zip`, 614.45MB: individual-bat on-board mono sonar, 500-kHz audio and 10-second files. Do NOT download to find unsupported movement XYZ.

## Structural opening only
1. GET only canonical public Dryad API metadata at `https://datadryad.org/api/v2/datasets/doi:10.5061/dryad.v9s4mw6wn` and equivalent for 2018 reference. Use same DOI, no guesses of missing IDs/alternate mirrors, redirects only HTTPS.
2. Enumerate *published file names, sizes, format, file UUIDs and external data links* via the official API's reported version and file-list links. Do not fetch ZIP content, raw waveforms, movement time series, or any numeric column.
3. If a small (<100 KB) public README/data dictionary is directly offered by the official API, only retrieve its *field labels and schema descriptions*. No numeric bat outcomes.
4. Respect publisher redirects/403; output `STOP_PUBLIC_SOURCE_INACCESSIBLE` if API blocks without retrying alternative private endpoints.
5. Output `STOP_NO_JOINT_3D_AUDIO` if verified file list is only audio or other non-track files; output `STRUCTURAL_CANDIDATE_JOINT_SOURCE` only if file labels/metadata document both individually attributable sonar and simultaneous 3-D XYZ/time series, AND documented matching event/bat identifiers. Merely seeing `SoundFile`, `Data`, or `trajectory` does not meet the linkage criterion; ambiguous cases yield `HOLD_NEEDS_SCHEMA`.
6. Stable biological bat identity across flight sessions is an independent stricter gate. `bat1` in a simultaneous trial is NOT enough. `STOP_NO_STABLE_ID` for cross-session identity if no individual map is supplied; same-session physical acoustic vs spatial modulation may remain structurally viable without cross-day IDs.
7. Only after structural PASS could any new quantitative endpoint be frozen *before* opening raw values. Each statistic must respect n=9 or independently verified real N, bat/session clustering, actual comparison structure and measured auditory/kinematic units. No reclassifying originals as prospective causal experimental assignment if conditions were already observed in a publication.

## Why this is worth doing
The 2022 article already reports closer social proximity in narrower rooms (~1.8 vs 2.7 m), different speed and group-dependent pulse changes with stabilized reference echoes. If the raw archive jointly preserves bat×time×3D and emit/receive audio, one could quantify *the previously untested trialwise acoustic–spatial joint covariance* **descriptively**; independent acoustic interference assignment would still be required for causal mediation.

The 2026 longitudinal resting CF2 archive DOI `10.17632/4y98p5y8fc.1` is valid for 101-individual frequency dynamics but cannot supply the 3-D movement side. The public Mendeley API for an unrelated 2026 Mormoops dataset returned HTTP 403 in the previous vetted Actions run; do not assume that provider can be accessed here.

## Stop on source ambiguity
Never download hundreds of megabytes of audio speculatively, infer XYZ from spectrograms, import a paper's published result as newly computed evidence, or silently change size/ID thresholds.
