# V9 coarse terrain result and decision
Executed https://github.com/zuizui0223/batter/actions/runs/45346280133, success. Actual ETOPO CRS EPSG:9518 (horizontal EPSG:4326); WorldClim EPSG:4326. V8 assertion failure explained. Exact raster hashes unchanged. No location-level outputs.
Primary repaired-name frequency-weighted regional SES: 159 eligible, 152 graph-complete at each radius, 29 countries / 4 realms. All model covariates complete in these rows. Equal-country-weight RMSE:
|Radius|Outcome|Country M0|M1|M2|Realm M0|M1|M2|
|---|---|---:|---:|---:|---:|---:|---:|
|50 km|Flight|1.052863|1.136528|1.157396|1.304726|1.316836|1.318210|
|50 km|Resource|0.965473|0.989469|0.999875|1.168154|1.176271|1.183112|
|100 km|Flight|1.052863|1.122913|1.144006|1.304726|1.343133|1.362923|
|100 km|Resource|0.965473|1.000435|1.001108|1.168154|1.207834|1.222487|
Across repaired weighted, repaired uniform and strict weighted x 2 radii x 2 blocking modes = 12 overlapping sensitivity conditions, M2 worse than M0 for both axes in 12/12. M2 improved M1 for flight in 2/12: strict weighted country 100 km (-0.07287) and repaired uniform realm 50 km (-0.00329); neither exceeded M0. Resource M2 worse than M1 12/12. Strict 70 sites, 18 countries, 3 realms. No independent replication or p-value. V9 predicts a descriptive SES (regional reference uses other held-out-country records); not a strict prospective unseen-population prediction.
Decision: close this uncalibrated symmetric 5 km, 50/100 km regional 2D terrain-cost model; do not retune costs to recover a positive. No support for explanatory/predictive increment of these specific broad terrain proxies, not a general rejection of terrain or 3D connectivity. No causal inference. Preserve V7 flight/resource contrast as observational, then test exact richness and occurrence margins within geographic blocks and source/family sensitivities. For actual slope-flight mechanisms use independently verified telemetry with wind, not the public imprecise cave coordinates. An independent non-cave comparator is still required for cave-specificity.
