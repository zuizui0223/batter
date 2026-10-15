#!/usr/bin/env python3
"""Static integrity gates for recovered original JAE source-native 3D geometry.

No GPS/DEM downloads, no new permutation tests, no claim of full environment
reproduction. Historical git-blob identity and source numeric results only.
"""
from __future__ import annotations
import ast
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
HIST=ROOT/"source_recovery/native_3d_history"
FIG=ROOT/"figures"
EXPECTED_GIT_BLOBS={
    "run_v1.py":"c08b442f97940eac3e90c1dac6e2de6d26010a7a",
    "contract_v1.json":"5c76d0432e53ea7733216245f229d68ae0df1f77",
    "run_external_geometry_v1.py":"c869a25c062b4bf5dc6b22e9f3e7fe03b69aeb30",
    "external_geometry_prediction_contract_v1.json":"e1047891ab37cd0b46cdd180cc7ed8d815abce4b",
}
NATIVE_BLOB="c1d37e42f72f59e5aba364daec9aef68b47778b6"
PANELS=["hypsignathus","phyllostomus_2022","phyllostomus_2023","phyllostomus_2016"]
EXPECTED_N=[8,5,6,9]
EXPECTED_SELF_XY=[.6187422837390575,.5493468569237422,.5465753800608059,.5105938420819637]
EXPECTED_OTHER_XY=[.3215600695671048,.3335654919163828,.2023187964434353,.20845026693562593]
EXPECTED_SELF_XYZ=[.5232789358742741,.5069866079258492,.5082630726980524,.42474161023256096]
EXPECTED_OTHER_XYZ=[.24046372261209492,.3088975402419429,.18964588802509272,.1806775859842606]
EXPECTED_S_NATIVE=[.10294924187835525,-.01659723395425109,-.003922999202991634,.1304000459741923]
EXPECTED_TERRAIN=[-.015806072455978037,-.008957479208159966,.016261860368360782,.028895449115765665]

def git_blob(data:bytes)->str:
    blob=b"blob "+str(len(data)).encode()+b"\x00"+data
    return hashlib.sha1(blob).hexdigest()

def close(actual:float,expected:float,name:str)->None:
    assert math.isclose(actual,expected,abs_tol=1e-11,rel_tol=0),(name,actual,expected)

def archive_gate()->None:
    for fn,sha in EXPECTED_GIT_BLOBS.items():
        data=(HIST/fn).read_bytes()
        assert git_blob(data)==sha,(fn,git_blob(data),sha)
        if fn.endswith(".py"):
            ast.parse(data.decode("utf8"),filename=fn)
        else:
            json.loads(data.decode("utf8"))
    native=(FIG/"ORIGINAL_NATIVE_3D_OVERLAP_SUMMARY_V1.json").read_bytes()
    assert git_blob(native)==NATIVE_BLOB
    runner=(HIST/"run_v1.py").read_text("utf8")
    assert "r3d = 1.0 - (oxyz / oxy)" in runner
    assert 'METRICS = ("oxy", "oxyz", "ozxy", "l3d", "r3d")' in runner
    internal=ROOT.parent.parent/"post_freeze_extensions/3d_niche_partition/run_original_terrain_geometry_v1.py"
    # This original historical runner may be missing from a stripped merge
    # checkout. The source recovery audit, not this guard, records missing rc2
    # immediate imports; do not pretend the whole original pipeline was rerun.
    print("PASS four exact historical source-code/contract Git blobs + native summary")

