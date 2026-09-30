# Small-panel prospectivity audit v1

## Purpose

Verify that the separately frozen four-individual programme was specified and its nonvertical source structure was committed before either admitted source's numeric vertical outcome was opened.

This audit does not alter any estimator or result.

## Chronology

### 1. New small-panel contract frozen

Commit:
`6851353aeff4e01b135598712a216461d0d9f9f5`

Time:
**2026-09-30 15:02:05 UTC**

Message:
`Freeze four-individual small-panel generality programme`

At this point the following were already known from nonvertical structural screening:
- *Myotis vivesi* had exactly four repeat individuals under the unchanged >=50-event / >4-h-gap session rule;
- *Pteropus poliocephalus* had exactly four repeat individuals under that same rule;
- both had native vertical-field presence;
- both remained structural STOP under the earlier >=5-individual programme.

No numeric vertical value had been parsed for either admitted source.

The new contract admitted **all and only** sources satisfying that structural state.

### 2. Nonvertical preflight and horizontal axis pinned

Commit:
`f83f11176b58dd743fe4f44a23ae99e17133e5ed`

Time:
**2026-09-30 15:05:19 UTC**

Message:
`Record small-panel outcome-blind preflight receipt`

The committed receipt fixed, before vertical opening:
- raw source SHA;
- repeat-individual IDs;
- frozen >=50-event session universe;
- 5-km projection/grid;
- exact cell universe;
- prospective horizontal-individuality result;
- exact vertically evaluable target sessions;
- exact common-support event counts.

Horizontal results fixed at this stage:

- *Myotis vivesi*: calibrated horizontal excess **-0.12378**, p=**0.5846**;
- *Pteropus poliocephalus*: calibrated horizontal excess **+3.48659**, p=**0.0001**.

Receipt decision:
**SOURCES_PASS_TO_VERTICAL**.

### 3. Receipt-gated primary implementation / workflow trigger

Commit:
`e789cf68a896e55aff6db37b1861592c3f321a89`

Time:
**2026-09-30 15:08:44 UTC**

Message:
`Run small-panel prospective vertical primary`

This occurs after the committed nonvertical receipt.

The primary script was receipt-gated and used the source-specific raw SHA, frozen session universe, frozen target sessions and frozen estimator settings.

### 4. Vertical primary results pinned

Commit:
`d9f5a6fa5960ba314a0f8aa29c2de10be1a5fe64`

Time:
**2026-09-30 15:15:19 UTC**

Message:
`Record small-panel prospective vertical primary`

Frozen results:

- *Myotis vivesi*: calibrated centered vertical excess **+0.00470**, p=**0.4419** -> **FAIL**;
- *Pteropus poliocephalus*: calibrated centered vertical excess **+0.16873**, p=**0.0001** -> **PASS**.

## Inferential classification

The small-panel programme is:

> **prospective with respect to the two admitted sources' numeric vertical outcomes.**

Important qualification:

> The programme itself was created after the earlier >=5-individual structural search showed that exactly two unopened native-height sources had four repeat individuals.

That is an outcome-blind design adaptation based on sample structure, not a continuation of the earlier >=5 programme.

Therefore:
- the earlier >=5 structural STOPs remain true;
- the small-panel results belong to a new frozen design;
- the *Pteropus poliocephalus* result is valid evidence of an independent prospective replication under that design;
- it must not be described as having passed the earlier >=5-individual programme.

## No-rescue boundary

After the vertical outcomes were opened, no change is authorized to:
- source admission;
- four-individual requirement;
- >=50-event session rule;
- >4-h session split;
- 5-km grid;
- common-support event minimum;
- vertical bins;
- individuals included;
- source-specific vertical endpoint.

The small-panel programme is closed.
