# Post-primary robustness result v1

## Status

**POST-PRIMARY DIAGNOSTIC — NOT CONFIRMATORY.**

Branch:
`prospective/task-reset-lockin-v1`

Authoritative workflow:
- run: **37206395065**
- job: **111448366784**
- artifact: **11305260597**
- artifact ZIP SHA256: `c9759960f9b23aca966e6b8eaebf72589d93d35323178f40f9bfc4e1fe43c6a0`

Parent:
`POST_PRIMARY_ROBUSTNESS_CONTRACT_V1.md`

Primary reference:
- route A = +0.225934, p=0.0003;
- cross-configuration policy K = +0.943560, p=0.0001.

## A1 — start-centered route identity

After subtracting each trajectory's own start position:

- A = **+0.058606**
- null mean = -0.000934
- null 95% interval = [-0.227277, +0.258243]
- p = **0.3039**
- positive bat means = **1/4**

Verdict:
**FAIL_A_IDENTITY**

Thus the primary literal-route identity is not robust to removing absolute translation in the arena.

## A2 — chord-residual route shape

After removing each trajectory's own start and end placement and the straight-line start-to-end chord:

- A = **-0.011216**
- null mean = +0.000173
- null 95% interval = [-0.166311, +0.183408]
- p = **0.5397**
- positive bat means = **2/4**

Verdict:
**FAIL_A_IDENTITY**

Therefore the primary A effect should not be interpreted as a repeatable individual curvature/meandering template.

### Revised interpretation of Primary A

The absolute-coordinate route signal is real under its frozen primary definition, but it is carried mainly by where the route is placed in the arena rather than by a translation-invariant route shape.

This may reflect:
- repeatable entry/exit placement;
- repeatable lane/location choice within a configuration;
- or a repeated experimental start-state component.

Without source-validated trial-start provenance, it should not be used as strong evidence for task-specific learned route shape.

## B1 — leave-one-feature-out stability

Removing any one of the eight primary features leaves a large positive K.

| dropped feature | K | fraction of full K |
|---|---:|---:|
| median speed | 0.8269 | 0.876 |
| p90 speed | 0.8120 | 0.861 |
| median abs vertical speed | 0.8877 | 0.941 |
| p90 abs vertical speed | 0.8398 | 0.890 |
| median abs horizontal turn rate | 0.9767 | 1.035 |
| p90 abs horizontal turn rate | 0.9439 | 1.000 |
| path efficiency | 0.9408 | 0.997 |
| vertical range | 0.8544 | 0.906 |

All five bat-level means remain positive in every leave-one-feature-out version.

Therefore no single frozen feature is necessary for the full cross-configuration identity signal.

## B2 — performance-magnitude-only transfer

Features:
- median/p90 3-D speed;
- median/p90 absolute vertical speed;
- vertical range.

Result:

- K = **+1.032607**
- positive bats = **5/5**
- null mean = -0.017456
- null 95% interval = [-0.349256, +0.488638]
- p = **0.0001**

Thus stable performance magnitude is sufficient to carry a strong cross-configuration individual signature.

## B3 — steering-style-only transfer

Features:
- median absolute horizontal turning rate;
- p90 absolute horizontal turning rate;
- path efficiency.

This diagnostic removes:
- 3-D speed magnitude;
- vertical speed magnitude;
- vertical range.

Result:

- K = **+0.269607**
- positive bats = **5/5**
- null mean = -0.013811
- null 95% interval = [-0.184108, +0.244603]
- p = **0.0189**

Thus the transferable identity is not reducible to speed and vertical-scale magnitude alone.

A weaker but directionally consistent steering/efficiency signature also transfers across configurations.

## Mechanistic update

The diagnostics weaken the earlier `task-specific literal-route lock-in` interpretation.

The best current reading is:

> *Rhinolophus nippon* individuals carry a configuration-general flight-policy/performance signature across obstacle geometries, while absolute route placement can also repeat within a configuration.

The portable signature has at least two components:

1. **performance magnitude** — strong;
2. **steering/efficiency style** — weaker but present across all five individuals.

This is more consistent with a stable individual sensorimotor/performance prior than with a single memorized route.

History and learning can still act on top of that prior to determine the realized solution in a given task.

## Remaining discriminator

The steering-only diagnostic still uses turning **rate**, which contains time scale.

The next high-value robustness test is therefore a scale-free geometry-only policy test that removes:
- elapsed time;
- speed;
- absolute spatial scale.

That diagnostic is frozen separately in:
`GEOMETRY_ONLY_POLICY_DIAGNOSTIC_CONTRACT_V1.md`.

## Claim boundary

These diagnostics are post-primary and must not be represented as independent prospective replication.

The confirmed primary remains the frozen A/B result; these analyses refine its mechanism interpretation.
