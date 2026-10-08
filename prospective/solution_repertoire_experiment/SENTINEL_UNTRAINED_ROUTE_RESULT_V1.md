# Sentinel untrained-route transfer — synthetic exact randomization result v1

**Evidence tier: NEW PROSPECTIVE SYNTHETIC DESIGN STRESS, NOT BAT OBSERVATIONS OR AN APPROVED EXPERIMENT.**

This result was calculated after freezing `SENTINEL_UNTRAINED_ROUTE_CONTRACT_V1.md` on the independent `prospective/sentinel-untrained-route-v1` branch (commit `ec8b3bee`). The source experiment described below has **not been run in living bats** and does not alter JAE, PR #72, or PR #85's original diagnostic C.

## Causal design

Use the existing 2×2 route classification:

| Route | horizontal | vertical | role |
|---|---|---|---|
| R1 | L | low | Training arm N (shares neither with sentinel) |
| R2 | L | high | Training arm V (shares sentinel high maneuver) |
| R3 | R | low | Training arm H (shares sentinel right maneuver) |
| **R4** | **R** | **high** | **Never additionally trained; identical physical B-family sentinel test for every bat** |

A proposed distinct future study, not the fixed original PR #72 randomized opportunity test: 18 new biological animals, six 3-animal blocks, uniformly randomize training in matched family A to R1/R2/R3 within each block; test performance on B-family R4 (opposite horizontal-vs-vertical decision order) in everyone. The *hypothetical* synthetic workload uses two pre and first two post sentinel trials and a matched A-family practice dose; these counts have **not** been welfare/engineering approved. Pre-randomization R4 baseline measurement makes the sentinel 'no extra trained practice', **not** literally never flown.

Test for a causal effect on a single fixed untrained target:

\[
T=(\bar Y_H+\bar Y_V)/2-\bar Y_N,\quad
Y_i=\bar c_{pre,i,R4}-\bar c_{post,i,R4}.
\]

## Exact conditional randomization is valid against a SHARP no-sentinel-effect null

Each of six blocks has 3! = 6 possible N/H/V assignments, giving **6⁶ = 46,656** allowed randomizations. Under the *sharp* null that training assignment does not change any individual's R4 sentinel potential outcome, keeping each observed R4 cost improvement fixed is legitimate **even if R1, R2, R3 practice has very large direct effects on those practiced routes**. Direct practiced-route scores never enter this test.

An important exact simplification arises from T's symmetric H/V coefficients: swapping H and V within each block does not change T. Therefore, the full 46,656-assignment distribution consists of **64 identical copies of 3⁶ = 729 distinct block-orbit statistics**, and the exact p-value can be evaluated by 729 outcomes without approximating the null. This is not a larger biological sample size: the uncertainty is still based on 18 animals.

Numerical invariants: six complete blocks; direct two-block 36-permutation brute force exactly equals orbit enumeration (including multiplicities), exact null mean T=0, target R4 never trained, paired raw observations identical under sensory- and motor-transfer rival models. All passed.

This inference is **not** exact against every possible *weak null* merely saying average transfer is zero when individual treatment effects are heterogeneous. Rejection of the strong no-assignment-effect null need not prove the physical process was motor learning.

## Locked Monte Carlo result (1,000 synthetic experiments per mechanism)

| Fixed generative model | Mean T | Exact sharp-null positives | H and V sample means both greater than N |
|---|---:|---:|---:|
| Whole-route skill only (no R4 transfer) | −0.001078 | 55 / 1,000 (5.5%) | 33.2% |
| Global equal improvement on R4 in all arms | +0.000077 | 49 / 1,000 (4.9%) | 33.5% |
| **Compositional motor component transfer (H=.12, V=.12, N=0)** | **+0.119387** | **633 / 1,000 (63.3%)** | **95.4%** |
| **Shared visual/acoustic cue transfer, not motor** | **+0.119387** | **633 / 1,000 (63.3%)** | **95.4%** |
| H-only transfer (H=.24, V=0, N=0) | +0.120006 | 381 / 1,000 (38.1%) | 50.8% |
| Weak module transfer (H=.06, V=.06, N=0) | +0.061302 | 279 / 1,000 (27.9%) | 73.5% |

Root seed `202610081858`, NumPy 2.3.5, synthetic Gaussian pre/post technical noise SD .10 per observation, nonspecific individual gain SD .05, block gain SD .05, and two technical pre/two post observations of the sentinel for each individual. None of these values is an empirical power estimate from bats.

The motor and shared-cue generator use **exactly the same path-label assignments, pre/post cost arrays and exact p-values in all 1,000 coupled simulations**. The experiment detects a specific *assignment-dependent generalization effect*, but sensory generalization is a viable causal competitor.

The H-only generator has the same theoretical primary mean (+.12) as both-component transfer, despite no V transfer. **One positive averaged T is therefore insufficient to assert two independently reusable motor modules.** Arm-specific H/V gains and a separately preregistered conjunction test are needed.

## Interpretation and next prospectively separable research questions

**Research claim possible after real data:** randomized additional practice on a different 3-D route changes execution of an otherwise identically tested and unpracticed-in-treatment sentinel path. This is stronger than a correlation between repeated flights, and scientifically different from PR #85's observational off-route C contrast.

**Research claim NOT established:** route transfer is motor-specific; both horizontal and vertical components independently transfer; actual fitness/energetic benefit; a personal 3-D flight equation; success in any bat species.

Existing bat studies already show route stereotypy after spatial learning (Barchi et al. 2013, DOI 10.1242/jeb.073197) and experience/cue-driven navigation adjustments (e.g. sonar corridor perturbation studies). Human motor sequence generalization can also follow *shared sensory/structural cues* (see npj Science of Learning 2023, DOI 10.1038/s41539-023-00194-7). Thus an R4 effect attributable to shared path dimensions would not, without physical/sensory dissociation, prove motor compositionality.

### Key follow-up 1: prove both partial-transfer arms rather than only one
A new pre-outcome, separately versioned **intersection-union** mechanism claim can require both H–N and V–N treatment contrasts to be positive under valid blocked inference. Directly permuting only the two arms under each pair's sharp null while holding the third arm fixed has 2⁶ = 64 assignments per pair at N=18. This analysis was **not frozen as confirmatory in the original synthetic v1**, and should be stress-tested prospectively, including its low finite-sample resolution.

### Key follow-up 2: motor versus perception
A genuine motor-specific claim needs *orthogonal experimentally randomized remapping* of shared physical maneuver versus shared echo/visual signature at unchanged safe clearance, or another independently identified sensorimotor dissociation. Merely changing the order of H and V decisions in A versus B does not guarantee visual/sonar cue invariance.

### Key follow-up 3: ecological payoff
Directly measure route-aligned collision/error, time and validated effort, plus comparable food reward, then ask whether learned transfer changes net ecological return. This paper's arbitrary movement-cost numbers are not metabolic energy or organismal fitness.

The next version must not be described as an update to the old original PR #72 primary or as new evidence from the same five *Rhinolophus* bats.
