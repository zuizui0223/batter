# ERA5 wind identifiability preflight result v1

## Status

ENVIRONMENT + X-Y-TIME ONLY. No numeric vertical response was parsed or used.

Authoritative workflow:
- run: 37090059505
- artifact: 11261673221
- conclusion: success

The pre-ERA5 500-m place x speed2_turn2 evaluable-individual counts exactly reproduced the frozen completed stress-test counts: 19 / 23 / 11 / 9.

| panel | x-y-time n | repeat n | span >=40% n | matched-wind fraction | max one-night fraction | verdict |
|---|---:|---:|---:|---:|---:|---|
| *Hypsignathus monstrosus* | 19 | 18 | 19 | 0.778 | 0.114 | PASS |
| *Phyllostomus hastatus* 2022 | 23 | 21 | 19 | 0.700 | 0.089 | PASS |
| *P. hastatus* 2023 | 11 | 9 | 10 | 0.527 | 0.262 | PASS |
| *P. hastatus* 2016 | 9 | 9 | 7 | 0.344 | 0.273 | FAIL |

Panel central-90% ERA5 10-m wind-speed ranges were 0.64-3.03 m/s (*Hypsignathus*), 0.66-2.33 m/s (2022), 1.38-3.76 m/s (2023), and 0.66-3.00 m/s (2016).

Three of four panels pass the frozen identifiability gate, so the reaction-norm vertical outcome may be opened for *Hypsignathus*, *P. hastatus* 2022, and *P. hastatus* 2023 only. The 2016 panel is stopped and is not rescued by relaxing support thresholds or changing the environmental predictor.

This is a feasibility result, not evidence that wind explains vertical individuality.
