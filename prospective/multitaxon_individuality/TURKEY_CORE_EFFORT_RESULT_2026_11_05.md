# Turkey spring reconfiguration survives individual removal in some groups

**5 November 2026. Original GPS replay and post-inspection within-source
diagnostics; not independent replication or a biological significance test.**

Question: is the observed seasonal reconfiguration confined to the previously
identified animal, or does expansion remain among the other animals after
matching observation dates and removing each animal? The full-year geographic
group definitions are inherited, not independently defined populations.

## Source results

The original Movebank turkey source [10.5441/001/1.671](https://doi.org/10.5441/001/1.671)
was downloaded again. Publisher MD5, pinned SHA256, original animal/tag/outlier
rules and the independent timestamp-position multiset checks passed for 435,214
accepted GPS fixes. The frozen monthly analysis at source commit
`45017e0f7f35fd79468db07f16ee162816efc0d6` was replayed before the follow-up.

The primary endpoint is April minus February **mean pairwise monthly-centroid
distance**, in km, distinct from the earlier monthly median. Day-specific
spherical centers receive equal weights. Every group has all 28/29 February,
31 March, 30 April, 30 June and 31 July days shared among its members. We also
select exactly seven shared dates per month, using 24 fixed seeds, and delete
each animal without changing the selected dates. Intraday sampling is not
otherwise standardized. Ranges below are dependent sensitivity ranges, not CIs.

| Source group | Full-day April minus February mean distance | Seven-day draws | Worst individual deletion across all draws |
|---|---:|---:|---:|
| 2020 six-animal core, 15 pairs | +3.357 km | +3.014 to +3.542; 24/24 positive | +1.704 km; every deletion positive in 24/24 draws |
| 2019 larger component, 11 animals/53 edges | +0.415 km | +0.289 to +0.606; 24/24 positive | −0.215 km; every deletion positive in only 4/24 draws |
| 2019 smaller component, 7 animals/20 edges | +2.609 km | +2.049 to +3.194; 24/24 positive | +1.468 km; every deletion positive in 24/24 draws |

The 2019 larger component also changes sign after one deletion using all days
(minimum −0.098 km; 10/11 deletions remain positive). Thus the claim of
equally distributed, removal-robust spring expansion in *all* components fails.
Using all member pairs instead of only the original 5-km graph edges (55 versus
53; 21 versus 20) does not change this verdict.

## Concentration and persistence

For the original seven 2020 animals, the full 21-pair mean increases by
6.951714 km between February and April. Exact accounting is:

`total = (6/21) × isolate–core change + (15/21) × core–core change`

The two weighted terms are +4.554086 km (65.5%) and +2.397628 km (34.5%).
The majority is associated with the six pairs involving the original isolate,
but expansion remains within the other six animals. These are signed
pair-distance contributions, not causal shares of an animal's displacement.

Persistence is less robust. In the 2020 core, February-to-March is positive
in 22/24 seven-day draws, and every animal deletion stays positive in only
15/24. February versus the average of **June and July monthly distance means**
is positive in 24/24 draws, but every deletion stays positive in only 18/24.
This does not establish uniform onset or persistent, broadly distributed
expansion throughout spring and summer. A pooled summer centroid is a
different estimand and was not substituted.

## Source reference attributes

The original eligible cohort was joined privately to the published reference
table. All seven 2020 animals are listed as female; the six core members are
listed as adult and the isolate as juvenile. Reference life stage is static,
not independently validated age/reproductive state at each observation. One
juvenile-coded animal cannot identify an age effect separately from identity.
2019 includes 15 female/4 male and 16 adult/3 juvenile-coded animals. The
source-wide 339 reference rows were not treated as the analyzed cohort.

## Numerical audit and reproduction

The replay agrees on counts, missingness and categories, and on all distance
values rounded to the report's 0.001 km precision. It is **not bitwise exact**:
110 floating-point values differ, maximum 0.00000922134 km (9.22 mm). Initial
exact and 1e-9-km reconciliation failed. After inspecting those differences,
the numerical gate required both <=1e-4 km discrepancy and agreement at 0.001
km reporting precision. This diagnostic gate amendment is post-inspection;
no biological threshold or cohort changed. An independent cross-product/atan2
distance expression differs from the source acos expression by at most
0.00001000546 km on follow-up distances. This checks arithmetic, not GPS accuracy.

- [Original follow-up contract](TURKEY_CORE_EFFORT_DESIGN_2026_11_05.md)
- [All outputs and reconciliation differences](TURKEY_CORE_EFFORT_RESULT_2026_11_05.json)
- [Published reference cohort counts](TURKEY_CORE_EFFORT_COVARIATES_2026_11_05.json)
- [Full original/stored numeric differences](TURKEY_CORE_EFFORT_REPLAY_DIFFERENCES_2026_11_05.json)
- [Portable original-source replay](turkey_core_effort_influence_v1.py)
- [Static result validator](validate_turkey_core_effort_v1.py)
- [Independent-source admission contract](TURKEY_INDEPENDENT_REPLICATION_GATE_2026_11_05.md)

```
python prospective/multitaxon_individuality/turkey_core_effort_influence_v1.py --output-dir /tmp/turkey-followup
python prospective/multitaxon_individuality/validate_turkey_core_effort_v1.py
python -m unittest discover -s prospective/multitaxon_individuality/tests -p test_turkey_core_effort_influence_v1.py -v
```

Only aggregate outputs are published. Dyads, repeated draws, years and graph
components are not certified independent populations. Neither geographic
centroid separation nor a nearby GPS pair demonstrates social contact,
resource partitioning, migration timing or reproductive mechanism.
