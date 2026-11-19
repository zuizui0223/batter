# H1 2025 Costa Rica bat risk-gating: original-author-source reanalysis v1

**Status: VERIFIED original-code/data conditional replication of published prior art, not a new biological discovery or H1 meta-analysis.** Authenticated original Git author file and reanalysis CI: https://github.com/zuizui0223/batter/actions/runs/44473278891 . The frozen `batter` JAE inference and `main` are not altered.

## Source, biological question, and independence

Gamba-Rios, McCracken & Chaverri (2025), *Biology Letters* 21:20250042, DOI [10.1098/rsbl.2025.0042](https://doi.org/10.1098/rsbl.2025.0042); public original Dryad [10.5061/dryad.6djh9w1d3](https://doi.org/10.5061/dryad.6djh9w1d3), original author [GitHub code and CSV](https://github.com/morceglo/Predator-recognition).

Study location **Hacienda Barú, Costa Rica** (distinct geographic region from 2015/2016 Barro Colorado Island Panama and 2019 lakes Germany). The experimental task measured **response social-call rate in a temporary roost while predator/nonpredator bat echolocation calls overlapped conspecific inquiry calls**. It did **not** measure foraging prey profitability, individual flight niches, information transfer between free bats or reciprocal food sharing.

The original authors tested **117 bats from 33 social groups**, and reported **38 responders with at least one responder per social group**. Their public behavioral source contains **228 rows = 38 bats ×2 stimulus treatments ×3 30-s periods**, not all 117. The physical group ID is absent; the 38 individuals are not demonstrably independent clusters. This is a **responder-conditional reanalysis**; the 79 other tested bats were **not imputed**.

Original source integrity: Git blob SHA1 `b8a119df0204ed0beb90b971c97f60cafbdb74cd`; SHA256 `11e281708be94ad76b0875d8cf43adf605e8095bb500ad43936f20a3c98d77d3`; `data.csv` 9,979 original bytes. Source analysis and three known-truth structural checks passed. No raw bat-ID-bearing file was committed or uploaded as an artifact.

## Fixed paired within-bat comparison (original experiment, not new biological finding)

Primary d_i = [(log(1+predator-during) − log(1+predator-before)) − (log(1+nonpredator-during) − log(1+nonpredator-before))].

| Observed unit | Effect / response | Comment |
|---|---:|---|
| 38 response-recorded bats | Mean d = **−2.1653** | Individual-equal, log(1+count) scale |
| 38 response-recorded bats | Median d = **−2.1459** | 35 negative, 3 positive |
| Predator condition | Before 30.63 / during 0.76 | Mean calls per 30s in selected sample |
| Nonpredator condition | Before 28.71 / during 17.89 | Same selected sample |
| Nonpredator-first (NP→P) | Mean d = −2.1260 (20/22 negative) | Order-stratified descriptive |
| Predator-first (P→NP) | Mean d = −2.2193 (15/16 negative) | Order-stratified descriptive |
| Novel control caller | Mean d = −3.3248 (14/14 negative) | Distinct source call exemplar |
| Frugivore caller | Mean d = −1.0662 (11/12 negative) | Nonpredator acoustically similar to predator; prior-art caveat |
| Insectivore caller | Mean d = −1.9115 (10/12 negative) | Same experiment, not another study |

All these are reexpressions of the original published 2025 experiment. The modest difference between original order strata is a descriptive observation, **not a randomization-based causal absence of carryover**, and nonpredator-call types use different fixed sound files.

## Mathematical response-to-unknown-group mapping (derived robustness, not population inference)

With 38 recorded responders from 33 groups each containing at least one responder, exactly five *extra responders* are distributed across groups. Seven integer-partition patterns for these five extras define all possible physical-group size vectors (e.g. one six-responder group and 32 one-responder groups, or five two-responder groups and 28 singles). No published source link identifies which bats share a group.

For each size vector, the equal-33-group mean is the mean of responder d_i averaged within each unknown group. For fixed group sizes, weights on bats are (1/n_g) before group division by 33. Applying the rearrangement inequality to the sorted 38 observed d_i gives the sharp minimum/maximum for that group-size vector. Enumerating all seven patterns yields:

**Any 33-group equal mean of the *recorded responder* d_i lies in [−2.5692434, −1.7530194].**

The sign is negative for **every compatible group allocation under the published 38-from-33-group constraint**. This is **not a confidence interval**, not a 33-group independent p-value, and **not** an estimate for all 117 tested bats or for groups where no calls were recorded in source. It is robust to the unknown group pairing only.

The result provides a principled structural sensitivity audit. It does not prove group-wide behavioural change in unobserved nonresponders, or that predator sound alone rather than acoustically distinctive sound structure caused the change.

## Cross-source H1 information-channel interpretation

- Germany, Lewanzik 2019: randomized feeding buzzes and activity at 12 lakes; incremental pre-activity×buzz moderator did **not** increase lake-heldout prediction in four response groups under frozen tested model.
- Panama, Carter 2015/Eckenweber 2016: distress-call response and location/caller contrasts; sources share one Barro Colorado Island field station and are *not independent regional replications*.
- Panama, Kohles 2020: original verified search-call **caller identity (WHO)** discrimination in *Molossus*, stronger matched bat evidence than across-roost inference.
- Israel, Lourie 2024: published role of roost-mediated odour as **WHEN** a known tree may be fruitful, potentially complementing personally held spatial locations.
- Costa Rica, this 2025 source: independent geographic **predator-risk suppression of outward social communication** under playback conditions. **Risk is a candidate information-channel gate**, and the main behaviour and link to group cohesion were already published.
- Canada, Wilson et al. 2026: four response species sign heterogeneity from publication; no original numbered playback records or validated control denominators in the present source index.

**Conceptual extension only:** social information is not a single amount: cues about *WHO*, *WHERE/WHEN*, *prey opportunity* and *risk to advertising a location* have distinct targets. These experiments do not yield a common estimand or independently validated global evolutionary tradeoff. A rigorous bat macro test must sample original studies with comparable treatments, controls, bat/group IDs and quantitative effort, with whole-study or whole-region holdout.

**STOP:** phylogenetic H1 pooled effects, global causal mechanism, individual social vs private memory replacement, or generalization beyond selected responders from this CSV.

Reproduction: `H1_COSTARICA_PREDATOR_RISK_PREOUTCOME_CONTRACT_V1.md`, `h1_costarica_predator_cue_source_v1.py`, `test_h1_costarica_predator_source_v1.py`, `H1_COSTARICA_2025_AUTHENTICATED_RESULT_V1.json`, CI link above. Original source raw rows and animal IDs are not in repository artifacts.
