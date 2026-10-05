# Self-maintaining specialization synthesis v9

## Status

**CURRENT POST-JAE MECHANISM SYNTHESIS — supersedes V8.**

JAE v0.4.0 remains frozen and unchanged.

V9 adds a controlled within-individual perturbation result to the V8 storage/expression framework:

> **a controlled sensory perturbation can shift expressed movement while preserving the identity-bearing personal movement bias.**

A personal movement tendency or learned task strategy can persist as latent control information while the relevant spatial behavior is not currently expressed.

---

## 1. Starting point: specialization persists without spatial partition

The JAE programme establishes that persistent individual vertical strategies can survive without strong contemporaneous physical partitioning.

The post-JAE programme further shows in wild *Phyllostomus hastatus* that:
- low-dimensional H/V movement policy is individually repeatable;
- peer-day residual identity persists;
- policy distance does not predict dyadic vertical separation;
- individual-specific peer-context slopes are unsupported;
- stable individual policy breadth is not established.

Therefore the strongest stable empirical object remains:

[
\boxed{
\text{persistent low-dimensional personal policy bias}
}
]

rather than:
- exclusive spatial niche;
- immutable route;
- universal individual reaction slope;
- fixed complete personal distribution.

---

## 2. A second distinction is now necessary: storage versus expression

Most movement analyses observe only expressed behavior.

But a persistent individual state can exist even when the task that reveals it is absent.

Write:

[
\mathbf z_i(t)
]

for stored individual control information and

[
\mathbf x_i(t)
]

for currently expressed movement behavior.

Then:

[
\mathbf x_i(t)
=
\mathcal E(
\mathbf z_i(t),
E_t,
T_t
)
+
\epsilon_i(t),
]

where:
- (E_t) = environment;
- (T_t) = current task class;
- (mathcal E) = context-dependent expression operator.

Crucially:

[
\mathbf z_i(t) \text{ can persist}
]

even when:

[
\mathcal E(\mathbf z_i,E_t,T_t)
]

does not currently reveal that individual state.

Thus failure to observe a specialized phenotype at one time does not imply that the underlying individual specialization has been erased.

---

## 3. Internal evidence for persistent personal policy bias

### Laboratory *Rhinolophus nippon*

Across obstacle configurations:
- full 8-D policy identity: `K=+0.94356`, `p=0.0001`;
- one training-derived latent dimension is sufficient for held-out identity;
- transparent FlightIntensity: `K=+0.49656`, `p=0.0003`;
- transparent two-axis identity: `K=+0.55428`, `p=0.0001`;
- calibrated residual identity after removing the transparent two-axis span is unsupported.

This supports a low-dimensional portable personal bias.

### External *Carollia perspicillata*

Fixed Rhino-derived axes transfer to an independent system:
- 2-D `K≈+0.348`, 6/7 positive, `p=0.0007`;
- FlightIntensity alone `K≈+0.368`, `p=0.0014`.

Thus the architecture recurs, although its exact dimensionality/orientation is not universal.

---

## 3b. The portable policy has predictive geometry, not only identity

A stronger post-primary test asks whether the personal coordinate estimated from other obstacle configurations can predict the bat's coordinate in a completely held-out configuration **without refitting coefficients**.

For target environment e:

- estimate each bat's transparent 2-D coordinate from all other environments;
- predict the held-out coordinate directly from that training-only personal coordinate.

Observed:

- 2-D no-refit held-out R² = **0.46659**;
- one-sided permutation p = **0.0002**;
- median cosine between predicted and observed held-out coordinates = **0.896**;
- 25 held-out bat × environment centroids.

Axis-specific:

- FlightIntensity no-refit R² = **0.50222**, p = **0.0012**;
- ManeuveringExtent no-refit R² = **0.38828**, p = **0.0041**.

The geometry among individuals also transfers.

For held-out bat pairs:

- pair-displacement-vector R² = **0.57972**;
- permutation p = **0.0001**;
- median predicted-versus-observed vector cosine = **0.863**;
- **97.1%** of pair × environment vectors have positive cosine.

Therefore the portable component is not merely enough to classify identity.

> **The relative arrangement of individuals in policy space predicts how they will be arranged in an unseen movement task.**

