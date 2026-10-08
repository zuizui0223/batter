# V2 frozen paired-arm component-transfer gate and sample-size stress

**SEPARATE PROSPECTIVE SYNTHETIC PLANNING ROUTE, NOT PR #86 v1 RECLASSIFICATION AND NOT REAL BAT DATA.** All v1 tests, numerical results, original JAE and fixed PR #72 remain unchanged. This v2 was designed after v1's six simulation endpoints were opened. Version v2 uses entirely fresh NumPy random streams and reports every predeclared condition, not an independent biological confirmation.

## Question
If the aggregate sentinel transfer contrast from PR #86 is positive, does this establish independently reusable *horizontal and vertical* movement information? No: H-only and V-only training effects can make the average positive. An independently fixed conjunctive rule would require both H and V training arms to beat the no-shared N arm on the identical B-family untrained sentinel R4=right×high.

## Assay and randomized treatment
Exactly the same ecological architecture as v1:
- N new hypothetical animals in six or eight complete 3-animal blocks: N ∈ {18,24}. These are planning alternatives, not a post-hoc choice of observed cohort size.
- Within each block independently randomize one each of N=training A-R1(left-low), V=training A-R2(left-high), H=training A-R3(right-low). ALL animals' common sentinel tested after practice is physical B-R4(right-high); nobody receives extra training on sentinel.
- Common pre-randomization familiarization across all four routes, plus fixed two baseline and first two post-training forced sentinel assessments.
- The scientific outcome is the physical cost improvement Y=mean(pre R4 cost)−mean(post R4 cost), with no self-selected routes in the outcome. All model costs in arbitrary units.

## Original v1 gate retained
For each block, T_b=(Y_H+Y_V)/2−Y_N; overall T=mean_b T_b.
Primary blocked randomization follows sharp null that all Y_i(t) are invariant to A-R1/R2/R3 training assignment: exactly 6^B assignments; with symmetric H/V labels there are only 3^B distinct orbit representatives with equal multiplicity 2^B.
One-sided p_T = Pr(T_null >= T_obs−1e-12); v1 supported T>0 and p_T<=0.05.

## New v2 *joint* endpoint
H vs N, conditioning on the **identity of the V-assigned bat** in each block:
- D_H=mean_b(Y_H,b−Y_N,b)
- under pairwise **sharp** null Y_i(H)=Y_i(N) for any bat assigned one of the pair (other animals including V held fixed), the two H and N identities may be swapped within each block;
- exact paired assignment null enumerates 2^B sign patterns of the six/eight observed block differences; p_H=Pr(D_Hnull >= D_Hobs−1e-12).

V vs N, conditioning on the **identity of the H-assigned bat** in each block:
- D_V=mean_b(Y_V,b−Y_N,b)
- exact paired label-swap null of 2^B sign patterns, p_V analogously.

**New v2 simulated decision**: `v1_primary_supported AND (D_H>0,p_H<=0.05) AND (D_V>0,p_V<=0.05)`. The latter is an **intersection–union requirement** for BOTH partial-transfer directions. It is not a new claim about actual animals nor guaranteed size control for a generic weak null of nonpositive mean treatment effects with heterogeneous potential outcomes. Exactness is stated only for each appropriate pairwise SHARP null with isolated animals/no spillover.

The two p values can be correlated and need **no Bonferroni adjustment when making a single conjunction claim**, because rejecting the composite null (either pairwise no effect) requires rejecting its true constituent null. The positive v1 T gate does not undermine conservative testing of this conjunction. The three-condition assignment randomization itself is mandatory; arbitrary trial-level sign flips would be invalid.

**Finite randomization resolutions**:
- six blocks: 6^6=46,656 v1 allocations (3^6 orbits); 2^6=64 pairwise conditional assignments per contrast, minimum possible exact one-sided p=1/64.
- eight blocks: 6^8=1,679,616 v1 allocations (3^8 orbits); 2^8=256 paired assignments per contrast, minimum p=1/256.

## Frozen hypothetical mechanisms, seven per N
Model technical measurement identical to previous v1: stable individual baseline Normal(1,.20), block nonspecific gain N(0,.05), individual nonspecific gain N(0,.05), two pre+two post technical noises N(0,.10) each; T and D outcomes from exactly the same simulated data.
Ordered mean arm costs improvements as N,V,H:
1. WHOLE_ROUTE_ONLY: (0,0,0);
2. GLOBAL_FAMILIARITY: (.12,.12,.12);
3. BOTH_MOTOR_COMPONENTS: (0,.12,.12);
4. BOTH_SENSORY_CUE_GENERALIZATION: exactly observationally identical to both-motor model, coupled in all simulation replicates including assignments and raw measurements;
5. HORIZONTAL_ONLY: (0,0,.24);
6. VERTICAL_ONLY: (0,.24,0);
7. WEAK_BOTH: (0,.06,.06).

These effect sizes and noise are chosen planning hypotheses and are NOT bat estimates.

## Monte Carlo and invariants
- Exactly 1,000 simulated experiments per mechanism × sample size (14,000 labelled scenarios). Independent scenario and replicate NumPy SeedSequence streams except paired motor vs sensory. Root seed `202610082015`, NumPy 2.3.5, Python 3.13.
- P value calculations exact; the Monte Carlo applies only to repeated independent hypothetical populations, never to the null assignment enumeration.
- Report for every model at both N=18 and N=24: mean T, p_T<=.05 fraction; mean H−N and mean V−N; p_H<=.05 and p_V<=.05 fractions separately; fraction passing BOTH pairwise tests plus original T gate; fraction both observed arm differences positive without p calibration; Monte Carlo binomial SE; no early stopping.
- All legal 3! and conditional 2! local assignments, exact null support and mean zero, direct 2-block 36-shuffle comparison for T and 2-block 4-sign comparison for pairwise p, known null minima.
- **A positive joint gate under both-effect model but not under H-only/V-only must be demonstrated rather than assumed; failure due to low sample size is allowed.**
- Entire observed pre/post cost and treatment allocation arrays are identical between motor/cue generators within paired replicates. Even a perfect conjunction cannot identify the physical sensory/motor carrier under those two models.
- Do not add a new animal endpoint, reweight the two maneuvers, change one-sided directions, selectively retain scenarios or declare a favorable simulated sample size after looking at output.

## Ecological ceiling
Both partial-transfer effects would support **assignment-dependent transfer tied to both horizontal and vertical route overlaps** under the proposed apparatus. It would not, without independently randomized sonar/visual cue controls, prove motor-element storage. This remains new-data work requiring welfare permission, tracking calibration and an independently approved 18–24 bat sample; numerical Monte Carlo detection rates are not prospective field/animal power.
