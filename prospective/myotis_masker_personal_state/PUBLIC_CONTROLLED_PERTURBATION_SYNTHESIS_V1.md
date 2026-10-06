# Public controlled-perturbation synthesis v1

## Status

**CURRENT PUBLIC-DATA CONTROLLED-PERTURBATION SYNTHESIS.**

This synthesis includes only analyses whose individual-identity question was frozen before the new identity outcome was opened.

It does not alter JAE v0.4.0.

---

## 1. Pipistrellus kuhlii — sensory masker perturbation

Independent public source:
Taub & Yovel 2020.

Frozen source-native movement endpoint:
3-D angle of attack.

### Baseline -> masker

- K = **+4.941 deg**
- 5/6 positive
- exact p = **0.04028**
- no-refit R² = **0.2855**

### Foam no-masker -> foam + masker

- K = **+6.779 deg**
- 5/5 positive
- exact p = **0.025**
- no-refit R² = **0.6414**

Published manipulation changes sensory conditions.

New individual-identity inference:

> personal movement bias remains predictive across the manipulation.

---

## 2. Myotis daubentonii — masking-noise gradient

Independent public source:
Foskolos et al. 2022.

Dataset:
Zenodo 4946256 / Dryad 10.5061/dryad.ngf1vhhv3.

Published experiment:
- four bats exposed to five masking levels;
- bats approach and land on a noise-emitting target;
- published treatment effect includes longer landing time with stronger noise.

Frozen public-data movement endpoint:
[
y=log(	ext{flight time}).
]

Structural support was defined before identity outcome:
- bats 1, 3 and 4 retain all five source noise conditions;
- bat 2 fails full high-noise support, consistent with the source study's published support limitation.

For every bat × noise level:
- equal-day summary;
- remove shared noise-condition mean;
- predict each current condition from that bat's other four conditions;
- compare with other bats' cross-condition histories.

### Result

- A_flighttime = **+0.377542**
- exact p = **0.00077160**
- exact assignments = **1296**
- extreme assignments = **1**
- positive bats = **3/3**

Individual mean advantages:
- bat 1 = **+0.461850**
- bat 3 = **+0.195650**
- bat 4 = **+0.475125**

Condition mean advantages:
- no noise / 20 dB = **+0.470269**
- 64 dB = **+0.408186**
- 74 dB = **+0.332180**
- 84 dB = **+0.343681**
- 94 dB = **+0.333394**

Thus every tested masking level contributes a positive mean advantage.

The observed identity correspondence is the unique most extreme mapping in the frozen exact null:
[
1/1296.
]

### Evidence label

**CONTROLLED_SMALL_N_MOVEMENT_SUPPORT**

This is deliberately not labelled broad replication because the biological sample is three complete bats.

---

## 3. What the two experiments jointly establish

The two sources differ in:
- species;
- laboratory;
- sensory manipulation;
- movement endpoint;
- statistical architecture.

Yet both support the same bounded statement:

[
oxed{
	ext{strong current sensory/context perturbation}

otRightarrow
	ext{erasure of all individual movement organization}
}
]

In *Pipistrellus*:
- individual angle-of-attack bias persists across masker manipulation.

In *Myotis*:
- relative individual landing-performance organization persists across a five-level masking gradient after the shared noise response is removed.

Therefore the repeatable individual signal is not adequately described as one context-fixed expressed value.

---

## 4. Storage-versus-expression interpretation

The evidence is consistent with:

[
x_{i,e}
=
mathcal{R}(E_e,	heta_i,u_{i,e}),
]

where:
- (E_e) is current sensory/task context;
- (	heta_i) is persistent personal organization;
- (u_{i,e}) contains unresolved individual × context realization.

The experiments manipulate (E_e).

They show that changing (E_e) can shift behavior while relative information about biological identity remains.

This is evidence for **storage-expression separation**.

It does not reveal the storage substrate.

---

## 5. Small-N boundary

The Myotis result is combinatorially strong but biologically small.

Do not confuse:
- exact null resolution: 1296 legal cross-condition label assignments;
with:
- population replication: only 3 complete biological bats.

The correct interpretation is:

> exceptionally consistent within-experiment identity correspondence across five controlled noise contexts in three bats.

Not:

> population-wide universal Myotis personality.

---

## 6. Relation to the auditory-midbrain public programme

A third independent public experiment is frozen but not yet numerically disposed:

Diebold/Lawlor et al. 2024, *Eptesicus fuscus*.

Public audio layer:
- four DREADDs bats;
- saline vs reversible ligand-induced auditory-midbrain perturbation;
- frozen four-dimensional vocal-policy primary;
- 4! exact identity mapping;
- structural gate PASS.

If supported, it would extend the same principle from:
- external sensory masking / current-context manipulation

to:
- reversible central auditory perturbation.

It would not imply a common carrier across movement and vocal domains.

---

## 7. What is now stronger than ordinary repeatability

The current public-data evidence is no longer merely:

> individuals differ repeatedly.

Instead:

> **experimentally imposed context changes can move the population-level behavioral state without necessarily destroying the relative organization that identifies individuals.**

That is the current strongest causal maintenance result available without collecting new data.

---

## 8. What remains unresolved

Public perturbation data do not yet identify:
- whether the persistent organization is learned or intrinsic;
- its neural storage location;
- biomechanics versus memory fractions;
- whether the same latent state spans species or behavioral domains;
- whether it explains wild vertical individuality;
- why individual specialization initially forms.

The direct causal formation arrow:

[
	ext{feasible solution opportunity}
ightarrow
	ext{formation of specialization}
]

remains untested by the current public archive universe.
