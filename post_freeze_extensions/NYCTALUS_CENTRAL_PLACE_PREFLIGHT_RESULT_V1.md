# Nyctalus central-place structural preflight result v1

## Status

**NONVERTICAL STRUCTURAL PREFLIGHT. Numeric Height values were never parsed.**

Authoritative workflow:
- run: `36700126597`
- head: `6b5559d7736806c92ce80cbd8718ad796553fb54`
- artifact: `11088834852`
- digest: `sha256:c4cfe0242fedf20d9029e4e2d93600be1d11b5ed3ae943ef79d90a693b45b1a8`

Reference evaluable n for the existing 5-km × HMM-state analysis: 27.
Frozen gate: retain at least 70%, i.e. **19 individuals**.

## Candidate support

| candidate | distance-from-track-start bins (km) | evaluable n | gate |
|---|---|---:|---|
| near_only | 0–0.5 / >0.5 | **24** | PASS |
| near_intermediate | 0–0.5 / 0.5–2 / >2 | **22** | PASS |
| near_mid_far | 0–0.5 / 0.5–2 / 2–5 / >5 | **22** | PASS |

Per the frozen rule, select the **finest structurally supported** candidate:

> **near_mid_far: 0–0.5 / 0.5–2 / 2–5 / >5 km**

The vertical paired attribution test may open with exact expected n=22.

## Claim boundary

`dist_start` is validated as distance from track start, not verified roost distance. The ecological interpretation is therefore central-place / flight-stage proxy, not exact roost-distance causation.
