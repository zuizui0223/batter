# Nyctalus source-RSF resource-context structural preflight result v1

## Status

**NONVERTICAL STRUCTURAL PREFLIGHT. Numeric Height values were never parsed.**

Authoritative workflow:
- run: `36701521537`
- head: `7ece3ae1b2247478bfc700ad69c61b2544e7745b`

Deterministic source linkage:
- linked rows: **8,129**
- maximum observed-to-RSF used-row link distance: **0.502 m**

Frozen gate:
- reference HMM-state n = 27
- required n = **19** (>=70%)

## Candidate contexts

| candidate | definition | evaluable n | gate |
|---|---|---:|---|
| roost_landcover | 5-km cell × HMM state × roost-distance 4-bin × detailed 50-m land cover | **20** | PASS |
| roost_forest | 5-km cell × HMM state × roost-distance 4-bin × forest/other | **24** | PASS |
| roost_only | 5-km cell × HMM state × roost-distance 4-bin | **25** | PASS |

Per the frozen priority rule, the selected context is the finest supported family:

> **roost_landcover**

Distance bins:
- 0–0.5 km
- 0.5–2 km
- 2–5 km
- >5 km from the source-defined closest potential roost.

Land cover:
- source `main_clc2_ratrel` 50-m context classification.

The one paired vertical attribution may now open with exact expected n=20.
