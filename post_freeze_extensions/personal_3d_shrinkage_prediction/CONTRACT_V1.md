# Personal 3D shrinkage prediction contract v1

## Why this test is needed

The predictive ladder showed a sharp distinction:

- a focal individual's conditional map is consistently better than another individual's conditional map;
- but the raw focal cell-specific map does **not** improve future prediction over the focal animal's own marginal vertical distribution.

That comparison is asymmetric in model complexity. The conditional map estimates many cell-specific probability vectors, whereas the marginal model estimates only one.

Therefore the remaining question is:

> Is the apparent failure of personal 3D shape a biological result, or simply estimation variance?

## Frozen variance-control test

For each held-out target, use only focal-individual sessions at least three days in the past.

Define:

- I0 = focal-history marginal vertical distribution;
- I1 = raw focal-history cell-specific vertical distribution.

Shrink I1 toward I0:

`P_lambda(z|cell) = w_cell I1(z|cell) + (1-w_cell) I0(z)`

with

`w_cell = n_cell / (n_cell + lambda)`.

Lambda candidates are fixed at:

0, 5, 20, 50, 100, 200, 500, 1000.

For each target, lambda is selected **only from the past self-history** by leave-one-history-session-out log score. The future target is never used for tuning.

Primary endpoint:

`regularized shape gain = log P_lambda(target) - log I0(target)`.

The exact Lane-B target support is retained.

## Interpretation

- Positive gain after cluster-bootstrap support: spatially resolved personal shape contains forward information, but raw maps were too noisy.
- Unsupported gain: variance control does not recover positive shape prediction; the distinction between repeatable geometry and forecastable geometry becomes stronger.

This is a post-outcome diagnostic and cannot be treated as an independent prospective confirmation.
