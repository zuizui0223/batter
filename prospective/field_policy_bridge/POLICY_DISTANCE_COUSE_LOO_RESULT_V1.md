# Policy-distance/co-use leave-one-individual robustness result v1

## Status

**NO ONE-INDIVIDUAL DELETION RESCUES A POSITIVE POLICY–SPACE COUPLING.**

**Evidence provenance:** this robustness analysis inherits the post-outcome status of the H/V policy coordinates. It strengthens only the conditional negative mapping result; it does not promote H/V into a confirmatory wild carrier. See `FIELD_EVIDENCE_PROVENANCE_GUARD_V1.md`.

Parent:
`POLICY_DISTANCE_COUSE_LOO_CONTRACT_V1.md`

Inputs are already-opened frozen outputs:

1. individual H/V policy coordinates from
   - workflow **37292966637**
   - job **111707482750**
   - 9,999-permutation horizontal/vertical policy-coupling analysis;

2. authoritative co-use dyad endpoint receipt and policy-distance result from
   - workflow **37296670608**
   - job **111719404182**
   - receipt-only implementation `policy_distance_couse_separation_receipt_v2.py`.

The calculation below was independently reproduced from those fixed outputs using the exact frozen node-deletion statistic, NumPy permutation generator and frozen seeds.

A fail-closed GitHub workflow using the same receipt-only implementation is retained as the machine replication path.

## Question

Could a single biological individual with several unusual dyads mask an otherwise strong positive relation between persistent policy distance and synchronous vertical separation?

For every admissible biological individual:

1. remove the individual;
2. remove every co-use dyad incident to that individual;
3. require >=5 remaining dyads;
4. recompute Spearman rho.

The most favorable deletion is then selected:

[
T_{max}=\max_i\rho_{(-i)}.
]

The permutation null repeats the **entire deletion scan**, so the p-value already pays the selection cost of choosing the best individual to delete.

## 2022

Admissible deletions: **6**

| deleted individual | remaining dyads | rho |
|---|---:|---:|
| 7250872 | 7 | +0.3571 |
| 74DB9C0 | 7 | +0.4643 |
| 7CCA9E6 | 6 | **+0.7143** |
| 7CDC7CF | 8 | −0.1667 |
| 7CDF3E7 | 6 | +0.0857 |
| 7CE04A9 | 6 | −0.0286 |

Deletion-profile summary:
- minimum rho = **−0.1667**
- median rho = **+0.2214**
- maximum rho = **+0.7143**
- fraction positive = **4/6**
- fraction >=0.3 = **3/6**
- maximizing deletion = **7CCA9E6**

Selection-corrected max-statistic null:
- valid permutations = **9,999**
- seed = **202610052201**
- null maximum-rho mean = **+0.4033**
- null central 95% = **[−0.2143, +0.9429]**
- one-sided max-stat p = **0.2058**

Verdict:
`NO_ONE_INDIVIDUAL_DELETION_RESCUE`

The apparently favorable rho=0.714 after dropping 7CCA9E6 is not unusual once the analysis acknowledges that the most favorable deletion was selected from six possibilities.

## 2023

Admissible deletions: **5**

| deleted individual | remaining dyads | rho |
|---|---:|---:|
| 989001041827562 | 7 | −0.5357 |
| 989001041827563 | 5 | −0.3000 |
| 989001041827573 | 5 | **+0.5000** |
| 989001041827592 | 6 | −0.4857 |
| 989001041827637 | 5 | −0.3000 |

Summary:
- minimum rho = **−0.5357**
- median rho = **−0.3000**
- maximum rho = **+0.5000**
- fraction positive = **1/5**
- fraction >=0.3 = **1/5**
- maximizing deletion = **989001041827573**

Selection-corrected null:
- valid permutations = **9,999**
- seed = **202610052202**
- null maximum-rho mean = **+0.3782**
- null central 95% = **[−0.5357, +0.9429]**
- one-sided max-stat p = **0.4823**

Verdict:
`NO_ONE_INDIVIDUAL_DELETION_RESCUE`

## Joint interpretation

The primary full-network result already showed no positive policy-distance/spatial-separation relation:

- 2022: rho = +0.1879, p = 0.2743;
- 2023: rho = −0.1905, p = 0.6887.

The node-deletion sensitivity adds:

> **No single biological individual can be removed to reveal a positive coupling stronger than expected after explicitly correcting for selection of the most favorable deletion.**

This directly addresses the most obvious small-network robustness objection.

It does not establish equivalence to zero.

## Ecological consequence

The result now has a stronger structure than a simple non-significant correlation.

In 2023:
- the panel-level synchronous co-use analysis detects excess vertical separation;
- persistent H/V movement-policy individuality is also supported;
- yet policy distance does not identify which dyads separate;
- deleting the most inconvenient individual still does not rescue the mapping.

Thus:

[
\boxed{
\text{persistent policy differentiation}
\not\Rightarrow
\text{pairwise spatial partitioning}
}
]

under the tested field geometry.

The interaction layer and the persistent policy layer can coexist without being the same dyadic organization.

## Claim ceiling

Supported:
- no positive full-network association in either year;
- no selection-corrected one-individual-deletion rescue.

Not supported:
- exact independence;
- absence of nonlinear coupling;
- absence of coupling at other spatial/temporal scales;
- equivalence of rho to zero;
- absence of competition.
