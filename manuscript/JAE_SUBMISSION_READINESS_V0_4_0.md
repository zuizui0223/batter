# JAE submission readiness v0.4.0

## Status

**READY TO FREEZE AS `release/jae-v0.4.0-rc2`**

Scientific same-data mechanism search is closed. Packaging and visual QA have been rerun on the maintenance-synthesis candidate.

## Manuscript

Title:

**Persistent individual vertical strategies need not partition three-dimensional space in two tropical bat species**

Canonical manuscript path:
`manuscript/MANUSCRIPT_DRAFT_V0_4_0.md`

Internal version:
v0.4.0 candidate — post-freeze maintenance synthesis.

## Submission gate

Authoritative v0.4.0 submission workflow:
- run: **37123936286**
- conclusion: **success**
- CI manuscript count: **7,995 words**
- JAE working limit: **8,500**
- pre-title-page headroom: **505 words**
- Abstract: **282 words**
- Introduction: **682 words**
- Results: **1,348 words**
- Discussion: **1,205 words**
- main figures: **6**
- Supporting Figures: **3**

Main-figure artifact:
- id: **11273753416**
- SHA256: `c07e2cc7bce7341debc930f05ce8e193c77e649401b4535d92b9ec9e94cf0bbf`

Supporting-figure artifact:
- id: **11273793396**
- SHA256: `e2e8e97dcc5ad37b639e53bccd7a27dcf194ab2fed254d5abd7482f820289261`

## Anonymous review manuscript

Authoritative v0.4.0 review workflow:
- run: **37123738669**
- conclusion: **success**
- anonymity gate: **PASS**
- PDF pages: **27**
- artifact id: **11274153477**
- SHA256: `2197b76028adfbe1375c08bf3c613755b235f634cbe23532adab3aa948c6f380`

The 27-page PDF was rendered to PNG for QA. Representative first, maintenance-Discussion and final pages were inspected; no clipping, overlap or broken glyphs were observed.

## Figure 1 visual QA

The v0.4.0 conceptual Figure 1 was rebuilt after the maintenance reframing and inspected from the authoritative main-figure artifact. The final three-layer layout contains:
1. detection/control of apparent individuality;
2. independent persistence and partitioning diagnostics;
3. convergence on the bounded synthesis that personal solutions can persist without exclusive vertical niches.

No text/arrow overlap or clipping remains.

## Scientific claim ceiling

Supported:
- persistent centered vertical individuality in five comparative panels;
- terrain-relative vertical-strategy fidelity in 4/4 evaluable panels from *H. monstrosus* and *P. hastatus*;
- no supported positive terrain-relative added segregation in those four panels;
- synchronous co-use separation in 1/4, with the 2023 limitation retained;
- temporal self-history persistence to the maximum structurally evaluable lags;
- persistence after 500-m place x broad kinematic matching;
- broad same-night context insufficient as a general explanation in the evaluable subset.

Preferred interpretation:
> persistent personal movement solutions can remain predictive without requiring mutually exclusive vertical niches.

Not established:
- memory or learning as the cause;
- morphology/performance as the cause;
- exact resource/task identity as the cause;
- fine environmental reaction norms;
- adaptive or fitness benefit.

The continuous ERA5-wind reaction-norm family was stopped before numeric vertical opening when the predeclared all-three structural gate failed (2023: 7/8).

## External boundary evidence restored in rc2

rc2 restores the previously frozen external sequence that was present in the integrated manuscript:
- *N. noctula* first frozen primary: FAIL (+0.05175, p=0.1224);
- *H. armiger/pratti*: FAIL (-0.04468, p=0.8616);
- *M. vivesi*: FAIL (+0.00470, p=0.4419);
- *P. poliocephalus*: PASS in the separate n=4 programme (+0.16873, p=0.0001);
- *Pteropus* MSL-minus-DEM diagnostic: +0.03231, p=0.0023.

The integrated manuscript's external Figure 4 is restored as **Supporting Figure S3**, with its numerical table as Supporting Table S1. These sources are boundary tests rather than a prevalence sample.

The title and central partitioning claim are correspondingly narrowed to **two tropical bat species**, *H. monstrosus* and *P. hastatus*.

## Remaining submission work

Human metadata and archive/release steps remain separate:
- final author list and affiliations;
- corresponding-author metadata;
- funding / conflicts / acknowledgements;
- explicit software licence;
- versioned archive DOI;
- final combined manuscript + generated title-page count.

No such metadata is inferred here.

## Stop rule

No further same-data mechanism fishing is authorized for v0.4.0.


## Synthetic human-metadata pipeline self-test

