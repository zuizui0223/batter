# Tag altitude-bias structural preflight v1 — frozen contract

Frozen before output: 2026-09-27.

This preflight uses **x-y, time and existing deployment/tag metadata only**. Numeric height values
are prohibited.

## Stationary candidate

Within each already-frozen session, a fix is a stationary candidate only when:

- both previous and next fixes exist;
- both adjacent time gaps are >0 and <=20 min;
- horizontal speed to both neighbours is <=0.5 m/s.

Coordinates use each panel/cohort's already-frozen projection.

Stationary candidates are assigned to fixed 100-m grid cells. A cell is shared only when >=3
individuals each contribute >=5 stationary-candidate fixes.

An individual has empirical offset support when it contributes >=10 stationary-candidate fixes
across >=1 shared cell.

## Panel feasibility

A panel is eligible for stationary-height offset correction only if the number of supported
individuals is at least:

`max(5, ceil(0.5 × original evaluable n))`

and at least one originally admitted cohort contains >=3 supported individuals with >=2 frozen
sessions each.

This is a **structural feasibility gate only**. Failure means the archive cannot identify a useful
stationary correction under the frozen rule; it is not evidence that tag bias is absent or present.

## Deployment timing

The same preflight reports tracking-window overlap between repeat individuals within cohort:
fraction of pairs with positive overlap, median positive overlap hours and the distribution of
tracking-window start-date differences.

This timing summary is descriptive only. No new time-block permutation family is authorized in
v1; residual timing confounding will be written as a limitation after this final audit.