This is the strongest evidence that the persistent object behaves like a genuine low-dimensional behavioral coordinate rather than a dataset-specific fingerprint.

### Target-normalization boundary

The result is not created solely by using held-out-environment scale information.

When target SD is removed and only training-derived scaling is used:

- target-centered/training-scaled 2-D K = **+0.55797**;
- 5/5 positive;
- p = **0.0001**.

Under fully training-only global mean/SD, with no target mean or SD:

- 2-D K = **+0.51604**;
- 5/5 positive;
- p = **0.0001**.

Thus the stable individual signal survives even when the target domain contributes no scaling parameters.

The strongest recurrent component is especially concentrated on FlightIntensity.

---

## 4. Wild evidence: the personal center persists but realization is flexible

Wild *P. hastatus* bivariate H/V carrier:

### 2022
- `K_2D=+0.65314`;
- 32/34 positive;
- `p=0.0001`.

### 2023
- `K_2D=+0.27052`;
- 9/11 positive;
- `p≈0.033`.

Variance decomposition:

### 2022 equal-axis mean
- individual = **52.5%**
- day = **17.3%**
- residual = **30.1%**

### 2023 equal-axis mean
- individual = **33.6%**
- day = **1.7%**
- residual = **64.7%**

The stable individual component is therefore real, but the expressed session-level behavior can be much more variable in some years.

---

## 5. The unresolved cloud around the center is not explained by simple alternatives

Several separately frozen diagnostics fail as general rules.

### Fixed prior-history centroid

Average prediction improves relative to the exchangeability pipeline, but only:
- 16/30 individuals in 2022;
- 4/7 in 2023;

benefit from the personal-past forecast.

The >=70% consistency rule fails.

### Individual peer-context reaction norm

Held-out individual slopes do not outperform the common slope.

2022:
- `G_RN=-0.0634`;
- 6/21 positive;
- `p=0.1163`.

2023:
- `G_RN=-0.0833`;
- 3/6 positive;
- `p=0.1595`.

### Stable personal policy breadth

2022:
- `K_W=+0.1814`;
- 11/16 positive;
- `p=0.0899`.

2023:
- structural STOP.

Therefore the current field evidence establishes the persistent **location/bias** of individuality more strongly than a fixed personal slope, width or deterministic transition rule.

---

## 6. Learning changes expression without necessarily erasing individuality

The Yamada/Ito learning experiment provides a direct bridge.

Naive bats change movement behavior over repeated obstacle exposure.

After removing condition × trial population shifts, personal state information persists overall.

Thus:

[
\text{shared learning update}
+
\text{persistent individual information}
]

can coexist.

The condition-level evidence is heterogeneous, so expression strength itself may be context dependent.

This motivates:

[
\mathbf x_{i,e,t}
=
\boldsymbol\mu_{e,t}
+
\alpha_{e,t}\boldsymbol\theta_i
+
\mathbf h_{i,e,t}
+
\epsilon_{i,e,t},
]

where:
- (oldsymbol\theta_i) = persistent individual prior/bias;
- (alpha_{e,t}) = how strongly the context reveals that prior;
- (mathbf h_{i,e,t}) = learned task/scene-specific component.

Only the persistent personal component is strongly established; (alpha) is not yet identified as a stable causal parameter.

---

## 6b. Controlled sensory perturbation: the personal bias survives an imposed shift

A separate frozen public-data reanalysis of Taub & Yovel (2020) uses six *Pipistrellus kuhlii* exposed to a source-defined within-individual sensory perturbation sequence.

The source primary movement endpoint is 3-D angle of attack.

The public workbooks contain source-native bat-condition means derived from per-flight 3-D angle summaries.
The new reanalysis opened only those bat-condition mean formula values after freezing the estimator.

### P1 — pre-perturbation bias -> masker conditions

Use:
- no masker / styrofoam baseline;
- 30-cm masker;
- 10-cm masker.

For each condition, subtract the equal-bat condition mean.
The centered no-masker value is the pre-perturbation personal predictor.

Exact identity-retention result:

