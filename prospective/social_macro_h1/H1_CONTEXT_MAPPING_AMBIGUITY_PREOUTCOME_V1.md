# 2015–2016 original source: design-authenticated pre-outcome amendment v1

2026-11-19. Recorded **before opening the numerical response columns** D:E:F in the 2016 XLSX or the 2015 Figshare response columns. Original article conclusions already known and are *prior art*. This is a robustness and independent-unit audit, not confirmation from untouched literature.

**Source authentication and factor structure:**
- 2016 Europe PMC original XLSX SHA256 `28402ac6c969f7a6c13acf5f90192afbfa4b6c5158e1bbc8f657b55f255b05ef`, 114 raw rows = 19 session labels 1–19 × within/close/foraging × conspecific S. bilineata / heterospecific M. molossus. Header D=pre-observation, E=reaction, F=responsiveness. Original paper says 11 physical colonies, 8 sampled in 2 years; the workbook only labels 19 sessions, NOT the mapping of repeated physical roosts.
- 2015 Figshare original CSV file `playback_response_data.csv`, MD5 `991be124c47f48a955fa5a0a40dd864c`, 19,693 bytes, 308 playback rows in 12 session IDs; 155 distress, 153 noise. The 3 descriptive `Roost proximity` levels are `close`, `far`, `adjacent`; original article says 8 distinct sites, no exact physical site key in raw column names. Original 2015 field paper reproduced published counts, but not outcome values yet.

## 2016 precomputed contrasts (per session 1–19)

Define observed response per trial (no outcome-dependent exclusion): `R_{i,l,c} = E_{i,l,c} - D_{i,l,c}`, directly crosschecked with F if numeric. Location `l∈{within,close,foraging}`, caller `c∈{S. bilineata,M. molossus}`.

Primary location-by-caller contrast, exploratory because order is not randomized: `x_i=(R_{i,within,S}-R_{i,within,M})-(R_{i,foraging,S}-R_{i,foraging,M})`. Also report `x_i^{close}` replacing within with close. Matched session values must be complete 19/19, no local recoding after seeing outcomes.

Published-main-context reproduction: `u_i=R_{i,within,S}-R_{i,foraging,S}`, `v_i=R_{i,close,S}-R_{i,foraging,S}`. This can be strong while the novel *call specificity* difference-in-difference is absent. Treat them as different estimands. The heterospecific M caller is **not a silent/noise treatment**.

**Unidentified 11 physical roost mapping:** According to paper, among 19 sessions from 11 colonies, 8 colonies had two distinct year samples and 3 had one. Let session-level contrasts sorted be `x_(1)≤…≤x_(19)`, `S=Σx_i`. Across *all* partitions of 19 sessions into 8 unknown pairs and 3 unknown singletons, the possible equal-colony means are bounded by:
- lower = `(S + x_(1)+x_(2)+x_(3))/22`
- upper = `(S + x_(17)+x_(18)+x_(19))/22`.

Proof: equal weight to 11 colonies gives (Σ paired-session means + Σ singleton sessions)/11 = (S+Σ singleton sessions)/(2×11); pairing within the remaining 16 does not change this mean. These bounds rely on exact 8 twice+3 once and do **not** recover a valid exact 11-colony p-value, variance, or causal assignment. If a required location/call is missing, STOP this bound rather than imputing.

Output session-equal descriptive means/medians/sign counts and the strict 11-colony mean identification bounds; do not call 19 sessions independent biological colonies. No confirmatory hypothesis p-value until colony/year mapping and order/clock controls become available.

## 2015 precomputed response (per 12 original sessions)

For each recipient (M. molossus, S. bilineata), compute per original trial `D_{trial}=playback passes - preceding 1-minute silent passes`. Session-mean disturbance contrast `w_i=mean(D|M.molossus distress,i)-mean(D|noise,i)`. Keep all 308 trials and report 12 session-equal mean, signs, unfiltered counts. Author's outcome-based `quiet=0 & playback=0` exclusion is a sensitivity only. 8 physical field sites are not mapped uniquely to 12 raw session IDs; no independent-site p-value without that crosswalk. The 2015 caller stimulus is always M. molossus distress or noise and not same treatment as 2016 caller identity contrasts.

**Stop/postpublication boundary**: Neither 2015 nor 2016 provides individual-tagged foraging information use, food profitability or reciprocity. A numerical finding at the session scale does not directly validate the 2019 buzz×baseline model. A location gradient is **already published by the 2016 authors**. Retain unfavorable/noisy contrasts, no postoutcome redefinition. Any quantitative report must state actual source bytes authenticated; raw files not redistributed in `batter`.

Source gate provenance: https://github.com/zuizui0223/batter/actions/runs/44463987029 ; https://github.com/zuizui0223/batter/actions/runs/44464383616 .
