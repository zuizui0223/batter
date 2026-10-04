# Low-dimensional personal-policy synthesis v1

## Status

**POST-PRIMARY MECHANISM SYNTHESIS.**

This file synthesizes already-opened prospective and post-primary results.
It does not modify JAE v0.4.0 and does not promote exploratory diagnostics to confirmatory status.

## Core question

How can individual specialization persist when individuals need not continuously partition three-dimensional space?

The current evidence no longer supports the simplest answer:

`exclusive personal space -> persistent specialization`.

For *Rhinolophus nippon*, it also does not require an irreducibly high-dimensional trajectory fingerprint.

A more specific current model is:

[
x_{i,e,t} = mu_e + 	heta_i v + lambda_e L_t + h_{i,e} + arepsilon_{i,e,t}.
]

Where:

- `mu_e`: configuration/task mean;
- `theta_i`: stable individual position on a transferable personal-policy axis;
- `v`: species/system-specific direction in movement-feature space;
- `L_t`: familiarity / learning state;
- `lambda_e`: environment-dependent learning response;
- `h_i,e`: configuration-specific personal solution / lane / route realization;
- `epsilon`: trial-scale residual variation.

This is a decomposition of evidence, not a uniquely identified dynamical law.

---

# 1. Evidence for a portable individual parameter theta_i

Authoritative *R. nippon* cross-configuration movement primary:

- full 8-D policy advantage: `K = +0.9435601`;
- 5/5 individuals positive;
- one-sided permutation `p = 0.0001`;
- leave-one-environment robustness retained positive individual means for all five bats under every one-environment omission.

Thus individual identity is not tied to one obstacle arrangement.

## One-dimensional sufficiency

Training-only leave-one-environment PCA1:

- one dimension sufficient;
- 5/5 positive;
- `p = 0.0006`;
- median training variance explained by PC1 = **46.68%**.

Training-only supervised identity axis:

- one dimension sufficient;
- 5/5 positive;
- `p = 0.0021`.

Therefore a one-dimensional axis can retain cross-configuration identity even though it does not explain all behavioural variance.

## Transparent scalar approximation

Define without fitted weights:

[
FlightIntensity =
rac{
z(v_{med})+
z(v_{90})+
z(|v_z|_{med})+
z(|v_z|_{90})
}{4}.
]

Result:

- `K = +0.4965562`;
- 5/5 positive;
- `p = 0.0003`.

It captures:
- 51.8% of the PCA1 identity advantage;
- 52.6% of the full 8-D identity advantage.

So an interpretable movement-intensity scalar captures a substantial fraction of the portable individual signal.

---

# 2. What the dominant axis means

Median squared PCA1 loading across held-out-environment folds:

- median 3-D speed: 0.211;
- p90 3-D speed: 0.231;
- median absolute vertical speed: 0.215;
- p90 absolute vertical speed: 0.230;
- median turn rate: 0.005;
- p90 turn rate: 0.074;
- path efficiency: 0.001;
- vertical range: 0.029.

Approximately 89% of squared loading lies in the four speed / vertical-speed features.

Post-frozen component decomposition:

### Total speed

- `K = +0.5212092`;
- 5/5 positive;
- `p = 0.0003`.

### Vertical speed

- `K = +0.4409791`;
- 5/5 positive;
- `p = 0.0012`.

### Relative verticality

[
Verticality = VerticalSpeed - Speed.
]

- `K = +0.0003302`;
- 3/5 positive;
- `p = 0.4093`.

Therefore the dominant personal axis is not well described as a relative preference for vertical motion.

The current descriptive label is:

> **flight intensity / movement vigor**

because overall speed and vertical-speed magnitude rise and fall together across individuals.

---

# 3. theta_i behaves like more than a classifier embedding

## Rank stability

Across obstacle configurations, pairwise FlightIntensity ordering:

- equal-pair accuracy = **0.8217**;
- null approximately 0.50;
- `p = 0.0048`;
- 9/10 bat pairs exceed chance ordering accuracy.

The main unstable near-tie is B versus C.

Descriptive full-data theta ordering:

[
A > C approx B > E > D.
]

## Held-out magnitude calibration

Using only other environments to estimate `theta_i,-e` and predicting pairwise differences in held-out environment e:

- through-origin calibration slope:
  `beta = 1.0314`;
- Pearson `r = 0.5548`;
- raw pair x environment sign accuracy = 0.8286;
- equal-pair sign accuracy = 0.8217;
- `p_beta = 0.0014`;
- `p_r = 0.0162`;
- `p_sign = 0.0065`.

The slope is descriptively close to one, but no equivalence interval was predeclared.

This supports:

> a scalar estimated in other configurations predicts not only individual ordering but a meaningful amount of the magnitude of held-out individual differences.

That is the strongest current reason for treating `theta_i` as a personal policy parameter rather than merely an identification score.

---

# 4. Configuration-specific realization h_i,e

Within the same obstacle configuration, absolute-coordinate route identity was supported:

- `A = +0.2259341`;
- `p = 0.0003`.

But:

- start-centered route identity failed;
- chord-residual shape identity failed;
- start point alone failed;
- end point alone failed;
- displacement vector failed;
- centroid-centered route failed / was borderline and did not satisfy the frozen primary identity rule.

The strongest post-primary carrier was absolute trajectory centroid / lane placement.

Thus the task-specific term `h_i,e` is currently better interpreted as:

> configuration-specific lane / spatial placement,

