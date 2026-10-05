# evsBat restricted ndarray metadata opening v3

## Status

**FROZEN AFTER STATIC PICKLE INVENTORY IDENTIFIED A NUMPY-ONLY OBJECT GRAPH.**

Previous static inspection of the exact frozen schema member found only these structural strings:

- `numpy.core.multiarray`
- `_reconstruct`
- `numpy`
- `ndarray`
- `dtype`
- `f8`
- `<`

No project-specific or arbitrary executable class string was present.

## Frozen member

`rawdata/chamber/event_camera/R_nippon/particle_tracking_results_kiku_2868_17-3_particle1_lower.pkl`

CRC32:
`34bb9458`

Uncompressed bytes:
461,730.

## Authorized restricted unpickling

Define a custom `pickle.Unpickler.find_class` that permits **only**:

- `numpy.core.multiarray._reconstruct`
- `numpy.ndarray`
- `numpy.dtype`

and rejects every other global.

No other callable/class may be resolved.

After restricted loading report only:

- Python top-level type;
- NumPy ndim;
- shape;
- dtype string;
- total element count;
- C/F-contiguous flags;
- whether dtype is numeric floating point.

Do not report:
- any array cell value;
- minima/maxima;
- means;
- first/last rows;
- coordinate ranges.

## Decision

If the top-level object is a 2-D float64 ndarray with a plausible trajectory-column count, freeze a column-semantics probe.

Column meanings must come from:
- source code/documentation; or
- a separately frozen minimal numeric/structural inference.

Do not assume column order from shape alone.
