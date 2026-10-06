# Solution abundance × history-dependent specialization theory v1

## Status

**MECHANISTIC THEORY / PROSPECTIVE PREDICTION.**

This note develops the existing decentralized-route Pólya model into an explicit solution-abundance prediction.

It does not claim that solution abundance has already been measured in the current bat experiments.

---

# 1. Setup

Suppose a recurrent movement task admits (K) functionally adequate solutions.

For individual (i), after (n) experiences:

[
P_i(kmid n)
=
rac{a+N_{ik}(n)}{Ka+n},
]

where:
- (k=1,ldots,K);
- (a>0) is symmetric baseline pseudo-count per solution;
- (N_{ik}) is the individual's accumulated use of solution (k).

All individuals begin exchangeable.

No:
- competition;
- territorial exclusion;
- individual fixed parameter;
- innate solution preference

is required.

The limiting personal solution weights are:

[
	heta_isim Dirichlet(a,ldots,a).
]

---

# 2. Exact individual-specialization advantage

For two independent future choices from the same individual:

[
P_{same}
=
rac{a+1}{Ka+1}.
]

For two choices from different individuals:

[
P_{between}
=
rac{1}{K}.
]

Therefore the same-individual matching advantage is:

[
oxed{
Delta(K,a)
=
rac{K-1}{K(Ka+1)}
}
]

with:

[
Delta>0quad	ext{for every }K>1.
]

Thus **more than one feasible solution is sufficient for history to create persistent individuality**, even from identical starting conditions.

---

# 3. But "more solutions -> more specialization" is not generally true

Treating (K) continuously for intuition:

[
rac{partial Delta}{partial K}
=
-rac{aK^2-2aK-1}{K^2(Ka+1)^2}.
]

The interior maximum occurs at:

[
oxed{
K^*
=
1+sqrt{1+rac{1}{a}}
}
]

under fixed per-solution pseudo-count (a).

Therefore:

- (K=1): individuality impossible;
- small-to-moderate (K): extra feasible solutions create scope for personal lock-in;
- sufficiently large (K): the same-individual matching advantage declines because personal history is diluted across too many alternatives.

This predicts an **intermediate-abundance maximum**.

Examples:

| (a) | continuous (K^*) | best nearby integer K |
|---:|---:|---:|
| 1.0 | 2.41 | 2 |
| 0.5 | 2.73 | 3 |
| 0.25 | 3.24 | 3 |
| 0.10 | 4.32 | 4 |
| 0.05 | 5.58 | 6 |

This is an important correction to a naive "behavioral opportunity always increases specialization" story.

---

# 4. Why the abundance prediction depends on what is held constant

The intermediate maximum assumes (a) is fixed **per available solution**.

But a different biological manipulation may keep total exploration/concentration mass fixed.

Let:

[
A=Ka
]

be a fixed total prior concentration and set:

[
a=A/K.
]

Then:

[
Delta(K,A)
=
rac{K-1}{K(A+1)}.
]

This increases monotonically with K and approaches:

[
rac{1}{A+1}.
]

So there are two biologically distinct regimes.

## Regime A — adding solutions also adds baseline exploration mass

Fixed per-solution (a).

Prediction:
**hump-shaped specialization versus solution abundance.**

## Regime B — fixed total exploration budget spread across more solutions

Fixed (A=Ka).

Prediction:
**increasing specialization that saturates.**

Therefore "number of solutions" alone is not enough.

The key ecological quantity is:

> **solution abundance relative to the individual's exploration / switching budget.**

---

# 5. Ecological interpretation

The mechanism has three necessary ingredients:

1. at least two adequate solutions;
2. repeated exposure to the same task class;
3. history dependence in reuse / reinforcement / switching.

Individual specialization then emerges as a **symmetry-breaking process**.

The environment supplies a feasible solution set.

Personal history selects and stabilizes a subset.

This differs from:

[
competition
ightarrow
spatial exclusion
ightarrow
individual niche.
]

Instead:

[
oxed{
solution opportunity
	imes
history
ightarrow
personal policy
}
]

---

# 6. Link to current empirical results

## Formation

Juvenile fruit bats:
- earliest matched two-day history does not robustly predict late personal use;
- recent matched two-day history strongly outpredicts earliest history;
- whole-history identity null controls general ontogenetic spatial expansion.

This supports history-dependent updating.

## Maintenance

Adult *Rhinolophus*:
- low-dimensional policy transfers across configurations;
- held-out policy geometry is predictable;
- scale-free route organization retains identity.

This supports consolidation into a portable personal policy.

## Expression

Controlled *Pipistrellus* sensory perturbation:
- shared environmental shift does not erase identity-bearing personal bias;
- expression strength can be context dependent.

## Spatial outcome

Wild *P. hastatus*:
- policy differentiation does not require increased pairwise vertical separation.

Together these results satisfy several predictions of the general mechanism.

What is still missing is direct measurement/manipulation of the **feasible solution set K**.

---

# 7. Direct experimental test

The clean experiment holds task goal and individual identity constant while changing solution abundance.

For each bat, expose repeated blocks:

### K = 1
A constrained corridor allowing essentially one viable path class.

Prediction:
little or no stable between-individual solution differentiation after common geometry is removed.

### K = 2–3
Several similarly viable corridors / obstacle homotopy classes.

Prediction:
strong history-dependent personal differentiation.

### large K
A broad open or highly redundant solution field.

Predictions differ by exploration-budget regime:
- fixed per-option exploration: specialization can weaken after an intermediate peak;
- fixed total exploration budget: specialization rises then saturates.

Randomize / counterbalance K order across bats.

Then reset the same geometry and test:
- immediate exploration;
- within-bat lock-in;
- between-bat divergence;
- persistence after delay;
- recovery after solution-set reopening.

---

# 8. Primary measurable quantities

Do not use realized route count as the manipulation.

K must be imposed by geometry.

Then measure:

## Individual identity

Own-history versus other-history held-out prediction.

## Consolidation rate

Trials required for within-individual policy variance to stabilize.

## Between-individual dispersion

Distance among personal policy centroids after removing common task effects.

## Hysteresis

After narrowing and then reopening the solution set:

> does the individual return to its previous solution, or establish a new one?

This distinguishes stored policy from purely reactive geometry following.

---

# 9. Strong falsifiers

The mechanism is weakened if:

- K > 1 does not increase scope for persistent individual differentiation;
- repeated experience does not improve own-history prediction;
- narrowing feasible solutions has no effect on expressed individual diversity;
- personal policies are fully explained by fixed morphology before experience;
- reopening the solution set yields no history dependence.

---

# 10. Main theoretical prediction

The most interesting prediction is not:

> more ecological opportunity creates more specialization.

It is:

> **individual specialization should depend nonlinearly on the ratio between available adequate solutions and the animal's effective exploration budget.**

This yields a direct bridge between:
- motor abundance;
- behavioral opportunity;
- learning/history;
- ecological individual specialization.

---

# Bottom line

Multiple feasible solutions are necessary but not sufficient to predict how much individuality emerges.

The exact Pólya model predicts:

[
oxed{
Delta(K,a)
=
rac{K-1}{K(Ka+1)}
}
]

and therefore a testable abundance × exploration interaction.

This converts the functional-abundance idea from a verbal mechanism into a quantitative ecological prediction.
