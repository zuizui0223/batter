# CF colony acoustic identity — public-source Gate 0 authoritative result v1

## Decision: STOP_SOURCE_API_INACCESSIBLE
This is a source-access result, **NOT a biological null** and **NOT an analysis of CF2 outcomes**. The publisher Data Availability and public dataset page confirm that the v1 dataset exists and is catalogued; access from our execution environment to the official Mendeley metadata API failed.

Authoritative GitHub Actions run: https://github.com/zuizui0223/batter/actions/runs/37751464652
- Run ID: 37751464652
- Source commit at execution: 4968f3d86584a71b5a1ec2783a5ee8eaac496dea
- Workflow: cf-colony-v1-public-structural-gate
- Overall GitHub Actions conclusion: **success** (the audit script itself correctly enforced and reported a STOP; CI success does not mean source access).
- Job ID: 113225453870, source/schema step success.
- Artifact ID: 11538426407, name cf-colony-v1-source-schema-only.
- Frozen pre-outcome contract: CF_COLONY_V1_SOURCE_AND_IDENTITY_GATE.md, commit 0810d403d95cb046cbd344ec62f751734e566585.
- Python source: preflight_cf_colony_v1.py, commit 0d9cd628cfbfadcfdf3ecdac63e2fd8a3c488b20.
- Published dataset DOI: 10.17632/4y98p5y8fc.1.

## Exact documented official public API calls

| Requested public API endpoint | Observed HTTP |
|---|---:|
| https://api.data.mendeley.com/datasets/4y98p5y8fc?version=1 | **403** |
| https://api.data.mendeley.com/datasets/4y98p5y8fc/files?version=1 | **403** |
| https://api.data.mendeley.com/datasets/publics/4y98p5y8fc/files?version=1 | **403** |

All 3 were tested from the GitHub Actions runner, not just a search-result preview. File metadata list empty due to access; no Mendeley source files downloaded, no header strings extracted, no stable animal-ID gate opened, no categorical support counts computed and no numerical CF2 outcomes analyzed.

## Distinguish published observations and the proposed new test

Matsumoto et al. 2026 already established acoustic convergence at the colony/capture-event level. **FM diverges / CF convergence protects a shared silent spectral window is also explicit published mechanistic speculation by the 2026 authors.** The present project cannot claim this as new.

If the raw v1 source later becomes accessible with permission, the unique proposed analysis is a *held-out across-event individual acoustic-history test*, not another group-means reanalysis:
- published 101 unique bats and 177 appearances DO NOT automatically imply ≥12 bats with two adequately sampled mixing events;
- source metadata must prove stable IDs spanning genuinely distinct events;
- expected cross-event identity-prediction advantage, role/year controls, and proper whole-bat uncertainty must be separately frozen before numeric CF2 outcomes are opened.

The published paper explicitly lacks **higher-frequency newcomers inserted into lower-frequency resident colonies** and acknowledges captivity/state alternatives. Accordingly the published data cannot identify whether colony convergence is caused by sensory-ecological silent-window costs rather than social conformity or captivity effects, even if file access is restored.

## Route stop and next action

Do NOT switch to an older Mendeley version, bypass blocked APIs via undocumented endpoints, copy graphical figure values to fabricate 'individual raw data', infer IDs from trial order, or reframe same 101-bat paper as an independent replication of its own conclusions.

A future raw data delivery or author-confirmed file listing would allow restarting Gate 1 only after recording identical DOI/version and SHA256. Without that, the research frontier is the **causal sensory-performance test**: jointly manipulate crowd signal geometry and prey-relevant jamming band and measure both acoustic response and 3-D occupancy *in the same bats*. Existing published FM group-flight sound data (Hase et al. 2018 Dryad 10.5061/dryad.4f99c46) lack archived synchronized raw 3-D tracks, and 2026 resting CF2 colony data likewise do not provide simultaneous 3-D flight.
