# Unified manuscript integration QA v1

**Date:** 2026-10-14  
**Level:** Source-text numeric reconciliation and epistemic-claim review. This is **not** a raw-data reanalysis, journal production validation, or independent rerun.

## Immutable source files verified

- JAE frozen: release/jae-v0.4.0-rc2, manuscript/MANUSCRIPT_DRAFT_V0_4_0.md, blob SHA c4ef51a7f3f291a6f203d303dbf73f5b54fb7683.
- BE frozen: prospective/public-causal-synthesis-v1, prospective/public_causal_synthesis/MANUSCRIPT_DRAFT_V1.md, blob SHA a83fed81a141c62df29f3c12f2fb5fd36399c160.
- BE authoritative numeric ledger: prospective/public_causal_synthesis/MASTER_RESULTS_TABLE_V1.md.
- The JAE draft copied on the BE branch had different SHA 2a4b2a3aafc8a4a8b4f495f4148e888f1a9c789c. All JAE-specific integrated claims were instead sourced from canonical rc2.

## Textual numerical audit performed

The committed unified draft was retrieved again from GitHub after creation and after rendered figure legend integration. Its values were compared with the canonical JAE manuscript and the BE authoritative numeric ledger (normalizing optional leading plus signs only).

- **Wild numeric keys checked: 21/21 found in both wild source and unified manuscript.** Keys: 0.443, 0.177, 0.111, 0.118, 0.574, -0.022, 0.5121, 0.042, 0.100, 0.077, 0.079, -0.0158, -0.0090, 0.0163, 0.0289, 3.57, 0.98, 1.92, 1.13, 0.0544, 0.0345.
- **BE numeric keys checked: 14/14 found in both BE ledger and unified manuscript.** Keys: 0.16733, 112.5554, 144.0791, 0.7081, 0.734699, -1.425497, 4.941, 6.779, 0.377542, 1.004452, 3.695264, 0.55428, 0.34758, -0.0350.
- **Manuscript provisional length:** approximately 8000 whitespace-delimited words including 37 scholarly reference entries and figure legends. The manuscript is a working Markdown document and this is not the target journal's official word count; the initial section counts are superseded by the subsequent bibliography and figure amendments. This is a drafting metric rather than the journal's official word counter.

This audit detects transcription-level omissions/mismatches of selected numbers; it does **not** verify code execution, calculation reproducibility, assignment semantics or all results. Full original source tables and receipts are authoritative in any discrepancy.

## Biological / inference QA

| Check | Outcome | Why it matters |
|---|---|---|
| BE juvenile p=0.0102 but frozen 8/14 < 10/14 rule | PASS — primary called FAIL | Avoids upgrading composite-gate failure |
| Developmental p=0.167785/0.716667 | PASS — described as nonsupport, not equivalence | No claim that development has zero effect |
| Acute experiments n=3,4,4,6 | PASS — source n limitations stated | Exact identity null not species prevalence |
| Coarse Rhino/Carollia positive, detailed geometry unsupported | PASS | Avoids universal latent-policy inference |
| Original wild five comparative centered-shape PASS with focal Tadarida FAIL | PASS | Conflicting original evidence retained |
| External Nyctalus/Hipposideros/Myotis failures plus Pteropus success | PASS | Avoids selective positive-source narrative |
| Four wild terrain/co-use panels represent two species | PASS | Prevents pseudo-independent taxonomic replication |
| V_rel 4/4 supported vs S_rel 0/4 positive supported | PASS | Ecological novelty preserved |
| Hypsignathus negative-side S_rel p=0.036 | PASS | "0/4 positive" not misdescribed as universally null |
| P. hastatus 2023 positive co-use | PASS | Coarse encounter rule and heterogeneity explicit |
| Co-use compatibility endpoints vs equivalence | PASS | No improper no-effect claim |
| Bridge PASS/PASS/FAIL/STOP = 2/4 | PASS | Neither full rejection nor false success |
| Wind-family structural stop | PASS | Not mislabeled a negative wind-mechanism result |
| Post-outcome wild terrain and maintenance | PASS | Not retroactively declared prospectively registered |
| Source-level experimental programmes heterogeneous | PASS | No pooled numeric effect |
| Mechanistic learning, morphology, resource state | PASS | Maintained as hypotheses, not demonstrated causes |
| New independent outcomes generated | NONE | Reinterpretation only |

## Remaining review/production gates — not passed

