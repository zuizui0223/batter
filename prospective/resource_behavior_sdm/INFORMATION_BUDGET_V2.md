# Noncausal identity-information budget v2

Research-only, 2026-11-20; adds only mathematical/source-free tests to the prospective 5-D bat use-model. No field identity information newly estimated.

Let individual I, horizontal cell X, time T, independently observed state B and height Z. By the chain rule:

\[I(I;B,Z\mid X,T)=I(I;B\mid X,T)+I(I;Z\mid X,T,B).\]

Term one is **state allocation identity information**, term two **within-state residual height identity information**. These are nonnegative information quantities under one normalized *joint* distribution. They are not an identified causal mediation decomposition, and `I(I;Z|XT) - I(I;Z|XT,B)` must **not** be equated with state-mediated effect.

`information_budget_v2.py` validates this algebra on a normalized 5-D use distribution. Two known-truth fixtures show state-only identity with residual zero, and within-state-only identity with state term zero; a third mixes them. Those are **synthetic sufficient examples**, not results for bats.

Existing empirical 5/5 speed×turn state and 4/4 eligible fine-place findings make the residual component a promising **next heldout target**. They do **not** supply the exact empirical joint distribution required to estimate these values because their calibrated permutation contrasts are not mutual-information estimators. Kinematic proxies do not establish feeding labels.

No original data, state labels, resource maps, species identities or frozen manuscripts are modified.
