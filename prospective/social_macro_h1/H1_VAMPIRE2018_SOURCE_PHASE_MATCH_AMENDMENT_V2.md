# Vrtilek 2018 original 188-row source: phase denominator and retention contrasts (v2)

Date 2026-11-19. **Amendment after viewing source design ONLY, before this project's source outcome calculations**. This is a reanalysis of published effects.

Original CSV rsos172483_si_001.csv, Figshare article 6466022 v2, file 12183227; MD5 935d61487756bd62837b9a53cc5f11f8, original SHA256 49e5e2a24ee7e0cb69f2c1df64ddc2c2c0964be39a1d2e5fc1cc9d06d7b5c128, 6,615 bytes, original 188 rows, 36 stable physical bat IDs, source fields: experiment, trial (trailing space), bat, demonstrator, phase, attempt, latency, latency2, exit.in.15, naive.

Outcome-blind verified phase×role rows:
- train: 104 rows, 12 demonstrators (experiment=train,phase=train,demonstrator=T), repeated attempts.
- pre: 24 rows, 24 naive animals (experiment=test,phase=1pre,demonstrator=F).
- during: 36 rows: 24 naive animals (experiment=test,phase=2test,demonstrator=F) plus 12 trained bats (demonstrator=T). **Exclude all 12 trained bats from naive transition denominator**.
- post: 24 rows, 24 naive animals (experiment=test,phase=3post,demonstrator=F).
- Stable physical ID is bat, not trial number; one source trial/individual/phase record required. Triad assignments share social cues and cannot be inferred as separate independently randomized bats.

**Existing published denominator anomaly to resolve from original exit.in.15 coding:** article says pre=0/24 and during=5/23, although 24 original during-naive rows exist. Before opening response counts, predeclare 23 as potentially eligible complete outcome subset; examine missing values in exit.in.15, maybe one missing/not observable. Do not change 23 to 24 or impute 0 without source evidence. Preserve both 24 rows and actual n_valid. If all 24 values are binary, report discrepancy to original denominator and do not claim exact independent replication of 5/23.

**Primary descriptive contrasts fixed ahead of current computation**:
1. Count eligible naive exit.in.15 T/F per phase; count missing/unknown separately, and exact original bat ID joins across three phases. All phase-specific counts must be reported in aggregate without personal identifier strings.
2. Among naive bats with during T and valid later post outcome, report conditional retention n_post_T / n_during_T with missing-post denominator separately. Expected published 4/5 only if source supports it. This is outcome-selected and not an experimental average learning effect.
3. Among all naive bats with matched pre and post valid tests, report transition table (pre T/F × post T/F), with caveat that post follows prior demonstrator exposure so no equal-experience randomized control.
4. For all during F naive rows, compare with their own pre trials only when both were observed; report individual paired transition counts, never count the 12 trained demonstrators in the same responder denominator.
5. Secondary (training data) inspect only 104 repeated trained-role trials from 12 demonstrator individuals; do not claim increase in memory/learning rate without fitting censoring and study-specific attempt covariate.

**No cause of exit asserted**: demonstrator movement, attention, individual learning and co-presence can all contribute. Authors already reported the central 4/5 phenomenon; this is transparent replication and an H1 boundary mechanism, not a novel result nor a bat foraging-resource timing fit.

Source gate https://github.com/zuizui0223/batter/actions/runs/44523605241 ; design gate https://github.com/zuizui0223/batter/actions/runs/44524399804 .
