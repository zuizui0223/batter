# Auditory perturbation result integration v1

## Status

**CONFIRMATORY PUBLIC-DATA RESULT — FROZEN PRIMARY SUPPORTED.**

Source:
Diebold, Lawlor et al. (2024), *Rapid sensorimotor adaptation to auditory midbrain silencing in free-flying bats*.

Public archive:
Zenodo `10.5281/zenodo.13857870`.

Parent records:
- `AUDIT_CONTRACT_V1.md`
- `STRUCTURAL_RESULT_V1.md`
- `ACOUSTIC_POLICY_PRIMARY_V1.md`
- `INTERPRETATION_LEDGER_V1.md`
- `ACOUSTIC_POLICY_RESULT_V1.md`
- `PROGRAMME_UPDATE_CONTRACT_V1.md`

## Frozen result

Four DREADD bats:
- jane;
- bea;
- jason;
- stella.

Frozen four-feature trial representation:
- mean call duration;
- mean bandwidth;
- mean inter-pulse interval;
- call rate.

Shared `treatment × trialtype` means were removed without using bat identity, followed by one pooled residual SD per feature.

Same-individual Saline-to-Ligand retention:

- K = **+1.004452**;
- **4/4** individual advantages positive;
- exact identity permutations = **24**;
- true same-bat mapping rank = **1/24**;
- exact one-sided p = **0.0416667**;
- verdict = **SUPPORTED**.

Individual advantages:
- jane: **+0.826821**;
- bea: **+1.411613**;
- jason: **+0.119224**;
- stella: **+1.660151**.

## Descriptive component localization

No component-wise inferential tests were authorized.

Descriptive K:
- duration: **+0.789331**;
- bandwidth: **+0.536278**;
- IPI: **+0.173420**;
- call rate: **+0.156400**.

Duration and bandwidth contribute most strongly descriptively, but no component may be promoted as an independently calibrated carrier.

## Interpretation

The source experiment reversibly perturbs central auditory processing.

After removing the common treatment × trial-class shift, Ligand vocal organization remained closer to the same bat's Saline organization than to other bats' Saline states.

Therefore:

> **A strong experimentally imposed change in central auditory processing altered common behavioral expression without erasing the individual-specific multivariate vocal organization captured by the frozen endpoint.**

This supports a storage-versus-expression distinction:

[
\text{perturbed current sensory processing}
\not\Rightarrow
\text{complete erasure of personal organization}.
]

It does **not** identify the storage substrate.

## Why this matters relative to the masker result

The earlier *Pipistrellus kuhlii* masker programme showed retention of individual movement bias across an external sensory perturbation.

This *Eptesicus fuscus* result differs in:
- species;
- manipulation;
- behavioral endpoint;
- experimental architecture.

The two results therefore triangulate rather than replicate one identical carrier.

Safe joint conclusion:

> **Across independent bat systems, distinct sensory perturbations can shift expressed behavior while leaving detectable individual-specific organization.**

## Exact-resolution boundary

This is only four biological individuals.

Because:

[
4! = 24,
]

the minimum attainable one-sided exact p-value is:

[
1/24 = 0.0416667.
]

The result succeeds because the observed true identity mapping is the single best mapping among all 24.

This is:
- strong within this exact permutation universe;
- low-resolution as population-level inference.

Do not describe it as high-powered population evidence.

## Implementation provenance

The first numeric attempt failed after all data preprocessing and centroid construction because of a pure code typo:

`np.linalg.norm(L, x)`

instead of:

`np.linalg.norm(L - x)`.

The frozen Euclidean-distance statistic was not changed.

After correcting only that implementation call:
- synthetic exact-identity self-test: PASS;
- frozen numeric primary: PASS;
- result commit: PASS.

The failure is not part of the biological evidence.

## Closed rescue paths

No further same-source confirmatory identity search is authorized through:
- feature subsets;
- PCA;
- trajectory n=3;
- sham pooling;
- Baseline inclusion;
- bat deletion;
- trial-level pseudoreplication.

Trajectory data remain descriptive/mechanistic only because the released DREADD trajectory layer contains three bats:

[
3! = 6,quad p_{min}=0.1667.
]

## Programme consequence

This result strengthens:

[
\text{persistent personal information}
\rightarrow
\text{context-dependent expression}.
]

It does not solve:
- developmental origin;
- biomechanics versus learning;
- solution abundance;
- field carrier-to-niche mapping;
- fitness payoff.

Those remain separate questions.
