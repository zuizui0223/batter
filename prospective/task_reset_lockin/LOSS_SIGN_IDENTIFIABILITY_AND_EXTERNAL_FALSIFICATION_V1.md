# Personal flight-intensity portability: exact loss identity, non-identification, and next falsifiable ecological test

## Status (2026-10-08)

**Post-outcome algebraic reconciliation, NOT a new biological endpoint or a fresh confirmatory test.** The current five *Rhinolophus nippon* bats and 45 existing trajectories have already been opened. This note does not re-fit them. It reconciles:
- `THETA_FIXED_PLASTIC_DECOMPOSITION_V1.md` and `THETA_SIGNAL_NOISE_SYNTHESIS_V1.md`;
- `THETA_CORRESPONDENCE_AUDIT_AUTHORITATIVE_RESULT_V1.md` (within-target environment centering);
- `TARGET_BLIND_FORECAST_AUDIT_RESULT_V1.md` (entire test configuration held out in scaling/prediction).

**Main caution:** A, D and E show positive *absolute* scalar forecast gain; B and C negative. These signs do **not** identify two different biological classes of flight strategies. They could arise under one shared model from individual mean position, context variance, sampling effort, or measurement reliability.

## 1. Why old B/C forecast failure is exactly explained without a distinct mechanism

For each bat, let `y_e` be the **previously defined within-configuration-standardized** FlightIntensity centroid, `n` the bat's number of observed configurations, `theta` the equal-configuration arithmetic mean, and `s^2` the sample variance of those n values with divisor n−1. The leave-one-configuration-out historical mean is

```text
h_{-e} = (n * theta - y_e)/(n - 1)
```

Let `G_old` be the average over a bat's target configurations of its zero-baseline squared error minus its leave-one-out personal-history squared error. Then **for every possible finite vector** of length n≥2:

```text
mean_e(y_e²)             = theta² + ((n - 1)/n) * s²
mean_e((y_e-h_{-e})²)    = (n/(n - 1)) * s²
G_old                    = theta² - ((2*n - 1)/(n*(n - 1))) * s².
```

This is an **exact deterministic identity**, not a statistical model, distributional assumption or proof of individual behavioral plasticity. The old predicted gains reconstructed from previously reported `theta` and `s` (4-decimal inputs, rounded) are:

| bat | n | theta | s | algebraic G_old | reported G_old |
|:--|--:|--:|--:|--:|--:|
| A | 5 | +1.0699 | 0.3061 | +1.102522 | +1.102492 |
| B | 4 | +0.1746 | 0.6104 | −0.186858 | −0.186842 |
| C | 5 | +0.3028 | 0.8319 | −0.219738 | −0.219724 |
| D | 6 | −0.7904 | 0.1613 | +0.615192 | +0.615213 |
| E | 5 | −0.4735 | 0.3943 | +0.154240 | +0.154219 |

Rounding accounts for differences below 0.000031. B/C cross zero because the squared magnitude of their personal displacement is less than the variance penalty. Their negative gains **cannot be separately cited as evidence for a learned switching strategy**, morphological flexibility, a non-Gaussian flight law, or adaptive bet hedging.

### Important scope boundary

The **new** target-configuration-blind PR #79 audit recomputes test-fold scaling using only other configurations. Its training reference changes with target e, so its gains **do not obey the above fixed-scale identity**. Independently executed gains are A +1.623521; B −0.070402; C −0.417945; D +0.851392; E +0.232007. The fact that signs match does not validate a causal mechanism. See the executed audit receipt for full MSE, conditional nulls, and five-bat bootstrap uncertainty.

## 2. Forward prediction: expected risk is not the empirical leave-one-out identity

Under an illustrative model (not established by data) with independent configurations:

```text
Y_new   = theta_true + error_new,   error ~ (0, sigma²)
h_train = mean(Y_1 ... Y_m),        independent of Y_new
```

the **expected** gain against zero after m independent training configurations is

```text
E[(Y_new - 0)² - (Y_new - h_train)²] = theta_true² - sigma²/m.
```

Thus even a genuinely stable theta can produce negative expected absolute improvement when the individual lies near baseline or the estimate is noisy. This is a prospective risk illustration **only**, not a new fitted model for the five bats. It also shows why the previously invalidated `91.6% converged` sample-size metric must not be recycled as biological evidence.

## 3. The key ecological gap: expression noise versus personal reaction norm

These rivals are observationally confounded in the current sparse archive:

**H0: fixed personal preference plus expression/measurement noise.**

```text
y_{i,e,s} = mu_e + theta_i + eps_{i,e,s}
```

**H1: repeatable individual × environment reaction norm.**