Authoritative synthetic self-test:
- workflow run: **37093159799**
- conclusion: **success**
- synthetic identity/licence existed only inside the Actions workspace and was not committed;
- pre-release metadata assembly: READY;
- pre-release combined manuscript + generated title-page count: **8,216 / 8,500**;
- pre-release headroom: **284 words**;
- post-DOI metadata assembly: READY;
- post-DOI combined count: **8,211 / 8,500**;
- post-DOI headroom: **289 words**;
- Zenodo metadata consistency: PASS;
- final JAE upload gate: READY.

These synthetic values validate the pipeline only. Real author, licence and DOI metadata remain required and are not inferred.


## Active-reference and release-preflight integrity

v0.4.0 active-reference guard:
- workflow run **37094415632**;
- conclusion: **success**;
- README, CURRENT_STATUS, manifests, readiness, metadata guide and release notes all resolve to the v0.4.0 RC rather than the superseded v0.3.8 package.

GitHub/Zenodo release-preflight self-test:
- workflow run **37094468063**;
- conclusion: **success**;
- synthetic pre-release metadata assembly: PASS;
- Zenodo readiness logic: PASS;
- candidate-integrity logic against `release/jae-v0.4.0-rc2`: PASS;
- real target tag `jae-v0.4.0`: absent at test time;
- real GitHub release with that tag: absent at test time.

The real release-preflight remains intentionally blocked until explicit human metadata and exactly one chosen repository licence are committed.


## Canonical v0.4.0 path validation

Versioned-file cleanup was completed without changing scientific content:

- canonical manuscript: `manuscript/MANUSCRIPT_DRAFT_V0_4_0.md`;
- canonical title-page template: `manuscript/TITLE_PAGE_TEMPLATE_V0_4_0.md`;
- canonical cover letter: `manuscript/COVER_LETTER_JAE_V0_4_0.md`;
- canonical claim ledger: `manuscript/CLAIM_LEDGER_V4.md`.

The canonical v0.4.0 manuscript blob SHA is:
`2a4b2a3aafc8a4a8b4f495f4148e888f1a9c789c`,
identical to the previously validated maintenance-synthesis scientific manuscript.

The legacy `manuscript/MANUSCRIPT_DRAFT_V0_3_8.md` in the RC was restored to the exact main-branch v0.3.8 blob SHA:
`016b1981524fa8d0c82553ad009fb0b35cc792a0`.

Canonical-path submission validation:
- run **37099994789** — success;
- CI manuscript count **8,039 / 8,500**;
- main-figure artifact **11266175026**, SHA256 `ae4015dbcb1f3b6d178422da7b2976ab353d6ed910edb9c93a65937adab34a3f`;
- supporting-figure artifact **11265438953**, SHA256 `2291a7d42af1fd0d977e8a00be355c0b4b3d0b5b796fcb75ae7ddb1f7f0e71eb`.

Canonical-path anonymous review validation:
- run **37099999137** — success;
- anonymity guard PASS;
- PDF **27 pages**;
- artifact **11265204413**, SHA256 `cad3f17c3e79b2f05e894863691fa68138a67b40653e85a0101cc95197cb4091`;
- first page, maintenance Discussion pages 18–19, and final page 27 visually inspected; no clipping, overlap or broken glyphs.

Canonical Figure 1 was re-inspected from the new artifact and retains the final three-layer detection -> persistence/partitioning diagnostics -> ecological synthesis layout without text/arrow collisions.


## rc2 external-boundary revalidation

The two reviewer-facing scope corrections are complete:

1. Previously frozen external validation has been restored to the main Results/Discussion and Supporting Information.
2. The `need not partition` claim and title are explicitly scoped to the four terrain/co-use panels from **two species**, *Hypsignathus monstrosus* and *Phyllostomus hastatus*.

External boundary sequence:
- first frozen *Nyctalus noctula* primary: FAIL (+0.05175, p=0.1224; n=27);
- *Hipposideros armiger/pratti*: FAIL (-0.04468, p=0.8616; n=13);
- *Myotis vivesi*: FAIL (+0.00470, p=0.4419; n=4);
- *Pteropus poliocephalus*: PASS (+0.16873, p=0.0001; n=4);
- *Pteropus* MSL-minus-DEM diagnostic: +0.03231, p=0.0023.

Supporting Table S1 and Supporting Figure S3 retain these results. S3 was visually inspected after rebuild; no clipping or overlap remains.

Final rc2 validation:
- submission run **37123936286** — PASS;
- manuscript CI count **7,995 / 8,500**;
- anonymous review run **37123738669** — PASS, 27 pages;
- synthetic metadata run **37123738694** — PASS;
- combined pre-release count **8,175 / 8,500** (325-word headroom);
- combined post-DOI count **8,170 / 8,500** (330-word headroom).
