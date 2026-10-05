# Target-normalization sensitivity contract v1

## Status

**POST-PRIMARY ROBUSTNESS DIAGNOSTIC.**

Frozen after the transparent two-axis policy was supported under within-environment z-scoring.

No alternative-normalization identity result has yet been calculated.

## Concern

The current transparent axes use target-environment mean and SD to express each trajectory relative to the other flights in that configuration.

That is appropriate for a **relative policy-coordinate** claim, but it could in principle make cross-configuration transfer look cleaner by normalizing away configuration-specific scale.

This diagnostic asks how much individuality survives when target-environment scaling information is removed.

## Raw features

Use the same eight physical movement summaries and the same 45 *Rhinolophus nippon* trajectories.

No pulse or absolute route-position feature enters.

---

# S1 — target-centered, training-scaled

For each held-out target environment e:

### Training transformation

For each training environment separately:
- subtract that environment's feature mean.

Pool all centered training residuals across the six training environments.

For each feature compute one pooled training SD.

### Target transformation

For the held-out environment:
- subtract its feature mean;
- divide by the **training pooled SD**.

Do **not** use target-environment SD.

Thus the target contributes only an unsupervised location shift, not a scale estimate.

Construct:
- FlightIntensity = mean(first four transformed features);
- ManeuveringExtent = mean(-feature1, feature5, feature6, feature7, feature8).

Use leave-one-environment-out individual centroids and the same identity-advantage estimator.

## S2 — fully training-only global scaling

For each held-out environment e:

From training trajectories only:
- compute one global feature mean;
- compute one global feature SD.

Apply those training mean/SD values unchanged to the target trajectories.

No target mean or target SD is used.

Construct the same transparent I/M coordinates.

This asks the stronger question:

> can absolute physical-policy position transfer to a new configuration without any target-domain normalization?

Because obstacle layouts legitimately change population-wide movement scale, failure here does not refute the relative-policy result.

---

# Outcomes

For each variant report:

1. FlightIntensity-only identity K;
2. ManeuveringExtent-only identity K;
3. transparent 2-D identity K;
4. positive-bat fraction.

## Null

Within every environment independently permute complete bat labels among trajectory clusters, preserving all feature values and environment support.

The transformation is label-free and remains fixed within a permutation.

9,999 permutations per 2-D primary diagnostic.

Seeds:
- S1 2-D: `202610051021`
- S2 2-D: `202610051022`

One-sided p.

For the one-axis components, report observed K and signs descriptively; no additional component p-values are needed.

## Interpretation

### S1 supported

Target-specific variance normalization is not required for the two-axis individuality.

### S2 supported

Very strong result: the two-axis individual signature transfers even in absolute training-defined physical scale.

### S1 supported, S2 unsupported

The stable policy is relative to the task's population/configuration scale rather than an absolute fixed physical-speed law.

This is biologically plausible and should be described as a **relative control phenotype**.

### S1 unsupported

The transparent two-axis finding depends materially on target-specific scaling and must be narrowed.

## Ceiling

This is a post-primary robustness analysis.
