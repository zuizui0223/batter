# Auditory-feedback adult individualization post-result update v1

## Status

**FROZEN RANDOMIZED PRIMARY COMPLETE — NO DIFFERENCE IN AMOUNT OF INDIVIDUALIZATION.**

Source:
Elie et al. (2024), Current Biology.
Public archive:
Mendeley Data `10.17632/h5ff9vv5pc.1`.

## Design

Ten pups were randomly assigned shortly after birth:

- hearing / saline control: n=5;
- deafened / kanamycin: n=5.

Each treatment:
- 3 females;
- 2 males.

Adult vocal phenotype was measured 3–4 years later after long-term shared social housing.

Frozen source representation:
- all **28,091** good-microphone-quality vocalizations;
- exactly **28** source acoustic features;
- exactly **10** biological bats;
- whole repertoire;
- bat as biological unit.

## Frozen primary

For each bat:
- calculate the 28-D whole-repertoire feature centroid;
- require >=100 finite calls per bat × feature;
- scale each feature treatment-blind across the ten bat centroids;
- remove the sex × treatment common centroid;
- calculate squared residual individual distance;
- compare average residual dispersion between hearing and deaf groups.

Observed:

- global minimum finite calls per bat × feature = **1,037**;
- V_hearing = **15.766760**;
- V_deaf = **17.192257**;
- D = V_hearing - V_deaf = **-1.425497**.

Conditional exact randomization:
- choose 3/6 females and 2/4 males as hearing;
- exact assignments = **120**;
- extreme |D| assignments = **86**;
- exact two-sided p = **0.716667**.

Verdict:

**NO_DIFFERENCE_IN_AMOUNT**

## Descriptive sex contrasts

- female D = **+2.238906**;
- male D = **-6.922102**.

These are descriptive only.

The opposite directions reinforce why no post-hoc sex-specific confirmatory rescue is authorized.

## Biological interpretation

The source study causally shows that auditory feedback is required for normal development of subsets of the adult vocal repertoire.

The new frozen analysis asks a different question:

> does that developmental sensory manipulation alter the **total amount of adult between-individual vocal differentiation**?

It does not detect such an effect.

Thus:

> **A developmental manipulation can substantially alter learned components of the adult phenotype without changing the overall amount of individuality in the whole-repertoire multivariate phenotype.**

This is not evidence that deafening has no behavioral consequence.

It separates:
- **what phenotype is expressed**
from
- **how much individuals differ from one another**.

## Relation to randomized enrichment

Independent randomized early-environment experiment:
Rachum et al. 2025.

There:
- D_enrichment = **+0.734699**;
- p = **0.167785**;
- no supported variance amplification.

The two experiments manipulate very different aspects of developmental experience:

1. broad environmental enrichment;
2. access to auditory feedback required for vocal learning.

Yet neither supports a change in the total amount of individual differentiation under its frozen multivariate phenotype.

Therefore the public-data formation evidence now supports a stronger boundary:

[
oxed{
	ext{developmental environment can change phenotype}

otRightarrow
	ext{change in total amount of individuality}
}
]

This is a replicated causal boundary across independent developmental manipulations.

## Why this matters

A simple ecological-opportunity model might expect richer or more informative experience to produce more individual differentiation.

The public experiments do not support that generic mapping.

The formation problem is therefore not:

> does more experience create more variance?

It is narrower:

> **how do individual-specific histories generate stable personal organization even when treatment-wide environmental effects do not predict the amount of between-individual differentiation?**

## Same-source ceiling

**STOP_NEW_WHOLE_REPERTOIRE_INDIVIDUALIZATION_AXES.**

Do not:
- select source-significant acoustic features;
- switch to PCA/UMAP;
- remove bats;
- split by sex for a new primary;
- choose an acoustic group to rescue;
- use calls as biological replicates;
- change the two-sided 120-assignment null.

Any acoustic-group analysis is exploratory only and cannot alter the primary verdict.

## Programme role

This is not a positive mechanism discovery for formation.

It is a strong causal boundary showing that:
- developmental auditory feedback matters for learned vocal structure;
- but the **amount of adult individuality** is not simply a function of that feedback.

Together with the maintenance results, this strengthens a formation/maintenance asymmetry:
- established individual organization is robust under current perturbation;
- environmental effects on developmental phenotype do not straightforwardly determine how much individuality exists.
