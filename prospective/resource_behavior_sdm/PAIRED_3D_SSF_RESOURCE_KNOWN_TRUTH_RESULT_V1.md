# Paired 3D resource × behavioral state benchmark v1 — verified known truth

Date: 2026-11-21. Scientific status: **SOURCE-FREE SIMULATION PASS, NO NEW FIELD 3D EFFECT ESTIMATED**. This is not a reproduction of the published continuous-space ssf3D fit, not a regional bat species occurrence model, and not an identified causal food mechanism. Draft batter PR #102; protect JAE/BE and main.

## Direct comparator and correct likelihood denominator

Klappstein et al. (2026, *Ecology Letters*) DOI https://doi.org/10.1111/ele.70414 already introduced 3D correlated random walks and step-selection functions. The source R code, https://github.com/NJKlappstein/ssf3D, has matched 3D observed/control endpoint generation, distance/turning metrics and explicit sampling-proposal correction for gamma/Kent distributions. This is direct prior art.

Our paired discrete diagnostic **is not the full R continuous 3D-SSF implementation**. Its purpose is to learn whether extra resource information on identical withheld steps is primarily about horizontal candidate choice or **height conditional on a chosen horizontal cell**. Fixed Cartesian XY × height candidate sets and matched log-score denominators are mandatory; do not equate this discrete grid with the ssf3D importance-sampling continuous normalizer.

Model ladder, same available endpoints / same heldout observed endpoints:
- M0: movement step length, log step length, 3D turn cosine, arc orientation, forest structure and candidate AGL, trained as ridge conditional softmax.
- M1: M0 + independent XY resource (cactus locations or dated directly observed blooms). Tests resource information about chosen endpoints.
- M2: M1 + resource × candidate height; compare **within-horizontal height prediction**, not only total step-choice performance.
- M3: M2 + resource × state and resource × height × state interactions. State is fixed independently of the altitude outcome (XY/time-only prior movement or another independent sensor), NOT the altitude-defined author cactus-visit class.

Exact discrete probability identity: log p(XY,Z) = log p(XY) + log p(Z|XY), and delta_joint = delta_horizontal + delta_height_given_horizontal. Mathematical bookkeeping only; cannot be interpreted as fitted regional species occupancy. Refit and standardize inside training folds only; equal animal, equal nights within animal, equal steps within night. Whole-bat, whole-bat-night or whole-site folds. Hold out an entirely unseen bat without introducing a learned personal coefficient.

## Tested deterministic synthetic scenarios

Generator seed 1834, 8 fictional bats × 2 nights × 15 steps = 240 fictional observed events; each with 2 XY × 3 AGL candidate endpoints. Every source-free scenario has eight whole-bat training/heldout folds. All values are nats per step; NOT field effects, statistical significance or independent animal data.

| Generated known-truth condition / paired contrast | Δjoint | Δhorizontal | Δheight given horizontal |
|---|---:|---:|---:|
| No resource effect, M1−M0 | −0.002546 | −0.002509 | −0.000037 |
| No resource effect, M2−M1 | −0.000885 | −0.000006 | −0.000879 |
| Resource only moves horizontal selection, M1−M0 | +0.096622 | +0.096533 | +0.000088 |
| Horizontal-only true effect, M2−M1 | −0.000532 | +0.000482 | −0.001013 |
| Resource×height true effect, M1−M0 | +0.231092 | +0.232591 | −0.001499 |
| Resource×height true effect, **M2−M1** | **+0.062559** | +0.023542 | **+0.039017** |
| State-conditioned resource×height true effect, **M3−M2** | **+0.601791** | +0.137035 | **+0.464757** |

These show that resource may add predictive information mostly horizontally, and a separate conditional height gain can be detected when deliberately programmed into the simulation. Resource affecting height can also change which XY is chosen, so do not require horizontal gain to vanish. No causal mechanism or empirical bat height fit is inferred.

## Fail-closed original-source eligibility

