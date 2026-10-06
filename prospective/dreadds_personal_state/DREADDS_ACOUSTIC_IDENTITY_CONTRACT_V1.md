# DREADDs cross-treatment personal acoustic-state contract v1

## Status

**FROZEN BEFORE THE NEW INDIVIDUAL-MATCHING OUTCOME IS OPENED.**

Parent:
DREADDS_STRUCTURE_AUDIT_CONTRACT_V1.md

## Biological question

Does individual acoustic-control organization remain identifiable after reversible suppression of excitatory inferior-colliculus neurons?

This is stronger than a passive repeatability test because the current central sensory-processing state is experimentally altered within the same animals.

It is an acoustic/sensorimotor-control endpoint, not a direct movement-policy endpoint.

## Biological sample

Use exactly the four public audio bats:

- jane
- bea
- jason
- stella

All four must pass the frozen structural gate.

No effect-dependent subset.

## Source-native trial filter

Use only trials satisfying:

trialtype < 4

exactly as in the public analysis code.

Treatments:
- 1 = saline
- 2 = ligand

## Frozen five-dimensional trial vector

For every structurally usable trial:

### F1 — mean call duration

mean of callduration for that trial.

### F2 — mean call bandwidth

mean of callbandwidth for that trial.

### F3 — mean IPI

Take first differences of onsetcalltrial within the trial and use their mean.

Require at least two finite call onset times.

### F4 — call rate

number of calls in onsetcalltrial divided by lengthtrialadjust.

Require positive finite lengthtrialadjust.

### F5 — SSG proportion

sum of sg_type for that trial divided by number of calls in onsetcalltrial.

No SSG-rate substitute.

No source feature may be dropped after outcome opening.

## Bat × treatment summary

For each bat and treatment, calculate the equal-trial mean of each feature.

This yields:

x_i,saline in R^5
x_i,ligand in R^5.

No session weighting or support weighting.

## Remove shared treatment shift

For each treatment and feature independently:

r_i,t,k =
x_i,t,k - mean_i(x_i,t,k).

This removes the population-level saline/ligand shift and retains relative individual organization.

## Feature scaling

For each feature k:

1. pool the eight centered values
   {r_i,saline,k, r_i,ligand,k};
2. compute one sample SD s_k with ddof=1;
3. require finite s_k > 0;
4. define z_i,t,k = r_i,t,k / s_k.

This scaling is identity-label invariant and is fixed before permutation.

If any feature SD is zero/nonfinite:
**PRIMARY STRUCTURAL STOP.**

No PCA, fitted weights, feature selection, or treatment-specific scaling.

## Cross-treatment identity statistic

For each saline bat i:

Own ligand distance:

d_self(i) =
Euclidean distance between z_i,saline and z_i,ligand.

Mean donor ligand distance:

d_other(i) =
mean over j != i of Euclidean distance between
z_i,saline and z_j,ligand.

Individual advantage:

A_i = d_other(i) - d_self(i).

Programme statistic:

A_DREADD = mean_i A_i.

Positive means the ligand-state acoustic-control vector is closer to the same bat's saline-state vector than to other bats' ligand-state vectors.

## Exact null

Hold saline labels fixed.

Enumerate every permutation of the four bat labels attached to the ligand vectors.

Exact assignment count:

4! = 24.

For each mapping recompute A_DREADD.

One-sided exact p:

p =
number of null statistics >= observed
divided by 24.

No +1 correction because the full randomization space is enumerated.

## Severe resolution boundary

With only 24 assignments:

minimum possible exact one-sided p = 1/24 = 0.0416667.

Thus support at p<=0.05 occurs only if the observed mapping is the uniquely most identity-consistent mapping in the complete permutation space.

This severe gate is intentional.

Do not replace it with:
- asymptotic mixed models;
- trial-level pseudoreplication;
- independent feature p-values;
- a feature subset selected after inspection.

## Confirmatory support

Support requires:
- A_DREADD > 0;
- exact p <= 0.05.

Report:
- A_DREADD;
- exact rank among 24 mappings;
- four individual A_i values;
- number of positive A_i;
- observed self-distance and mean-donor distance per bat.

## Secondary descriptive trajectory layer

For the three public trajectory bats only:
- report source-native saline versus ligand changes already represented in the public code/paper;
- do not generate a confirmatory identity p-value;
- do not count n=3 trajectory patterns as an independent replication.

## Claim ceiling

A positive primary supports:

> relative individual acoustic-control organization survives a reversible disruption of central auditory processing.

It does not establish:
- a stable individual movement trajectory under IC silencing;
- origin of the personal state;
- a neural locus storing individual specialization;
- equivalence to Rhino I/M;
- the wild vertical-individuality bridge.

A negative primary is also informative because the exact test is extremely discrete and n=4; distinguish failure of identity preservation from limited inferential resolution.
