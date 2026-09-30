# Supporting Information — integrated ecological-contingency manuscript

## Scope

This file contains methodological and robustness details moved from the main text for submission-length control. No analysis, threshold, outcome, claim status, or inferential classification is changed by this move. The complete frozen contracts, result JSON files, source-screen records and amendment history remain in the repository.

## Supplementary Methods

### Original conditional and marginal scores

For each horizontal cell c, the self conditional predictor P_self(z|c) was the equal-session average of smoothed vertical-bin distributions from the focal animal's other sessions. The other-individual predictor P_other(z|c) was the equal-individual average of the corresponding distributions from other bats.

The original conditional identity score was

G_cond = mean_target [ log P_self(z|c) - log P_other(z|c) ].

The original marginal score separately estimated P_self(z) and P_other(z) from each training set's own horizontal occupancy and calculated

G_marg = mean_target [ log P_self(z) - log P_other(z) ].

Their difference, G_adv = G_cond - G_marg, was initially used to describe conditional- versus marginal-dominant predictive architecture. A later estimator audit showed that G_adv has a panel-specific non-zero exchangeability expectation and that ordinary P(z) can inherit differences in horizontal cell occupancy. We therefore retain these values only as historical endpoints and do not use their sign to classify biological architectures.

### Direct pairwise self-identification

To translate the result into an intuitive biological magnitude, we froze a separate pairwise analysis before opening its output. For each held-out target session and each specific alternative individual within the same cohort, we compared the same-bat and alternative-bat vertical profiles using identical self-derived horizontal cell weights. A self win occurred when the target's mean log probability was higher under the same individual's profile.

Alternative comparisons were averaged within target session, sessions were averaged within biological individual across admitted cohorts, and individuals were weighted equally. We report the equal-individual self-win fraction and a 20,000-replicate individual-bootstrap percentile interval.

Because the prediction pipeline itself can shift the exchangeability baseline away from 0.5, we subsequently froze a null-calibration family before opening any pairwise-null output. For each panel, the entire pairwise statistic was recomputed under the same whole-session label-permutation design, permutation count and seed already used for that panel's estimator calibration. We report the observed self-win fraction, panel-specific permutation-null mean, observed-minus-null excess and one-sided P(null >= observed). A 0.5 line is retained only as an intuitive visual reference.

We also report exp(G_cc) as an observed per-fix geometric self-versus-other likelihood multiplier and exp(G_cc - mean(null)) as a null-calibrated effect scale. Because GPS fixes are not independent biological replicates, these multipliers are not compounded across fixes.

### Focal early/late identity assignment and residual-map ceiling

A separate focal analysis predating the comparative calibration split each of eight *Tadarida* individuals into early and late observations within 18 frozen 5-km cells. Early individual conditional maps were scored against every individual's later observations. The observed statistic was the mean identity-matched diagonal gain relative to the population conditional predictor; its null was the complete set of 8! assignments.

A stronger frozen refinement first absorbed each bat's marginal altitude identity into a marginal-adjusted cell baseline and then tested whether an individual-specific cell-by-height residual was stable from early to late. This test sets a mechanistic ceiling: failure means repeatable vertical identity cannot be relabelled as one fixed individual-specific cell-by-height route map.

### Terrain-relative AGL calibration

The focal annotated source provided height above ground, calculated in the original source workflow relative to a 30-m ASTER terrain model. Before opening the AGL common-cell calibration, we froze a decision contract requiring exact reproduction of the previously frozen ordinary AGL scores. We then applied the same common-cell weighting and whole-session calibration used for MSL.

The primary AGL test used 5-km cells and 9,999 permutations. Fixed grain robustness tests used 2.5- and 10-km cells with 4,999 permutations each. The predeclared scale statement required both sensitivity scales to pass if the manuscript were to claim robustness across 2.5–10 km.

### Night-endpoint neighbourhood exclusion

To assess whether departure/arrival or central-place structure could dominate the focal AGL result, we froze an x-y-only endpoint proxy before opening results. This proxy is not claimed to identify the biological roost.

Within each retained BatDay, the first five and last five finite projected fixes were selected using timestamps only. These endpoint fixes were pooled within individual, and the observed endpoint minimizing summed Euclidean distance to all other pooled endpoints was selected as that individual's proxy centre. The primary analysis removed every event strictly within 1,000 m of its own individual's proxy, symmetrically from training and target data. Sessions retained their original identities but had to contain at least 50 remaining events. Fixed descriptive radii of 500 and 2,000 m were also frozen. The focal primary endpoint was calibrated common-cell AGL identity, not the conditional increment.

After the focal 1-km test failed, we froze a separate cross-panel endpoint-exclusion contract before opening any non-*Tadarida* exclusion output. The same first-five/last-five x-y/time-only logic was applied within each originally admitted cohort and individual, using each cohort's already-frozen UTM projection. The 1-km radius was the sole primary radius; 500 m and 2,000 m were descriptive sensitivities only. Sessions falling below 50 remaining numeric-scored events were removed, no new cohorts were admitted, and the 5-km common-cell marginal identity was recalibrated by whole-surviving-session label permutations within cohort. Panel-specific minimum evaluable-individual gates were frozen in advance.

