# JAE RC2 original tracking-source rights: source-gated DataCite metadata audit

**2026-10-10; frozen before remote DOI-rights queries.** Editorial legal/reproducibility support only, not a copyright opinion, biological data reanalysis, new test, release or author permission.

## Why this is necessary
The [Movebank General Terms](https://www.movebank.org/cms/movebank-content/general-movebank-terms-of-use) state that CC0, CC BY and CC BY-NC public-study downloads do not require separate owner permission for licensed uses, while following license-specific conditions, citations and reasonably attempting to contact dataset owners for new analyses is encouraged. [Movebank citation guidance](https://www.movebank.org/cms/movebank-content/citation-guidelines) says study-level owners retain ownership and citation/attribution needs must follow the study/owner terms; merely saying "we used Movebank" is inadequate. The [Movebank data policy](https://www.movebank.org/cms/movebank-content/data-policy) distinguishes CC licences and restricted/custom data. This policy **does not prove the licence of ANY one DOI**.

Only the exactly **ten** DOI identifiers listed in `submission/jae_v0_4_0_original_source_rights.template.json` may be checked:
- 6 original named source DOI datasets: *Tadarida*, *Eidolon*, *Hypsignathus*, three *Phyllostomus* panels;
- 4 nonrepresentative external-boundary datasets: *Nyctalus* Zenodo, *Hipposideros* Dryad, *Myotis vivesi* and *Pteropus* Movebank.

## Allowed *metadata-only* endpoint and outputs
- Query at most one original DataCite DOI record per DOI, using exact canonical `https://api.datacite.org/dois/{URL-encoded-DOI}` with HTTPS, strict redirect to `api.datacite.org` only.
- No moving-animal tracks, sample locations, dataset files, PDF contents, owner emails or raw metadata descriptions accessed or printed.
- Parse at most 256 KiB of JSON, and only `data.id`, `attributes.doi`, `attributes.rightsList`, `attributes.url` as source identity/landing link, and `attributes.publicationYear`. Emit rights text, `rightsIdentifier` and `rightsUri` only if they occur verbatim in DataCite response; cap strings. Do not construct a missing CC licence.
- If a CC rights identifier is declared, status `METADATA_CC_CANDIDATE_NEEDS_DATASET_TERMS_CONFIRMATION`, **not** 'permission secured'. If DataCite has no rightsList, `NO_MACHINE_READABLE_LICENSE_OWNER_REVIEW_REQUIRED`. If DOI lookup inaccessible or wrong identity, `STOP_METADATA_LOOKUP_OR_IDENTITY`, never infer original dataset does not exist.
- Human authors must verify the original repository landing page and data-owner terms actually in force when data were downloaded, attribution, restrictions on derived maps and whether separate explicit permission is legally needed. The public signing form remains **all UNVERIFIED** until humans approve it.
- This is a **single one-time frozen check**; no DataCite-specific field probe outside fixed exact DOI list and no reclassification by opportunistically substituting other sources.

## Gate
No CI success implies compliance. Both `submission/jae_v0_4_0_metadata.json` and `submission/jae_v0_4_0_policy_signoff.json` remain human-release blockers; `LICENSE` for newly authored analysis code is independent of dataset use rights. No final GitHub Release/DOI or JAE submission is authorized by this report.
