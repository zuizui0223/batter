# H1 independent source audit: Molossus individual acoustic recognition (2026-11-19)

**Evidence status: reanalysis of published prior art; NOT an independent confirmation of the Lewanzik 2019 buzz×baseline moderator and NOT a macro phylogenetic result.** Frozen batter JAE and main are unchanged.

## Source and verified units

Kohles et al. (2020), *Behavioral Ecology* DOI 10.1093/beheco/araa056; Dryad DOI 10.5061/dryad.tqjq2bvvx. Public 2020 video-analysis CSV: https://zenodo.org/records/4953622/files/molossusinddiscrim_data_videoanalysis.csv?download=1 .

The full browser-displayed CSV **51 data lines** was transcribed and assessed. This is **not original-byte-verified**: expected original MD5 from Zenodo `b4b9970eac190601b4a291725137c110`, current local transcription was not byte-equal. Results are subject to the original-byte consistency gate if that file is independently obtained.

Search-phase: **34 trials, 19 distinct subjects, five original roost groups**, of which **20 test and 14 control** match the paper. There are 20 unique bat IDs across both call classes, because one subject occurs only in approach calls; **19** are observed in search-phase trials. Same-bat search-phase test/control matched sample **n=12**. Trials and recordings must not be counted as independent animals.

Published source already concluded that *Molossus molossus* discriminates between individual group members from search-phase calls. The below calculation is an independent implementation on the web-visible source table, **not a newly discovered biological effect**.

## Explicit response and two distinct inference levels

Response per bat×trial: `D = number(head waggles, 40 seconds dishabituation) - number(head waggles, 40 seconds posthabituation)`. For every biological bat, average D separately among test (speaker switches caller) and control (same caller remains) sessions. Paired individual contrast `d_i = mean(D_test,i) - mean(D_control,i)`; no session pseudo-replication. All source video-analysis rows passed the original 50% habituation reduction criterion.

- **12 matched bats**: equal-bat mean **+12.70833 head waggles/40 sec**, 10 positive, 2 negative, two-sided exact bat-level sign flip **p=0.01123** (exploratory), bat-resampling percentile 95% interval **[+5.08,+20.04]**. Bat-level intervals assume independence across bats and can understate dependence within roost.
- **Five independent roost groups**: roost means 150A +13.25 (4 matched bats); 152A +28.00 (2); 251 −14.00 (1); 263 +16.75 (2); 275 +8.00 (3). Four of five positive. Roost-equal mean **+10.40**, sign-flip **p=0.25**, low-N roost bootstrap 95% **[−2.40,+21.25]**. The putative population-transfer claim is **not established**, despite a within-bat positive contrast.
- **Approach call negative-control gate STOP**: web-rendered CSV only 17 rows, 13 biological animals, four matched animals across three roosts; does not satisfy the precomputation minimum of >=6 matched animals and >=3 roosts. Moreover the paper text refers to 19 approach trials (10 test, 9 control), whereas displayed public CSV contains 17 (9 test, 8 control); discrepancy unverified. Do not treat the approach contrast as a confirmatory null result.

## Relation to H1, and external sources

Lewanzik 2019: randomized feeding buzz content and observed recipient activity during playback at 12 lakes; cannot pool bat-seconds/min with 2020 within-bat *attentional discrimination* or assume stable personal memory. The 2019 result remains no positive heldout lake gain from additional buzz×pre-activity moderation in four recipient groups (Pnat structurally 11 lakes).

Other sources checked (newly considered but NOT new findings): Egert-Berg et al. 2018, DOI 10.1016/j.cub.2018.09.064, archived Mendeley MATLAB figure data 10.17632/rb7r4cb74r.1, five-species *theory development*; Roeleke et al. 2020 DOI 10.1111/oik.07158, Movebank source study 622521340, landscape-conditional social foraging in *Nyctalus noctula*; Stidsholt et al. 2023 DOI 10.1111/gcb.17063, Mendeley 10.17632/67njb78d59.1, social presence+prey attacks not randomized graded buzz; Lourie et al. 2024 DOI 10.1098/rstb.2024.0060, odor-driven temporal/remembered-spatial foraging; Wilson et al. 2026 DOI 10.1016/j.anbehav.2025.123406, four species attracted/repelled/unresponsive to feeding/distress calls, but original source event table and denominators unverified.

**Scientific result:** At least one independent bat species has experimentally supported ability to decode individual identity from search-phase calls, and this published evidence is conceptually distinct from 2019 buzz/pre-activity response. It does not prove a universal negative personal-memory/social-information tradeoff nor a transferable across-species acoustic decision rule. Population-level transfer remains an open question. The exact same H1 buzz×baseline moderator cannot yet be independently re-tested from these additional source materials.

## Reproduce / guards

Original source public link above. Recalculation code accepts original videoanalysis CSV and does not require caller/recipient individual names to be published. Source-web transcription and animal-level rows are **not committed**. Precomputation criteria at `EXTERNAL_SOURCE_DISCRIMINATION_CONTRACT_V1.md`. Aggregates: `H1_EXTERNAL_MOLOSSUS_2020_RECEIPT_V1.json`, `H1_EXTERNAL_SOURCE_ELIGIBILITY_V1.csv`. A future genuinely acquired original CSV must match the Zenodo MD5 before a byte-authenticated replication is declared.
