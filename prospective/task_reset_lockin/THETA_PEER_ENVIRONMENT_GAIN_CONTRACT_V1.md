# Peer-calibrated environment expression gain — contract v1

## Status
Post-outcome mechanism diagnostic after the observed theta estimates, mixed per-bat predictability, and correction of the tautological subset-MSE convergence claim were already known. Not an independent hypothesis confirmation.

## Biological question
When a bat encounters a novel obstacle configuration, is the expression of its portable scalar theta multiplied by a **common environment-dependent gain** that can be inferred from conspecifics, or are the departures intrinsically individual-by-environment?

## Sources
Use the same 25 bat×configuration FlightIntensity centroids from the frozen authoritative Teshima programme. No new outcomes.
- bats A–E, contexts Env1–Env7;
- exactly 23 eligible targets in contexts with at least **three distinct bats** (Env1–Env6).
- Env7 with only A and B excluded **before opening results**, since one peer cannot robustly determine a shared gain.

## Baseline M0 — personal scalar only
For each eligible target bat i and held-out environment e:

\[
\hat\theta_{i,-e}=mean_{e'\ne e} y_{i,e'}
\]

using only the focal bat's other configurations.

Predicted y for target: \(\hat y^{M0}_{ie}=\hat\theta_{i,-e}\).

## Model M1 — peer-calibrated common expression gain
For each other bat j in the held-out target environment e:
- estimate \(\hat\theta_{j,-e}\) only from j's configurations other than e;
- observe peer's \(y_{j,e}\) in e (without touching focal y).

Estimate a shared multiplier with fixed ridge prior alpha=1:

\[
\tilde\alpha_{e,-i}
=\frac{1+\sum_{j\ne i}\hat\theta_{j,-e}y_{je}}
{1+\sum_{j\ne i}\hat\theta_{j,-e}^{2}}.
\]

Set \(\hat\alpha_{e,-i}=\min(2,\max(0,\tilde\alpha_{e,-i}))\) to restrict gain to nonnegative values with maximum doubling.

Then \(\hat y^{M1}_{ie}=\hat\alpha_{e,-i}\hat\theta_{i,-e}\).

Ridge strength 1 and range [0,2] are **fixed before opening results**; no tuning against focal test outcomes.

## Primary outcome
Target-level improvement in squared error:

\[
G_{ie}=(y_{ie}-\hat y^{M0}_{ie})^2-
       (y_{ie}-\hat y^{M1}_{ie})^2.
\]

Aggregate equal target contexts within bat, then equal bat; report overall G and individual contributions.

Also report M0/M1 MSE and relative M1-vs-M0 gain.

## Uncertainty
- Biological-bat cluster bootstrap with replacement; 9,999 resamples, seed 20261008131.
- 95% percentile CI for mean G.
- Rule for *descriptive support*: mean G>0, bootstrap CI lower bound >0, and at least 3/5 bats have positive mean G.
- Show each bat and each configuration's effect, no selective dropping.

## Interpretation
If M1 improves held-out forecasts, conspecific responses carry transferable information about environmental gain, consistent with a shared \(\alpha_e\) on the stable personal axis.

If M1 fails, a single shared multiplier is insufficient: individual-by-configuration terms \(h_{ie}\), nonlinear responses, or measurement noise may dominate.

Neither outcome identifies learned physiology, neural mechanisms, temporal stationarity, causal peer influence or colony memory. Peer observations are contemporaneous data in the test environment; M1 is a **peer-informed forecast**, not an entirely past-only forecast.
