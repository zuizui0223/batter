# Personal 3D shrinkage prediction — authoritative result v1

## Execution

- workflow run: 37619301387
- head SHA: `45a591fffc1516c389d6a31670e19f3bdd5bec35`
- conclusion: success
- artifact: 11480954336
- artifact zip SHA256: `1606acac56759b72f5bb9ab146b5b710afdb6c63a42ed1e8a2d80e95182732af`

## Result

History-only cross-validation selected the amount of shrinkage of the focal individual's 500-m cell-specific vertical profile toward its own marginal vertical distribution.

| panel | raw shape gain on eligible subset | regularized shape gain | support | dominant shrinkage pattern |
|---|---:|---:|---|---|
| *Hypsignathus monstrosus* | +0.0429 [-0.0222,0.1125] | **+0.0779 [0.0353,0.1270]** | **PASS** | heterogeneous; 50, 20, 200 and 1000 all selected |
| *Phyllostomus hastatus* 2022 | -0.3893 [-0.5490,-0.2396] | -0.0007 [-0.0109,0.0133] | FAIL | lambda=1000 in 43/62 targets |
| *P. hastatus* 2023 | -0.1061 [-0.1604,-0.0400] | +0.0091 [-0.0113,0.0393] | FAIL | lambda=1000 in 2/5 targets; strong shrinkage generally |

## Interpretation

The failure of the unregularized cell-specific map is partly an estimation-variance problem in *Hypsignathus*: selecting shrinkage strictly from past self-history recovers positive future predictive information beyond the focal marginal vertical state.

That rescue does not generalize to *P. hastatus*. In 2022 and 2023, history-only tuning drives the cell-specific map strongly toward the marginal model and produces approximately zero incremental predictive value.

Therefore:

> **A forecastable personal 3D probability shape exists in at least one system, but it is not a general bat architecture.**

For *P. hastatus*, the strongest stable personal predictive component in the current analyses is fine horizontal geography rather than a persistent cell-specific vertical map.

This remains a post-outcome variance-control diagnostic, not independent confirmation or proof of cognitive memory.
