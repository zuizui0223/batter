# Target-configuration-blind flight-intensity forecast — executed result v1

## Evidence status (2026-10-08)
**POST-OUTCOME PREDICTIVE-SEMANTICS AUDIT OF THE SAME FIVE RHINO BATS, NOT INDEPENDENT CONFIRMATION.** This result closes the previously unreported GitHub Actions output of PR #79. It does not amend the frozen primary, the JAE manuscript, the θ convergence correction, or any outcome from other branches.

- Frozen contract: `TARGET_BLIND_FORECAST_AUDIT_CONTRACT_V1.md`.
- Frozen analysis: `target_blind_forecast_audit_v1.py`, in the same directory.
- [Successful workflow run 37726588937](https://github.com/zuizui0223/batter/actions/runs/37726588937) at head `82358ff47537a61b059efa9b7c54e5650c198c45`; job `113146038655`; artifact `11528948388`, `target-blind-forecast-audit-v1`.
- Workflow: synthetic target-blind reference, focal-excluded peer reference, permutation/score self-tests all **PASS**. Real-data script successfully completed.
- Source and unit: 45 feature-valid *Rhinolophus nippon* trajectories from the pre-existing Figshare 29209493 archive, summarized into 25 bat×configuration centroids (5 bats, 7 configurations; bat support A5/B4/C5/D6/E5). Four velocity features combined into one standardized flight-intensity scalar. Each bat carries equal weight.
- This output was previously available in a completed Actions job and is being transcribed without retuning the endpoint or rerunning with altered settings.

## 1. Primary: target-configuration-blind forward-style prediction

The mean and SD of each feature were fitted **only from trajectories in other configurations**. Each target bat's own prior configurations predicted the target scalar; comparison baseline = zero in that training-derived reference. There were no target-configuration values or peers in the reference or predictor.

| Quantity | Executed value |
|---|---:|
| `MSE_zero` | 0.9327492766210093 |
| `MSE_self` | 0.48903488399553935 |
| Gain `G = MSE_zero - MSE_self` | **+0.4437143926254699** |
| Relative `R2 = 1 - MSE_self/MSE_zero` | **+0.4757059627351049** |
| Within-configuration identity-label permutation, 9,999 draws, one-sided p | **0.0003** |
| Conditional permutation null 95% interval | [-0.4639000397381728, +0.1226548710335694] |
| Bat-cluster bootstrap percentile 95% interval for gain, 9,999 draws | **[-0.14893759423902952, +1.1303103528284981]** |

Per-bat gain (the biological unit is the bat, not the trajectory):
- A: **+1.6235208883744896**
- B: **-0.07040245632839617**
- C: **-0.41794503427219265**
- D: **+0.8513915553474181**
- E: **+0.23200701000603002**

**3/5 bats improve, 2/5 worsen.** A conditional permutation against shuffled correspondence is highly unusual, but the bat-level CI crosses zero. The five bats are too few for a strong population-level generalization; p=0.0003 is NOT the uncertainty of sampling new bats.

**Interpretation:** observed individuals' historic one-dimensional flight intensity carries cross-configuration forecasting information without test-configuration centering leakage. It does **not** forecast full 3-D trajectories, vertical occupancy shapes, acoustic decision rules, future foraging payoffs or fitness.

## 2. Secondary: peer-conditioned, target-bat-blind relative prediction

This secondary uses **contemporaneous peer bats within the test configuration**, excluding the target bat from the peer mean. It cannot be advertised as an operational target-configuration-blind forecast.

| Quantity | Executed value |
|---|---:|
| `MSE_zero` | 1.3836175257213292 |
| `MSE_self` | 0.6354948980707184 |
| Gain `G` | **+0.7481226276506109** |
| Relative `R2` | **+0.5407004564072632** |
| Permutation one-sided p | **0.0005** |
| Conditional permutation null 95% interval | [-0.7537265440539650, +0.29992910793976313] |
| Bat-cluster bootstrap percentile 95% interval for gain | **[-0.22485790790170834, +1.7942115370339073]** |

Per-bat gain: A **+2.5582360788273073**, B **-0.3022020367606655**, C **-0.4059130767253446**, D **+1.5985514854482794**, E **+0.2919406874634784**. Again 3/5 positive and the cluster CI crosses zero.

## Inferential corrections and closeout

1. The original θ correspondence result conditioned on the target-configuration cohort, which was not a fully out-of-configuration forecast. The newly audited **primary** removes this feature-reference leakage and still shows a positive conditional identity correspondence, though two bats lack absolute prediction gain.
2. The original exhaustive subset-size '91.6% convergence' is an algebraic identity, **not** empirical biological parameter convergence. See `THETA_CORRESPONDENCE_AUDIT_AUTHORITATIVE_RESULT_V1.md`; this receipt does not restore the invalid claim.
3. The 9,999 within-configuration relabelings test archive-conditional identity correspondence, **not** the distribution of effects in other individuals, other species or other ecological habitats.
4. This is the same already-opened 45-trajectory archive and a post-outcome sensitivity audit, not an independent replication or a discovery of learned memory, unique flight equations, acoustic interference compensation, spatial partitioning, or adaptive benefit.
5. No further same-source endpoint switching is warranted. Mechanistic/functional inference needs genuinely independent histories, perturbations or outcomes; the previously reviewed public data do not presently close that gap.

**Final status:** `SUPPORTED_ARCHIVE_CONDITIONAL_TARGET_BLIND_SCALAR_FORECAST_WITH_HETEROGENEOUS_BAT_LEVEL_GAIN`; `POPULATION_GENERALITY_UNRESOLVED`; `MECHANISTIC_CAUSALITY_UNRESOLVED`.
