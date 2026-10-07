# Rhino theta-to-lane linkage result v1

## Execution
- workflow run: 37635491980
- artifact: 11488631408
- eligible route-centroid cells: 10
- bats: B,C,D,E

## Held-out-bat linkage

Model:
[
\mathbf c_{i,e}=\boldsymbol\mu_e+\mathbf b\theta_{i,-e}+\epsilon.
]

Observed prediction gain over environment-only baseline:
[
G=-0.08779.
]

Bat gains:
- B +0.14949
- C +0.08358
- D -0.20826
- E -0.37598

Positive: 2/4.

Exact 4! theta-profile reassignment null:
- p = 0.29167
- supported = false

Descriptive full-data slope:
[
\mathbf b=(0.348,0.890,-0.226), quad ||\mathbf b||=0.982.
]

The descriptive slope is not predictive under held-out-bat validation.

## Interpretation

The portable FlightIntensity theta does **not** predict the individual's absolute 3-D lane centroid in a new bat under this archive.

Thus the context-specific spatial realization is not reducible to a universal linear function of the one-dimensional movement-intensity parameter.

This strengthens a two-level architecture:

[
\text{portable policy }\theta_i
\quad + \quad
\text{separable context-specific spatial realization }h_{i,e}.
]

The route-axis result still shows that h is geometrically simple in one sense: within a fixed configuration, route identity is carried mainly by absolute lane/centroid placement rather than a complex translation-invariant curve.
