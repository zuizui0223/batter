# Early-experience trait reallocation decomposition v1

## Status

**POST-PRIMARY DESCRIPTIVE DECOMPOSITION. NO P-VALUES.**

Parent:
- `PRIMARY_CONTRACT_V1.md`
- `PRIMARY_RESULT_V1.md`
- `POST_RESULT_UPDATE_V1.md`

The frozen randomized primary found:

- (D=V_{enriched}-V_{impoverished}=+0.734699);
- one-sided randomization (p=0.167785);
- verdict = `UNSUPPORTED_INDIVIDUALIZATION`.

This decomposition cannot alter that verdict.

## Question

The frozen multivariate D is additive across the three standardized traits.

Therefore ask descriptively:

> **Is the positive but unsupported total D aligned across Boldness / Exploration / Activity, or is it produced by opposing trait-specific changes in individual differentiation?**

## Frozen decomposition

Use exactly the primary:
- Season-2 n=29 cohort;
- pooled pre-treatment Trial 1–2 scaling;
- baseline = mean Trials 1–2;
- change = Trial 3 − baseline;
- treatment-group mean change removal.

For trait (k):

[
V_{E,k}
=
operatorname{mean}_{iin enriched} r_{ik}^2
]

[
V_{I,k}
=
operatorname{mean}_{iin impoverished} r_{ik}^2
]

[
D_k=V_{E,k}-V_{I,k}.
]

By construction:

[
sum_{k=1}^{3}D_k=D.
]

The implementation must assert equality to numerical tolerance.

## Outputs

Report all three traits:
- V enriched;
- V impoverished;
- D_k;
- sign.

Also report:
- positive contribution sum;
- negative contribution sum;
- total absolute contribution;
- cancellation ratio

[
C=1-rac{|D|}{sum|D_k|}.
]

No p-values.

## Boundary

This cannot establish a trait-specific causal treatment effect.

Do not:
- attach trait-wise randomization p-values;
- promote one trait after seeing the decomposition;
- redefine the primary;
- use Trial 4/5;
- select outdoor survivors.

The only purpose is to localize whether the frozen multivariate total reflects aligned versus opposing trait contributions.
