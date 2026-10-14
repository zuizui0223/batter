# Supplementary Material — anonymous review draft

**Associated manuscript:** Persistent individuality need not entail spatial partitioning in bats (anonymous draft).

**Contents:** experimental source metadata and frozen source-specific nulls, original six-panel wild vertical identity, terrain-relative fidelity and segregation tests, contemporaneous co-use uncertainty, external boundary cases, and evidence-tier rules.

**Review status:** source tables and estimands are retained; anonymous computational archive URL and author approvals are pending. This file is not the final submission version.

## Study scope and source-provenance principles

The study reanalyzes publicly archived bat experiments and independent repeated field tracking datasets. The individual bat is the biological replication unit; trial, call, GPS fix, session, dyad and permutation counts are not substitutes for independent biological individuals. Study-specific statistical endpoints and exchangeability nulls were recorded before their corresponding result values were opened, whereas the across-source synthesis was iteratively developed and not preregistered as a prospective multisystem meta-analysis. Field terrain-relative and co-use analyses were explicitly **post-outcome diagnostics**.

The detailed reproducibility contracts and legally redistributable data-derived tables will be linked from the anonymized source archive when placed: [ANONYMIZED_REVIEW_ARCHIVE_URL]. Original source data are cited under their public source DOIs.

## Supplementary Table S1. Experimental public sources and provenance

| Source | Species | Public archive | Programme role | Biological n | Source-level status |
|---|---|---|---|---:|---|
| Harten et al. 2020 | Rousettus aegyptiacus | Mendeley 10.17632/n9d8gbz3xr.1 | first-flight history formation/maintenance | 14 | primary formation FAIL; late secondary supported |
| Rachum et al. 2025 | Rousettus aegyptiacus | Mendeley 10.17632/wh7c636y3t.1 | randomized enrichment / individualization | 29 | unsupported individualization |
| Elie et al. 2024 | Rousettus aegyptiacus | Mendeley 10.17632/h5ff9vv5pc.1 | randomized auditory-feedback development | 10 | no difference in total individualization |
| Taub & Yovel 2020 | Pipistrellus kuhlii | source public archive / source paper | external sensory masker | 6 | supported |
| Foskolos et al. 2022 | Myotis daubentonii | Zenodo 10.5281/zenodo.4946256; Dryad 10.5061/dryad.ngf1vhhv3 | graded masking | 3 complete | supported; small n |
| Diebold et al. 2024 | Eptesicus fuscus | Zenodo 10.5281/zenodo.13857870 | reversible auditory-midbrain perturbation | 4 | supported; small n |
| Aharon et al. 2017 | Pipistrellus kuhlii | Mendeley 10.17632/f6mvhj5gj9.3 | navigation-context manipulation | 4 | supported |
| Teshima et al. 2026 | Rhinolophus nippon | source public archive | coarse policy portability | 5 adult mechanism cohort | supported; small n |
| Eveland et al. 2026 | Carollia perspicillata | public repository 00keveland/Tunnel_2026 | external fixed-representation transfer | fixed evaluable cohort | coarse supported; detailed geometry unsupported |
| frozen wild carrier programme | multiple wild bat panels | source Movebank datasets | laboratory-to-wild boundary | 4 panels | 2/4 FAIL |

---

## Supplementary Table S2. Experimental endpoint definitions, biological support and frozen nulls

