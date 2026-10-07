# Prat 2017 Figure-2 personal-offset primary v1

## Status

**FROZEN BEFORE FIGURE-2 LD1/LD2 MAGNITUDES ARE OPENED.**

Parent:
- `AUDIT_CONTRACT_V1.md`
- `FIGURE2_SUPPORT_AUDIT_CONTRACT_V1.md`

Numerical opening is authorized only if `FIGURE2_SUPPORT_RESULT_V1.json` reports `PASS_FIGURE2_REPEATED_SUPPORT`.

## Biological question

> During one year of shared social vocal learning, does each pup retain a stable personal vocal offset relative to the moving dialect of its own group?

This is an identity-maintenance question within groups, not a causal test of playback treatment differences.

## Source representation

Use exactly the `Figure 2` sheet from Prat et al. 2017 S1 Data.

Frozen axes:
- source LD1;
- source LD2.

The source LDA axes were defined from playback calls and are not refit to pup outcomes.

Do not rescale, rotate, whiten, PCA-transform or weight LD1/LD2.

## Pup × session state

For each source pup × session:
1. pair its LD1 and LD2 source columns;
2. retain rows where both coordinates are finite numeric values;
3. require >=5 paired calls under the structural gate;
4. calculate the arithmetic mean LD1 and arithmetic mean LD2 across those paired calls.

This yields one 2-D state per pup × session.

Calls are only measurement replicates; pups remain the biological units.

## Remove the learned group dialect

For each source group × session, subtract the equal-pup centroid from every pup state in that group/session.

For pup i at session s:

`r_i,s = q_i,s - mean_j_in_group(q_j,s)`

This removes the shared developmental movement of the group dialect at each session.

## Personal history and held-out target

Frozen history:
- sessions 1, 2 and 3;
- equal-session mean of the pup's group-centered residual states.

Frozen target:
- session 4 group-centered residual state.

For pup i:

`h_i = mean(r_i,1, r_i,2, r_i,3)`

`t_i = r_i,4`

## Identity advantage

For every pup i:
- self distance = Euclidean distance from t_i to h_i;
- donor distances = distances from t_i to histories of every other pup in the **same source group**;
- `K_i = mean(donor distances) - self distance`.

Programme statistic:
- equal mean of K_i across all 14 pups.

Positive K means session-4 vocal position is closer to the same pup's earlier within-group offset than to other pups' histories.

## Exact null

Keep sessions 1–3 histories fixed.

Within each source group, independently permute the mapping of session-4 target states to pup identities.

Group sizes:
- High-F0 = 4;
- Low-F0 = 5;
- Control = 5.

Exact null size:
`4! × 5! × 5! = 345,600`.

Enumerate all 345,600 assignments.

One-sided exact p:
`p = fraction(K_perm >= K_obs)`.

Minimum possible p:
`1 / 345600 = 0.0000028935`.

## Support rule

Confirmatory support requires:
- K > 0;
- exact p <= 0.05.

Also report descriptively:
- 14 pup-level K_i values;
- positive pup fraction;
- group-level mean K for High-F0 / Low-F0 / Control;
- leave-one-pup-out programme K.

No group-specific p-values.

## Interpretation

### Supported

> A learned group dialect can shift substantially over development while stable individual-specific vocal offsets remain detectable within the moving group state.

This would support coexistence of shared social learning and persistent personal organization.

### Unsupported

> Under the frozen playback-defined LD1/LD2 representation, session-4 within-group vocal position is not predictably closer to the same pup's earlier residual position than to other pups' histories.

This does not negate group dialect learning.

## Hard prohibitions

After LD coordinates are opened do not:
- change history to sessions 2–3;
- select only session pairs;
- select one playback group;
- use F0 instead of Figure-2 LDA coordinates;
- rotate or rescale LD axes;
- weight pups by call count;
- use call-level pseudoreplication;
- drop low-support pups that passed the frozen >=5 paired-call gate;
- replace the within-group donor set with across-group donors.

## Claim ceiling

A positive result does not establish that playback caused individuality.

It establishes only that persistent personal offsets can coexist with experimentally induced group-level social vocal learning.
