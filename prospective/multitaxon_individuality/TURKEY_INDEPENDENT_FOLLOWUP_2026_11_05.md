# Follow-up: acquisition and overlap audit of independent turkey candidates

5 November 2026. This follow-up adds executed source-overlap checks, not a new
February-April ecological effect. The existing eligibility contract is unchanged.

## Original releases: acquisition still unresolved

| Original release | Official version / file | February and April coverage | Record overlap with discovery |
|---|---|---|---|
| Maine Dryad 10.5061/dryad.s4mw6m9gg | 320798 / 3528443 | Unverified: original bytes not obtained | Unverified for these exact bytes |
| Savannah River males, 2020 | 289285 / 3078872 | Unverified: original bytes not obtained | Unresolved |
| Savannah River males, 2021 | 289285 / 3078873 | Unverified: original bytes not obtained | Unresolved |

The ordinary public file links returned HTTP403; the advertised API download
links returned HTTP401. A fresh ordinary browser attempt for Maine timed out;
its public preview rendered only an excerpt, and a full-dataset download did
not complete. Partial preview rows do not establish full calendar coverage.
The [linked Zenodo software deposit](https://doi.org/10.5281/zenodo.13854408)
lists 14 R files and no GPS CSV, so it cannot supply this original GPS file.
These are environment-specific acquisition failures, not proof that the data
are unavailable by every legitimate route. See the [acquisition receipt](TURKEY_INDEPENDENT_ACQUISITION_FOLLOWUP_2026_11_05.json).

Pinned metadata from the [Maine API](https://datadryad.org/api/v2/versions/320798/files)
and [male API](https://datadryad.org/api/v2/versions/289285/files):

| File | Bytes | SHA256 |
|---|---:|---|
| GPS_Seasonal_-_Used.csv | 162705 | `95b75720531e90904a79e209d1717d5f5a3335625709c63e0e4fa1a29694bc6f` |
| Locations2020.csv | 1422491 | `fe3b2d4935c6414f16c8926b0391e8dd54f2f9a14e64eec5a7fe3b56272749c5` |
| Locations2021.csv | 1853245 | `225d9c2de3239a27857e2d6a498ffc5941421e80d51836ab2de0872dfddef4b7` |

## Executed overlap audit: Maine author version only

We compared all 3,205 records / 24 labels from the pinned
[author release](https://github.com/mattgonnerman/MaineTurkeyConnectivity/blob/e639fb66bf27b16d83c72d03faa638a496246ff4/GPS%20Seasonal%20-%20Used.csv)
against **all 796,419 records / 339 animals** in the original discovery GPS CSV,
not only the accepted 435,214 fixes or the focal six-animal group. Every row had
a usable ID, timestamp and coordinate pair for this audit. Both input SHA256
checks passed; no raw rows or identifiers are published.

- Exact normalized-UTC timestamp plus numeric-coordinate matches: **0**.
- Matches with coordinates rounded to five decimal places: **0**.
- Literal ID-label intersection: **0**, but namespaces differ and this alone
  cannot establish independent animals.
- The latitude-envelope gap gives a conservative lower bound of **1,246.766 km**
  between any recorded position in the two releases; this is not a nearest-pair
  distance estimate or an ecological effect.

Together with the [documented Maine study provenance](https://datadryad.org/dataset/doi:10.5061/dryad.s4mw6m9gg),
this supports **VERIFIED_DISTINCT_SOURCE for the pinned Maine author release**
as a distinct study/site sample. It does not certify the unretrieved Dryad bytes,
provide an animal identity crosswalk, or imply that different Maine papers are
independent populations. No match test alone can rule out recoded animals across
separate deployments.

The unchanged timestamp gate still excludes this author release:

| Year | February rows | April rows | April animals | April animals with >=7 dates | Paired February-April animals with >=7 dates each |
|---|---:|---:|---:|---:|---:|
| 2018 | 0 | 891 | 7 | 4 | 0 |
| 2019 | 0 | 511 | 6 | 3 | 0 |
| 2020 | 0 | 737 | 9 | 4 | 0 |

These counts apply only to the author release whose SHA differs from Dryad.
No valid February-April cohort is available from it, despite geographic independence.

## Male data: independence cannot yet be adjudicated

The [original paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC11046083/) describes
Savannah River Site adult males captured January-March2020 and December-March2021.
March-August is a remote data-retrieval period, **not proof of absent February
GPS fixes**. Shared authors, southeastern region and a potentially shared year
raise an overlap question but do not establish duplication. The full discovery
archive has 339 animals; being male distinguishes these candidates from the
female focal cohort, not necessarily from that full archive. A distinct year
alone also does not exclude recapture or repeated tracking.

The accessible paper/README and targeted DOI/title/filename search did not yield
an identifiable alternative public raw-data mirror or an animal/deployment
crosswalk. Status is **UNRESOLVED**, not confirmed overlap or confirmed independence.

## What is required to run the locked test

Obtain the three checksum-matched original files through a functioning public
download or an authorized copy. Then screen original measured fixes for both
months, at least four animals and seven common dates per month. For males,
compare IDs in their actual namespaces, source/deployment metadata, and
UTC timestamp-position records against the full discovery source. Record the
site/cohort and hashes before evaluating the endpoint. If both gates pass, run
the fixed 24 seven-day draws and every one-animal deletion for April-minus-February
mean pair-centroid distance. No substituted month or modeled location is used.

**No independent effect estimate or ecological null was produced.** The pending
step is original-file acquisition; the failed author-version time gate cannot
be repaired by changing the endpoint.

## Reproduction and verification

`audit_maine_source_overlap_v1.py` requires `--discovery`, `--candidate` and
`--output` paths, verifies both pinned hashes and exports only aggregate results.
See [executed receipt](TURKEY_MAINE_AUTHOR_OVERLAP_2026_11_05.json).
Three synthetic tests cover recoded IDs with timezone normalization, coordinate
rounding distinct from exact matching, and the spatial lower bound. The existing
calendar gate and core-effect tests remain in CI. Only synthetic/aggregate
checks run in CI; it does not download protected or precise GPS tracks.
