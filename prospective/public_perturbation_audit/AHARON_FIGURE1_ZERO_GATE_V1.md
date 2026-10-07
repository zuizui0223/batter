# Aharon Figure-1 zero-sentinel gate v1

## Status

**STRUCTURAL NUMERIC-MASK AUDIT ONLY. NONZERO TURNING MAGNITUDES FORBIDDEN.**

Parent:
- `AHARON_FINITE_MASK_AUDIT_CONTRACT_V1.md`
- `AHARON_FIGURE1_STRUCTURE_V2.md`
- `AHARON_FIGURE1_FINITE_MASK_V2.md`

The general finite-mask contract prospectively authorized exact-zero counts before numeric turning medians are calculated.

## Authorized opening

For every one of the 12 Figure-1 bat × condition matrices report only:

- exact-zero cell count;
- finite cell count;
- finite-nonzero bilateral trial count.

Do not report any nonzero magnitude.

## Proceed rule

If all 12 matrices contain zero exact-zero cells:

> **PASS_NO_ZERO_SENTINEL**

and the frozen cross-condition turning-location primary may open.

If any exact zero occurs:

> **STOP_ZERO_ENCODING_NEEDS_FREEZE**

and no turning median may be calculated until source zero semantics are resolved prospectively.
