#!/usr/bin/env python3
"""Prospective sample-size planning for the paired solution-opportunity experiment.

This is a planning approximation, not the confirmatory test.
The confirmatory analysis uses the randomized within-individual OPEN-versus-CONSTRAINED
family assignment.

We approximate power for a one-sided paired mean contrast using a noncentral t
distribution, parameterized by standardized paired effect d = mean(Delta_i) / sd(Delta_i).
"""

from math import sqrt
from scipy.stats import t, nct

ALPHA = 0.05
N_VALUES = [10, 12, 14, 16, 18, 20, 24]
D_VALUES = [0.5, 0.6, 0.7, 0.8, 1.0]


def power_one_sided_paired_t(n: int, d: float, alpha: float = ALPHA) -> float:
    df = n - 1
    critical = t.ppf(1.0 - alpha, df)
    ncp = d * sqrt(n)
    return 1.0 - nct.cdf(critical, df, ncp)


def main() -> None:
    header = ["n"] + [f"d={d:.1f}" for d in D_VALUES]
    print("\t".join(header))
    for n in N_VALUES:
        vals = [f"{power_one_sided_paired_t(n, d):.3f}" for d in D_VALUES]
        print("\t".join([str(n)] + vals))


if __name__ == "__main__":
    main()
