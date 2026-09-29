# Multi-day temporal-persistence feasibility preflight v1

## Status

**X-Y-TIME ONLY. No vertical persistence outcome was opened.**

Authoritative workflow:
- run: `36538374767`
- head: `5590f6a68e2a9f2b3303c0e23c3e4426c579bd4a`
- artifact: `11018559529`
- digest: `sha256:25ace01da68ba9fb8598d831481288c98f05fbc3f609096f654209c9761d12e0`

## Frozen result

No lag passed the all-five-panel support gate.

| minimum self-history lag | Eidolon | Hypsignathus | P. 2022 | P. 2023 | P. 2016 |
|---|---:|---:|---:|---:|---:|
| >=7 d | 0/12 | 20/23 | 17/32 | 0/14 | 0/10 |
| >=3 d | 4/12 | 22/23 | 25/32 | 11/14 | 0/10 |
| >=1 d | 7/12 | 22/23 | 31/32 | 13/14 | 8/10 |

The five-panel vertical outcome is therefore **not opened**.

## Structurally evaluable 1-day subset

At >=1 day, all four non-Eidolon panels pass the frozen support gate:
- *Hypsignathus*: 22/23
- *P. hastatus* 2022: 31/32
- *P. hastatus* 2023: 13/14
- *P. hastatus* 2016: 8/10

A separate four-panel >=1-day persistence test may be opened with those exact n values.

## Interpretation

The archive can test whether vertical organization persists across at least one day in four systems. Longer-lag generalization is structurally limited: P2016 loses all >=3-day self support, and Eidolon/P2023 also lose support at longer lags.
