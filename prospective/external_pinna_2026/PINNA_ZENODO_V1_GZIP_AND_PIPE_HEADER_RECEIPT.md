# Official PNAS 2026 Zenodo v1 header-only source receipt and correction

**NO original angle, ear-separation, velocity, target distance or other numerical outcomes opened.** The initial 2026-10-08 GitHub Actions run 37767065293 returned HTTP200 and 19 official public file records (Zenodo source DOI 10.5281/zenodo.20927789); three eligible small CSV content links returned HTTP200. However the response transfer encoding was gzip; first implementation used raw HTTP bytes as if CSV text, reporting three one-column junk headers and a *false-positive* "PASS_SCHEMA_CANDIDATE" status. **That pass was invalid.**

## Correction sequence
- Original source-only contract committed before the initial request: d29f31bb.
- Incorrect header result run: [37767065293](https://github.com/zuizui0223/batter/actions/runs/37767065293) (artifact 11546056102). Its "header" comprised gzip bytes and MUST NOT be interpreted as real column names or an eligibility pass.
- First decompressed-source correction: [37770167453](https://github.com/zuizui0223/batter/actions/runs/37770167453); delivered true CSV header text but initially did not recognize the PIPE delimiter for two sensorimotor CSVs.
- Added gzip-binary self-test, fixed physical CSV delimiter detection and a standalone categorical Gate 2 contract **before opening any record-level biological identifiers**.
- Final corrected HEADER-ONLY run: [37770368387](https://github.com/zuizui0223/batter/actions/runs/37770368387), artifact 11548135200. The implementation and GitHub Actions succeeded, source metadata HTTP200 and all three CSV headers parsed.

## Actual source headers after correct HTTP decompression
The modelled CI curve file `earTipSep_SSblin_500mmRange_full_nlme_vms_tm_CIbands_MC.csv` is a **comma CSV** with six headers: `species,dist2target,origEstimate,Estimate,Q2.5,Q97.5`. It lacks bat or session identity and is INELIGIBLE as a personal policy dataset.

The two *per-observation sensorimotor exports* are **PIPE**-delimited, with exactly these 15 headers:
`earTipSep|dist2target|batID|sdEarTipSep|meanModelConf|reprojectionErrorC1|reprojectionErrorC2|inCluster|dataStructNr|recTimePosix|dist2target_buzzstart|filename|frametime|eyeDist|isExcluded`.

Their source file/size identity is:
- `mdau_basement_config_UCLOUD_01_collect_20241008_203617_processed_20251112_szred_lcs_20251114_PARTIALLY_export.csv`, 5,562,691 bytes, publisher md5 `97ae631fcabfcb972b7896bef72c100e`.
- `ppyg_config_UCLOUD_01_collect_20241008_122450_processed_20251112_szred_lcs_20251114_export.csv`, 14,878,218 bytes, publisher md5 `d6f96d2d002e296c2575d586cdd92731`.

Important: `batID` and `filename` are only **potential** physical-ID and independent-bout sources. No source-verified repeated physical bat trajectories are established by merely observing these headings. Modelled curves and per-frame camera rows are not independent biological subjects.

## Gate 2 freeze
`PINNA_FLIGHT_CATEGORICAL_SUPPORT_GATE_V1.md` was committed before accessing per-bat/filenames. It restricts the next source read to categorical per-bat ID and recording filename counts, treating species separately and requiring >=5 bats each with >=3 independently recorded files and ≥2 verified comparable task contexts. No physiology, angle, velocity, signal-to-noise or inferential statistic is permitted until structural count and author-documented stable ID mapping is established.

The scope of a successful *future* independent original question would be personal cross-bout ear-target/heading alignment beyond shared target-focused hearing. The universal prey-facing ears finding itself is prior art by Häfele et al. (2026).

## Scientific status
Corrected header-only result: **PASS_SCHEMA_CANDIDATE_REQUIRES_INDEPENDENT_BOUT_GATE**, NOT "PASS BIOLOGICAL SUPPORT". Per-bat categorical count job is independent, and its gate may fail due to physical N, number of filenames or lack of two comparable task contexts. The initial gzip bug must remain disclosed and not erased. The JAE RC2 paper and its primary evidence are unchanged.