1. A second human statistical review of each key panel including frozen support denominators and population-level limitations.
2. Textual bibliography merge complete (45 source-manuscript DOIs plus two added external ecological papers (Carlson 2021; Calderón-Capote 2025), yielding 37 main scholarly references). **Publisher-level DOI resolution, author names/year suffixes, in-text citation coverage and final journal style remain unverified**.
3. Original numerical pipelines independently re-executed if coauthors or the target journal require it. This integration did not rerun them.
4. Figures 1–6 pass source-backed SVG reproduction and original JAE source-profile hashes. Assistant preview of six figures and original source heatmap recorded (FIGURE_RENDER_VISUAL_QA_V1.md); **journal-size human-coauthor/grayscale approval is still pending**.
5. Combined SI **working draft** assembled, but full method/provenance archival appendices, anonymized reviewer archive, source redistribution licences, journal rule verification, final PDF/figure conversion QA and DOI remain pending.
6. Authorship, institutional approvals, funding, CRediT, conflict and AI-methods disclosures approved by the human authors.

**Assessment:** The integrated draft is a coherent evidence-bounded scientific candidate. The field-study source attribution check corrected the three Phyllostomus year-to-DOI assignments and the Eidolon source publication, without changing numerical outcomes. The supplementary Methods now include eleven source-specific sections. This QA supports text-level numerical alignment and boundary discipline only; it does not declare the new manuscript submission-ready.

## Ecological identifiability and priority amendment — 2026-10-14

- **Verified previously completed post-outcome conditional tracking**: 500-m place × speed × turning individuality supported 4/4 eligible panels (n=19,23,11,9; calibrated excess +0.3840,+0.0868,+0.1015,+0.4514; p=0.0002,0.0002,0.0006,0.0286). This is a sensitivity/maintenance analysis, not independent biological replication.
- Same-night shifted-night conspecific comparator supported 3/4; original P2016 p=0.0544 fails its frozen gate despite a positive calibrated excess. Lag checks ≥1/≥3/≥7 days have changing denominators of 4/3/2 structurally eligible panels and do not support a common temporal decay model.
- Frozen continuous wind reaction norm remained **structural STOP**: P2023 7 vs 8 required and no numeric vertical response opened. This cannot support a wind null-effect conclusion.
- **Model non-identifiability**: an explicit two-task/two-height-bin mathematical illustration produces exactly the same marginal p_A=(0.6,0.4), p_B=(0.4,0.6) either through personal task proportions or through within-task differences. Toy probability overlap=0.8 and KL=0.081093 nats are mathematical, not source effect sizes, and do not stand in for empirical S_rel.
- **Historical novelty correction**: Carlson et al. (2021; DOI 10.1038/s41467-021-24826-x) had already shown stable strongly overlapping/nested individual environmental niches in white storks. Wang et al. (2023) documented spatial specialization/overlap variation in bats. The novel candidate is the limited 3D source-specific vertical-shape/conditioning/co-use test architecture, **not** the first demonstration that overlapping individual niches are possible.
- Frozen source receipts are pinned with original branch/path/blob SHA and full result summaries in `figures/FROZEN_MAINTENANCE_BOUNDARY_INPUTS_V1.json`; mathematical and numerical assertions run in `validate_ecological_identifiability_v1.py` under the main-figure and SI CI. Original source branches were not modified.

These additions strengthen interpretive clarity, not the evidence tier. No new source outcomes, causal task/learning results or preregistration are introduced.

## Exploratory descriptive original-profile overlap QA (2026-10-14)

This **post-outcome descriptive transformation is new**, unlike the frozen primary results. The design rule was committed before computing overlap values, but the underlying profiles/individuality outcomes had already been inspected; do not describe it as independent validation or prospective registration.

- Immutable original profile JSON SHA256: `9efd5d2914ad012905a004aee1114d715deaaf94e3f54689deb4f1208a188cb2` (the source remains unchanged).
- All 103 original individual profiles used and exactly the 5 original comparative panels included. Strata defined by the exact original collection site/colony/year cohort, never between cohorts. Original individuals 20/24/33/16/10 and within-cohort unordered pairs 41/276/262/60/45 = **684 dependent dyads**, in 12 source cohorts with one singleton cohort.
- Metric: 10-bin centered residual-height probability intersection O = sum(min(p_i,p_j)) = 1 - total-variation distance. In the five panels, descriptive dyad median O: **0.817036 / 0.800608 / 0.918737 / 0.898593 / 0.802058**. The corresponding 10th/90th percentiles are empirical across-dependent-dyad ranges, not confidence intervals.
- Reproduction from original byte-verified JSON via pure Node script plus regular PR figure CI verifies all derived pair rows and medians, source original n, 1D metric algebra, and supplementary Figure S1 SVG/XML layout. The underlying full-pipeline identity/terrain S_rel/co-use analyses remain unchanged.
- Caution: original profiles were estimated on **individual-specific supported horizontal cells/weights**, and height was median-centered and smoothed. This plot does **not** estimate actual 3D geographic/behavioral overlap, true instantaneous contact, common prey or equivalent absence of competition.
- The anonymous and internal SI PDF pipeline embeds the same vector Figure S1; its final printed appearance still needs human coauthor sign-off.

