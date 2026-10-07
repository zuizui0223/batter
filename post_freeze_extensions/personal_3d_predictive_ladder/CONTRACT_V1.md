# Personal 3D predictive ladder v1

## Why this exists

The first past-to-future decomposition produced an important asymmetry: the focal animal's own conditional map consistently beat other individuals' conditional maps, but in two *Phyllostomus* panels the focal conditional model still failed to beat the strict other-individual marginal baseline.

So the next question is narrower:

> Is future predictability carried by an individual's overall vertical state, or does the **spatial shape** of its 3D probability map add information beyond that state?

## Four frozen models

- **G0**: other-individual marginal vertical distribution.
- **I0**: focal-individual marginal vertical distribution.
- **G1**: other-individual spatially conditional distribution, P(z|500-m cell).
- **I1**: focal-individual spatially conditional distribution, P(z|500-m cell).

All four score the exact same held-out target fixes.

The key contrasts are:

- marginal identity = I0 - G0;
- shared spatial gain = G1 - G0;
- **self spatial increment = I1 - I0**;
- personal conditional advantage = I1 - G1;
- total personal-history gain = I1 - G0.

The decisive quantity for the original 3D-shape question is **I1 - I0**. If it is positive, knowing *where* the bat is allows its own past 3D probability shape to predict vertical state better than simply knowing that individual's overall height tendency.
