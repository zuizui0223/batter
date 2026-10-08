#!/usr/bin/env python3
"""No bat data: 3D ear-tip separation non-identifiability witness.

A simultaneous rotation of both unit ear directions around the fixed
left/right head baseline preserves measured ear-tip distance exactly,
while changing their directions relative to prey ahead of the bat.
"""
import argparse
import json
import math

def vec(*x): return tuple(float(v) for v in x)
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def scale(s,a): return tuple(s*x for x in a)
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def norm(a): return math.sqrt(dot(a,a))
def unit(a): return scale(1/norm(a),a)
def rotate_x(a,t):
    x,y,z=a
    return (x,math.cos(t)*y-math.sin(t)*z,math.sin(t)*y+math.cos(t)*z)

def distance_and_gaze(uL,uR,angle,b=.025,length=.04,eye_dist=.075):
    left=vec(-b,0,0);right=vec(b,0,0)
    ul=rotate_x(uL,angle);ur=rotate_x(uR,angle)
    pl=add(left,scale(length,ul));pr=add(right,scale(length,ur))
    prey_forward=vec(0,1,0)
    return {
      "ear_tip_distance":norm(sub(pl,pr)),
      "distance_over_eye_dist":norm(sub(pl,pr))/eye_dist,
      "mean_forward_cosine":(dot(ul,prey_forward)+dot(ur,prey_forward))/2,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    opt=ap.parse_args()
    left=unit(vec(.2,.95,.24))
    right=unit(vec(-.1,.96,-.26))
    angles=[0,math.pi/4,math.pi/2,math.pi]
    observed=[distance_and_gaze(left,right,t) for t in angles]
    base=observed[0]["ear_tip_distance"]
    for z in observed:
        assert abs(z["ear_tip_distance"]-base)<1e-12
        assert abs(z["distance_over_eye_dist"]-observed[0]["distance_over_eye_dist"])<1e-12
    cosines=[z["mean_forward_cosine"] for z in observed]
    assert max(cosines)-min(cosines)>.8
    # Strongest case: two ears point exactly the same way, d=2b regardless.
    for vector in [vec(0,1,0),vec(0,0,1),vec(0,-1,0)]:
        z=distance_and_gaze(vector,vector,0)
        assert abs(z["ear_tip_distance"]-.05)<1e-12
    summary={
      "evidence_tier":"PURE_MATHEMATICAL_COUNTEREXAMPLE_NO_BAT_VALUES",
      "fixed_ear_bases_and_lengths":True,
      "tested_angles_radian":[float(a) for a in angles],
      "max_abs_distance_deviation":max(abs(z["ear_tip_distance"]-base) for z in observed),
      "gaze_cosine_span":max(cosines)-min(cosines),
      "identical_ear_directions_forward_up_backward_same_separation":True,
      "conclusion":"SCALAR_DISTANCE_CANNOT_IDENTIFY_HEAD_RELATIVE_3D_EAR_GAZE"
    }
    if opt.self_test: assert summary["gaze_cosine_span"]>.8
    print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
