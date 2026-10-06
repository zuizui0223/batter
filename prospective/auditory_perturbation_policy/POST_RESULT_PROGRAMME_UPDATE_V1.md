# Auditory perturbation post-result programme update v1

## Status

**FROZEN PRIMARY SUPPORTED. SAME-SOURCE IDENTITY SEARCH CLOSED.**

Source:
Diebold, Lawlor et al. (2024), Current Biology.
Public archive: Zenodo `10.5281/zenodo.13857870`.

Parent preregistration:
- `ACOUSTIC_POLICY_PRIMARY_V1.md`
- `INTERPRETATION_LEDGER_V1.md`
- `PROGRAMME_UPDATE_CONTRACT_V1.md`

## Frozen result

Four DREADDs behavioral bats:
- jane;
- bea;
- jason;
- stella.

After source-native `trialtype < 4` filtering and treatment × trialtype pooled mean residualization, the frozen 4-D vocal vector was:

- mean call duration;
- mean bandwidth;
- mean inter-pulse interval;
- call rate.

Saline-to-Ligand identity retention:

- K = **+1.004452**;
- positive individual advantages = **4/4**;
- exact identity permutations = **24**;
- observed true same-bat mapping rank = **1/24**;
- exact one-sided p = **1/24 = 0.041667**;
- verdict = **SUPPORTED**.

Individual advantages:
- jane: **+0.826821**;
- bea: **+1.411613**;
- jason: **+0.119224**;
- stella: **+1.660151**.

## Exact-resolution interpretation

With four biological individuals, 1/24 is the smallest attainable conventional exact one-sided p-value.

Therefore the observed same-individual mapping achieved the strongest rank-based result available under the frozen design.

This is strong within-archive evidence, but it is not high-powered population inference.

The appropriate statement is:

> **Under a reversible central auditory perturbation, the true same-bat Saline-to-Ligand mapping remained the single most identity-consistent mapping among all 24 possible identity assignments in these four bats.**

## Biological interpretation

The perturbation changes central auditory processing and alters common vocal expression.

Yet the multivariate vocal state retains enough individual-specific organization that every Ligand bat remains closer, in the frozen identity sense, to its own Saline organization than expected under alternative identity mappings.

Thus:

[
oxed{
	ext{central sensory perturbation}

otRightarrow
	ext{complete erasure of individual organization}
}
]

This independently supports a storage-versus-expression distinction.

A personal behavioral organization can persist while the common operating state is experimentally shifted.

## Relation to the existing masker result

The earlier *Pipistrellus kuhlii* masker experiment showed retained individual movement bias across an external sensory perturbation.

The present *Eptesicus fuscus* experiment shows retained individual vocal organization across reversible central auditory perturbation.

The systems differ in:
- species;
- intervention;
- behavioral endpoint;
- representation.

Therefore do not call them the same carrier.

The supported cross-system statement is:

> **Across independent bat systems, more than one kind of sensory perturbation can alter common behavioral expression without erasing all individual-specific organization.**

## Relation to Rhinolophus portability

The *Rhinolophus* programme shows that personal movement information can transfer across obstacle contexts.

The two perturbation datasets now add experimental leverage:

1. current context can change;
2. expressed behavior can shift;
3. individual-specific organization can remain detectable.

The strongest empirical hierarchy is therefore:

[
oxed{
	ext{persistent personal organization}
ightarrow
	ext{context-dependent behavioral expression}
}
]

with direct experimental support for non-erasure under perturbation.

## Feature localization boundary

Descriptive component K values:
- duration: +0.789331;
- bandwidth: +0.536278;
- IPI: +0.173420;
- call rate: +0.156400.

These are descriptive only.

No component-wise p-values are authorized.

Do not promote duration or bandwidth into a new confirmatory carrier.

## Small-sample boundary

n=4 biological individuals.

Therefore:
- effect prevalence in the wider species is not estimated precisely;
- p=0.04167 reflects exact mapping rank, not large-sample precision;
- all four individuals being positive is biologically useful but does not remove the small-n limitation.

## Same-source ceiling

**STOP_NEW_AUDITORY_IDENTITY_AXES.**

Do not:
- add Baseline;
- add sham bats;
- switch to 3-D trajectory identity;
- run one-feature confirmatory tests;
- remove jason or stella;
- fit PCA;
- learn feature weights;
- change trialtype filter;
- treat trials/calls as biological replicates.

The public trajectory layer has only three DREADDs bats and is structurally incapable of a conventional exact identity primary.

## What remains unresolved

This result does not identify:
- where the persistent individual organization is stored;
- whether it is intrinsic, learned, or mixed;
- whether vocal and movement individuality share a common latent state;
- whether the same structure controls wild niche individuality;
- how personal organization originally forms.

## Next public-data priority

The next public source must add a **different causal axis**, not another proof that identity survives perturbation.

Priority:
1. Aharon et al. 2017 path-integration / navigation-cue manipulation, if public structure can be recovered;
2. Ma et al. 2025 only as a lower-priority manipulation-localization source.

Aharon is valuable only if it tests navigation-policy persistence across a different information manipulation.

Do not open another acoustic feature search in the current Zenodo archive.
