# Rhino personal theta–sigma model — authoritative result v1

## Execution

- workflow run: **37638712396**
- head SHA: `c91e3c43a0001a82026fdda0600893161b8ae021`
- conclusion: **success**
- artifact: **11491273127**

## Result

25 held-out bat × environment targets from five *Rhinolophus nippon* individuals.

Primary held-out probabilistic comparison:

[
G = log p(	heta_i,sigma_i)-log p(	heta_i,sigma_{common})
]

aggregated equal target environment within bat, then equal bat.

Observed:

[
G=-0.0782.
]

Bat means:
- A: -0.0650
- B: -0.5020
- C: +0.1774
- D: +0.4499
- E: -0.4514

Positive bats:
**2/5**.

Bat-cluster bootstrap 95% CI:

[
[-0.3944,+0.2379].
]

Verdict:
**THETA_ONLY_NO_PERSONAL_SIGMA_GAIN**.

Secondary descriptive Spearman correlation between training personal SD and held-out absolute deviation:

[
ho=+0.3223.
]

## Interpretation

The obvious between-environment spread differences among bats do not behave like a reliably estimable personal noise-scale parameter.

Therefore the next model should not be:

[
y_{ie}=	heta_i+sigma_i z_{ie}
]

as the main explanation.

The remaining deviations are more consistent with structured individual × environment terms,

[
h_{ie},
]

or with data limitations, rather than a single individual-specific heteroscedasticity parameter.

This sharpens the current model to:

[
y_{ie}=	heta_i+h_{ie}+epsilon.
]

The next diagnostic should ask whether (h_{ie}) itself has low-rank structure.
