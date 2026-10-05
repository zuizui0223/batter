# Peer-controlled early-to-late policy persistence contract v1

## Status

**POST-OUTCOME STABLE-POLICY DIAGNOSTIC.**

Frozen after:
- strict-past self-history prediction was supported in both P. hastatus years;
- raw within-individual temporal state ordering exceeded a fixed-trait + exchangeable-noise null;
- that short-lag state ordering became unsupported after contemporaneous peer correction.

No peer-controlled early-to-late individual-identity result has yet been calculated.

## Question

After removing short-term allocation shifts shared with contemporaneous conspecifics, does a persistent **individual-specific policy offset** remain from the early part of the record to the late part?

This distinguishes:

[
A_{it}=	heta_i+eta_t+arepsilon_{it}
]

from a model with only shared temporal forcing (eta_t) and no stable individual parameter (	heta_i).

## Data

Use exactly the fixed-bin 360-s P. hastatus sessions and transparent allocation scalar

[
A=(H-V)/sqrt2
]

from the existing field bridge.

Analyse 2022 and 2023 separately.

## Peer correction

Use the exact (pm12) h, >=2-donor peer correction from
`PEER_CONTROLLED_STATE_PERSISTENCE_CONTRACT_V1.md`.

For each eligible focal session:

[
A^{resid}_{it}=A_{it}-overline A_{mathrm{other bats},t}.
]

No focal individual's own sessions enter its peer correction.

## Early/late split

Within each biological individual separately:

1. order peer-controlled sessions by source start time;
2. require at least **4** eligible sessions;
3. split chronologically after (lfloor n_i/2floor):
   - early = first (lfloor n_i/2floor) sessions;
   - late = remaining sessions;
4. require at least 2 early and 2 late sessions.

Early personal parameter:

[
hat	heta_i^{early}=mathrm{mean}(A^{resid}_{i,mathrm{early}}).
]

## Held-out late identity advantage

For each late target session q of focal individual i:

- self distance:
  [
  D_{self}=|A^{resid}_{iq}-hat	heta_i^{early}|;
  ]

- donor distance:
  equal-donor mean distance to the early centroids of other eligible individuals in the same frozen cohort.

Require at least 2 donor individuals.

[
K_q=D_{other}-D_{self}.
]

Aggregate:
- equal late targets within individual;
- equal individuals within year.

Primary statistic:
[
K_{early	o late}.
]

## Null

Within each frozen cohort:
- keep every early centroid value fixed;
- keep every late target value and target identity fixed;
- permute the mapping of early centroids to biological individual labels.

This preserves:
- cohort;
- peer-corrected early-value distribution;
- late-value distribution;
- sampling support;
- shared environmental correction.

It destroys only early-to-late individual correspondence.

9,999 permutations.

Seeds:
- 2022: `202610051561`
- 2023: `202610051562`.

One-sided positive p.
Require >=9,500 valid permutations.

## Secondary rank statistic

Across eligible individuals within each cohort:
- late centroid = equal-session mean peer-controlled late value;
- compute Spearman correlation between early and late centroids.

Report descriptively; do not use it to rescue the primary K criterion.

## Support rule

A year supports stable peer-controlled policy persistence if:
- (K_{early	o late}>0);
- p <= 0.05;
- >=70% of evaluable individuals have positive individual mean K.

## Interpretation

### Supported

Short-term shared environmental forcing can explain the residual serial autocorrelation, but it does not erase the **persistent individual policy offset**.

The parsimonious architecture becomes:

[
	ext{stable individual policy }	heta_i
+
	ext{shared time-varying environment }eta_t
+
	ext{residual noise}.
]

### Unsupported

The strict-past identity result may be substantially driven by shared temporal structure rather than a stable individual parameter.

## Ceiling

Support does not identify the origin of (	heta_i):
- morphology;
- physiology;
- development;
- learned long-term policy;
- or a mixture.