1. Original GPS fixes with verified terrain-relative AGL, regular sampling, valid movement history; candidate endpoint availability frozen before outcomes, never constructed from heldout chosen locations.
2. Each XY candidate offers the same set of >=2 height categories. Nonnegative independently measured XY resource must be constant across Z bins for a given XY. Source location and date support cannot be inferred from a model-generated flower count.
3. For Stage A mapped cactus XY only: resource kind is cactus_location_proxy, not real dated food. For Stage B: independent observed dated flower counts, same field and bat-night, verified survey effort and **no simulation imputation**; else STOP.
4. For M3: independently height-blind classification. The Goldshtein paper defined cactus visits with altitude <20 m, so those labels and any height-derived core classes are prohibited.
5. To interpret a new field effect, additionally audit source file SHA-256/headers, original candidate sampling process, spatial/temporal survey coverage, height sensor measurement error and observation/detection. This pure-stdlib conditional scorer cannot authenticate input provenance flags. Thus its output always sets **empirical_resource_height_bat_gain_claim_allowed = false**.
6. Never report GPS fix-level independent p-values, source exact coordinates, identities, real animal IDs or source rows. The tool emits only aggregate ordinals and means.

The newly implemented code: [paired_3d_ssf_resource_benchmark_v1.py](paired_3d_ssf_resource_benchmark_v1.py). Known truth tests: [test_paired_3d_ssf_resource_benchmark_v1.py](test_paired_3d_ssf_resource_benchmark_v1.py).

## Exact next source gate

Original Goldshtein Mendeley DOI https://doi.org/10.17632/jxghjjsttw.1 remains officially HTTP 401 from GitHub (recovered original source gate artifact). Publication documents approximately 3,600 mapped cacti for 8 GPS bats versus direct bloom observations of 414 cacti in 3 different fields. Whether exact same-night observed bloom counts align with GPS events is **UNVERIFIED**. The separate safe ZIP intake [goldshtein_user_archive_structural_gate_v1.py](goldshtein_user_archive_structural_gate_v1.py) is ready when author files become accessible. Until then, M0–M3 results above are known-truth software checks only.

Frozen JAE/BE, esdm main and batter main untouched; PR remains Draft.


---

## Unmeasured-habitat confounder counterexample (same 8 fictional-bat holdouts)

An additional synthetic data-generating world specifies latent habitat quality H at candidate XY. H causes **both** (i) measured resource abundance R, and (ii) bat horizontal and vertical step-choice probability. The direct causal coefficient **R → bat is explicitly ZERO** in the generator; the coarse observed forest_structure predictor does not fully measure H.

This world nevertheless produces:

| Contrast | Δjoint | Δhorizontal | Δheight conditional XY |
|---|---:|---:|---:|
| M1−M0 (add observed resource proxy) | +0.312697 | +0.311696 | +0.001001 |
| M2−M1 (add resource × height interaction) | +0.186130 | +0.031978 | **+0.154152** |

Thus, **out-of-bat heldout prediction of height can improve strongly even without ANY causal role for the measured resource**. A reproducible test named test_hidden_habitat_generates_false_causal_resource_height_conclusion is now in the source-free test suite. This is a **methodological counterexample**, not a measurement of forests or bats.

**Implications for later field inference:**
- Distinguish the predictive claim (R helps forecast Z conditional XY) from causal claims (changing R changes Z).
- Require observed *same-XY repeated nights* with real flower changes, habitat/terrain and weather controls, verified survey effort, and contemporaneous altitude observations before proposing a time-varying resource mechanism. A temporally stable cactus XY map alone cannot identify that mechanism.
- Test food versus matched nonfood and within-habitat/time resource shuffle nulls, and quantify unmeasured-structure sensitivity. If such data are missing, report the extra forecast information but STOP before claiming mechanism.
- Do not use dated or proxy flags alone as guarantees of causal identifiability, even with perfect nested group holdout.