| Source / analysis | Biological unit | Frozen endpoint / representation | Scale / shared-context removal | Biological support | Frozen null | Primary rule / status |
|---|---|---|---|---|---|---|
| Harten first-flight primary | juvenile bat | individual Spearman slope (B_i) of own-history predictive advantage vs prior valid-day count | source-coordinate spatial-history score; equal individual weighting | 14 juveniles, target valid-day ordinals 3–20 | 9,999 whole-history identity permutations within cohort | programme excess >0, p<=0.05, >=70% positive slopes; **FAIL** because 8/14 positive |
| Harten late-history secondary | juvenile bat | mean late own-history advantage (L_i), target ordinals 11–20 | same frozen source-coordinate estimator | same 14 juveniles | same frozen permutation architecture | predeclared secondary; L=+112.5554, p=0.0001, 12/14 positive |
| Harten recent-vs-earliest diagnostic | juvenile bat | (Q): recent two-day history advantage minus earliest two-day history advantage | equal-sized two-day history windows | same 14 juveniles | post-primary diagnostic permutation | **diagnostic only**; cannot rescue failed primary |
| Rachum laboratory individualization | bat | 3-D change vector: Boldness, Exploration, Activity | traits standardized from pooled Trials 1–2 only; treatment-group mean change removed | Season-2 complete n=29, 14 enriched / 15 impoverished | 199,999 origin-stratified random assignments, seed 202610070817 | D=V_enriched-V_impoverished >0 and p<=0.05; **unsupported**, p=0.167785 |
| Elie developmental auditory feedback | bat | 28-D whole-repertoire adult vocal centroid | treatment-blind feature scaling; sex×treatment centroid removed | 10 randomized bats, 5 hearing / 5 deafened; >=1,037 finite calls per bat×feature | exact 120 sex-conditioned assignments | two-sided treatment contrast in total residual dispersion; **no difference in amount**, p=0.716667 |
| Taub & Yovel masker | bat | source-native approach/movement angle personal-bias state | condition-centered personal bias | 6 bats baseline→masker; independent foam contrast 5 bats | exact complete identity permutations: 6!=720 and 5!=120 | K>0 with exact upper-tail support; both contrasts **supported** |
| Foskolos graded masking | bat | log flight-time identity state across five noise levels | shared condition mean removed | 3 bats complete across all 5 levels | exact 1,296 legal condition-wise identity assignments | positive programme identity advantage + exact support; **supported, small n** |
| Diebold auditory-midbrain perturbation | bat | 4-D trial vocal vector: duration, bandwidth, IPI, call rate | treatment×trialtype pooled mean removed without identity; pooled residual SD | 4 DREADD bats with >=5 saline and >=5 ligand trials | exact 4!=24 saline/ligand identity mappings | K>0, p<=0.05; **supported**, true mapping rank 1/24 |
| Aharon navigation-context manipulation | bat | bilateral turning-location vector from per-trial left/right medians | source-condition mean removed across 4 bats | 4 bats × 3 source conditions; >=10 valid trials/cell | con anchored; labels independently permuted in 75 and 300: (4!)²=576 | K>0, p<=0.05; **supported**, rank 2/576 |
| Teshima/Rhino transparent policy | bat | fixed (I,M) from eight 3-D trajectory features | feature z-scoring within obstacle environment | 5 adult *Rhinolophus nippon* | 9,999 environment-wise identity permutations, frozen seed | K>0, p<=0.05, positive individual fraction gate; **supported**, 5/5 positive |
| Eveland/Carollia fixed I/M | bat | Rhino-fixed (I,M) representation | feature standardization within fixed date block | 7 evaluable bats across two date blocks | 9,999 trial-label shuffles within date block, seed 202610051141 | K>0, p<=0.05, >=70% positive bats, both block means >0; **supported** |
| Eveland/Carollia detailed geometry | bat | fixed scale-free Rhino trajectory-geometry representation | same fixed date-block architecture | same 7-bat external cohort | 9,999 fixed-architecture permutations | **unsupported**, K=-0.0350, p=0.2144 |
| Wild scalar carrier bridge | panel | frozen scalar FlightIntensity persistence | source-panel-specific frozen estimator | 4 wild panels | panel-level frozen PASS/FAIL gates | bridge opens only if >=3/4 panels support; observed 2/4 -> **FAILED FROZEN GATE** |
| Wild H/V localization | selected wild panel | post-outcome H/V components | harmonized/post-outcome representation | selected contexts only | post-outcome diagnostics | **exploratory only**; cannot reopen scalar bridge |


## Supplementary Table S3. Wild original panel archive register

| Original panel | Movebank archive DOI | Integrated role |
|---|---|---|
| *Tadarida teniotis* | 10.5441/001/1.52nn82r9 | Motivating boundary; centering fails |
| *Eidolon helvum* | 10.5441/001/1.k8n02jn8 | Comparative centered-shape PASS |
| *Hypsignathus monstrosus* | 10.5441/001/1.278 | Centered shape and terrain/co-use eligible |
| *Phyllostomus hastatus 2022* | 10.5441/001/1.282 | Centered shape and terrain/co-use eligible |
| *Phyllostomus hastatus 2023* | 10.5441/001/1.321 | Centered shape and terrain/co-use eligible |
| *Phyllostomus hastatus 2016* | 10.5441/001/1.322 | Centered shape and terrain/co-use eligible |

The original tracking source screen considered 23 Movebank parent datasets, admitted six same-event x-y-height repeated-tracking panels and then closed its source universe. The 2016 *P. hastatus* panel has weaker overlap of individual tracking windows (31.1%) than the five others, so identity/time confounding has a stronger residual limitation. The motivating *T. teniotis* panel is not a positive example of session-centered shape identity. All wild panel-level inclusion, source checksums and height-datum processing remain available in the original tracking source receipts and manuscript Methods.

## Supplementary Table S4. Session-centered vertical identity (original calibrated results)

