# Peer-plus-past field forecast result v1

## Status

**UNSUPPORTED UNDER THE FROZEN INDIVIDUAL-CONSISTENCY RULE IN BOTH YEARS.**

Authoritative workflow:
- run: **37301038521**
- job: **111733544251**
- head: `fe279c2c578fde715e5cfe3b8576388b10dbd442`
- workflow conclusion: **success**
- fail-closed shell: `set -euo pipefail`

Parent:
`PEER_PLUS_PAST_FORECAST_V1.md`

## Question

After subtracting the contemporaneous cohort-day policy of peers, does strictly prior personal H/V policy history improve prediction of the focal bat's next residual policy?

The frozen support rule required:
- Delta > 0;
- one-sided permutation p <= 0.05;
- >=70% of evaluable individuals with positive individual Delta.

## Results

| year | peer-controlled sessions | targets | individuals | Delta | pooled no-refit R2 | positive individuals | p | verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2022 | 211 | 143 | 30 | +0.10876 | 0.08010 | 16/30 (53.3%) | 0.0009 | unsupported |
| 2023 | 36 | 20 | 7 | +0.40484 | 0.16637 | 4/7 (57.1%) | 0.0140 | unsupported |

Permutation-null means:
- 2022: -0.29210;
- 2023: -0.35829.

The observed average forecast improvement is above the identity-exchangeability null in both years, but the predeclared majority-consistency requirement fails clearly.

## Interpretation

The result rejects an overly simple population-wide forecast model in which a fixed personal centroid estimated from prior residual sessions improves prediction for most individuals.

A weaker statement remains descriptive:

> On average, adding personal past after peer-day correction reduces squared forecast error relative to peer-only prediction, but the benefit is heterogeneous and is not positive for the required 70% of individuals.

This distinction matters because separate peer-day residual identity tests show that individual identity remains detectable after removing shared day context.

Together the results imply:

- a persistent individual component exists at the distribution/identity level;
- that component is not well represented for every individual by one fixed prior-history centroid;
- current field behavior is therefore more compatible with a **personal distribution / policy region plus context-dependent expression** than with a deterministic fixed point.

A useful next model class is:

[
\boldsymbol\theta_{it}
=
\boldsymbol\theta_i
+
\mathbf B_i \mathbf c_t
+
\boldsymbol\xi_{it},
]

where:
- `theta_i` is persistent individual position;
- `c_t` is shared environmental context;
- `B_i` allows individual-specific reaction to context;
- `xi_it` is residual within-individual variation.

The present forecast does not estimate `B_i`; it only shows why a constant-centroid forecast is insufficient as a general rule.

## Claim boundary

Supported elsewhere:
- 2-D H/V individual carrier in 2022 and 2023;
- peer-day residual identity in both years.

Not supported here:
- a fixed personal-past centroid improving next-session prediction for >=70% of individuals;
- autonomous short-term self-reinforcement;
- deterministic personal policy state.

Do not weaken the 70% rule or drop negative individuals.

## JAE firewall

This is post-JAE mechanism work and does not modify v0.4.0.