```text
y_{i,e,s} = mu_e + theta_i + b_i(E_e) + eps_{i,e,s}
```

**H2: learned path dependence or behavioral state carryover.**

```text
y_{i,e,s} = mu_e + theta_i + b_i(E_e) + f_i(H_{i,s}) + eps_{i,e,s}
```

Here s indexes **independent re-exposures**, not video frames or repeated measurements from the same flight. H0 can have heterogeneous sigma_i and reproduce the observed +/- gain signs without b_i or f_i. H1 and H2 may also generate exactly the same one-time bat×configuration centroids. For any proposed b and f, residual eps can be redefined to recover the same observations, so the five-bat archive alone cannot uniquely resolve this decomposition.

A genuinely ecological finding would show not simply that a mean flight intensity is individual, but **whether environmental opportunities reproducibly evoke different responses from the same individuals**, and whether those responses improve a function such as target acquisition/foraging success. A stable mean, a context-specific response, and adaptive payoff must be reported as three separate estimands.

## 4. Pre-outcome external falsification design: repeated environments across independent nights

This section defines requirements for **future independent measurements / an as-yet-unidentified external source**. Nothing in this note constitutes authorization for an animal experiment, and no current public archive is asserted to pass.

- Same physically validated bats repeatedly experience **the same independently verified obstacle configurations** on separate nights/sessions, plus genuinely new held-out configurations; log bat, context geometry, date/session, order, known sensor quality and appropriate actual task-performance measures. Repeat whole bat×configuration episodes across nights; do not count high-speed frames or multiple consecutive trajectories as independent individuals/nights.
- Freeze environmental contrasts, feature definitions, model complexity, training baseline and exclusion policy **before numerical outcomes**. Set biological sample size via independent-bat/session precision or power rather than arbitrary trajectory counts.
- **Primary test of H1:** from independent *training* nights, learn each individual's response to a particular configuration after removing shared configuration effects and separately trained personal mean; evaluate the predicted *sign and magnitude* of that residual response on held-out nights in the **same** configuration. Compare with a heteroscedastic H0 (each bat has its own noise scale but no reproducible b_i). Never infer plasticity merely from a large within-individual SD.
- **Counter-test:** assess prediction on truly new configurations; H1 may only predict re-encountered conditions unless E has prespecified explanatory axes, such as measured obstacle spacing or maneuver clearance. Claim transfer only over the contexts actually held out.
- **History test of H2:** randomize/counterbalance route or cue experience before the same probe configuration, including appropriate washout / resets. A reliable bat-specific history×probe response supports acquired state dependence; persistence alone cannot distinguish memory from unobserved inertia or predisposition.
- **Ecological payoff:** task success (e.g. prey/target capture rate and energy/time cost) is an **additional preregistered outcome**, not assumed from route fidelity. Separate intervention effects on route choice from effects on performance and from mediation; acoustic masks/gates need the independent physical engineering and safety gate already documented in PR #93.
- **Uncertainty:** inference unit = individual bat and independent session, with clustered/nested uncertainty. Null simulations/negative controls must preserve geometry and date. Report all individuals and failed contexts; do not select the A/D/E-style successful individuals post hoc.

### Discriminating outcomes

| Observed independent pattern | Strongest compatible interpretation | Still not established |
|:--|:--|:--|
| Personal mean predicts, but re-encountered context residuals do not repeat | H0 sufficient at measured precision | No individual reaction norms exist |
| Context residual direction repeats across nights beyond heteroscedastic H0 | Repeatable personal reaction norm (H1) | Learning, adaptive advantage |
| Randomized experience changes later response in a fixed probe context | Causal effect of assigned history (part of H2) | That any payoff difference mediates preference |
| Randomized opportunity changes task success after calibrated acoustic/physical gate | Functional effect of route opportunity | Long-term fitness benefit or acoustic mediation without additional tests |

## Closeout / decision

1. **Resolved now, without new data:** the old A/D/E versus B/C loss-sign heterogeneity is an exact consequence of mean–variance geometry, not additional evidence of behavioral mechanisms.
2. **Supported by already executed PR #79:** positive archive-conditional, target-blind *scalar* prediction for the five sampled bats; only 3/5 improve, five-bat cluster CI crosses zero.
3. **Unresolved:** why individuals differ in mean position/dispersion; whether they have reproducible within-individual environmental reaction norms, acquired policies, functional savings or lasting 3-D niche effects.
4. **No further same-archive adaptive feature fishing.** The next empirical increment requires an independent crossed bat×configuration×night design or a well-supported external dataset, not another degree of freedom in the existing five-bat output.