| Panel | Biological n | Observed | Null mean | Calibrated excess (nats/fix) | Permutation p | Original verdict |
|---|---:|---:|---:|---:|---:|---|
| T. teniotis | 6 | -0.2629 | -0.2408 | -0.0222 | 0.5121 | FAIL |
| E. helvum | 20 | 0.3719 | -0.0710 | 0.4429 | 0.0002 | PASS |
| H. monstrosus | 24 | 0.0736 | -0.1032 | 0.1768 | 0.0002 | PASS |
| P. hastatus 2022 | 33 | -0.0394 | -0.1508 | 0.1114 | 0.0002 | PASS |
| P. hastatus 2023 | 16 | 0.0454 | -0.0726 | 0.1181 | 0.0002 | PASS |
| P. hastatus 2016 | 10 | -0.0084 | -0.5824 | 0.5740 | 0.0076 | PASS |

These are full-pipeline whole-session individual-label permutation nulls, not a test against a naive zero baseline. Each evaluated session was shifted to its own zero median before fixed vertical binning. Centering removes an additive constant altitude offset; it does not remove non-additive device error. The original tracking full individual-profile heatmap (103 individuals across five comparative panels) has now been **restored unchanged** from archived workflow artifact 10950667566 as [Figure 5B](figures/original_jae/figure6_individual_centered_shape_profiles.png); its exact source CSV and JSON are alongside the image, with original hashes and reconstruction details in the source-profile archive receipt. This figure is descriptive only: observed component ranges and heatmap heterogeneity are not separately exchangeability-calibrated; finite-session estimation noise and state-dependent altitude error remain possible.

## Supplementary Table S5. Terrain-relative individual fidelity and added segregation

| Field panel | Observed V_rel | V upper-tail p | Observed S_rel | S null mean | S null 2.5% | S null 97.5% | S two-sided p |
|---|---:|---:|---:|---:|---:|---:|---:|
| H. monstrosus | 0.04186 | 0.0001 | -0.01581 | 0.00008 | -0.01567 | 0.01380 | 0.0362 |
| P. hastatus 2022 | 0.09956 | 0.0001 | -0.00896 | -0.00037 | -0.02081 | 0.01755 | 0.3639 |
| P. hastatus 2023 | 0.07689 | 0.0001 | 0.01626 | 0.00069 | -0.03320 | 0.02602 | 0.2704 |
| P. hastatus 2016 | 0.07865 | 0.0345 | 0.02890 | 0.00018 | -0.09129 | 0.06912 | 0.4796 |

All four panels comprise *H. monstrosus* and three *P. hastatus* datasets (two species, not four). The terrain-relative geometry family was developed **post-outcome**. Positive V_rel fidelity was supported in all four. No S_rel panel supported the **positive added-segregation** direction; *H. monstrosus* showed a negative-side signal (two-sided p = 0.0362). The S null quantiles are permutation-null intervals and **not** confidence intervals for observed S. A positive uncalibrated S value alone is insufficient to support segregation.

## Supplementary Table S6. Synchronous co-use design, excess and compatibility uncertainty

| Field panel | Time window | Spatial scope | Biological n | Dyads | Encounters | Excess above phase-shift null (m) | upper-tail p | Dyad-bootstrap 95% compatibility range (m) | Positive direction supported? |
|---|---:|---|---:|---:|---:|---:|---:|---|---|
| H. monstrosus | 60 s | endpoint-excluded | 11 | 22 | 883 | -1.983 | 0.9045 | [-4.808, 0.985] | NO |
| P. hastatus 2022 | 60 s | endpoint-excluded | 6 | 10 | 347 | -0.947 | 0.9186 | [-3.207, 1.918] | NO |
| P. hastatus 2023 | 600 s | all-space | 6 | 8 | 679 | 3.574 | 0.0231 | [-4.633, 11.729] | YES |
| P. hastatus 2016 | 600 s | endpoint-excluded | 5 | 8 | 16096 | -0.854 | 0.8611 | [-3.127, 1.128] | NO |

The fixed co-use primary scores median terrain-relative vertical differences within each dyad then averages dyads equally. The source-specific phase-shift procedure breaks contemporaneous cross-animal height alignment at frozen actual encounters. The *P. hastatus* 2023 encounter set is **all-space with a 600-second window** because the endpoint-excluded universe did not meet its biological-individual gate; 2016 also used 600 seconds but endpoint exclusion. The 2023 positive result (+3.574 m, phase-shift upper-tail p = 0.0231) had eight dyads and a wide dyad-resampling interval crossing zero; neither this interval nor those in the other three panels are formal equivalence tests or power calculations.

