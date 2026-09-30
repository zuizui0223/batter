# Independent common-noctule validation preflight v1

## Status

**OUTCOME-BLIND PASS. Numeric `Height` magnitudes were not parsed or summarized.**

Authoritative workflow:
- run: `36650800992`
- head: `a352ee1560db8c6aea9ef99e61971b08e7ce2da5`
- artifact: `11069749646`
- digest: `sha256:43185dc20118ae483f47b53ab5ddf89afcfc896b832cbb7c3a1b52300306bf31`

Source:
- *Nyctalus noctula*
- Zenodo DOI `10.5281/zenodo.7535030`
- `Observed_GPS_locations.csv`
- frozen source SHA256 `2f373d47706c5b56313de70b623bb5446f5925c69af30f1b145993419e382aa9`

## Frozen structural result

The exact year × field-period structure is:

| cohort | >=50-fix tracks | repeat individuals | 5-km common-cell evaluable individuals | evaluable target tracks |
|---|---:|---:|---:|---:|
| 2019 early (`19::one`) | 15 | 7 | **6** | 10 |
| 2019 late (`19::two`) | 16 | 4 | **3** | 4 |
| 2020 early (`20::one`) | 20 | 8 | **7** | 13 |
| 2020 late (`20::two`) | 25 | 11 | **11** | 20 |

Totals:
- >=50-fix tracks: **76**
- 5-km common-cell evaluable individual×cohort units: **27**
- evaluable target tracks: **47**
- preflight verdict: **PASS**

These exact eligibility counts are frozen before numeric `Height` is opened.

## Next step

Open the predeclared independent primary validation only:
- session median-center native Height;
- fixed residual-height bins;
- 5-km common horizontal occupancy;
- equal-session self / equal-individual other;
- identical self-derived common-cell weights;
- whole-session identity permutations within year × field-period cohort;
- B=9,999, seed=2026093001.

Mechanism extensions remain closed unless this independent primary test passes.
