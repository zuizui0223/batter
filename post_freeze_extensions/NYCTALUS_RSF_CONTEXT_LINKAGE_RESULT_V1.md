# Nyctalus RSF context linkage audit result v1

## Status

**NONVERTICAL SOURCE/LINKAGE AUDIT. No Height or other vertical-like field was retained or summarized.**

Authoritative final linkage workflow:
- run: `36701188201`
- head: `f02ce1ddf5429ac2b32a261b2313f7b2cad392dc`

Zenodo source:
- `Observed_GPS_locations.csv`: 8,129 rows
- `Model_dataset_RSFFlight_Complete_EPSG25833.csv`: 48,774 rows
- RSF response rows: 8,129 used (`response_rvso=1`) + 40,645 available/random (`response_rvso=0`)

## Deterministic linkage

The two tables use slightly different coordinate precision, so exact floating-point coordinate equality identifies only 19.4% of observed rows.

Within each frozen `trackid`, however:

- observed tracks: **107**
- RSF used tracks: **107**
- common tracks: **107**
- tracks with identical row count: **107/107**
- tracks with a bijective nearest-neighbour mapping: **107/107**
- unique used rows assigned: **8,129/8,129**
- nearest-distance median: **0.187 m**
- nearest-distance 95th percentile: **0.467 m**
- maximum: **0.502 m**
- fraction <=1 m: **1.000**

Thus every observed GPS position has a unique source-RSF used-row counterpart within the same track at sub-metre coordinate discrepancy.

## Available ecological context

The linked RSF table contains, among others:

- `DistanceAssumedRoostsInKm`
- `main_clc2_ratrel` (dominant 50-m land-cover context, including Diverse)
- `forestornot`
- `mindist_WKA_inKm`
- local land-cover fractions
- nearest-turbine attributes

This makes a support-matched **roost/resource context** test possible without introducing external GIS inference.

## Claim boundary

This audit establishes linkage and available context only. It does not show that roost distance, habitat or turbines cause the vertical-identity pattern.
