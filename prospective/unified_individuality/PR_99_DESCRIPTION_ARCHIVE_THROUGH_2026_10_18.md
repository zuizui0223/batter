# Original PR #99 cumulative draft description through 18 October 2026

This is a verbatim-preserved editorial progress description before its replacement with a concise review-oriented PR body. It contains previously stated source-based claims and provenance notes, including superseded limits resolved by later audits. The **current** manuscript, evidence/rights ledgers and concise active PR body are authoritative; this archive is historical, not a fresh source claim.

---

## 2026-10-18: four original bat Movebank data packages verified CC0; ecological task alternatives

- **New verified original published dataset rights:** official Movebank Data Repository **Full item** metadata for all four source bat DOIs (H [1.278](https://doi.org/10.5441/001/1.278), P2022 [1.321](https://doi.org/10.5441/001/1.321), P2023 [1.322](https://doi.org/10.5441/001/1.322), P2016 [1.282](https://doi.org/10.5441/001/1.282)) each explicitly records `dc.rights=CC0 1.0 Universal`, with `dc.rights.uri` pointing to CC0. [Source-specific full-metadata/rights ledger](prospective/unified_individuality/figures/VERIFIED_MOVEBANK_ORIGINAL_DOI_RIGHTS_V1.json), [offline CI guard](prospective/unified_individuality/validate_original_doi_rights_v1.py), and [updated preservation plan](prospective/unified_individuality/SOURCE_ARTIFACT_RETENTION_AND_RIGHTS_GATE_V1.md) added. **Derived original bat-ID/dyad ZIP redistribution, author/overlap approval and restricted long-term storage remain separate unresolved decisions**, despite the input published source CC0 terms.
- **Biological hypotheses sharpened using the original study descriptions:** `H. monstrosus` mating-lek versus foraging allocation; `P. hastatus` colony-associated long-distance use of flowering-balsa versus seasonal other resources, and 2016 commuting/foraging/resting distinctions. Main Discussion and both SI Methods S12 variants now contrast **different task allocation** versus **persistent within-task vertical policy**, with prospective task/resource-verified falsifiers. These are existing source-publication ecology and *untested* mechanisms, not newly classified GPS tasks.
- [Current source-verified head `86b07ee5`](https://github.com/zuizui0223/batter/commit/86b07ee5b53b89498c6a0e65d3aba3fd05a0033b) has **4/4 Actions checks successful**, including anonymous main/SI PDFs, source-only provenance and the updated DOIs/rights validator. No source-permutation tests, original GPS/DEM, original frozen JAE/BE results, or source animal ID values changed. PR stays **DRAFT, not journal-submitted**.

---

## 2026-10-17: original shared-geometry co-use dyad support and artifact retention deadline

**New noninferential field-support calculation from the same 16 checksum-verified original successful source artifact ZIPs:** We matched each corrected original co-use dyad's two original cohort-qualified bat IDs to the original 500-m joint-geometry V/S eligible individual sets, **without opening raw GPS/DEM or recomputing statistical nulls**.

- Both co-use bats were V/S-eligible in **9/22, 3/10, 5/8 and 8/8** original source dyads (H/P2022/P2023/P2016). Across the four distinct observational designs this gives **25/48 dyads**; 20 dyads had exactly one V/S bat and three neither.
- Original repeated matched events represented in these both-geometry dyads were **592/883, 284/347, 650/679 and 16,096/16,096** by panel, total **17,622 of 18,005**. **Events and reused dyads are NOT independent bat samples**; the 2016 600-second endpoint-excluded source contributes 16,096 events alone and cannot be pooled as equal exposure with the other three designs.
- **No subgroup co-use phase-shift null, individual-level V–I correlation, behavioural or physical-altitude-gap effect has been estimated**. Original source-full-panel p-values and compatibility bounds cannot be applied to these selected 25 dyads. This is a support/feasibility audit, not a positive ecological mechanism result.
- **New artifacts:** [source-hash-referenced aggregate dyad/event table](prospective/unified_individuality/figures/FROZEN_SHARED_GEOMETRY_COUSE_DYAD_SUPPORT_V1.json), [scientific interpretation and hard inferential boundary](prospective/unified_individuality/COUSE_DYAD_GEOMETRY_MEMBERSHIP_AUDIT_V1.md), expanded [cross-estimand validator](prospective/unified_individuality/validate_cross_estimand_eligibility_v1.py), updated main text, both SI Table S15 versions, Figure 6 caption, README and coauthor/reviewer gates. No bat IDs/dyad-identifying records were re-published.
- **Retention hard stop and stewardship plan:** the original fine500 output ZIPs' earliest currently reported expiry is **28 December 2026**, followed by native, terrain and co-use ZIPs around 30–31 December. [Rights-first preservation protocol](prospective/unified_individuality/SOURCE_ARTIFACT_RETENTION_AND_RIGHTS_GATE_V1.md) records per-DOI Movebank license and original-output reuse checks, owner/coauthor credit/access review, approved access-controlled escrow, SHA checks and privacy-safe aggregate DOI release. GitHub's retention-setting changes are not retroactive; no public mirror, rights clearance or permanent archive has been claimed.
- Final exact head [`4c06205d`](https://github.com/zuizui0223/batter/commit/4c06205ddffba89f729bf5edb80ad55ee70e6df9) has all **four PR CI checks SUCCESS** including source-summary/dyad support, internal/anonymous PDF proof and historical source-only replay checks.

**PR remains DRAFT, unsubmitted; original BE/JAE source branches, inferential outputs and GPS/DEM inputs remain unchanged.**

---

## 2026-10-16: original source cohort-qualified ID intersection recovered

**The earlier aggregate-only "exact source bat-ID overlap unverified" limitation has now been materially resolved.** We retrieved **16 original successful GitHub Actions result artifact ZIPs** (four named wild panels × original fine500/native3D/terrain3D/corrected co-use analyses); all **16/16 SHA256 ZIP digests matched the published original Actions artifact hashes**. Only already derived original per-bat results and dyad cohort/source-ID fields were examined, not raw GPS/DEM.

- On exact *(original collection cohort, source animal ID)* matching, the V/S geometry-eligible bat sets were **identical between native and terrain workflows**, and **each entire V/S set was a subset of the 500-m place×speed×turn eligible set** in all four panels.
- **Verified intersection V/S ∩ co-use I = 5 / 3 / 5 / 5 cohort-qualified bat records** in source-panel order H/P2022/P2023/P2016. Fine500∩I = 10/6/6/5. This is **18 panel-indexed overlaps**, **not** 18 confirmed distinct bats over years. The full V/S and I cohorts are not identical in any panel: *P. hastatus* 2023 uses n=6 on each side but shares **only five** source IDs.
- **This is an eligibility/provenance breakthrough, NOT an individual-level ecological effect.** No paired V-rel versus I relationship, dyad-dependent individual effect, physical 3D gap or causal response was estimated. Original source p-values and inferential gates are unchanged.
- Source outcome figures and review text: [aggregate counts, artifact IDs and SHA metadata only](prospective/unified_individuality/figures/FROZEN_CROSS_ESTIMAND_ELIGIBILITY_V1.json), [original-source interpretive audit](prospective/unified_individuality/CROSS_ESTIMAND_ELIGIBILITY_SCOPE_AUDIT_V1.md), [offline checksum/ID crosswalk verifier](prospective/unified_individuality/validate_cross_estimand_eligibility_v1.py). Figure 6 labels V/S n, I n **and the verified shared bat-ID count in each row**; main text, anonymous manuscript, SI **Table S15**, journal abstract (247 words), cover letter and scientific/editorial gates use the corrected scope. No animal IDs/ZIPs were republished.
- **Review reproducibility boundary:** Original ID-bearing Actions artifacts have **December 2026 expiration dates**. The public integration deliberately preserves only aggregate counts and digest provenance, not the original per-bat records; reconstructing IDs after source-artifact expiry would require properly licensed archival access or authorized re-analysis. **Human coauthor/rights approval, independent source GPS/DEM replay and DOI archive remain hard stops.**
- Final head [`d4e09360`](https://github.com/zuizui0223/batter/commit/d4e0936044657ab333a82df6892ce9cb8ba388d5) has all four PR CI workflows **successful**.

**PR remains DRAFT; not journal-submitted.**

---

## 2026-10-16: three distinct wild eligibility frames prohibit matched-bat V–I claims

**Source-original biological n cross-check across the same four named bat study-year panels (H/P2022/P2023/P2016):**

| Independent source-analysis family | H | P2022 | P2023 | P2016 |
|---|---:|---:|---:|---:|
| 500-m place × speed × turning identity | **19** | **23** | **11** | **9** |
| 500-m smoothed native/terrain joint geometry V/S | **8** | **5** | **6** | **9** |
| Fixed x-y-time matched co-use residual-deviation I | **11** | **6** | **6** | **5** |

- Geometry V/S and I n differ in **3/4** panels; fine matching and geometry in **3/4**; fine matching and I in **4/4**. A matching count in a single source year is **not verified matching animal IDs**. No cross-assay per-animal identity intersection was recovered from the source result summaries, and no V–I within-bat association/correlation was calculated.
- As a result the **same named study-panel** results may be juxtaposed but **must not be described as tracking the same individually predictable bats through an absence/presence of encounter avoidance**. These are distinct biological eligibility frames, nulls and outcomes. Original source positivity, native/terrain estimators and source p-values remain unchanged.
- **Completed corrections:** Figure 6 now explicitly labels *V/S n* and *I n* on each study row, while the main manuscript Methods/Results/Discussion/conclusion, Figure 6 caption/alt text, cover letter and both SI versions (new **Supplementary Table S15**) disclose this sample-frame boundary. [Exact original-output source/n ledger](prospective/unified_individuality/figures/FROZEN_CROSS_ESTIMAND_ELIGIBILITY_V1.json), [independent source-blob and eligibility validator](prospective/unified_individuality/validate_cross_estimand_eligibility_v1.py), [reviewer-oriented scientific audit](prospective/unified_individuality/CROSS_ESTIMAND_ELIGIBILITY_SCOPE_AUDIT_V1.md). Original fine-place result, native geometry summary and corrected original co-use result were all verified against original Git source blobs and source-only copies; no GPS/DEM or individual ID tracks were opened.
- **Scope of thesis:** persistent individually identifiable centered height-use probabilities are the substantive original field finding; nested joint geometry V and S are algebraically coupled, and the co-use residual-height test is on an **unverified different eligible animal set**, not measured physical co-presence avoidance. Prior unrelated experiments remain separate behavioural analogues, not established causal ancestors of the field phenotype.
- **Journal status:** work remains **DRAFT**, not submitted. Original raw GPS/DEM independent numerical replay, data rights and human author/coauthor/overlap/DOI sign-off remain hard stops.

---

## 2026-10-16: source-exact V–S algebra, median-valid counterexample and unified editorial thesis

**Scientific revision grounded in the exact archived original native 500-m overlap summaries and source weighting code (no new animal GPS/DEM analysis):**

- **Main new constraint:** conditional relative-height individuality `V` and normalized added 3D segregation `S` are **non-equivalent but mathematically coupled**. Pair-level `epsilon = O_XYZ/O_XY − O_Z|XY ≥ 0` and original matched source pair/session/animal weighting yield **`S_native = V_native − (mean epsilon_other − mean epsilon_self)`**. Exact original native epsilon-other-minus-self gaps are **+0.06775, +0.08255, +0.05809, +0.01483** for H/P2022/P2023/P2016, respectively; the identity holds to source floating-point precision. These are algebraic terms, **not causal horizontal allocation effects or independent significance tests**. Terrain V_rel/S_rel remain different processed quantities without separately preserved terrain epsilon-self/other summaries.
- **True original-preprocessing-conformant artificial counterexample:** under **ten centered height bins, α=0.5, 100 fixes per session, ≥50 fixes in shared XY cells and a genuine zero session median**, two invented bat profiles have conditional **V≈0.498** while joint normalized extra segregation **S≈0**. No real bat data and no cohort n≥5; this demonstrates original estimand coupling rather than absence of ecological competition.
- **Title/lay recalibration:** *Persistent behavioral individuality and the limits of 3D niche inference in bats* (**80 characters**). The **65-word lay summary** now clearly distinguishes reproducible individual height-use information from **unmeasured physical shared airspace**, instead of suggesting the biological absence of separation. Abstract remains **244 words**; same text is synchronized to anonymous review manuscript, source-anonymized SI builder and cover letter.
- **New exact-source deliverables:** [algebraic/reviewer audit](prospective/unified_individuality/V_S_ALGEBRAIC_COUPLING_AND_INDEPENDENCE_AUDIT_V1.md), [locked machine-readable source and epsilon rows](prospective/unified_individuality/figures/NATIVE_3D_V_S_OVERLAP_SLACK_DECOMPOSITION_V1.json), [independent Git-blob/median-consistent synthetic test](prospective/unified_individuality/validate_original_v_s_overlap_coupling_v1.py), [single-paper inferential thesis and editorial go/no-go criteria](prospective/unified_individuality/ONE_PAPER_SCIENTIFIC_ARGUMENT_AND_EDITORIAL_GATE_V1.md). The main manuscript, **SI Table S14 and Methods S15**, Figure 6/footer+alt text, reviewer/citation/QA ledgers and target-journal editorial gates now prohibit describing `V` and `S` as independent field confirmations.
- **Validated final head `b791e3c2`: four GitHub CI workflows completed successfully**: [source-figure/numerical validators](https://github.com/zuizui0223/batter/actions/runs/38824735994), [anonymous complete text PDF](https://github.com/zuizui0223/batter/actions/runs/38824736013), [anonymous and internal SI proof](https://github.com/zuizui0223/batter/actions/runs/38824735997), [historical source-provenance closure](https://github.com/zuizui0223/batter/actions/runs/38824736083).

**Limits unchanged:** original source-specific V_rel test 4/4 nominal, 3/4 under retrospective expanded 12-test Holm; positive S_rel 0/4; co-use centered-deviation I only 1/4 nominal, not Holm-robust and *not physical altitude-gap avoidance*. Physical 3D airspace overlap/competition, a shared lab-to-field causal carrier, independent raw GPS/DEM replay and author/rights/overlap/DOI approvals remain unresolved. PR is **DRAFT, not submitted**, and source-frozen JAE and BE branches/results were not mutated.

---

## 2026-10-16: corrected physical meaning of 3D overlap and co-use I

**Source audit found two substantive measurement-interpretation ceilings, now repaired on the unified DRAFT branch without reopening any animal data or source tests:**

- **Source 500-m O_XYZ is smoothed and centered**, not actual observed shared three-dimensional airspace. The historical native and terrain workflows use 10 session-centered height bins with **0.5 pseudocount per height bin in each occupied XY cell**; their pair eligibility requires ≥50 fixes per session **summed across pairwise-shared cells**, not within each cell. Exact synthetic-only examples with **zero raw observed matching XY×height bins** give estimated O_XYZ **5/6** when the same 50 fixes occupy 50 shared cells, versus **1/11** when concentrated in one shared cell. These are *not* bat results and do not quantify empirical smoothing bias.
- **Source co-use I is not measured physical altitude gap.** The corrected original co-use source (workflow 36953712597, code Git blob `1f528f0343ac9e6e26851e4adad5c106e8e5dffc`, same in frozen JAE rc2) explicitly constructs `z_rel=(GPS_height−DEM)−median_of_own_session(GPS_height−DEM)`, then source encounter endpoint `abs(z_rel_A−z_rel_B)`. Thus the P2023 **+3.57 m** is **excess *session-centered relative-height-deviation dissimilarity*** over a fixed encounter/within-cell phase-shift null (source raw upper-tail p=0.0231, Holm-four p=0.0924, Holm-twelve p=0.2079); it does **not** mean two bats physically flew 3.57 m further apart, nor identify avoidance. The ~1–2-m positive nonsupporting compatibility endpoints are also on the **centered-deviation** scale, not physical height-equivalence limits.
- This narrows the integrated ecological conclusion to **individual predictive information in smoothed, session-centered vertical-use probability structure** without consistently source-supported added *centered relative-height distribution segregation*. Physical 3D space sharing, physical avoidance and the proximate cognitive/food/task carrier are *not* established. Original wild centered-shape results, V_rel 4/4 original panels (3/4 under exploratory Holm-twelve), S_rel positive 0/4 and the one **nominal** co-use panel remain original unchanged evidence.
- **New documents/code:** [reviewer-facing estimand matrix](prospective/unified_individuality/REVIEWER_EMPIRICAL_VS_PHYSICAL_GEOMETRY_V1.md), [smoothing and aggregate cell-support source audit](prospective/unified_individuality/SMOOTHED_3D_OVERLAP_SUPPORT_AUDIT_V1.md), [corrected co-use residual/physical-gap audit](prospective/unified_individuality/COUSE_CENTERING_PHYSICAL_GAP_SCOPE_AUDIT_V1.md), plus exact-Git-blob-guarded synthetic-only validators and byte-identical original co-use source snapshot. Main manuscript/anonymous text, Abstract, both SI copies, Figure 1/6/S2 SVG **and source renderers**, alt text, editor letter, evidence/QA ledgers and submission hard stops have been corrected. No source p-value, original numerical result, GPS/DEM observation, original frozen JAE/BE branch or laboratory→field bridge result was changed.
- Current final manuscript includes a **prospective decisive experiment** that explicitly contrasts genuine same-datum measured altitude gaps with baseline-centered residual-height differences under observed task labels, source-calibrated instrumentation and predeclared bin smoothing/per-cell support. **These are prospective study requirements, not results of the archived analysis.**

**Unclosed hard stops:** independent raw-GPS/DEM numerical replication, legal data/code redistribution checks, actual coauthor/author approval, single-publication overlap decision, verified source vertical-datum alignment, anonymous DOI archive and journal production review. This remains a draft PR and **has not been submitted**.

---

## 2026-10-15: terrain-reference-sensitive 3D geometry and GPS vertical datum audit

**New ecological interpretation from pre-existing, source-frozen geometry (no new GPS/DEM data analysis):** original **native-height** and **DEM-subtracted terrain-relative** 500-m joint probability geometry were compared within each of the four originally structurally eligible two-species panels, with unchanged original horizontal overlap contrast H and original data supports.

- **Main quantitative comparison:** *H. monstrosus* descriptive added-segregation `S_native +0.1029 → S_rel −0.0158`; *P. hastatus* 2016 `+0.1304 → +0.0289`. Across four panels, the native→relative change in **S** is negative in two and positive in two; likewise for the individual-fidelity **V** statistic. This is **not** a universal effect of topography or a separately tested contrast. Original terrain-relative individual fidelity remains source-supported in 4/4 (only 3/4 in the **retrospective 12-test Holm** sensitivity); positive terrain-relative S remains source-unsupported 0/4.
- **Source-method accuracy correction:** the historical runner [`run_original_terrain_geometry_v1.py`](https://github.com/zuizui0223/batter/blob/819acc829d615485b57033f1ddcbebf64b4b49a0/post_freeze_extensions/3d_niche_partition/run_original_terrain_geometry_v1.py) bilinearly interpolates DEM terrain elevation **for each original GPS fix** and only **then** assembles 500-m horizontal-cell joint 3D probability distributions; 500 m is **not** the declared source DEM pixel size. Source GPS vertical fields are **ellipsoid** for H/P2023 and **MSL** for P2022/P2016. The DEM-subtracted height is a **terrain-relative proxy**, not an independently harmonized physical AGL or canopy-clearance measurement.
- **New pinned evidence:** [ecological/datum scientific audit](prospective/unified_individuality/TERRAIN_DATUM_AND_GEOMETRY_SENSITIVITY_V1.md), [all exact source-matched four-panel processing contrasts](prospective/unified_individuality/figures/FROZEN_TERRAIN_DATUM_CONTRAST_V1.json), [independent Git-blob/datum/Methods/SI validator](prospective/unified_individuality/validate_terrain_datum_contrast_v1.py). This guard is in the figure CI. Main text, anonymous proof, **Supplementary Table S13** and Methods S7, cover letter, submission gates and evidence crosswalk are synchronized; anonymous SI grammar/table-link repairs are also guarded.
- Main Abstract now **245 words** and explicitly distinguishes the terrain reference from the evidence for extra segregation. Original JAE/BE frozen branches, tracked animal observations, original p-values/9,999-label nulls and source numerics are unchanged. **Do not claim** a causal topographic mechanism, physical AGL, absent competition, source-independent replication or preregistered multisystem confirmation.

**Remaining hard stops:** legal source access/redistribution, raw-GPS/DEM + original-environment independent numerical replay, coauthor approval, original study identity/attribution, publication-overlap sign-off, anonymous versioned DOI and final PDF human review. PR remains a draft, not journal submitted.

---

## 2026-10-15: expanded twelve-test Holm sensitivity limits the 4/4 robustness claim

The existing original **terrain-relative fidelity V_rel 4/4 nominally supported** finding and the earlier **4/4 within-endpoint four-test Holm** arithmetic remain unchanged; however, a reviewer-relevant *different retrospective family choice* changes the robustness wording:

- Treating all **twelve displayed field endpoint p-values together** (4 V_rel one-sided + 4 S_rel two-sided + 4 co-use I one-sided) leaves **V_rel significant in 3/4**, not 4/4: H, P2022 and P2023 have adjusted p **0.0012**; P2016 V_rel raw **0.0345276** becomes adjusted **0.276221**. Neither S_rel nor co-use has any adjusted p below 0.05. The nominal P2023 co-use p 0.0231 becomes **0.2079** in the illustrative 12-test suite.
- **Neither correction family was preregistered, and 12 tests are not all the tests conducted in this research programme**; these are post-outcome *sensitivity demonstrations only*. Do not infer that the true V_rel effect exceeds S_rel or that vertical segregation is absent. The four original V_rel source verdicts and nominal co-use exception are preserved.
- New reproducible [twelve-test narrative audit](prospective/unified_individuality/TWELVE_TEST_MULTIPLICITY_SENSITIVITY_V1.md) and [machine-readable original-p/4-test/12-test table](prospective/unified_individuality/figures/FROZEN_TWELVE_TEST_MULTIPLICITY_V1.json), independently verified from the unchanged source hashes by [the extended Holm checker](prospective/unified_individuality/validate_four_panel_multiplicity_v1.py). Integrated Abstract (244 words), Results/Methods/Conclusion, Figure 6 caption, both SI copies (new Table S12), cover letter, reader README and review gates now explicitly describe this family dependence.
- [Latest exact head `a1297e9a`](https://github.com/zuizui0223/batter/commit/a1297e9af0c3a3abb34d4a20ddebb26bcdb2ce94) has **all four source-provenance, figure/arithmetical, anonymous-main-PDF and SI-PDF workflows PASS**: [figures/checks](https://github.com/zuizui0223/batter/actions/runs/38753874671), [source-only history](https://github.com/zuizui0223/batter/actions/runs/38753874805), [anonymous main](https://github.com/zuizui0223/batter/actions/runs/38753874578), [SI](https://github.com/zuizui0223/batter/actions/runs/38753874642).

**No source analyses, code outcomes, GPS/DEM bitstreams, frozen JAE/BE manuscript branches, or figure numeric data were altered.** PR remains a **draft**, not a journal submission. Coauthor ethics/authorship and overlapping-publication decisions, source permissions, independent original-data numerical replay and a versioned anonymous DOI archive still block submission.

---

## 2026-10-15: post-outcome four-panel multiplicity audit

A new **source-hash-guarded, deterministic Holm sensitivity** reuses *only original frozen panel p-values* and performs no new GPS/DEM sampling, null permutation or subgroup fit. The procedure is **retrospective** and **separate for each four-panel V_rel, two-sided S_rel, and upper-tail co-use I endpoint family**; it is neither across-family multiplicity control nor preregistration.

- **V_rel remains nominally supported 4/4 and within-family Holm-significant 4/4** (maximum adjusted p **0.03453**; 4 panels from 2 species).
- The *Hypsignathus* **negative-direction** S_rel original raw p **0.0362** becomes Holm **0.1448**; no positive S_rel panel was supported under its original null.
- The *P. hastatus* 2023 co-use positive raw p **0.0231** becomes Holm **0.0924**; the original **1/4 nominal** source co-use result remains true but does not survive four-panel adjustment.
- **New artifacts:** [narrative scientific audit](prospective/unified_individuality/FOUR_PANEL_MULTIPLICITY_SENSITIVITY_V1.md), [exact machine table](prospective/unified_individuality/figures/FROZEN_FOUR_PANEL_MULTIPLICITY_V1.json), [independent original-Git-blob and Holm verifier](prospective/unified_individuality/validate_four_panel_multiplicity_v1.py).
- Manuscript Abstract/Methods/Results/Figure 6 caption, paired anonymous text, both SI drafts (new Table S11 and Methods S16), cover letter, evidence crosswalk and review gates now distinguish **original per-panel source verdicts** from this post-outcome sensitivity. Source results, original six SVGs and frozen JAE/BE branches are unchanged. No absence of spatial/resource partitioning or universal bat mechanism is asserted.
- Verified current head [`2b47af66`](https://github.com/zuizui0223/batter/commit/2b47af666e02d92863d298a6d3908f018b25a13c) with all four on-PR workflows **successful**: [figure/source and arithmetic checks](https://github.com/zuizui0223/batter/actions/runs/38703526507), [anonymous main PDF](https://github.com/zuizui0223/batter/actions/runs/38703526812), [SI PDF](https://github.com/zuizui0223/batter/actions/runs/38703526345), [historical two-stage source closure](https://github.com/zuizui0223/batter/actions/runs/38703526250).

**Remaining hard stops unchanged:** independent raw GPS/DEM + environment replay, source permissions, coauthor approval, rights/AI author disclosures, DOI-linked anonymous archive, and actual publication-overlap signoff. PR stays **draft**; not submitted.

---

## 2026-10-15: two-stage original S_rel provenance and exact authorized-input bill of materials

- **Three measurable geometry layers now explicit in the manuscript:** `p_i(h,z|c)=p_i(h|c)p_i(z|h,c)` distinguishes horizontal site allocation, conditional height use within a supported cell and joint XY–height overlap. The original conditional self-prediction and added terrain-relative S_rel remain different estimands, not estimates of a universal personal flight-rule cause. Nominal negative S_rel p=0.0362 is clearly labeled post-outcome and uncorrected across panels.
- **Exact original raw-input inventory, no raw bytes hosted:** [4 GPS + 4 reference records and 2 unique DEM gzips](prospective/unified_individuality/source_recovery/terrain_replay_input_manifest_v1.json); historical input sizes total 69,505,395 + 43,818 + 19,365,315 bytes, original preflight records 240,042 coordinate rows and 521 sessions. The [stdlib-only offline verifier](prospective/unified_individuality/source_recovery/verify_terrain_replay_input_manifest_v1.py) checks source manifests by default; optionally checks all 21 original historical source Git blobs or operator-supplied authorized GPS/DEM bitstreams by original MD5/SHA256. **No original data bytes were downloaded for this inventory.**
- **Critical source-stage distinction:** [original terrain geometry success](https://github.com/zuizui0223/batter/actions/runs/36946126004) from `819acc829...` calibrates V_rel in its 9,999 requested permutations but only produces a descriptive S_rel point value. The subsequent original [S_rel calibration success](https://github.com/zuizui0223/batter/actions/runs/36992380946) from `d0193c1...` recalculates per-label S_rel nulls and their two-sided p-values. The source Stage B runner/contract blobs (9aba94c6 / 1dfc8625) and unchanged helper blob identities are in a [separate manifest](prospective/unified_individuality/source_recovery/partitioning_s_calibration_provenance_v1.json) with an optional **public source-code-only** [Git SHA audit](prospective/unified_individuality/source_recovery/verify_partitioning_s_provenance_v1.py). Original summary blob e969698e is unchanged. This avoids falsely claiming the first 21-file ZIP alone reproduces S_rel significance.
- Both verifier families have been added to CI and exact stage-B code integrity to the source-only GitHub workflow. **Source metadata/Git code closure is not original GPS/DEM retrieval, matched environment, 9,999-permutation numerical replication, data licence or journal permission.** Original BE/JAE frozen branches and numerical outcomes remain unchanged; PR stays draft.

---

## 2026-10-15: calibrated spatial scope and source-native overlap inequality

The combined paper has been edited on this **draft integration branch only**, leaving the frozen BE and JAE source branches and all animal-data outcomes unchanged. The former broad title ("need not entail spatial partitioning") was too easily read as excluding horizontal differentiation. The updated working title is **Persistent individuality without consistent additional vertical segregation in bats** (83 characters; lay 65 words; abstract 233 words).

- Original native 500-m XY overlaps were descriptively greater for same-animal than other-animal session pairs in all four eligible panels (same 0.511–0.619 vs other 0.202–0.334); **horizontal partitioning has not been excluded**.
- For each common pairwise probability grid, O_XYZ <= O_XY is a mathematical property, not a biological test of between-animal **extra** vertical segregation. The historical other-minus-self R3D is descriptive; the terrain-relative S_rel null tests remain authoritative (positive 0/4), while 2023 co-use remains a heterogeneous positive exception (1/4).
- A new [source-locked horizontal-vs-vertical claim audit](prospective/unified_individuality/HORIZONTAL_VS_ADDED_VERTICAL_SEGREGATION_CLAIM_AUDIT_V1.md) contains the original four-panel XY/XYZ/n/S comparisons, probability-intersection proof and allowed/disallowed phrasing. Main manuscript, anonymous proof source, lay/abstract compliance, cover letter, internal/anonymous SI, submission gate and deterministic interpretive validator are synchronized. **No new animal analyses or p-values were created.**
- Latest head [64e21aa](https://github.com/zuizui0223/batter/commit/64e21aa2eb5163f2401fe8853e0cbd4b4e52100c) has all four relevant Actions completed successfully: [figures/source guards](https://github.com/zuizui0223/batter/actions/runs/38697394821), [main review PDF](https://github.com/zuizui0223/batter/actions/runs/38697394803), [SI review PDF](https://github.com/zuizui0223/batter/actions/runs/38697394792), and [historical source-only closure](https://github.com/zuizui0223/batter/actions/runs/38697394786).

**Still hard stops:** coauthor approval, source licensing/permissions, independent full GPS/DEM and historical-dependency numerical replay, anonymous DOI archive, verified human author/AI disclosures, and a genuine single-publication overlap decision. Neither journal submission nor full raw-data replication is claimed.

---

## 2026-10-15: completed historical terrain-code source closure (NOT a GPS/DEM rerun)

The original archived 500-m terrain-relative geometry and native 3D overlap results were previously published in successful JAE workflow artifacts. **The later frozen JAE rc2 checkout itself cannot execute the historical terrain runner unchanged**: its `run_v1.py`, `run_external_geometry_v1.py`, and `contract_v1.json` files are absent. The original terrain driver, terrain contract, DEM preflight and key source-loader scripts remain byte-identical to the successful commit.

**Source-only repair committed to this integration branch, without altering either original frozen JAE/BE branch:**

- [21-file historical single-commit manifest](prospective/unified_individuality/source_recovery/terrain_source_closure_manifest_v1.json) and [cryptographically verified recovery generator](prospective/unified_individuality/source_recovery/recover_terrain_source_closure_v1.py). Every source file is pulled from **exactly** commit `819acc829d615485b57033f1ddcbebf64b4b49a0` and checked against its source Git blob SHA.
- [Recovery/limitations report](prospective/unified_individuality/HISTORICAL_TERRAIN_SOURCE_CLOSURE_V1.md): 21 source/contract/preflight files recovered, portable source ZIP **61,398 bytes**, SHA256 `27e1f7cd44e3aa367f150aef8f608a7cec35a73a8ef922c0f2950d0059f13ce1`. GitHub workflow source-recovery [PASS, run 38685340549](https://github.com/zuizui0223/batter/actions/runs/38685340549); final original code import plus *synthetic-only* O_XY/O_XYZ/R3D function smoke [PASS, run 38685805292](https://github.com/zuizui0223/batter/actions/runs/38685805292).
- [Workflow](.github/workflows/unified-historical-terrain-source-closure-v1.yml) retrieves only original public-repository source code, parses and checks its dependencies, smoke-imports original modules with explicitly modern compatible dependencies, uses **invented** one-cell probability arrays to check original overlap equations, then uploads the source-only ZIP. **No raw Movebank GPS, tag tables, DEM rasters, 9,999-label-permutation source tests, or empirical bat outcomes have been downloaded or rerun.**
- [Native 3D overlap and provenance comparison](prospective/unified_individuality/NATIVE_3D_GEOMETRY_AND_SOURCE_CLOSURE_AUDIT_V1.md) remains unchanged scientifically: terrain-relative V_rel fidelity 4/4 in two species, **positive** S_rel segregation 0/4, co-use 1/4; original native-height S values are distinct from corrected S_rel and new descriptive 1D Figure S1 overlap.

**Residual hard stops:** original GPS/DEM source access and reuse permissions; original runtime/dependency version closure; independent end-to-end replay of original numerical outputs; anonymous versioned DOI deposit; coauthor sign-off and publication-overlap decisions. Do not call this a successful raw-data replication or journal submission.

---

## 2026-10-15: original 500-m native 3D overlap recovered; historical code closure documented

- **Original executed result, not a new GPS analysis:** recovered source-identical original 500-m gridded horizontal O_XY and joint native 3D O_XYZ from JAE original successful workflow [36881187913](https://github.com/zuizui0223/batter/actions/runs/36881187913). Exact original numeric summary Git blob **c1d37e42f72f59e5aba364daec9aef68b47778b6** is byte-preserved in [original 3D summary JSON](prospective/unified_individuality/figures/ORIGINAL_NATIVE_3D_OVERLAP_SUMMARY_V1.json). Structurally eligible source n = 8/5/6/9 in four *two-species* study-year panels.
- **Inference separated:** previous original native S_native (other-minus-self averaged R3D) +0.103/−0.017/−0.004/+0.130 contrasts with original terrain-relative S_rel −0.0158/−0.0090/+0.0163/+0.0289, with **zero positive permutation-supported S_rel panels**; conditional vertical identity V_rel 4/4. R3D is computed per eligible session pair before equal-individual weighting, not from the displayed OXY/OXYZ mean ratio. Earlier Figure S1's 0.80–0.92 1D centered profile SHAPE overlap is NOT 3D joint habitat overlap and covers a different source eligible sample.
- **New original-source visualization:** [Figure S2 SVG](prospective/unified_individuality/figures/FIGURE_S2_NATIVE_HORIZONTAL_AND_JOINT_3D_OVERLAP_V1.svg), source-verified deterministic [builder](prospective/unified_individuality/figures/render_original_native_3d_overlap_s2_v1.cjs), Table S10 and Methods S15 in anonymized SI, and new source-bounded Results/Discussion paragraph in unified main. Visual proof inspected: polished Figure S2 table/header does not collide.
- **Historical code closure blocker:** frozen `release/jae-v0.4.0-rc2` retains the terrain runner but lacks its historical `run_v1.py`, `run_external_geometry_v1.py`, native contract and summary. Original successful execution commits retain these. Four historical Python/contract files were archived **byte-identically** under [source_recovery/native_3d_history](prospective/unified_individuality/source_recovery/native_3d_history/), plus original terrain/calibration summaries. [Provenance audit](prospective/unified_individuality/NATIVE_3D_GEOMETRY_AND_SOURCE_CLOSURE_AUDIT_V1.md) and [static source/numerical validator](prospective/unified_individuality/validate_native_3d_source_recovery_v1.py) guard the source Git blobs and values. **No full source GPS/DEM/environment rerun has been performed**; archive/replay remains a hard gate, not misreported as complete.
- **Latest complete CI pass (all 3):** [Figures and source-hash audit](https://github.com/zuizui0223/batter/actions/runs/38684317047), [line-numbered anonymous main PDF](https://github.com/zuizui0223/batter/actions/runs/38684317149), [anonymous SI with Figures S1 & S2 as vector objects](https://github.com/zuizui0223/batter/actions/runs/38684317157). Current review proof is **27-page main + 18-page SI**. These PDFs remain coauthor proof material and not portal submission.
- **Original scientific, ethical and overlap guards unchanged**: JAE/BE frozen branches untouched; no new permutation or positive segregation claim, no new six-year animal persistence claim, no shared identified experimental-to-field mechanism. Coauthor approvals, source licenses, anonymous DOI archive and full raw-code replay remain pending.

---
## 2026-10-14: within-cohort size imbalance, projection caution and PDF readability

**These are source-preserving, exploratory descriptive checks of already-opened results, not new hypothesis tests or preregistration.**

- **Panel versus animal count:** immutable original CSV contains **103 individual-by-panel profiles**, but only **101 distinct literal animal-ID strings**; two repeat in original 2016 and 2022 `P. hastatus` source panels. Source PIT recapture metadata makes true recapture possible but **not confirmed** for these two tags. All 684 Figure S1 pairs remain distinct-ID comparisons **within the same exact panel and site/colony/year**; no cross-year self-pairs, original JAE inferential changes or pooled animal-independent effect is claimed.
- **Cohort weight audit:** [complete 12-cohort table and evidence boundary](prospective/unified_individuality/COHORT_WEIGHT_SENSITIVITY_AUDIT_V1.md) · [machine numbers](prospective/unified_individuality/figures/COHORT_WEIGHT_SENSITIVITY_V1.json) · [independent source CSV/Python validator](prospective/unified_individuality/validate_cohort_weight_sensitivity_v1.py). Largest source cohorts account for **68.3%** (*Eidolon*) and **75.0%** (*P. hastatus* 2023) of within-panel **dependent dyads**. Original pooled median shape overlaps 0.817/0.899 vs equally cohort-weighted **descriptive** medians-of-medians 0.855/0.865. In *Eidolon*, three pair-eligible cohorts each contain just one pair; neither aggregate is a defensible species-level niche-overlap parameter.
- **Physical-dimensionality limitation:** even with comparable actual 3D joint occupancy distributions, projected vertical overlap can equal **1** when joint 3D overlap is **0** (completely different horizontal cells, identical altitude). Original Figure S1 profile estimates were separately session-centered and used potentially different source self-horizontal weights, so these `O` coefficients cannot be converted into a measured 3D habitat overlap or even a quantitative bound on one. Exact synthetic mathematical counterexample and one-dimensional-versus-3D caution are in Methods S13; original terrain-relative S_rel and contemporaneous co-use nulls remain independent.
- **SI publication text:** added **Table U9/S9** (cohort counts, individual profiles, pair medians and dominance) and **Methods U14/S14** (aggregation rules); kept original Figure S1 only a supplemental descriptive figure and made its axis/footer explicitly mark size imbalance and nonindependent percentile bars. In the regenerated PDF, the cohort Table S9 heading was kept with its first table and source-safe plain-text mathematical formulas replaced nonrendering inline math. Original zero-change source hashes retained.
- **Original-field prior art:** [Calderón-Capote et al. 2025](https://doi.org/10.1371/journal.pone.0313782) had used the 2016/2022 La Gruta archives to analyze *horizontal foraging-area* overlap, a different estimand from the new 1D centered profile-shape overlap; they must not be equated.

**Hard stop unchanged:** coauthor approval, source/permit/redistribution permissions, anonymous archive, author attribution, and any new longitudinal tag registry confirmation before a six-year same-bat claim. PR remains draft.

---

## 2026-10-14: corrected global animal count and direct same-source foraging-overlap prior

**Publication-integrity update (original animal observations, frozen JAE/BE results and 684 descriptive dyads unchanged):**

- The 103 original JAE Figure 5B entries are **103 individual-by-panel self-prediction profiles** (20/24/33/16/10 within respective panels), **NOT proven 103 globally distinct living bats**. Source CSV/JSON identify only **101 different literal animal-label strings**: exactly two source identifiers recur at **La Gruta** in both 2016 and 2022 *P. hastatus* tracking panels. The 2025 source publication reports **PIT tagging and low 2016–2022 recapture**, making animal continuity plausible, but a confirmed transponder crosswalk for the two exact reused strings is still unavailable. Neither six-year strategy memory nor extra independent bat n is claimed. See [profile source-ID audit](prospective/unified_individuality/PROFILE_PANEL_IDENTITY_SCOPE_AUDIT_V1.md), [independent original-CSV guard](prospective/unified_individuality/validate_profile_panel_identity_scope_v1.py). **No 2016–2022 cross-year dyads enter the 684 previously computed within-panel/cohort pair outputs.**
- **Direct horizontal foraging-area prior art for same La Gruta source cohorts:** [Calderón-Capote et al. 2025, *PLOS ONE* 20:e0313782](https://doi.org/10.1371/journal.pone.0313782) evaluated the 2016/2022 archives' female/social-group 2D foraging areas and reported approximately **0.20 mean horizontal Bhattacharyya overlap**. This is scientifically **not the same variable** as the newly displayed **0.80–0.92 marginal session-centered 1D relative-altitude *shape* overlap**; the latter cannot be called 80–92% of shared 3D ecological space. The Introduction/Discussion/SI/figure legend and [prior-art ledger](prospective/unified_individuality/ECOLOGICAL_PRIOR_ART_POSITIONING_V1.md) now explicitly separate these measures.
- The unified main and anonymous bibliographies now have **37 referenced scholarly studies** (45 historical source DOI records plus two cited ecological papers from external prior-art review). The cover letter no longer claims all panels are biologically independent; original per-panel source null tests and results remain untouched.
- Updated [Figure 5](prospective/unified_individuality/figures/FIGURE_5_COMPOSITE_177x238MM_V2.svg) and [Figure S1](prospective/unified_individuality/figures/FIGURE_S1_WITHIN_COHORT_VERTICAL_SHAPE_OVERLAP_V1.svg) say **103 panel-indexed records** rather than globally independent animals. Derived overlap JSON now reports 103 panel profiles, 101 literal source strings, and `global_animal_identity_verified=false`; existing 684 pair values and median overlap statistics are numerically unchanged.
- GitHub Actions on verified head: [Source/profile/vector CI PASS](https://github.com/zuizui0223/batter/actions/runs/38529514473), [Anonymous main PDF PASS](https://github.com/zuizui0223/batter/actions/runs/38529514370), [Anonymous/internal SI PDFs PASS](https://github.com/zuizui0223/batter/actions/runs/38529514414).

**Still a DRAFT**: no submission, no human/coauthor sign-off, no permission to redistribute unsupported source archives, no direct neural/fitness/competition/longitudinal identity mechanism proved.

---

## 2026-10-14: cohort-restricted original 103 source-panel vertical profiles (descriptive only)

- **New descriptive research summary** from the exact frozen original Figure 5B **103 panel-indexed profiles / 10 height bins**: within original panel **and same site/colony/year source cohort** only, all **684 nonindependent unordered individual pairs** in 12 original source cohorts. No between-country, between-year or between-colony comparisons. Metric **1D centered profile shape overlap** O=sum(min(p_i,p_j))=1-TV; never true 3D habitat overlap, shared prey or synchronous co-use.
- Median O by panel: *Eidolon* **0.817** (41 pairs), *Hypsignathus* **0.801** (276), *Phyllostomus* 2022 **0.919** (262), 2023 **0.899** (60), 2016 **0.802** (45). The 10th–90th percentile bars are **empirical dependent-dyad spread, not confidence intervals**. Individual self-profile pairs can be estimated using different horizontal-cell supports and weights; session-centering and pseudocount smoothing influence apparent similarity.
- **Strict source provenance:** [exploratory metric design/claim boundary](prospective/unified_individuality/DESCRIPTIVE_VERTICAL_PROFILE_OVERLAP_CONTRACT_V1.md) was committed before computing new overlap values, but original profiles/results had already been inspected; **NOT preregistration or independent replication**. The exact original JAE JSON SHA256 is verified. [All 684 rows](prospective/unified_individuality/figures/ORIGINAL_PROFILE_WITHIN_COHORT_OVERLAP_PAIRS_V1.csv), [cohort + panel summary JSON](prospective/unified_individuality/figures/FROZEN_PROFILE_OVERLAP_DESCRIPTIVE_V1.json), [deterministic Node generator](prospective/unified_individuality/figures/derive_centered_vertical_overlap_v1.cjs) are tracked in the integration PR.
- **Figure S1** [fully editable vector](prospective/unified_individuality/figures/FIGURE_S1_WITHIN_COHORT_VERTICAL_SHAPE_OVERLAP_V1.svg) added to [illustrated figure atlas](prospective/unified_individuality/FIGURE_ATLAS_AND_CAPTIONS_V1.md), with accessible alt text. **Table U8/S8 and Methods U13/S13** added to both SI versions and the chart is **embedded as vector art in the anonymous single SI PDF** (13 A4-landscape pages). PDF page rendering/figure-heading placement checked; it is still author-review only.
- **Two independent numeric paths** agree to full reported precision: original archival **JSON → pure Node script** versus original independent **CSV → Python** ([validator](prospective/unified_individuality/validate_overlap_independent_csv_v1.py)); both check the source SHA, exact panel/cohort eligibility and 684 dependency-aware pair count. [Figure CI PASS](https://github.com/zuizui0223/batter/actions/runs/38522253268), [anonymous SI+PDF CI PASS](https://github.com/zuizui0223/batter/actions/runs/38521907553), [anonymous main PDF CI PASS](https://github.com/zuizui0223/batter/actions/runs/38522253182).
- **Inference unchanged:** established original whole-session vertical identity, post-outcome terrain V_rel 4/4, positive S_rel 0/4, synchronous phase-shift I 1/4, and failed laboratory-to-field bridge remain separate. The new 1D overlap is only a transparent visual explanation for how normalized estimated shapes can look similar while their original held-out individual predictions differ. This is **not** a new ecological non-partitioning test.

**Draft only; no publication overlap, author/ethics/AI disclosure, licence or anonymized DOI repository gate was bypassed.**

---

## 2026-10-14: ecological mechanism identifiability and honest historical novelty

**One-paper draft remains the preferred editable research candidate, NOT submission-authorized.** No new animal-data test has been run or source-based significance threshold changed.

- **Previously completed conditional individuality now in Results, Discussion, Abstract and expanded SI S12:** Four source-opened post-outcome panels retain vertical identity after 500-m place × coarse speed–turn matching (n=19/23/11/9; calibrated excess +0.3840/+0.0868/+0.1015/+0.4514; source p=0.0002/0.0002/0.0006/0.0286). Calendar-night conspecific controls 3/4 (P2016 p=0.0544 remains FAIL), self-history lags >=1/>=3/>=7 days support 4/4,3/3,2/2 on **different eligible panels**.
- **Source and code audit:** [frozen JAE conditional/lag/wind source receipts pinned by seven original Git blob SHAs](prospective/unified_individuality/figures/FROZEN_MAINTENANCE_BOUNDARY_INPUTS_V1.json) and [validator](prospective/unified_individuality/validate_ecological_identifiability_v1.py) now guard all statuses, S_rel 0/4 positive, co-use 1/4, 60/600-s scope, wind structural STOP 7/8 and a mathematical demonstration of unresolved latent-task mechanisms.
- **Mechanism identifiability:** [mathematical note](prospective/unified_individuality/ECOLOGICAL_IDENTIFIABILITY_AND_DECISIVE_TESTS_V1.md) shows exactly how the **same** two marginal vertical probability vectors can be obtained either from individual task allocations or different within-task solutions. The hypothetical overlap=0.8 and KL=0.081093 are **not bat source outputs** and not the empirical S_rel measure. Future study requires independently labeled tasks/patches and matched prospective experimental interventions.
- **Ecological novelty priority corrected:** [Carlson et al. 2021](https://doi.org/10.1038/s41467-021-24826-x) already demonstrated persistent highly overlapping/nested stork environmental niches, and [Wang et al. 2023](https://doi.org/10.1186/s40462-023-00394-1) bat spatial specialisation with seasonal overlap. The unified paper now expressly **disclaims any first-ever overlap-vs-individuality concept**. Distinct candidate evidence is calibrated *bat 3D height probability shape*, conditionally matched retained identity and separate terrain/co-use nulls; see [prior-art ledger](prospective/unified_individuality/ECOLOGICAL_PRIOR_ART_POSITIONING_V1.md).
- **Latest document state:** 69-character title, **233-word Abstract / 73-word Lay Summary**, **36** main scholarly references, anonymous SI Methods **S1–S12**. No raw-data rerun, no common lab–field causal carrier (frozen bridge 2/4 FAIL), and no fabricated individual animal profiles.

**Unchanged editorial stops:** human coauthor/statistical/novelty review; permission-respecting anonymized DOI data/code archive; all original data reuse/ethics approvals; journal-specific figure/PDF approval and author/AI disclosures. Draft PR remains open.

---

## 2026-10-14: scientific source-attribution corrections and full Methods

- **Source DOI mapping corrected** in both internal and anonymous SI: *Phyllostomus hastatus* 2016 = **10.5441/001/1.282**, 2022 (2021–2022 archive) = **10.5441/001/1.321**, 2023 = **10.5441/001/1.322**. The previous initial SI draft cyclically misassigned these three DOIs. Original JAE rc2 and its data-ingestion script independently support the corrected mapping. Numeric effect results are unchanged.
- **Actual original study citations repaired:** *Eidolon helvum* dataset corresponds to O'Mara et al. (2019), not a separate Fahr et al. (2015) source; *P. hastatus* 2016 traces to O'Mara and Dechmann (2023), longitudinal 2021–2023 to Calderón-Capote et al. (2024). The main/anonymous bibliography now contains **35 cited scholarly records**, with high-risk 2026 external metadata verified.
- **Fuller source-derived SI Methods:** added **S4–S11** covering wild screening, 5-km common-cell estimator, complete-pipeline nulls, shift-invariant altitude binning/device checks, 500-m terrain/co-use and bootstrap bounds, multi-day maintenance, acute experiments, development randomizations, I/M portability and the failed field bridge. Anonymous SI PDF proof is now **9 A4-landscape pages**, not the superseded five-page abbreviated draft.
- **Regression prevention:** [source attribution validator](prospective/unified_individuality/validate_source_attribution_v2.py) checks both SI copies and the updated published references against the canonical source-year identities; [publisher/source audit](prospective/unified_individuality/SOURCE_DOI_AND_METADATA_AUDIT_V2.md) documents corrections and exact external authority links.
- **Coauthor workflow:** [editorial cover-letter draft](prospective/unified_individuality/COVER_LETTER_BEHAVIORAL_ECOLOGY_UNIFIED_DRAFT_V1.md) discloses post-outcome field geometry, failed lab-to-field bridge, original overlap and AI assistance, with hard-stop author/DOI placeholders. No journal submission has been carried out.
- **Current checks:** [Figures PASS](https://github.com/zuizui0223/batter/actions/runs/38515570661) · [anonymous manuscript PASS](https://github.com/zuizui0223/batter/actions/runs/38515570623) · [nine-page SI PASS](https://github.com/zuizui0223/batter/actions/runs/38515570657). An anonymous SI proof was rendered and visually inspected; orphaned table heading placement was corrected.

**Research inference unchanged:** post-outcome V_rel 4/4 supported, positive S_rel 0/4, co-use 1/4 across just two bat species; experimental identity correspondence does not establish a single shared causal laboratory-to-wild mechanism.

---

## 2026-10-14: unified single-paper coauthor review package

**Status:** Draft PR for scientific/coauthor review, **NOT authorized for journal submission**. This is the *alternative single article* replacing duplicate primary JAE + BE submissions, not a third paper.

- [Unified paper](prospective/unified_individuality/INTEGRATED_MANUSCRIPT_V1.md): one causal-layer ecological argument; **69-character title, 215-word abstract, 73-word lay summary**, consolidated 34 scholarly main references.
- [Figure 5 A+B](prospective/unified_individuality/figures/FIGURE_5_COMPOSITE_177x238MM_V2.svg): full 177 × 238 mm editable vector figure from the **original 103 individually identified × 10 altitude-bin source probabilities**, with exact source archival hashes and a separate original unchanged PNG. New plotting does not constitute new component-level inference.
- [Six main figures and captions](prospective/unified_individuality/FIGURE_ATLAS_AND_CAPTIONS_V1.md) plus [accessible figure alt text](prospective/unified_individuality/FIGURE_ALT_TEXT_V1.md); [source-snapshot and figure CI](.github/workflows/unified-manuscript-figures-v1.yml) checks the original archived profile hashes, figure reproducibility and scientific verdicts.
- [Anonymous complete text draft](prospective/unified_individuality/COMPLETE_ANONYMOUS_TEXT_DRAFT_V1.md) generated reproducibly and [line-numbered review PDF workflow](.github/workflows/unified-anonymous-main-v1.yml): **22 pages, 654 numbered lines**, internal coauthor proofreading only.
- [Single-source combined SI draft](prospective/unified_individuality/SUPPORTING_INFORMATION_DRAFT_V1.md), [anonymous SI draft](prospective/unified_individuality/SUPPORTING_INFORMATION_ANONYMOUS_DRAFT_V1.md), and [5-page PDF workflow](.github/workflows/unified-si-draft-v1.yml) providing separate internal and anonymous review variants.
- [Submission readiness / hard-stop ledger](prospective/unified_individuality/SUBMISSION_READINESS_GATE_V2.md) documents outstanding coauthor and statistical review, source licence and ethics checks, actual anonymous DOI archive URL, funding/authorship/AI disclosure approval, figure and SI final journal-size checks.

**Recent CI at commit b16039d:** [Figures PASS](https://github.com/zuizui0223/batter/actions/runs/38513434849), [anonymous manuscript PASS](https://github.com/zuizui0223/batter/actions/runs/38513434859), [SI PASS](https://github.com/zuizui0223/batter/actions/runs/38513434862).

**Inference is bounded:** lab-to-field carrier bridge overall FAIL 2/4; post-outcome field fidelity 4/4, positive segregation 0/4, co-use separation 1/4 in four panels of **two species**; do not overclaim shared causal mechanism, no competition, or equivalence of null effects.

---

## 2026-10-14: original 103-individual JAE Figure 6 recovered and reviewed

- Original JAE visual from [frozen run 36375056204](https://github.com/zuizui0223/batter/actions/runs/36375056204), source artifact `10950667566`, restored **byte-for-byte** as [source PNG](prospective/unified_individuality/figures/original_jae/figure6_individual_centered_shape_profiles.png), [103-row CSV](prospective/unified_individuality/figures/original_jae/centered_shape_individual_profiles_v1.csv) and [profile JSON](prospective/unified_individuality/figures/original_jae/centered_shape_individual_profiles_v1.json).
- Five original comparative panels, **103 individual-by-panel records / 10 centered height bins**, original probabilities and upper/lower-tail component estimates. These profiles are DESCRIPTIVE, not a new inference or novel strategy class.
- [Recovery receipt](prospective/unified_individuality/ORIGINAL_PROFILE_RECOVERY_RECEIPT_V1.md) pins SHA256 for all imported bytes. The one-time write-privileged import workflow completed successfully ([run 38507348011](https://github.com/zuizui0223/batter/actions/runs/38507348011)) and was **removed afterward**. Existing read-only figure CI now guards imported exact hashes, CSV probability sums and SVG reproducibility.
- Manuscript **Figure 5A** = calibrated original six-panel identity; **Figure 5B** = exact source original 103-individual profile heatmap. [Figure atlas](prospective/unified_individuality/FIGURE_ATLAS_AND_CAPTIONS_V1.md) updated accordingly.
- [Source DOI bibliography audit](prospective/unified_individuality/BIBLIOGRAPHY_MERGE_AUDIT_V1.md): source JAE+BE reference lists reconciled to **45 unique DOI records** (39 scholarly + six source datasets); 34 selected articles in combined main bibliography. This is **textual** source reconciliation, not an external Crossref verification.
- [Preliminary visual QA](prospective/unified_individuality/FIGURE_RENDER_VISUAL_QA_V1.md): six SVG figures rendered and visually checked in PNG preview; Fig. 6 must stay full width. This is NOT target-journal proof approval.
- [Scientific reviewer gate](prospective/unified_individuality/INTERNAL_SCIENCE_REVIEW_GATE_V1.md): integrated mechanism, post-outcome geometry, small n, source licensing and single nonredundant publication plan remain critical limits.

**Status remains DRAFT — not approved for submission.** Remaining: human coauthor/statistical review, final DOIs/author-year audit, complete SI/review archive/licensing and journal-size figure/PDF proof.

---

## New generated evidence figures and SI (2026-10-14)

- **Six manuscript SVG figures rendered:** [visual figure atlas](https://github.com/zuizui0223/batter/blob/prospective/unified-be-jae-individuality-v1/prospective/unified_individuality/FIGURE_ATLAS_AND_CAPTIONS_V1.md), with source-specific uncertainty labels and evidence tiers.
- **Figure 6 is the ecological core:** wild terrain-relative identity supported 4/4, positive additional segregation supported 0/4, synchronous co-use separation 1/4. Plots show distinct estimands on separate axes, S permutation-null envelopes vs I dyad-bootstrap compatibility intervals.
- **Co-use comparator corrected:** H and P2022 60 s endpoint-excluded; P2023 600 s all-space; P2016 600 s endpoint-excluded.
- **Actual combined SI draft:** [SUPPORTING_INFORMATION_DRAFT_V1.md](https://github.com/zuizui0223/batter/blob/prospective/unified-be-jae-individuality-v1/prospective/unified_individuality/SUPPORTING_INFORMATION_DRAFT_V1.md), with source-specific experimental nulls, original wild panel results, external boundary evidence, and data-redistribution caveats.
- **Reproducibility:** figure input snapshot pins 8 source files by branch/path/blob SHA; [generator](https://github.com/zuizui0223/batter/blob/prospective/unified-be-jae-individuality-v1/prospective/unified_individuality/figures/generate_integrated_figures_v1.cjs) uses built-in Node only; [validator](https://github.com/zuizui0223/batter/blob/prospective/unified-be-jae-individuality-v1/prospective/unified_individuality/figures/validate_integrated_figures_v1.py) checks source statuses/encounter rules and SVG XML; [workflow](https://github.com/zuizui0223/batter/blob/prospective/unified-be-jae-individuality-v1/.github/workflows/unified-manuscript-figures-v1.yml) checks generated files are deterministic.
- **Current remaining gates:** external DOI/author-year verification, full independent human visual/statistical review, complete SI/reviewer archive and licence audit, target-journal checks, author disclosures, and approved single-paper publication decision. Original JAE profile figure/data are now recovered and protected by regular CI. Draft PR remains not submission-ready.

---

## Purpose

Develop **one integrated research manuscript**, not an additional paper to publish on top of the existing JAE and BE candidates. The biological question is: **What persists when behavior remains individually predictable, and when does that persistence require spatial partitioning?**

## New files only

- [Full integrated manuscript](prospective/unified_individuality/INTEGRATED_MANUSCRIPT_V1.md): rewritten Abstract, Introduction, Methods, Results and Discussion, with explicit limits on a common laboratory–field causal mechanism.
- [Evidence crosswalk](prospective/unified_individuality/EVIDENCE_CROSSWALK_V1.md): primary/secondary/post-outcome distinctions, exact original numbers, biological n, external failures and prohibited inference.
- [Figures and SI plan](prospective/unified_individuality/FIGURES_AND_SI_PLAN_V1.md): six main figure designs, SI source allocation and draft section budget.
- [Integration QA](prospective/unified_individuality/INTEGRATION_QA_V1.md): 35 selected numeric keys reconciled textually against canonical sources; not raw-data recomputation.
- [README](prospective/unified_individuality/README.md).

All JAE and BE original files remain unchanged on their frozen source branches. This PR only adds the unified directory.

## Authoritative originals (important)

- **Wild JAE v0.4.0 rc2**: release/jae-v0.4.0-rc2, manuscript blob \`c4ef51a7f3f291a6f203d303dbf73f5b54fb7683\`.
- **BE controlled/development programme**: prospective/public-causal-synthesis-v1, manuscript blob \`a83fed81a141c62df29f3c12f2fb5fd36399c160\`.
- The JAE copy resident on the BE branch is **not** identical to the rc2 manuscript and was not used as a numerical source.

## Most defensible integrated result

1. Individual correspondence survives several acute sensory/navigation manipulations (small biological n in some sources).
2. A compact movement representation can retain correspondence where fixed detailed trajectory geometry does not.
3. Wild terrain-relative individual configuration retains identity in four eligible panels from **two species**, while **none** supports positive added segregation and **only one** supports synchronous extra co-use separation under a coarser design.
4. Developmental total-dispersion contrasts and the frozen laboratory-style wild bridge constrain inference; they do not establish a shared mechanism.

## Review red lines

- Do not relabel first-flight composite-gate FAIL (8/14 < 10/14) as PASS simply because one component p=0.0102.
- Do not turn p=0.167785 / 0.716667 developmental nonsupport into equivalence.
- Do not turn S_rel positive non-support into proof that competition does not occur.
- Keep H. monstrosus negative-direction S_rel p=0.036 and P. hastatus 2023 co-use +3.57 m (p=0.023; 600 s/all-space).
- Keep external Nyctalus/Hipposideros/Myotis failures and the Pteropus positive result.
- The frozen lab-to-field bridge is **PASS/PASS/FAIL/structural STOP**, overall FAIL at 2/4 versus >=3/4.
- Do not count post-outcome wild geometry as prospective confirmation or the same P. hastatus species across three years as three independent species.
- No common individual latent policy, learning mechanism, or direct transfer to wild foraging niche has been demonstrated.

## Not submission-ready

This is a **draft PR** for scientific review only. Still required: bibliography/citation audit, source-level methods and Supporting Information completeness, figure regeneration, coauthor review, author/AI disclosures, anonymous archive and new publication decision. Do **not** submit both previous manuscripts plus the unified version with duplicated primaries.
