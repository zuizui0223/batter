import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
C=ROOT/"analysis/marginal_altitude_identity_contract_v3.json"
R=ROOT/"analysis/run_marginal_altitude_identity_v3.py"

def test_v3_is_explicitly_explanatory():
    p=json.loads(C.read_text())
    assert p["role"].startswith("post-v2 explanatory")
    assert p["inherited"]["individual_count"]==8
    assert p["primary_test"]["null"].startswith("all 8!")

def test_v3_tests_only_marginal_altitude():
    t=R.read_text()
    assert "source_by_target_marginal_gain_matrix" in t
    assert "cell" not in t.lower().split("def build",1)[1].split("def score",1)[0]

def test_v3_uses_exact_permutation():
    assert "itertools.permutations" in R.read_text()
