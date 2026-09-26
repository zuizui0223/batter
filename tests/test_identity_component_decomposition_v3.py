import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
C=ROOT/"analysis/identity_component_decomposition_contract_v3.json"
R=ROOT/"analysis/run_identity_component_decomposition_v3.py"

def test_two_components_are_frozen():
    p=json.loads(C.read_text())
    assert set(p["components"])=={"altitude_identity","horizontal_identity","location_specific_vertical_interaction"}
    assert p["inherited"]["primary_lambda"]==20

def test_v3_does_not_retest_v2_interaction():
    t=R.read_text()
    assert 'V2=ROOT/"results/spatial_interaction_refinement_result_v2.json"' in t
    assert 'bool(v2["primary"]["primary_pass"])' in t
