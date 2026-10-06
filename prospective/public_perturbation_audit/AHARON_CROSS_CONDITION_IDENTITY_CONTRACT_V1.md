# Aharon cross-condition navigation identity contract v1

## Status

**FROZEN BEFORE NUMERIC TURNING-POINT VALUES ARE OPENED.**

Parent:
- `AHARON_2017_STRUCTURE_AUDIT_CONTRACT_V1.md`
- `PUBLIC_BROWSER_DOWNLOAD_STRUCTURE_CONTRACT_V1.md`

Source:
Aharon, Sadot & Yovel 2017, Current Biology.
Public Mendeley dataset `f6mvhj5gj9` v3.

## Biological question

Does individual navigation organization persist across experimentally altered current navigation contexts?

The source paper manipulated current navigation information/conditions, including acoustic flow, starting position, wind and landmark-related structure. The public source stores turning-point matrices by bat and condition. cite omitted in repository record; see DOI 10.1016/j.cub.2017.10.012

This test does not ask which manipulation has the strongest identity.

It asks whether the same individual remains relatively self-similar across the full set of source-defined conditions within one structurally eligible experiment.

## Endpoint priority

Primary endpoint is fixed now:

> **turning-location organization**

Use variables matching source semantics:

`<bat>_YRLturns_together_<condition>`

The Mendeley description defines:
- numeric prefix = biological bat;
- suffix = condition;
- each column = one trial;
- odd rows = right turns;
- even rows = left turns.

Do not switch to slowing points or speed if turning identity fails.

Slowing/speed may be opened only under a separate future contract and cannot rescue this primary.

## Figure selection rule

Search Figure 1, then Figure 2, then Figure 3, then Figure 4.

Select the **first** figure satisfying all structural requirements:

1. turning-location variables are present;
2. >=2 source-defined condition suffixes;
3. >=4 biological bats are represented in **every** condition;
4. for every common bat × condition matrix:
   - rows >=2;
   - columns >=5;
5. a later finite-mask audit confirms >=5 valid trial columns per common bat × condition.

All structurally eligible source-defined conditions in the selected figure are included.

Do not:
- drop a difficult condition;
- select a later figure because it gives a stronger biological result;
- choose a subset of bats after numeric outcomes are seen.

If no figure passes:
**STOP_NO_STRUCTURALLY_IDENTIFIED_AHARON_PRIMARY.**

## Trial representation

For each matrix column (one trial):

- right-turn values = finite entries from odd-numbered source rows;
- left-turn values = finite entries from even-numbered source rows.

A trial is valid only if it contains:
- >=1 finite right-turn value;
- >=1 finite left-turn value.

Trial vector:

[
q_t=
(operatorname{median}(Right_t),operatorname{median}(Left_t)).
]

Median is frozen prospectively for robustness to a variable number of turns per trial.

No trajectory reconstruction, smoothing, turn filtering, PCA or outcome-dependent feature engineering.

## Bat × condition summary

For bat i in condition c:

[
m_{ic}
=
operatorname{mean}_{tin valid(i,c)} q_t.
]

Equal trial weighting.

Require >=5 valid trials.

## Condition-level shift removal

The experiment manipulates current context and may shift the whole population.

For each condition c, calculate the equal-bat mean:

[
ar m_c
=
rac{1}{n}sum_i m_{ic}.
]

Condition-residual personal organization:

[
r_{ic}=m_{ic}-ar m_c.
]

No condition-wise variance rescaling.

Thus the test asks whether each bat's **relative position within the population** persists across current-context manipulations.

## Leave-one-condition-out self-history test

For every target condition c and bat i:

Training self centroid from all other conditions:

[
s_{i,-c}
=
rac{1}{C-1}sum_{d
e c}r_{id}.
]

For donor bat j:

[
s_{j,-c}
=
rac{1}{C-1}sum_{d
e c}r_{jd}.
]

Self distance:

[
d_{self}=||r_{ic}-s_{i,-c}||_2.
]

Other-bat distance:

[
d_{other}
=
operatorname{mean}_{j
e i}
||r_{ic}-s_{j,-c}||_2.
]

Target advantage:

[
K_{ic}=d_{other}-d_{self}.
]

Aggregate:
1. equal target conditions within bat;
2. equal bats.

Programme statistic:

[
K=operatorname{mean}_ioperatorname{mean}_c K_{ic}.
]

Positive K means navigation organization under a held-out manipulated context is closer to the same bat's organization in other contexts than to other bats' histories.

## Null

Preserve:
- every numerical turning summary;
- every condition;
- every condition's bat-label multiset.

Fix biological labels in the first source-defined condition as the anchor.

Independently permute the complete bat labels in every other condition.

This breaks cross-condition individual correspondence while preserving all condition-specific distributions.

If:

[
(n!)^{C-1}le100000,
]

enumerate the full null.

Otherwise:
- use 99,999 deterministic Monte Carlo joint permutations;
- seed = `202610062143`;
- one-sided p = ((1+#nullge observed)/(N+1)).

## Primary support

Support requires:
- K > 0;
- one-sided p <= 0.05.

Also report:
- individual mean K_i;
- positive-individual fraction;
- leave-one-bat-out K;
- condition-specific mean K_c.

These are robustness/descriptive outputs, not alternative gates.

If deleting one bat reverses the sign of K:
label **SUPPORTED_BUT_FRAGILE_SMALL_N** if the primary p passes.

## Exact small-n boundary

At least four common bats are required.

With exactly:
- n=4, C=2: exact null size 24; minimum p = 1/24 = 0.0417;
- n<4, C=2: conventional p<=0.05 is unattainable.

No support threshold relaxation.

## Interpretation

A positive result may support:

> **Individual navigation organization persists across experimentally altered current navigation contexts after population-level condition shifts are removed.**

Together with the existing sensory-perturbation result, this would independently support separation between:
- persistent personal organization;
- context-dependent behavioral expression.

## Claim ceiling

Do not claim:
- personal history caused the individual organization;
- path integration itself is individual-specific in origin;
- biomechanics versus learning fractions;
- universal bat navigation individuality;
- equivalence to the frozen wild JAE carrier;
- fitness consequences.

This is a controlled-current-context persistence test, not an origin experiment.
