# Supplementary Material

**Individual organization remains detectable across acute perturbations in bats**

This supplement contains source/provenance tables, frozen inference definitions, descriptive developmental decompositions, exact-null resolution context, and the evidence-tier rules used for the comparative synthesis.

---

# Supplementary Table S1. Public source and analysis provenance

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

# Supplementary Table S2. Frozen inference definitions

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

# Supplementary Figure S1. Analysis-provenance timeline

The provenance timeline summarizes the sequence:

1. endpoint / support / null frozen;
2. structure or schema opened;
3. numerical outcome opened;
4. frozen result recorded;
5. implementation-only correction, when one occurred.

Special cases shown explicitly:
- Eptesicus: a Euclidean-distance syntax error was corrected without changing the frozen endpoint, statistic or null before the successful rerun;
- Aharon: an initial API-access failure was resolved through the anonymous public file route before the frozen Figure-1 primary opened;
- Rachum: the primary calculation completed reproducibly while an output-receipt push race affected persistence only, not the numerical result.

No scientific endpoint was changed by these implementation events.

See Supplementary Material Figure S1.

---

# Supplementary Figure S2. Developmental descriptive decompositions

## Rachum

Display all three additive contributions to D:
- Boldness +0.465792;
- Exploration +0.250837;
- Activity +0.018070.

No trait-wise p-values.

## Elie

Display all 28 additive feature contributions to D, ordered by absolute magnitude.

Report:
- 15 positive;
- 13 negative;
- cancellation ratio 0.840173.

No feature-wise p-values.

---

# Supplementary Figure S3. Exact-null resolution and biological n

Exact identity/null spaces differ among the small-n controlled experiments:

- Eptesicus: 4 biological individuals, 4!=24 identity mappings, minimum attainable exact one-sided p=1/24=0.041667;
- Aharon: 4 biological individuals across two independently permuted non-anchor conditions, (4!)²=576 mappings, minimum p=1/576=0.001736;
- Myotis: 3 biological individuals under the frozen five-context architecture, 1,296 legal assignments, observed true mapping uniquely most extreme.

The size of the combinatorial null quantifies resolution of the **within-experiment identity-mapping test**. It does not increase the number of biological individuals and must not be interpreted as population-level replication.

See Supplementary Material Figure S3.

---

# Supplementary Methods S1. Evidence-tier rules

Define:
- frozen primary;
- predeclared secondary;
- post-primary diagnostic;
- descriptive/exploratory result;
- structural STOP;
- failed frozen gate.

State explicitly that a lower evidence tier cannot rescue a failed higher-tier gate.

---

# Supplementary Methods S2. Cross-study synthesis boundary

State:
- no pooled quantitative meta-analysis;
- no shared effect-size scale across endpoints;
- common inferential object for acute perturbation = same-individual correspondence after shared context effects are removed;
- source discovery and cross-study synthesis were iterative;
- source-level endpoints/nulls were frozen before outcome opening.

---

# Supplementary publication-overlap disclosure

Several public tracking datasets used as a downstream wild-boundary analysis also appear in a separate vertical-individuality manuscript. The synthesis does not count those vertical-shape results as independent positive evidence. The older Tadarida-only Movement Ecology draft containing the same V1/V2 analysis now incorporated into the vertical-individuality manuscript has been retired from separate submission.
