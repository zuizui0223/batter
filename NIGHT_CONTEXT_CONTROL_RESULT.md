# Same-night context control v1

Date: 2026-09-26

## Question

Could the apparent cross-night individual signature simply reflect night-specific atmospheric
conditions? The control compares two predictors for each target session:

1. the same bat on another night;
2. other bats flying during the **same calendar night** as the target.

Night identity was frozen as UTC timestamp shifted backward by 12 hours and then converted to a
calendar date, which keeps an evening-to-next-morning nocturnal flight in one night bin.

## Result at 5 km

### Height above ground (AGL)

- evaluable individuals: 5
- equal-individual mean self-vs-same-night gain: **+0.4840 nats/fix**
- positive individual means: **4/5**
- individual median: **+0.3527**

Individual means:

- Bat3: +0.3527
- Bat4: -0.3997
- Bat6: +1.1213
- Bat7: +0.0989
- Bat8: +1.2469

### Height above mean sea level (MSL)

- evaluable individuals: 5
- equal-individual mean self-vs-same-night gain: **+0.4357 nats/fix**
- positive individual means: **4/5**
- individual median: **+0.1007**

Individual means:

- Bat3: +0.0294
- Bat4: +0.1007
- Bat6: +0.3002
- Bat7: -0.0800
- Bat8: +1.8280

The contemporaneous baseline was typically based on five or six other tracked bats on the same
night, so the comparison is not a single-donor contrast.

## Ecological interpretation

The vertical signature is not well explained as a shared calendar-night state. For most evaluable
animals, another night from the **same individual** predicts local vertical state better than
multiple other animals exposed to the **same night**.

This strengthens the interpretation of persistent individual organization of 3-D airspace use.
It does not prove that unmeasured conditions are irrelevant, but it rules out the simplest
"everyone responds similarly to tonight's conditions" explanation.

Bat4 remains an informative exception in AGL, and Bat7 remains weaker in MSL. Individual
heterogeneity is therefore still part of the result rather than noise to be averaged away.

## Claim ceiling

This control does not establish foraging, learning, personality or a causal mechanism. It
specifically tests whether contemporaneous night context outpredicts cross-night individual
history under the same spatially conditioned scoring architecture.
