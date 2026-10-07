# Aharon 2017 post-result programme update v1

## Status

**FROZEN FIGURE-1 PRIMARY SUPPORTED. SAME-SOURCE IDENTITY SEARCH CLOSED.**

Source:
Aharon, Sadot & Yovel (2017),
*Bats Use Path Integration Rather Than Acoustic Flow to Assess Flight Distance along Flyways*.

Public data:
Mendeley Data `10.17632/f6mvhj5gj9.3`.

Parent contracts:
- `AHARON_CROSS_CONDITION_IDENTITY_CONTRACT_V1.md`
- `AHARON_FIGURE1_STRUCTURAL_AUDIT_V2.md`
- `AHARON_FIGURE1_FINITE_MASK_CONTRACT_V2.md`
- `AHARON_FIGURE1_ZERO_GATE_V1.md`
- `AHARON_FIGURE1_PRIMARY_V1.md`
- `AHARON_FIGURE1_INTERPRETATION_LEDGER_V1.md`

## Structural result

Figure 1 was the first structurally eligible source figure under the frozen first-eligible rule.

Bats:
- 500;
- 503;
- 505;
- 510.

Conditions:
- con;
- 75;
- 300.

All 12 bat × condition cells:
- present;
- matrix rows >=2;
- >=10 valid bilateral trial columns;
- zero exact-zero cells.

Trial support:
- bats 500 and 505: 10 trials/condition;
- bats 503 and 510: 15 trials/condition.

## Frozen endpoint

For every trial:
- right-turn location = median of finite odd-row entries;
- left-turn location = median of finite even-row entries.

Each bat × condition state:
equal-trial mean of the two-dimensional bilateral turning vector.

For every condition:
the equal-bat condition mean was removed.

Primary:
leave-one-condition-out self-history advantage.

Exact null:
- `con` anchored;
- complete bat labels independently permuted in `75` and `300`;
- exact null size = `(4!)^2 = 576`.

## Confirmatory result

- K = **+3.695264**;
- positive bats = **4/4**;
- exact p = **0.00347222**;
- observed rank among 576 mappings = **2**;
- verdict = **SUPPORTED**.

Bat-level mean advantages:
- 500: **+1.931476**;
- 503: **+6.438521**;
- 505: **+3.265457**;
- 510: **+3.145604**.

Condition-level mean advantages:
- con: **+2.752794**;
- 75: **+4.109808**;
- 300: **+4.223191**.

Leave-one-bat-out descriptive K:
- drop 500: **+4.283194**;
- drop 503: **+2.780846**;
- drop 505: **+3.838534**;
- drop 510: **+3.878484**.

Thus the sign does not depend on any one bat.

## Biological interpretation

The source experimentally changes current navigation conditions while the same bats repeatedly perform the flyway task.

After removing the shared condition-level shift:

> **bilateral turning-location organization remains individually identifiable across all three navigation conditions.**

This supports:

[
oxed{
	ext{navigation context changes}

otRightarrow
	ext{erasure of personal navigation organization}
}
]

The result is nonredundant with:
- *Rhinolophus* obstacle-context portability;
- *Pipistrellus kuhlii* masker perturbation;
- *Eptesicus fuscus* central auditory perturbation.

It adds a path-integration / navigation-context manipulation.

## Small-n boundary

n = 4 biological bats.

Unlike the auditory 4-bat test, three conditions provide a larger exact correspondence space:

[
(4!)^2=576.
]

The exact result is therefore more finely resolved than a single two-condition 4-bat mapping test.

Still:
- no population-prevalence estimate is precise;
- no broad species-general claim;
- source-specific turning organization is the tested object.

## Same-source ceiling

**STOP_NEW_AHARON_IDENTITY_SEARCH.**

Do not:
- select only a favorable condition pair;
- move to Figure 2/3/4 as a confirmatory rescue/replication;
- split right versus left turns into new confirmatory endpoints;
- switch median to mean;
- add slowing or speed as co-primary;
- learn weights/PCA;
- drop a bat.

Figure 3 may remain descriptive/source-context material only.

## Programme consequence

Public-data evidence for maintenance/portability now spans independent intervention classes:

1. obstacle/task context;
2. external sensory masking;
3. central auditory perturbation;
4. path-integration/navigation-context manipulation.

The bounded cross-system principle is:

> **Established individual organization is repeatedly more stable than the behavioral expression through which it is observed.**

This still does not identify the causal origin of the personal organization.