def source_gate()->None:
    d=json.loads((FIG/"ORIGINAL_NATIVE_3D_OVERLAP_SUMMARY_V1.json").read_text("utf8"))
    assert d["study_id"]=="batter-3d-niche-partition-v1"
    assert d["workflow"]["run_id"]==36881187913
    assert d["workflow"]["head_sha"]=="676ae76aec952a38410766577d51c5eca438a6c1"
    assert d["panels"]["tadarida"]["eligible_individuals"]==4
    assert d["panels"]["tadarida"]["structural_gate"] is False
    assert d["panels"]["eidolon"]["eligible_individuals"]==0
    assert d["panels"]["eidolon"]["structural_gate"] is False
    for idx,panel in enumerate(PANELS):
        r=d["panels"][panel]
        assert r["eligible_individuals"]==EXPECTED_N[idx]
        assert r["supported"] is True and 0<r["p_upper"]<=.05
        for field,values in [
            ("self_oxy",EXPECTED_SELF_XY),("other_oxy",EXPECTED_OTHER_XY),
            ("self_oxyz",EXPECTED_SELF_XYZ),("other_oxyz",EXPECTED_OTHER_XYZ)
        ]:close(r[field],values[idx],panel+" "+field)
        assert 0<r["self_oxyz"]<=r["self_oxy"]<=1
        assert 0<r["other_oxyz"]<=r["other_oxy"]<=1
        close(r["other_r3d"]-r["self_r3d"],EXPECTED_S_NATIVE[idx],panel+" S_native")
        assert 0<=r["self_r3d"]<=1 and 0<=r["other_r3d"]<=1
        assert r["self_oxy"]>r["other_oxy"]
        assert r["self_ozxy"]>r["other_ozxy"]
    assert git_blob((FIG/"ORIGINAL_TERRAIN_RELATIVE_3D_SOURCE_V1.json").read_bytes())=="08631a0dce61cc47e12b2d32642c46b5759fe872"
    assert git_blob((FIG/"ORIGINAL_TERRAIN_PARTITIONING_CALIBRATION_V1.json").read_bytes())=="e969698e2a594d2eeca2631d7473e598a8a8f371"
    terrain_source=json.loads((FIG/"ORIGINAL_TERRAIN_RELATIVE_3D_SOURCE_V1.json").read_text("utf8"))
    terrain_cal=json.loads((FIG/"ORIGINAL_TERRAIN_PARTITIONING_CALIBRATION_V1.json").read_text("utf8"))
    assert terrain_source["workflow"]["run_id"]==36946126004
    for idx,key in enumerate(PANELS):
        close(terrain_source["panels"][key]["S_rel"],EXPECTED_TERRAIN[idx],key+" exact source terrain")
        assert terrain_source["panels"][key]["supported"] is True
        assert abs(terrain_cal["panels"][key]["S_rel"]-EXPECTED_TERRAIN[idx])<.0001
    frozen=json.loads((FIG/"FROZEN_FIGURE_DATA_V1.json").read_text("utf8"))
    terrain=frozen["terrain"]
    assert [x["panel"] for x in terrain]==PANELS
    for row,value in zip(terrain,EXPECTED_TERRAIN):
        assert abs(row["s_rel"]-value)<.0001,(row["panel"],row["s_rel"],value), "Figure summary intentionally rounded"
        assert row["v_supported"] is True
    assert not any(r["s_rel"]>0 and r["s_p_two_sided"]<=.05 for r in terrain)
    assert sum(bool(r["couse_supported"]) for r in terrain)==1
    print("PASS original 500-m direct 3D probability overlap, 4/4 conditional source identity, 0/4 positive terrain S_rel")

def figure_and_text_gate()->None:
    svg=(FIG/"FIGURE_S2_NATIVE_HORIZONTAL_AND_JOINT_3D_OVERLAP_V1.svg").read_text("utf8")
    root=ET.fromstring(svg)
    assert root.tag=="{http://www.w3.org/2000/svg}svg"
    assert "177mm"==root.attrib["width"] and "140mm"==root.attrib["height"]
    for token in ["O_XY","O_XYZ","0.322 / 0.240","0.334 / 0.309","0.202 / 0.190","0.208 / 0.181","not CIs or p-values"]:
        assert token.lower() in svg.lower(),("Missing Figure S2 term",token)
    si=(ROOT/"SUPPORTING_INFORMATION_DRAFT_V1.md").read_text("utf8")
    asi=(ROOT/"SUPPORTING_INFORMATION_ANONYMOUS_DRAFT_V1.md").read_text("utf8")
    main=(ROOT/"INTEGRATED_MANUSCRIPT_V1.md").read_text("utf8")
    anon=(ROOT/"COMPLETE_ANONYMOUS_TEXT_DRAFT_V1.md").read_text("utf8")
    for item,txt,chapter in [(si,"internal","U"),(asi,"anonymous","S")]:
        for anchor in ["Supplementary Table "+chapter+"10.","Supplementary Methods "+chapter+"15.","Supplementary Figure S2"]:
            assert anchor in item,(txt,anchor)
    for msg,t in [(main,"main"),(anon,"anonymous")]:
        for k in ["between-individual **O_XY** values were 0.322","0.309","0.190","0.181",
                  "joint-gridded **O_XYZ**","not yet corrected for terrain"]:
            assert k.lower() in msg.lower(),(t,k)
    assert "source-closure" in si.lower()
    assert "source-closure" in main.lower() or "source-recovered" in main.lower()
    for secret in ["zuizui0223","release/jae","prospective/public-causal-synthesis"]:
        assert secret not in asi and secret not in anon,("identity leaked to anonymous scientific text",secret)
    print("PASS Figure S2 original-source semantics and blinded main/SI source quantities")

if __name__=="__main__":
    archive_gate()
    source_gate()
    figure_and_text_gate()
