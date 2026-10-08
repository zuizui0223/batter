# Causal and mechanistic interpretation after the memory-versus-inertia simulation

**Status: planning-only child-branch interpretation amendment.** Do not change frozen PR #72's P1 endpoint, treatment assignment, primary p threshold, 16-trial probe or submitted JAE manuscript. No animal data were collected for this note.

## The causal question P1 actually answers
Under the paired randomized A/B design, a supported `Delta_R=R_OPEN-history-R_CONSTRAINED-history>0` is evidence that **availability of multiple movement solutions during acquisition changes the individual-specific predictability of short-window route choices under equal current opportunity**.

P1 alone does **not** establish that the mediator is:
- an enduring learned preference;
- memory for one route or corridor;
- a portable two-coordinate personal movement policy;
- a stable route-use probability across extended time;
- or the ecological/fitness benefit of specialization.

The synthetic first-order Markov counterexample (same `rho` for all bats within a treatment, no individual theta; `rho_OPEN=.95`, `rho_CONSTRAINED=.10`) yields P1 support in 958/1000 simulated experiments. This is a *genuine modeled causal effect on short-term inertia*, not a Type-I statistical error.

## Mathematical discriminator: conditional dependence across a standardized reset

If four-route choice is a common first-order Markov chain,
```
Pr(X_(t+1)=r | X_t=s) = rho * 1[r=s] + (1-rho)/4,
```
then
```
Pr(X_(t+ell)=X_t) = 1/4 + 3/4 * rho**ell.
```
At `rho=.95`, same-route probability at lag 8 is 0.748, and at lag 16 is 0.580 despite no enduring individual `theta_i`.

When all animals' *most recent* route is experimentally forced to common R1, the first-order Markov property predicts no dependence of their reopened route choices on their individual PRE-reset route profiles after conditioning on treatment, family and the forced final state.

In contrast, if `X_{i,t} ~ Categorical(theta_i)` and `theta_i` is unchanged by temporary route restriction, individual early route profiles continue to predict post-reset choices even though every animal last flew R1.

This is the precise biological question for the S2 re-expression layer:
> **Does an individual's pre-restriction route history retain predictive information after everyone has been forced to express the same current route state?**

Use the first fixed eight eligible reopening trials, no later exploratory windows, to avoid rewriting of the latent state during the assay. The hypothetical `8 forced R1 / 8 reopening` counts in the simulation are **not** frozen animal trial counts; freeze only after engineering and welfare review.

## S2 outcome meaning
- **P1 positive, S2 positive:** acquisition opportunity affects short-window differentiation; some individual information survives the standardized route restriction. Still not proof of learning rather than stable morphology, perceptual bias, reward preference, or a higher-order motor state.
- **P1 positive, S2 negative:** acquisition opportunity affects short-window differentiation, but this assay does not support retention across restriction. The immediate-inertia explanation remains sufficient; the suppression treatment may also have rewritten a genuinely durable state.
- **P1 negative, S2 positive:** history-dependent identity persists, but the experiment has not established a causal effect of solution opportunity on its formation.
- **Both negative:** neither acquisition-opportunity differentiation nor post-interruption retention was established in these endpoints; not evidence that animals cannot learn.

## What a sham control could add
To separate forced-state synchronization from time, fatigue, reward exposure and return-to-apparatus effects, an independent prospective *reset versus sham* manipulation would be valuable. The sham must match exposure time, animal handling, reward schedule and rest, while preserving open route options; it should be allocated prospectively with adequate animal-level replication. The original 20-animal sample may be underpowered for an extra factorial contrast, and crossover may itself alter history.

Do not silently append sham trials to the original fixed confirmatory sequence or treat a pilot's route biases as outcome-blind planning data. Any change is a **new separately versioned secondary experiment**.

## Generality ceiling
A positive S2 would rule out only the **specified common first-order route-inertia model**, not all short-memory, higher-order Markov, biomechanical or stable-state mechanisms. An eight-flight forced interval does not guarantee biological memory erasure or equal opportunity in cognition.

## Publication boundary
This simulation gives a reason to keep a clear two-stage narrative:
1. **Formation effect on short-window expression (P1)** — causal opportunity history;
2. **Retention/re-expression of individual correspondence despite forced convergence of immediate state (S2)** — separate mechanism discriminator.

P1-only results should not be marketed as evidence that opportunity creates a permanently stored personal strategy. A supported P1 plus S2 would be stronger, but remains one level below identifying the neural carrier, ecological adaptive value or wild three-dimensional niche consequences.