- overall identity advantage: **K = +4.941 deg**;
- 30-cm masker: **K = +8.004 deg**;
- 10-cm masker: **K = +1.878 deg**;
- **5/6 bats positive**;
- all **6! = 720** baseline-label permutations enumerated;
- exact one-sided **p = 0.04028**;
- no-refit centered prediction **R² = 0.2855**.

Baseline-to-target ordering:
- 30 cm: Pearson **r = 0.927**, Spearman **rho = 0.771**, pair-order accuracy **0.800**;
- 10 cm: Pearson **r = 0.487**, Spearman **rho = 0.543**, pair-order accuracy **0.733**.

Thus stronger sensory challenge attenuates the personal ordering but does not erase the frozen identity-retention signal.

### P2 — masker removal/control -> masker re-addition under the same foam target

Five bats share the same 30-cm foam-masker design.
Alvin was excluded before outcome opening because the source used 20 cm for Alvin's foam condition.

Compare:
- four-day foam-target / no-masker control;
- foam target + 30-cm masker.

Results:

- **K = +6.779 deg**;
- **5/5 bats positive**;
- all **5! = 120** permutations enumerated;
- exact one-sided **p = 0.025**;
- no-refit **R² = 0.6414**;
- Pearson **r = 0.957**;
- Spearman **rho = 0.900**;
- pair-order accuracy **0.900**.

This is the cleanest current perturbation result.

The population operating state changes with sensory context, but the relative individual movement bias remains recognizable.

Therefore:

[
\boxed{
\text{condition shift}
+
\text{persistent individual bias}
}
]

is now directly supported in a controlled within-individual manipulation.

This does **not** establish that the retained bias is learned, biomechanical or neural in origin.

It also does not establish that the one-dimensional angle-of-attack bias is the same latent coordinate as the Rhino I/M policy or the wild H/V carrier.

---

## 7. Barchi: learned scene solutions can be stored and retrieved

External *Eptesicus fuscus* obstacle-reset evidence shows:

- individual stereotyped routes form with familiarity;
- changing release point does not erase the learned route;
- after about one month, returning to the same obstacle geometry retrieves the familiar route;
- mirror-reconfigured geometry produces new stable routes.

This establishes a persistent **scene-specific learned solution**:

[
m_{i,e}.
]

It can be stored over an interval and retrieved when the familiar scene returns.

It is not an immutable morphological route because the same animal can acquire a different solution after reset.

---

## 8. Taub & Yovel: a task-class policy can remain latent for six months

The *Pipistrellus kuhlii* clutter-learning experiment adds a different level.

Published design:
- prolonged first exposure to extreme clutter;
- subsequent return to a much less cluttered large room for about six months;
- later reintroduction to clutter.

Published result:
- bats gradually acquired a clutter-adapted pre-takeoff sensorimotor strategy;
- after the long interval away from the clutter task, the learned strategy was expressed immediately when clutter returned;
- a subset expressed a similar strategy in an acoustically enhanced clutter environment.

The important mechanistic fact is not simply “memory lasts six months.”

It is:

> **the specialized policy did not need to be continuously expressed in order to remain available for later expression.**

Thus:

[
\text{maintenance}
\neq
\text{continuous phenotype}.
]

The learned state can be behaviorally latent.

---

## 9. The Taub public archive cannot provide a new confirmatory individual-identity p-value

An outcome-blind public-data programme inspected only metadata/schema.

It established five identifiable individuals and stage-4 same/enhanced environment assignment.

A condition-preserving individual-identity permutation would have only:

[
3!\times2!=12
]

possible label mappings.

Therefore:

[
p_{min}=1/12=0.0833.
]

A conventional exact `p<=0.05` individual recall primary is mathematically unattainable.

The prospective programme was stopped before IPI outcome opening.

This protects the published perturbation evidence from being converted into an underidentified post-hoc “replication.”

---

## 10. Revised three-level memory/control hierarchy

The combined evidence is now best represented by three persistent information layers.

### Level 1 — portable personal policy bias

[
\boldsymbol\theta_i
]

A cross-context individual tendency in how movement is controlled.

Evidence:
- Teshima/batter cross-configuration transfer;
- held-out policy-coordinate and pair-geometry prediction;
- Carollia external validation;
- wild low-dimensional carrier;
- controlled *P. kuhlii* sensory-perturbation retention.

