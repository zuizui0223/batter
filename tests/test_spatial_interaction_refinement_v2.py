import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
C=ROOT/"analysis/spatial_interaction_refinement_contract_v2.json"
R=ROOT/"analysis/run_spatial_interaction_refinement_v2.py"

def test_v2_controls_marginal_identity_before_cell_interaction():
    p=json.loads(C.read_text())
    assert "marginal altitude preference" in p["models"]["marginal_adjusted_cell_baseline"]
    assert "individual-by-cell interaction" in p["models"]["marginal_adjusted_cell_baseline"]
    assert "raw early individual-cell z counts" in p["models"]["individual_spatial_model"]

def test_v2_inherits_geometry_and_split():
    p=json.loads(C.read_text())
    assert p["inherited_without_change"]["geometry"]=="same 18 frozen 5-km cells"
    assert p["inherited_without_change"]["primary_lambda"]==20
    assert p["inherited_without_change"]["sensitivity_lambdas"]==[5,50]

def test_v2_uses_exact_identity_permutation():
    t=R.read_text()
    assert "itertools.permutations" in t
    assert "full[source][cell][z]" in t
    assert "additive[source][cell][z]" in t
