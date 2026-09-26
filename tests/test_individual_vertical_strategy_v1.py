import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"analysis/individual_vertical_strategy_contract_v1.json"
RUNNER=ROOT/"analysis/run_individual_vertical_strategy_v1.py"

def test_contract_keeps_original_geometry():
    p=json.loads(CONTRACT.read_text())
    assert p["frozen_geometry"]["cell_size_m"]==5000
    assert len(p["frozen_geometry"]["eligible_cells"])==18
    assert p["frozen_geometry"]["z_edges_m"]==["-inf",0,50,100,200,400,800,1600,3200,"inf"]

def test_primary_replication_unit_is_individual():
    p=json.loads(CONTRACT.read_text())
    assert p["source"]["expected_individuals"]==8
    assert p["primary_test"]["null"].startswith("Enumerate all 8!")

def test_followup_does_not_rewrite_odsp_result():
    p=json.loads(CONTRACT.read_text())
    assert p["relationship_to_odsp"]["original_claim_unchanged"] is True
    assert p["relationship_to_odsp"]["purpose"].startswith("mechanism follow-up")

def test_runner_uses_exact_permutation_not_event_bootstrap():
    t=RUNNER.read_text()
    assert "itertools.permutations" in t
    assert "bootstrap" not in t.lower()
