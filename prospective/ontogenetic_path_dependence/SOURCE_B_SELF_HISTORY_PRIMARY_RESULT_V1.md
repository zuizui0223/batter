# Source B first-flight self-history primary result v1

## Status

**PRIMARY FORMATION RULE: FAIL.**

**PREDECLARED LATE-HISTORY SECONDARY: STRONGLY SUPPORTED.**

Authoritative workflow:
- run: **37176511358**
- job: **111360116102**
- artifact: **11293422789**
- artifact ZIP SHA256: `ccf37a42fee73d978609a2d2848c71d67cf07fb9fd4a96650d714b673b52e7e4`

Parent contracts:
- `SOURCE_B_SELF_HISTORY_ESTIMATOR_CONTRACT_V1.md`
- `SOURCE_B_PERMUTATION_ELIGIBILITY_CLARIFICATION_V1.md`
- `SOURCE_B_MATLAB_STANDARDIZED_COORDINATE_BRIDGE_V2.md`
- `SOURCE_B_MATLAB_COORDINATE_SUPPORT_RESULT_V1.md`

## Dataset actually tested

Primary-evaluable juveniles:
**14**

All 14 are from the structurally eligible 2017–2018 first-flight cohort.

Target events:
**252** = 14 juveniles × target valid-day ordinals 3–20.

The 2016–2017 cohort was structurally ineligible under the frozen >=20-valid-day target rule and contributed no primary target.

## Primary endpoint: does self-history advantage increase with experience?

For each juvenile:

`B_i = Spearman rho(prior valid-day count, own-history predictive advantage R)`.

Programme statistic:

`B = equal-individual mean B_i`.

Frozen null:
9,999 whole-history identity permutations within cohort.

Seed:
`20261004021`.

### Result

- `B_obs = +0.16733`
- null mean = **-0.06936**
- calibrated excess = **+0.23669**
- null 95% interval = **[-0.25845, +0.12871]**
- one-sided permutation p = **0.0102**

Thus the programme-level mean experience slope exceeds the identity-exchangeability null.

However, the predeclared individual-consistency rule fails:

- positive `B_i`: **8 / 14 = 57.1%**
- required: **>=10 / 14 = 70%**

Therefore the frozen primary verdict is:

> **FAIL_PRIMARY_FORMATION_RULE**

Do not relabel the p=0.0102 group-average contrast as primary support.

## Why the primary failed

The primary hypothesis was deliberately stronger than “own history matters.”

It required a common ontogenetic pattern:

> as independent experience accumulates, personal-history advantage should increase in a directionally consistent majority of juveniles.

The mean tendency is positive and permutation-supported, but six juveniles have non-positive monotonic experience slopes.

The simple model of broadly shared, gradual, monotonic personal-route canalization is therefore **not supported under the frozen rule**.

## Predeclared secondary: late personal-history advantage

For target ordinals 11–20:

`L_i = mean daily R`.

Programme mean:

- `L_obs = +112.5554`
- null mean = **-0.1814**
- calibrated excess = **+112.7368**
- null 95% interval = **[-27.9659, +49.9576]**
- one-sided permutation p = **0.0001**

Descriptively:
- **12 / 14** juveniles have positive late `L_i`;
- median individual late advantage = **+36.04** source-coordinate distance units.

The two non-positive late individuals are:
- Eli: approximately -0.03;
- Fima: approximately -18.69.

This secondary was frozen before outcome opening and is not a rescue of the failed primary.

Allowed conclusion:

> By later early ontogeny, a juvenile's own recent movement history is substantially more informative about its next spatial use than experience-matched conspecific histories.

## Descriptive ontogenetic curve

The predeclared descriptive equal-individual mean R is already positive at the earliest estimable target ordinal:

- day 3: +17.15
- day 4: +41.81
- day 5: +47.75

It remains positive at every target ordinal 3–20, but is non-monotonic.

This is descriptive only.

It suggests a new possibility:

> personal history may become informative very rapidly and then fluctuate or refine idiosyncratically, rather than rising through one common gradual trajectory.

That hypothesis was generated after the outcome and requires an independent test.

## Individual B_i heterogeneity

Positive:
- Anka +0.166
- Eli +0.290
- Eva +0.259
- Nadav +0.913
- Odelia +0.245
- Shem_Tov +0.647
- Tishray +0.676
- Tzedi +0.564

Non-positive:
- Fima -0.309
- K -0.383
- Mazi -0.121
- Nature -0.486
- Nazir -0.071
- V -0.049

This heterogeneity is retained rather than filtered.

## Ecological interpretation

The data support a narrower maintenance statement than the original formation hypothesis.

They show:
1. **late personal history carries strong individual spatial information**;
2. that information is not well described by a universal monotonic build-up across the first 20 valid flight days;
3. individuals differ markedly in how self-history advantage changes through ontogeny.

Combined with the JAE result, the current evidence is consistent with:

> individual specialization being maintained by reuse of personal spatial history without requiring exclusive spatial niches.

But it does **not** establish a universal gradual reinforcement process.

Potential architectures still include:
- rapid early path dependence before target day 3;
- individual-specific learning/refinement timescales;
- stable performance constraints plus experience;
- destination/resource fidelity combined with personal history.

## Stop rules

Do not:
- lower the 70% primary consistency rule;
- drop negative juveniles;
- choose a post-hoc breakpoint;
- redefine “early” or “late” to make the primary pass;
- replace Spearman B_i with another slope metric;
- shorten the target horizon;
- add the 2016 cohort by threshold relaxation;
- reinterpret the secondary as the primary.

## JAE firewall

No change to JAE v0.4.0.
