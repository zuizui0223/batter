# Independent turkey source audit and executed calendar gate

**5 November 2026. No independent spatial effect has been fitted.**

[Later same-day acquisition and full-archive overlap follow-up](TURKEY_INDEPENDENT_FOLLOWUP_2026_11_05.md): the pinned Maine author release has zero matching timestamp-position rows against all 796,419 discovery rows, but still lacks February. Dryad and male original downloads remain unresolved. A new-source
eligibility contract was saved before examining candidate GPS spatial outcomes.
The exact primary endpoint remains April minus February mean pair-centroid
distance, seven shared observation days/month and leave-one-animal robustness.
The source inventory is a targeted search, not proof that no other dataset exists.

## Maine author release: obtained, but February is absent

The [Gonnerman et al. source](https://datadryad.org/dataset/doi:10.5061/dryad.s4mw6m9gg)
describes female tracking near Bangor, Maine. This is a geographically distinct
study programme from the southeastern discovery source; alternate Maine papers
using the same tracking programme do not create independent replicates.

Dryad metadata is accessible, but this environment received HTTP403 for the
public file link and HTTP401 for the API download. An ordinary browser download
also did not complete. These observations are **access failures**, not evidence
of insufficient sampling. Dryad file3528443 `GPS_Seasonal_-_Used.csv` has declared
size162705 bytes and SHA256
`95b75720531e90904a79e209d1717d5f5a3335625709c63e0e4fa1a29694bc6f`.

The [original-author GitHub release](https://github.com/mattgonnerman/MaineTurkeyConnectivity/blob/e639fb66bf27b16d83c72d03faa638a496246ff4/GPS%20Seasonal%20-%20Used.csv)
was successfully acquired at commit `e639fb66bf27b16d83c72d03faa638a496246ff4`.
Its154101 bytes have SHA256
`2c7f1651235dbc4d411bee524393d91a761fd493751c845ac53eae223501e996`.
The hash differs from Dryad, so the executed result below applies **only to this
pinned author version**, not to the unacquired Dryad bytes.

The actual file has3205 rows and24 source animal labels, with individual ID,
latitude, longitude and timestamp fields. Timestamp-only screening found:

| Source year | Observed months | February rows | Animals with >=7 dates in both February and April |
|---|---|---:|---:|
| 2018 | April, May | 0 | 0 |
| 2019 | March, April, May | 0 | 0 |
| 2020 | March, April | 0 | 0 |

**STOP_NO_FEBRUARY_OBSERVATIONS in all three years.** No centroids, spatial
distances, model coefficients or hypothesis effect estimates were computed.
April-only sample support cannot repair the absent baseline. The result is a
failed eligibility gate, not failure or confirmation of the ecological hypothesis.

- [Executed aggregate calendar receipt](TURKEY_INDEPENDENT_MAINE_TIME_GATE_2026_11_05.json)
- [Reusable timestamp-only gate](screen_turkey_month_support_v1.py)
- [Prospectively fixed admission rules](TURKEY_INDEPENDENT_REPLICATION_GATE_2026_11_05.md)

## Other source paths and their limits

| Candidate | Evidence | Current status |
|---|---|---|
| Maine full original Movebank study | Original author study name is `Eastern Wild Turkey, Gonnerman, Maine`; repository README refers to Movebank | Public original-fix export and numeric study ID unresolved; no effect fitted |
| Maine WinterSelection | [Author v1.0.0](https://github.com/mattgonnerman/WinterSelection/tree/v1.0.0), [Zenodo archive](https://doi.org/10.5281/zenodo.6840568) preparation restricts January–March15 and includes modeled/interpolated positions | Not an unrestricted original February–April observation file |
| Maine SeasonalHMM | [Author repository](https://github.com/mattgonnerman/SeasonalHMM) exports modeled hourly movement inputs | Interpolated positions cannot establish original observed-day support |
| Maine road selection | [Dryad source](https://datadryad.org/dataset/doi:10.5061/dryad.zgmsbcctf), [primary article](https://pmc.ncbi.nlm.nih.gov/articles/PMC13668704/) | Same Maine programme; selected used/available steps, not a new independent full-calendar source |
| Savannah River males2020/2021 | [Lott et al. original GPS release](https://datadryad.org/dataset/doi:10.5061/dryad.rv15dv4fb), [primary article](https://pmc.ncbi.nlm.nih.gov/articles/PMC11046083/) | Raw GPS schema plausible; actual February support unverified. Shared authors/region/year with the discovery archive leave overlap unresolved. Male-only data are a sex/context extension, not a same-sex replication |

The Savannah River files (`Locations2020.csv`, `Locations2021.csv`) have GMT date,
time, animal label and measured-coordinate fields according to their source
README. Capture months alone do not prove released February GPS support.
Public download attempts also failed here. Neither absence nor presence of a
replication effect can be claimed.

## Reproduction and next condition

Obtain the pinned author file using its public GitHub link, then run:

```
python prospective/multitaxon_individuality/screen_turkey_month_support_v1.py --input /private/path/maine.csv --sha256 2c7f1651235dbc4d411bee524393d91a761fd493751c845ac53eae223501e996 --source-url https://github.com/mattgonnerman/MaineTurkeyConnectivity/tree/e639fb66bf27b16d83c72d03faa638a496246ff4 --output /tmp/maine-time-gate.json
```

Only monthly aggregate counts and provenance are committed. Original coordinates,
precise observation dates, animal labels and tracks remain outside the repository.
The next empirical step requires an openly obtainable original February–April
export with certified source/site/deployment provenance, not a new threshold,
substituted month or extrapolated location. The existing core result remains
within-source exploratory evidence, without independent confirmation.
