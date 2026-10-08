# Repeated context response: biological identifiability and prospective gate v1

**Status:** PRE-OUTCOME DESIGN AND SYNTHETIC CHECK ONLY. No animal data, no new public dataset and no new ecological result. This branch is a child of the already-closed Rhino target-blind audit (#79), not an amendment of JAE or its results.

## Why this new discriminator is necessary

The existing five-*R. nippon* target-blind scalar forecast finds positive *archive-conditional* personal-history predictive gain, but 2/5 bats have negative gain, and the five-bat cluster interval crosses zero. In the *older fixed-standardization* analysis, the per-bat gain is **exactly** `theta² - [(2n-1)/(n(n-1))]s²`: positive versus negative loss signs merely summarize individual displacement and contextual dispersion. They cannot reveal whether a large `s` is noisy flight, reliable personal environmental plasticity or recording artifacts.

The first empirically falsifiable question beyond those moments is **whether an individual-specific response to a prespecified 3D challenge is reproducible on *independent subsequent nights***. This is an established behavioural-reaction-norm concept, not a novel mathematical test in itself; novelty would need a specifically ecological explanation and independently measured task consequences.

Prior art:
- Dingemanse et al. (2010), *Trends Ecol Evol*, “Behavioural reaction norms: animal personality meets individual plasticity”, doi:10.1016/j.tree.2009.07.013.
- van de Pol (2012), *Methods Ecol Evol*, “Quantifying individual variation in reaction norms: how study design affects the accuracy, precision and power of random regression models”, doi:10.1111/j.2041-210X.2011.00160.x.
- Teshima et al. (2026), *Evidence for latent regularities in echolocation-guided flight behaviour of bats*, authors already analyze the Figshare 29209493 flight source: source overlap prohibits any “first latent bat policy” claim.
- Aoki et al. (2026), *Animal Behaviour*, doi:10.1016/j.anbehav.2026.123669, already document species differences in head–beam coordination; do not confuse this with an individual response test.

## Matched repeated-challenge contrast

Let bat `i` encounter **the same** predeclared contrast, e.g. a physical obstacle-clearance manipulation, within each of two **independent** occasions `s in {S1,S2}`, with both challenge levels `c in {0,1}` and randomized/counterbalanced order. The primary phenotype `Y` must be frozen **before** observing outcomes: a single biomechanically interpretable scalar (or a separately registered 3D endpoint, never chosen adaptively). Do not select “responding” bats or the most attractive contrast after outcomes.

Define
```text
Delta[i,s] = Y[i,challenge,s] - Y[i,reference,s]
D[i,s]     = Delta[i,s] - mean_j Delta[j,s]
C          = sum_i D[i,S1]*D[i,S2] / (N - 1).
```

Bat intercepts `theta_i` disappear by within-bat contrasts. Population-wide condition and occasion shifts disappear after occasion-specific centering. Under an illustrative random-response model `Delta[i,s] = gamma_s + b_i + epsilon[i,s]`, with independently sampled biological individuals and independent, zero-mean session residuals, `E[C] = Var(b_i)`. If environmental response is **only** shared and the bat's heterogeneous noise is independent across occasions, the expected cross-occasion covariance is zero. This avoids interpreting a large individual SD as reliable individual plasticity.

### Important inferential qualification

- C estimates **replicated covariance of challenge contrasts under its assumptions**, not innate/learned origins or ecological adaptation.
- A device's bat-specific challenge-response bias, persistent body-position calibration error, order × bat interaction or correlated successive sessions can also yield C>0. Sensor rotation and independent calibration, blinded processing, repeat occasions and balance of condition order are mandatory to isolate a biological response.
- Exact relabelling of the S2 bat identities (N! small N; Monte Carlo otherwise) is only an **archive-conditional correspondence test under exchangeability**, which may fail with strong bat-specific heterogeneous error. A permutation p-value alone is not a population-level confidence interval or causal test. Use independent-bat cluster uncertainty, heteroscedastic null calibration/sensitivity, and fully prespecified eligibility; an effect with only five bats is precision-limited.
- N independent bats, not rows/frames, is the biological sampling unit; two occasions are the **mathematical minimum** to estimate replication covariance, not a recommended adequacy threshold for estimating a distribution of personal reaction norms.

## Rival ecological predictions that can actually fail

| Rival | Predictive test in independently held-out occasion | Extra evidence needed |
|---|---|---|
| H0 stable mean (theta) + independent, possibly heterogeneous noise | Personal **contrast** covariance ~0 after shared context shifts | Calibrated sensor/noise envelope and adequate precision |
| H1 persistent personal context response b_i | Personal context contrasts covary across occasions after exchangeable-label null and heteroscedastic sensitivity | Multiple distinct challenge levels and independent dates to estimate shape and generalize |
| H2 history-induced personal response | Randomized/counterbalanced learning history changes the same later probe contrast, beyond transient order/inertia | Washout/reset and independent new bats |
| H3 sensory/geometric response with functional payoff | Prespecified context response predicts target success or energetic/time cost in held-out data; causal reward contrast where possible | Independently measured outcome and control of gate acoustic artifacts |

The field 3D vertical-space *shape* question is different from the laboratory flight-intensity question. A scalar response to an obstacle challenge can inform a candidate sensorimotor mechanism; it **cannot** mediate wild vertical niche individuality without same-individual, same-ecological-task linkage. A 3D shape endpoint would need the same crossed occasions and spatial-support-matched prediction test, and its own frozen source-independent contract.

## Minimal source eligibility gate (not filled in)

A potential dataset is eligible only if it contains: verifiable physical bat IDs, >=2 nonadjacent independently replicated occasions per bat and >=2 prespecified matched conditions **within each occasion**, known challenge geometry, independent recording/batch IDs, bat-level task trial support, bat/device calibration, and enough bats/occasions for predeclared precision. Without proof of independence and cross-classification, **STOP_SOURCE_NOT_IDENTIFIABLE**; do not reinterpret camera frames as independent occasions or pool unrelated species to create n.

If an eligible source is later identified, **freeze exact endpoint, contrasts, cohort, null generator, and performance criterion before opening the response magnitudes**. The enclosed Python only uses transparent **fabricated synthetic inputs** to verify covariance algebra, label-relabelling mechanics, and common-shift/intercept invariance. It does **not** connect to, download or analyze a bat dataset.

## Falsification before further search

1. With identical individual intercepts but no reproducible challenge response, the covariance test must be 0 under a deterministic common-response input despite large among-individual mean differences.
2. With perfectly stable idiosyncratic b_i replicated across two occasions, the observed mapping must be maximally aligned, and exact label permutations must dilute it.
3. A stable device-specific challenge error can produce exactly the same data as stable biological b_i: outcome data alone cannot distinguish them. Counterbalanced sensor assignment/calibration is a scientific requirement, not a numerical tweak.
4. A positive replicated contrast covariance is not automatically better foraging and does not imply social spatial partitioning.

## Scientific decision

**Empirical result now:** no new effect; inherited scalar portability only, with heterogeneous gains and limited across-bat uncertainty.

**Methods advance now:** a sharper next data requirement: crossed `bat × challenge × independent occasion` design, distinguishing reliable personal response from simple mean/variance differences. No more same-45-flight posthoc endpoint sweeps.

**Novelty boundary:** reaction norms are classic. The nontrivial bat ecological contribution, if independently supported, must be *how* 3D sensory/flight opportunity produces persistent personal response, and whether that response has an actual functional benefit.
