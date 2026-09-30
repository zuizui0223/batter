# Pteropus terrain-confound audit result v1

**Classification:** post-outcome confound diagnostic; it does not alter the historical prospective MSL verdict.

| endpoint | observed | null mean | calibrated excess | p(null>=obs) | verdict |
|---|---:|---:|---:|---:|---|
| original centered MSL (pinned) | +0.11003 | -0.05870 | +0.16873 | 0.0001 | PASS |
| centered MSL - DEM | +0.00728 | -0.02503 | +0.03231 | 0.0023 | PASS |
| centered DEM terrain | +0.27630 | -0.10257 | +0.37887 | 0.0034 | PASS |

Terrain-adjusted/original calibrated-excess ratio (descriptive): **0.192**.

Frozen interpretation: **centered vertical individuality persists after terrain subtraction, while repeatable terrain use also exists; terrain contributes context but does not eliminate the vertical signal**

The DEM subtraction is a terrain-relative proxy, not a source-measured AGL endpoint. All four individuals, the original session universe, 5-km cells, centered bins and support rules were retained.
