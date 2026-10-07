# Auditory-feedback call-class support audit v1

## Status

**STRUCTURAL SUPPORT ONLY. ACOUSTIC FEATURE MAGNITUDES FORBIDDEN.**

Parent:
- `PAF_SCHEMA_AUDIT_CONTRACT_V1.md`
- `PAF_SCHEMA_AUDIT_V2.md`

## Authorized opening

Using `PAF_Tbl`, report only:

- Acoustic Group levels;
- call counts per bat × Acoustic Group;
- number of rows per bat × Acoustic Group with all 28 frozen acoustic features finite;
- whether each acoustic group is represented by every one of the 10 bats.

Do not report:
- any feature mean;
- variance;
- centroid;
- distance;
- identity score;
- treatment comparison.

## Architecture rule

If at least one Acoustic Group has:
- all 10 bats represented;
- >=20 complete 28-feature calls per bat;

then the first numerically ordered such group is selected for a **class-conditioned individualization primary**.

If no group passes:
use the whole repertoire under a separately frozen **Acoustic Group × Sex × Treatment residualization** architecture.

No outcome magnitude may influence this choice.
