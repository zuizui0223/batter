# Three-panel >=3-day temporal persistence stress test v1

## Status

**POST-FREEZE TEMPORAL-STABILITY STRESS TEST. Opened after partial >=1-day positive results; not independent confirmation.**

Outcome-blind source preflight:
- run: `36538374767`
- exact >=3-day n fixed before vertical outcome: 22 / 25 / 11

Authoritative vertical workflow:
- run: `36539572278`
- head: `88b1bec135f223de319b3873f7079a0d2fb74f43`
- aggregate artifact: `11019714326`
- digest: `sha256:550b61525713ceaa7bca3a1a8fc24ccd72a8d9f948b96a8d77932b94de8e28f4`

## Frozen result

**3/3 panels PASS when self-training is restricted to sessions at least three days from the target.**

| panel | n | calibrated excess | p(null >= observed) |
|---|---:|---:|---:|
| *Hypsignathus monstrosus* | 22 | **+0.1539** | **0.0002** |
| *Phyllostomus hastatus* 2022 | 25 | **+0.0959** | **0.0002** |
| *P. hastatus* 2023 | 11 | **+0.0573** | **0.0216** |

## Interpretation

In the three systems with sufficient pre-outcome support, individual centered vertical organization persists even when the self predictor is built only from sessions separated by at least three days.

This pushes the signal beyond immediate night-to-night carryover and supports a **multi-day stable individual component**.

It does not establish lifetime stability, immutable personality or a particular intrinsic cause. P2016 and Eidolon are structurally unavailable at this lag.

## Claim boundary

- this is a post-hoc stress test opened after partial >=1-day results;
- no inference to P2016 or Eidolon;
- persistence beyond three days remains unresolved;
- frozen v0.3.8 remains unchanged.
