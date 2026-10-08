# Four-route compositional skill feedback — frozen theoretical/numerical audit v1

**Status: prospective theory and synthetic experiment-design stress, NO real bat outcomes.**
Builds on PR #84 without changing frozen JAE, PR #72 P1/P2, PR #81–84 claims or the original five-bat Rhinolophus archive. Do not count this work as biological validation or claim originality for the mathematically classical Potts/mean-field softmax transition. Freeze these test definitions before opening any fresh numerical scan.

## Why the previous two-route bifurcation is insufficient
The original planned bat obstacle layout is four 3-D routes, not two:
- L-low, L-high, R-low, R-high (the two choices are horizontal and vertical).
- Under a whole-route practice model, each one of four complete paths has its own independent acquired skill state.
- Under a compositional/motor-module model, each path combines one horizontal and one vertical maneuver skill. Practice in one path can transfer to *unpracticed recombinations*.

The main biological difference is **transfer structure**, not yet any evidence of a neural motor module.

## Model W: whole-route independent skill
K=4; states s_r, r=0..3; per decision:
  Pr(R_t=r | s)=softmax(kappa*s_r).
  s_(r,t+1)=(1-delta)*s_(r,t)+eta*1[R_t=r].

Conditional mean dynamics:
  F_r(s)=(1-delta)*s_r+eta*softmax(kappa*s)_r.
Let A=eta*kappa/delta, eta=.20, delta=.10, and set kappa=A/2 when scanning A.

Uniform equilibrium: s_r=eta/(4 delta)=.5.
At uniform the discrete-map Jacobian has a common eigenvalue 1-delta and three contrast eigenvalues 1-delta+eta*kappa/4. Local uniform stability requires A<4.

Find all nonuniform **one-dominant** fixed points
  p=(x,y,y,y), y=(1-x)/3, x in (1/4,1);
  A(x)=3*log(3*x/(1-x))/(4*x-1).
At saddle-node A_spin=min_x A(x) on (1/4,1), obtained by root of
  (4*x-1)/(x*(1-x)) - 4*log(3*x/(1-x)) = 0.
Coexistence value A_coex=3*log(3) with p_dominant=(3/4,1/12,1/12,1/12).
Uniform instability A_unstable=4.
The fixed-point free-energy-like Lyapunov-potential comparison is
  Phi_A(p)=(A/2)*sum_r(p_r**2)-sum_r(p_r*log(p_r))
at stationary p. It is not actual bat fitness. Verify at A_coex that Phi for uniform and dominant match numerically and analytically, while their probability vectors differ by finite magnitude.

Linear stability for dominant x, y:
  common mode lambda0=1-delta;
  dominant-vs-rest eigen lambda1=1-delta+eta*kappa*(4*x*y);
  two minority-contrast eigen lambda2=1-delta+eta*kappa*y.
Require abs(lambda1)<1 and abs(lambda2)<1 for local attractiveness. Label the lower-x root unstable; upper root attractive under the registered parameters.

Exact prescribed A scan: [3.1, 3.25, 3*log(3), 3.5, 3.9, 4.0, 4.3].
Output for each: uniform eigen, nonuniform roots, Jacobian stability, potential Phi difference, and number of locally stable stationary alternatives (uniform + four equivalent dominant states).

## Model M: factorized skill components, not exact route memories
The four paths are compositions of two binary subtasks H in {L,R}, V in {low,high}.
Skills h_L,h_R,v_low,v_high decay with delta=.10.
Each chosen route (H,V) increases **both involved component skills** by eta_module=.20.
Route utility is kappa*(h_H+v_V) with kappa=2.0.
Pr(H,V)=softmax over four summed route utilities, which factorizes exactly:
  Pr(H,V)=Pr(H)*Pr(V).
Then horizontal and vertical difference dynamics each follow the *original two-route rule*
  d'=(1-delta)*d+eta_module*tanh(kappa*d/2).
Their gain is g_module=eta_module*kappa/(2*delta)=2.
This model has four stable route combinations (two signs for each module) despite the whole-route model with eta=.20, delta=.10, kappa=2 (A=4) being only at its uniform linear instability boundary.
CAUTION: A route decision practices TWO motor components in Model M, so the per-choice total skill investment is greater than one whole-route increment in W. Comparing g numerically assumes comparable **per-component units**, not equal energy-learning budgets. Do not claim direct empirical threshold contrast until modules and their acquisition rates are measured.

