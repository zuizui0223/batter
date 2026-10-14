# A nominally duration-matched target challenge in the 2025 Myotis assay

**Date:** 2026-10-14. **Status:** DESIGN/PHYSICS-IDENTIFIABILITY NOTE and optional descriptive diagnostic. **No new bat data read, no actual target-motion durations measured, no test of a biological duration rule.** This document is downstream of published protocol and original observed group-level conclusions: it is NOT a preregistration or a new independent empirical finding.

## Opportunity revealed by the six original motor treatments

Foskolos et al. (2025), *BMC Biology* 23:21, https://doi.org/10.1186/s12915-024-02106-6. Original Methods specify six nominal displacement and speed regimes.

| Original grouping | Displacement (m) | Nominal target speed (m/s) | Nominal distance/speed (ms) |
|---|---:|---:|---:|
| easy | 0.08 | 0.5 | **160.000** |
| easy | 0.08 | 1.0 | 80.000 |
| easy | 0.08 | 1.3 | 61.538 |
| easy | 0.24 | 0.5 | 480.000 |
| difficult | 0.24 | 1.0 | 240.000 |
| difficult | 0.24 | 1.5 | **160.000** |

The endpoints **0.08 m / 0.5 m/s** and **0.24 m / 1.5 m/s** share `D/V=0.160 s`, despite their positions in the paper's *easy* versus *difficult* groups.

**This is a nominal kinematic coincidence, NOT a verified physical time match.** The rig is a step-motor linear-motion system. The actual displacement–time curve includes unknown initiation delay, acceleration, deceleration, and potentially nonconstant speed; only the original synchronized video/rig measurements can establish actual movement start, end, time profiles, motor sounds, and trial-by-trial exposure. Especially with a bat approaching and intercepting the target, exposure available before interception can be shorter than full programmed target motion.

## New physical calculation: finite acceleration removes nominal duration equality

This is an **assumption-dependent analytical counterexample**, not a reconstruction of the apparatus. Suppose each condition starts at rest, accelerates at the **same** constant magnitude `a>0` until the programmed speed `v` or half the route is reached, then decelerates symmetrically at `a` and finishes at rest. Its **minimum idealized mechanical travel time** is:

```text
                  { D/v + v/a      if D >= v²/a (trapezoid)
T(D,v,a) =         {
                  { 2 sqrt(D/a)    if D <  v²/a (triangle)
```

This is continuous at `D=v²/a`. The two published conditions are related by the same scale factor in speed and displacement: `(D_B,v_B)=(3 D_A,3 v_A)`. Under the same finite acceleration `a`, **T_B > T_A for every a>0**, even though `D_B/v_B=D_A/v_A=160 ms`:

- In the trapezoidal regime, `T(kD,kv,a)=D/v + kv/a`, strictly increasing in scale `k` for fixed `a`.
- After the regime changes to triangular, `T(kD,kv,a)=2 sqrt(kD/a)`, also strictly increasing with `k`.
- Hence the joint scale-up from k=1 to k=3 cannot have identical actual durations **under this model**.

| Identical assumed acceleration, m/s² | 8 cm at 0.5 m/s actual modeled time | 24 cm at 1.5 m/s actual modeled time | Difference |
|---:|---:|---:|---:|
| 5 | 260 ms | 438 ms | 178 ms |
| 10 | 210 ms | 310 ms | 100 ms |
| 20 | 185 ms | 235 ms | 50 ms |
| 50 | 170 ms | 190 ms | 20 ms |

**No assumed acceleration here is measured from the paper.** The real apparatus could use different acceleration profiles, never reach the setpoint speed, overshoot, or stop early; those alternatives can change sign/magnitude and cannot be settled by arithmetic. The experiment records video at 90 frames/s, so raw synchronized target trajectories *could in principle* check differences at roughly 11.1 ms temporal resolution, but the published Mendeley download has not been accessed and raw time series availability is unconfirmed.

**Consequence:** Even a reproducible personal A–B Buzz-II difference is compatible with a simple **actual-duration response**, given the as-yet-unverified duration mismatch. The A–B predictor in code must remain `nominal_duration_pair_diagnostic` / `actual_duration_verified=false`. Do not cite A–B difference as a falsification of a duration-only model or as evidence for personal velocity/displacement sensing until physical timing, interception censoring, motor noise and valid-buzz selection are independently controlled.

