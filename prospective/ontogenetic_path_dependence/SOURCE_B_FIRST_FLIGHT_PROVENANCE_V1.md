# Source B first-flight chronology provenance v1

## Status

**SOURCE-PROVENANCE RECORD. No movement outcome opened.**

Source:
Harten, L., Katz, A., Goldshtein, A., Handel, M. & Yovel, Y. (2020).
*The ontogeny of a mammalian cognitive map in the real world*.
Science 369: 194–197.
DOI: `10.1126/science.aay3354`.

Public movement dataset:
Mendeley Data v1, `10.17632/n9d8gbz3xr.1`.

## Formation boundary

The peer-reviewed paper explicitly states that the study continuously tracked **22 Egyptian fruit bat pups from their very first flight outdoors and over the first months of their lives**.

This is the formation boundary used by the prospective Source B programme.

It is qualitatively different from the adult JAE archive, where deployment onset could not be interpreted as first learning or first environmental experience.

## Source-code chronology

The authorized public MATLAB code independently establishes the internal chronology used by the archived data.

`createRealDays.m` defines:
- `firstDay = datetime(data(1).timeStart)`;
- for each `data(i)`, elapsed real day is calculated relative to that first day.

The code therefore treats elements of the top-level `data` struct as chronological track-day objects and anchors the series to the first archived day.

The public code also accesses route geometry below each day's `data(day).track` object.

## Prospective interpretation

Before opening route outcomes, the Source B programme fixes:

- the study-level ontogenetic boundary from the peer-reviewed source: first outdoor flight;
- the archive chronology from source code: `data(1)` is the first archived track day and later `data(i)` objects are chronologically indexed track days;
- the biological unit: juvenile individual;
- the experience axis: strictly prior independent track days, not deployment duration inferred retrospectively from route shape.

## Claim boundary

This provenance supports testing **formation through independent experience**.

It does not itself establish:
- increasing self-predictability;
- route stereotypy;
- path dependence;
- reinforcement;
- a specific cognitive mechanism.

Those remain unopened prospective outcomes.

## References used for provenance

- Harten et al. 2020, Science, DOI `10.1126/science.aay3354`.
- Public Mendeley Data v1, DOI `10.17632/n9d8gbz3xr.1`.
- Source files `createRealDays.m` and `loadData.m` opened under `SOURCE_B_CODE_OPENING_AMENDMENT_V1.md`.

## JAE firewall

This record is outside JAE v0.4.0 and cannot alter the frozen JAE claim.
