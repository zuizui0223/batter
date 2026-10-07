# Rhino Mini-like support matching result v1

## Execution

- workflow run: **37628603852**
- head SHA: `9e6e02114639c4926108221a7140a74585ad9415`
- conclusion: **success**
- artifact: **11485946253**

## Stress design

For every one of the five leave-one-bat-out subsets:

- exactly **4 bats** retained;
- every self/donor personal centroid uses exactly **2 non-target environments**;
- every training environment contributes exactly **1 trajectory at a time**;
- all such one-trajectory pair centroids are enumerated;
- target trajectories are scored individually;
- 9,999 within-environment cluster-label permutations.

This deliberately removes three support advantages relative to Miniopterus:
- fifth biological individual;
- >2 training environments per personal estimate;
- averaging multiple trajectories inside a training bat × environment centroid.

## PCA1 result

All **5/5 four-bat subsets supported**.

| omitted bat | K | positive bats | p |
|---|---:|---:|---:|
| A | +0.511 | 4/4 | .0203 |
| B | +1.202 | 4/4 | .0007 |
| C | +1.162 | 4/4 | .0004 |
| D | +0.717 | 3/4 | .0061 |
| E | +1.021 | 4/4 | .0010 |

Programme stress verdict:
**PCA1_ROBUST_ALL_FOUR_BAT_SUBSETS**

## Transparent FlightIntensity result

All **5/5 four-bat subsets supported**.

| omitted bat | K | positive bats | p |
|---|---:|---:|---:|
| A | +0.290 | 4/4 | .0118 |
| B | +0.615 | 4/4 | .0007 |
| C | +0.647 | 4/4 | .0004 |
| D | +0.350 | 3/4 | .0075 |
| E | +0.498 | 4/4 | .0017 |

Programme stress verdict:
**FLIGHT_INTENSITY_ROBUST_ALL_FOUR_BAT_SUBSETS**

## Contrast with Miniopterus

Miniopterus:
- 4 bats;
- 19 trajectories;
- each bat represented in 3 environments, hence two training environments for a held-out environment;
- PCA dimensions 1–8 all unsupported;
- supervised identity dimensions 1–3 all unsupported;
- family-wise max-statistic calibration also unsupported.

Rhinolophus remains strongly identifiable even after forcing its personal estimates to the same key structural regime:
- four bats;
- two training environments;
- one trajectory per training environment.

Therefore the current Rhino–Mini contrast is not plausibly explained solely by:
- number of bats;
- number of training environments;
- or within-environment centroid averaging.

## Remaining caveat

The analysis does not equalize total target trajectory count, exact obstacle incidence, sensor/trajectory noise, or species-specific nonlinear structure.

The admissible current contrast is therefore:

> *Rhinolophus nippon* has a strongly detectable portable low-dimensional individual component that survives severe support thinning, whereas no portable linear individual component is detectable in the current *Miniopterus fuliginosus* archive.

Do not convert this into a claim that Miniopterus is infinitely dimensional.