Mechanism discrimination depends on **off-route transfer**:
After a controlled fixed exposure to L-low, compare change in *independently measured physical performance*, before and after exposure, for four routes:
- W: expected cost savings [gamma, 0, 0, 0];
- M: expected savings [2c, c, c, 0];
- global task-familiarity G: expected savings [c,c,c,c].
The model-declared measurement sensitivity for numerical demonstration: route-specific component gain c=0.10, W whole-route gain gamma=0.20, global gain c=.10. These are intentionally on the same maximum learned-route improvement 0.20 for W and M (not the same per-choice total motor investment). Avoid inferring real costs from faster flight alone.

## Exact synthetic *measurement signature* design — no bat data
- Four canonical routes in the order [L-low,L-high,R-low,R-high].
- One assigned practiced route per synthetic animal, balanced in each 4-animal block. N=20 synthetic animals (5 blocks), route assignment uniform among 24 block permutations, arbitrary actual identity of trained route.
- Synthetic pre/post performance measure repeated twice per route per animal; assume **Gaussian measurement noise SD=.08** on individual pre- and post-means, independently (4 observations per route total).
- A route-invariant animal practice effect and generic matched temporal change common to all four route classes may occur; include an independent N(0,.04) individual global improvement term; its additive effect cancels from contrasts.
- Analyze trained-route improvement and exactly-one-shared-component route improvement, vs the no-component-share alternative, **within** matched each animal. The frozen primary mechanistic contrast is:
  C = mean_i(0.5*[(pre-post)_(shareH) + (pre-post)_(shareV)] - (pre-post)_(shareNeither)).
  Under W: expected C=0. Under M: expected C=c=.10. Under global G: expected C=0.
- Also report D=mean_i((pre-post)_practiced - (pre-post)_shareNeither), W and M both expect +.20, global G 0. This checks primary contrast is *transfer-specific*, not just own-route benefit.
- Run 1,000 independently seeded synthetic experiments per model (W/M/G), root numpy seed 202610081747; 20 individuals, 4 routes. For each experiment compute C and D and nominal t-based intervals as **descriptive design calibration only**, and the fraction of experiments in which 95% t CI for C excludes zero on positive side. No p-value from these simulations is an animal study outcome.
- For every simulated dataset, also independently permute the route assigned to shareNeither/route labels under the exact blocked route assignment, if meaningful: BUT because the data generator explicitly attaches benefit to assigned route, treatment-specific signatures are analytically known. Therefore avoid claiming label permutation independently estimates motor-module causality; report only model-planning properties without constructing a misleading randomization test.


## Frozen seed-basin diagnostic (deterministic, not extra biological data)
At A=3.5 for W, starting all route skills at zero, force exactly m initial choices of L-low, with m in [0,1,2,3,6,12], then iterate the original deterministic conditional-mean update for exactly 4,000 steps, with equal current rewards. Report resulting probability of choosing the initially practiced route, its skill-difference (lead versus mean other 3) and whether it falls in the known locally stable uniform or dominant basin. Do NOT vary m, A, δ, η or iterations in this version to find a "pretty" switch. Initial skill 0 is not the same as the uniform fixed point .5 in all four routes; the common state component relaxes and does not affect relative softmax choice.

For M under the declared g_module=2, test algebraic separability numerically on a predeclared fixed score vector h=[+.30,-.10], v=[+.20,-.25] and verify joint softmax probabilities equal outer product of separate binary softmax probabilities to 1e-14.

## Synthetic invariants
1. Analytic stationary equation residual <1e-10 for roots in prescribed grid.
2. A_coex=3*log3 equality of Phi values <1e-10, dominant fixed p=(.75,1/12,1/12,1/12).
3. First-order coexistence A_spin<A_coex<4, and stable uniform + stable dominant for A=3.5.
4. Original two-route threshold g2=2 when eta=.20,delta=.10,kappa=2; four-route whole-path uniform critical gain g4=1 at same units.
5. Four-route module softmax factorizes into H and V; its two contrast gains both 2 at the declared parameters.
6. At every control model, expected C and D matches the frozen analytical table exactly; simulated sample sizes, seeds and unblinded scenario labels are retained as explicit model assumptions.
7. No free fitting of observed five-bat movement features or route labels; this is theoretical/synthetic only.

## Biological and methodological stop rules
Neither a classic 4-state mean-field Potts transition nor skill modularity is mathematically novel by itself. Claims about *Rhinolophus* behavior require new, ethics-reviewed experiments directly measuring transfer to **unpracticed paths sharing only one motor decision**.
A positive transfer assay could also arise from shared visual/acoustic cues, endpoint generalization or global reward expectation. Engineering must match shared-route affordances and independently control sensory and biomechanical transfer.
A formal cost/fitness claim needs calibrated energetic, time, collision risk and task rewards, not just repeatable path geometry.
Synthetic stable states do not prove indefinite animal memory; finite stochastic trajectories can switch.