## Source-cohort imbalance and count-independent QA — 2026-10-14

- Added a **post-outcome descriptive sensitivity** of the already-opened 684 *dependent* dyad overlap coefficients, restricted to 12 exact original source collection cohorts. The original five panel profile counts are 20/24/33/16/10 **individual-by-panel records**, with 101 distinct literal source identifier strings due to two repeated 2016/2022 labels.
- Dominant source cohorts contribute 28/41 pairs (**68.3%**) in *Eidolon*, 171/262 (65.3%) in *P. hastatus* 2022, and 45/60 (**75.0%**) in 2023. Original pooled pair medians (0.817/0.919/0.899) differ from equally weighted medians of cohort medians (0.855/0.917/0.865). The *Eidolon* equal-cohort value includes **three cohorts with exactly one dyad each**; it is not an unbiased estimator or formal confidence adjustment.
- After leaving out the largest cohort, remaining descriptive dyad medians are 0.887 (13 remaining pairs), 0.912 (91) and 0.831 (15), respectively. This is not a leave-one-independent-unit-out test. The one-cohort *Hypsignathus* and 2016 *Phyllostomus* panels have no meaningful leave-largest-cohort value.
- Independent original byte-verified CSV Python computation (`validate_cohort_weight_sensitivity_v1.py`) checks all 12 cohort medians and panel aggregation against `figures/COHORT_WEIGHT_SENSITIVITY_V1.json`; the original descriptive JSON, original 103 profile source and main JAE/BE test results are unchanged. This note and Table S9 are **not a new inferential ecological result**.

## Direct same-source 2D prior art and animal-ID integrity amendment — 2026-10-14

- Targeted literature validation found Calderón-Capote et al. (2025; *PLOS ONE*, DOI 10.1371/journal.pone.0313782), which analysed the very same La Gruta P. hastatus 2016 and 2022 source archives for **horizontal foraging-area overlap**, averaging near 0.20 with a Bhattacharyya coefficient. This is not mathematically comparable to the new 1D centered height-shape overlap median 0.80–0.92; no “80–92% shared 3D habitat” statement is admissible.
- Independent **byte-verified source CSV identity-scope QA**: 103 panel-indexed profile rows across five source panels, **101 distinct literal animal-ID strings**, two repeated strings in the 2016 and 2022 P. hastatus La Gruta cohorts. The 684 descriptive profile pairs are entirely within each panel and exact collection cohort; none cross these two years.
- The 2025 paper states PIT tagging and low recaptures over 2016–2022, but the exact PIT registry crosswalk for the two identical archived strings was not independently confirmed. Hence manuscript, anonymous manuscript and new figure labels now use **103 panel-profile records**, not “103 confirmed independent bats”, and the cover letter no longer asserts all programmes are biologically independent.
- The original JAE per-panel calibration, positive/nonsupporting original verdicts, 500-m conditional stress tests, full source profile data and original graphic remain unchanged; no added cross-year individual memory test has been performed.

## Original native 3D source closure and visual QA — 2026-10-15

- Original native 500-m JAE result recovered exactly from successful workflow 36881187913, historic summary blob c1d37e42f72f59e5aba364daec9aef68b47778b6.
- Native within-study source biological n = 8/5/6/9 in four structurally eligible panels. Original source native S = +0.10295/−0.01660/−0.00392/+0.13040; DEM-adjusted original S_rel = −0.01581/−0.00896/+0.01626/+0.02890. Terrain V_rel 4/4 supported; positive S_rel 0/4 supported.
- Original native XY-versus-XYZ overlap measures actual gridded joint distributions for source-eligible session pairs; do not confuse with S1's 1D centered-profile self-predictor shape similarity in different animals and cell supports. Pair-based R_3D is computed before biological averaging; ratio of group means would be incorrect.
- Original JAE rc2 is missing historical direct Python imports and native contract/summary. Source-dependent runner/config files were archived byte-identically from the original successful commits in the integration-only source-recovery folder, but this is NOT a full GPS/DEM rerun.
- Figure S2 now exists with original-source deterministic vector renderer; Table U10/S10 and Methods U15/S15 are in both SI copies. Automated original-blob/provenance/figure tests passed, and the crowded S2 header was corrected after visual inspection.
## Rendered figure amendment (2026-10-14)

