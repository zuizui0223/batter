# Early-seed versus recent-history diagnostic result v1

## Status

**EARLY-SEED PERSISTENCE UNSUPPORTED. IDENTITY-SPECIFIC REFINEMENT SUPPORTED.**

Authoritative workflow:
- run: **37391282588**
- job: **112036685644**
- conclusion: **success**
- fail-closed shell: `set -euo pipefail`
- frozen MATLAB bridge rebuilt successfully:
  - bridge files: 22
  - primary-complete juveniles: 14

Parent:
`EARLY_SEED_VS_RECENT_HISTORY_DIAGNOSTIC_V1.md`

This is a **post-primary ontogenetic mechanism diagnostic**.
It does not rescue or reclassify the failed monotonic-formation primary.

---

## Question

For late juvenile movement, target valid-day ordinals 11–20:

1. does the individual's **earliest two structurally valid independent movement days** still predict its later spatial use?
2. do the **immediately preceding two valid days** contain more identity-specific predictive information than those earliest two days?

Early and recent histories both contain exactly two days.
The comparison therefore does not give recent history a larger training-history sample.

The same frozen x/y representation, 30-s standardization, nearest-point distance and cohort-blocked whole-history identity null are used as in the Source B primary.

---

## D1 — early-seed persistence

Programme statistic:

[
E
=
E_iE_t[R^{early}_{it}],
]

where each target is predicted from valid-day ordinals 1 and 2 of each donor history.

Observed:

- `E = +15.1920`
- null mean = **-0.1388**
- calibrated excess = **+15.3308**
- null 95% interval = **[-29.2372, +31.4378]**
- one-sided permutation `p = 0.1655`
- positive juveniles = **8/14 = 57.1%**
- frozen requirement = **10/14**

Verdict:

**UNSUPPORTED_EARLY_SEED_PERSISTENCE**

The first two structurally valid independent movement days are therefore not a robust long-term personal template for target days 11–20 under the frozen rule.

This does **not** mean early movement contains no individual information.
The observed mean is positive.
It means that the early two-day history is not reliably more informative than identity-exchangeability across the required majority of juveniles.

---

## D2 — recent two days versus early two days

For every late target:

[
Q_{it}
=
R^{recent}_{it}
-
R^{early}_{it},
]

where recent history is exactly target ordinals (t-2,t-1).

Programme result:

- recent-history programme mean `R_recent = +159.2711`
- `Q = +144.0791`
- null mean = **+0.3466**
- calibrated excess = **+143.7325**
- null 95% interval = **[-47.6112, +70.5144]**
- one-sided permutation `p = 0.0001`
- positive juveniles = **10/14 = 71.4%**
- frozen requirement = **10/14**

Verdict:

**SUPPORTED_IDENTITY_SPECIFIC_REFINEMENT**

The whole-history permutation preserves:
- cohort;
- each donor's ontogenetic spatial expansion;
- early/recent chronology;
- sampling support;
- route autocorrelation within each juvenile history.

Therefore the large recent-over-early gain cannot be explained simply by the general fact that all juveniles range farther or differently later in ontogeny.

It is specifically associated with the true target-to-personal-history linkage.

---

## Individual heterogeneity

The refinement effect is not universal.

Large positive examples:
- Nadav: early **-37.77**, recent **+332.28**, Q **+370.05**
- Odelia: early **+34.51**, recent **+871.27**, Q **+836.76**
- Shem_Tov: early **+76.24**, recent **+412.88**, Q **+336.64**
- Tishray: early **-139.57**, recent **+71.30**, Q **+210.87**

Negative Q:
- Nature: **-17.51**
- Nazir: **-1.31**
- Tzedi: **-75.28**
- V: **-9.98**

All negative individuals are retained.

---

## Relation to the earlier formation primary

The original frozen formation primary asked for a common monotonic increase in self-history advantage over valid days 3–20.

That rule failed:
- mean slope above null, p = .0102;
- only 8/14 positive slopes versus required 10/14.

The new diagnostic does **not** contradict that failure.

Together the two results say:

1. development is **not** well described by one smooth, common monotonic increase in individuality;
2. the earliest two valid days are **not** a stable long-term personal seed;
3. by later early ontogeny, the immediately recent personal history contains dramatically more identity-specific predictive information.

The stronger architecture is therefore:

[
	ext{early movement}
;longrightarrow;
	ext{individual-specific updating/refinement}
;longrightarrow;
	ext{strong personal-history predictability}.
]

The timing and trajectory of that refinement differ among juveniles.

---

## Mechanistic implication

A fixed-predisposition model in which an adult-like personal spatial bias is already fully expressed in the earliest independent movement is weakened.

The result is more compatible with:

> **personal spatial organization is constructed or substantially refined during independent movement experience.**

This can arise through:
- spatial learning;
- destination/resource familiarity;
- motor refinement;
- reinforcement or switching costs;
- interaction between stable morphology/physiology and accumulated experience.

The diagnostic does not identify one of these as the unique cause.

---

## Relation to maternal/social seeding

Independent published work in the same fruit-bat system shows that mothers expose pups to specific destinations/routes before full independence.

The present Source B result does **not** directly measure maternal templates.

Therefore the combined hypothesis:

[
	ext{socially seeded early template}
ightarrow
	ext{personal refinement}
ightarrow
	ext{persistent individual policy}
]

is a cross-study synthesis, not a single-dataset causal result.

Source A's direct maternal-to-self crossover primary remains a structural STOP and is not reopened.

---

## Important wording boundary

Use:

> **earliest two structurally valid independent movement days**

not:

> first two physical flights.

Some earlier source days may fail the frozen >=20-standardized-fix validity rule.

Do not claim:
- learning as the sole source of individuality;
- absence of morphology;
- smooth monotonic canalization;
- maternal-to-self crossover from this dataset;
- a confirmed developmental breakpoint.

---

## JAE firewall

No change to JAE v0.4.0.
