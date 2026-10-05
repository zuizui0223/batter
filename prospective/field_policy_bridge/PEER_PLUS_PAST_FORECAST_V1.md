# Peer-plus-past field forecast v1

Status: frozen post-outcome predictive diagnostic.

Question: after accounting for the contemporaneous cohort-day policy of peers, does strictly prior personal policy history improve prediction of the focal bat's next 2-D H/V policy?

Data: exact harmonized P. hastatus H/V session policy used by the fixed-bin bivariate carrier.

For each session:
1. compute the equal-individual mean H/V policy of other bats from the same cohort and source day;
2. require at least two peer individuals;
3. residual policy = focal H/V - peer-day mean H/V.

For each focal target session:
- use only residual sessions from the same individual that ended before the target;
- require at least two prior residual sessions;
- personal predictor = equal-session mean of those prior residuals.

Peer-only prediction of the target residual is zero.
Peer-plus-past prediction is the personal predictor.

Primary statistic:
Delta = equal-individual mean of [||target residual||^2 - ||target residual - personal predictor||^2].
Positive Delta means personal history improves prediction beyond contemporaneous peer context.

Also report:
- pooled no-refit R2 = 1 - SSE(peer+past)/SSE(peer-only);
- positive individual fraction;
- target count.

Null:
within every cohort-source-day independently, permute the exact individual-label multiset attached to complete residual policy vectors. This preserves shared day structure and the residual vectors while breaking persistent individual continuity across days.

9,999 permutations.
Seeds: 202610052001 (2022), 202610052002 (2023).

Support requires:
- Delta > 0;
- one-sided p <= 0.05;
- >=70% evaluable individuals have positive individual Delta.

Interpretation boundary:
support shows a persistent personal offset with predictive value beyond shared day context. It does not identify whether that offset is learned, morphological, physiological, or developmental.
