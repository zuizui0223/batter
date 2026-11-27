# V5 Borneo acquisition receipt
GitHub Actions run 45933631273, job 140291690883 completed success, artifact 15169333039, ZIP SHA256 db3f42c996ac8baa7159e9d1e047066d7915e7c6ca1262b37779c024fb8b736e. Actual official Zenodo downloads and published checksum checks:
|record|file|bytes|SHA256|schema|
|---|---|---:|---|---|
|5018280|Haysom_etal_2021_Frontiers.xlsx|10358292|7c356be1ecae1a4a6a0a118fe2ca508c2afb7277eaf93a1e771df76234084c2a|expansion cap stopped schema, source bytes verified|
|7740421|SAFE_data_archive_Yoh2.xlsx|8911914|0c874b45b265d326c9cff12db30f96fa6cbf5f19cbfe24530a64bc72fcf25da2|CRC OK 4 sheets|
|4010757|DeereEtAl2020_PNAS.xlsx|1154266|e597ac5e2e3d382c64dfc89f257ec074c16a97d362f27ef3b42556bcdf872f61|CRC OK 5 sheets|
|7789416|external_files.zip|15751658|ebe6aee0b50ac8a8b2626027adf4f374511f5985b048e7c1be66de47be7086aa|CRC OK 7 members|
|7789416|SAFE_Functional_Groups_template.xlsx|2084581|2baa7270dbd7f19b1234b962defd5b45f06696ef1b91f482c617c975e0d08e7a|CRC OK 3 sheets|
Note Haysom Zenodo metadata DOI is publication DOI 10.3389/ffgc.2021.673071, use exact record URL not guessed DOI. SAFE R code not acquired (format gate).
## Crucial eligibility correction
Yoh 2023 published methods section 2.3: 47 sites each one detector, 1.5–2m above ground, 1–3 nights, 2011–2012. 2014 airborne LiDAR, not simultaneous. Cannot test actual vertical strata response. Deere 2020 ground cameras 2015–17, likewise not paired vertical strata. Haysom 2017–19 canopy/ground pairs, one unlogged and one logged forest, cannot identify forest-type effect separately from site. Thus three verified datasets are potential cross-method landscape comparisons, NOT co-located matched cross-taxon vertical validation. No fit or independent ecological replication yet.
Next targeted Haysom schema audit: workbook expansion cap only, not invalid source. Preserve raw size/hash gate, use ZipFile central directory and streamed worksheet headers, no extraction to disk; independently verify XML member limits; avoid raw rows / coordinates. Compare exact published 99 main usable deployments and 8008 events; need camera IDs, effort, forest, independently assigned locomotor trait. Report whether data admission passes before fitting. No favourable metric selection, no main change. 
