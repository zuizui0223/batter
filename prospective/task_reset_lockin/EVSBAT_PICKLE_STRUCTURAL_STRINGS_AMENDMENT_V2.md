# evsBat pickle structural-string inventory amendment v2

## Status

**FROZEN AFTER V1 STATIC PROBE RETURNED NO WHITELISTED COLUMN-KEY STRINGS.**

No pickle has been executed and no numerical trajectory value has been interpreted.

Parent:
`EVSBAT_PICKLE_SCHEMA_PROBE_AMENDMENT_V1.md`

## Motivation

The V1 pickletools probe showed protocol 4 with:
- STACK_GLOBAL;
- BINBYTES;
- BUILD;
- REDUCE;

but no whitelisted time/x/y/z-style strings.

This is consistent with a direct NumPy/pandas object serialization where array values are stored as opaque byte payloads and structure is encoded through module/class strings rather than column labels.

## Authorized operation

Use the exact same frozen pickle member:

`rawdata/chamber/event_camera/R_nippon/particle_tracking_results_kiku_2868_17-3_particle1_lower.pkl`

and the same exact range extraction / CRC validation.

Run `pickletools.genops` only.

Report:

1. every unique **string opcode argument** satisfying:
   - length <= 120 UTF-8 characters;
   - printable;
2. occurrence counts for those strings;
3. the ordered first 200 string-opcode events with opcode name and string value;
4. no numerical opcode arguments;
5. no BINBYTES payload content.

## Forbidden

Do not:
- call any unpickler;
- execute STACK_GLOBAL/REDUCE;
- decode BINBYTES as arrays;
- report numeric trajectory values.

## Decision

If the string inventory identifies a narrow, standard safe object family such as NumPy ndarray/dtype reconstruction, a new restricted safe-load contract may whitelist only those constructors.

If arbitrary/project-specific executable classes are referenced, STOP external numeric opening.
