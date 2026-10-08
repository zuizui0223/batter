# Sentinel transfer — joint horizontal and vertical inference v2

## Provenance and evidence status

**Purely synthetic planning; no new bat measurements.** Independent v2 contract `SENTINEL_TWO_COMPONENT_GATE_CONTRACT_V2.md` was committed first (`135021b9`). The design and its root seed were fixed before the new simulation outputs were viewed. This is a distinct inference problem from PR #86 v1 and does not retroactively change v1's primary null or PR #85's C metric. Both motor and sensory hypothetical models are paired by identical raw outcome simulations; neither is a demonstrated bat mechanism.

## Technical inference extension

The v1 sentinel outcome is the change in blinded performance on B-family R4=right×high, NEVER an additionally practiced route. Each bat is assigned extra practice on an A-family path of N=left×low (shares neither), V=left×high (shares vertical), or H=right×low (shares horizontal), exactly one of each per 3-bat randomized block.

Original v1 test:

\[
T=(\bar Y_H+\bar Y_V)/2-\bar Y_N.
\]

A positive T can be driven entirely by H alone or V alone. New proposed conjunction requires **all** of:
- original sharp-no-effect exact randomization p_T <=0.05 and T>0;
- H−N>0 and conditional exact one-sided p_H<=0.05 while **holding the V-assigned bat fixed in each block**;
- V−N>0 and conditional exact one-sided p_V<=0.05 while **holding the H-assigned bat fixed in each block**.

Under the appropriate *pairwise sharp equality null*, each conditional test has exactly 2^B within-block H/N or V/N assignments. With six blocks (18 animals), this is 64 possibilities, minimum exact p=1/64. With eight blocks (24 animals), 256 possibilities, minimum p=1/256. The original symmetric T remains an exact 6^B assignment test, equivalently 3^B orbit values each with equal multiplicity 2^B.

This is a single intersection-union **conjunctive** research claim. Since a failure of either partial-transfer component prevents the biological conjunction, each condition can be tested at nominal 0.05 without an extra Bonferroni factor. However, exact finite randomization p applies to the defined *sharp potential-outcome nulls*, not without qualification to every weak zero-average contrast with heterogeneous individual effects or post-treatment attrition. The empirical false-support fraction in Monte Carlo will fluctuate around its underlying rate.

## Seven hypothetical alternatives; 1000 runs/model/sample size, independent v2 seed 202610082015

Arm mean changes assigned before opening: N, V, H, respectively:
- WHOLE_ROUTE_ONLY = [0,0,0];
- GLOBAL_FAMILIARITY = [.12,.12,.12];
- BOTH_MOTOR_COMPONENTS = [0,.12,.12];
- BOTH_SENSORY_CUE_GENERALIZATION = same arrays AND same raw synthetic trial values as BOTH_MOTOR_COMPONENTS;
- HORIZONTAL_ONLY = [0,0,.24];
- VERTICAL_ONLY = [0,.24,0];
- WEAK_BOTH = [0,.06,.06].

All settings of trial technical noise, individual/block generic improvement, and pre/post count were reused from v1 in fresh independent simulations. Any percentages are conditional-on-assumptions Monte Carlo frequencies, **not actual study power**.

| Scenario | 18 animals: v1 T | 18: both components | 24 animals: v1 T | 24: both components |
|---|---:|---:|---:|---:|
| Whole-route, no sentinel transfer | 5.0% | **1.3%** | 5.5% | **1.0%** |
| Equal global familiarity | 5.4% | **0.3%** | 6.9% | **2.0%** |
| **Two shared motor elements** | **62.4%** | **28.0%** | **75.9%** | **40.8%** |
| **Acoustic/visual cue similarity** | **62.4%** | **28.0%** | **75.9%** | **40.8%** |
| H-only transfer | 34.2% | **5.1%** | 51.7% | **6.4%** |
| V-only transfer | 35.1% | **4.8%** | 47.1% | **5.8%** |
| Weak dual transfer | 25.9% | **7.0%** | 32.2% | **11.2%** |

All model outcomes (including sample means and trial arrays) are **exactly equal** in both motor-vs-sensory causal-model partners for 2000 (1000×2 N) paired synthetic experiments. Neither the v1 nor v2 observable outcomes can distinguish those origins.

### Interpretation of the low two-component rate
Under the generous toy per-component improvement +0.12 and SD=.10 per technical observation, 18 bats produce a conjunctive detection fraction of only 28.0%; 24 bats, 40.8%. Thus a real experiment targeting BOTH reusable 3D motor elements should not simply inherit the original ~20-bat PR #72 enrollment from an unrelated hypothesis. **Pilot estimates of effect size and technical measurement error** are mandatory before cohort sizing, and single-animal multiple post tests may themselves induce further learning. Additional technical measurements are not a free way to increase independent biological n.

The apparent ~6% conjunction frequency in the H-only and V-only scenarios at n=24 is compatible with Monte Carlo uncertainty with 1000 synthetic runs; it is not a demonstrated guarantee against all weak-null data-generating processes. One-sided exact randomization under the appropriate sharp pair null is the intended theoretical guarantee.

## Additional valid design requirement — sensory versus motor

A true motor-module explanation needs **independent variation of physical maneuver similarity and echo/sensory cue similarity**. The planned A→B order reversal is helpful but does not alone prevent both physical and acoustic transfer from being present.

Prior work demonstrates real-time artificial echo playback in flying pipistrelles (e.g. https://pmc.ncbi.nlm.nih.gov/articles/PMC7668068/) and independent route memory under obstacle reconfiguration (Barchi et al. DOI 10.1242/jeb.073197). But importantly, a study of real vs virtual obstacles found that some virtual echoes **failed to elicit real-obstacle avoidance**, showing that an echo-playback cue may fail to recreate realistic angular acoustic geometry (https://pubmed.ncbi.nlm.nih.gov/22085788/). A future orthogonal cue-remapping experiment therefore requires a source-level acoustic scene and behavior feasibility gate rather than assuming an artificial echo treatment is a purely symbolic cue.

No bat endpoint has been opened and no test of energetic benefit or animal welfare feasibility was made. This new planning result is a technical proposal and must be versioned, preregistered, and ethically approved before use.

## Reproducibility

File `sentinel_two_component_gate_v2.py`, JSON result `SENTINEL_TWO_COMPONENT_GATE_RESULT_V2.json`, root NumPy SeedSequence 202610082015, NumPy 2.3.5. Self-tests passed for 36-allocation primary and 4-allocation conditional two-block correspondences, complete blocks, fixed structural support and coupled motor/sensory sources.
