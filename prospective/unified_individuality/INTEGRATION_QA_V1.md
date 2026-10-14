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
- **Manuscript provisional length:** 6122 whitespace-delimited words including selected references and metadata (count updated after six figure legends). Introduction ~566; Methods ~1,083; Results ~1,388; Discussion ~1,310. This is a drafting metric rather than the journal's official word counter.

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
2. Full manuscript references and source DOIs merged, checked for year suffixes and required citation coverage.
3. Original numerical pipelines independently re-executed if coauthors or the target journal require it. This integration did not rerun them.
4. Figures 1–6 now generated as source-backed SVGs and regenerated in the figure workflow. Human-readable journal-size, grayscale and full source-profile artifact visual QA are not yet complete.
5. SI assembly, anonymized reviewer archive, original-data redistribution licence review, final journal rule verification, manuscript PDF/figure QA and DOI creation.
6. Authorship, institutional approvals, funding, CRediT, conflict and AI-methods disclosures approved by the human authors.

**Assessment:** The integrated draft is a coherent evidence-bounded scientific candidate. This QA supports text-level numerical alignment and boundary discipline only; it does not declare the new manuscript submission-ready.

## Rendered figure amendment (2026-10-14)

- Six draft SVG figures, the frozen source-summary data snapshot, a zero-dependency Node figure builder, a Python SVG/XML-and-biological-claim guard, and an on-PR workflow were added to the same draft PR.
- A source-specific encounter distinction was corrected in text/legends: the 2016 co-use panel also used a 600-s window, but endpoint exclusion; only 2023 used 600-s **all-space** scope, while H and 2022 used 60-s endpoint-excluded scope.
- Figure 5A shows calibrated original-result centered-shape scores and Figure 5B now links the exact original JAE heatmap, with 103 individual profiles preserved as original CSV, JSON and PNG. SHA256 for all three original artifact members and the 103 × 10 probability structure were verified in restore workflow 38507348011; graphical details remain descriptive, not independent inferential tests.
- The figure validator cannot substitute for visual QA, and the underlying source calculations have not been independently recomputed in this integrated PR.
