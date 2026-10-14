#!/usr/bin/env python3
"""Guard interpretation of previously completed JAE stress tests and a pure math example.

This validation opens NO new animal records or statistical test families.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

HERE=Path(__file__).resolve().parent
WILD=json.loads((HERE/"figures/FROZEN_FIGURE_DATA_V1.json").read_text())
BOUNDARY=json.loads((HERE/"figures/FROZEN_MAINTENANCE_BOUNDARY_INPUTS_V1.json").read_text())
NAMES=["hypsignathus","phyllostomus_2022","phyllostomus_2023","phyllostomus_2016"]

def close(a,b,label):
    assert math.isclose(float(a),float(b),rel_tol=0,abs_tol=1e-9),(label,a,b)

def source_checks():
    assert BOUNDARY["source_branch"]=="release/jae-v0.4.0-rc2"
    families=BOUNDARY["families"]
    assert len(families)==7
    for key in families:
        record=families[key]
        assert record["source_path"].endswith(".json")
        assert len(record["source_blob_sha"])==40
        assert record["source_workflow_run"] is not None
        assert record["source_result"]["schema_version"] >= 1
    fine=families["fine500"]["source_result"]
    assert fine["fine_grid_m"]==500 and fine["pass_count"]==4
    assert fine["independent_confirmation"] is False
    assert list(fine["panels"])==NAMES
    p500=[(19,0.38400231972735227,0.0002),
          (23,0.08675910017357275,0.0002),
          (11,0.10152641549492719,0.0006),
          (9,0.4514183752230124,0.0286)]
    for panel,(n,e,p) in zip(NAMES,p500):
        row=fine["panels"][panel]
        assert row["pass"] is True and row["n"]==n
        close(row["calibrated_excess"],e,panel+" 500m score")
        close(row["p"],p,panel+" 500m p")
    night=families["same_night"]["source_result"]
    assert night["pass_count"]==3 and night["panel_count"]==4
    for idx,panel in enumerate(NAMES):
        assert night["panels"][panel]["pass"] is (idx<3)
    close(night["panels"][NAMES[3]]["p"],0.0544,"2016 unresolved")
    for name,lag,count in [("lag1",1,4),("lag3",3,3),("lag7",7,2)]:
        info=families[name]["source_result"]
        assert info["minimum_self_lag_days"]==lag
        assert info["pass_count"]==count
        assert len(info["panels"])==count
        assert all(x["pass"] for x in info["panels"].values())
    wind=families["wind_structural"]["source_result"]
    assert wind["vertical_outcome_may_open"] is False
    assert wind["decision"]=="STOP"
    assert wind["panels"]["phyllostomus_2023"]["evaluable_n"]==7
    assert wind["panels"]["phyllostomus_2023"]["required_n"]==8
    assert families["wind_preflight"]["source_result"]["vertical_numeric_opened"] is False
    geo=WILD["terrain"]
    assert len(geo)==4 and all(z["v_supported"] for z in geo)
    assert sum(z["s_rel"]>0 and z["s_p_two_sided"]<=0.05 for z in geo)==0
    assert sum(z["couse_supported"] for z in geo)==1
    assert geo[2]["couse_supported"] is True
    assert [z["couse_tolerance_s"] for z in geo]==[60,60,600,600]
    assert [z["couse_scope"] for z in geo]==[
        "endpoint_excluded","endpoint_excluded","all_space","endpoint_excluded"]
    print("PASS previously completed JAE fine-place, same-night, lag, wind STOP and geometry boundaries")

def pure_mathematical_counterexample():
    # These are pedagogical invented probability vectors and NOT wild bat records.
    pA=[0.6,0.4];pB=[0.4,0.6]
    shared_q=[[0.8,0.2],[0.2,0.8]]
    def marginal(pi,conditionals):
        return [sum(pi[k]*conditionals[k][z] for k in range(len(pi))) for z in range(2)]
    A_alloc=marginal([2/3,1/3],shared_q)
    B_alloc=marginal([1/3,2/3],shared_q)
    A_within=marginal([0.5,0.5],[[0.7,0.3],[0.5,0.5]])
    B_within=marginal([0.5,0.5],[[0.5,0.5],[0.3,0.7]])
    for x,target in [(A_alloc,pA),(B_alloc,pB),(A_within,pA),(B_within,pB)]:
        for a,b in zip(x,target):close(a,b,"theoretical mixture")
        close(sum(x),1,"synthetic normalisation")
    overlap=sum(min(a,b) for a,b in zip(pA,pB))
    kl=sum(a*math.log(a/b) for a,b in zip(pA,pB))
    close(overlap,0.8,"synthetic overlap")
    close(kl,0.08109302162163282,"synthetic KL")
    print("PASS two distinct latent decompositions with identical marginal probabilities; overlap=.8, KL=.081093")

def projection_nonidentifiability_counterexample():
    """Mathematical example only, never the GPS source outcome."""
    # Each list is p(z) at one horizontal cell. Both bats fly only at z=0,
    # but in different cells, yielding identical height marginals and
    # mutually exclusive true joint x/y/z support.
    a=[[1.0,0.0],[0.0,0.0]]
    b=[[0.0,0.0],[1.0,0.0]]
    overlap_3d=sum(min(x,y) for row_a,row_b in zip(a,b) for x,y in zip(row_a,row_b))
    z_a=[sum(row[z] for row in a) for z in range(2)]
    z_b=[sum(row[z] for row in b) for z in range(2)]
    overlap_vertical=sum(min(x,y) for x,y in zip(z_a,z_b))
    close(overlap_3d,0.0,"synthetic true joint overlap")
    close(overlap_vertical,1.0,"synthetic shared vertical-marginal overlap")
    assert overlap_3d<=overlap_vertical
    print("PASS pure math: identical vertical marginals (O=1) with disjoint joint 3D cells (O=0)")

def text_bounds():
    manuscript=(HERE/"INTEGRATED_MANUSCRIPT_V1.md").read_text()
    anon=(HERE/"COMPLETE_ANONYMOUS_TEXT_DRAFT_V1.md").read_text()
    for source,name in [("SUPPORTING_INFORMATION_DRAFT_V1.md","U12"),("SUPPORTING_INFORMATION_ANONYMOUS_DRAFT_V1.md","S12")]:
        si=(HERE/source).read_text()
        for token in ["Supplementary Methods "+name,"0.3840","0.0868","0.1015","0.4514",
                      "0.0544","0.081093","0.8","not data from any animal","post-outcome"]:
            assert token.lower() in si.lower(),(source,token)
    for table,section in [("SUPPORTING_INFORMATION_DRAFT_V1.md","U13"),("SUPPORTING_INFORMATION_ANONYMOUS_DRAFT_V1.md","S13")]:
        content=(HERE/table).read_text()
        assert "Projection inequality" in content and "Supplementary Methods "+section in content
        assert "their reported O" in content.lower() or "their reported o" in content.lower()
    for doc in [manuscript,anon]:
        assert "marginal-height overlap 1 and joint spatial overlap 0" in doc
    for token in ["500-m horizontal cells","+0.384","p = 0.0006","identifiability problem",
                  "different task proportions", "not a formal equivalence proof"]:
        assert token.lower() in manuscript.lower(),("Manuscript mechanism boundary missing",token)
    # Historical priority is limited: overlapping persistent niches were already
    # demonstrated outside this bat analysis.
    assert "Carlson et al. 2021" in manuscript and "Carlson et al. 2021" in anon
    for token in ["10.1038/s41467-021-24826-x","Nature Communications",
                  "37 scholarly entries"]:
        assert token in manuscript,("Earlier ecology reference/priority missing",token)
    assert "10.1038/s41467-021-24826-x" in anon
    assert "10.1371/journal.pone.0313782" in manuscript and "10.1371/journal.pone.0313782" in anon
    assert "not opposing estimates of the same ecological quantity" in manuscript
    assert "The novelty is **not**" in manuscript
    assert "Supplementary Methods S12" in anon
    assert "An observed individual vertical-use distribution" in anon
    for secret in ["zuizui0223","release/jae","prospective/public-causal-synthesis"]:
        assert secret not in anon,("anonymous body identity leak",secret)
    print("PASS ecological mechanism text and evidence tiers retained in both manuscripts and SI")

if __name__=="__main__":
    source_checks()
    pure_mathematical_counterexample()
    projection_nonidentifiability_counterexample()
    text_bounds()
