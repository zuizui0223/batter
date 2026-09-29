# Four-panel 2-km fine-place × same-night context test v1

## Status

**POST-FREEZE STRUCTURALLY-EVALUABLE SUBSET TEST. No inference to Eidolon and no change to v0.3.8.**

Outcome-blind preflight:
- run: `36518495772`
- exact n fixed before vertical outcome: 19 / 26 / 14 / 9

Authoritative vertical workflow:
- run: `36518735021`
- head: `2a63679213a07effc39d40cccaf57cfd66dd87e8`
- aggregate artifact: `11015219112`
- digest: `sha256:ee6017479463c5eded4344fd5e733d4a0744b02fcd8e33d63903f71dd5a85e55`

## Frozen result

**3/4 panels PASS.**

| panel | n | observed self-vs-same-night gain | calibrated excess | p(null >= observed) | verdict |
|---|---:|---:|---:|---:|---|
| *Hypsignathus monstrosus* | 19 | +0.237 | **+0.302** | **0.0002** | PASS |
| *Phyllostomus hastatus* 2022 | 26 | +0.101 | **+0.169** | **0.0002** | PASS |
| *P. hastatus* 2023 | 14 | +0.0305 | **+0.0822** | **0.0286** | PASS |
| *P. hastatus* 2016 | 9 | +0.287 | **+0.564** | 0.0544 | FAIL |

## Interpretation

Within three of four structurally evaluable panels, **same-individual history remains more informative than contemporaneous other bats on the same shifted night**, even after matching at 2-km horizontal place × speed×turning state.

Thus broad shared calendar-night context is insufficient as a general explanation in this subset.

The 2016 panel has a large positive calibrated excess but misses the frozen tail threshold (p=0.0544), so it remains inferentially unresolved rather than counted as support.

Calendar-night matching is only a broad temporal-context proxy. It does not match exact local wind, uplift, temperature or microclimate.

A cached-equivalent implementation was independently validated against the completed 2023 result and reproduced the observed gain, calibrated excess and p-value exactly.
