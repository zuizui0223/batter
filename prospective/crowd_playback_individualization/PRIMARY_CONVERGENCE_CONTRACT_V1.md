# Crowd-playback developmental convergence primary v1

## Status

**FROZEN BEFORE THIS PROGRAMME OPENS S1-DATA FIG.2 NUMERIC COORDINATES.**

Source:
Prat et al. (2017), PLOS Biology.
S1 Data:
`10.1371/journal.pbio.2002556.s011`.

## Source-defined representation

Use only the pup-level average coordinates underlying **Fig. 2**.

The two axes are the source's fixed LDA axes trained on the three playback stimulus sets, not on the pup outcomes.

For pup i and recording session s:

[
z_{i,s}=(LD1_{i,s},LD2_{i,s}).
]

The same axes are used in all four sessions.

No re-fitting, rotation, scaling, PCA, F0-only endpoint, entropy-only endpoint, or call-level re-analysis is allowed.

## Developmental sessions

Use exactly:
1. 12–18 weeks;
2. 31–35 weeks;
3. 40–43 weeks;
4. 48–51 weeks.

Primary asks whether pups sharing a playback history become more internally similar from the earliest to the latest session.

## Final cohort

Use the final Fig. 2 pup cohort exactly as represented in S1 Data:

- High-F0 = 4;
- Low-F0 = 5;
- Control = 5;
- total = 14.

Because:
- one High-F0 pup died;
- one original control pup died;
- one mother+pup was later added to control,

the final 14-pup cohort is **not treated as a clean original randomized cohort**.

Inference is explicitly:

> **conditioned final-cohort playback-group permutation**

and not an unqualified randomized-treatment test.

If S1 Data structurally identifies the late-added control pup, report a 13-pup original-survivor sensitivity descriptively, but do not replace the final-cohort primary.

## Within-group individual dispersion

For playback group g and session s:

[
W_{g,s}
=
rac{1}{n_g}
sum_{iin g}
||z_{i,s}-ar z_{g,s}||_2^2.
]

Equal-group aggregate:

[
W_s
=
rac{1}{3}
sum_{gin{High,Low,Control}}
W_{g,s}.
]

Every group receives equal weight regardless of n=4/5/5.

## Primary statistic

Freeze the longest-exposure contrast:

[
Q=W_4-W_1.
]

Interpretation:
- Q < 0 = pups sharing playback history are more internally converged at the final than earliest recording;
- Q > 0 = within-history differentiation increased.

The endpoint does not use the already-published group centroid separation statistic.

## Null

Hold each pup's four-session trajectory fixed as a unit.

Permute final playback-group labels across pups while preserving group sizes:

- High = 4;
- Low = 5;
- Control = 5.

For every legal assignment:
1. apply the same group label to all four sessions of a pup;
2. recompute W1;
3. recompute W4;
4. recompute Q.

If sex labels are structurally recoverable for all pups in S1 Data, the exact null preserves the observed sex count within each playback group.

If sex is not recoverable in S1 Data:
- preserve group sizes only;
- mark the result **FINAL_COHORT_CONDITIONED**.

No acoustic coordinate enters the choice of null architecture.

## Direction and test

The biological prediction is convergence under shared dialect learning.

Primary is one-sided:

[
p=P(Q_{perm}le Q_{obs}).
]

Support requires:
- Q < 0;
- permutation p <= 0.05.

Enumerate the full legal assignment space if <=1,000,000.

Otherwise use >=499,999 Monte Carlo assignments with a seed frozen before coordinate opening.

## Developmental-shape diagnostics

After primary, report descriptively:
- W1, W2, W3, W4;
- each W_{g,s};
- session-wise observed-vs-null percentile;
- Q for each group separately.

No additional session-specific p-values.

Session2/3 cannot rescue a failed session4-vs-session1 primary.

## Relation to published dialect separation

The source paper already shows that group means become separable from session2 onward.

This new test asks a different question:

> **Did dialect formation also reduce individual differentiation within a shared social-acoustic history?**

Possible outcomes are therefore biologically distinct:

### Group means separate + Q supported negative
Shared social history both shifts and canalizes vocal phenotype.

### Group means separate + Q unsupported
A group dialect can form while substantial within-group individuality persists.

### Q positive
Shared playback history is associated with increasing within-group differentiation despite group-level dialect formation.

## Claim ceiling

Even a supported result is not a clean original-randomization causal estimate because of post-assignment mortality and the later-added control pup.

Allowed wording:

> **Within the final experimental cohort, pups sharing a year-long playback history became more internally similar in the fixed playback-derived dialect coordinate space than expected under conditioned group-label reassignment.**

Do not write:
- playback causally reduced total individuality across the full repertoire;
- social learning erases individuality;
- the result generalizes to movement-policy formation.

## Hard prohibitions

After coordinate opening do not:
- switch to session2 or session3 as primary;
- drop High-F0 because its stimulus was unnatural;
- remove the added control based on outcome;
- switch to F0-only;
- re-fit LDA on pup data;
- weight groups by number of pups;
- use call-level pseudoreplication;
- choose a different distance metric.
