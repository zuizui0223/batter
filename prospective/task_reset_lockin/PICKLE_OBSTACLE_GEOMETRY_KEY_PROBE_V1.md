# Pickle obstacle-geometry key probe amendment v1

## Status

**STRUCTURE-ONLY PROBE. PICKLE EXECUTION AND NUMERIC PAYLOAD DECODING FORBIDDEN.**

Parent:
- `PICKLE_STRING_METADATA_AMENDMENT_V1.md`
- `METADATA_PREFLIGHT_CONTRACT_V1.md`

Public files:
- `kiku.pkl`
- `yubi.pkl`

## Purpose

The public Figshare article contains no standalone obstacle/layout geometry file.

Before abandoning a geometry-defined solution-abundance analysis, determine whether the pickle files expose structural keys indicating that obstacle geometry is embedded in their object graph.

## Authorized operation

Read at most the first **16 MiB** of each pickle by HTTP Range.

Do not:
- call `pickle.load`;
- call `numpy.load`;
- execute any pickle opcode;
- decode floating-point arrays;
- print arbitrary binary payload.

Search only for ASCII/UTF-8 structural tokens matching these case-insensitive terms:

- obstacle
- obstacles
- wall
- walls
- arena
- environment
- env
- layout
- geometry
- position
- positions
- coordinate
- coordinates
- center
- centres / centers
- radius
- diameter
- width
- height
- x
- y
- z
- start
- goal
- target

Also report source-native `Env[0-9]+` tokens.

## Proceed rule

A geometry-only abundance programme may continue only if:
- the pickle exposes unambiguous obstacle/layout structural keys;
- a later structural schema can separate obstacle geometry from trajectory numeric arrays before values are opened.

If not, record:

`STOP_NO_PUBLIC_OBSTACLE_GEOMETRY_SCHEMA`

and do not infer solution abundance from realized trajectories.

## Claim boundary

File size, trajectory dispersion, number of recorded flights, or model prediction error must never be used as a proxy for geometric solution abundance.