not as one invariant memorized curve.

The public Teshima archive does not recover cross-environment temporal order, so it cannot identify reset or relearning time.

---

# 5. Independent learning evidence makes theta_i unlikely to be a purely immutable constant

Yamada et al. 2020, *Scientific Reports*, studied 14 naive *Rhinolophus ferrumequinum nippon* individuals over 12 repeated flights.

Published results:

- all bats were naive to the tested obstacle layout;
- the first flight represented unfamiliar space;
- in the acoustically permeable condition, mean maximum speed rose from approximately 2.5 to 3.4 m/s from flight 1 to flight 12;
- in the reflective condition the shift was much smaller, approximately 2.6 to 2.8 m/s;
- the flight-number x acoustic-condition interaction was significant;
- pulse emission strongly decreased with repeated experience in both conditions.

This establishes that movement/sensing control in the same species complex is experience-dependent and that the magnitude of learning-related speed change depends on environmental information structure.

It does **not** establish that the present obstacle-flight `theta_i` changes with learning, because the two studies do not share identified individuals and the Yamada raw individual series are not publicly recoverable from the indexed supplement.

Therefore the strongest admissible bridge is:

[
personal control = stable individual prior + plastic familiarity state,
]

not:

`theta_i is genetically fixed`.

---

# 6. Independent reset literature supports a separate learned task state

Barchi, Knowles & Simmons 2013 (*Eptesicus fuscus*) reported:

1. six bats developed individually stereotyped flight paths with familiarity;
2. after learning, unfamiliar release points did not erase the previously learned path;
3. after one month, bats returned to the original obstacle configuration resumed their accustomed path;
4. bats exposed to a mirror-image obstacle configuration rapidly developed new stable paths differing from their original ones.

This qualitative architecture is compatible with:

[
stable personal prior; 	heta_i
+
configuration-specific learned state; h_{i,e}.
]

The Barchi raw trajectory archive was not located, so this remains an external literature bridge rather than a re-analysis.

---

# 7. What is *not* currently supported

## Not universal across bat species

The same Teshima archive includes *Miniopterus fuliginosus*.

For Miniopterus:

- full 8-D cross-configuration identity: unsupported;
- fixed Rhino FlightIntensity axis: unsupported;
- fixed Rhino PC1 axis: unsupported;
- Mini-specific leave-one-environment PCA1: unsupported
  (`K=-0.1688`, `p=0.2529`, 2/4 positive).

Mini PC1 still explains substantial behavioural variance (~58.8% median), but it does not carry stable cross-configuration individual identity.

Therefore:

> low-dimensional variance is not the same thing as low-dimensional individual specialization.

The one-parameter personal policy is currently a *Rhinolophus*-system result, not a universal bat law.

## Not simple body mass

A separate four-panel body-mass donor-gradient analysis supported the predicted morphology-transfer gradient in 0/4 panels.

This does not rule out wing loading, muscle physiology, age, sensorimotor development or morphology generally.

## Not an independent pulse/sensing parameter after strict control

Pulse identity transferred across configurations in naive post-primary analyses.

However, after cross-fitted nuisance removal of movement + route predictors:

- residual pulse identity = +0.1179;
- 3/5 positive;
- `p = 0.2032`.

Therefore the current synthesis does **not** require an additional independent sensing parameter.

Pulse individuality may covary with the movement policy.

---

# 8. Current ecological answer

The current evidence supports a stronger answer to the original JAE maintenance question:

> Individuals need not maintain specialization by occupying mutually exclusive volumes of space. At least in one horseshoe-bat system, individuals carry a portable low-dimensional movement-intensity parameter across different obstacle configurations. Environmental geometry determines the available solution space, learning/familiarity can shift the operating state, and individual-specific task solutions determine realized lanes or routes.

In compact form:

[
oxed{
behaviour =
environment
+
personal control parameter
+
learning state
+
task-specific solution
}
]

Spatial exclusion is therefore one possible ecological consequence of personal policies, not a necessary maintenance mechanism.

---

# 9. Relation to the "pi" analogy

The present result argues **against** the strongest version of the analogy that bat flight is irreducibly complicated and cannot be compressed mathematically.

For *R. nippon*:

- a one-dimensional latent axis is sufficient for held-out identity;
- a transparent speed/vertical-speed scalar is strongly predictive;
- the scalar has stable pairwise ordering across configurations;
- its held-out pairwise magnitude calibration is positive and approximately unit-slope descriptively.

So the current problem is not:

> no mathematical rule can reproduce the bat.

It is:

> the realized 3-D trajectory is a high-dimensional output of a potentially low-dimensional personal control state interacting with environment and experience.

The unresolved issue is causal origin of that personal parameter.

---

# 10. Strongest next discriminator

The next decisive data would follow the **same identified individuals** through:

1. an unfamiliar task;
2. repeated learning;
3. a task reset / obstacle reconfiguration;
4. optional biomechanical perturbation.

Then fit/test whether:

[
	heta_i(t)
=
	heta_i^0
+
Delta_i^{learn}(t)
+
Delta_i^{load}(t).
]

Key questions:

- Does individual rank remain stable while the population mean shifts with learning?
- Does a mirrored/new task change `h_i,e` while retaining `theta_i`?
- Does added load shift `theta_i` within individual?
- After removing load, does the old `theta_i` return?

That design separates:
- morphology/performance;
- learned policy;
- task-specific route memory

far more directly than another observational decomposition of the current 45 trajectories.
