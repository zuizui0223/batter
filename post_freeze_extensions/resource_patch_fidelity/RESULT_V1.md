# Resource-patch fidelity mechanism test v1

## Status

**POST-FREEZE EXPLORATORY RESULT. Not part of the frozen v0.3.8 submission claim set.**

Frozen contract commit: `1a52704431a92e07e70550b2d7054687d5334c5c`  
Authoritative workflow run: **36508617613**  
Final artifact: **11008176963**  
Digest: `sha256:426c86df56b74483cdbe9b42087a82a5cbb99e93f5db3683193cd4228727ecf8`

## Question

Does individual-specific reuse of fine-scale horizontal movement patches predict the strength of
repeatable centered vertical-distribution identity?

The primary x-y-only proxy is 1-km fine-scale patch-fidelity excess after pairwise conditioning on
shared 5-km cells:

`same-individual session similarity - other-individual session similarity`.

Vertical identity is individually calibrated against the frozen whole-session permutation pipeline.

## Frozen primary result

- equal-panel mean Spearman rho: **+0.1759**
- one-sided within-panel stratified permutation p: **0.05731**
- positive panel correlations: **4/5**
- frozen verdict: **FAIL**

| panel | n | rho |
|---|---:|---:|
| *Eidolon helvum* | 20 | **-0.5218** |
| *Hypsignathus monstrosus* | 24 | **+0.6035** |
| *Phyllostomus hastatus* 2022 | 33 | **+0.3473** |
| *P. hastatus* 2023 | 16 | **+0.1294** |
| *P. hastatus* 2016 | 10 | **+0.3212** |

The directional and consistency parts of the frozen rule pass, but the p<=0.05 part does not.
The simple claim that fine-scale patch fidelity is a general driver of centered vertical
individuality is therefore not supported.

## Grid sensitivities

These were frozen as sensitivities and cannot replace the 1-km primary result.

| fine grid | equal-panel mean rho | one-sided p | positive panels |
|---|---:|---:|---:|
| 500 m | +0.1323 | 0.11718 | 3/5 |
| 1 km primary | +0.1759 | 0.05731 | 4/5 |
| 2 km | +0.1780 | 0.05508 | 4/5 |

The pattern is therefore not a sharp artifact of choosing exactly 1 km, but none of the frozen
analyses crosses the primary support threshold.

## Descriptive boundary comparison

*Tadarida teniotis* was excluded from the primary meta-statistic. Its descriptive 1-km
individual-level correlation is **rho=+0.5429** (n=6).

This is not evidence for a taxon-level resource-regime contrast; it is retained only as the
predeclared boundary comparator.

## Post-hoc heterogeneity diagnosis: *Eidolon*

The strong negative panel-level association is not a consistent negative relationship within the
largest *Eidolon* cohorts.

Among matched individuals:

- Zambia, Kasanka 2014: n=8, within-cohort rho about **-0.024**;
- Burkina Faso, Ouagadougou 2014: n=5, within-cohort rho **0.000**.

Cohort means differ strongly. Kasanka 2014 has low mean patch-fidelity excess (~0.084) but high
mean calibrated vertical identity (~0.731), whereas some cohorts with stronger patch fidelity have
lower mean vertical identity. Thus the overall *Eidolon* rho=-0.522 is substantially associated
with between-cohort ecological context rather than a stable inverse within-cohort rule.

This diagnosis is **post hoc** and cannot rescue the frozen primary test.

## Ecological interpretation

The result weakens a simple universal pathway:

`persistent horizontal patch fidelity -> stronger vertical individuality`.

It does **not** reject resource-linked behavioural allocation more broadly. Strong vertical
individuality can occur where fine-scale horizontal patch fidelity is weak, especially in
*Eidolon*. This makes two mechanisms more plausible targets for the next test:

1. **behavioural-mixture individuality** — repeated differences in the fraction of time allocated
   to commuting, local movement, feeding-patch residence, social-site use, etc., even if exact
   horizontal patches change;
2. **within-state individuality** — different vertical organization while performing the same
   broad movement state.

The next discriminating analysis should therefore use x-y-time movement-state composition rather
than absolute patch identity.

## Claim boundary

The movement-patch proxy is not a direct measure of food resources, competition, feeding trees or
behavioural state. This exploratory result does not modify the v0.3.8 manuscript, figures, frozen
inferential endpoints, or submission package.
