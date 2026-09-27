# Tag altitude-bias audit v1 — freeze record

Frozen before any stationary-height or centered-shape outcome was opened: 2026-09-27.

- `contract/tag_altitude_bias_preflight_v1.json`
  - blob SHA: `51afaa6c63ccf5d92b122e26f315ce2e1e7e7f2a`
- `contract/tag_altitude_bias_audit_v1.json`
  - blob SHA: `4e0f4b12260a957cb734c9a75666d59763fe925e`

The structural preflight may inspect x-y, timestamps and existing deployment/tag metadata only.
Numeric vertical values are prohibited in that stage.

The primary centered-shape contract fixes:
- per-session median centering;
- residual bins `[-inf,-400,-200,-100,-50,0,50,100,200,400,inf]` m;
- 5-km common-cell weighting;
- exact original evaluable-individual counts;
- existing panel-specific permutation counts and seeds;
- one-sided p<=0.05 with positive observed-minus-null mean.

The secondary stationary-height correction may be run only where the preflight's already-frozen
structural feasibility rule is met. It cannot rescue a failed primary centered-shape result.

Any modification of either contract after an output exists creates a new analysis family/version
and may not overwrite v1.

This v1 family is the declared final post-hoc empirical robustness audit before submission.
