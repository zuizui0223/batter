# Historic bat individual-output retention and permission gate

**As of 17 October 2026:** This document is a rights-first reproducibility *plan*, not an existing long-term archive, an assertion about any source license, source-animal consent, or completed original GPS/DEM reanalysis.

## Exact currently reported artifact expiry (UTC)

| Original source outputs | Original workflow | Four original source ZIPs expire |
|---|---:|---|
| Fine 500-m place × speed × turning | 36519747717 | **2026-12-28 04:01:37** |
| Native joint 500-m 3D geometry | 36881187913 | **2026-12-30 15:02:49** |
| Terrain-corrected joint geometry | 36946126004 | **2026-12-31 00:28:01** |
| Corrected co-use individual/dyad results | 36953712597 | **2026-12-31 02:01:52** |

**Earliest source-artifact deadline: 28 December 2026.** Recheck the live expiry metadata. GitHub documents that a public repository's artifact retention range is 1–90 days and changes to repository or organization retention settings do **not retroactively extend existing artifacts**. Source: https://docs.github.com/en/organizations/managing-organization-settings/configuring-the-retention-period-for-github-actions-artifacts-and-logs-in-your-organization

## Specific data ownership, attribution and redistribution review

The four original source tracking DOI records must be reviewed independently rather than presumed to share a license:

- *Hypsignathus monstrosus*: 10.5441/001/1.278
- *Phyllostomus hastatus* 2022: 10.5441/001/1.321
- *P. hastatus* 2023: 10.5441/001/1.322
- *P. hastatus* 2016: 10.5441/001/1.282

Movebank says original owners select access and license terms, and publicly downloadable data can have CC0, CC BY or CC BY-NC licenses. The general terms explain that for data genuinely covered by those public CC licenses, a separate owner permission request is *not required* for the specified CC-licensed use, but appropriate attribution is needed and outreach/credit or collaboration should be considered. Do **not** assume the four original studies have the same status. Derived source-per-animal result ZIPs, authorship, geolocation sensitivity and use of original animal tags also require a source-appropriate publication and governance assessment.

Official sources: https://www.movebank.org/cms/movebank-content/data-policy ; https://www.movebank.org/cms/movebank-content/general-movebank-terms-of-use ; https://www.movebank.org/cms/movebank-content/citation-guidelines

## Concrete resolution steps, not completed here

1. **Before 28 December 2026**, an authorized data steward should confirm all original 16 ZIP artifact IDs, published SHA256 checksums and live expiry times in the aggregate-only integration file figures/FROZEN_CROSS_ESTIMAND_ELIGIBILITY_V1.json.
2. Review the exact four DOI license records and any additional study terms; clarify credit and coauthor/editorial overlap; confirm permitted retention and redistribution of **derived original bat-ID/dyad records**, not merely public GPS coordinates.
3. Where terms allow, place original exact checksum-matched source ZIPs in a **steward-managed access-controlled archival location**, with owner approvals, applicable credit, access restrictions and a recorded file manifest. **Do not publicly mirror animal-ID-bearing source result archives to the draft PR.**
4. With that authorized archive, independently execute the optional original-zip checker: python3 prospective/unified_individuality/validate_cross_estimand_eligibility_v1.py --artifact-dir /authorized/original_zip_directory . It rehashes the original 16 ZIPs and recomputes the panel-qualified **5/3/5/5 V/S–I bat membership** and **9/3/5/8 co-use dyads with both geometry bats** without printing original IDs.
5. The public proof can retain the aggregate counts, SHA256 metadata, original workflow IDs and verification code. Any future permanent DOI package must exclude restricted original bat IDs/positions unless license and coauthor approvals explicitly permit them.
6. Independent GPS+reference+DEM source data and historical environment rerun remains a separate hard stop: exact source-output hash verification **does not** establish reproducible empirical analysis from raw tracking records.

## Current status

**Verified now:** the 16/16 original source ZIP SHA256 digests, exact cohort-qualified bat-ID intersection counts, original co-use dyad support partitions, machine-readable aggregate public receipts and offline source-ID verification procedure.

**Not complete:** exact per-DOI legal/author permission determinations, any approved permanent ID-bearing archive, original GPS/DEM end-to-end rerun, source-human coauthor signoff and journal upload.

This checklist does not perform future reminders or background monitoring and does not authorize unrestricted data redistribution.
