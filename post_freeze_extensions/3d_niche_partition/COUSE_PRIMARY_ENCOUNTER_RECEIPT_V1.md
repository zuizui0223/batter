# Co-use primary encounter receipt v1

## Status

**PRIMARY ENCOUNTER SET MAY OPEN VERTICAL.**

No terrain-relative pair separation was used to define these encounter sets.

Final definition:
- selected synchronization tolerance from the x-y-time preflight;
- endpoint-near fixes removed before matching in endpoint-excluded panels;
- mutual-nearest temporal matching within the same 500-m cell;
- exact dyad/individual support gates fixed before vertical opening.

| panel | scope | tolerance | individuals | dyads | encounters | phase-shiftable endpoints |
|---|---|---:|---:|---:|---:|---:|
| *Hypsignathus monstrosus* | endpoint-excluded | 60 s | 11 | 22 | 883 | 99.2% |
| *P. hastatus* 2022 | endpoint-excluded | 60 s | 7 | 10 | 347 | 99.4% |
| *P. hastatus* 2023 | all-space | 600 s | 7 | 8 | 679 | 94.1% |
| *P. hastatus* 2016 | endpoint-excluded | 600 s | 5 | 8 | 16,096 | 100% |

All four exceed the predeclared 90% phase-shiftability gate.

## Frozen encounter-set hashes

- Hypsignathus: `fdafe2a5c07acec790196617dc011dae97cb435a061a10c62893479eddc7139c`
- P. hastatus 2022: `f5395250f476e22eab441bd9c2b52297277f282e71d66c0a4eebc531f612158a`
- P. hastatus 2023: `d4250eafeb7b602e47f7b9449bb76d4a71af0f0bfaa3bc3b801b260e69f2f6bb`
- P. hastatus 2016: `65efc47708c6e4b85d4012421cb3d84e3983c46acf46bbe64a7305a8f5546402`

The vertical runner must reconstruct the identical canonical x-y-time encounter descriptor list and abort on any SHA mismatch.

## Interpretation boundary

This is a **shared-local-site co-presence** design.

The encounter distributions are highly localized, especially in the Phyllostomus panels. Even if synchronous vertical separation is supported, the result applies to the repeatedly shared sites represented here, not to the entire foraging landscape.
