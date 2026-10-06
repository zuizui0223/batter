# Sample-size planning v1

## Status

**PROSPECTIVE PLANNING ONLY.**

This document sets the sample-size logic for the matched-family solution-repertoire experiment before confirmatory outcomes are opened.

The final confirmatory test is a paired randomization test induced by the within-individual randomized assignment of matched obstacle family to OPEN versus CONSTRAINED acquisition.

For transparent planning only, power is approximated with a one-sided paired t model on the individual treatment contrast:

Delta_i = A_i,OPEN - A_i,CONSTRAINED.

Standardized paired effect:

d = mean(Delta_i) / sd(Delta_i).

## Approximate power

One-sided alpha = 0.05.

| evaluable bats | d=0.5 | d=0.6 | d=0.7 | d=0.8 | d=1.0 |
|---:|---:|---:|---:|---:|---:|
| 10 | 0.427 | 0.543 | 0.655 | 0.754 | 0.898 |
| 12 | 0.492 | 0.619 | 0.735 | 0.829 | 0.945 |
| 14 | 0.551 | 0.685 | 0.798 | 0.882 | 0.971 |
| 16 | 0.604 | 0.740 | 0.847 | 0.920 | 0.985 |
| 18 | 0.652 | 0.787 | 0.886 | 0.946 | 0.992 |
| 20 | 0.695 | 0.827 | 0.915 | 0.964 | 0.996 |
| 24 | 0.768 | 0.886 | 0.954 | 0.984 | 0.999 |

## Decision

Target:
- 18-20 evaluable biological individuals.

Hard structural minimum:
- 14 evaluable biological individuals.

Reason:
- n=14 is approximately the first listed design reaching 80% power for d around 0.7;
- n=18-20 gives materially better protection against a moderate paired effect;
- n=10-12 would recreate the programme's current small-sample vulnerability.

If fewer than 14 animals complete the required phases, the confirmatory primary returns STRUCTURAL STOP.

No post-outcome lowering of the minimum.

## Why no 70% positive-individual primary gate

The treatment is randomized within individual.

The paired randomization test is therefore the clean causal test.

Adding a separate >=70% positive-individual requirement would impose a second, discretized threshold with poor and non-monotonic power as N changes.

Instead report:
- positive-individual fraction;
- leave-one-individual-out treatment effect;
- maximum single-individual influence.

If one deletion reverses the sign of the treatment effect, classify the result as fragile/outlier-sensitive.

## Caveat

These calculations assume an approximately continuous paired treatment contrast and are used only for planning.

They do not replace:
- exact treatment randomization;
- route-capability structural checks;
- trial-level support checks;
- the final preregistered analysis.

Re-run this planning script only before outcome opening if the design itself changes.
