# Orthogonal route practice — GitHub Actions execution receipt

## Execution and source provenance
**SYNTHETIC DIAGNOSTIC, not empirical animal evidence.**

- GitHub Actions run: 37740216195
- Workflow: `orthogonal-route-practice-identifiability-v1`
- Code head at execution: `43167a3eb8c550801c602f2e2a497c35321339ff`
- Conclusion: **success**
- All invariant-check and five-model steps: **success**
- Artifact ID: `11533017932`, `orthogonal-route-practice-v1`, content file `ORTHOGONAL_ROUTE_PRACTICE_RESULT_V1.json`.

## Independent check
A separately written NumPy implementation in the current runtime re-executed all five frozen scenarios with root seed `202610081616` (N=20, 5 blocks, 8 choices, 1,000 replicate datasets), maintaining independent per-condition streams except the intentionally coupled causal-model pair.

The independent result matches the authoritative Actions artifact **exactly** for each model's:
- 1,000-run support count: 39; 1000; 1000; 40; 1000 respectively;
- mean practice-choice hit fraction;
- mean seed-choice hit fraction;
- mean practice-specific true cost gain.

No discrepancy was observed. The two practice-plus-performance worlds were matched trial by trial for all 1,000 datasets. The local code and machine summary were saved as `batter_orthogonal_independent.py` and `batter_orthogonal_independent_result.json`; they do not replace the authoritative GitHub artifact.

## Interpretation / ceiling
Exact conditional randomization in five blocks yields `9^5=59,049` legal P assignments when practice P must differ from seeded S. The correct null expectation is one-third of the **non-seed** choices, not one-quarter of every choice.

The completed diagnostic establishes a mathematical possibility of independent practice→choice and practice→cost effects without identifying causal cost mediation. It does not add biological bat samples or solve the sensory/motor isolation problem necessary for an animal mediator intervention.

Do not promote this simulation into a P1 or JAE empirical result.