### Level 2 — learned task-class policy

[
\boldsymbol\lambda_{i,k}
]

A learned strategy for a recurring class of problems such as clutter navigation.

Evidence:
- Taub & Yovel long-term clutter-strategy recall;
- partial expression in enhanced clutter.

This layer can remain latent when the task class is absent.

### Level 3 — learned scene-specific solution

[
m_{i,e}
]

A route/lane/solution tied to a particular physical scene.

Evidence:
- Barchi route learning;
- retrieval in the same scene;
- replacement under mirror reset.

The realized bout is generated by all three plus current context:

[
\boxed{
\mathbf x_{i,e,t}
=
F(
E_e,
\boldsymbol\theta_i,
\boldsymbol\lambda_{i,k(e)},
m_{i,e},
\eta_t
)
+
\epsilon_{i,e,t}
}
]

---

## 11. This resolves the original maintenance paradox

Original puzzle:

> If bats do not keep occupying mutually exclusive vertical niches, how can individual specialization remain stable?

The answer no longer requires continuing ecological separation.

Information can be stored in the animal.

A persistent behavioral difference can be maintained through:
- stable sensorimotor bias;
- long-lived task knowledge;
- scene memory;
- stable physiology/morphology;
- combinations of these.

Current conspecifics do not need to keep “pushing” the individual into its specialized state.

The physical niche is an **expression surface**, not necessarily the storage medium.

---

## 12. The strongest new conceptual distinction

The post-JAE programme now separates four concepts:

[
\boxed{
\text{storage}
\neq
\text{expression}
\neq
\text{spatial segregation}
\neq
\text{active avoidance}
}
]

### Storage

Persistent information carried by the individual.

### Expression

How that stored information is manifested in the current task/environment.

### Spatial segregation

Whether realized trajectories occupy different volumes.

### Active avoidance

Whether current co-presence changes relative position.

These can vary independently.

This is the clearest answer to why specialization can persist without spatial partitioning.

---

## 13. Why this is stronger than “personality”

Calling the result “personality” would hide the mechanism.

A personality label often collapses:
- stable mean behavior;
- plasticity;
- learned task knowledge;
- context-specific expression.

The current evidence instead supports a hierarchy in which:
- the persistent individual bias is low-dimensional;
- learned task state can persist latently;
- learned route state can be scene specific;
- momentary expression remains flexible.

Therefore the more precise object is:

> **persistent control information with context-gated expression.**

---

## 14. Remaining decisive causal fork: what creates the persistent bias?

The reversible sensory result closes the earlier question of whether a controlled environmental shift necessarily erases the individual bias: it does not.

The main unresolved fork is now the **origin of the bias itself**.

### Stable biomechanics / physiology

Prediction:
- reversible physical loading shifts the expressed coordinate within individual;
- removing the load restores the pre-load relative ordering;
- same-individual wing loading / morphology / performance predicts the portable bias.

### Long-lived learned / developmental sensorimotor state

Prediction:
- extended retraining can alter the persistent coordinate even without changing morphology;
- task-class or scene memories can be retrieved after periods without expression;
- early experience or controlled retraining changes later personal bias.

### Mixed architecture

A plausible remaining model is:

[
\theta_i
=
\theta_i^{biomechanics}
+
\theta_i^{development}
+
\theta_i^{long-term\ learning}.
]

The next decisive experiment should manipulate biomechanics and learning history orthogonally within the same identified individuals while repeatedly measuring the portable coordinate.

---

## Bottom line

V7 concluded that the strongest stable empirical object is a low-dimensional personal policy bias.

V8 added the key temporal insight that individual-specific control information can persist without continuous expression.

V9 adds the controlled perturbation result:

> **environmental manipulation can move expressed movement while preserving the identity-bearing personal movement bias.**

Therefore persistent specialization need not be maintained by continuous spatial partition, continuous route use, or one fixed behavioral output.

The strongest current architecture is:

[
\boxed{
\text{portable personal bias}
+
\text{context-dependent expression}
+
\text{learned task/scene information}
\rightarrow
\text{realized movement}
}
]

The remaining mechanistic problem is no longer whether the bias survives change.

It is **where that persistent bias comes from**.
