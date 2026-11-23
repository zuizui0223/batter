# Münster thermal 3D bat tracks + NRW public LiDAR: source-only co-location admission v1

**Date 2026-11-24 JST. Scientific status before reading real track xyz:** new independently found original field candidate; no original flight coordinates, heights, vegetation/clutter associations or phenotype outcomes viewed. This is **NOT** yet a colocated air-volume SDM source.

## Original published track dataset

Heim, Chávez, Courtiol, Paul & Voigt (2023), *The response behaviour of bats to motion-controlled LED lighting of bicycle trails*, Zenodo original v1 DOI [10.5281/zenodo.7797077](https://doi.org/10.5281/zenodo.7797077). Author methodological description: 5 lamp posts 210–300m apart along 1.5km test section of bicycle trail in **Münster, NRW Germany**, each bordering forest/open/residential/park settings; acoustic activity was measured at 5 posts. Stereo thermal imaging at selected lamp locations yielded **12 reconstructed 3D bat flight tracks**, 9 on 2022-10-18 and 3 on 2022-10-19, **all while LEDs off**. These dozen tracks are **not** 12 independent forest sites and do not give an out-of-forest test. The source must distinguish tracks from fixed-post acoustic activities, cannot infer a species solely from unspecified thermal track metadata.

Original version fixed file:
- `https://zenodo.org/records/7797077/files/3DTracks.zip?download=1`, original author MD5 **648c3effc18d43731f6ac267493046b9**, shown file size **61.5 kB**.
- `https://zenodo.org/records/7797077/files/README.md?download=1`, original MD5 **b91d8cb9113e470af3108c4b6c5eb0b6**, shown ~4.2 kB.
- Source public Zenodo only. No mirrored content substitution, no authentication circumvention. Confirm MD5, original ZIP file list and path safety; store ZIP SHA256 and member sizes/file extensions. **Do not commit source raw bat xyz**; do not use sampled raw spatial positions to choose a model after outcomes.
- README author *methods* content may be read to find coordinate system/unit/photogrammetric camera calibration, sites, source IDs and whether height is AGL/MSL/local, lamp post geographic position, original observation events, coordinate transform. No original flight x,y,z values, flight-height summary, source ecological effects or correlations opened in **v1**.

## Paired regional LiDAR candidate

Geobasis NRW official [3D-Messdaten NW (3DM)](https://www.opengeodata.nrw.de/produkte/geobasis/hm/3dm_l_las/) gives classified airborne LiDAR returns in LAZ covering the state, with ~4–10 returns/m² depending acquisition and a dated-tile WMS. The public data product may include Münster, **but no original bat-track sensor location, absolute transform, LAS tile ID, acquisition date, or common datum has yet been verified**. Airborne LiDAR return coordinates and thermally reconstructed local xyz cannot be treated as colocated without independent control points and a rigid transform. ALS return density cannot resolve the 10–25cm understory geometry or certified free-air visibility of the TLS Hermans precedent.

## Stage v1 source-only admission

1. Fetch both original Zenodo files, verify exact author MD5 and ZIP safe member count/extension/individual size (<10MB total uncompressed). Open only *headers*, member filenames, README textual design/coordinate documentation, matrix shape from binary containers if applicable. No x/y/z coordinate values, no per-flight altitude range, no bat-beam or clutter analysis, no independent-site predictive score.
2. Report number of internal flight files, grouping names/dates/site IDs present in filenames, column names only if flat CSV/TSV, extracted README lines specifically documenting the coordinate frame/unit and lamp reference. No guessing geographic positions from study city alone.
3. **Gate A** flight-XYZ source: at least one real original track structure has explicitly named x,y,z measured physical coordinates with documented units and a flight ID/time or index. If only plotted screenshot/binary data without readable schema, STOP and record exact blocker rather than fabricating numeric tracks.
4. **Gate B** LiDAR co-location: requires **actual lamp/sensor geometry or original absolute CRS coordinate**, enough to select a correct NRW 3DM tile and independent rigid transform; airborne point cloud must be acquired proximate to field dates (2022) with known height datum and point classes; check source license and tile metadata rather than assuming all NRW tiles align.
5. **Gate C** ecological predictive independence: ≥3 genuinely independent original forest plots/sites, q calibration/known observation footprint, nights and track group IDs for block validation, and per-site LiDAR within detector support. Twelve source tracks from one or a few lampposts DO NOT satisfy by count alone. At best a single-site **real XYZ geometry integration demonstration** if Gate A/B pass; not independent forest transfer.
6. No bat zoological claim, 3D clutter preference, height activity distribution or source wildlife predictive model until a **separate outcome-scoring contract** is committed, including equal source observation/effort and track autocorrelation handling.

## Real-goal transparency

A public 3D track ZIP is an actual improvement over restricted Hermans original CSV, but **a track without verified LiDAR alignment cannot validate a physical-air-volume clutter hypothesis**. This new source gate is an auxiliary to source-free PR #103, not an attempt to rescue previously opened negative 62-study transfer results. JAE `batter/main`, ODSP N2, esdm E5 remain frozen.
