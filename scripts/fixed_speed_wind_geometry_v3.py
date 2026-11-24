"""Analytic 2D fixed-airspeed, uniform-wind, direct roundtrip benchmark.
Not a field estimate or free-speed optimum. Wind must be slower than airspeed.
"""
import json
import pathlib
import numpy as np


def analytic_axes(u,w):
    if not np.isfinite([u,w]).all() or not 0 <= w < u:
        raise ValueError("require 0 <= wind < fixed airspeed")
    a=1-(w/u)**2
    return a, np.sqrt(a), a**1.5


def numerical_check(u,w):
    # Forward and backward ground velocities from crosswind compensation.
    theta=np.linspace(0,2*np.pi,100001)
    forward=np.sqrt(u*u-(w*np.sin(theta))**2)+w*np.cos(theta)
    reverse=np.sqrt(u*u-(w*np.sin(theta))**2)-w*np.cos(theta)
    radial=2/(u*(1/forward+1/reverse))
    a,b,area=analytic_axes(u,w)
    predicted=1/np.sqrt(np.cos(theta)**2/a**2+np.sin(theta)**2/b**2)
    integrated=np.trapezoid(radial**2,theta)/(2*np.pi)
    assert np.allclose(radial,predicted,atol=1e-10,rtol=1e-10)
    assert np.isclose(integrated,area,rtol=1e-10)
    return {"airspeed_m_s":u,"wind_m_s":w,"along_radius_fraction":a,
            "cross_radius_fraction":b,"area_fraction":area,
            "numeric_area_fraction":integrated,
            "max_radial_error":float(np.max(np.abs(radial-predicted)))}


def main():
    rows=[numerical_check(u,w) for u in (5,7,9) for w in (0,2,4)]
    for u,w in [(0,0),(5,5),(5,-1),(5,6)]:
        try: analytic_axes(u,w)
        except ValueError: continue
        raise AssertionError("invalid input was admitted")
    result={"scope":"analytical_and_numerical_benchmark_not_empirical",
            "assumptions":"2D uniform steady wind, same fixed airspeed and constant positive power outbound and return, straight routes, fixed energy budget, no turning cost, no obstacles",
            "rows":rows}
    p=pathlib.Path("results/fixed_speed_wind_geometry_v3.json")
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2)+"\n")
    print(p.read_text())


if __name__=="__main__": main()