## Ecological/behavioral falsification, not a discovery claim

The interesting rival mechanisms are:

- **M_time-only**: the bat's conditional terminal-buzz response is a function only of experimentally realized target-motion duration `T`, after appropriate common/bat/day reference control. If `T` and the relevant approach stage are physically matched, the expected response difference should be negligible.
- **M_motion-content**: velocity/displacement information and associated sensory dynamics can influence response independently of nominal `D/V` duration. Different outcomes at **truly matched actual durations**, after acoustic rig sound, trial order, approach-stage and selection controls, would be inconsistent with the simplest M_time-only response explanation.
- **M_apparatus/selection**: motor acoustics, timing of prey interception, tag/microphone conditions, and differential occurrence/quality of Buzz II can produce the same observed pattern without different motion-sensing control laws. The observed contrast alone cannot reject these.

Let `i` denote physical bat, `d` dated session, `Y`=log(1 + valid Buzz-II duration ms) and `A=(0.08,0.5)`, `B=(0.24,1.5)`. Define:

```text
R[i,d] = mean(Y | i,d,B) - mean(Y | i,d,A).
```

The code records this fixed scalar **nominal-pair diagnostic**, requiring >=2 valid Buzz II trials in *all six* original moving regimes per bat×day, not only in A/B. Train each bat's R on first two dates; compare common R versus `R_group + 0.5*(R_bat - R_group)` in dates 3–4, equal bat/day. Report each bat's signed prediction gain, not just the pooled gain. This is a secondary descriptive forecast, *not* a causal test of moving duration, velocity, or displacement.

**The group-level hard-versus-easy difference and one strongly responsive laboratory individual are already published.** If R predicts, the new narrow observation would be recurrence of bat-specific A–B correspondence *within the same source* (n=4), not first discovery of acoustic response to evasive prey.

## Three independent gates before ANY ecological claim

1. **File/sampling gate.** Recover Mendeley Data V3 (https://doi.org/10.17632/8b57pz6bpj.3), validate actual bat identity, dated session, original six-condition mapping, trial-level Buzz II eligibility, sound tag batch, exact physical onset/end and kinematic profile. The public landing page lists figure/code materials but the source file schema is **not accessed in this environment**; no real observations have been opened.
2. **Temporal validity gate.** Verify the original control/alternative `t0` definitions. Stationary trials were aligned at a call-interval-derived mock origin, not an independent physical motion onset; never use this to claim a duration-matched time-series test. No actual onset/end or acceleration metadata → this diagnostic remains **NOMINAL_ONLY**, regardless of estimated R.
3. **Biological distinctiveness gate.** Demonstrate within-study held-out bat-specific R beyond a population-shared R and explicit bat-specific residual noise, and separate valid-buzz selection from acoustic amplitude/duration. No individual physical XYZ, energy cost, actual wild prey success, and no linkage to JAE 3D niche individuality are established. The printed descriptive contrasts and synthetic test success provide none of this missing evidence.

## Physical non-identifiability and alternatives

Because `T=D/V` for nominal constant-velocity movements, changing velocity at fixed D *also changes movement duration*. The 2×2 factorial `speed`, `distance` and interaction estimates are effect-coded descriptions of outcomes; they do not isolate a biological neural controller. The A/B pair offers a **possible** duration-control discriminator conditional on measured real-motion equality, but it simultaneously changes speed and displacement, so it cannot attribute any residual response to one of those two physical cues. It also may change apparatus sound and pre-interception time available.

A meaningful next **independent** mechanistic experiment would physically balance actual duration across multiple speed/displacement regimes with sound-matched sham motors and randomized/counterbalanced opportunities, record actual camera motion onset/end and chase outcomes, and repeat identified individuals across independent days. It must be animal-welfare/ethically authorized and cannot be retrofitted to the existing experiment.

## Scientific status

- **COMPLETED:** identifying the exact `D/V=160ms` nominal pair; derived a fixed diagnostic from the existing six-level design; added train/held-out comparator using declared source gates and synthetic tests.
- **HOLD:** original Mendeley trial-level source not available; actual duration equality not verified; no new measured personal-response coefficients; no new positive/negative empirical support.
- **FIREWALL:** PR #98 stays a child DRAFT of PR #95, not merged into frozen JAE or main.
