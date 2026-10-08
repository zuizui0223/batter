# Target-blind flight-intensity forecast audit v1

## Status and firewall
**Post-outcome predictive-semantics audit.** The original Rhino cross-configuration identity results, theta-correspondence permutation result (G=+0.293072; p=.00175), 1D/2D dimension tests, and JAE manuscript are frozen and remain unchanged. This audit cannot be promoted to an independent confirmatory biological test. Do not use a favourable audit result to claim a unique flight law or causal memory.

## Problem identified before running this audit
The inherited `flight_intensity_scalar_v1.py` standardizes every test trajectory using a mean and SD computed from **all trajectories in its own held-out configuration**, including the target bat. This is valid for retrospective *relative identity* conditional on the full configuration, but not for a target-blind operational forecast. The zero-standardized baseline uses target information through its reference frame. Calling the original result an operational new-environment forecast is too strong.

## Frozen data and units
- Only the existing 45 feature-valid *Rhinolophus nippon* trajectories from the frozen Figshare source; four speed summaries, in the fixed order median speed, p90 speed, median absolute vertical speed, p90 absolute vertical speed.
- Unit = bat × configuration centroid (equal trajectories within cell); score = equal held-out configurations within each bat, then equal among the five bats.
- Preserve all 25 occupied bat × configuration cells and all seven configurations; do not drop a configuration or bat by outcome. If any input structural gate fails, STOP, not rescue.

## Primary: completely target-configuration-blind forecast
For target configuration e, compute a **single** 4-feature training mean and sample SD from trajectories in configurations *other than e*. Freeze those reference values for all 25 cell feature vectors in the fold. Reduce each standardized centroid to the equally weighted mean of four features.

For every target (i,e):
- predict its standardized centroid with the **same bat's** mean over all *other configurations*;
- baseline predicts training-reference 0;
- gain = squared baseline error minus squared personal-history error;
- summarize MSE_self, MSE_0, gain, R², all bat-level gains, and leave-one-bat-out gains.

No target-configuration raw value, mean, variance, trajectory or peer feature may enter the **training reference or prediction**. The held-out target value is used only for scoring.

## Secondary: target-bat-blind, peer-conditioned relative forecast
In the same held-out fold, use the same training-only sample SD. For each observed bat in any configuration, subtract the **equal-bat mean of all the other observed bats in that configuration** from its own four-feature centroid before scaling. The held-out target bat is absent from its peer reference; however, its **co-observed peers in the target configuration are required**. Own prior relative centroids predict the held-out peer-relative centroid; baseline 0 = peer mean.

This conditions on contemporary peers and is **not** an operational target-configuration-blind forecast. It tests whether dependence on *the focal test bat's own observations inside the centering reference* explains earlier apparent forecasting.

## Null and uncertainty
For each endpoint independently, 9,999 Monte Carlo null permutations, RNG seed 202610081319: independently relabel complete bat × configuration centroids **within each configuration**, holding labels present, centroids, configuration-specific distributions, trial support, and all numeric fold training-only references fixed. Refit historical individual means and rescore each mapping. Report one-sided p=(1+#null >= observed)/(B+1), full null mean and 95% interval. These are *conditional correspondence nulls*, not population sampling p-values.

Bat-cluster bootstrap, B=9,999, seed 202610081320, equal-weight resample 5 bats, provide percentile 95% uncertainty and all individual gains. The n=5 limit is binding.

## Verification gates
1. 45 source trajectories, 25 bat × environment centroids, bats A–E, environments 1–7, expected per-bat environment counts A5/B4/C5/D6/E5.
2. For a target e, varying *any* target-configuration feature cannot alter training means/SD or history-based forecast.
3. For peer-conditioned target, changing that bat's feature vector cannot alter its own peer reference.
4. One joint deterministic implementation is frozen before numerical outcomes are opened. No post-hoc endpoint switching, subgroup rescue, or threshold optimization.

## Interpretation boundaries
- Primary >0 with supportive conditional null means absolute flight-intensity forecasting can transfer to held-out configurations **without their data being used in prediction**; it still does not imply future spatial route or 3D-niche-shape prediction.
- Secondary >0 alone means **only peer-conditioned** relative forecastability, and operational forecasting remains unsupported.
- Null findings are specific to the estimand/support; they do not overturn frozen within-configuration-conditioned identity tests.
- This audit is about predictive target leakage and transport, **not** mechanistic attribution, optimality, learning or an intrinsic two-parameter universal law.
