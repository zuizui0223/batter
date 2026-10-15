#!/usr/bin/env python3
"""Exact native 3D V/S overlap coupling; only pinned summary bytes and synthetic samples.

Never reads original animal GPS/DEM, estimates new bat effects or reruns permutation tests.
"""
import hashlib
import json
import math
from pathlib import Path

HERE=Path(__file__).resolve().parent
SRC=HERE/"source_recovery"/"native_3d_history"
FIG=HERE/"figures"
PANELS=("hypsignathus","phyllostomus_2022","phyllostomus_2023","phyllostomus_2016")
BLOBS={
 FIG/"ORIGINAL_NATIVE_3D_OVERLAP_SUMMARY_V1.json":"c1d37e42f72f59e5aba364daec9aef68b47778b6",
 FIG/"ORIGINAL_TERRAIN_RELATIVE_3D_SOURCE_V1.json":"08631a0dce61cc47e12b2d32642c46b5759fe872",
 SRC/"run_v1.py":"c08b442f97940eac3e90c1dac6e2de6d26010a7a",
 SRC/"run_external_geometry_v1.py":"c869a25c062b4bf5dc6b22e9f3e7fe03b69aeb30",
 SRC/"contract_v1.json":"5c76d0432e53ea7733216245f229d68ae0df1f77",
}
def blob(path):
    a=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(a)).encode()+b"\0"+a).hexdigest()
def load(path):
    return json.loads(path.read_text(encoding="utf8"))
def eq(a,b,what):
    assert math.isclose(a,b,abs_tol=1e-12,rel_tol=0),(what,a,b)

def source_gate():
    for p,h in BLOBS.items():
        assert blob(p)==h,(p,"source drift")
    L=load(FIG/"NATIVE_3D_V_S_OVERLAP_SLACK_DECOMPOSITION_V1.json")
    N=load(FIG/"ORIGINAL_NATIVE_3D_OVERLAP_SUMMARY_V1.json")
    T=load(FIG/"ORIGINAL_TERRAIN_RELATIVE_3D_SOURCE_V1.json")
    C=load(SRC/"contract_v1.json")["preprocessing"]
    assert (L["schema_version"],L["source_panels"])==(1,list(PANELS))
    assert C["alpha"]==.5 and len(C["centered_height_edges_m"])-1==10
    assert C["pair_common_support_min_fixes_each"]==50
    assert N["workflow"]["run_id"]==36881187913 and T["workflow"]["run_id"]==36946126004
    assert L["source"]["native_summary_git_blob"]==BLOBS[FIG/"ORIGINAL_NATIVE_3D_OVERLAP_SUMMARY_V1.json"]
    assert L["source"]["terrain_summary_git_blob"]==BLOBS[FIG/"ORIGINAL_TERRAIN_RELATIVE_3D_SOURCE_V1.json"]
    assert L["source"]["native_pair_metric_source_git_blob"]==BLOBS[SRC/"run_v1.py"]
    assert L["source"]["terrain_pair_metric_source_git_blob"]==BLOBS[SRC/"run_external_geometry_v1.py"]
    assert list(L["panels"])==list(PANELS)
    for panel in PANELS:
        n,t,o=N["panels"][panel],T["panels"][panel],L["panels"][panel]
        assert n["supported"] and o["biological_n"]==n["eligible_individuals"]
        s=o["source_native_means"]
        for key,field in (("self_conditional_overlap","self_ozxy"),
                         ("other_conditional_overlap","other_ozxy"),
                         ("self_normalized_joint_overlap_loss","self_r3d"),
                         ("other_normalized_joint_overlap_loss","other_r3d")):
            eq(s[key],n[field],panel+key)
        V=n["self_ozxy"]-n["other_ozxy"]
        S=n["other_r3d"]-n["self_r3d"]
        Es=1-n["self_r3d"]-n["self_ozxy"]
        Eo=1-n["other_r3d"]-n["other_ozxy"]
        assert Es>=-1e-12 and Eo>Es
        eq(V,n["d_panel"],panel+" V")
        eq(o["source_native_conditional_fidelity_V"],V,panel+" ledger V")
        eq(o["source_native_added_segregation_S"],S,panel+" ledger S")
        for key,val in (("self_mean_E",Es),("other_mean_E",Eo),
                        ("other_minus_self_E",Eo-Es)):
            eq(o["source_native_overlap_slack"][key],val,panel+key)
        eq(V-S,Eo-Es,panel+" exact decomposition")
        eq(o["native_math_identity_check"]["V_minus_S"],V-S,panel+" gap")
        eq(o["native_math_identity_check"]["S_rebuilt_as_V_minus_gap"],S,panel+" rebuilt S")
        eq(t["V_native"],V,panel+" native V match")
        eq(t["S_native"],S,panel+" native S match")
        eq(o["source_terrain_relative"]["fidelity_V"],t["V_rel"],panel+" Vrel")
        eq(o["source_terrain_relative"]["segregation_S"],t["S_rel"],panel+" Srel")
        eq(o["source_terrain_relative"]["arithmetic_V_minus_S"],t["V_rel"]-t["S_rel"],panel+" terra gap")
    print("PASS exact native V-S = epsilon_other - epsilon_self in all 4 original panels; no new inferential test.")

def pair(A,B):
    """Invented session pair under source alpha=.5, 10 height bins, shared-fix >=50."""
    cells=set(A)&set(B)
    totals=lambda C:sum(map(sum,C.values()))
    assert sum(sum(A[c]) for c in cells)>=50
    assert sum(sum(B[c]) for c in cells)>=50
    assert all(len(x)==10 for x in list(A.values())+list(B.values()))
    px={c:sum(A[c])/totals(A) for c in A}
    py={c:sum(B[c])/totals(B) for c in B}
    oxy=sum(min(px[c],py[c]) for c in cells)
    assert oxy>0
    ozxy,oxyz=0.,0.
    for c in cells:
        a,b=px[c],py[c]
        q=lambda v:[(x+.5)/(sum(v)+5) for x in v]
        u,v=q(A[c]),q(B[c])
        assert sum(u)>0.99999 and sum(v)>0.99999
        ozxy+=(min(a,b)/oxy)*sum(min(x,y) for x,y in zip(u,v))
        oxyz+=sum(min(a*x,b*y) for x,y in zip(u,v))
    slack=oxyz/oxy-ozxy
    assert slack>=-1e-12 and oxyz<=oxy+1e-12
    eq(1-oxyz/oxy,1-ozxy-slack,"pair geometry")
    return oxy,oxyz,ozxy,slack

def synthetic_gate():
    v=lambda x,y:[x,y]+[0]*8
    A={0:v(80,10),1:v(10,0)}
    B={0:v(0,10),1:v(10,80)}
    _,_,own,_=pair(A,A)
    oxy,oxyz,other,slack=pair(A,B)
    eq(own,1,"same identity source estimator")
    eq(oxy,.2,"other XY")
    eq(oxyz,.2,"other XYZ")
    eq(other,.18596491228070167,"other conditional Z")
    eq(slack,.8140350877192983,"overlap slack")
    V=own-other
    S=1-oxyz/oxy
    assert V>.8 and abs(S)<1e-12
    print("SYNTHETIC ONLY: source-like conditional V≈0.814 while normalized added S≈0.")
    print("This two-animal toy is not an original n>=5 bat-panel analysis or evidence of no physical segregation.")

if __name__=="__main__":
    source_gate()
    synthetic_gate()
