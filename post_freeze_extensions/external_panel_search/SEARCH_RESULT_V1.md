# Prospective external bat-panel search result v1

## Status

**OUTCOME-BLIND SEARCH COMPLETE. One independent external source passes the frozen structural gate. Numeric vertical magnitudes were not used for admission.**

Authoritative structural screen:
- workflow run: `36625875776`
- head: `96a1753c0f7251dcec2101af82051051b3c6e3fe`
- artifact: `11060441382`
- digest: `sha256:013272ffa19574500e4b0ab998171b5718df30c6ae4bd4b800d36033f9f817c3`

## Admitted external source

### Common noctule — *Nyctalus noctula*

- repository: Zenodo
- DOI: `10.5281/zenodo.7535030`
- source study: *Wind energy production in forests conflicts with tree-roosting bats*
- raw event file: `Observed_GPS_locations.csv`
- file SHA256: `2f373d47706c5b56313de70b623bb5446f5925c69af30f1b145993419e382aa9`
- rows with id + x + y + native vertical present: **8,129**
- individuals: **60**
- explicit flight tracks: **107**
- tracks with >=50 presence-qualified fixes: **76**
- individuals with >=1 eligible track: **46**
- individuals with >=2 eligible >=50-fix tracks: **30**
- native vertical field: `Height` (GPS-estimated height above the geoid / mean sea level)
- timestamp field: `utc`
- individual field: `bat_id`
- track/session field: `trackid`
- x-y fields available both as WGS84 longitude/latitude and UTM coordinates
- admission verdict: **PASS**

The source is genuinely external to the previously closed Movebank search universe and is not one of the six datasets used by v0.3.8.

## Other screened public sources

- Figshare `10.6084/m9.figshare.28845701.v1`: native altitude exists, but the public 3-D table has no timestamp/track structure sufficient for the frozen repeat-session gate — FAIL.
- Figshare `10.6084/m9.figshare.21717086.v3`: no native event-level vertical field in the GPS table — FAIL.
- Dryad *Hipposideros armiger* + *H. pratti* `10.5061/dryad.j0zpc86r1`: highly promising structurally (17 adults; repeated 7–10-night site fidelity; native AGL `height`), but exact >=50-fix/night counts remain unavailable without authenticated Dryad file download — PENDING, not admitted.
- Dryad *Leptonycteris nivalis* Texas 2024 `10.5061/dryad.stqjq2cfg`: 21 bats with native altitude; exact repeated-night >=50-fix structure remains unverified — PENDING, not admitted.
- sparse vampire-bat and other candidates fail or remain below priority under the frozen gate.

## Decision

The external-search requirement is satisfied by the Zenodo noctule source. No further candidate discovery is needed before independent validation.

The next step is a new prospective validation contract frozen **before opening numeric `Height` values**.
