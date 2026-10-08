# Four-route skill feedback: classic first-order formation plus shared-maneuver transfer

## Evidence and version status

**MATHEMATICAL/SYNTHETIC ONLY — NO NEW BAT OBSERVATIONS.** The parent JAE manuscript and PR #72 P1/P2 are unchanged. This extends PR #84 in a separately versioned prospective branch.

Frozen before new numerical outcomes: contract commits `9765d67f`, `525e2dbf`. Local numerical engine `four_route_skill_feedback_v1.py` (Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0). All five mathematical/structural self-tests passed. Exact local SHA256: source `d2013afc5407597c288a6eb035cfcfab83628f5dae4b8de4e4c985c51a5928ae`; machine result `e52bd060332018c471cccec38b668204027f0158956c3f58b438baf28ad73657`. The companion Actions run must independently complete before declaring GitHub CI success.

## A — Whole-route practice has a finite-jump formation region at four routes

Four possible physical paths are R1=L-low, R2=L-high, R3=R-low, R4=R-high. Route-specific skills s_r decay by delta and increase by eta each time path r is flown. Route probabilities are softmax(kappa*s_r). Define A=eta*kappa/delta.

**Mathematical exact landmarks**:

- At A=**3.218741088337**: a stable route-dominant and an unstable separating stationary state emerge together (saddle-node). Their leader route probability is x=0.630344336789.
- At A=**3 ln 3 = 3.295836866004**: uniform 25%-each and dominant 75%-leader states have equal *mathematical* potential, despite different observed route profiles.
- At A=**4.000000**: uniform state loses its strict local linear stability. At A=4 itself it is linearly marginal.
- Throughout 3.218741 < A < 4: equal route use **and four alternative one-route-dominant choices are simultaneously locally attracting**. Intermediate unstable fixed points separate basins.

| A | uniform locally stable? | leader preference at stable specialist | specialist potential − uniform | number of locally attracting states |
|---:|:---:|---:|---:|---:|
| 3.10 | yes | no specialized branch | — | 1 |
| 3.25 | yes | 0.708718 | −0.007078 | 5 |
| 3 ln3 | yes | 0.750000 | 0 | 5 |
| **3.50** | **yes** | **0.838725** | **+0.041389** | **5** |
| 3.90 | yes | 0.912750 | +0.147706 | 5 |
| 4.00 | marginal | 0.923783 | +0.177493 | 4 strictly attractive |
| 4.30 | no | 0.948010 | +0.271847 | 4 |

Analytic stationary shape is p=(x,(1-x)/3,(1-x)/3,(1-x)/3) where A=3 log(3x/(1-x))/(4x-1). Stability was verified with both full contrast modes. The potential Φ_A=(A/2)Σp²−Σp log(p) is a **mean-field statistical-mechanics potential, NOT a bat's payoff, energy or adaptive fitness**. This four-state discontinuity is classical Curie–Weiss–Potts first-order phase behavior, *not an original mathematical theorem of this programme*. Prior art: https://doi.org/10.1016/j.spa.2009.10.011 and https://alexxthiery.github.io/notes/potts_transition/potts.html.

## B — a tiny history dose can select a basin without a new reward

At A=3.5, eta=.2, delta=.1, kappa=1.75, start all skill vectors at zero; force L-low m times (the precommitted m-list), then iterate the deterministic conditional-mean dynamics 4,000 steps with all four routes freely available and equal reward.

| Initial forced L-low choices m | final P(L-low) | basin |
|---:|---:|---|
| 0 | .250000 | uniform |
| **1** | **.250000** | uniform |
| **2** | **.838725** | **specialized** |
| 3 | .838725 | specialized |
| 6 | .838725 | specialized |
| 12 | .838725 | specialized |

The separatrix/saddle at this A has dominant probability x=.385525, smaller three each y=.204825, skill difference d_saddle=(eta/delta)(x−y)≈**.361401**. From zero initial skills one forced route use yields d=.20; two sequential uses yield d=.38. The sharp one-versus-two contrast is restricted to these declared synthetic units/parameters. It is **not a measured bat training threshold**, a fitness result or a claim of irreversible behavior under finite stochasticity.

## C — practice that transfers across shared maneuvers is the discriminating ecology

The four routes form two elementary choice factors: H=L/R, V=low/high. A *whole-route* learner improves only the exact practised path. A *compositional module* learner improves the practised path and **two previously unpractised routes sharing one movement component**. A global familiarity model improves every route similarly.

The synthetic expected after-practice performance gains from training R1 are:

- Whole-route W: R1 .20; R2 .00; R3 .00; R4 .00.
- Shared-maneuver M: R1 .20; R2 .10; R3 .10; R4 .00.
- Generic-familiarity G: all four .10.

Precommitted diagnostic contrast **C** is the mean gain for the two one-component-overlapping unpractised routes minus the gain for the no-component-overlap route, under independently measured pre/post physical performance. Contrast D is trained-path improvement minus no-overlap improvement. Generated values above are model assumptions, not real observations.

| Declared model | mean C | mean D | synthetic runs with strictly positive two-sided 95% t lower interval for C |
|---|---:|---:|---:|
| Whole-route W | +.000852 | +.201888 | 39 / 1,000 |
| **Shared maneuvers M** | **+.099428** | **+.199707** | **992 / 1,000** |
| Generic familiarity G | +.002165 | +.001603 | 20 / 1,000 |

Simulation: 1,000 independent artificial experiments per mechanism; N=20, complete 4-animal balanced training assignments, two technical before/two technical after observations per route; independent noise SD .08; common animal-level global shift SD .04; NumPy SeedSequence root 202610081747. These detection fractions are **hypothetical precision diagnostics conditional on chosen true effects and noise, not bat-data significance or prospective biological power**.

### Modular factorization and learning-budget caveat
If horizontal and vertical component skills are updated separately, route score κ(h_H+v_V) gives exactly factorized choice probabilities P(H,V)=P(H)P(V). For eta_module=.20, kappa=2, delta=.10, **each** binary motor component independently has feedback gain 2, allowing four combinatorial stable alternatives. This is different from the whole-route four-way uniform gain 1 with eta=.20, kappa=2, delta=.10. However, the modular model updates **two component skills per flight**, and whole-route model updates one; the numeric threshold difference cannot be treated as equal-learning-budget efficiency without independent component-rate measurement.

## Independent biological prediction and protocol boundary

A valid *new* prospective animal study, separate from original PR #72, would balance which of four paths each bat practices, and measure execution performance for **all** four routes before and after, not just chosen paths. Its primary ecological signature is **partial skill transfer to unpractised one-component-overlap routes, above non-overlap and generic global familiarity controls**. The existing matched geometry families A/B (horizontal-before-vertical vs vertical-before-horizontal decisions) could later test whether the transfer survives changed order/coordinates.

Alternative explanations must be tested: perceptual similarity, shared sensory cues, generic condition changes, route reward familiarity, unequal aerodynamic difficulty. A positive performance transfer is not proof that skill **caused** choice; mediation remains separate from independent randomized performance and choice effects. Laboratory speed/time/path efficiency do not establish energetic savings or evolutionary fitness. Animal numbers, forced route tests, 3D tracking and welfare must be approved/piloted before any real trials.

**Falsifiable research question:** Is the effective object of personal 3-D route memory a complete scene-specific path, or reusable left/right and vertical maneuver elements that can be recombined when routes change?
