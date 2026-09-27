# Effect-translation null calibration result v1

Contract frozen before output:
`contract/effect_translation_null_calibration_v1.json`
(blob `169caf84fb96db70a937b6ecf14486c6e5eb6e1a`).

Primary workflow run: **36317089590**.

## Pairwise self-identification

The intuitive 0.5 line is not the inferential null. Whole-session label permutations give
panel-specific finite-sample self-win baselines.

| panel | observed self-win | null mean | calibrated excess | p upper | main-text calibrated translation |
|---|---:|---:|---:|---:|---|
| *Tadarida teniotis* | 0.7935 | 0.5075 | +0.2860 | 0.0189 | **YES** |
| *Eidolon helvum* | 0.8579 | 0.5829 | +0.2750 | 0.0002 | **YES** |
| *Hypsignathus monstrosus* | 0.7671 | 0.5408 | +0.2263 | 0.0002 | **YES** |
| *Phyllostomus hastatus* 2022 | 0.8416 | 0.5317 | +0.3099 | 0.0002 | **YES** |
| *P. hastatus* 2023 | 0.7824 | 0.5349 | +0.2474 | 0.0002 | **YES** |
| *P. hastatus* 2016 | 0.5936 | 0.4979 | +0.0957 | 0.1168 | **NO** |

Thus **5/6 panels** retain a calibrated pairwise biological translation. The 2016 panel remains a
useful weak case and is not promoted as independent pairwise evidence.

The null means are not universally 0.5: they range from 0.498 to 0.583. This directly supports the
paper's methodological point that intuitive prediction baselines should not replace
pipeline-specific exchangeability calibration.

## Focal AGL expected-height separation

Frozen raw statistic:

- equal-individual mean absolute self-vs-other expected AGL separation = **256.459 m**;
- median individual separation = **144.573 m**.

Under the exact frozen 9,999 whole-session AGL label permutations:

- null mean = **133.733 m**;
- null SD = 54.905 m;
- null median = 120.661 m;
- null 95% interval = 56.462–262.599 m;
- calibrated excess = **122.727 m**;
- one-sided p = **0.0297**.

The raw 256 m therefore remains permitted as a main-text biological magnitude, but it must be
reported together with its positive finite-sample null. The correct headline is not “256 m above
zero”; it is approximately **256 m raw separation, 134 m exchangeability baseline, 123 m calibrated
excess**.

## Reporting consequence

- Figure 4 should show each panel's permutation-null mean as the inferential baseline.
- A 0.5 line may remain only as a secondary intuitive reference.
- *P. hastatus* 2016 pairwise self-win should not be used as independent main-text support.
- The focal 256 m value may remain in the main text only with its null mean and calibrated excess.
