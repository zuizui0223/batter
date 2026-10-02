# P. hastatus 2023 co-use localization diagnostic contract v1

## Status

POST-OUTCOME ROBUSTNESS DIAGNOSTIC.

Opened only after the corrected 2023 primary co-use result was known:
- observed 26.57 m
- phase-null mean 22.99 m
- excess +3.57 m
- p = 0.0231

Nothing in this diagnostic can replace, rescue, upgrade or invalidate that frozen primary result.

## Diagnostic A — leave-one-dyad-out

Use the exact corrected 2023 all-space encounter universe:
- 600-s tolerance
- 8 frozen dyads
- 679 fixed encounters
- same terrain-relative, session-centered z endpoint
- same phase groups
- same primary seed 20261002103
- same 9,999 phase-shift replicates

For each of the 8 frozen dyads:
- remove that dyad only;
- do not reselect dyads or individuals;
- compute the equal mean of the remaining 7 dyad medians for observed and every null replicate;
- report observed, null mean, excess and p(null >= observed).

These are post-outcome sensitivity p-values, not independent tests.

## Diagnostic B — endpoint-excluded 2023 universe

Use the exact x-y-time endpoint-excluded universe from the prior endpoint audit:
- 600-s tolerance
- 4 usable individuals
- 6 usable dyads
- 629 encounters
- endpoint-excluded scope

Because this universe failed the predeclared >=5-individual primary gate, it is **descriptive only**.

Use:
- the same terrain-relative endpoint and phase-null construction;
- B = 9,999;
- seed = 20261002113.

Report observed, null mean, excess and empirical tail location, but do not assign PASS/FAIL.

## Stop rule

Do not:
- alter the time window;
- change grid or endpoint radius;
- drop additional cells/dyads after seeing these diagnostics;
- reinterpret endpoint-excluded p as confirmatory;
- choose the most favourable leave-one-out result.
