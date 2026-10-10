# Eight Myotis bats: categorical shared receiver support across two nights (executed V6)

**2026-10-10. Verified ORIGINAL source `rx` categorical data only — NO temporal co-detection, prey captures, RSSI, coordinates, 3D altitude or social mechanism estimated.** Original paper Hernández-Montero et al. 2026 (*Ecology and Evolution*), doi 10.1002/ece3.73604. Original OSF project `sg6dz`. Original stable-tag V5 receipt `MYOTIS_2026_EIGHT_BAT_TWO_NIGHT_EXECUTED_RECEIPT_V5.md`.

## Pre-outcome source gate and technical execution

The exact 16 source filenames and OSF resource IDs were frozen before opening their `rx` columns, in `MYOTIS_2026_RECEIVER_PAIR_TWO_NIGHT_CATEGORICAL_CONTRACT_V6.md`, GitHub commit `f694b705fc81a2ddad9baebd0ffe20cb6242c487`.

[Official successful GitHub Actions **38012351593**](https://github.com/zuizui0223/batter/actions/runs/38012351593), committed workflow head `322191110ce5a90ee98c6e86daeed2c52239f413`; source reader `preflight_myotis_shared_rx_pairs_v6.py`, Python 3.13. Every original file ID/name checked through official OSF metadata. The reader selected **ONLY original `rx` value cells**, used them as transient sets, and emitted only count summaries; raw station IDs were never logged, and no other row fields were accessed.

## Real categorical support

| Exact structural quantity | Result |
|---|---:|
| Stable known individual tags | 8 (V5 source-verified) |
| Source observation nights | 2 (20240515, 20240516) |
| Pre-frozen real original files | 16 |
| Possible unordered pairs, before station check | 28 |
| Distinct candidate receiver IDs — night 20240515 | **59** |
| Distinct candidate receiver IDs — night 20240516 | **54** |
| Bat pairs with >=1 shared receiver-ID **within each of the two nights** | **22/28** |
| Bat pairs sharing the **same receiver-ID** on both nights | **22/28** |

Authoritative program status: `PASS_SHARED_RECEIVER_STRUCTURE_BOTH_NIGHTS_ONLY`.

The shared receiver-ID counts mean that each animal of a pair has some technical observations assigned to a matching receiver key in that night. They **DO NOT** demonstrate that the two bats were present **at the same time** or even physically within direct body-body sensing distance. Large/overlapping detection footprints and effort imbalances make this a structural eligibility result rather than evidence of avoidance, cooperation or competition. 22 possible paired comparisons are not 22 biologically independent units because bats appear in multiple pairs.

## Concurrent separate source clock quality check

An independently committed original source integrity check [official successful CI **38012274824**](https://github.com/zuizui0223/batter/actions/runs/38012274824) observed source clock/receiver parseability for all 16 files (**16/16** passed >=95% format/receiver support), but its **frozen status was `HOLD_TIMEZONE_AMBIGUITY`** because source timestamps are timezone-unknown ISO format. It calculated **NO co-detection, site sharing, or behavior endpoints**.

This caveat is binding: receiver-clock synchronization, timestamp timezone/DST conventions, gaps and offset interpretation must be independently resolved and a time-conditioned, autocorrelation-preserving dyad null must be fixed **before** opening synchronous-use outcomes. A common timezone label does not alone prove clock synchronization. Do not retrofit an apparently favorable temporal shift window after outcome exposure.

## Ecological claim ceiling / decision

**Resolved in real public data:** original physical RFID/TX stable for eight bats over two nights; the cohort has **22 structurally eligible bat pairs** with common receiver candidates in both nights. This makes a future same-night temporal sharing/avoidance test *possible to plan*.

**Not yet resolved:** true same-time co-detection, direct encounters, kinship differences in synchrony, individual night-to-night persistence of behavioral response, acoustic interference, prey capture or payoff, the maintenance of 3D vertical-niche shapes.

**Next authorized step:** document clock protocol and source schema semantics from author readme/scripts/published methods without selecting event windows or computing co-detection; verify station deployment consistency and uncertainty in receiver footprint before freezing a single held-out time-conditioned endpoint. Otherwise STOP temporal claim at V6. No changes to the frozen JAE or Behavioral Ecology manuscripts and no promotion of this support result into a third completed paper.
