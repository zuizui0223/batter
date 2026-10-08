# Mormoops v4 2026 public-data gate — authoritative structural receipt

**Result: STOP_SOURCE_INACCESSIBLE. No bat behaviour outcomes opened.**

Published source: Pradhan et al. (2026), `Sensorimotor strategies for rapid leadership takeover in flying echolocating bats`, *Communications Biology*, DOI `10.1038/s42003-026-10966-7`. Mendeley dataset v4 DOI `10.17632/mrnvkzrdsd.4` publicly lists `TrackTable_All.mat`, `Switch_AnalysisTable.mat`, `RelativeTurningStartTime_AnalysisTable.mat` and `Echolocation_AnalysisTable.mat`. Listed files ≠ readable raw values.

The pre-outcome contract `MORMOOPS_V4_SOURCE_ELIGIBILITY_CONTRACT_V1.md` was committed before running its source-only script. The exact official public API endpoint `https://api.data.mendeley.com/datasets/mrnvkzrdsd?version=4` responded **HTTP 403 Forbidden** on 8 October 2026 (GitHub Action web runner); therefore no MAT bytes, schema, bat IDs, times or numeric positions were obtained. No alternate Mendeley version or unofficial third-party mirror was used.

- Github Actions [37749735084](https://github.com/zuizui0223/batter/actions/runs/37749735084): **completed success**, but this success means the fail-closed audit and artifact upload worked, NOT that dataset access or scientific eligibility passed.
- Artifact: `11537194469`, `mormoops-v4-public-source-structural-only-v1`.
- Machine result inside artifact: `MORMOOPS_V4_STRUCTURAL_RECEIPT_V1.json`; `status=STOP_SOURCE_INACCESSIBLE`, `numeric_bat_outcomes_opened=false`.
- No valid stable biological individual ID mapping was verified. Do not use per-track segment names as persistent bats.

**Follow-on scientific question, NOT YET TESTABLE from this source:** does biological individual identity predict 3-D maneuvers and echolocation parameters after the same bat changes lead/follow role, beyond relative partner geometry? This would require a new verified public data copy or an author-supplied original with stable bat IDs and emitter–track timestamp joins, then a fresh outcome lock *before numeric opening*.

There is no evidence here of a positive/negative individual-level bat effect, and this source must not be counted as a new independent replication of the earlier Rhino identity result.
