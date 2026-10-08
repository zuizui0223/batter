# Prospectively frozen sentinel-route transfer design and null (v1)

## STATUS, TARGET, FIREWALL
**NEW INDEPENDENT SYNTHETIC DESIGN, NO BAT EXPERIMENT OR OBSERVED NEW BIOLOGICAL RESULT.** This child branch builds on PR #85, not on frozen JAE nor on PR #72 P1/P2. The object is **transfer to a single never-additionally-trained route**, not private identity classification. No confirmatory animal sampling is authorized. Parameters and simulation scripts must not change after numeric results are opened.

## Ecological question
Does practice on a 3D flight solution improve later physical execution of **another 3D solution that was never additionally practiced**, specifically when the two share one horizontal/vertical maneuver? This would be compatible with compositional transfer but not by itself proof of neural motor modules, fitness or mediation.

## Route factorial structure
Canonical 2×2 routes:
- R1 = LEFT × LOW
- R2 = LEFT × HIGH
- R3 = RIGHT × LOW
- R4 = RIGHT × HIGH (fixed **sentinel** / untrained primary target)

Every animal is assessed on the SAME sentinel route R4 in physical obstacle family B (vertical decision before horizontal). Prospective extra training is assigned in matched family A (horizontal before vertical), on ONE of R1/R2/R3 only. No animal is assigned extra training on R4. Historical initial familiarity and route-capability checks for R4 must be identically scheduled for all animal groups before randomization. The sentinel is "not additionally trained", **not** literally unexperienced by animals if a baseline trial occurs.

Treatment arms (exactly one per three-animal block):
- N = R1 (shares NEITHER RIGHT nor HIGH with R4);
- V = R2 (shares HIGH only; vertical maneuver);
- H = R3 (shares RIGHT only; horizontal maneuver).

These are interventions on the *physical trained path*, not just recoded labels. All arms receive the same planned practice dose and reward, with adequate geometry/cue/performance matching. Animal order/fatigue and ability restrictions must be assessed in a **separate engineering pilot**.

## Frozen measurement and estimand
Independent blinded technical 3D sentinel performance, same calibrated physical cost (positive means improvement):
- two baseline forced R4-in-B assessment flights before the training randomization;
- a predeclared matched dose of 12 valid assigned A-route practice flights (hypothetical planning only, not an authorized animal workload);
- first two forced R4-in-B flights AFTER randomized extra training, before any additional testing or R4 voluntary choice; use the mean of those first two as the locked outcome.
- (Y_i=overline{c}_{i,mathrm{pre}}-overline{c}_{i,mathrm{post}}), a cost reduction.
- Pre vs post tracking features, failure handling and physical units must be frozen **before** treatment/outcome opening; this simulated file uses arbitrary comparable cost units only.

Primary assignment-contrast:
[
T = rac{1}{2}left(overline{Y}_{H}+overline{Y}_{V}ight)-overline{Y}_{N}.
]
This detects improvement associated with practicing a route that shares exactly one physical maneuver with the sentinel rather than a route that shares none. Because sentinel R4 is NOT additionally trained under ANY randomized assignment, a nonzero direct practiced-route effect on R1/R2/R3 does NOT contaminate the sentinel sharp null.

Separate mandatory descriptive H and V treatment-arm means; a positive average contrast with only one positive shared arm is **not** evidence that BOTH motor components generalize. The secondary asymmetry is (overline{Y}_{H}-overline{Y}_{V}) (report; no new significance claim).

## Restricted animal-level exact design and null
18 new animals, 6 complete randomized three-animal blocks. Exactly one H, one V, one N per block. Animal selection/blocking occurs before assignment; assignment is uniform over the six possible permutations within each block.

