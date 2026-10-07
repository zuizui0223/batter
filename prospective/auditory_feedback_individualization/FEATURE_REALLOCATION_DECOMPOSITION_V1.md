# Auditory-feedback feature reallocation decomposition v1

## Status

**POST-PRIMARY DESCRIPTIVE MECHANISM DECOMPOSITION. NO P-VALUES.**

Parent:
- `PRIMARY_INDIVIDUALIZATION_CONTRACT_V1.md`
- `PRIMARY_RESULT_V1.md`
- `POST_RESULT_UPDATE_V1.md`

The frozen primary found no treatment effect on the **total** amount of adult whole-repertoire individual differentiation:

- (D=V_H-V_D=-1.425497);
- exact two-sided (p=0.716667).

This decomposition does not alter that verdict.

## Question

The primary total is a sum across 28 standardized acoustic dimensions.

Therefore:

> **Did developmental auditory feedback leave the total amount of individuality similar because individuality was redistributed across acoustic dimensions?**

This is a descriptive localization question.

## Frozen decomposition

Use exactly the same:
- 10 bats;
- 28 source acoustic features;
- whole repertoire;
- bat centroids;
- treatment-blind 10-bat feature scaling;
- observed sex × treatment residualization

as the frozen primary.

For feature (k):

[
V_{H,k}
=
operatorname{mean}_{iin H} r_{ik}^2
]

[
V_{D,k}
=
operatorname{mean}_{iin D} r_{ik}^2
]

and exact additive contribution:

[
D_k=V_{H,k}-V_{D,k}.
]

By construction:

[
sum_{k=1}^{28}D_k=D.
]

The implementation must assert equality to numerical tolerance.

## Outputs

Report all 28 features, without selection:

- (V_{H,k});
- (V_{D,k});
- (D_k);
- sign of (D_k);
- absolute contribution (|D_k|).

Also report:

[
P=sum_{D_k>0}D_k
]

[
N=sum_{D_k<0}D_k
]

and verify:

[
P+N=D.
]

Define a descriptive cancellation ratio:

[
C=
1-rac{|D|}{P+|N|}
]

when (P+|N|>0).

Interpretation:
- (Capprox0): most feature contributions point in the same net direction;
- (Capprox1): large positive and negative feature contributions cancel.

No threshold defines support.

## Ranking

A table may be sorted by (|D_k|) for readability **only after all 28 values are reported**.

Ranking does not create a new endpoint.

No top-feature p-values.

## Claim boundary

Allowed if cancellation is strong:

> **The absence of a total individualization effect coexists with substantial opposing changes across acoustic dimensions, consistent with redistribution of where individuality is expressed rather than simple gain/loss of individuality.**

Allowed if cancellation is weak:

> **The null total result is not hiding large opposing feature-level contributions.**

This decomposition cannot establish causal feature-specific effects.

Do not:
- test feature-wise p-values;
- select source-significant features;
- create a reduced-feature primary;
- change sex residualization;
- split acoustic groups to rescue the primary;
- reinterpret the total primary verdict.
