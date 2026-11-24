# V6/V7 wing trait quality and FD diagnostics
Executed V6 https://github.com/zuizui0223/batter/actions/runs/45342657203 (success).
20 pooled wing-loading values <1 N/m2; 16 <0.5. Several around 0.0005-0.002 N/m2 equal approximately 1/10000 of the pooled mass-area dimensional calculation, consistent with area unit-conversion error, not proof of the original source computation. Other low values combine reported and derived measurements. Original V5 pooled WL should not be used without QC.
## V6 posthoc sensitivity (corroborated names; same paired sites per scenario)
|Scenario|n|Flight SES median|Resource SES median|Flight negative|
|---|---:|---:|---:|---:|
|WL >= 1|148|-1.05765|0.98097|0.92568|
|WL >= 1 frequency-weighted|148|-0.41703|0.51110|0.75000|
|WL >= 1 family-conditioned|148|-0.58936|1.33015|0.75676|
|WL >= 1 diet-conditioned|148|-1.05736|0.99215|0.93243|
Family conditioning is not full phylogenetic control. Diet-conditioned resource contrast reflects mass conditional on fixed diet composition; not evidence of dietary partitioning in that model.
## V7 study-level reconstruction
Executed https://github.com/zuizui0223/batter/actions/runs/45344929018 (success). 932 rows, 457 species with reference IDs. For valid direct source traits use direct values; derive missing traits only from same study-row dimensional measurements (AR=span_cm^2/area_cm2; WL=98.0665*mass_g/area_cm2). First median within reference then median across references. Diagnostic plausibility bounds; no general imputation. Direct-only 338 complete species; direct-or-formula 351, formula fills 83 AR and 79 WL rows. WL range 3.42-43.41322 N/m2; AR 4-13.7. Area-definition variation remains and same-study reference median differs from pooled original estimator.
|Scenario|n|Countries|Flight SES median|Resource SES median|AR SES median|WL SES median|
|---|---:|---:|---:|---:|---:|---:|
|Direct-only repaired names|156|29|-0.968234|0.820212|-0.857678|-0.972922|
|Direct-or-formula repaired names|159|29|-0.985590|0.767885|-0.909942|-0.983880|
|Direct-or-formula strict names|75|20|-0.877397|0.614751|-0.927622|-0.574547|
|Direct-or-formula frequency weighted|159|29|-0.455037|0.368235|-0.483288|-0.323187|
|Direct-or-formula country pool|47|8|-0.616065|0.752553|-0.891313|-0.119565|
|Direct-or-formula complete coverage|86|24|-0.938034|0.923758|-0.852307|-0.920249|
Pattern recurs across overlapping diagnostics; not independent studies or a global significance test. Stronger relative signal for AR across regional-pool definitions. Taxonomic, reporting, effort, area-definition and source bias remain. No direct causal coexistence inference.
## V8
Registered protocol ROOST_FD_COARSE_TERRAIN_CONTRACT_V1.md and workflow https://github.com/zuizui0223/batter/actions/runs/45345122702 (queued at inspection). Actual ETOPO and WorldClim acquisition, regional 2D circuit proxy and out-of-country validation pending. No cave-location outputs, no true flight-resistance or 3D claim. 
