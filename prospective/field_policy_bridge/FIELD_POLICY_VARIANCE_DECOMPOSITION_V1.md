# Field policy variance decomposition v1

Status: frozen post-outcome descriptive analysis.

Question: partition wild P. hastatus H/V policy variation into stable individual, shared source-day, and residual components.

Data: exact harmonized 360-s field-policy rows already used by the 2-D carrier. Fit years separately. H and V are standardized separately.

Model for each year and component:
y = cohort fixed effects + individual random intercept + cohort-day random intercept + residual.

Fit by Gaussian REML with positive variance components and multiple deterministic starts.

Report:
- individual variance fraction
- day variance fraction
- residual variance fraction
- conditional individual ICC = individual/(individual+residual)

Two-dimensional summary: equal mean of H and V variance fractions within year.

Robustness:
- leave one individual out: min/median/max individual fraction
- leave one source day out: min/median/max individual fraction

Interpretation boundary: this quantifies persistence, not its causal origin. Stable individual variance may include morphology, physiology, development, long-term learning, or persistent skill/history.
