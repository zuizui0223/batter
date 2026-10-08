# Official Dryad 2015 Excel retrieval stop — authoritative Gate 0 result

## Status
**STOP_RAW_SOURCE_INACCESSIBLE — not a null acoustic phenotype.** This was an intentionally source-only procedure and did not open any bat-level audio parameters, spreadsheets, numerical values, raw 3-D tracks or identity labels.

Study source: Amichai, Blumrosen & Yovel (2015), Proc R Soc B, DOI 10.1098/rspb.2015.2064.
Public catalogue: Dryad DOI 10.5061/dryad.8f0v4, advertised single 1.81 MB `Dryad.xlsx`.

Frozen pre-result source-gate contract commit: `a5a05a0f6e4558a48c291325bbf2375479dd60d5`.
Two source-only GitHub Actions executions:
- [Run 37753247712](https://github.com/zuizui0223/batter/actions/runs/37753247712), original official public file-stream URL, GitHub conclusion success in enforcing STOP, HTTP **403**.
- [Run 37753441253](https://github.com/zuizui0223/batter/actions/runs/37753441253), original official public file-stream plus officially documented public REST file endpoint, GitHub conclusion success in enforcing STOP.
- [Artifact 11539380688](https://github.com/zuizui0223/batter/actions/runs/37753441253/artifacts/11539380688), exact native receipt JSON.

### Native source statuses (confirmed in artifact)
| Official Dryad endpoint | HTTP |
|---|---:|
| https://datadryad.org/downloads/file_stream/68296 | **403** |
| https://datadryad.org/api/v2/files/68296/download | **401** |

Source bytes downloaded: **0**. Reported xlsx sheet names/column headers: **none**, because workbook content was unavailable. Raw-file SHA256, recorded individual/session support and per-bat repeats were therefore **not evaluated**. Do not infer that source is not publicly catalogued or that no raw data exist. Do not claim file content, novel acoustical treatment effects, new JAR nulls or individual random-response diversity.

## Important novelty/power boundary even if source is later made accessible
The paper already:
- experimentally varied original SELF versus time-reversed SELF masker at a matched broad spectral content;
- measured changes in emitted intensity, duration, frequency, inter-call characteristics and behavioral performance;
- reported acoustic call identity classification **61% across treatments**;
- included **only four biological bats**, with treatment sessions on different days.

Thus a later per-call regression with many thousands of audio events cannot become a population-level replication (n=4). A separate pre-outcome audio-treatment contrast would need independently documented bat/session labels and an exact source-value gate. No automatic adoption of 'reversed self masker causes different individual mechanisms' is permitted without checking prior publication/supplement for the same endpoint.

## Ecological evidence pivot after this STOP
Recent independent *real* study supplies a strong comparison of spatial/sensory routes but does not prove substitution:
Goldshtein et al. 2025 PNAS DOI 10.1073/pnas.2407810122, tracked **96** bats (59 in 2018 +37 in 2019) and recovered onboard audio from **four** individuals during emergence of ~2000 Rhinopoma microphyllum. The group spread laterally as distance from the cave increased; associated encounter density and masking probability fell rapidly, with little evidence of systematic spectral jamming avoidance.

This **published group-scale spatial dilution** is not the same as exclusive *individual* long-term airspace partitioning in our JAE work. Both may coexist: group dispersal reduces masking while within the expanded group different individuals can continue using overlapping 3-D niches. The Goldshtein results were already published and are not a new measurement here. Their tracking and audio source is Mendeley 10.17632/k7pt2j84f7.1; no source bytes opened in this branch.

Separate 2015 receiver-side study Luo et al., Sci Rep DOI 10.1038/srep18556 already quantitatively decomposed signal amplitude, duration and redundancy into actual modelled/behavioral detection gains in *Phyllostomus discolor*. Therefore the general hypothesis 'bats combine amplitude/duration/time to preserve detection payoff' is also prior art; only a new cross-intervention or individual-causal interaction would be distinct.

## Next authorized step
Wait for an authorized legitimate native Dryad workbook download by the user/repository or direct author sharing; record exact source DOI, bytes and digest before re-opening Gate 1. Do not make workaround requests to undocumented endpoints, scrape plots as 'individual raw observations' or repeat simulation-only attempts to mask missing data.

For this source in this environment: **STOP**.
