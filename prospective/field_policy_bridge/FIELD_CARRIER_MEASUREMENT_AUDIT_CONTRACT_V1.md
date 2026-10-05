# Field carrier measurement-architecture audit contract v1

## Status

**POST-OUTCOME DIAGNOSTIC — CANNOT RESCUE THE FROZEN WILD CARRIER GATE.**

The frozen wild FlightIntensity carrier result is already known:

- *Hypsignathus monstrosus*: PASS;
- *Phyllostomus hastatus* 2022: PASS;
- *P. hastatus* 2023: FAIL in the negative direction;
- *P. hastatus* 2016: structural STOP because at least one cohort-level raw feature SD was zero/non-finite.

Overall carrier gate:
**2/4 — FAIL.**

Therefore:
- the downstream wild policy-to-vertical-shape bridge remains closed;
- nothing in this audit can reclassify a failed/stopped panel;
- no harmonization result can override the frozen gate.

## Question

Why did the same species, *P. hastatus*, show:

- strong FlightIntensity persistence in 2022;
- strong failure in 2023;
- structural non-identifiability in 2016?

Before proposing ecological temporal contingency, test whether the contrast is plausibly explained by measurement/session architecture.

## Panels

Use exactly the four frozen field panels and source contracts already used by
`WILD_FLIGHT_INTENSITY_PERSISTENCE_CONTRACT_V1.md`.

No new source, individual, manipulation, or session definition.

## Session construction

Reuse the exact frozen source admission and sessionization:
- same source/reference files;
- same source exclusions;
- same >4 h session split;
- same minimum source session size;
- same cohort definitions;
- same projection;
- same height field selected by the frozen panel contract.

Do not alter session boundaries.

## Measurement quantities

For every source-admitted session, before the >=50 valid-interval policy gate, report:

### Temporal sampling
- source rows;
- positive finite consecutive dt count;
- valid policy interval count under the frozen rule `0 < dt <= 1800 s`;
- fraction of consecutive intervals retained;
- median dt;
- p10 dt;
- p90 dt;
- maximum dt among retained intervals;
- session duration from first to last admitted fix.

### Spatial/vertical quantization diagnostics
Using the same ordered admitted fixes:
- fraction of consecutive intervals with zero horizontal displacement;
- fraction with zero vertical displacement;
- number of unique raw height values;
- unique-height fraction = unique heights / source rows;
- median absolute non-zero height step;
- p90 absolute height step.

These are measurement-structure diagnostics, not individuality endpoints.

### Raw policy features
Compute exactly the four pre-standardization session features from the frozen carrier:
1. median 3-D speed;
2. p90 3-D speed;
3. median absolute vertical speed;
4. p90 absolute vertical speed.

Do not z-score for the first-level audit.

## Cohort summaries

For each frozen cohort report:
- number of source-admitted sessions;
- number with >=50 valid intervals;
- number of individuals represented;
- number of individuals with >=2 policy-valid sessions;
- median and IQR of valid intervals/session;
- median and IQR of median dt;
- median and IQR of session duration;
- median zero-vertical-step fraction;
- median unique-height fraction;
- sample SD of each of the four raw policy features;
- minimum/maximum of each feature.

Explicitly flag any feature with:
- SD = 0;
- non-finite SD;
- >95% of policy-valid sessions taking one identical value.

## Panel summaries

Aggregate cohort summaries without pooling raw rows across cohorts.

For each panel report median cohort-level values and the complete cohort table.

For 2022 vs 2023 *P. hastatus*, additionally report descriptive ratios/differences for:
- median dt;
- valid intervals/session;
- duration;
- zero-vertical-step fraction;
- unique-height fraction;
- each raw feature SD.

No p-value is computed for these post-outcome comparisons.

## Source-reference audit

From the already-opened reference table, report **metadata vocabularies only** for fields whose canonical names contain any of:

- sensor;
- tag;
- manufacturer;
- model;
- sampling;
- frequency;
- burst;
- duty;
- gps;
- deployment;
- study_site.

Do not use reference values to exclude data.

This may reveal a known tag/sampling regime change between 2022 and 2023.

## Interpretive rules

### Measurement architecture plausibly explanatory

This label is allowed only if at least one major frozen input differs sharply between 2022 and 2023, such as:
- order-of-magnitude sampling-interval difference;
- severe height quantization in one year;
- raw policy feature collapse/near-zero variance;
- documented tag/sampling regime change.

It does not rescue the carrier result.

### Measurement architecture broadly comparable

If timing, quantization and feature-variance diagnostics are broadly similar, the 2022→2023 reversal becomes more consistent with genuine temporal/context dependence, while remaining observational.

## 2016 diagnosis

The audit must identify exactly which raw policy feature(s) caused the frozen zero/non-finite SD stop and report their cohort values.

Do not replace or remove the degenerate feature.

## Claim ceiling

This is a post-outcome measurement audit.

It can distinguish:
- obvious measurement non-comparability;
- versus no obvious measurement explanation.

It cannot prove ecological causation and cannot reopen the policy-to-vertical-shape bridge.
