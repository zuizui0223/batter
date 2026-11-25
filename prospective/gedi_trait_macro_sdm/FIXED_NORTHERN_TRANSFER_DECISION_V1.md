# Fixed northern transfer — executed decision (2026-11-25)

Frozen contract: FIXED_NORTHERN_TRANSFER_CONTRACT_V1.md. Run 45599153163, artifact 15014832006, ZIP SHA256 36447f8b3d4c074c038d28c3fa7916c6274efe61c0b4fca917f38d865c24e02e.

## Data readiness
Fixed GBIF snapshot environment run 45591426116: 10,983 valid common environmental cells, 6,775 forest cells, 56,847 all-bat forest records / 14,124 species-cells. Zero failed WorldCover tiles. After exact-name physical-trait matching and explicit roost-context screening: 50,268 records, 11,970 species-cells, 27 taxa; 20 pass original geographic criteria (>=30 cells and >=4 blocks of >=5 cells). Training-latitude subset: 20,906 screened records, 4,496 species-cells, 16 passing taxa. Northern disjoint block/provider subset: 14,014 screened records, 5,041 species-cells, 17 taxa, 48 blocks, 12 passing taxa. Captive flag count zero is not proof of wild status; establishment field missing throughout.

## In-domain consistency, not independent replication
Run 45599009912, 14 shared taxa, 34,350 comparisons, 50 blocks. Profile increment B2-B1 +0.00984277 (5/5 folds, 32/50 blocks). 1,635/1,763 compared cells, 36/42 comparison providers, 47/50 blocks overlap prior pilot; novel-block check B stopped (only 4 test comparisons). Do not call independent replication.

## Disjoint northern transfer
Train only prior 14-taxon archive; northern data geographically and provider disjoint from entire prior archive, not pooled with training observations. 89,684 comparisons, 35 blocks, 15 test taxa, 15 sources, 2,561 compared cells.
Known species flexible slopes: 47,741 comparisons, 10 taxa, 28 blocks. Profile gain -0.00259445, 8/28 positive blocks; descriptive conditional block bootstrap [-0.0105363,+0.0052003].
Matched trait-only cold start: 89,267 comparisons, 15 taxa, 35 blocks; each test pair excluded from old training; 99.5% pair coverage.
| Model | Baseline | With profile | Gain |
|---|---:|---:|---:|
| AR | -0.694633775 | -0.695981559 | -0.001347784 |
| W | -0.699212991 | -0.700613676 | -0.001400685 |
| WA | -0.686750395 | -0.686726272 | +0.000024123 |
WA profile minus AR base +0.007907503; WA profile minus AR profile +0.009255287; WA profile minus W profile +0.013887404. WA profile gain conditional descriptive bootstrap [-0.0060583,+0.0062781]. All profile increment bootstrap ranges span zero. WA improvement over AR/W is overall predictive information from combined flight and acoustic descriptors, NOT northern confirmation of profile-specific filtering, not causal attribution to hearing, not established inferential significance. The north test combines observation/biological transfer with extrapolated GVSM structural prediction.

## Decision
The original primary SDM remains nonadmitted. 20 geographic passes all latitudes does not replace 16 training-latitude passes or missing terrain, taxonomy, calibrated effort, true PAVD/vertical use and independent validation. Retain positive in-domain recorded-label sorting, negative/inconclusive north profile transfer, and descriptive multivariate trait transfer separately. Do not tune the model against the northern holdout or search more contrasts in the old 14-taxon archive. Next priority: independent structural validation and independent region within GEDI training latitude with harmonized trait/observation data; or a distinct explicitly defined recorded-label prediction research question, not inflated 3D occupancy claims. Main and existing manuscripts unchanged.
