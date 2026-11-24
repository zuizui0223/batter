"""Published-fit scenario: Currie et al. 2023 eqs 2.2 and 2.4.
Not raw observations, independent validation, or observed patch choice.
Bound both curves to the shared 5–9 m/s speed band shown in Fig. 3.
"""
import json
import pathlib
import numpy as np

COEFFICIENTS = {"mechanical": (.176, 9.21e-5, .0297),
                "metabolic": (2.52, 3.73e-4, .490)}
SPEED = np.linspace(5., 9., 40001)


def minimum_cost(coefficients, parallel, cross, u=SPEED):
    a, b, c = coefficients
    power = a/u + b*u**3 + c
    ground = parallel + np.sqrt(np.maximum(0., u*u-cross*cross))
    valid = (u >= abs(cross)) & (ground > 0)
    if not valid.any():
        return {"J_per_m": None, "airspeed": None, "boundary": False}
    cost = np.full_like(u, np.inf)
    cost[valid] = power[valid]/ground[valid]
    j = int(np.argmin(cost))
    return {"J_per_m": float(cost[j]), "airspeed": float(u[j]),
            "boundary": bool(j in (0,len(u)-1))}


def scenario(coefficients, wind):
    out, back, cross = [minimum_cost(coefficients,p,q)
                        for p,q in [(wind,0),(-wind,0),(0,wind)]]
    along = 1000*(out["J_per_m"]+back["J_per_m"])
    perpendicular = 2000*cross["J_per_m"]
    return {"along_1km_J": along, "cross_1km_J": perpendicular,
            "critical_distance_ratio_B_to_A": along/perpendicular,
            "cross_1100m_J": perpendicular*1.1,
            "outbound": out, "return": back, "cross": cross}


def main():
    result = {"source":"https://doi.org/10.1098/rspb.2023.0045",
              "equations":["2.2", "2.4"], "speed_band_m_s":[5,9],
              "scope":"published_fit_illustration_not_field_validation",
              "coefficients_A_B_C":COEFFICIENTS,
              "wind_scenarios":{str(w):{k:scenario(c,w) for k,c in COEFFICIENTS.items()}
                                for w in range(5)}}
    for k,c in COEFFICIENTS.items():
        assert abs(scenario(c,0)["critical_distance_ratio_B_to_A"]-1)<1e-12
        assert abs(scenario(c,4)["along_1km_J"]-scenario(c,-4)["along_1km_J"])<1e-10
    a=result["wind_scenarios"]["4"]
    assert a["mechanical"]["along_1km_J"] < a["mechanical"]["cross_1100m_J"]
    assert a["metabolic"]["along_1km_J"] > a["metabolic"]["cross_1100m_J"]
    # Independent algebra diagnostic: do not silently adopt published optimum labels
    # if the displayed rounded coefficients give different derivative roots.
    u=np.linspace(3,16,130001)
    result["unbounded_equation_diagnostic"]={}
    for key,(a,b,c) in COEFFICIENTS.items():
        p=a/u+b*u**3+c
        result["unbounded_equation_diagnostic"][key]={
          "minimum_power_m_s":float(u[np.argmin(p)]),
          "minimum_P_over_u_m_s":float(u[np.argmin(p/u)]),
          "warning":"Unconstrained extrapolation diagnostic only; not admitted as physical prediction."}
    path=pathlib.Path("results/currie_published_curve_roundtrip_v1.json")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
