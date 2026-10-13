# From individual mean to individual feedback gain — conditional 2025 Myotis test v1

**2026-10-13. Proposal only; no trial-level outcomes accessed.** Companion of `PUBLIC_2025_MYOTIS_ESCAPING_PREY_REPEATED_RESPONSE_SOURCE_GATE_V1.md`. Do not mistake these equations for estimated bat parameters, new evidence, a first control-law discovery or an amendment of frozen JAE.

## Biological question

When evasive prey starts moving, is there a **persistent personal sensory–motor feedback rule** that predicts the same bat's acoustic adjustment on a later day, distinct from (i) its own average calling level, (ii) a population-shared reaction to prey movement and (iii) bat-specific measurement noise?

Published Foskolos et al. (2025) reports all four bat subjects prolonging buzz duration during difficult target motion, but prominent time-resolved call-interval feedback in **one of four**; one response latency reported ~242 ms. These are already published findings, **not new outcomes** from this proposal.

## Nested, interpretable, pre-data-access candidate laws

Let `c` be one of the six published moving-target conditions for actual **motion-triggered** comparisons; for ordinary buzz-duration-level comparisons, the stationary condition can serve as a separate baseline, but is not a physically aligned motion-onset trial. `i` is a **physical bat**, `d` a distinct dated session and `r` a trial. Treat trials and call frames as nested, not as independent bats. Each candidate is conditional on future file-column verification.

**Scalar baseline (already a standard model, not a new law)**

```text
Y_i,d,c,r = alpha_i + day_d + mu_c + b_i,c + epsilon_i,d,c,r
```

- `alpha_i`: stable individual baseline/intercept.
- `day_d`: calendar/session history; must not be estimated using held-out outcomes when evaluating future prediction.
- `mu_c`: group-shared treatment response.
- `b_i,c`: bat-specific deviation from the shared response, **relative to a fixed, recorded reference condition**. For scalar buzz durations, a stationary reference may be legitimate after eligibility and missingness audits; for pulse-aligned time series, do **not** use the response-dependent stationary pseudo-onset as a matched real-time treatment reference. Constrain centered across bats for identifiability, or use hierarchical shrinkage.
- `Y`: a declared one-outcome phenotype (e.g. log(1+buzz-II-duration in ms) **conditional on valid measured buzzes**, with eligibility transparently stated). This model does **not** identify a continuous physical flight-control equation.

**A possible time-resolved sensor-feedback law (requires actual trial-level pulse timestamps and target-motion onset)**

```text
D_i,d,c,r(t) = f_c(t) + g_i * h_c(t - tau_i) + eps_i,d,c,r(t)
D(t)          = call_interval(t0+tau) - train_defined_pre_movement_CI_baseline
h_c(t)        = measured stimulus-motion time course at verified physical onset t0, with convolution kernel fixed before scoring
```

- `f_c(t)`: population-shared, condition-dependent call-interval trajectory;
- `g_i`: extra personal **feedback gain** relative to the common response (sum-centered across bats);
- `tau_i`: individual reaction latency, estimable **only if** gains and sampling support are sufficient;
- `eps`: autocorrelated trial/session measurement variation.

A group-common descriptive response model fixes `g_i=0`; a personal-gain alternative permits `g_i≠0`; an expanded alternative adds `tau_i` only if lag can be identified **without choosing the lag after viewing held-out outcomes**. **Only physically motion-onset-aligned moving-target trials enter this time-resolved contrast.** Pre-establish filter/interpolation, time window, call quality, time origin and any movement kernel; train normalization and shared time-course entirely on days 1–2. The paper's published one-responder and 242 ms latency must never be rebranded as a new independently verified result.

## Independent-day forecast gate (not statistical confirmation with N=4)

