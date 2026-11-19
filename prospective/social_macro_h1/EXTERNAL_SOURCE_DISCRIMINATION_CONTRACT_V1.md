# H1 independent-source capability gate: Molossus individual-acoustic discrimination

Date: 2026-11-19. Analysis protocol written after the paper and its web-readable CSV were discovered. **NOT a prospective independent preregistration** and NOT external replication of the Lewanzik (2019) buzz×baseline moderator.

## Source

Kohles, Carter, Page & Dechmann (2020), Behavioral Ecology, DOI 10.1093/beheco/araa056. Dryad DOI 10.5061/dryad.tqjq2bvvx, original public `molossusinddiscrim_data_videoanalysis.csv` (3.3 KB), web-visible at https://zenodo.org/records/4953622/files/molossusinddiscrim_data_videoanalysis.csv?download=1 . Original biological subject = individually PIT-tagged Molossus molossus bat; do NOT expose original transponder IDs outside input or commit them. Study tested 19 marked animals drawn from social groups, multiple sessions per bat; one paper, not 19 independent studies.

Response variable = head waggles in **40-second segments** before (Posthabituation) and after (Dishabituation) a caller switch. An observation is one bat × trial × call type × test/control condition. In test, caller identity changes; in control, the same caller continues. A test reaction need not indicate prey abundance, competition payoff, stable routes or group-level recruitment.

## Descriptive estimands and aggregation (fixed before numerical run)

1. Search-phase call only; response D = Dishabituation - Posthabituation, in *head waggles per 40 sec*. For each biological bat separately, average D over available test trials and control trials.
2. Primary matched-unit estimate: for bats with both trial types under search-phase calls, `d_i = mean(D_test,i) - mean(D_control,i)`; average d_i over bats; exact paired sign-flip/randomization reference and 95% bat-bootstrap CI if n adequate. Zero response included and no raw trial counted as an independent bat.
3. Full source secondary descriptive: bat-equal weighted group means, test minus control D; nonpaired animals not randomly imputed.
4. Separate negative control: approach-phase calls with identical metrics, but **do not** compare call-type effects as if outcomes came from different random samples; bat overlap is possible. No binary group-specific causal claim from a lack of significance.
5. 5 social roosts: show roost contribution and leave-one-roost-out sign as *descriptive source-internal transfer only*, not universal extrapolation. If fewer than 3 roosts contain matched pairs or fewer than 6 matched animals, STOP quantitative inference and report descriptively.
6. Original source already published evidence for individual discrimination; any positive numerical contrast here is a reproducibility exercise, not a new biological discovery. Do NOT interpret behavioral discrimination as cooperative information transfer or as memorized spatial strategies.

## Source integrity and comparability

A web tool displayed 51 CSV data lines plus one header, and original paper documents 20 search-phase test trials and 14 controls after habituation gating. The web tool renders public text, but cannot provide original ZIP byte SHA: classify local reconstruction as **web-text-transcribed, no original SHA**; verify counts and columns against paper before making any causal/statistical inference. If rows cannot be completely/accurately reconstructed, STOP and keep metadata-only result.

Previous 2019 Lewanzik data measure change in bat-seconds during randomized foraging buzz intensity and a different subject grain (lake × emitter × condition), without stable animal IDs; 2020 Kohles measures individual auditory discrimination under habituation. They are **incompatible endpoints**, so no pooled meta-analysis, common effect size or cross-study negative-tradeoff test.

Other reviewed independent candidates (not yet original-byte ingested):
- Egert-Berg et al. 2018, 5-species resource-predictability case + 2-species field playback summary, DOI 10.1016/j.cub.2018.09.064, Mendeley 10.17632/rb7r4cb74r.1: original evidence in theory development, not independent theory test.
- Wilson et al. 2026, 4 species acoustic response to feeding/distress calls, DOI 10.1016/j.anbehav.2025.123406: candidate for matched caller/treatment field response; exact raw outcome table and sampling design not yet independently retrieved.
- Lourie et al. 2024, roost-mediated odor timing information in Egyptian fruit bats, DOI 10.1098/rstb.2024.0060: directly measured timing/known locations but not acoustic contest or 2019 moderator.
- Leavell et al. 2023 DOI 10.1098/rspb.2023.1910, Dryad 10.5061/dryad.z8w9ghxkd: individual-ID Trachops cirrhosus binary frog prey-call choice; NOT conspecific social foraging or buzz-density test.

## Decision gate

Source-independent *ecological mechanism* H1 is NOT solved by a published Molossus identity-discrimination test. The next external replication of the exact 2019 buzz×baseline moderator requires another independent controlled trial series with baseline activity, graded buzz content, detection effort and lake/site grouping. No source substitution.
