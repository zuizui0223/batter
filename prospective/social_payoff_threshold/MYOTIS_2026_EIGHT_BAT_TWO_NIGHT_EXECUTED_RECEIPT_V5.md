# Source-valid 2026 Myotis eight-bat, two-night categorical gate — executed result V5

**2026-10-10. Verified real source PROVENANCE / categorical identity, NOT a bat-behavior outcome, synchronized encounter test or ecological mechanism.** Original paper: Hernández-Montero et al. (2026), *Ecology and Evolution*, DOI 10.1002/ece3.73604. Original OSF read-only project: https://osf.io/sg6dz/overview?view_only=4624cf1757b34e87bf7a4aca9d889319.

## Original data actually accessed
Public OSF `proximity_UD/data/sn_prox/`: author-created nightly folders, each containing one CSV per tagged bat as described in original `README.md`. We selected **two specific consecutive original sampling-night folders** `20240515` and `20240516` and **all eight identically named tag series** present in both (16 files total), after exact file-ID/filename allowlist frozen in `MYOTIS_2026_EIGHT_TAG_TWO_NIGHT_CATEGORICAL_CONTRACT_V5.md`. The published logger schedule of 21:00–05:00 legitimately spans midnight.

CSV row-one headers, identical across sources:
`timestamp,date,batdate,time,rx,tx,rfid,dyad,rssi,batch,box,grid_sn,lon_sn,lat_sn,records`.
`rx` and `tx` are separate receiver/transmitter identifier candidates; `rfid` is the proposed physical bat crosswalk. **We do not interpret `dyad` without author semantics**. Original reader copied only `rfid`, `tx`, and `date` categorical values into transient local memory to count uniqueness and compare across nights; no raw IDs were logged.

## Authoritative empirical source support

[Official GitHub Actions 38012020164](https://github.com/zuizui0223/batter/actions/runs/38012020164): **completed/SUCCESS**.

- **8/8** filename-matched original tagged bat series have one nonblank source RFID and one source transmitter key *within each nightly file*, consistent across the two original dates.
- **8 distinct physical RFID keys per day** (no duplicates across those eight source series), and **8 distinct TX keys per day**.
- Every series' categorical RFID/TX association is stable between the two sampling nights.
- 16 original CSVs compared; exact source file identities verified against original OSF v2 metadata; technical row counts are not interpreted as independent flight or bat samples.
- **No RSSI measurements, physical station IDs from rows, geocoordinates, event timestamps/time-series, encounter indicators, feeding performance, prey success, vertical altitude or p-values were used**.

Result code: `PASS_EIGHT_DISTINCT_CROSS_NIGHT_TAGS_CATEGORICAL_ONLY`.

### Chronology of transparent source-access/schema corrections
- Source OSF node and metadata access: [38010699176](https://github.com/zuizui0223/batter/actions/runs/38010699176) success.
- OSF source folder/dated file catalogue access: [38010744981](https://github.com/zuizui0223/batter/actions/runs/38010744981), [38010881468](https://github.com/zuizui0223/batter/actions/runs/38010881468), [38010983448](https://github.com/zuizui0223/batter/actions/runs/38010983448), [38011050723](https://github.com/zuizui0223/batter/actions/runs/38011050723) success.
- Header retrieval initially stopped at OSF external storage redirects; allowed **only** previously observed official OSF regional `files.de-1.osf.io` and original `storage.googleapis.com` delivery hostnames **before** successful header access. [38011479273](https://github.com/zuizui0223/batter/actions/runs/38011479273) header source accessible. False schema STOP caused by parser neglecting compact aliases `rx,tx,rfid,dyad`; corrected and rerun [38011659642](https://github.com/zuizui0223/batter/actions/runs/38011659642).
- [38011625165](https://github.com/zuizui0223/batter/actions/runs/38011625165) read the original **README text only** and confirmed per-tagged-bat nightly CSV meaning. This specifically corrects an early mistaken assumption that filename prefixes denoted stationary receiver units.
- [38011826140](https://github.com/zuizui0223/batter/actions/runs/38011826140) first same-tag categorical test mistakenly required exactly one civil date per nocturnal file; this produced a false `STOP_NOT_STABLE_BIOLOGICAL_TAG`. The published 21:00–05:00 recorder schedule justifies recognizing filename start date **and next civil date** within one sampling night; corrected in a source-only schema amendment before [38011908943](https://github.com/zuizui0223/batter/actions/runs/38011908943) verified one real physical RFID/TX across two nights.
- Finally, 8-tag extension was **pre-frozen** and passed in authoritative 38012020164.

All interim STOPs are provenance information, not evidence that the underlying biology lacks individual signatures.

## What this DOES and DOES NOT establish

**Established:** This independent public source has at least **eight individually recognizable original bat tags associated one-to-one with distinct RFIDs**, observed across **two different sampling nights** in a fixed 2024 local receiver network. The source has published receiver-by-tag timestamps and RSSI (but those event fields have not been analyzed here). Thus unlike one-bout Molossus archives, there is genuine categorical support for prospective bat-level repeated-night analysis.

**NOT established:** That 28 potential dyads among these eight were ever at the same receiver/time, that any pair repeatedly shared or avoided a patch, that any social response is stable, that kinship causes overlap, that acoustic interference reduces capture, or that the underlying measured space is a fine-scale 3D flight distribution. Two nights, eight bats, a partial receiver grid and overlapping ~35-m footprints are still limited.

**Next source-only gate:** verify stationary receiver IDs from event rows as *categorical keys* for the same cohort and that receiver IDs are meaningfully comparable across these two nights. Do not inspect timestamps/RSSI until a primary temporal co-detection endpoint and an autocorrelation/time-of-night conditioned null are frozen. If too few co-observed bat×receiver×night combinations exist, **STOP** rather than relabel zeros into social avoidance.

**Future ecology question:** Are spatial overlap and synchronous receiver-footprint co-use decoupled at the individual/dyadic level? This is at *receiver neighborhood* resolution only. Actual prey capture payoff, independent assigned treatment effects and JAE 3D terrain-relative vertical identity remain completely separate.
