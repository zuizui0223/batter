# Comparative generality programme v1 — structural-scarcity closeout

## Status

**CLOSED — STRUCTURAL SCARCITY.**

The search universe and thresholds were frozen before any new-source numeric vertical outcome was opened.

Final count:

- genuinely new comparative vertical outcomes opened: **0**
- new sources reaching the full frozen vertical gate: **0**
- threshold rescues: **0**
- new search terms after the frozen search snapshot: **0**

Historical Nyctalus and Hipposideros outcomes are not counted here.

## What was screened

The closed search covered Dryad, Zenodo, Figshare and Movebank Data Repository/public Movebank-derived records under the frozen query families.

### 1. Leptonycteris nivalis

Dryad DOI `10.5061/dryad.stqjq2cfg`

- source vertical field documented: `Altitude (m)`;
- 2,402 nonvertical-valid rows;
- 21 Tag IDs;
- >=50-fix sessions under frozen rule: **0**;
- repeat-eligible IDs: **0**;
- horizontal individuality: not evaluable;
- numeric altitude opened: **false**.

**STRUCTURAL STOP.**

### 2. Desmodus rotundus

Dryad DOI `10.5061/dryad.7wm37pw53`

- native raw GPS `ALTITUDE` documented;
- 1,678 presence-qualified rows;
- >=50-fix sessions: **4** total;
- only one local contained one repeat ID;
- no local met the frozen minimum panel structure;
- numeric altitude opened: **false**.

**STRUCTURAL STOP.**

### 3. Hypsignathus monstrosus 2022–2023 Dryad source

Dryad DOI `10.5061/dryad.7m0cfxq4t`

Source README documents the deposited event table as x/y/time/trackId without a raw vertical response.

**REJECT — NO VERTICAL RESPONSE.**

### 4. Airflows multispecies compilation

Zenodo DOI `10.5281/zenodo.21915776`

Nonvertical metadata audit:
- 38 biologging species in full compilation;
- GBIF-classified bat subset: *Eidolon helvum* and *Pteropus lylei*;
- 8 bat study×species panels;
- 5 panels passed the segment-level necessary screen.

Sealed point-level preflight:
- Eidolon studyIDs 14253246, 183770262, 259100173;
- Pteropus studyIDs 6609898, 8239320;
- >=50-fix nights: **0 in every panel**;
- passing panels: **0**;
- point-level vertical values accessed by analysis logic: **false**.

The three Eidolon panels belong to the historical `10.5441/001/1.k8n02jn8` data universe and are not new prospective sources.

The two Pteropus Thailand panels are genuinely new study panels but the Airflows compilation is too thinned/segment-oriented for the frozen repeated-night estimator.

**STRUCTURAL STOP.**

The separately frozen Airflows vertical design remains unused.

### 5. Pteropus lylei — Cambodia

Movebank Data Repository DOI `10.5441/001/1.j25661td`

- DOI resolved successfully;
- two event-like headers identified;
- individual/time/x-y fields present;
- accepted native vertical field: **none**;
- numeric event rows opened: **false**.

**REJECT — NO VERTICAL RESPONSE.**

### 6. Pteropus poliocephalus

Movebank Data Repository DOI `10.5441/001/1.5bd6pq55`

Header audit:
- event table found;
- native vertical field: `height-above-msl`.

Outcome-blind structural preflight:
- rows in event file: **148,084**;
- presence-qualified rows: **145,262**;
- individuals with presence: **4**;
- >=50-event sessions: **158**;
- repeat IDs: **403, 588, 657, 684**;
- repeat-individual count: **4**;
- frozen required repeat individuals: **5**;
- numeric height opened: **false**.

This source is data-rich within four individuals but fails the predeclared cross-individual replication gate by one individual.

**STRUCTURAL STOP.**

### 7. Myotis vivesi

Movebank Data Repository DOI `10.5441/001/1.kk3bg2f4`

Provenance correction:
- the frozen raw-screen candidate list incorrectly labelled this source *Noctilio leporinus*;
- source paper/repository taxon is **Myotis vivesi**;
- numerical screen result is unchanged.

Outcome-blind raw screen:
- native vertical field: `height_above_ellipsoid`;
- presence-qualified rows: **14,328**;
- individuals with presence: **11**;
- >=50-event sessions: **15**;
- repeat IDs: **Viv12, Viv14, Viv6, Viv8**;
- repeat-individual count: **4**;
- frozen required repeat individuals: **5**;
- numeric height opened: **false**.

**STRUCTURAL STOP.**

### 8. Other raw Movebank candidates

No accepted native vertical field in event headers:

- *Lavia frons*
- *Noctilio albiventris*
- *Vespertilio murinus*
- *Rhinolophus ferrumequinum*
- *Trachops cirrhosus*
- *Myotis daubentonii*
- *Carollia* spp.

**REJECT — NO NATIVE VERTICAL RESPONSE.**

Other frozen-query results consisting of acoustic/radar monitoring, UAV/video, publication-only or summary-only data were rejected as the wrong data type.

---

## Primary programme result

> **Within the frozen public-repository search universe, no genuinely new bat tracking source met the predeclared data structure required for a prospective centered vertical-individuality test.**

This is not evidence that the screened taxa lack vertical individuality.

It is a **structural-scarcity result**.

The limiting requirements were not total row count alone. The decisive requirements were:

1. a native event-level vertical coordinate;
2. repeated dense sessions within individual;
3. enough repeat individuals for an identity-exchangeability null;
4. enough shared horizontal support for same-versus-other prediction.

Many public datasets satisfy one or two of these requirements but not all four.

## Particularly informative near-misses

Two independent Movebank sources had native vertical coordinates and dense tracking but only **four** repeat individuals under the frozen rule:

- *Myotis vivesi*: 4 repeat individuals;
- *Pteropus poliocephalus*: 4 repeat individuals.

The frozen minimum was five, so neither vertical outcome was opened.

This demonstrates why lowering the threshold after screening would be outcome-independent in one sense but still violate the predeclared comparative design. The current programme therefore stops rather than moving the goalposts.

## Data-design implication

Future studies intended to test individual 3-D spatial organization should deliberately collect:

- >=5 individuals at minimum, preferably substantially more;
- >=2 dense tracking nights per individual;
- >=50 usable fixes per repeated night under the current estimator;
- simultaneous tracking that creates cross-individual horizontal overlap;
- explicit native vertical reference and metadata;
- raw event-level release rather than only thinned movement segments.

For mechanism identification, the stronger target remains:

`exact route/resource × independently observed behaviour × local environment × time window`

with repeated individuals and detailed flight morphology.

## Relation to v10

v10 already establishes that:
- centered vertical individuality is not prospectively universal;
- horizontal fidelity and centered vertical individuality can dissociate;
- context-residual individuality is a property of positive systems, not a universal rule.

The present programme adds a separate methodological/ecological boundary:

> **The public data landscape itself is poorly populated with independent 3-D bat datasets that can test repeatable within-individual vertical organization without relaxing the estimator.**

That statement is restricted to the frozen search universe and design.

## Stop rule

The programme is closed.

Do not:
- lower the >=50-event session threshold;
- lower the >=5-repeat-individual threshold;
- redefine sessions;
- add new search terms;
- open vertical values from structurally stopped sources;
- treat structural STOP as biological FAIL.

A future lower-density analysis requires a **new programme with a newly justified estimator**, not a revision of this one.
