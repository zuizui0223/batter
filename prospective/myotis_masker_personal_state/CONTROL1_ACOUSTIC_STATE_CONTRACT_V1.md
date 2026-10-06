# Myotis control-1 personal acoustic-state contract v1

## Status

**FROZEN BEFORE NEW NUMERICAL OUTCOME OPENING.**

## Provenance boundary

The published study already reports population-level treatment effects. During source discovery, public Zenodo preview rows were also technically visible for the control-1 file.

No individual × condition summary, self-history statistic, permutation distribution, p-value, or individual ranking was calculated before this contract was frozen.

Therefore this is **prospective with respect to the new individual-identity analysis**, not outcome-blind with respect to the original published treatment effect.

## Biological question

Does a bat-specific acoustic-control bias remain identifiable when the spatial source of masking noise changes?

This is a sensorimotor-control triangulation test, not a movement-policy replication.

## Frozen conditions

1. no_noise
2. noise_target
3. noise_above
4. noise_side

Use the mapping in MYOTIS_MASKING_STRUCTURE_AUDIT_CONTRACT_V1.md.

## Trial endpoint

For each successful trial:

s_trial = mean(sl_rms)

over the five source-selected loudest calls.

No alternative call subset.

## Equal-day individual-condition summary

For each animal i, condition c and date d:

m_i,c,d = mean over trials of s_trial.

Then equal-weight the three source days:

m_i,c = mean over dates of m_i,c,d.

Thus dates with more successful trials do not receive more weight.

## Condition centering

Remove the shared manipulation shift:

r_i,c = m_i,c - mean across bats of m_i,c.

This tests persistent relative individual organization, not the population Lombard effect.

## Cross-condition self-history statistic

For target animal i and target condition c:

h_i,-c = mean of r_i,c' over the other three conditions.

For each donor j:
h_j,-c = its corresponding other-condition mean.

Target advantage:

A_i,c =
mean over j != i of abs(r_i,c - h_j,-c)
minus abs(r_i,c - h_i,-c).

Aggregate equally across conditions within bat, then equally across bats.

Programme statistic: A_control1.

Positive means the current-context observation remains closer to that bat's own cross-context acoustic-control history than to other bats' histories.

## Exact null

Fix the no_noise label mapping as reference.

For each of the other three conditions independently enumerate all 5! bat-label permutations.

Exact null size:

(5!)^3 = 1,728,000.

For every assignment:
- preserve condition summaries;
- relabel identity only in the three non-reference conditions;
- recompute the complete statistic.

One-sided exact p =
fraction of null statistics greater than or equal to observed.

No Monte Carlo approximation.

## Primary support

Support requires:
- A_control1 > 0;
- exact p <= 0.05.

Report:
- sign of each bat's mean advantage;
- condition-specific mean advantages;
- leave-one-condition-out values descriptively.

No condition deletion can rescue a failed primary.

## Claim ceiling

A positive result supports:

a persistent individual acoustic-control bias remains detectable across experimentally altered masking-source geometry.

It does not establish movement-policy portability, origin by learning, neural mechanism, equivalence to FlightIntensity/ManeuveringExtent, or wild vertical individuality.