### Biological-scale translation in focal *Tadarida*

For focal AGL only, we calculated an expected-height separation in metres. Within common supported cells, self training-session cell means were averaged equally across self sessions and other-individual cell means were averaged equally across other individuals. Both were then integrated under identical self cell-use weights. For each target session we recorded the absolute difference between the self and other expected AGL; sessions were averaged within individuals and individuals equally. This is a mean-height translation and does not capture distribution-shape differences.

Absolute separation is positive even under exchangeability. We therefore froze a second effect-null calibration before opening its output and recomputed the full metre-scale statistic under the exact focal AGL whole-session label-permutation design (9,999 permutations; the previously frozen AGL seed). We report the raw separation, permutation-null mean, calibrated excess and one-sided upper-tail probability.

### Descriptive visualization of individual centered-shape profiles

To expose the biological content of the already-tested centered-shape individuality, we froze a descriptive visualization before opening any individual-profile output. This step added no new hypothesis test, permutation family, clustering, strategy classification or threshold optimization.

For each evaluable target session in the five comparative panels, we reconstructed the exact identity-matched self profile used by the frozen centered-shape estimator. Self conditional residual-height distributions were learned from the individual's other sessions, restricted to the target's jointly supported 5-km cells, and integrated under the same equal-session self-derived common-cell weights used in the inferential analysis. We then averaged those target-session self profiles equally within biological individual. Each displayed individual profile therefore sums to one across the ten already-frozen session-centered residual-height bins.

For Figure 6, rows were ordered within panel by descriptive upper-tail mass at residual height >=100 m, with ties broken by individual identifier. A common linear probability scale was used across panels. Individual identifiers were retained only in the machine-readable output and were not displayed in the paper figure. Central-mass and tail-mass ranges were not compared with a permutation null; they are visualization summaries only and may include estimation variability from finite numbers of sessions. We therefore do not use them to infer which component of the profile carries individual identity, and we did not infer clusters, strategy classes or behavioural states from the visualization.


### Additive tag/device altitude-bias audit — full support-gate details

GPS altitude can contain device-specific additive offsets, so a stable tag zero point could mimic repeatable individual vertical location. For the primary test, each retained session was translated to zero median before vertical binning, using fixed residual-height edges of -∞, -400, -200, -100, -50, 0, 50, 100, 200, 400 and +∞ m. Horizontal cells, cohort definitions, weighting, scoring thresholds and whole-session permutations were unchanged. Panels had to retain their original evaluable-individual counts; support required positive observed-minus-null common-cell shape identity and one-sided P(null >= observed) <=0.05.

A separate x-y/time-only preflight defined stationary candidates by both adjacent gaps <=20 min and both adjacent horizontal speeds <=0.5 m/s. Shared 100-m cells required at least three individuals with >=5 candidate fixes each; supported individuals required >=10 candidate fixes. Stationary correction was allowed only when supported individuals numbered at least max(5, ceil(0.5 × original evaluable n)) and an admitted cohort retained >=3 supported repeat individuals. Only *Hypsignathus monstrosus* and *Phyllostomus hastatus* 2016 passed this gate.

For those panels, individual-by-cohort offsets were estimated relative to the median individual height in each shared stationary cell, subtracted from all primary-height observations, and the original vertical bins and 5-km calibration were rerun. This correction was corroborative only. The same preflight summarized tracking-window overlap descriptively; no time-block permutation family was opened.
## Supplementary Results

### Descriptive profiles illustrate variation in central concentration and tail use

The centered-shape result was not only an abstract prediction score. We reconstructed, for each evaluable individual in the five comparative panels, the exact leave-one-session-out identity-matched self profiles used by the frozen common-cell estimator and averaged them equally over that individual's evaluable target sessions (Figure 6). No new inferential test was applied, and the component summaries below were not separately calibrated.

After every session's median altitude had been removed, the displayed profile estimates varied visibly in how tightly probability was concentrated near zero and how much probability extended into the upper and lower tails. Central mass within -50 to +50 m ranged from 0.123 to 0.926 in *E. helvum*, 0.458 to 0.910 in *H. monstrosus*, 0.438 to 0.850 in *P. hastatus* 2022, 0.333 to 0.863 in the 2023 panel, and 0.548 to 0.994 in the 2016 panel. Upper-tail mass at >=100 m ranged from 0.022 to 0.215, 0.012 to 0.151, 0.037 to 0.157, 0.038 to 0.250, and 0.0009 to 0.0686 across those panels, respectively.

Because these ranges come from leave-one-session-out profiles estimated from finite numbers of sessions, part of their apparent spread can arise from profile-estimation noise even under exchangeability. We did not generate null distributions for central mass or tail mass, so the ranges illustrate the plotted estimates but do not identify which profile component carries the calibrated whole-shape identity signal. In the displayed estimates, the 2016 *P. hastatus* profiles appeared more centrally concentrated around the session median than the other comparative panels, but no inferential comparison of these component ranges among panels or individuals is made.

