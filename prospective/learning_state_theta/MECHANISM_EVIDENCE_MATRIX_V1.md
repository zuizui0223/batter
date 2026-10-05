# Mechanism evidence matrix v1

## Status

**Cross-programme evidence synthesis.**

Branch:
`prospective/learning-state-theta-v1`

Purpose:
separate what is directly supported, what is weakened, what is stopped for identifiability, and what remains causally unresolved.

This matrix does not modify JAE v0.4.0.

## Evidence classes

- **CONFIRMATORY / FROZEN PRIMARY** — outcome opened only after the relevant contract/support gates were frozen.
- **PROSPECTIVE SUPPORT / STOP** — prospectively frozen auxiliary programme.
- **POST-PRIMARY DIAGNOSTIC** — mechanism refinement after a primary result; not independent confirmation.
- **EXTERNAL LITERATURE BRIDGE** — published source result not re-analysed as a frozen primary.

---

| Mechanism / explanation | Prediction | Evidence | Status | Current interpretation |
|---|---|---|---|---|
| **Persistent exclusive 3-D spatial partition** | Individual specialization requires conspecifics to occupy persistently separate volumes | JAE co-use/separation analyses; no positive S separation; extra separation upper bounds ~1–2 m | **WEAKENED / NOT NECESSARY** — JAE frozen primary family | Persistent personal vertical organization does not require continuing spatial exclusion |
| **Contemporaneous avoidance keeps individuality apart** | When animals co-use space, individual organization should weaken or extra separation should appear | JAE co-use upper-bound analyses | **UNSUPPORTED AS NECESSARY MAINTENANCE** | Specialization can persist while individuals overlap |
| **Simple fixed personal route memory** | Same individual should preserve translation-invariant route shape | Teshima Rhino Primary A initially positive; start-centered and chord-residual diagnostics fail | **WEAKENED** — primary absolute-route signal survives, invariant shape does not | Literal curve memory is not the best carrier |
| **Configuration-specific lane / placement reuse** | Same individual should repeatedly occupy a similar lane within the same obstacle geometry | Teshima absolute-coordinate route identity A=+0.2259, p=.0003; route centroid strongest post-primary carrier | **SUPPORTED DESCRIPTIVELY** | Task-specific spatial realization exists, mainly as placement/lane rather than invariant curvature |
| **Stable cross-configuration movement policy** | Individual identity should transfer to unseen obstacle configurations after removing environment means | Teshima Rhino Primary B K=+0.9436, p=.0001, 5/5 positive | **SUPPORTED — FROZEN PRIMARY** | A portable individual policy/performance signature exists |
| **Irreducibly high-dimensional personal flight rule** | Most/all measured dimensions should be required for held-out identity | Training-only PCA/identity subspace: d=1 sufficient | **WEAKENED** | In Rhino, the portable component is surprisingly low-dimensional |
| **One-dimensional personal movement-intensity axis** | A single scalar should identify individual across configurations | PCA1 d=1; transparent FlightIntensity K=+.4966, p=.0003, 5/5 | **SUPPORTED** — post-primary dimensionality/interpretable diagnostic | Dominant carrier resembles a movement-vigor axis |
| **Scalar is merely a classifier embedding** | Scalar may identify bats but should not predict magnitude of unseen differences | Held-out magnitude calibration beta=1.031, r=.555; p_beta=.0014, p_r=.0162 | **WEAKENED** | Scalar behaves more like a transferable personal control coordinate |
| **Relative vertical preference is the main scalar** | Vertical movement relative to total speed should transfer | Verticality = VerticalSpeed − Speed: K≈0, p=.409 | **UNSUPPORTED** | Dominant axis is broad vigor/intensity, not relative verticality |
| **Overall speed component** | Faster/slower tendency transfers across configurations | speed-only K=.5212, p=.0003, 5/5 | **SUPPORTED** | Major component of personal policy |
| **Vertical-speed magnitude component** | Stronger/weaker vertical movement magnitude transfers | vertical-speed-only K=.4410, p=.0012, 5/5 | **SUPPORTED** | Covaries with common vigor axis |
| **Scale-free geometry contributes** | Identity survives removal of time, speed and absolute spatial scale | geometry-only K=.3886, p=.0153, 5/5 | **SUPPORTED BUT ENVIRONMENT-SENSITIVE** — post-primary | Maneuver geometry contributes, but is less robust than full movement policy |
| **Independent sensing/pulse policy** | Pulse identity remains after proper held-out control for movement/route | naive pulse identity positive; strict cross-fitted nuisance residual P=.1179, p=.2032, 3/5 | **UNSUPPORTED AS INDEPENDENT PARAMETER** | Pulse individuality may covary with movement policy |
| **Simple body mass generates personal policy** | Similar-mass donors should transfer organization better | four-panel mass gradient 0/4 predicted effects | **UNSUPPORTED AS GENERAL SIMPLE PROXY** | Does not rule out wing loading, muscle condition, age, etc. |
| **Broad early enrichment determines history carrier** | Randomized enriched vs impoverished rearing should alter later personal-history strength | Rachum randomized contrast p≈.324 | **UNSUPPORTED** | Broad early environment is not enough to explain carrier strength |
| **Slow monotonic formation of individuality** | Self-history advantage should gradually rise from weak/absent to strong | Harten first-flight predeclared monotonic formation rule failed; advantage already positive at earliest estimable days | **UNSUPPORTED** | Individual solution appears rapidly rather than via a common slow ramp |
| **Rapid early symmetry breaking / lock-in** | Personal history becomes informative very early and remains so | Harten earliest estimable self-history positive; later 12/14 positive | **SUPPORTED AS ARCHITECTURE, NOT UNIQUE CAUSE** | Rapid establishment followed by reuse is plausible |
| **Personal policy is completely fixed / immutable** | Learning should shift population mean without altering personal state expression | Yamada overall personal speed-state persistence supports stable component, but strong-learning condition loses calibrated rank persistence | **WEAKENED** | Personal prior exists but expression is plastic/context-dependent |
| **Learning completely overwrites individual differences** | Trial-12 state should be no closer to own trial-1 than others | Yamada K=+.5277, p=.0052, 12/14 positive | **REJECTED FOR OVERALL SCALAR PRIMARY** | Shared learning shift coexists with persistent personal information |
| **Stable prior + shared learning shift** | Remove condition×trial mean; late state remains closer to own early state | Yamada prospective scalar primary supported | **SUPPORTED — FROZEN PRIMARY** | Best current learning architecture |
| **Expression strength is context-dependent** | Persistence differs across information/learning contexts | reflective K=.8797 p=.0016, 7/7; permeable K=.1758 p=.259; direct ΔK p=.082 | **SUGGESTIVE, NOT CONFIRMED** | `alpha_context` is a high-value unresolved mechanism |
| **Universal one-dimensional bat law** | Same scalar/low-dimensional identity should transfer across species | Mini full 8-D fail; Rhino scalar fail in Mini; Mini-specific PCA1 fail | **UNSUPPORTED** | Low-dimensional personal policy is species/system contingent |
| **Task-specific learned solution layered on personal prior** | Environment changes realized route while higher-level personal policy persists | Teshima: route placement config-specific + policy transfers; Barchi literature mirror/reset architecture | **SUPPORTED AS SYNTHESIS** | Best current two-level model |
| **Morphology/physiology is the source of theta** | Individual morphology should map to policy axis | same-individual morphology crosswalk unavailable; body mass proxy fails elsewhere | **UNRESOLVED / IDENTIFIABILITY STOP** | Still plausible, but not demonstrated |
| **Long-lived learned/developmental policy is the source of theta** | Stable personal axis should survive tasks yet be modifiable by experience | cross-config transfer + Yamada learning persistence; no direct same-individual origin manipulation | **PLAUSIBLE / UNRESOLVED** | Strong candidate, not causally separated from physiology |

