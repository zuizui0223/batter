# Aharon Figure-1 cross-condition identity primary v1

## Status

**IMPLEMENTATION RECEIPT FOR THE ALREADY-FROZEN CROSS-CONDITION CONTRACT.**

Authoritative inference:
`AHARON_CROSS_CONDITION_IDENTITY_CONTRACT_V1.md`.

This file changes no inferential choice.

## Frozen source

Figure 1.

Bats:
- 500
- 503
- 505
- 510

Conditions in frozen order:
- con
- 75
- 300

All 12 matrices passed:
- shape gate;
- >=5 finite bilateral trials.

Numeric opening additionally requires:
`AHARON_FIGURE1_ZERO_GATE_V1.json = PASS_NO_ZERO_SENTINEL`.

## Frozen trial representation

For each valid trial column:

- right = finite odd-source-row entries;
- left = finite even-source-row entries;
- q = (median(right), median(left)).

Bat × condition state:
equal-trial mean q.

Condition mean is removed across the four bats.

## Frozen held-out identity statistic

For every bat × target condition:

- target = condition-residual state in target condition;
- own history = equal mean of that bat's residual states in the other two conditions;
- donor history = same construction for each other bat;
- K_ic = mean donor distance - own distance.

Programme K:
equal mean across conditions within bat, then equal mean across four bats.

## Exact null

Anchor condition:
`con`.

Independently permute complete biological labels in:
- 75;
- 300.

Exact null size:

[
(4!)^2=576.
]

One-sided exact p:
fraction of null K >= observed K.

Minimum exact p:
[
1/576=0.00173611.
]

## Support

Supported if:
- K > 0;
- p <= 0.05.

Also report:
- four bat-level K means;
- three condition-level K means;
- positive bat fraction;
- leave-one-bat-out K.

No alternate gate.

## No rescue

After opening do not:
- select only con vs 75;
- select only con vs 300;
- switch Figure;
- switch endpoint;
- drop bat 500/503/505/510;
- change median to mean;
- rescale by condition;
- treat trial columns as biological replicates.
