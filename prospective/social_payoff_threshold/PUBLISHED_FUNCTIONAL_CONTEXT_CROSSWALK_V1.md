# Social co-use ecology: independent evidence crosswalk and a falsifiable boundary

**2026-10-08 | Source-backed programme synthesis | NOT a new empirical analysis.** This document explicitly separates existing published functional evidence from the JAE descriptive vertical-identity result and the open methodological proposals in #95. No values from unpublished or previously unopened raw 3D bat trajectories have been analyzed.

## 1. Why the simple narrative "overlap is harmless" is wrong

**Existing JAE programme:** repeated individual vertical-use shape can be detected without positive excess contemporaneous spatial partitioning in the evaluable panels. That establishes *non-necessity of additional segregation for repeatable observed individuality*, not that overlap never causes foraging costs, that bats never avoid one another or that the individual policy maximizes fitness.

**Independent, real wild functional observations:**

| Source and ecological setting | Already published direct result | What the source does NOT show |
|---|---|---|
| [Krivoruchko et al. 2024, PNAS](https://doi.org/10.1073/pnas.2321724121), openly described [10-*Molossus* bat functional dataset](https://doi.org/10.17632/h7krh54zxc.1) | Onboard microphones measure conspecific calls, prey attacks and *chewing-supported capture success* in 5-s windows. Success improves from none to a modest conspecific presence then decreases at higher call density. This *hump-shaped social benefit/cost* is **prior art**, NOT a novel model found in batter. | Does not observe matched fine-scale 3D paths or causally manipulate conspecific density; unknown if individual optimum densities are stable across independent nights/bouts. Acoustic calls are a density proxy, not necessarily the count of nearby physical bats. |
| [Fujioka et al. 2026, PLOS ONE](https://doi.org/10.1371/journal.pone.0343485), pond foraging by *Myotis macrodactylus* | Individual **prey-attack rate** (~buzz/attack attempts, NOT confirmed actual capture success) is ~25% lower during two-bat simultaneous patch use than solo use, and overlap duration is shorter than a simple independent Poisson-process reference. [Open S1 event dataset](https://doi.org/10.1371/journal.pone.0343485.s001): pond entry/exit/prey-attack times for 3 field nights. | Does not experimentally isolate acoustic interference vs maneuver obstruction vs prey depletion. Identifying an emitter/flight within a pond event is NOT documentation of an enduring physical bat ID linked across all three nights. 44/75/61 visit counts are NOT verified unique recaptured bats. 25% reduction is in attack *attempt rate*, not measured per-prey capture efficiency or fitness. |
| [Delmotte et al. 2025, Behavioral Ecology](https://doi.org/10.1093/beheco/araf090), [Dryad](https://doi.org/10.5061/dryad.6q573n6b0) | 3D acoustic tracking of flight *trajectories* and feeding-buzz **scores**: conspecific and intra-guild heterospecific co-occurrence is associated with different speed–feeding-buzz relationships. For intra-guild heterospecifics, a negative speed–buzz relationship weakens or disappears. This social-context dependence is **already published**. | IdTraj is a trajectory identifier, **not an established stable physical animal ID across contexts/dates**; buzz score is an attack proxy not independently verified captures. Co-occurrence is observational, not randomized. |
| [Goldshtein et al. 2020, Current Biology](https://doi.org/10.1016/j.cub.2020.07.079), flower/cactus foraging by *Leptonycteris yerbabuenae* | Individual foraging cores can become weakly overlapping, and a reinforcement-learning model reproduces resource partitioning. Both learned patch allocation and low overlap are **existing prior art**. | Does not prove that every bat system must partition space or that overlapping behavioral policies are not individualized. |
| [Lin et al. 2023, Molecular Ecology](https://doi.org/10.1111/mec.17150), [Dryad](https://doi.org/10.5061/dryad.4mw6m90fr) | Laboratory bat-ID-keyed moth-capture success rates (real performance), differing prey acoustic defence, and field diet-prey availability. This already shows ecological capture outcomes depend on prey and availability context. | No synchronized multi-bat fine-scale 3D co-use or measured route-conditioned sonar competition. |

## 2. The actual biological gap (must NOT be claimed as prior-art novelty)

The generic social-density optimum, costly patch co-use, learning-mediated resource partition, and conspecific/heterospecific change in buzz–speed relation have all been published.

The potentially distinctive **integration question** is:

> Does an individual's persistent movement/sensorimotor response map alter the density or interference level at which sharing a physically constrained foraging patch stops paying, even when coarse 3D utilization overlaps with other individuals?

This is a *cross-level causal hypothesis*, NOT a confirmed finding. In particular the functionally relevant distinction is whether a bat maintains a personal 3D policy while (a) remaining in shared space, (b) changing its vertical maneuver within a patch, or (c) temporarily leaving that patch. These responses can coexist and do not imply one universal replacement strategy.

## 3. Mechanism-specific, preregistrable predictions

Define externally, **before choosing outcomes**, using measured independent variables:
- `G`: calibrated physical route freedom (number of safe paths, clearance, unobstructed vertical maneuver volume), not inferred from successful routes;
- `A`: receiver-side acoustic interference (exogenous playback/calibrated propagation), not the bat's chosen pulse frequencies;
- `P`: independently measured prey availability and replenishment, not attack buzz rate;
- `H_i`: personally held-out or intervention-frozen bat reaction norm/history, independent of test response;
- `R_i`: absolute-scale verified capture success per unit effort and/or measured search time; do not relabel feeding buzz as captured prey;
- `E_i`: hazard of leaving a patch after conspecific arrival, with counterbalanced arrival/reward constraints.

**Proposed tests if independently eligible new data exist:**
1. **Sensory interference versus prey depletion:** At constant measured prey, externally increased masker load causes lower capture success without requiring food consumption by the co-forager; conversely, prey supplementation changes success even when acoustic exposure is fixed. Without these measurements the two mechanisms remain unresolved.
2. **3D route freedom as a buffer:** Exogenously increased physically valid route choice mitigates the treatment-induced drop in *capture success*, holding the canonical route's acoustic field fixed as required by engineering gate #93. Beware that distinct routes may legitimately have distinct acoustic fields and travel costs.
3. **Personal response persistence:** Independently estimate bat-specific **density/interference response slopes** on prior bouts and test them on entirely held-out independent sessions. The source unit is a physical bat×session; 5-sec windows and multiple attacks within one continuous bout are NOT independent animals or sessions.
4. **Patch-exit substitution:** If a bat can reach a profitable alternative patch cheaply, social interference may be resolved by a higher exit hazard rather than different altitude in the same patch. This prediction distinguishes temporal from vertical/spatial avoidance; repeated movement measures are needed to identify which choice occurred.
5. **No identity mediation by statistical fiat:** Even if randomizing route freedom improves performance, it does not establish that an individual's learned personal controller caused the effect without a separate valid intervention on training/history or clear identifiable mediation assumptions.

**Disconfirming outcomes:** If individual response slopes do not replicate after bat/device/time controls, the personal-payoff-threshold claim is unsupported even if the pooled density curve is hump-shaped. If response predicts repeated trajectory differences but not a functionally credible payoff at available precision, individuality remains descriptive. If a static prey/resource model explains changes, sensory-buffering is not supported.

## 4. Data-source eligibility and priority

**2026-10-08 authoritative source correction:** The original 2024 PNAS article explicitly recorded the **evening or the morning** foraging bout of each of its 10 tagged bats, with one dated flight interval per bat in Table 1. This is **not a repeated-bat×independent-bout study**. It therefore fails the separately frozen individual-threshold held-out-night primary even if all original five-second observation rows are later accessible. The original Mendeley API access audit returned HTTP 401 on both metadata paths; an alternative PNAS/PMC supplemental XLSX URL gate also did not retrieve the file; both are access-path issues, independent of the design-based STOP. See `PNAS_2024_ORIGINAL_METHODS_INDEPENDENT_BOUT_STOP_V1.md`. The source remains valuable **published functional evidence**, NOT an empirical source for stable personal thresholds.


- **Existing payoff source, confirmatory gate CLOSED:** Krivoruchko/Mendeley `h7krh54zxc.1`: 10 bats, one author-documented evening OR morning recording/bout per bat, actual capture success counted in five-second bins. No genuine cross-night individual threshold holdout is available under the published design. STOP persistent personal-threshold test without numerical opening; population-level social benefit/cost remains valid published prior art.
- **Independent behavioral patch-source:** Fujioka 2026 S1 event times: useful for pooled time-resolved **co-use and exit** analyses, but the paper has already tested patch overlap and attack-rate reduction. Absent persistent physical bat IDs and independent prey abundance, STOP longitudinal individual mechanism and causal interference.
- **Independent 3D movement-context source:** Delmotte 2025 Dryad: 3D trajectories and buzz intensity plus co-occurrence guild, but no verified persistent animal IDs and no actual prey capture success. STOP individual threshold/fitness.
- **New prospective simultaneous bat×3D×sonar×payoff study:** potentially decisive, but only if safe and ethically approved, with calibrated physics and adequate independent bat/session replication; not executable from current archives.

## 5. Interpretive ceiling and manuscript placement

JAE may claim repeatable vertical organization without established exclusive contemporaneous partitioning **in the examined settings**, not a general claim that competition is absent. The independent PLOS/PNAS/Behavioral Ecology studies should appear as **boundary context in a future discussion** (subject to human coauthor review), not be folded post hoc into primary JAE effect claims or counted as replications.

**Programme verdict:** DATA-SUPPORTED CONTEXT-DEPENDENT SOCIAL COST/BENEFIT IS PRIOR ART; PERSONAL 3D OPPORTUNITY→SOCIAL PAYOFF THRESHOLDS REMAIN **UNIDENTIFIED**. This note supplies a falsifiable ecological bridge rather than another same-five-bat permutation result.