- Six draft SVG figures, the frozen source-summary data snapshot, a zero-dependency Node figure builder, a Python SVG/XML-and-biological-claim guard, and an on-PR workflow were added to the same draft PR.
- A source-specific encounter distinction was corrected in text/legends: the 2016 co-use panel also used a 600-s window, but endpoint exclusion; only 2023 used 600-s **all-space** scope, while H and 2022 used 60-s endpoint-excluded scope.
- Figure 5A shows calibrated original-result centered-shape scores and Figure 5B now links the exact original JAE heatmap, with 103 individual-by-panel profiles preserved as original CSV, JSON and PNG. SHA256 for all three original artifact members and the 103 × 10 probability structure were verified in restore workflow 38507348011; graphical details remain descriptive, not independent inferential tests.
- The figure validator cannot substitute for visual QA, and the underlying source calculations have not been independently recomputed in this integrated PR.

## Horizontal spatial baseline versus added vertical separation — 2026-10-15

The integrated title/lay/abstract, ecological Results/Discussion/Conclusion, cover letter and both SI versions have been aligned to the source-supported **narrower** claim: no consistently supported additional **terrain-relative vertical** segregation in four eligible panels from two species. This does not assert lack of horizontal spatial differentiation, diet sorting or all-scale partitioning. In the original native source the 500-m O_XY same-animal values 0.619/0.549/0.547/0.511 exceed the corresponding other-animal 0.322/0.334/0.202/0.208 descriptively. The mathematical inequality O_XYZ <= O_XY applies to the same pairwise grid, so native geometry loss alone is non-diagnostic for extra between-animal segregation. See `HORIZONTAL_VS_ADDED_VERTICAL_SEGREGATION_CLAIM_AUDIT_V1.md`. This is editorial/scoping work and a deterministic probability fact, **not a new biological analysis**. No existing source test, p-value or figure datum was changed.

## Retrospective within-endpoint four-panel Holm sensitivity — 2026-10-15

All four source-frozen V_rel p-values, two-sided terrain-relative S_rel p-values and separate upper-tail co-use I phase-shift p-values were copied to the pinned machine record without modifying any GPS/DEM inputs or original source results. The independent validator uses original Git blob hashes and reconstructs the Holm adjusted values rather than trusting the stored outputs. Within each **separate** four-panel family, adjusted support counts at p <= 0.05 are V 4/4, two-sided S 0/4, I 0/4; original per-panel nominal counts are V 4/4, S two-sided 1/4 **negative direction**, I 1/4 positive. Nominal *H. monstrosus* S p=0.0362 becomes 0.1448; nominal *P. hastatus* 2023 I p=0.0231 becomes 0.0924. The paper's Figure 6 remains frozen at original nominal symbols/results, while legend, main text, both SI versions and cover letter clearly distinguish source verdicts and sensitivity. This is **not** an across-family multiplicity control, prospective preregistration, proof of zero interaction, or generalization to four independent species. See `FOUR_PANEL_MULTIPLICITY_SENSITIVITY_V1.md` and `validate_four_panel_multiplicity_v1.py`.


## Expanded displayed-suite twelve-test Holm audit — 2026-10-15

The last paragraph's within-endpoint Holm checks were **not the only sensitivity**. We additionally computed the identical procedure after combining the twelve frozen V_rel/S_rel/I p-values into one post-outcome display suite. Its source-hash-verified machine ledger is `figures/FROZEN_TWELVE_TEST_MULTIPLICITY_V1.json`; the extended `validate_four_panel_multiplicity_v1.py` independently recomputes both families. The illustrative 12-test counts at adjusted p <= .05 are V_rel **3/4**, S_rel **0/4**, co-use I **0/4**; the original raw field outcomes are **V 4/4 source-positive**, S_rel **0/4 positive-supported**, I **1/4 nominal source-positive**. H/P2022/P2023 V_rel all have p_Holm12 = .0012, but P2016 V_rel rises from raw .0345276 to p_Holm12 = .276221. Nominal H negative S_rel and P2023 positive co-use have p_Holm12 = .276221 and .2079, respectively. The expansion is **not** a prospective, exhaustive paper-wide family; p-value-count asymmetry is not an equivalence or effect-magnitude contrast. Title, Abstract, main Results, Discussion/Conclusion, Figure 6 legend, SI Table S12, cover letter, reviewer gate and audit report acknowledge dependence on the family definition. Original frozen JAE/BE code and biological values were not altered.
