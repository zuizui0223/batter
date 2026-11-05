# Non-Dryad public sources and Movebank follow-up

5 November 2026. The frozen endpoint and eligibility rules are unchanged.
No newly eligible independent February-April original-GPS cohort has yet been
obtained. Acquisition, schema exclusion, metadata bounds and ecological results
are kept separate below. [Machine-readable receipt](TURKEY_INDEPENDENT_ALTERNATIVES_RECEIPT_2026_11_05.json).

## Author GitHub: two files acquired, original-fix schema absent

The [Gulotta author repository](https://github.com/nickgulotta77/Harvest_Selection_Behavioral_Types_WildTurkeys/tree/de9399319493e872893403e550285a5fd95332a0)
is explicitly linked by its corresponding data record. At this pinned commit,
`Data/Male_gps_Webb.csv` has **6,271 rows** and `Data/Male_gps_GA_sites.csv` has
**8,731 rows**. Both were downloaded and independently rechecked for byte hash,
column names and row counts. Hashes and source URLs are in the receipt.

Despite GPS in their names, these are modeling-ready daily movement metrics:
daily date, individual labels, habitat covariates, distances/speeds and home-range
areas. They lack original measured fix coordinates and fix times. They therefore
cannot reconstruct daily-equal monthly utilization centroids or pair-centroid
separation. **STOP_NO_ORIGINAL_FIX_COORDINATES_OR_TIMES** applies before inspecting
hypothesis outcomes. Dates in a summary table cannot certify original observation
day support. Full track overlap also cannot be checked from these summaries;
independence of these southeastern cohorts remains unresolved.

## Movebank Data Repository: avoid reusing the discovery archive as replication

The official [repository search](https://datarepository.movebank.org/server/api/discover/search/objects?query=turkey&size=50)
returned nine entries on one page. The [Wild Turkey taxon item](https://datarepository.movebank.org/handle/10255/move.3627)
is a taxonomic index, not a new tracking dataset: its linked data package is
[the existing southeastern discovery source](https://datarepository.movebank.org/handle/10255/move.3495).
Other search entries include turkey vultures and a study in the country Turkey;
these are not wild-turkey replication sources. This repository check does not
exhaust the live Movebank database or prove no additional study exists.

## Live Movebank: Forest Park Living Lab

The [research team's own account](https://www.forestparklivinglab.org/news/regina-the-turkey)
confirms a female wild turkey was GPS tagged in Forest Park, St. Louis, Missouri,
and directs readers to Movebank. The [live study](https://www.movebank.org/cms/webapp?gwt_fragment=page=studies,path=study1605024900)
was opened successfully in the ordinary public interface. Its study ID is
**1605024900**, PI Stephen Blake, license **CC0**. The interface reports 45 animals
across multiple species; this is **not** a count of 45 turkeys.

One turkey individual was directly inspected and confirmed as female
*Meleagris gallopavo*. Its metadata report **2,608 valid GPS records**, spanning
February-September2024. The first record falls late enough in February that
at most **five February calendar dates** can be represented. Thus this inspected
individual cannot meet the frozen seven-day February requirement even before
missing-day checks. The whole study's turkey count and April daily support are
not established; the metadata date envelope is not evidence of April observations.
No individual identifiers, precise dates or positions are reproduced here.

The documented direct-read API returned HTTP401. The public JSON endpoint
returned HTTP200 with an empty response, which is an acquisition failure rather
than a zero-observation result. In the public browser UI, the normal download
control reached the study's license agreement dialog. Acceptance/download is not
yet complete, so no raw GPS, record-overlap audit or ecological effect is claimed.
The geographic/project provenance is promising for a distinct source, but no
full-record independence certification is assigned without the input records.

## Additional public repository lead: Harvard Dataverse

The [Stoakley et al. autumn/winter paper](https://onlinelibrary.wiley.com/doi/full/10.1002/ece3.71403)
links [DOI10.7910/DVN/SXWCHY](https://doi.org/10.7910/DVN/SXWCHY).
Its stated autumn/winter observations cover October2022-January2023.
A [companion breeding-season paper](https://link.springer.com/article/10.1186/s40462-025-00578-x)
describes March-June2022 analysis and earlier capture, but capture dates do not
establish released February fixes. The normal anonymous Dataverse API returned403;
web retrieval did not expose a file list. No original file was acquired and
coverage, overlap and suitability remain unresolved. This is a specific lead,
not a successful original-GPS acquisition or a permanent unavailability finding.

## Previously screened Maine exports

The acquired MaineTurkeyConnectivity author CSV still has no February records.
The archived WinterSelection workflow selects winter through mid-March and uses
modeled positions; SeasonalHMM outputs are derived tracks. Neither has been
established as an unrestricted measured February-April export. Derived/modelled
locations are not substituted for original fixes. The Movebank study name
`Eastern Wild Turkey, Gonnerman, Maine` remains a lead without a verified public
original-fix export in this investigation.

## Decision and reproducibility

The two newly acquired CSVs fail the required original-fix schema; the inspected
Forest Park individual fails the seven-day February bound; other original files
are still unresolved. Consequently **no independent replication effect, null,
p-value or confidence interval has been produced**. The prior within-source core
result is unchanged. No group, month or threshold was selected after observing
a new spatial effect.

Receipt validation re-read both downloaded author files and independently checked
SHA256, row count and complete headers. No author-supplied code was executed.
Only aggregated metadata, schema and acquisition status are committed. The next
eligible analysis still requires measured positions and timestamps, at least four
independent animals with seven common dates in both February and April, and
source/record-overlap clearance before the fixed24 draws and animal deletions.
