# Miniopterus structural identifiability audit v1

## Status

**Post-outcome design audit.** This does not change the frozen Miniopterus PCA/identity-subspace results or relabel their test statistics. It corrects their ecological interpretation.

Sources:
- [Dimension scan workflow 37625879870](https://github.com/zuizui0223/batter/actions/runs/37625879870), artifact 11483569925
- [Structural inventory workflow 37642465695](https://github.com/zuizui0223/batter/actions/runs/37642465695), artifact 11493871783

## Source incidence structure

19 trajectories from four bats A–D form exactly **12 distinct bat × obstacle-environment cells**.

| environment | observed bats | count |
|---|---|---:|
| Env1 | A | 1 |
| Env2 | B,C,D | 3 |
| Env3 | A,B,C,D | 4 |
| Env4 | B | 1 |
| Env5 | D | 1 |
| Env6 | A | 1 |
| Env7 | C | 1 |

Each of the four bats is observed in exactly three environments.

Only **Env2 and Env3** contain more than one bat. Five of seven environments contain a **single bat**.

## The identification problem is algebraic

The frozen Mini preprocessing, inherited from `cross_species_policy_axis_v1.py`, computes:

\[
\mathbf z_{k,e}=
\frac{\mathbf x_{k,e}-
\overline{\mathbf x}_{e}}{s_{pooled}}
\]

where the environment mean is computed over all recorded trajectories in that environment.

For a one-bat environment e with n trajectories, all of those trajectories are from the same bat i. Therefore:

\[
\overline{\mathbf z}_{i,e}
=\frac1n\sum_{k=1}^n\mathbf z_{k,e}
=\mathbf 0
\]

**exactly**, for every feature, regardless of the bat's true movement style.

That means five of the twelve bat×environment centroids used in the donor/history model are mechanically zero.

In particular:
- bat A's only multi-bat environment is Env3; its other two environment centroids are mechanically zero;
- bats B,C,D share only the two multi-bat environments Env2 and Env3; each one's third centroid is mechanically zero.

The data therefore do **not** contain three independently informative multi-bat environments from which to estimate a stable species-wide bat-specific policy axis.

## Interpretation of the all-dimensionality failure

The 1–8D unsupervised and 1–3D supervised scans remain null under their exact frozen estimands.

However, the result must be interpreted as:

> portable individual policy was not detected **under a sparse, structurally confounded observation design in which many bat×environment personal centroids are forced to zero by preprocessing**.

It is **not** a strong biological contrast of “Rhinolophus stable, Miniopterus intrinsically variable,” and it is certainly not evidence that Miniopterus behavior is nonconvergent, high-dimensional, or governed by no finite rule.

Do not rescue the failed frozen diagnostic by changing centering/thresholds after opening. A species generality claim needs new, properly crossed design with multiple individuals in each independently held-out environment.
