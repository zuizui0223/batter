# Cat-only follow-up gate for two open Zenodo 2026 pinna CSVs

## Evidence firewall
**FROZEN BEFORE OPENING ANY RECORD-LEVEL BATS OR FLIGHT IDs.** This gate is a source-support inquiry only. No measured ear angle, 3D coordinates, speed or subject physiology will be inspected. Previous source-only run 37770167453 revealed the published compiled CSVs are **HTTP-gzipped** and, crucially, that the physical measurement exports use PIPE `|` delimiters, not commas; its 1-column 'success' was therefore invalid. A corrected header-only parser is on this branch, with independent gzip/pipe tests.

Files are explicitly fixed from Zenodo record 20927789, DOI 10.5281/zenodo.20927789 (no substitution):
- mdau_basement_config_UCLOUD_01_collect_20241008_203617_processed_20251112_szred_lcs_20251114_PARTIALLY_export.csv
- ppyg_config_UCLOUD_01_collect_20241008_122450_processed_20251112_szred_lcs_20251114_export.csv

Confirmed legitimate header variables from the corrected HEADER-ONLY 37770167453 source scan (raw values unopened):
`earTipSep|dist2target|batID|sdEarTipSep|meanModelConf|reprojectionErrorC1|reprojectionErrorC2|inCluster|dataStructNr|recTimePosix|dist2target_buzzstart|filename|frametime|eyeDist|isExcluded`.

The compiled CSV `earTipSep_SSblin_500mmRange_full_nlme_vms_tm_CIbands_MC.csv` instead has only `species,dist2target,origEstimate,Estimate,Q2.5,Q97.5`, so no individual/bout IDs: not eligible for per-bat self-history inference.

## Gate 2 — categorical keys and support only
Before opening physiological values, read the **TWO declared per-observation CSVs** as streaming CSV lines, parse ONLY:
- `batID` categorical string, combined with species/file prefix to prevent cross-species bat ID conflation;
- `filename` (candidate independent recording event);
- `dataStructNr` (source-group integer, as *string* identifier only);
- `recTimePosix` (timestamp only as a string; do not calculate physiological speed/values);
- `inCluster`, `isExcluded` (structural flags) used only in counts;
- total row count to assess frame granularity and source support.

Do not parse or log any numeric `earTipSep`, `dist2target`, `sdEarTipSep`, `meanModelConf`, `reprojectionErrorC1/2`, `dist2target_buzzstart`, `frametime`, `eyeDist`. Do not read other source files, audio or >16MB advertised downloads. Do not put raw Zenodo files into Github.

**Genuine physical IDs:** documentation must support one `batID` referring to same physical bat across different `filename` values. A single numeric code reused within an export is not proof of individual identity; figure script `figure_02.m` references `BatID` but that is not itself an independent identity map. Report `UNVERIFIED_PHYSICAL_ID` unless source code/protocol confirms. Independent bouts are candidate distinct `filename` values; one filename with many frames is ONE bout, not many. Different `dataStructNr` segments of a filename are not independent.

A *within-species* analysis requires **at least 5 independently identified biological bats** each with >=3 distinct recording filenames, >=15 eligible bat×file combinations and >=2 externally documented comparable task contexts. Do not combine 3 species to meet n=5; species may have distinct acoustic modalities, physiology and camera setups. The 5-bat and 3-bout floors were originally frozen in `PINNA_FLIGHT_IDENTITY_STRUCTURAL_CONTRACT_V1.md`; this contract explicitly prevents false aggregation across species.

A derived eligibility count by source species+batID, unique files and distinct file-bat pairs is allowed. Per-file number of frames is structural support, not repeated independent bats. Keep table of individual IDs anonymized in any public report; summary counts only. Never compute bat phenotype, numerical sensorimotor coefficients or p-values in this stage.

## Three possible outcomes
- `STOP_SOURCE_INACCESSIBLE`: source HTTP error / compressed stream cannot parse.
- `STOP_NO_INDEPENDENT_INDIVIDUAL_BOUTS`: missing stable physical IDs, filename support, within-species biological N or 2 contextual conditions.
- `PASS_CATEGORICAL_COUNTS_SUBJECT_TO_AUTHORED_ID_DOCUMENTATION`: counts sufficient, independently verified mapping and contexts still need source/protocol confirmation before numeric contract.
These cannot be retroactively lowered for convenience.

## Epistemic boundary
The 2026 PNAS paper's **prey-focused hearing** result is prior art. An independently transferable *personal ear/heading residual* has not been established. Even a future supported result would come from individual prey-targeting flights (not a multi-bat competition manipulation), so it cannot establish acoustic-spatial niche substitution or social-interference adaptation.

This categorical gate is not automatically an experiment, not a bat motor memory test and not permission to publish individual-data claims without distinct pre-outcome preregistration.