- There are exactly ((3!)^6=46,656) treatment allocations conditional on the fixed 3-person block structure.
- Under the **sharp null** that each bat's sentinel performance outcome (Y_i(t)) is invariant to which of R1/R2/R3 received extra practice, the 18 observed sentinel outcomes remain fixed while the 6 labels per block are reassigned.
- Compute all 46,656 exact assignments by enumerating six block contributions and forming their Cartesian sum; one-sided (p=#{T_{m perm}geq T_{m obs}-10^{-12}}/46,656), including ties. Criterion in synthetic scenarios: T>0 and p<=.05.
- The sharp null allows *arbitrary direct treatment effects* on the actually trained R1/R2/R3, since none is used as a sentinel target. It does NOT encompass a general "zero average transfer contrast" null with unit-heterogeneous effects, and its rejection does not identify motor-module mediation or rule out training-path salience effects.
- Secondary arm-specific differences and any continuous route cost effect remain descriptive unless independently preregistered for animal work.
- Real post-treatment attrition may invalidate sharp-null analysis by missing outcomes; welfare-approved predeclared missingness, no selective complete-case removal and route-feasibility gates are necessary.

## LOCKED synthetic study
Exactly 1,000 independent virtual experiments per scenario, root NumPy SeedSequence `202610081858`, Python 3.13 and NumPy 2.3.5 if possible. Six scenarios. Under each synthetic experiment:
- N=18 animals in 6 blocks; each block gets a uniformly random 3-label permutation.
- Animal baseline costs (c_i=1+epsilon_i), with (epsilon_isim N(0,0.20)); these stable individual baselines cancel in within-animal pre/post difference.
- Block-period common gain (g_bsim N(0,0.05)), shared for three animals in block.
- Individual-period nonspecific gain (h_isim N(0,0.05)), independent of arm.
- Exactly 2 synthetic pre and 2 synthetic post R4 technical cost measurements per individual, each independent (N(0,0.10)) measurement noise.
- The mean sentinel gain determined by the assignment + (g_b+h_i); pre measurements centered at (c_i), post at (c_i-g_b-h_i-mu_{m arm}).
- No simulated animals' cost observations are selected conditional on route choice.
- The per-scenario numbers are **hypothetical model inputs, not true effect sizes, validated energy or expected biological power**.

Six frozen scenarios (ordered arm effects `[N,V,H]`):
1. WHOLE_ROUTE_ONLY: [0,0,0] (the trained A route may benefit but is NOT an R4 target).
2. GLOBAL_FAMILIARITY: [0.12,0.12,0.12].
3. SHARED_MOTOR_MODULE: [0,0.12,0.12].
4. SHARED_SENSORY_CUE: **identical observed physical performance means** [0,0.12,0.12] caused by learned acoustic/visual scene similarity rather than shared motor actions. Must be **paired byte-identical** to SHARED_MOTOR_MODULE in every simulated replicate (same assignment, individuals, noise).
5. HORIZONTAL_ONLY_TRANSFER: [0,0,0.24]. Primary T same expected +0.12 as both-module scenario, but only H transfers. Its H vs V difference distinguishes this *particular* simulator but does not establish motor origins.
6. WEAK_SHARED_MODULE: [0,0.06,0.06], for finite precision sensitivity.

Under the first two scenarios the sentinel treatment assignment has no effect even when global time improvements exist; p should be near 0.05 with Monte Carlo error. Under the motor vs cue pair the observed causal effect and entire dataset are deliberately identical; a positive exact test cannot distinguish them.

## Validation and reporting
Before opening numeric results:
1. Exact 3! local label assignments, 6^6 total, one each H/V/N in every block.
2. Direct enumeration of 3!^2=36 pair-block assignments equals the Cartesian-sum null used by the implementation (within tolerance 1e-12).
3. For arbitrary test (Y), mean exact null T equals 0, and the observed allocation is present.
4. Original principal implementation scores the SAME R4 for all individuals; the trained path under all assignments is one of R1/R2/R3, never R4.
5. Coupled motor-vs-sensory causal generators have exactly the same simulated raw pre/post outcome arrays and null p values.
6. All 6×1000 runs execute with independent scenario+replicate substreams, deliberately coupling motor/cue only. Compute observed mean T, mean arm gain, exact p<=.05 rate and MC binomial SE, fraction both H and V means exceed N, and separate mean H−V difference.
7. Do not post hoc change animal N, training dose, noise, model response, target path or one-sided decision to make synthetic results favorable.

## Biological interpretation and STOP rules
A positive sentinel T with both H and V positive supports **assignment-specific transfer to an untrained configuration**, with a valid randomization test under the sharp no-sentinel-effect null. It does not uniquely support shared motor modules: similar echo cues, landmark memory, geometry familiarity or differential training difficulty can generate the same outcomes.

Crucial independent next design: randomized sensory cue remapping while **holding physical motor maneuvers constant**, or randomized motor-demand remapping while matching sensory cues, with validated matched exposure and outcome. Counterbalancing A→B task order and field geometry alone may not remove perceptual transfer.
The original 4-route C statistic need not be abandoned; it remains a useful descriptive full-grid pattern. This new sentinel-specific test is a **different, independently proposed experiment**, never a post-outcome rescue of PR #85. No animal welfare/ethics approval is implied.
