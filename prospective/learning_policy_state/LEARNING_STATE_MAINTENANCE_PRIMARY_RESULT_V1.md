# Learning-state maintenance primary result v1

## Status

**PASS — prospective personal-state maintenance primary supported.**

Branch:
`prospective/learning-policy-state-v1`

Source:
Yamada et al. 2020 raw-data release, Figshare `19102712`.

Authoritative workflow:
- run: `37251572797`
- workflow: `learning-state-maintenance-primary-v1`

Parent contract:
`LEARNING_STATE_MAINTENANCE_PRIMARY_CONTRACT_V1.md`

## Structural support

- evaluable subjects: **14**
- permeable/chain condition: **7**
- reflective/acrylic condition: **7**
- every subject: exactly trial 1 and trial 12
- no duplicated subject × trial rows

## Published learning change reproduced descriptively

These are descriptive source-validation quantities, not new inferential endpoints.

### Condition 1 — acoustically permeable / chain

Maximum flight speed:
- trial 1: **2.464 m/s**
- trial 12: **3.356 m/s**

Meandering width:
- trial 1: **533.2 mm**
- trial 12: **352.8 mm**

### Condition 2 — acoustically reflective / acrylic

Maximum flight speed:
- trial 1: **2.548 m/s**
- trial 12: **2.822 m/s**

Meandering width:
- trial 1: **498.0 mm**
- trial 12: **317.0 mm**

Thus there is substantial behavioural updating between first and twelfth exposure, especially in the permeable condition.

## Primary P1 — personal policy-state maintenance

Before identity comparison, both endpoints were standardized independently within each:

`condition × trial`

cell.

Therefore:
- the mean learning shift is removed;
- condition-specific scale is removed;
- the test asks only whether **relative individual policy position persists**.

Two-dimensional state:
- standardized maximum flight speed;
- standardized meandering width.

Observed personal-state advantage:

[
K_{policy}=0.67436
]

Individual direction:
- positive: **11/14**
- required by frozen rule: **10/14**
- positive fraction: **0.786**

Permutation calibration:
- permutations: **9,999**
- null mean: **0.00049**
- null 95% interval: **[−0.4005, 0.4652]**
- one-sided p: **0.0027**

Verdict:

`PASS_PERSONAL_STATE_MAINTENANCE`

## Secondary P2 — component persistence

### Maximum flight speed

Across all 14 subjects after condition × trial standardization:

- Pearson r = **0.4503**
- p = **0.0605**

Condition-specific descriptive r:
- condition 1: **0.0026**
- condition 2: **0.8980**

Thus speed alone does not clear the frozen secondary calibration across both conditions.

### Meandering width

Across all subjects:

- Pearson r = **0.5694**
- p = **0.0273**

Condition-specific descriptive r:
- condition 1: **0.5072**
- condition 2: **0.6317**

Route/meandering organization therefore retains clearer individual ordering than maximum speed alone in this independent learning experiment.

## Biological interpretation

The result distinguishes two things that had previously been confounded.

### Policy updating occurs

Repeated obstacle experience changes the population-level behaviour:
- speed can rise;
- meandering width falls.

### Personal policy position nevertheless persists

After those common condition-specific changes are explicitly removed, a bat's twelfth-flight state remains closer to its own first-flight state than to other bats' states.

Therefore:

> **learning changes the policy without erasing the individual.**

This is a direct formation/maintenance bridge.

A useful model is:

[
mathbf{y}_{ict}
=
oldsymbol{mu}_{ct}
+
oldsymbol{	heta}_i
+
oldsymbol{epsilon}_{ict},
]

where:
- (oldsymbol{mu}_{ct}) is the shared experience/condition update;
- (oldsymbol{	heta}_i) is persistent personal policy position.

The present summary-endpoint result supports a non-zero persistent (oldsymbol{	heta}_i), but it does not identify its origin.

## Relation to the task-reset programme

The independent Teshima 2026 obstacle-flight analysis found approximately two calibrated individual-policy dimensions in *R. nippon*:
- FlightIntensity;
- ManeuveringExtent / route organization.

The Yamada result is consistent with that architecture:
- speed alone is insufficient;
- route/meandering organization retains individual structure;
- the 2-D combination is more strongly maintained than either simple scalar alone.

However, the summary endpoints are not mathematically identical to the Teshima policy axes.

A direct raw-trajectory replication using the Yamada 1st/12th trajectory sheets remains a separate prospective endpoint.

## Claim ceiling

This result supports:

> repeated learning can update flight behaviour while preserving relative individual policy states.

It does not establish whether the persistent offset is caused by:
- morphology;
- physiology;
- developmental history;
- earlier learning;
- neural control;
- or their interaction.

## JAE firewall

No part of this result modifies JAE v0.4.0.
