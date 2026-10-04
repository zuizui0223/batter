# Learning-state modulation of personal flight intensity — source receipt v1

## Status

**PROSPECTIVE INDEPENDENT LEARNING-BRIDGE PROGRAMME. NO YAMADA ROW OUTCOME OPENED.**

Branch:
`prospective/learning-state-theta-v1`

This programme is independent of JAE v0.4.0 and independent of the Teshima 2026 configuration-conditioned primary.

## Biological question

The Teshima *Rhinolophus nippon* programme supports a portable one-dimensional individual movement-intensity parameter:

[
theta_i
]

that predicts held-out cross-configuration individual differences in speed/vertical-speed intensity.

The unresolved causal question is:

> **Is this personal control parameter fixed, or can spatial learning shift the operating state within the same individual?**

## Source paper

Yamada et al. (2020)

*Modulation of acoustic navigation behaviour by spatial learning in the echolocating bat Rhinolophus ferrumequinum nippon*

Scientific Reports 10:10751.

DOI:
`10.1038/s41598-020-67470-z`

## Public raw dataset

Figshare dataset explicitly cited by the 2022 BMC Biology re-analysis:

Yamada, Yasufumi; Mibe, Yurina; Yamamoto, Yuya; Ito, Kentaro; Heim, Olga; Hiryu, Shizuko (2022).

*row dataset for article entitled “Modulation of acoustic navigation behaviour by spatial learning in the echolocating bat Rhinolophus ferrumequinum nippon”*

DOI:
`10.6084/m9.figshare.19102712.v1`

Expected Figshare article id:
`19102712`.

## Published source design inherited as provenance

The source study reports:

- 14 *R. ferrumequinum nippon*;
- 7 bats in an acoustically permeable obstacle condition;
- 7 bats in an acoustically reflective obstacle condition;
- all bats naive to the obstacle layout at first exposure;
- 12 repeated flights per bat;
- first flight = unfamiliar-space state;
- twelfth flight = familiar-space state;
- maximum flight speed increased strongly with learning in the permeable condition but only weakly in the reflective condition;
- pulse emission declined with repeated experience.

These published results motivate the new contrast but are not counted as new discoveries.

## New question

The new analysis is not simply “does speed increase from flight 1 to 12?”

It asks whether the individual policy can be decomposed as:

[
x_{i,c,t}
=
mu_{c,t}
+
theta_i
+
delta_{i,c,t}.
]

Specifically:

1. **population learning shift** — does the group mean move with flight number?;
2. **personal-rank persistence** — do faster/slower individuals retain their relative ordering as learning proceeds?;
3. **personal magnitude persistence** — does an individual offset estimated from early flights predict its offset in later flights?;
4. **individual learning slope** — do bats differ in how strongly they shift with learning?

If stable personal offsets coexist with a common learning shift, the architecture becomes:

[
personal prior + plastic learning state.
]

## Relation to current one-parameter result

The Teshima 2026 transparent scalar is:

[
FlightIntensity =
mean(
z(median speed),
z(p90 speed),
z(median |vertical speed|),
z(p90 |vertical speed|)
).
]

Yamada 2020 may expose only maximum speed rather than all four components.

Therefore this programme does **not** claim to measure the identical Teshima scalar unless the raw schema actually exposes compatible kinematic variables.

If only maximum speed is available, the Yamada endpoint is treated as a **one-dimensional speed-state analogue**, not the same `theta`.

## Outcome firewall

Before opening row values:

1. inventory Figshare article/file metadata only;
2. identify filenames, sizes, hashes and types;
3. open schemas/headers only;
4. freeze exact identity / condition / flight-number / speed columns;
5. count individual and repeated-flight support without reading speed values;
6. freeze the learning-state estimator;
7. only then open speed outcomes.

## Claim ceiling

A positive result may support:

> stable individual movement-intensity differences coexist with within-individual learning-induced shifts in the same horseshoe-bat species complex.

It cannot establish:
- genetic determination;
- morphology as the source of the stable offset;
- that the Teshima and Yamada bats share the same numerical latent parameter;
- a universal bat control law.

## JAE firewall

No result from this programme modifies JAE v0.4.0.
