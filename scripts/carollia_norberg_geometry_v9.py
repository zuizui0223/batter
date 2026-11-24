"""Analytical and numerical diagnostic, no new individual outcome data.
Carneiro et al. 2023 PowFlight.R exact verified MD5
00c6f7a1ea6806944b7d58baa361ab0f; SI units, original speed support 2–7 m/s.
"""
import json, pathlib, math
import numpy as np

def coefficients(m,b,S):
    return 2.4*(m*9.8)**2/(1.205*math.pi*b*b), .5*1.205*(S*.02+.00285*m**(2/3))

def curve(m,b,S,u):
    a,d=coefficients(m,b,S)
    return a/u+d*u**3

def run():
    u=np.linspace(5,7,41)
    m,b,S=.0088,.23,.0077
    ref=.176/u+9.21e-5*u**3+.0297
    old=2*1.2*(m*9.81)**2/(1.2*math.pi*b*b)/u+.5*1.2*S*.08*u**3
    new=curve(m,b,S,u)
    def metrics(p):
        return dict(MAE=float(np.mean(abs(p-ref))),bias=float(np.mean(p-ref)),RMSE=float(np.sqrt(np.mean((p-ref)**2))))
    # Fixed mass and area, varying span: calm-optimal range speed ∝ span^-1/2,
    # calm radius ∝ span. Fixed-speed absolute area proportional to
    # t^2*(1-t)^1.5 for t=(wind/calm_optimal_speed)^2 in (0,1).
    # Its maximum t=4/7; not a result about optimal free-speed routes.
    t=np.linspace(.0001,.9999,9999)
    f=t*t*(1-t)**1.5
    assert abs(t[np.argmax(f)]-4/7)<.00011
    # With a common feasible speed set, increasing span lowers A/u pointwise
    # and leaves B unchanged. Thus min(P/g) cannot increase for any heading.
    # Numerical demonstration of this dominance, not biological feasibility.
    speeds=np.linspace(5,7,2001)
    w=4
    theta=np.linspace(0,2*np.pi,361)
    def radius(span):
        p=curve(m,span,S,speeds)
        out=[]
        for ang in theta:
            q=w*np.sin(ang);along=w*np.cos(ang)
            g=np.sqrt(speeds**2-q*q)
            out.append(1/(np.min(p/(g+along))+np.min(p/(g-along))))
        return np.array(out)
    r1,r2=radius(b),radius(b*1.2)
    assert np.all(r2>=r1)
    result={"scope":"published_formula_replay_and_conditional_math_only",
        "common_speed_band_m_s":[5,7],"reference":"Currie 2023 displayed Eq 2.2, not raw observations",
        "norberg":metrics(new),"V5_reduced":metrics(old),
        "fixed_speed_turning_point_beta_squared":4/7,
        "optimized_span_dominance":{"span_multiplier":1.2,"min_radius_ratio":float(np.min(r2/r1)),"max_radius_ratio":float(np.max(r2/r1))}}
    p=pathlib.Path("results/carollia_norberg_geometry_v9.json")
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2)+"\n");print(p.read_text())
if __name__=="__main__":run()
