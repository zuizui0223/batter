# Skill-driven route individuality: a simple ecological formation threshold (v1)

## Tier and provenance
**NEW THEORETICAL / SYNTHETIC MODEL; NO ACTUAL BAT MOVEMENT, FIT OR VALIDATED EFFECT.** The model illustrates a sufficient causal mechanism for multiple personal routes in the absence of competitive spatial segregation. It does not alter PR #72–84's frozen experimental primaries, the JAE submission or their statistical evidence. The mathematical structure is a standard positive-feedback bifurcation, not claimed as a novel discovery of dynamical systems.

Reproducible numerical verification: `skill_feedback_phase_v1.py`, Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0; root RNG seed 202610081818. Companion record `SKILL_FEEDBACK_PHASE_RESULT_V1.json` is derived from a local independent execution and may be compared with a pinned GitHub Actions artifact.

## Biological causal story
Two comparably adequate movement routes in the same physical airspace, no conspecific competition or exclusion, identical initial physical capability and rewards. By using a route an individual acquires route-specific motor proficiency; execution with higher proficiency is more likely to be selected again.

Let `s1,s2` be learned proficiency benefits in *arbitrary commensurate utility units*. On every time step, `s_{r,t+1}=(1-delta)s_{r,t}+eta 1[R_t=r]`. Let d=s1-s2. Each choice selects route 1 with probability `sigma(alpha*(Delta+beta*d))` where `Delta` is route-1 relative reward, beta converts proficiency into net expected benefit and alpha is choice sensitivity.

Then the **exact conditional expectation**, not necessarily the trajectory of any one noisy animal, is

```
E[d_(t+1)|d_t] = (1-delta)d_t + eta*tanh((alpha*Delta + alpha*beta*d_t)/2).
```

Write kappa=alpha*beta and the dimensionless feedback intensity

```
g = eta*kappa / (2*delta).
```

### Formal bifurcation statement for equal current rewards (Delta=0)
The mean drift is `f(d)=-delta*d+eta*tanh(kappa*d/2)`. Because `tanh(x)/x` strictly decreases on x>0:
- if **g<=1**, the only fixed point is d=0; for 0<delta<1 it is locally stable for g<1 and at g=1 marginal in linearization;
- if **g>1**, d=0 becomes unstable and exactly two nonzero attracting fixed points `-d*<0<d*` exist, solving `delta*d*=eta*tanh(kappa*d*/2)`.

These two attractors represent alternative self-sustaining individual route specializations without fixed initial individual traits. Initial stochastic route use can select which attractor is approached. Under persistent stochasticity, rare switches remain possible even when the deterministic mean has two attractors.

### Reward-change hysteresis threshold
With reward difference Delta, stable/unstable branches satisfy

```
delta*d = eta*tanh((kappa*d+alpha*Delta)/2).
```

For g>1 the magnitude at which one of the two attracting branches disappears is

```
Delta_c = [ kappa*(eta/delta)*sqrt(1-1/g)
            - 2*acosh(sqrt(g)) ] / alpha.
```

For opposing reward advantages with `|Delta|<Delta_c`, the deterministic system can have two stable historical states even though the **current reward landscape is no longer symmetric**. Beyond the saddle-node threshold, only one attracting state remains. This is a finite-history hysteresis mechanism, not proof of optimality or universal stability.

## Fixed numerical example
Use `eta=.20`, `delta=.10`, `alpha=1`, `beta=2`, so `kappa=2`, `g=2`.

- Equal rewards: stable equilibria `d*=+/-1.915008`; d=0 unstable (derivative of next-state mean 1.1).
- Critical opposing reward difference: **Delta_c = 1.065680** in synthetic reward units.
- Reward Delta=+1.0: **two stable states** remain (d=-1.603519 and +1.971680) with an unstable branch at -1.170128.
- Reward Delta=+1.2: **only one stable state** remains (d=+1.977029).
- Negative Delta produces symmetric sign-reversed branches.

These numbers were obtained independently by numerical bracketing/root finding and direct substitution into the exact mean-field formula; they are not estimated from bats.

## Finite stochastic simulation boundary
2000 identical artificial individuals began with `s1=s2=0` and equal rewards. Each made 1500 sequential stochastic choices based on its current proficiency difference.

At high feedback g=2, the ending branch split is near 50/50 (P[d>0]=0.499). **99.1%** remained in the same sign branch between time 800 and 1500 in the chosen simulation, not all 100%. End SD(d)=1.919. With lower feedback g=0.6 and the same eta/delta, end SD(d)=0.684. This is a constructed demonstration of amplification and path dependence, not empirical duration in days or years.

## Ecological implications to test, not to assert
1. **Formation from symmetry**: equal starting bats can diverge if route-specific learning reinforces subsequent choices strongly enough relative to skill decay.
2. **Individual specialization without partitioning**: both personal routes can overlap in the same 3D space and reach the same reward; route preference is individual-specific in *solution* space rather than requiring conspecific avoidance.
3. **History-dependent response to environmental change**: if route reward changes moderately, a prior preference can persist despite a better current alternative, **without assuming that it is irrational**; learned performance savings can change the net value of alternatives.
4. **Large environmental change**: beyond the mean-field critical threshold, the previous history-specific state disappears; quantitative threshold is source/model specific.
5. **Falsifiers**: if route-specific motor execution cost does not change after randomized controlled practice, this *skill-feedback* carrier is unsupported even if route choice is stable. If practiced route skill improves but choice remains unaffected under careful controls, the loop is broken. Stable intrinsic biases, route reward differences, sensory cues and social learning remain rival causes of individual routes.

## Experimental value and limits
The earlier PR #84 establishes that independent forced practice can causally change preference and performance, but does not identify mediation. This dynamical model makes an additional **quantitative phase prediction**, not a new causal identification:
- measure skill gain eta per exposure;
- measure effective loss/forgetting delta;
- estimate choice sensitivity kappa after calibrating independent route reward/cost;
- predict whether positive feedback is above or below g=1 **before opening a new long-run specialization outcome**;
- independently test bifurcation/hysteresis and actual ecological task benefit.

No suitable existing public dataset from the present five-*Rhinolophus* archive identifies all three components. Fitting a high-order nonlinear feedback rule to the same previously opened 45 trajectories would be post hoc and likely confounded. Only new, balanced, welfare-reviewed task/performance measurements can adjudicate this model.

This is not evolutionary adaptation, a validated memory storage mechanism, or an intrinsic two-dimensional bat flight law.
