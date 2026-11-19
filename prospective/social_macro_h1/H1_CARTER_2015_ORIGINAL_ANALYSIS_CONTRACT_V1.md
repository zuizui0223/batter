# H1 2015 Figshare same-scale distress versus noise: original-data analysis contract

2026-11-19. Registered **after 2015 paper was read but before opening individual original source observations** in the new reanalysis. This is published prior art reanalysis, not prospective independent replication of H1.

Source: Carter et al. (2015), PLOS ONE 10:e0136146 DOI 10.1371/journal.pone.0136146; original Figshare article DOI 10.6084/m9.figshare.1454597.v2, file `playback_response_data.csv` expected 19693 bytes with original MD5 `991be124c47f48a955fa5a0a40dd864c`. Confirm actual MD5 and source row count before opening outcome values; do not publish original row data in repo or CI artifacts.

Published field design: 12 playback sessions over 8 nights at 8 field sites; 308 playback sequences (155 distress, 153 noise). The caller is *Molossus molossus*, while simultaneously detected recipient responses include *M. molossus* and sympatric *Saccopteryx bilineata*. Each sequence has a 1-min quiet control before 1-min playback, repeated sequences within session. A recorded bat pass is NOT a unique animal.

Primary input outcome per original sequence and recipient: `D = passes_during_playback - passes_during_prior_silence`. **Include all source trials**, including pre=0 and during=0. Author's original paper excluded no-activity trial pairs in one analysis, but presented sensitivity including them; selection based on playback outcome is not appropriate for a broad independent trial universe.

Primary study-specific contrast for each recipient, after confirming original columns:
- Form mean(D | distress) − mean(D | noise) *within each playback session*, only where both treatments documented.
- Evaluate sign distribution and equal-session mean. Session-blocked uncertainty via exact sign flips and session bootstrap, but these sessions may repeat 8 field sites, so **not eight independent random sites** unless original site identifier supports grouping. Treat session inference as descriptive unless 8 independent site labels can be verified. If data show ordered alternating distress/noise, adjust/check sequence and time, but do not assume genuine random treatment order.
- Estimate recipient-specific contrasts for M. molossus and S. bilineata separately. Their differences can be described but not inferred as independent species replicates within one study.

Sensitivity: repeat after the author's source outcome-dependent no-activity exclusion and document any sign/gain change, never switching primary. Restrict to explicitly identified original sessions. Roost proximity is descriptive/potentially confounded with site, and should not be used to claim a causal patch-context effect merely from uncontrolled proximity.

2016 Eckenweber & Knörnschild source compares Saccopteryx conspecific versus heterospecific distress calls across roost and foraging contexts. **Different sound and sampling controls**: 2015 heterospecific Molossus distress versus pink noise; 2016 conspecific Saccopteryx distress versus Molossus distress. Neither is a matched external replication of 2019 Lewanzik buzz×pre baseline. Do not pool estimated effects without harmonized treatment, response and independent sampling units.

STOP conditions: original checksum mismatch; fewer than three with both distress and noise under a stable session; no known 8 field site labels for site-level significance; nonhuman technical artifacts (speaker gain and detector sensitivity) not controlled; missing raw unit identification; arbitrary postoutcome strata.

Interpretation ceiling: **source-reproduction / context-aware source hierarchy**, NOT first demonstration of social cue responsiveness, reciprocity, mobbing, original information strategy or H3 personal memory.
