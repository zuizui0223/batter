# Relative tag-burden vs centered vertical-identity strength v1

## Status

**POST-FREEZE TECHNICAL-CONFOUND TEST. Frozen v0.3.8 claims are unchanged.**

Authoritative workflow:
- run: `36520751223`
- head: `bde657ea9c8444071e136da97f9e7a51d5189b1c`
- artifact: `11012234841`
- digest: `sha256:0aebb17bf6b9d80d473851938367d653073f33696d1cfb56030800de5d3d8c8b`

Response: individual permutation-null-calibrated centered vertical identity from authoritative run 36508617613.

Exposure: relative biologger burden = tag mass / animal mass.

## Frozen result

Cross-panel equal-panel mean absolute Spearman rho = **0.268**.

Permutation **p = 0.1399 → FAIL**.

| panel | n | signed rho | two-sided permutation p |
|---|---:|---:|---:|
| *Eidolon helvum* | 20 | -0.371 | 0.1070 |
| *Hypsignathus monstrosus* | 24 | -0.034 | 0.8754 |
| *Phyllostomus hastatus* 2022 | 31 | -0.401 | 0.0274 |
| *P. hastatus* 2023 | 16 | +0.199 | 0.4571 |
| *P. hastatus* 2016 | 10 | -0.334 | 0.3399 |

## Interpretation

A simple monotonic **relative tag burden → stronger/weaker vertical individuality** relationship is not supported across the five comparative panels.

The isolated 2022 association is retained, but signs are inconsistent among panels and the frozen cross-panel test is not significant. Relative payload therefore does not provide a general technical explanation for the comparative individuality pattern.

This does not rule out non-monotonic payload effects, aerodynamic attachment effects, or tag-model effects not represented by mass ratio.
