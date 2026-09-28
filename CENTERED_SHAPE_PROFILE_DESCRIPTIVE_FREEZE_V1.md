# Descriptive centered-shape profile freeze v1

Frozen before opening any individual-profile visualization output: **2026-09-28**.

## Purpose

This is **not a new scientific audit or inferential analysis family**. It only visualizes what the
already-completed session-centered common-cell estimator means biologically at the individual
profile level.

The figure is intended to answer the descriptive question:

> When centered-shape individuality is detected, what parts of the individual's vertical
> distribution visibly differ?

No new p-values, clustering, strategy classes, thresholds or biological-state labels are allowed.

## Frozen profile definition

For the five comparative panels only:

- *Eidolon helvum*
- *Hypsignathus monstrosus*
- *Phyllostomus hastatus* 2022
- *P. hastatus* 2023
- *P. hastatus* 2016

use exactly the session-median-centered events, 5-km cells, Jeffreys smoothing and centered bins
already frozen for the tag-altitude-bias audit.

For each evaluable target session, reconstruct the **same identity-matched common-cell self
profile used by the frozen estimator**:

1. exclude the target session from self training;
2. average the remaining self-session conditional distributions equally;
3. retain only horizontal cells jointly supported by self and other predictors for that target;
4. calculate the same equal-session self-derived horizontal weights used in the estimator;
5. integrate the self conditional profile over those weights.

Then average those target-session self profiles **equally within biological individual**.

Each displayed row therefore sums to one across the ten already-frozen centered-height bins.

## Frozen display

- one row = one evaluable individual;
- one column = one frozen centered-height bin;
- one stacked heatmap per comparative panel;
- rows sorted only by displayed upper-tail mass `P(residual height >100 m)`, ascending;
- ties sorted by individual identifier;
- one shared linear probability colour scale;
- no individual IDs printed in the paper figure;
- no clusters, dendrograms, PASS/FAIL labels, p-values or inferred strategy names.

The machine-readable table retains IDs for reproducibility.

## Interpretation ceiling

Visible differences in width, upper/lower tails, asymmetry or multimodality may be described as
features of the displayed profiles, but they are not separately tested.

The figure does not identify behavioural state, foraging, personality, adaptation or niche type.
Tag-specific differences in non-additive altitude-error variance remain possible.

This descriptive visualization does not reopen the declared stop rule for new scientific audits.
