# Tadarida residual-confound robustness v1 — frozen contract

Frozen: 2026-09-27

The manuscript rewrite is paused until three remaining focal confounds are tested under rules
fixed before output.

## A. AGL common-cell calibration — primary

Use the checksum-pinned annotated table, `animal-id × BatDay` sessions, 5-km EPSG:3035 cells,
the existing AGL field `height_true`, existing vertical bins and Jeffreys alpha 0.5.

Before any new result is accepted, reproduce the frozen ordinary AGL values to 1e-12:

- conditional = +0.33655976011332095;
- marginal = -0.25489567533550034;
- advantage = +0.5914554354488213;
- n = 6.

Then calculate the same common-cell-weighted marginal used in the MSL calibration and run 9,999
whole-session label permutations.

**Pass rule:** at least 5 evaluable individuals, observed-minus-null mean common-cell marginal > 0,
and one-sided `P(null >= observed) <= 0.05`.

A pass supports terrain-relative vertical identity at 5 km. A failure blocks that claim.

## B. Night-endpoint / roost-proxy exclusion — primary radius 1 km

No biological roost coordinate is inferred from outcome data.

The proxy uses x-y and time only:

1. sort each retained BatDay by timestamp;
2. take the first 5 and last 5 projected fixes;
3. pool those endpoints across nights within each bat;
4. define the bat's proxy center as the **medoid endpoint** minimizing summed Euclidean distance
   to all pooled endpoints.

This is deliberately called a **night-endpoint/roost proxy**, not a verified roost.

Primary exclusion:

- remove fixes <1,000 m from their own bat's proxy center;
- apply the same exclusion to target and training events;
- retain original BatDay IDs;
- after exclusion, require >=50 events/session;
- rerun 5-km AGL common-cell calibration with 9,999 permutations.

Descriptive fixed-radius sensitivities: 500 m and 2,000 m, 4,999 permutations each.

**Pass rule:** >=5 evaluable individuals, calibrated common-cell marginal >0, upper-tail p<=0.05.

A failure means departure/arrival or central-place structure remains a viable contributor.

## C. AGL grid sensitivity

Without endpoint exclusion, rerun common-cell AGL identity at:

- 2.5 km;
- 10 km.

Each uses 4,999 whole-session permutations.

The primary scale endpoint is **common-cell marginal identity**. Conditional advantage is
secondary/descriptive.

Each scale passes if:

- >=5 evaluable individuals;
- calibrated common-cell marginal >0;
- upper-tail p<=0.05.

Only if **both** scales pass may the manuscript say the focal terrain-relative identity persists
across the tested 2.5–10-km grain. One-scale failure must be reported as scale dependence.

## Predeclared manuscript decision rule

Strongest permitted focal statement requires A + B + both C scales to pass:

> Repeatable focal vertical identity persists relative to terrain, away from the night-endpoint
> neighborhood, and across 2.5–10-km horizontal grain.

If A passes but B fails, terrain-relative identity remains supported but near-roost/departure-
arrival structure cannot be excluded.

If A fails, the paper may not use AGL to support terrain-independent individuality.

If either C scale fails, grain robustness is restricted to the scales that pass.

Individual bootstrap intervals must be reported, but are descriptive uncertainty rather than a
second significance gate.

Nothing in this contract may be retuned after output.
