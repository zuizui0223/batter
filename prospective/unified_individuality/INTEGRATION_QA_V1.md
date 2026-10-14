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
- **Manuscript provisional length:** approximately 7400 whitespace-delimited words including 36 scholarly reference entries and figure legends. The manuscript is a working Markdown document and this is not the target journal's official word count; the initial section counts are superseded by the subsequent bibliography and figure amendments. This is a drafting metric rather than the journal's official word counter.

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
2. Textual bibliography merge complete (45 original-source DOIs plus a newly verified Carlson 2021 prior (36 scholarly references in main)). **Publisher-level DOI resolution, author names/year suffixes, in-text citation coverage and final journal style remain unverified**.
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

## Rendered figure amendment (2026-10-14)

- Six draft SVG figures, the frozen source-summary data snapshot, a zero-dependency Node figure builder, a Python SVG/XML-and-biological-claim guard, and an on-PR workflow were added to the same draft PR.
- A source-specific encounter distinction was corrected in text/legends: the 2016 co-use panel also used a 600-s window, but endpoint exclusion; only 2023 used 600-s **all-space** scope, while H and 2022 used 60-s endpoint-excluded scope.
- Figure 5A shows calibrated original-result centered-shape scores and Figure 5B now links the exact original JAE heatmap, with 103 individual profiles preserved as original CSV, JSON and PNG. SHA256 for all three original artifact members and the 103 × 10 probability structure were verified in restore workflow 38507348011; graphical details remain descriptive, not independent inferential tests.
- The figure validator cannot substitute for visual QA, and the underlying source calculations have not been independently recomputed in this integrated PR.
