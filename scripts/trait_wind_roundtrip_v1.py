"""Exploratory synthetic directional commuting cost, not an empirical fit.
Run: python scripts/trait_wind_roundtrip_v1.py
All morphologies and coefficients are illustrative, not species observations.
"""
import numpy as np

G = 9.81
RHO = 1.2
U = np.linspace(2.0, 16.0, 14001)


def cost_per_m(mass, span, area, parallel, cross, k=1.2, cd=0.08, profile=0.12):
    """Minimum mechanical J/m over feasible forward-heading, level flight.
    Airspeed grid is a scenario assumption; no hovering, gliding, or gusts.
    parallel/cross are ground-track-relative wind components (m/s).
    """
    a = 2 * k * (mass * G)**2 / (RHO * np.pi * span**2)
    b = 0.5 * RHO * area * cd
    speed = parallel + np.sqrt(np.maximum(U**2 - cross**2, 0))
    ok = (U >= abs(cross)) & (speed > 0)
    if not np.any(ok):
        return float("inf")
    return float(np.min((a / U[ok] + b * U[ok]**3 + profile) / speed[ok]))


def routes(span, area, wind, k=1.2, cd=0.08, profile=0.12):
    def c(p, q):
        return cost_per_m(0.02, span, area, p, q, k, cd, profile)
    return 1000 * (c(wind, 0) + c(-wind, 0)), 1123 * 2 * c(0, wind)


def main():
    morphs = {"broad": (0.27, 0.014), "narrow": (0.35, 0.010)}
    for name, (span, area) in morphs.items():
        a0, b0 = routes(span, area, 0)
        a4, b4 = routes(span, area, 4)
        assert np.isclose(b0 / a0, 1.123)
        assert np.allclose(routes(span, area, -4), (a4, b4))
        assert cost_per_m(0.02, span, area, 4, 0) < cost_per_m(0.02, span, area, -4, 0)
        print(name, "AR", span**2 / area, "WL N/m2", 0.02*G/area,
              "calm A/B J", (a0,b0), "wind A/B J", (a4,b4))
    assert routes(*morphs["broad"], 4)[0] > routes(*morphs["broad"], 4)[1]
    assert routes(*morphs["narrow"], 4)[0] < routes(*morphs["narrow"], 4)[1]
    for k, cd, profile in [(1, .05, .08), (1.2, .08, .12), (1.4, .12, .16)]:
        print("scenario", k, cd, profile,
              {name: routes(*m, 4, k, cd, profile) for name, m in morphs.items()})
    assert np.isinf(cost_per_m(.02, .27, .014, -20, 0))
    print("Synthetic sanity checks PASS; no biological source fitted.")


if __name__ == "__main__":
    main()
