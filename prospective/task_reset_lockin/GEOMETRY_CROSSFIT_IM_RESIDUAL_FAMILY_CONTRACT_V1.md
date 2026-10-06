# Cross-fitted I/M residual geometry family localization contract v1

## Status

**POST-PRIMARY EXPLORATORY LOCALIZATION DIAGNOSTIC.**

Parent:
`GEOMETRY_CROSSFIT_IM_EXPRESSION_RESULT_V1.md`

Known:
a single I/M -> geometry map learned from the other six environments leaves held-out geometry identity:
- K = +0.20160;
- 5/5 positive;
- p = 0.0156.

Question:

> **Which pre-existing broad geometry family carries this residual identity beyond the cross-fitted I/M map?**

No individual geometry feature may be selected.

## Frozen families

Use exactly the previously frozen geometry families:

### G — global route organization
indices 1–4:
- 3-D path efficiency;
- horizontal displacement ratio;
- absolute vertical displacement ratio;
- vertical range ratio.

### H — horizontal maneuver geometry
indices 5–6:
- median absolute horizontal turn angle;
- p90 absolute horizontal turn angle.

### V — vertical maneuver geometry
indices 7–8:
- median absolute vertical slope;
- p90 absolute vertical slope.

## Fold construction

For every held-out environment:
- reproduce exactly the parent training-only movement scaling;
- training-only geometry scaling;
- training-only linear I/M -> 8-D geometry map;
- calculate residual geometry for all training and target trajectories.

Then use only the specified family coordinates from the 8-D residual.

No re-standardization.

## Identity estimator

Use the exact parent leave-one-environment-out own-versus-other identity estimator.

## Null

Within environment independently permute complete bat×environment labels.

9,999 permutations per family.

Seeds:
- G residual: `202610062001`
- H residual: `202610062002`
- V residual: `202610062003`

Require >=9,500 valid permutations.

## Interpretation

A family is called descriptively identity-bearing only if:
- K > 0;
- p <= 0.05;
- >=4/5 bats positive.

If one family alone is supported:
the cross-fitted I/M insufficiency is localized mainly to that geometry aspect.

If multiple are supported:
residual identity remains distributed.

If none is supported:
the 8-D residual signal depends on combined weak contributions and should not be localized further.

## Ceiling

Do not:
- test individual residual features after output;
- regroup families;
- infer neural modules;
- call a supported residual family an independent causal policy axis.

This is localization of model insufficiency, not discovery of a new primary trait.
