import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
C=ROOT/"analysis/shared_template_individual_reweighting_contract_v4.json"
R=ROOT/"analysis/run_shared_template_individual_reweighting_v4.py"

def test_v4_is_explanatory_and_finite():
    p=json.loads(C.read_text())
    assert p["role"].startswith("post-v2/v3 explanatory")
    assert p["inherited"]["individual_count"]==8
    assert p["primary_test"]["null"].startswith("all 8!")

def test_v4_contains_no_individual_cell_residual_fit():
    p=json.loads(C.read_text())
    assert "No individual-by-cell residual is fitted" in p["model"]["reweighted_shared_template"]
    t=R.read_text()
    assert "ratio=p_i/species_marg" in t
    assert "p_cell*ratio" in t

def test_v4_uses_exact_permutation():
    assert "itertools.permutations" in R.read_text()