---

# Current minimum model

The evidence is most compactly represented by:

[
x_{i,e,t}
=
mu_{e,t}
+
alpha_{e,t}	heta_i
+
h_{i,e,t}
+
arepsilon_{i,e,t}.
]

Where:

- `mu_e,t` — common environment / familiarity / learning-state effect;
- `theta_i` — latent personal control prior;
- `alpha_e,t` — context-dependent expression of the personal prior;
- `h_i,e,t` — task-specific personal solution / lane / history term;
- `epsilon` — residual trial variation.

## What is directly supported

### theta_i

Supported by:
- Rhino cross-configuration frozen Primary B;
- one-dimensional held-out identity;
- transparent FlightIntensity transfer;
- pairwise rank stability;
- held-out magnitude calibration;
- Yamada trial-1 -> trial-12 scalar self-history persistence.

### mu_e,t

Supported by:
- configuration means in Teshima;
- strong published/reproduced learning shift in Yamada.

### h_i,e,t

Supported descriptively by:
- same-configuration absolute route/lane identity;
- loss of literal-route identity after translation/shape normalization;
- external reset literature showing task-specific route rebuilding.

### alpha_e,t

Currently only suggested by:
- strong reflective persistence;
- weak permeable condition-specific persistence;
- larger mean learning shift in permeable condition.

The direct condition contrast is not significant at 0.05.

Thus `alpha` is the key unresolved term.

---

# What the current evidence rules out as the main story

Do not lead with:

1. **individuals specialize because they continuously exclude one another in space**;
2. **each bat memorizes one fixed geometric route and repeats it forever**;
3. **flight individuality is an irreducibly high-dimensional mathematical fingerprint**;
4. **simple body mass explains the individual policy**;
5. **pulse timing is an independent latent policy after strict movement control**;
6. **individuality always forms slowly with repeated experience**;
7. **one universal scalar explains individuality across bat species**.

---

# Current ecological story

> Individuals can remain specialized without maintaining exclusive spatial niches because the persistent object is not necessarily a place. In one horseshoe-bat system, a portable low-dimensional movement-intensity tendency survives changes in obstacle geometry and remains informative across a naive-to-familiar learning transition. Environment and experience move the common operating state, while personal policy and task-specific solutions jointly determine realized movement.

This is more specific than:

> specialization need not partition space.

It proposes a candidate maintenance architecture:

> **persistent personal control prior + plastic state change + task-specific solution.**

---

# Highest-value unresolved causal fork

The remaining central fork is the origin and modifiability of `theta_i`.

## A. Stable biomechanics / physiology

Prediction:
- reversible physical loading should shift the measured policy within individual;
- removing the load should restore the original individual state/order;
- morphology/wing loading should predict theta when measured on the same identified animals.

## B. Long-lived learned / developmental sensorimotor policy

Prediction:
- a reset/new task changes task solution `h` while personal policy partly transfers;
- extended retraining can alter `alpha theta` or theta itself even without physical manipulation;
- old policy may reappear under return-to-original context.

## C. Mixed architecture

Most biologically plausible current candidate:

[
	heta_i =
	heta_i^{biomechanics}
+
	heta_i^{development}
+
	heta_i^{long-term\ learning}.
]

The decisive next experiment is not another decomposition of the same archive.

It is a **within-individual reversible perturbation / reset study** that changes one causal component while tracking the same policy scalar before, during and after perturbation.
