# Historic bat individual-output retention and permission gate

**Updated 18 October 2026:** The four original Movebank DOI **published data packages** have now been individually checked in their official DSpace Full item records and **all four specify CC0 1.0 Universal** (`dc.rights`, `dc.rights.uri`). This is a rights-first reproducibility *plan*, not an existing long-term archive, not an independent legal conclusion for the separate derived original per-ID Actions ZIP files or permission to reuse their animal identifiers, and not a completed GPS/DEM rerun.

## Exact currently reported artifact expiry (UTC)

| Original source outputs | Original workflow | Four original source ZIPs expire |
|---|---:|---|
| Fine 500-m place × speed × turning | 36519747717 | **2026-12-28 04:01:37** |
| Native joint 500-m 3D geometry | 36881187913 | **2026-12-30 15:02:49** |
| Terrain-corrected joint geometry | 36946126004 | **2026-12-31 00:28:01** |
| Corrected co-use individual/dyad results | 36953712597 | **2026-12-31 02:01:52** |

**Earliest source-artifact deadline: 28 December 2026.** Recheck the live expiry metadata. GitHub documents that a public repository's artifact retention range is 1–90 days and changes to repository or organization retention settings do **not retroactively extend existing artifacts**. Source: https://docs.github.com/en/organizations/managing-organization-settings/configuring-the-retention-period-for-github-actions-artifacts-and-logs-in-your-organization

## Specific data ownership, attribution and redistribution review

**Verified published dataset rights, inspected 18 October 2026 using each official Full item page (not just a generic Movebank policy):**

| Original data package | DOI | Official Full item rights field | Rights URI |
|---|---|---|---|
| *H. monstrosus* | [10.5441/001/1.278](https://doi.org/10.5441/001/1.278) | **CC0 1.0 Universal** | [DSpace Full metadata](https://datarepository.movebank.org/entities/datapackage/a51b51e0-fbf2-43e2-86ae-bc41c9f53a98/full) |
| *P. hastatus* 2022 | [10.5441/001/1.321](https://doi.org/10.5441/001/1.321) | **CC0 1.0 Universal** | [DSpace Full metadata](https://datarepository.movebank.org/entities/datapackage/9ce236cf-c0a7-41c4-bbf6-eaf802b2ae92/full) |
| *P. hastatus* 2023 | [10.5441/001/1.322](https://doi.org/10.5441/001/1.322) | **CC0 1.0 Universal** | [DSpace Full metadata](https://datarepository.movebank.org/entities/datapackage/6749e3ab-1625-445c-bd42-9feac301dedf/full) |
| *P. hastatus* 2016 | [10.5441/001/1.282](https://doi.org/10.5441/001/1.282) | **CC0 1.0 Universal** | [DSpace Full metadata](https://datarepository.movebank.org/entities/datapackage/5259147d-04a1-471d-a65c-240cd3d7071d/full) |

**The four metadata records expose the exact fields** `dc.rights = CC0 1.0 Universal` and `dc.rights.uri = http://creativecommons.org/publicdomain/zero/1.0/`. The machine-readable source evidence (four DOI/UUID URLs, license and dated verification receipt) is in [the original DOI rights snapshot](figures/VERIFIED_MOVEBANK_ORIGINAL_DOI_RIGHTS_V1.json), with an offline integrity guard.

**What CC0 verification resolves:** original *public data-package* reuse restrictions were previously unverified and can now be cited precisely at their source. **What it does not resolve:** ownership and appropriate controlled retention/republication of **separately generated, originally saved GitHub Actions per-individual/dyad ZIP outputs**; original author contribution/coauthorship and attribution, dataset/version lineage, ethically appropriate animal tag/linkage exposure, and human editorial permissions. CC0 for one published dataset is not a substitute for an independent rights review of every component of a new bundled archive.

The four original source tracking DOI records must be reviewed independently rather than presumed to share a license:

- *Hypsignathus monstrosus*: 10.5441/001/1.278
- *Phyllostomus hastatus* 2022: 10.5441/001/1.321
- *P. hastatus* 2023: 10.5441/001/1.322
- *P. hastatus* 2016: 10.5441/001/1.282

Movebank says original owners select access and license terms, and publicly downloadable data can have CC0, CC BY or CC BY-NC licenses. The general terms explain that for data genuinely covered by those public CC licenses, a separate owner permission request is *not required* for the specified CC-licensed use, but appropriate attribution is needed and outreach/credit or collaboration should be considered. Do **not** assume the four original studies have the same status. Derived source-per-animal result ZIPs, authorship, geolocation sensitivity and use of original animal tags also require a source-appropriate publication and governance assessment.

Official sources: https://www.movebank.org/cms/movebank-content/data-policy ; https://www.movebank.org/cms/movebank-content/general-movebank-terms-of-use ; https://www.movebank.org/cms/movebank-content/citation-guidelines

## Concrete resolution steps, not completed here

1. **Before 28 December 2026**, an authorized data steward should confirm all original 16 ZIP artifact IDs, published SHA256 checksums and live expiry times in the aggregate-only integration file figures/FROZEN_CROSS_ESTIMAND_ELIGIBILITY_V1.json.
2. **Original published DOI license verification is complete (four CC0 1.0 data packages)**; next inspect the lineage/rights for the **separately generated original per-ID/dyad result ZIP outputs**, author credit/coauthorship, location/animal-ID exposure concerns, and coauthor/editorial overlap before approving storage or redistribution. Record a decision for the derivative ZIPs, not just the source CC0 values.
3. Where terms allow, place original exact checksum-matched source ZIPs in a **steward-managed access-controlled archival location**, with owner approvals, applicable credit, access restrictions and a recorded file manifest. **Do not publicly mirror animal-ID-bearing source result archives to the draft PR.**
4. With that authorized archive, independently execute the optional original-zip checker: python3 prospective/unified_individuality/validate_cross_estimand_eligibility_v1.py --artifact-dir /authorized/original_zip_directory . It rehashes the original 16 ZIPs and recomputes the panel-qualified **5/3/5/5 V/S–I bat membership** and **9/3/5/8 co-use dyads with both geometry bats** without printing original IDs.
5. The public proof can retain the aggregate counts, SHA256 metadata, original workflow IDs and verification code. Any future permanent DOI package must exclude restricted original bat IDs/positions unless license and coauthor approvals explicitly permit them.
6. Independent GPS+reference+DEM source data and historical environment rerun remains a separate hard stop: exact source-output hash verification **does not** establish reproducible empirical analysis from raw tracking records.

## Current status

**Verified now:** all four original published DOI packages explicitly show **CC0 1.0 Universal** in DSpace Full metadata (18 October 2026); the 16/16 original source ZIP SHA256 digests, cohort-qualified bat-ID intersection counts, original co-use dyad support partitions, machine-readable aggregate receipts and offline source-ID verification procedure.

**Not complete:** a recorded rights and stewardship decision for the 16 **derived original ID-bearing artifact ZIPs**, any approved permanent restricted archive, GPS/DEM end-to-end rerun, human source/coauthor approval and final journal upload. Source-package CC0 is verified but does not automatically answer these separate questions.

This checklist does not perform future reminders or background monitoring and does not authorize unrestricted data redistribution.
