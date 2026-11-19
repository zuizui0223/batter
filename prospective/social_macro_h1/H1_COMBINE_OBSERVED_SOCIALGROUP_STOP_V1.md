# COMBINE original *reported* (nonimputed) bat social-group size: structural STOP for global H1

**2026-11-19 | source/data-quality finding, NOT a fitted ecological effect.**

**Data provenance:** Soria et al. (2021), COMBINE (Ecology DOI `10.1002/ecy.3344`), original Figshare v4 DOI `10.6084/m9.figshare.13028255.v4`. This turn directly inspected the Git blob `7e274bac17eba845d93cdd27c1357605af3d710e` of a third-party mirror's `Soria_etal_2021_Traitdatareported_snapshot.csv`. Its README reports the copy is byte-identical to the original Figshare `trait_data_reported.csv` (original Figshare file id 27703263). **Authoritative original-content hash verified:** Figshare v4 API identifies file `trait_data_reported.csv` as ID 27703263, size 1,612,538 bytes, MD5 `d894586c3858620723b1182d8b491d3e`. The complete mirrored Git blob independently yielded exactly that size and MD5 (MD5 implementation validated against standard test strings). This authenticates dataset content against the published hash, although the file was retrieved from a Git mirror rather than directly from the Figshare file download endpoint. The earlier independent Actions attempt to download *every* Figshare file stopped without verifying any single data file; a targeted recheck has been issued. Source raw bytes and animal-level rows are not committed to `batter`.

## Actual source coverage

| QC check | Verified value |
|---|---:|
| Total reported-source rows × columns | 6,263 × 60 |
| Chiroptera taxon rows | **1,342** |
| Valid IUCN2020 binomial taxa | 1,335 |
| Literal `Not recognised` IUCN values | 7 *different* PHYLACINE species, all group-size NA |
| Nonimputed reported `social_group_n` for bat taxa | **45/1,342 = 3.35%** |
| Missing social group size | **1,297/1,342 = 96.65%** |
| Group size recorded as exactly one | **33/45 = 73.3%** |
| Group size reported >1 | **12/45** |
| Group size reported >5 | **3/45** |
| Nonimputed bat groups with diet and adult mass available | **45/45** |
| Families represented among measured group sizes | **6** |

**Taxonomy correction:** An earlier provisional count of 1,336 was the number of distinct literal IUCN labels: it erroneously collapsed seven distinct taxa whose IUCN entry is the same string `Not recognised`. Their separate PHYLACINE binomials show there are 1,342 source bat taxon rows, of which 1,335 have recognized IUCN binomials. The 45 recorded social-group sizes and the analytical STOP do not change. Do not silently merge unmatched taxa.

### Data availability by family

| Family | Taxa in reported table | With social group size | Rate |
|---|---:|---:|---:|
| Pteropodidae | 199 | 30 | 15.08% |
| Vespertilionidae | 471 | 9 | 1.91% |
| Emballonuridae | 54 | 3 | 5.56% |
| Nycteridae | 16 | 1 | 6.25% |
| Hipposideridae | 95 | 1 | 1.05% |
| Rhinolophidae | 93 | 1 | 1.08% |
| All remaining bat families combined | 414 | **0** | 0% |

Within the 45 reported group-size bats, 30 are Pteropodidae (**66.7%**), whereas Pteropodidae is only 199/1,342 (**14.8%**) of bats in the reported table. The *odds of social-group size being documented* are **13.35× higher** for Pteropodidae than other bats (counts: 30/169 vs 15/1128). This is an **observation/selection property of the source table**, not a biological group-size difference.

**Crucial identifiability failure:** All 30 recorded bats with >50% plant dietary fraction are Pteropodidae; no bat from other recorded families has plant >50%. Thus in this dataset, the binary majority-plant indicator is algebraically identical to a Pteropodidae family dummy. A family-adjusted plant versus insect resource effect **cannot be separately estimated** (design matrix rank deficiency). Any unadjusted group-size vs diet comparison is entirely vulnerable to family/taxonomic coverage bias, on top of 96.65% missing sociality outcomes. 14/45 recorded species are >50% invertebrate-fed; one remains neither majority plant nor majority invertebrate. No phylogenetic correction rescues the absence of within-family cross-diet comparisons.

### Value distribution and biological unit

Reported group-size values: `1` (33), `1.25` (2), `1.33` (1), `1.5` (6), `5.5` (1), `6` (1), `45` (1). That is only 12 recorded species above singleton size. The maximum 45 belongs to *Rhynchonycteris naso*; species-level mean/number need source provenance before interpreting social systems. The field `social_group_n` means number spending most daily time together, not colony abundance, cooperative foraging or male-only grouping. Values are **nonimputed published COMBINE traits**, not freshly observed daily animals or independently measured behavioral probabilities in this programme.

## Scientific decision (go/no-go)

- The prewritten **>=30 nonimputed species gate is numerically met (45)**, but a minimum quantity gate alone is not sufficient.
- **STOP a group-size × majority-plant versus insect phylogenetic ecological coefficient**: categorical predictor is perfectly family-confounded among observed response species; very low response coverage and severe class imbalance mean no independent ecological signal can be separated from measurement selection.
- **STOP original H1 male sociality/info sharing**: group-size is a different trait, and no evidence links the number `1` or `45` to foraging information or reciprocity.
- Group-size data are not useless: the decisive, independently inspectable deliverable is an **observed-data coverage/identifiability result** showing why naive global bat sociality models can be apparently large while effectively unidentifiable.

Next valid input is *independently documented* social foraging or male group status for bat species that fills **within-family, cross-diet** response gaps, while retaining field effort/methods. A complete response source with measured social behavior is more useful than adding 1,300 imputed values. Until then the approved H1 deliverable is a study-level source ledger and methodological falsification, not a new universal behavioral law.

**Original-source Figshare verification workflow** (may be queued): `h1_combine_figshare_source_gate.py` with isolated Actions `h1-combine-source-gate.yml`. This separate step can upgrade provenance but **cannot change the observed 45-value sparsity** unless the original dataset materially differs from the mirrored source; discrepancies must be investigated instead of silently substituted.
