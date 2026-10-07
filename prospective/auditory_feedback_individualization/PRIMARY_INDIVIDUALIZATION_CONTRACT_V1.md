# Auditory-feedback adult vocal individualization primary v1

## Status

**FROZEN BEFORE THIS PROGRAMME OPENS PAF ACOUSTIC NUMERIC VALUES.**

Source:
Elie et al. (2024), Current Biology.
Public acoustic measurements:
Mendeley Data `10.17632/h5ff9vv5pc.1`.

## Design

The source paper states that the ten pups were randomly assigned shortly after birth to:

- kanamycin / deafened: n=5;
- saline / hearing control: n=5.

Observed sex balance in each treatment:
- 3 females;
- 2 males.

Adult vocalizations were recorded years later in a shared social environment.

## Question

> **Does access to auditory feedback during development change the amount of stable between-individual vocal differentiation expressed in adulthood?**

This is not a test of the treatment mean.

It is a test of adult **individualization** after randomized developmental sensory history.

## Frozen source representation

Use exactly the source table:

`PAF_AllBatsData.mat : PAF_Tbl`.

Use exactly source acoustic-feature columns **5:32**, all 28 features.

No feature selection.

No PCA primary.

No UMAP primary.

No use of published per-feature significance to choose dimensions.

The source code already publicly reports treatment analyses for individual features; this programme therefore fixes the complete 28-feature representation to prevent outcome-driven selection.

## Repertoire scope

Use **all good-microphone-quality vocalizations in PAF_Tbl**, matching the source's all-repertoire analysis.

Do not condition the primary on acoustic group/call class.

Reason:
the biological target is whole adult vocal organization, including any individual differences in repertoire composition expressed through the common 28-feature representation.

Call-class analyses, if any, are downstream descriptive only.

## Bat-level unit

The biological unit is the bat.

For each bat i and acoustic feature k:

[
m_{ik}
=
operatorname{mean}
(x_{call,k})
]

over all finite source calls from that bat.

Frozen support:
- each bat must have >=100 finite calls for every one of the 28 features;
- otherwise return `STOP_28D_BAT_CENTROID_SUPPORT`;
- no feature or bat deletion.

## Treatment-blind feature scaling

Construct the 10 × 28 bat-centroid matrix M.

For every feature k:
- calculate mean across the 10 bat centroids;
- calculate sample SD across the 10 bat centroids, ddof=1;
- require finite SD > 0;
- z-standardize the ten bat centroids.

No treatment or sex label enters scaling.

Thus every bat has one 28-D whole-repertoire adult vocal centroid:

[
z_i.
]

## Remove shared sex × treatment state

The target is individuality beyond:
- sexual dimorphism;
- the common hearing/deaf treatment shift.

For each observed or permuted assignment, within every sex × treatment cell:

[
r_i
=
z_i
-
ar z_{sex(i),treatment(i)}.
]

Cell sizes under the observed conditioned design are:
- female hearing = 3;
- female deaf = 3;
- male hearing = 2;
- male deaf = 2.

## Treatment-specific individualization

For treatment g:

[
V_g
=
rac{1}{5}
sum_{i:g(i)=g}
||r_i||_2^2.
]

Primary signed contrast:

[
D
=
V_{hearing}
-
V_{deaf}.
]

Interpretation:
- D > 0: hearing-development animals are more differentiated;
- D < 0: deafened animals are more differentiated.

## Exact null

Because treatment was randomized before the adult outcomes, use a conditional exact randomization preserving the observed sex balance.

Among six females:
- choose 3 as hearing.

Among four males:
- choose 2 as hearing.

Exact assignment space:

[
inom{6}{3}inom{4}{2}
=
120.
]

For every assignment:
1. preserve the fixed 10 × 28 treatment-blind centroid matrix;
2. relabel hearing/deaf according to the legal assignment;
3. recompute sex × treatment means;
4. recompute residuals;
5. recompute V_hearing, V_deaf and D.

Two-sided exact p:

[
p
=
rac{#(|D_{perm}|ge |D_{obs}|)}{120}.
]

Because complementary assignments reverse the sign of D, the minimum attainable two-sided exact p is expected to be at least 2/120 = 0.01667.

## Support rule

Support for a developmental-feedback effect on amount of individuality requires:

- two-sided exact p <= 0.05.

Direction is determined only after the two-sided gate:
- hearing-more-differentiated if D > 0;
- deaf-more-differentiated if D < 0.

No directional rescue after opening.

## Descriptive robustness

Report without additional p-values:
- V_hearing;
- V_deaf;
- D;
- female-only signed D;
- male-only signed D;
- per-bat squared residual norm;
- finite-call support per bat × feature.

Sex-specific values do not replace the primary.

## Hard prohibitions

After acoustic numeric values are opened do not:
- select significant source features;
- remove features;
- remove bats;
- switch to PCA/UMAP;
- choose one acoustic group;
- change whole-repertoire scope;
- change centroid aggregation;
- use calls as independent biological replicates;
- change the two-sided null to one-sided;
- pool sex without the frozen sex × treatment residualization.

## Claim map

### Exact p <= 0.05, D > 0

Allowed:

> **Randomized developmental access to auditory feedback increased the amount of stable adult individual vocal differentiation in the frozen whole-repertoire acoustic representation.**

### Exact p <= 0.05, D < 0

Allowed:

> **Randomized developmental auditory deprivation increased adult between-individual vocal differentiation, consistent with feedback normally constraining/idiosyncrasy in the mature vocal phenotype.**

Do not reinterpret this as "deafening improves individuality."

### p > 0.05

Allowed:

> **Auditory feedback is causally required for parts of normal vocal learning, but this experiment does not show that it changes the total amount of adult individual vocal differentiation in the frozen 28-feature whole-repertoire phenotype.**

## Claim ceiling

Even if supported, this concerns:
- adult vocal phenotype;
- one randomized developmental sensory manipulation;
- n=10 bats.

It does not establish:
- movement-policy formation;
- a universal individual-specialization mechanism;
- wild niche individuality;
- neural storage location.
