# V5 empirical FD baseline
Executed run: https://github.com/zuizui0223/batter/actions/runs/45342495171, success.
Source counts and cave grain: 1514 exact uniquely landscape-matched and realm-consistent composite site keys across 44 countries; 4030 cave-taxon pairs. Not an audited complete census of 2002 caves. Strict names resolve 6428 occurrence and 559 checklist rows; corroborated encoding sensitivity adds 9 and 118, respectively. No precise locations exported.
Crane pooled mean wing AR/WL metadata confirmed, n.AR/n.WL pooled effective sample sizes. 359 species complete positive AR/WL; 337 with both positive source counts. 162 trait-complete recorded species in conservative sites. IMPORTANT: WL minimum 0.000473074 N/m2 is highly suspect and can influence log range and regional pools. Results below are provisional pending V6 QC; do not use as confirmed ecological evidence.
## Paired MPD null, same cave keys / taxa / draws
|Scenario|Sites|Countries|Median flight SES|Median resource SES|Fraction flight delta<0|Fraction resource delta<0|
|---|---:|---:|---:|---:|---:|---:|
|Strict realm primary|70|18|-0.986994|0.632301|0.9000|0.3000|
|Encoding repair realm|152|26|-1.125251|0.888600|0.9408|0.2434|
|Repair country pool|47|8|-0.712920|0.731188|0.7660|0.2766|
|Repair frequency weighted realm|152|26|-0.499654|0.508584|0.8026|0.3487|
|Repair 100% coverage realm|84|23|-0.983292|0.919156|0.9524|0.2619|
|Repair positive source counts realm|145|25|-1.202623|0.867120|0.9517|0.2345|
Standalone flight: 154 sites, 28 countries; median SES -1.121466; negative delta 145/154. Strict resource: 276 sites, median SES +0.757647. Same sample paired result is the more relevant contrast. Median effects differ by axis; no paired statistical inference or global p-value. Overlapping sensitivities are not independent replications.
## Interpretation
Recorded assemblages show provisional flight-trait clustering alongside resource-trait dispersion relative to empirical regional reference. A common flight filter with differentiated resource use is one hypothesis, NOT established mechanism. Regional, phylogenetic, sampling, measurement, cave identity and source effects remain. Country weighting and frequency null attenuate flight clustering. V6 tests extreme WL, 5–95% winsorization, AR vs WL decomposition, same-family and same-diet nulls; these are posthoc diagnostic tests. No terrain/3D connectivity predictor has been applied.
