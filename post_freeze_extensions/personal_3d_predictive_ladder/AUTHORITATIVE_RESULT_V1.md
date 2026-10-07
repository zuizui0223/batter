# Personal 3D predictive ladder — authoritative result v1

## Execution

- workflow run: 37617952904
- head SHA: `b27c8fb6143939acc3e3dbb4f764d8fffee1b748`
- conclusion: success
- artifact: 11481385106
- artifact zip SHA256: `3e0c0e7d56881499fac774cd5242f6a33dae6e67cca2e1132cae3c11ea498f2d`

## Result

The decisive contrast was the **self spatial increment**:

`I1 - I0 = focal-individual P(z|500-m cell) - focal-individual marginal P(z)`.

| panel | marginal identity I0-G0 | self spatial increment I1-I0 | personal vs other map I1-G1 | total I1-G0 | classification |
|---|---:|---:|---:|---:|---|
| *Hypsignathus monstrosus* | +0.0501 [0.0192, 0.0818] | +0.0329 [-0.0307, 0.1000] | +0.4256 [0.3137, 0.5437] | +0.0830 [0.0030, 0.1666] | marginal_state_prediction_without_shape_increment |
| *Phyllostomus hastatus* 2022 | +0.0222 [-0.0075, 0.0607] | -0.3724 [-0.5168, -0.2332] | +0.2459 [0.1049, 0.4188] | -0.3502 [-0.5022, -0.2036] | relative_personalization_only |
| *P. hastatus* 2023 | -0.0090 [-0.0331, 0.0092] | -0.0891 [-0.1452, -0.0319] | +0.3645 [0.2763, 0.4523] | -0.0981 [-0.1524, -0.0504] | relative_personalization_only |

## Interpretation

The previously observed same-individual advantage over other individuals' conditional maps does **not** establish that a spatially resolved personal 3D probability shape improves future prediction beyond the focal animal's own overall vertical state.

- In *Hypsignathus*, future personal predictability is positive, but the supported component is the individual's marginal vertical state; the extra cell-specific shape increment is not supported.
- In P2022 and P2023, the focal conditional map is better than conspecific conditional maps but worse than the focal marginal baseline. This is relative personalization, not positive shape prediction.

Thus the strongest current prediction claim is **not** "personal 3D shape is remembered." It is:

> Fine-scale conditional maps are non-interchangeable among individuals, but unregularized cell-specific personal shape does not add forward predictive information beyond a simpler individual vertical-state model in the tested panels.

A separate shrinkage diagnostic is required before concluding that spatial shape contains no predictive signal, because the conditional model is higher dimensional and may incur estimation variance.
