# Proposal-density correction for sampled 3D candidate steps — known-truth v1 (2026-11-21)

**Status: software/methodological audit only; synthetic 3D endpoint choices. Not bat field data, not ssf3D R reproduction and not newly estimated ecological 5-D resource-height selection.**

## Scientific problem

The earlier [paired XY×AGL grid benchmark](paired_3d_ssf_resource_benchmark_v1.py) enumerated **every** 2D cell × vertical bin; all candidates were an equally weighted finite set. Real 3D-SSF often samples a *subset* of potential future positions from a movement/turning-angle proposal, e.g. gamma length and Kent turning distributions implemented in [Klappstein et al. (2026) ssf3D](https://github.com/NJKlappstein/ssf3D). A sampled 3D set is **not** the uniform exhaustive grid. Estimating a movement proposal from **all** observations would leak withheld bat/test outcomes; any real proposal must be externally defined or fit on the training data only.

For a finite endpoint domain, suppose one observed endpoint is sampled from target distribution

    p(x) = mu(x) * exp(beta * f(x)) / Z

and K control endpoints are sampled **independently** from a known proposal q(x) (with positive support wherever p is positive). Condition on the unordered observed+control candidate values and on exactly one observed label. Bayes' rule gives the matched-choice label probability

    Pr(label=j | candidates, one observed) ∝ p(x_j)/q(x_j)
     ∝ exp(beta * f(x_j) + log(mu(x_j)) - log(q(x_j))).

The additive offset log(mu/q) is therefore necessary in this *particular* case-control sampling design. This derivation does **not** mean one always subtracts q in a fully enumerated grid, or that this module reproduces the R ssf3D gamma/Kent density correction. When candidate points are generated with a different process, the appropriate likelihood and reference measure must be derived again.

## Executed tests

New Python module [proposal_corrected_3d_stepchoice_v1.py](proposal_corrected_3d_stepchoice_v1.py) implements ridge conditional choice between one observed and K q-sampled controls, supports site-/bat-heldout refits, and uses equal bat then night then step weighting. Regression suite: [test_proposal_corrected_3d_stepchoice_v1.py](test_proposal_corrected_3d_stepchoice_v1.py).

Known-truth generator seed 119. **16 fictional bats, 2 nights each, 35 steps/night = 1,120 observed artificial steps**. For each step, 12 available endpoints = four XY resource sites × three height levels; an observed endpoint is sampled from true p and **8** independent control endpoints sampled from q. The proposal strongly favors higher resource×height levels in study site A (proposal exponent +2.2) and lower levels in B (−2.2). Two disjoint site holdouts each contain 8 bats. The real coefficient in the first scenario is exactly **zero**.

| True constructed scenario | Corrected full pooled β | Naïve pooled β | Site-equal corrected − naïve heldout log score |
|---|---:|---:|---:|
| **No resource×height effect; only q changes across sites** | −0.0574 | −0.0064 | **+2.4241 nats/step** |
| **Real resource×height selection β=+0.95; q changes** | +0.9987 | +1.2878 | **+2.1199 nats/step** |

The pooled β can mask the problem because the **opposite** q biases cancel. The source-heldout fits explain the transfer failure:

| Source held out, null world | Corrected train β | Naïve train β | Corrected holdout logscore | Naïve holdout logscore | Corrected advantage |
|---|---:|---:|---:|---:|---:|
| A | −0.1372 | +2.0342 | −1.5042 | −3.8946 | +2.3904 |
| B | +0.0303 | −2.1385 | −1.5337 | −3.9915 | +2.4578 |

The nonzero simulated selection world additionally recovers the positive beta with proposal correction; an independent fixed-q null test finds corrected β near zero and uncorrected β with spurious magnitude above 1.

These are **illustrative fixed-generator conditional label log scores**. Nats/step are conditional selected-vs-sampled-alternatives classification scores, **not** absolute trajectory density, biological relative selection strength, occupancy, or a field effect. The large gain is intentionally produced by reversing the proposal's strength between the two synthetic study sites. It should not be generalized to actual 3D-SSF bias size or applied as an empirical correction without the actual source proposal.

## What changes in the original 3D resource model programme

1. **Do not simply score true+control 3D steps as if all alternatives are uniform**, when the controls were sampled from a fitted gamma/Kent or other nonuniform proposal. Freeze candidate generation and proposal/reference measures on source-qualified original tracks, using training animals only.
2. Preserve the already implemented **exact horizontal/height decomposition** of the *same matched candidate probability* for actual model comparison. In a sampled riskset, this is decomposition of the **conditional matched-choice task**, not automatically an absolute p(z|x) or mapped abundance.
3. Add a **proposal/height error audit** before promoting any Goldshtein field result. A positivity failure, unsupported q(x), test-data-derived proposal, height-defined behavioral state, unmatched dated flowers or incomplete survey coverage is a **STOP**.
4. Compare with the published full **ssf3D** implementation using the *same original tracks, 3D alternative generation and observation denominator* if qualified; direct likelihood comparisons require compatible base measures. This Python module is a proof of the danger and an eligibility benchmark, not a replacement for the established package.
5. Resource prediction **is not resource causality**. The previous independent synthetic hidden-habitat counterexample already showed strong resource×height heldout gain when the true direct effect was zero.

## Source availability

Goldshtein et al. 2020 [Mendeley Data](https://doi.org/10.17632/jxghjjsttw.1) Version 1 is listed as public, with description of movement, video and nectar data. On 2026-11-21, the publisher HTML landing page can be read but its embedded file list is not exposed in the tool's retrieved content; direct public Mendeley API metadata/files read from the browser tool is inaccessible. The original GitHub Actions gate yielded **HTTP 401**. Thus raw source files and true bat GPS × dated cactus bloom join remain **NOT VERIFIED**, and the resource-conditioned **wild 3D height predictive gain remains NULL**.

No raw GPS or author source rows are committed. Keep draft PR #102 and protect existing JAE/BE and parent main.
