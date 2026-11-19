# H1 external Costa Rica 2025 predator-risk/social-call gate — source-first contract

Date: 2026-11-19. **Protocol for reanalysis of already published evidence, not pre-registration independent of prior-art outcome knowledge.** The main 2019 German lake buzz×baseline test and the frozen JAE `batter` paper remain unchanged.

## Independent region and prior art

Gamba-Rios, McCracken & Chaverri (2025), "Recognition of predator cues hinders social communication", Biology Letters, DOI 10.1098/rsbl.2025.0042; Dryad DOI 10.5061/dryad.6djh9w1d3; original author GitHub https://github.com/morceglo/Predator-recognition .

**Costa Rica (Hacienda Barú), not the Panama Barro Colorado Island field station.** The published experiment tested 117 *Thyroptera tricolor* bats from 33 social groups. **Only 38 animals responded and the public `data.csv` contains 228 rows = 38 individual IDs × 2 presented cue types × 3 recording periods.** The other 79 animals and their treatment-level original rows are not represented, and no original field social-group ID is present. These selection and clustering limits must remain explicit.

The stimulus was **conspecific inquiry calls** before/during/after either predator `Vampyrum spectrum` echolocation or one of three nonpredator/control bats (`Uroderma convexum`, `Rhogeessa io`, `Molossops temminckii`). Published 2025 authors already showed call suppression under predator cues and roost cohesion effects. No novel claim for this pattern.

## Original source gate

Pin exact author CSV as Git blob SHA-1 `b8a119df0204ed0beb90b971c97f60cafbdb74cd` and capture file SHA256. Verify UTF-8 CSV with explicit semicolon separator, fields `bat;experiment;order;treatment;bat_type;period;response`; 228 source rows, 38 subjects, 2 treatments per subject, 3 phases per treatment, 14 nonpredator novel-control, 12 frugivorous, 12 insectivorous subject pairs. Published parent sampled 117/33 groups but response sample 38/unknown mapped groups. Do not commit raw subject rows to `batter`.

## Reanalysis estimands fixed before numerical outcomes opened for the new comparative work

One and only primary observed sample: the **38 source-recorded responder bats**, not all 117.

For bat i and cue t ∈ {predator,nonpredator}, response count `Y_i,t,p` by 30s period p. Primary paired transformed contrast:

`d_i = [log(1+Y_pred,during)-log(1+Y_pred,before)] - [log(1+Y_NP,during)-log(1+Y_NP,before)]`.

All 38 pairs retained, including zero during. A negative score means stronger **within-individual suppression under predator than nonpredator calls after accounting for own immediate pre-period responses**. This is a source-conditional contrast: two call stimuli differ in acoustic structure, identity and predatory status, and phase order can matter.

Secondary (predeclared):
- original-scale paired difference of changes, keeping zero counts;
- `during`-only log1p(P)−log1p(NP) with no pre-normalization;
- `after` versus `before` difference by cue to explore persistence/recovery; since trials ordered and before periods differ, not a randomized carryover treatment estimate;
- strata by presentation order NP-P versus P-NP and by three nonpredator call classes, **descriptive only**, with no selection of stronger subgroup as the new main result.

Report bat-equal mean/median, negative/positive/zero counts, all matched data checks and response distribution. A bat-level bootstrap (fixed deterministic seed) may quantify dispersion among 38 selected animals, but is **NOT** a valid 117-bat or 33-group confidence interval; physical group membership and inclusion/selection probabilities are unavailable. Inference as a prospective ecological effect or independent site/group replication must STOP.

The published "25 flight-cage group cohesion tests" are a **separate experiment and not in this source CSV**; do not combine the 38 acoustically responding animals with the group-level cage observations as one measured cohort.

## Comparison to current H1 programme

- Lewanzik 2019: graded bat feeding buzz x receiver pre-activity in Germany (foraging activity), different response, signal/controls.
- Carter 2015 and Eckenweber 2016: BCI Panama, distress-call phonotaxis, same field station. Costa Rica provides **a geographically separate primary source**, but not the same treatment/estimand and does not turn two prior papers into a meta-analysis.
- Kohles 2020: bat acoustic recognition (caller WHO), Panama. Costa Rica studies threat-driven suppression (WHEN not to expose social signal), not cooperation, personal spatial memory or reciprocity.
- 2026 Wilson's four-species paper: sign heterogeneity known, raw trial-level activity and group IDs unverified. Do not infer effect magnitude or absence across species from abstract.

### Explicit STOP claims

No universal personal-information vs social-information tradeoff, no global phylogenetic H1 estimate, no independent colony-group p-value from these 38 bats, no estimate of unobserved 79 individual cue effects, no adaptation/fitness claim and no experimentally isolated cognitive "threat classifier" from these two playback files alone.

Source DOI: https://doi.org/10.1098/rsbl.2025.0042 , data https://doi.org/10.5061/dryad.6djh9w1d3 , original author code https://github.com/morceglo/Predator-recognition .
