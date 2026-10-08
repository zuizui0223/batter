# Unknown shared-context means: no-go for naive plug-in sign-flips (V4 pre-outcome contract)

**Status:** mathematical and completely synthetic methodological test. No bat measurements, no modification to #79/JAE frozen results. This file fixes the question, transforms, seeds and stop boundary BEFORE the plug-in outcome simulation.

## Why the prior V1 oracle cannot simply be applied
The original whole-cell sign flip maps the entire 4-vector residual r_ie = Y_ie - mu_e to s_ie*r_ie, with independently chosen s_ie ∈ {−1,+1}. Its finite-sample reference is exact for a sharp centrally symmetric zero-mean response law only if **mu_e is known independently** and the cell residual vectors form a sign-invariant joint distribution.

For a publicly observed bat configuration with m_e=2–5 co-observed bats, the natural plug-in is muhat_e = mean_i Y_ie. Then by construction:
  sum_i (Y_ie - muhat_e) = 0   (componentwise).
Independent whole-cell signs generally violate this deterministic constraint:
  sum_i s_ie (Y_ie-muhat_e) ≠ 0.
Thus those flips are not transformations preserving the conditional law of the observed residual vector given its fitted mean; treating them as an *exact* reference is invalid. Cross-fitting or recentering can make a practical test in richer data, but neither automatically restores finite-sample group invariance with heterogeneous bat errors and sparse shared contexts.

This is a mathematical **support/invariance counterexample** even if a particular Monte Carlo false-positive fraction happens to be 5%. The test must never infer validity from one simulated rejection rate alone.

## Prespecified source-free stress design
Synthetic support is IDENTICAL to the prior V1 toy: 5 named fictional bats, 7 environments, schematic 25 occupied bat×environment cells, 45 artificial trial-file rows made by exact within-cell duplicates, four correlated normal features with rho=0.6 and a known constructed common 4D context offset mu_e. The original per-bat environment support counts are reproduced, but the exact source occupancy and original raw measurements are NOT.

Null generators fixed in advance:
- Gaussian independent centrally symmetric 4D residuals with individual SD [1,1,1,1,1].
- Gaussian independent centrally symmetric 4D residuals with individual SD [.3,.6,1.2,2.5,5].
- No stable individual **mean** theta and no stable personal reaction norm.
- 120 independent fabricated archives per generator, B=99 independent randomizations per archive; seed 202610082238; evaluation p=(1+count)/100. No other tuning after seeing results.

Methods to compare using the unchanged four-feature target-blind personal history MSE gain:
1. **Known-mu sign oracle:** flip the entire bat×environment 4D vector about externally known simulated mu_e, and recompute training-only fold means and SD on all transformed artificial rows.
2. **Same-sample fitted-mu naive plug-in:** compute unweighted bat-centroid mean within each environment using all bats in that environment, flip each residual about that estimated mean, recompute training-only folds. muhat is *held fixed* inside each randomization, exposing the naive plug-in failure. This is deliberately NOT called a valid method.
3. **Label permutation comparator:** shuffle bat labels within context without changing original folds, as in prior synthetic audit. Intended only as comparator, not valid H0_mean test under bat-specific SD.

Negative-control deterministic invariance check:
- sample-fitted residuals sum to 0 in each context and each feature before transformation;
- there exists an independent sign assignment that makes their sum !=0 afterwards (a transformation outside fitted residuals' support);
- the oracle sign flips preserve each entire 4D residual's absolute coordinate and cross-feature orientation up to sign.

## Frozen interpretation / scientific stopping rule
- Compare empirical nominal-5% null rejection descriptively, with binomial Monte Carlo uncertainty from only 120 trials. Do not claim a method is 'fixed' or valid solely because an error rate is near 5%.
- Invariant-group validity is absent for plug-in muhat *regardless of whether simulated size appears too low, near, or above 5%*.
- A practical variance-robust real-data method would need independent external task-mean data, repeated independent matched occasions, explicitly fitted variance and session dependence, or randomized treatment-level inference for a precisely defined sharp causal null.
- Do not retrofit a favorable corrective null to the already-exposed five-bat archive. #79's G and permutation p remain its own prior reported estimand/conditional result. No new bat mechanism or adaptive benefit follows.
