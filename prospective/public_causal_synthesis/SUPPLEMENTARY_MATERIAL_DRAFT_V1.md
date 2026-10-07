# Supplementary Material draft v1

This file is the content source for the single Supplementary Material PDF allowed by Behavioral Ecology.

Do not include executable code here. Code and result receipts belong in the anonymized analysis archive.

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

For each source, provide:
- biological unit;
- endpoint;
- scale/transform;
- equal-weighting hierarchy;
- minimum support;
- frozen null/randomization architecture;
- exact/Monte-Carlo assignment count;
- primary support rule;
- whether any later analysis is secondary/diagnostic.

Populate from MASTER_RESULTS_TABLE_V1.md and source contracts before final PDF assembly.

---

# Supplementary Figure S1. Analysis-provenance timeline

For each source show:
1. endpoint/contract freeze;
2. structural/schema opening;
3. numerical opening;
4. primary result;
5. any implementation-only correction.

Include explicit notes for:
- Eptesicus Euclidean-distance syntax correction;
- Aharon public-file retrieval resolution;
- Rachum result-receipt push race.

Purpose:
show that implementation fixes did not change frozen scientific choices.

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

Illustrate:
- Eptesicus: 4! = 24 mappings;
- Aharon: (4!)^2 = 576 mappings;
- Myotis: 1,296 legal condition-wise assignments.

Explain that exact-null resolution measures within-experiment identity correspondence and does not substitute for broad population biological replication.

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