### Coarse-horizontal standardized identity exceeds exchangeability expectations in all six panels

Before altitude centering, the identity-matched common-cell vertical score exceeded the panel-specific session-label permutation expectation in every panel after self and other profiles were integrated under identical 5-km horizontal weights (Figure 2).

Observed-minus-null common-cell identity was +0.602 nats/fix in *T. teniotis* (p=0.0005), +0.265 in *E. helvum* (p=0.0002), +0.076 in *H. monstrosus* (p=0.0002), +0.200 in *P. hastatus* 2022 (p=0.0002), +0.120 in *P. hastatus* 2023 (p=0.0002), and +0.270 in *P. hastatus* 2016 (p=0.0422). The 2016 panel had a raw common-cell score near zero (-0.0039), but its exchangeability expectation was substantially lower (-0.274). The relevant result is therefore identity matching relative to the finite-sample prediction-pipeline null, not positivity relative to zero.

### Stationary-height correction corroborates the two structurally eligible comparative panels

The x-y/time-only preflight permitted empirical stationary-height correction only in *H. monstrosus* and *P. hastatus* 2016. In *H. monstrosus*, offsets were estimated for 12 individuals, 10 remained evaluable after correction, and the median absolute offset was 4.64 m; corrected identity retained calibrated excess +0.0671 (p=0.0002). In *P. hastatus* 2016, 11 offsets were estimated, seven remained evaluable, and the median absolute offset was 2.00 m; calibrated excess was +0.3808 (p=0.0002).

Thus both structurally eligible comparative panels retained identity after empirical offset correction. Shared stationary 100-m cells are calibration locations rather than verified equal-height roost or perch references, so this analysis is corroborative rather than a universal device calibration.

### Endpoint-neighbourhood exclusion is robust in four comparative panels but not universal

Four of five comparative panels passed the predeclared 1-km endpoint-neighbourhood exclusion (Figure 4). *H. monstrosus* retained calibrated excess +0.308 (p=0.0002; n=19), *P. hastatus* 2022 +0.219 (p=0.0002; n=30), the 2023 panel +0.152 (p=0.0002; n=12), and the 2016 panel +0.358 (p=0.0002; n=10).

*E. helvum* retained a strong signal after exclusion (calibrated excess +0.390; p=0.0002) but fell to 11 evaluable individuals, below the frozen minimum of 15, and therefore failed the predeclared gate. The motivating *Tadarida* panel also failed its corresponding 1-km inferential criterion (p=0.1109). Endpoint-associated structure therefore does not generally erase the comparative signal, but it is not universally excluded.

### Pairwise self-identification exceeds its pipeline-specific null in five panels

Direct same-individual versus specific-alternative comparisons gave an intuitive translation of the common-cell result (Figure 3). The same individual's profile won 0.794 of comparisons in *T. teniotis* versus a null mean of 0.508 (calibrated excess +0.286; p=0.0189), 0.858 in *E. helvum* versus 0.583 (+0.275; p=0.0002), 0.767 in *H. monstrosus* versus 0.541 (+0.226; p=0.0002), 0.842 in *P. hastatus* 2022 versus 0.532 (+0.310; p=0.0002), and 0.782 in the 2023 panel versus 0.535 (+0.247; p=0.0002).

The 2016 *P. hastatus* panel did not retain independent pairwise support: observed self-win was 0.594 versus a null mean of 0.498 (calibrated excess +0.096; p=0.1168). Across panels, pairwise null means ranged from 0.498 to 0.583, showing that 0.5 is an intuitive reference rather than a universal exchangeability null.

### Tracking windows overlap strongly in five panels but less in the 2016 panel

Positive overlap among repeat-individual tracking windows was 71.4% in *Tadarida*, 86.0% in *Eidolon*, 91.7% in *Hypsignathus*, 76.6% in *P. hastatus* 2022, 100% in 2023 and 31.1% in 2016. The 2016 panel also had a median start-date difference of 4.0 d, leaving the strongest residual individual-versus-time limitation in that dataset.

### Pipeline calibration changed the inferential baseline

The estimator audit altered interpretation rather than merely changing p-values. The original conditional-minus-marginal contrast had a negative panel-specific exchangeability expectation, and the ordinary marginal score inherited horizontal occupancy differences. Most visibly, *P. hastatus* 2022 changed from an apparent marginal-dominant value of G_adv = -0.120 to a common-cell conditional increment of approximately +0.0066 after horizontal standardization (Supporting Figure S2).

The same principle appeared in the biological translations: pairwise null means ranged from 0.498 to 0.583 rather than being fixed at 0.5, and the focal absolute AGL separation had a positive null mean rather than zero. These results motivate pipeline-specific exchangeability calibration as a general methodological conclusion.

## Evidence-status note

These supporting analyses remain subordinate to the manuscript's evidence hierarchy. Historical estimator endpoints are retained for transparency; pairwise, endpoint-neighbourhood, stationary-offset, descriptive-profile and focal *Tadarida* analyses do not replace the centered-shape primary result. Post-freeze localization analyses remain outcome-informed stress tests, not independent confirmation.
