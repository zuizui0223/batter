# Multitaxon individuality → ecological partitioning (database programme)

**New branch: `prospective/multitaxon-identity-ecology-v1`**  
**Research status as of 18 October 2026:** 437 published animal movement database package metadata records verified and archived; **individual GPS eligibility and cross-species biological test NOT completed**. This is deliberately independent of the [original bat integration draft PR #99](https://github.com/zuizui0223/batter/pull/99), whose source records, source p-values and historical freeze remain unchanged.

## One new biological question

**When does an identifiable animal's movement policy translate into actual ecological resource/space segregation, and when does individuality persist even when resource/space use overlaps?**

We aim for genuine cross-clade inference from archived individual movement tracks, not reusing a few papers or assuming that the bats prove a universal pattern.

Importantly, stable overlapping individual environmental niches (Carlson et al. 2021), movement-derived individual niche hypervolumes (Takola 2026) and individual movement → community resource overlap across Yellowstone ungulates (Caldwell et al. 2026) **already exist**. The prospectively testable addition is the **independent, conditional identity → resource/encounter-partitioning relationship and its ecological moderators**, not the mere existence of individuality or niche overlap.

## Verified 18 October 2026 metadata-only Movebank result

The original Movebank Data Repository *Data packages* DSpace public collection was censused on all nine pages (50 records per page, the last 37), with unique DOI and package UUID:

| Original published repository package metadata | Count |
|---|---:|
| Total packages | **437** |
| Source CC0 packages | **376** |
| Source CC BY 4.0 packages | **27** |
| Source CC BY-NC 4.0 packages | **34** |
| Literal GPS keyword anywhere in stored title/subjects/abstract excerpt | **198** (not confirmed GPS source files) |

This catalogue contains birds, mammals, reptiles and marine movement examples; it **does not** establish 437 independent eligible studies or species. Some DOI/subject records are versions, subsets, multiple taxa or missing usable sensor/individual support. Current metadata alone cannot quantify ecological individuality.

## Files and reproducibility

- [Complete 437-publication source metadata and rights census](MOVEBANK_PUBLISHED_DATAPACKAGES_CENSUS_2026_10_18.json): published DOI, UUID, title, issued date, source keywords, rights and limited abstract text — **no bat/animal IDs or GPS points**.
- [Complete cross-taxon scientific analysis and eligibility design](CROSS_TAXON_RESEARCH_PROTOCOL_V0_1.md): pre-outcome eligibility, independent individual predictability versus resource/encounter segregation, multilevel cross-clade inference, altimetry caveats, and failure/stop rules.
- [15 actual published DOI format/rights examples](METADATA_FORMAT_PILOT_SOURCES_V1.json): birds/mammals/reptiles/sea mammal and **all three licenses**. These only exercise source-format review; they are **NOT a convenience science sample**, and original GPS/sensor contents, animal repeats and ecological eligibility are **not yet checked**.
- [Whole-source census/seed verifier](validate_metadata_census_v1.py): standard-library Python, exact count/right checks and source catalogue blob guard.
- [Separate-estimands synthetic controls](validate_distinct_identity_partition_estimands_v1.py): demonstrate that held-out movement-decision individuality is logically distinct from spatial allocation overlap, not a source bat result or ecology mechanism.
- [Offline GitHub Actions validation](../../.github/workflows/multitaxon-individuality-metadata-v1.yml): tests only source metadata, licence receipts and synthetic logic; **no network animal-data acquisition**.

## Analysis and publication boundary

1. **Next:** audit all 437 original source package bitstream/reference records for real GPS events, repeated animals, deployments, UTC, locations, outlier flags, independent site/study/sampling-year populations, source permissions. Publish every DOI's eligibility or reason for rejection. DO NOT claim a biological effect.
2. Freeze **identity information G** from individual-trained but held-out conditional step choices, using the same covariates and effort as a pooled conspecific model, and an appropriate block-permuted null.
3. Independently measure **environmental/resource use** or **physically opportunity-corrected simultaneous co-use** in the source datasets where those ecological quantities are actually identifiable, with disjoint heldout time blocks and dyad dependence.
4. Only if adequate **independent source populations across ≥3 taxonomic groups** and adequate D3 ecological endpoints survive, fit a multilevel source/clade/habitat model testing moderators of individuality-to-segregation. Report negative and nonidentifiable populations openly.
5. A vertically measured **3D tier** applies only to properly calibrated flight height or dive depth; never pretend terrestrial 2D GPS provides an additional altitude niche axis.

**No cross-taxon biology result or journal-ready universal law is claimed at this stage.** The source metadata census and mathematical protocol are completed research infrastructure for the first data-eligibility screen.
