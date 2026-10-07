# Rhino context-sensitivity parameter diagnostic v1

## Status

**POST-PRIMARY MATHEMATICAL-STRUCTURE DIAGNOSTIC. NOT CONFIRMATORY.**

Frozen after:
- the portable scalar theta was supported and shown to converge;
- descriptive between-environment SD differs strongly among bats;
- theta-context decomposition showed large context-specific gain for some individuals and little/negative gain for others;
- no held-out predictive test of an individual-specific context-sensitivity scale has been calculated.

## Question

Can individual context sensitivity itself be represented by a second finite personal parameter?

Use:

[
y_{i,e}=	heta_i+sigma_i u_{i,e},
]

where:
- (y_{i,e}) is the bat × environment FlightIntensity centroid;
- (	heta_i) is the individual's portable location parameter;
- (sigma_i>0) is a personal amplitude of environment-to-environment expression;
- (u_{i,e}) is a zero-mean unit-scale context realization.

The question is not whether (u_{i,e}) can be predicted. It is whether its **amplitude** is stable enough to estimate as (sigma_i).

## Data

Use exactly the authoritative bat × environment FlightIntensity centroids from the 45 *Rhinolophus nippon* trajectories.

All five bats A–E have at least four observed environments.

## Held-out target

For every observed bat × environment centroid (y_{i,e}):

1. remove environment e from the focal bat's history;
2. require >=3 remaining focal environments;
3. estimate:
   [
   hat	heta_{i,-e}=mean(y_{i,e'}), quad e'
eq e
   ]
4. estimate personal scale:
   [
   hatsigma_{i,-e}=SD(y_{i,e'}), quad e'
eq e.
   ]

## Common-scale baseline

For the same target environment e:

- for each bat j, compute its non-target-environment mean using all observed environments other than e;
- collect every training residual
  (y_{j,e'}-hat	heta_{j,-e})
  for e' != e;
- pool those residuals across bats with >=3 training environments;
- calculate one pooled sample SD:
  (hatsigma_{common,-e}).

Both models use the **same focal theta estimate**. They differ only in residual scale.

## Predictive score

Use Gaussian held-out log score with mean-estimation variance correction:

[
V_{personal}
=
hatsigma_{i,-e}^2(1+1/n_i)
]

[
V_{common}
=
hatsigma_{common,-e}^2(1+1/n_i)
]

where n_i is the number of focal training environments.

For target y:

[
ell(y|mu,V)
=
-rac12[log(2pi V)+(y-mu)^2/V].
]

Target gain:

[
G_{sigma,i,e}
=
ell_{personal}-ell_{common}.
]

Positive means knowing the focal bat's personal context-sensitivity amplitude improves prediction over a common residual scale.

No variance floor is allowed. Stop if a required variance is zero/nonfinite.

## Aggregation

1. equal target environments within biological bat;
2. equal bats.

Report:
- programme G_sigma;
- individual bat means;
- positive bats;
- target-level scores.

## Exact individual-scale null

For every source bat s and target environment e, precompute:

[
hatsigma_{s,-e}
]

using source bat observations excluding e, whether or not s itself has a target in e.

Require >=3 source observations after exclusion.

Enumerate all 5! = 120 global permutations assigning the five complete sigma profiles to target bat labels.

For every permutation:
- theta predictions remain attached to the true focal bat;
- target outcomes remain attached to the true focal bat;
- common scale remains unchanged;
- only the correspondence between bat identity and personal sigma profile is broken.

Exact one-sided p:

[
p = #(G_{perm}ge G_{obs})/120.
]

Identity permutation is included.

## Support rule

Call personal context-sensitivity supported only if:
- G_sigma > 0;
- exact p <= 0.05;
- >=4/5 bats have positive mean G_sigma.

## Secondary descriptors

Report full-data:
- theta_i;
- sigma_i = SD across all observed environment centroids;
- coefficient of variation is **not** used because theta can cross zero;
- ordering of sigma high to low.

## Interpretation

### Supported

A finite two-parameter personal description becomes plausible:

[
(	heta_i,sigma_i)
]

where theta is portable operating position and sigma is stable context sensitivity.

This does not predict which direction a new environment will move the bat; it predicts how strongly that individual tends to deviate.

### Unsupported

The observed differences in between-environment SD are not sufficiently portable to act as a second personal parameter. Context dependence then remains in unresolved (h_{i,e}) rather than a stable individual amplitude.

## Claim ceiling

Even support does not establish:
- Gaussian context effects;
- a complete two-parameter law;
- known environment drivers;
- lifetime stability of sigma;
- universality beyond this experimental system.

The test asks only whether a personal residual amplitude adds held-out predictive information.