1. **Verify source schema first:** physical bat, session date, trial, exact motion stimulus, stationary controls, timestamped call intervals or declared scalar, validity flags, audio device/tag ID, and separately coded **moving-trial pursuit**. Published denominators differ materially: 631 total trials, 606 Fig. 2b chase cases, 474/479 Fig. 2 buzz-I/II cases, 391 Fig. 3 timing trials (with only 59/123 stationary controls selected). Without original pulse timestamps and independently measured physical motion onset, **do not fit `g_i,tau_i`**.
2. Use **days 1–2 for training** and days **3–4 as an unopened test set** across **all four** bats. Later two days belong only to bat #4; sensitivity analysis only. Chronology is real but adjacent dates do not guarantee independence from carryover learning or fatigue.
3. Predefine group-common-only M0 versus personal-gain M1 (and conditional lag model M2 **only with supported timing resolution**). Personal baseline intercept must be present in **both** where needed, so gain is not rewarded for explaining mean flight intensity.
4. Score whole held-out **trials/days**, with bat as biological sampling unit. For normalized interval time series, never treat its 1-ms interpolation or hundreds of pulses as new independent subjects. Report per-bat and equal-bat loss deltas; include negative results. With four bats, uncertainty is necessarily wide.
5. Estimate individual observation variance separately from mean/gain, and expose sensitivity to temporal dependence, device reattachment, baseline condition quality, and dropout; do not apply naive identity-label permutation as a valid `mean gain=0` test under heteroscedasticity.
6. Separately compare **chase probability across the six moving-target treatments** and acoustics *conditional on valid buzz*. A stationary-target 'chase' is not the same kind of decision as pursuit of a moving target. The original single-day motor-noise sham (108 trials) is not a balanced longitudinal control. Only a reproducible bat-specific gain on held-out days supports a **within-study personal acoustic-response predictor**; neither gain nor pursuit association establishes that the gain **causes** better actual prey capture or 3-D route choice.

## Pre-response methodological pitfall: stationary mock onset

The original Methods (Foskolos et al. 2025) align **moving** trials at a manually verified target movement start `t0`, but **stationary** control trials at a synthetic `t0` selected when the bat reaches a call-interval value sampled from the moving-trial distribution. The clock origin of the latter is selected using the acoustic response itself.

It follows that

```text
CI_moving(t - physical_t0) - CI_stationary(t - CI_selected_mock_t0)
```

is not an unbiased causal estimate of a prey-motion-triggered feedback kernel and might generate differences under nonstationary buzz time-courses *without a true stimulus response*. The original study's pooled exponential normalization also used outcomes across treatments and must not be transferred unchanged into a train/test protocol.

**Gate:** a personal `g_i` or `tau_i` dynamic law is only attempted on moving-target trials where the stimulus onset can be verified independently of call interval, with pre-exposure call baselines and control for approach-stage/time-to-interception (selection/censoring). The stationary group may inform scalar buzz duration and descriptive background but cannot function as a matched physical `t0` for the dynamic response. If only the article's processed normalized Fig. 3 curve is available, **STOP_DYNAMIC_FEEDBACK_LAW_UNIDENTIFIABLE**.

This is a source-structure and measurement warning, not a claim that the paper's published findings were invalid; its question and pooled descriptive estimands are distinct.

## Outcomes and stop decisions

| Source property / held-out result | Interpretation |
|---|---|
| No trial-level audio timestamps or day labels, or only stationarily mock-aligned Fig. 3 curves | **STOP** personal time-delay law; possibly descriptive scalar contrast if bat×day present |
| 4×4 crossed sensory challenge/reference, but no xyz | **SENSORY-ONLY** law, not 3-D flight strategy or spatial niche mechanism |
| M0 ≥ M1 on held-out days | Stable personal feedback-gain forecast **unsupported** |
| M1 improves in only one bat | **Case-level repeatable response candidate**, not general bat individuality |
| M1 improves, audio and chase unlinked or chase effect absent | Response may be real; functional/payoff interpretation **unestablished** |
| M1 improves across all bats, trial/device/day QA satisfactory | A stronger **within-study replicated predictive acoustic policy** (still n=4, post-publication) |

There is no statistical theorem or causal identification from these equations alone. Needed for wild 3-D mechanism: trial-wise XYZ with matched repeated challenges in identified bats, individually measured payoffs, independently calibrated observation processes, and an external/new cohort.

## Relation to other prior art

- Foskolos et al. 2025, BMC Biology 23:21, DOI https://doi.org/10.1186/s12915-024-02106-6 — direct acoustic-target feedback prior work, already reports one prominent personal responder.
- Grey, Aung & Abaid 2026, PLOS Complex Systems e0000100, https://doi.org/10.1371/journal.pcsy.0000100 — **group-level** SINDy dynamics of call number/acoustic power versus crowding and obstacles, not identified bat-specific gains.
- Existing batter PR #95 mathematical gate distinguishes distributional personal identity, mean response and heteroscedasticity. Do not conflate their nulls.
