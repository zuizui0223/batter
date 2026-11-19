# H1 — can social cues update personal knowledge across bats?

> **CURRENT STATUS (2026-11-19, v10):** Authentic published 2015–2025 cue-response reanalyses remain source- and endpoint-specific. The 2019 new-lake graded-buzz×baseline moderator is not supported; no independent same-estimand external validation is available. Original 2007 male-sociality comparative source TXT and XLS were located at the publisher but returned HTTP403 under independent GitHub Actions; 2026 Wilson four-species original trial rows are not authenticated. A study/response compatibility audit now proves none of the eight examined source families supplies a new verified independent external replicate of the 2019 model. **No global H1 or H3 effect is fitted.** Existing JAE and main unchanged; PR remains DRAFT.

**2026-11-19, v3: prospective external validation design + source-backed aggregates + known-truth estimator falsification. No novel multi-species biological effect is claimed.**

All work remains separate from frozen batter JAE inferential results and from `main`.

## Completed / independently auditable work

1. **Theory seed, not an external test:** 2022 review Table 2 extracted into 35 rows, 29 explicitly named bat species plus one pooled-taxonomy row. Twenty rows have one of four strategies; the subset of 25 with measurable persistence and information-use site matches the review's framework by construction. Do NOT count this as replication.
2. **Original paper ledger:** 12 targeted context/receiver observations, eight named taxa, six original-study clusters from 2024–2026. No new independent fully measured cases yet meet the classical four-strategy global phylogenetic response test. No systematic worldwide sampling frame/absence denominator.
3. **New prior-art guardrail:** 2019 experimental study (Lewanzik et al.) already tested 24 emitted-signal×recipient group combinations at 12 lakes, not 24 independent recipient species, and ecological context modulated cue responses. Four recipient groups had negative coefficients of pre-playback activity on the response defined as playback-minus-pre-playback activity; 3 species + one mixed NEV group, not four separate studies.
4. **Known-truth mathematical gate:** In a stationary no-social-effect world, fitting (during-pre) ~ pre yields slope rho-1; all 128 simulation replicates at each of rho=0,0.5,0.9 had negative slopes, reproducing the negative-baseline *sign* with true social competition=0. The observed 2019 negative signs therefore cannot alone identify an actual social-cost effect; this does not disprove the published interpretation or invalidate cue-specific results.
5. **Sex-specific actual published model contrasts:** 2026 Glossophaga paper reported male/female playback-vs-silent flower-visit RRs 0.17/6.57 for alert and 0.73/2.58 for benign calls (16 biological bats; 8 each). Descriptive female/male ratio-of-rate-ratios =38.65 alert, 3.53 benign. Both effects belong to ONE prior study, not novel bat evidence or independent replicated species.
6. **2024 author-original data QA:** Rousettus odor intervention 10 naive visitor IDs out of 56 naive bats (17.86%); source total cell 22 rather than 23 on 19 July 2020, no effect on naive denominator. This was a count verification, not new cue information/memory mechanism.
7. **Automated validation:** isolated GitHub Action checks source-unit boundaries, deterministic 2019/2026 reconstruction, known-truth null, and analysis STOP gates (6 unit tests PASS).
   - [Latest validated negative-control run](https://github.com/zuizui0223/batter/actions/runs/44449278361)
   - [Source tracking](https://doi.org/10.1111/1365-2656.12989) and [2026 original](https://doi.org/10.1111/nyas.70427)

## Primary scientific decision

The publication-grade novelty cannot be merely 'social information is context dependent' or 'fruits mean personal knowledge and insects mean social knowledge'. Those are prior art or overly restrictive, respectively.

**Testable next question**: Does the *causal* effect of a given acoustic or social cue on foraging decisions change with independently measured baseline resource/social context (receiver sex, competitive ability and actual alternative patch opportunity), beyond regression-to-the-mean and method-specific observation effects?

Valid proposed treatment interaction: difference in during-cue and randomized time-matched silent-control response, conditional on a pre-treatment activity stratum; the raw baseline shared with a difference-score outcome must not be confused with actual crowding moderation. A 0-buzz playback that contains search calls is **not** a true silent control.

**STOP** global H1 effect fit / H3 individual memory tradeoff: sources have incompatible outcome units (activity change in bat-seconds/min vs flower-visit RR vs tree visitation), and no controlled multi-study comparable summary/detection-negative frame yet.

## Files

- `H1_PREREG_AND_FEASIBILITY_V1.md` — initial hypotheses, gates, source selection
- `H1_CODING_DICTIONARY_V1.md` — independent blinded coding dictionary
- `H1_V2_INFORMATION_CHANNEL_AMENDMENT.md` — when-versus-where hypothesis, source provenance
- `REVIEW_TABLE2_BASELINE_V1.csv` — 35 legacy review cases
- `POST2022_PRIMARY_EVIDENCE_V1.csv` — 12 targeted ecological context rows
- `PUBLISHED_LEWANZIK_2019_DENSITY_V1.csv` — four published baseline coefficients and 95% CrIs
- `PUBLISHED_GLOSSOPHAGA_CONTRASTS_V1.csv` — eight published rate-ratio/z pairs; no invented raw data
- `CROSS_STUDY_SIGN_AND_BASELINE_COUPLING_AUDIT_V1.md` — identification proof, estimator compatibility, ecology limits
- `published_contrast_and_change_score_audit_v1.py` — deterministic aggregate and simulated-null receipt
- `test_published_contrast_and_change_score_audit_v1.py` — 3 dedicated tests
- `ROUSETTUS_ORIGINAL_SOURCE_QA_V1.md` — author original CSV QA
- `run_h1_feasibility.py` and `test_h1_feasibility.py` — primary feasibility and 3 tests
- `.github/workflows/h1-social-information-evidence.yml` — 2 JSON receipts in CI artifact

## Next empirical gate, not yet executed

Original Lewanzik 2019 Dryad source is an ~84 KB XLSX (https://datadryad.org/dataset/doi:10.5061/dryad.gp65g2t). Public metadata was verified, but binary download via this environment was blocked. Do not claim a raw reanalysis. Current Dryad access may require tokenized API downloads. Source-provenance gate must precede any computation or ingestion. The 2026 individual-bat data are in supplementary files/requested from the corresponding author and were not ingested. A genuine held-out across-study test is not yet possible.

**Branch/claim firewall:** proposal and source QA only. No `main` merge or change to frozen 3D individuality outcome.


## 2026-11-19 source/identifiability gate update (v4)

**Empirical Dryad source acquisition: STOP.** The original 2019 XLSX is listed by Dryad, but the fresh GitHub Actions runner got HTTP403 (published file_stream) and HTTP401 (both documented API routes). No source workbook or biological results were retrieved; the dedicated source-gate CI intentionally FAILED with JSON receipt. See [source attempt run](https://github.com/zuizui0223/batter/actions/runs/44452289881), `LEWANZIK_2019_ORIGINAL_SOURCE_ACCESS_STOP_V1.md` and `source_schema_lewanzik_gate_v1.py`. Do not claim the original 2019 data were re-fitted.

**New prospective response estimand frozen before opening any 2019 outcomes:** evaluate the buzz-information signal, 0/12/24/48/96 feeding buzzes/min *within acoustic caller identity*, against baseline activity using absolute Y_playback as response, with `buzz×X_pre` moderation and lake-blocked transfer. 0 buzz includes bat search-phase calls and is not a no-social-acoustic control; pre/post silent controls are phase-confounded. This source is 12 lakes, 30 randomized blocks per lake, not 24 independent recipient bat species. See `LEWANZIK_2019_FROZEN_ANALYSIS_AND_SOURCE_GATE_V1.md`.

**Synthetic-only estimator positive/negative control: PASS** (12 lakes×30 blocks×128 replicates per world):
- Known truth cue×baseline interaction=0.0: recovered mean +0.008619, while naive difference-score baseline slope mean -0.346658.
- Known truth cue×baseline interaction=+0.8: recovered mean +0.808944, while naive difference-score baseline slope mean -0.048503; 128/128 estimated interactions positive.
- Source-code-only tests and all pre-existing H1 tests: **7/7 PASS** with [CI and JSON receipt](https://github.com/zuizui0223/batter/actions/runs/44452894981). No real bat effect estimate is identified by this simulation.

**Scientific decision:** strong *methodological* reason to separate receiver baseline density from baseline-subtracted response, but the original empirical source is inaccessible via verified interfaces. STOP empirical density-context interaction and H3 cognitive-memory/social-information generality until authenticated original row-level source or independently eligible other experiment is available. Frozen batter JAE/BE claims stay unchanged.


## 2026-11-19 v5: ORIGINAL USER-SUPPLIED DATA RECOVERED; prospective H1 empirical test completed

The independent Dryad automatic fetch STOP from earlier in the same day remains documented as a historical **401/403 access-path failure**. It is no longer a missing input: the user uploaded Dryad v20190410 ZIP and the original XLSX SHA256 was verified as `fbabb5021c613aa7033ad13bc1a357a68700a7d3683ec16ae1bcf4a65e121c86`. **No raw XLSX uploaded to this GitHub branch.**

- **Verified original design:** 1,440 complete source rows, 12 lakes, 6 callers ×5 buzz rates ×4 response classifications. 360 unique stimulus blocks, no duplicate 6×5 combination within lake, and published authors' 250/94/110/180 selection counts exactly reproduced.
- **Structural eligibility:** *P. nathusii* absent at one of 12 original lakes, leaving 330 rows/11 independent lake-folds for its recipient-specific H1 (all other groups 360/12). `NEV` remains a pooled three-genus response, not a species.
- **Frozen *new H1* test:** buzz×pre-playback-activity interaction for actual playback activity (not `Y-X`), with caller and caller×buzz adjustment, pre-period heterospecific presence, time and lake grouping; genuinely unseen lake out-of-sample prediction.
- **Empirical result:** interaction confidence interval includes zero in all 4 responses and equal-lake held-out log-score increment is **negative in all 4**: Myotis `-0.00119484`, NEV `-0.00171772`, Pnat `-0.00309600`, Ppip `-0.00308932`. **STOP** strong ecological moderation/generalization claim.
- **Sensitivity:** quadratic buzz×caller nuisance keeps all four increments negative; author's exclusion of `pre=0 & during=0` changes Pnat to a *positive* `+0.00627` but conditions selection on the post-treatment outcome, so is not admissible as a replacement primary causal test. This sensitivity explicitly limits the generality of the negative result.
- **Reproducibility:** `H1_EMPIRICAL_LEWANZIK2019_RESULT_V1.md` / `H1_EMPIRICAL_LEWANZIK2019_RECEIPT_V1.json` document results and source checksum; `h1_empirical_reanalysis_v1.py` is the source-pinned executable taking `--xlsx` (local original) and `--out` aggregate JSON; `test_h1_empirical_receipt_v1.py` validates claim/format consistency without falsely implying an original-source CI rerun.
- **Unchanged:** frozen batter JAE/BE, `main`, and all original author findings. This is one central European study, not a multi-paper global meta-analysis.

Next valid scientific progress is an **independent matched randomized cue×baseline study**, not more outcome-driven tuning of this original dataset.


## 2026-11-19 v6 — independent published Molossus 2020 source audited

- Published Kohles et al. 2020 original *Molossus molossus* video-analysis CSV (DOI 10.5061/dryad.tqjq2bvvx) is readable as a public 51-row web text document. **Only web text transcription, original byte-MD5 not yet verified.** Source-specific search-phase 34 trials, **19 biological bats**, 5 roosts, 20 test/14 controls. Exactly 12 animals have matched test and control.
- This outcome is **individual auditory discrimination** (40-second head waggles after changing caller vs retaining the caller), not the 2019 graded buzz×baseline foraging response. **No numerical pooling.**
- Source-published discrimination result recalculated from web text: bat-equal matched increase **+12.71 head waggles/40 sec**, 10/12 bats positive, exploratory bat-level signflip p=0.01123. Roost-equal contrast **+10.4**, **4/5 roosts positive**, signflip p=0.25 with low-n bootstrap interval [-2.4,+21.25]; **cross-roost generality unproven**. These are existing published biological phenomena, not new discoveries.
- Approach-call data are 17 public rows vs 19 article-described trials; four matched bats do not pass the registered minimum. **STOP** any approach-based confirmatory interpretation.
- [External source methods and limits](EXTERNAL_SOURCE_DISCRIMINATION_CONTRACT_V1.md), [empirical report](H1_EXTERNAL_MOLOSSUS_2020_RESULT_V1.md), [aggregation receipt](H1_EXTERNAL_MOLOSSUS_2020_RECEIPT_V1.json), [cross-study compatibility](H1_EXTERNAL_SOURCE_ELIGIBILITY_V1.csv), [source-reading script](reanalyze_molossus_2020_source_v1.py). GitHub CI tests aggregate integrity and compiles source reading code, but does not rerun original source because raw CSV is not committed.

**Programme conclusion:** The claimed simple private-vs-social tradeoff is still unsupported; the independent Molossus case illustrates an additional class of social information (caller identity) but does not externally reproduce Lewanzik's cue-density interaction. True between-study standardized H1 test still requires an eligible independent original experiment with matched treatments, controls and response.

## 2026-11-19 v7 — original 2020 Zenodo bytes authenticated

**Supersedes the v6 web-transcription uncertainty, not its observed numerical conclusions.** Original public CSV was independently obtained in [Actions run 44462987103](https://github.com/zuizui0223/batter/actions/runs/44462987103), 3298 bytes, HTTP 200, published MD5 `b4b9970eac190601b4a291725137c110` **PASS**. The source-pinned original reanalysis independently confirmed 34 search-phase trials / 19 bats / 12 matched bats / 5 roosts, bat mean +12.70833, roost mean +10.4, roost exact signflip p=0.25. Authenticity receipt: `H1_EXTERNAL_MOLOSSUS_2020_AUTHENTICATED_V2.json` and amendment `H1_EXTERNAL_MOLOSSUS_2020_SOURCE_AMENDMENT_V2.md`. Raw animal observations were not committed or uploaded. This remains **published prior art** and **not** cross-study replication of the graded-buzz×baseline ecological moderator.

## 2026-11-19 v8 — two public distress-call source reanalyses completed, not two independent regions

- **2016 Eckenweber & Knörnschild**, published `S. bilineata` responses to distress calls at roost versus foraging ground: authenticated original Europe PMC XLSX, SHA256 `28402ac6c969f7a6c13acf5f90192afbfa4b6c5158e1bbc8f657b55f255b05ef`. Original 114 rows = 19 session IDs × 3 locations × 2 callers, but only **11 real physical colonies** under unknown session-to-colony crosswalk. Original response mean during-minus-pre: at roost `S. bilineata` +30.97 vs `M. molossus` +3.21; at foraging −12.63 vs −1.13. The **call identity × location difference-in-difference** averages **+39.2579**, 14/19 sessions positive. Its **exact mean partial-ID bounds** over all possible 8 doubled+3 singleton colony mappings are **[+22.7682,+56.2909]**. This bound is not a population confidence interval, test p, or randomized place effect.
- **2015 Carter et al.**, authenticated original Figshare CSV MD5 `991be124c47f48a955fa5a0a40dd864c`, **308 trials** (155 Molossus distress vs 153 noise), 12 session IDs at eight reported physical sites (site mapping missing). Session-equal distress-minus-noise playback-change averages *M. molossus* **+0.54936** passes/min (9/12 sessions positive), *S. bilineata* **+0.25371** (6/12 positive). The author's zero-activity outcome-based exclusion changes effect magnitudes; retained as sensitivity, not primary.
- **Geographic caveat:** BOTH experiments were carried out at the Smithsonian **Barro Colorado Island station in Panama**, where the authors' groups and study sites may overlap. They are original distinct experiments, **NOT independent regional or biologically proven nonoverlapping population replications**, and the treatments (distress vs noise, same vs different bat caller) are not equal. No valid meta pooled effect.
- **Original-source empirical workflow:** [source-authenticated checksum + analysis run 44464841326](https://github.com/zuizui0223/batter/actions/runs/44464841326); derived receipt `H1_TWO_DISTRESS_ORIGINAL_RECEIPT_V1.json`, scientific report `H1_TWO_DISTRESS_ORIGINAL_EMPIRICAL_V1.md`, `H1_CROSS_STUDY_RESPONSE_COMPARABILITY_V2.csv`, and source-pinned runner `h1_2015_2016_original_empirical_v1.py`. Files with original animal trial rows were **not committed**. Existing publications already reported the central behavior; the present analysis adds data provenance and uncertainty boundary, not a first bat discovery.
- **Wilson et al. 2026** four-species original playback results can be compared qualitatively from publications, but raw trial-level table and observation denominators remain unverified. Never treat publication-level no-detection as a species-wide zero.

**STOP:** no across-species transferable cue×density law, no 11-independent-colony test p, no reciprocity mechanism or private-memory/social information tradeoff. Independent source studies across other regions with harmonized cue/response/control/effort are required before a macro hypothesis test.

## 2026-11-19 v9 — independent Costa Rica 2025 risk-gated *social calling* source verified

Gamba-Rios et al. (2025, *Biology Letters*, DOI `10.1098/rsbl.2025.0042`) tested 117 *Thyroptera tricolor* bats from 33 social groups at **Hacienda Barú, Costa Rica**, beyond the Panama BCI site. Original authors' public `data.csv` on GitHub [Predator-recognition](https://github.com/morceglo/Predator-recognition) (also Dryad `10.5061/dryad.6djh9w1d3`) contains **228 rows from 38 bats that actually emitted responses**, each with predator and one nonpredator cue × before/during/after. The other **79** tested animals are not included as rows; no social-group ID in published behavioral CSV.

- **Authenticated original** (author Git blob SHA1 `b8a119df0204ed0beb90b971c97f60cafbdb74cd`, source SHA256 `11e281708be94ad76b0875d8cf43adf605e8095bb500ad43936f20a3c98d77d3`).
- **Matched 38-responder analysis:** mean `[(log1p(during)-log1p(before))_predator - same_nonpredator]` = **−2.16529**, median −2.14586, **35/38 negative**; first-nonpredator −2.126 (20/22 negative), first-predator −2.219 (15/16 negative).
- **Unknown social-group membership partial identification:** 38 recorded responders all come from 33 groups, with ≥1 responsive animal per group. Enumerating all 7 group-size allocations of five extra responders and all possible source individual placements gives **sharp 33-group-equal responder mean bounds [−2.56924,−1.75302]**. Strictly negative under ANY matching. **NOT a 95% CI, group-independent statistical test, full 117-animal estimate, or causal individual difference.**
- **Prior-art guard:** the original 2025 authors already reported predator sound suppression of group social response calling, acoustic call similarity/order effects, and cage group-cohesion association. This reanalysis provides source verification and a conservative missing-group mapping sensitivity. It is **NOT an independent replication of 2019 graded foraging buzz×baseline activity**, not a test of memory, and does not add another bat species to any valid pooled H1 effect.
- **Code and evidence:** `H1_COSTARICA_PREDATOR_RISK_PREOUTCOME_CONTRACT_V1.md`, `h1_costarica_predator_cue_source_v1.py` (original raw Git blob verified before numeric opening), `H1_COSTARICA_2025_AUTHENTICATED_RESULT_V1.json`, `H1_COSTARICA_2025_EMPIRICAL_NOTE_V1.md`, `H1_CROSS_STUDY_RESPONSE_COMPARABILITY_V3.csv` (separate estimands), and CI [original-source run 44473278891](https://github.com/zuizui0223/batter/actions/runs/44473278891). No raw individual IDs stored.
- Wilson et al. (2026) original four-species playback source remains a **trial-denominator/source-eligibility STOP**, not a valid four-species held-out effect.

**Ecological implication as hypothesis, NOT a universal rule:** useful information is multidimensional (*who* gave the cue, *when/where* a resource can be used, and *risk to publicly advertising one's location*). The Costa Rica source demonstrates an already published **risk-to-communication tradeoff** in one bat species, not a universally estimated private-information/social-information tradeoff.

## 2026-11-19 v10 — direct macro H1 response feasibility and external same-taxon context

- **Species-level original source found but inaccessible via current automated path:** Safi & Kerth (2007) `42248data.txt` and `42248data.xls` are publisher-listed original male-social-group coding/trait files. Both downloads were HTTP403 in separate GitHub Actions steps. [Expected failure + metadata receipt](https://github.com/zuizui0223/batter/actions/runs/44511407420). **No 2007 original rows or new phylogenetic coefficient have been inspected.** Roost male group formation remains distinct from tested social foraging.
- **Published same-species context contrast, NOT matched replication:** *Myotis lucifugus* responded to conspecific distress in a New Hampshire barn (1976), whereas Canadian foraging-stream acoustic monitoring reported no detectable response to the tested conspecific/heterospecific sequences (Wilson 2026). *Lasiurus cinereus* approached conspecific and Eptesicus playback in the western US (2018) and showed attraction primarily to conspecific hawking sequences in Canada (2026); different stimuli, response units, methods, and regions **cannot isolate habitat moderation or prove a new mechanism**. The 2018 Dryad `AudioVideoData.xlsx` is an **audio/video filename map**, not the needed original per-playback response. In the 2026 abstract the Eptesicus fuscus direction is not supplied and **must remain unknown**, not a true tested negative.
- **Other sources are biologically relevant but not H1 replications:** 2024 Vespertilio murinus synchronized male co-foraging (already prior art, Białowieża, DOI 10.1016/j.anbehav.2024.08.020); 2025 Phyllostomus hastatus Panama study (already published source-backed noncoordinated commuting); 2024 global 1279-species anthropogenic roost trait is NOT a measure of social information or male groups.
- **Reproducible result:** `H1_MACRO_2007_ORIGINAL_SOURCE_AND_EXTERNAL_RESPONSE_GATE_V1.md`, `h1_male_sociality_2007_source_gate_v1.py`, `H1_INDEPENDENT_REPLICATION_ELIGIBILITY_V4.csv`, `test_h1_independent_eligibility_v4.py`, `H1_GLOBAL_COMPARATIVE_GO_NO_GO_20261119.md`. Eight distinct published-source entries checked; **zero independent source entries replicate the exact 2019 buzz×preplayback moderator**. No raw data files or copyrighted supplements committed.
- **Next admissible target:** original 2007 TXT/XLS plus genuinely independent new male-sociality species coding (sex, effort, region) **OR** Wilson 2026 trial-level data plus another harmonizable playback study; otherwise **STOP** and retain old literature synthesis without numerical global claim.

**This is a source-sufficiency result, not a biological no-effect test.**