## Supplementary Table S7. External wild centered-shape boundary tests

| Source | Calibrated excess | Original frozen p | n | Status / limitation |
|---|---:|---:|---:|---|
| *Nyctalus noctula* (first primary) | +0.05175 | 0.1224 | 27 | FAIL; later same-source revised eligibility is not the authoritative primary |
| *Hipposideros armiger/pratti* | −0.04468 | 0.8616 | 13 | FAIL |
| *Myotis vivesi* | +0.00470 | 0.4419 | 4 | FAIL in a separate four-individual programme |
| *Pteropus poliocephalus* | +0.16873 | 0.0001 | 4 | PASS in separate four-individual programme; after DEM subtraction +0.03231, p=0.0023 |

External results are scope/boundary probes, not a statistically sampled estimate of bat-wide prevalence. The original tracking V1/V2 *Tadarida* residual cell × height map did not support a stable individual-specific residual route map (p=0.160), even though its more basic absolute-height identity score was positive.

## Supplementary Methods S1. Boundaries of the three integrated inference axes

**Identity correspondence:** correct animal–behavior mapping after source-specific shared-condition adjustment. Each experimental study uses its own fixed representation, biological support and assignment null; raw K, A or B values cannot be combined into a single pooled metric.

**Developmental individualization:** origin-stratified or sex-conditioned assignment of randomized treatments and the corresponding effect on predeclared residual multivariate dispersion. Failure to reject a change in D does not prove that variance and covariance are identical under treatment, nor does it exclude trait-level changes. Elie feature contributions (15 positive, 13 negative) and Rachum trait contributions (all three positive) remain descriptive, not confirmatory reallocation tests.

**Field individuality vs partitioning:** the held-out centered-shape individual score, V_rel terrain-relative configuration fidelity, S_rel added-segregation test, and I synchronous co-use separation use different nulls. They quantify distinct ecological questions. Four/panel counts must not be interpreted as four independent species or four confirmations of a joint laboratory-to-field causal mechanism.

## Supplementary Methods S2. Evidence ranks and historical freeze amendments

1. A source-level primary must pass **all** frozen gates to be supported. The juvenile formation primary FAILS even though its mean permutation test p=0.0102, because only 8/14 slopes were positive against required 10/14.
2. The juvenile late-history result is a predeclared **secondary** that supports late personal-history prediction, but the early-vs-recent Q statistic is post-primary diagnostic.
3. Randomized developmental D contrasts are unsupported under their source-specific tests. **Absence of support is not statistical equivalence.**
4. A source-level structural STOP is not a biological FAIL (e.g. broad ERA5 wind reaction norm test stopped at 7 eligible *P. hastatus* 2023 individuals against eight required, before numeric vertical outcomes).
5. Field terrain/co-use and lag/kinematic stress tests are **post-outcome** diagnostic families, although their later specific null outputs were frozen before being inspected. Their inferential tier is not promoted retrospectively.
6. Frozen laboratory-style wild FlightIntensity scalar carrier: PASS/PASS/FAIL/STRUCTURAL STOP = 2/4, below ≥3/4 overall threshold. Later H/V field components are exploratory only and do not rescue the scalar field gate.
7. No universal neural policy, direct learned-route cause, specific fitness advantage, or competition absence has been identified.

## Supplementary Methods S3. Figure reproducibility and non-independence guard

Figs. 1–6 are reproducible vector summaries generated from the exact frozen source-summary snapshot and validated original individual-profile records. The combined Figure 5A/B plate is 177 × 238 mm; Figure 5B redraws the original 103 biological individuals' ten-bin probability vectors without smoothing or re-estimation. The complete original PNG, CSV and JSON are preserved unchanged and hash verified; the original figure's profile contrasts are descriptive only and have no component-wise null calibration. The rendering workflow checks figure determinism, XML structure, archived-source checksums and evidence-tier outcomes. The figure packaging adds no inferential tests and does not alter the source result receipts.

## Supplementary data access, redistribution and ethics

Original bat datasets remain governed by source-level licences and permit conditions. For example, the Taub and Yovel public Dropbox archive is linked in the original research publication but no independent redistribution permission was established by the present reanalysis. Raw third-party datasets should not be duplicated into the anonymized archive without source permission or editorial authorization. Public source DOIs and retrieval instructions are provided above; code and legally distributable derived products will be placed at [ANONYMIZED_REVIEW_ARCHIVE_URL].

The present study involved no new handling or manipulation of animals. Ethical oversight and permits for the underlying studies are reported by the original source investigators. The final anonymized archive link and source-data redistribution statements require author and journal verification.
