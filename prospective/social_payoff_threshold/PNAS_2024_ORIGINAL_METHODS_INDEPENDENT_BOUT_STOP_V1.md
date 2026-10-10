# Original PNAS 2024 methods decisively stop the repeated-individual threshold primary

**2026-10-08. Source-backed, categorical interpretation of already-published METHODS / Table 1; NOT a new raw-data result.** Supersedes the earlier metadata-only HOLD status for the particular confirmatory independent-bout-replication gate, regardless of whether publisher/Mendeley files can be downloaded.

## Original article

Krivoruchko et al. (2024), *PNAS* 121(30):e2321724121, DOI https://doi.org/10.1073/pnas.2321724121. Public full-text: https://pmc.ncbi.nlm.nih.gov/articles/PMC11287165/ .

The original **Results** explicitly states:

> "Because we could not record audio continuously from sunset to dawn, we recorded either the evening or morning activity bout of the bat."

The **Methods** describes 90 minutes of continuous recording in a predefined evening or morning schedule, and 10 recovered bats. Original Table 1 has 10 numbered bats, **one flight start and end interval per listed bat**, not an independently observed bat×multiple-night schedule. Five-second time bins are nested within each recording. The independent source [Mendeley DOI 10.17632/h7krh54zxc.1](https://doi.org/10.17632/h7krh54zxc.1) describes exactly those 10 bats' attacks, successful attacks and detected conspecific calls per 5-sec window, not a separate longitudinal recapture cohort.

This provides **strong documentary evidence of no recorded independent evening-plus-morning replication per physical bat in this study**, much stronger than an API failure. Multiple attacks, 5-s windows and within-recording commutes cannot be upgraded to independent *days*.

## Fixed hypothesis and source gate

The preregistered candidate question required each bat's own individual social-exposure response slope or crossover to be estimated from *earlier independent bouts/nights* and validated on physically independent held-out bouts, under fixed exposure regimes, to rule out a single-day behavioral state. With only one source-documented recording/flight interval per bat, the study cannot support that validation as stated.

**Final primary decision:** `STOP_NO_INDEPENDENT_BAT_BOUT_REPLICATION`.

This is a categorical/source-design stop, not `NO_BIOLOGICAL_PERSONAL_THRESHOLDS`. It does NOT negate the paper's real published capture-success trade-off; the group-level functional hump is original author prior art.

The earlier [GitHub Actions run 37793760213](https://github.com/zuizui0223/batter/actions/runs/37793760213) succeeded mechanically but both Mendeley public API endpoints returned **HTTP 401**. Source access status remains `STOP_API_OR_SOURCE_INACCESSIBLE` for that *one API method*; now there is a **separate, independent stronger biological STOP** from the paper design itself.

## Alternate supplement is not a source-data rescue

The PNAS paper's [PMC supplementary list](https://pmc.ncbi.nlm.nih.gov/articles/PMC11287165/) advertises an ~160KB `pnas.2321724121.sd01.xlsx`, for which a **separate source-header-only audit** was frozen in `PNAS_2024_SUPPLEMENT_HEADER_ONLY_GATE_CONTRACT_V1.md` and executed only if a real original download URL responds. Even if this workbook is accessible and contains physical bat ID and 5-sec rows, it **cannot create independent repeat days** absent contradictory source documentation verified before any endpoint opening.

A metadata/header check may continue for reproducibility and schema transparency, but **no secondary analysis of already published attack/success effects should be promoted as confirming durable bat-specific personal benefit thresholds**. In particular, do not choose favorable subsets or arbitrarily split one bout into pretend independent life-history periods.

## What still can be legitimately inferred from published work

- The author-reported *population-level* nonmonotonic relationship between acoustic social exposure (conspecific call count) and capture success is measured for 10 bats. It is not randomized conspecific density: environmental prey density, acoustics, same-roost overlap and patch opportunity could jointly drive it.
- Bat-ID differences in raw realized attack rates or successes, if ever documented, would describe **within-recording variation**, not an individual social-response reaction norm retained across nights.
- Data are *functional* (chewing-associated capture identification), but **no synchronized fine-scale 3D body flight trajectories** or bat×route-response controlled interventions are available from this paper.
- The next credible distinct empirical source must be crossed physical animal × independent occasions × social exposure regime with genuinely replicated realized capture outcomes; it should also include 3D location and independent prey availability to test the full field-individuality bridge.

## Research decision

Source question resolved at publication-method level. **Close the repeated personal threshold attempt on this original ten-bat dataset** without numerical reanalysis.

JAE finding of repeatable vertical organization without supported extra exclusion remains separate and unchanged. Ecological mechanism remains unconfirmed; cannot reverse its conclusion from this group-average competition paper.
