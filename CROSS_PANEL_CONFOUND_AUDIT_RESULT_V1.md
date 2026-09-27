# Cross-panel confound audit v1 — synthesis

Contracts were frozen before output and recorded in
`CROSS_PANEL_CONFOUND_AUDIT_FREEZE_V1.md`.

Primary workflow run: **36317089590**.

## 1. Central-place / endpoint-associated structure

The frozen 1-km night-endpoint exclusion passes in **4/5 comparative panels**:

- *Hypsignathus monstrosus*: PASS;
- *P. hastatus* 2022: PASS;
- *P. hastatus* 2023: PASS;
- *P. hastatus* 2016: PASS;
- *Eidolon helvum*: FAIL solely because n falls to 11 below the frozen minimum 15, despite
  calibrated excess +0.390 and p=0.0002.

The prior focal *Tadarida* exclusion remains FAIL (p=0.1109).

Across all six paper panels, the predeclared endpoint-neighbourhood test therefore passes in
**4/6**, fails by inferential tail in focal *Tadarida*, and fails by the frozen sample-size gate in
*Eidolon*.

Interpretation: endpoint-associated structure does **not generally erase** the comparative vertical
identity result, but independence from central-place structure is not universal and cannot be
claimed.

## 2. Pairwise biological translation

Whole-session permutation calibration supports the pairwise self-win translation in **5/6
panels**. Only *P. hastatus* 2016 fails (observed 0.594, null mean 0.498, p=0.1168).

The inferential baseline is panel-specific; observed null means range from about 0.498 to 0.583.
The visual 0.5 line is therefore intuitive only.

## 3. Focal metre-scale translation

The raw focal AGL expected-height separation is 256.459 m. Its exchangeability null is not zero:

- null mean 133.733 m;
- calibrated excess 122.727 m;
- p=0.0297.

The metre-scale translation survives calibration and may remain in the main text with the null
reported beside it.

## 4. Paper-level consequence

The scientific story is now:

> Identity-matched bat vertical profiles retain more held-out information than expected under
> session-level exchangeability after coarse 5-km horizontal occupancy is standardized. This
> vertical identity is not generally removed by a fixed endpoint-neighbourhood exclusion, but the
> endpoint audit is not universal: focal *Tadarida* fails inferentially and *Eidolon* fails its
> frozen post-exclusion sample-size gate. Central-place-associated structure therefore remains a
> panel-dependent contributor rather than a general explanation or a fully excluded confound.

The methodological result is equally important:

> Prediction-based individual-identity statistics have pipeline-specific finite-sample nulls.
> Neither zero for absolute separation nor 0.5 for pairwise self-win should be assumed without
> label-permutation calibration.

## 5. Required manuscript changes

- change the title to explicitly say **coarse** or **5-km** horizontal occupancy;
- report the 4/5 comparative endpoint result plus the prior focal failure;
- replace the 0.5-only pairwise interpretation with panel-specific null means;
- remove *P. hastatus* 2016 pairwise self-win as independent support;
- report 256 m together with 134 m null mean and 123 m calibrated excess;
- foreground pipeline-specific null calibration in the Discussion;
- do not claim central-place independence, a verified roost mechanism, or a universal vertical
  strategy.
