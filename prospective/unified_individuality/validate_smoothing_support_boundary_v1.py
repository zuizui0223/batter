#!/usr/bin/env python3
"""Source-hash guarded synthetic-only audit of 500-m bat 3D overlap smoothing.

NO access to animal GPS events, downloaded DEM, source-generated overlap
matrices or new biological permutation outcomes. The examples are mathematical
counterexamples to interpreting estimated O_XYZ as raw observed co-use.
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "source_recovery" / "native_3d_history"
SHA = {
    "run_v1.py": "c08b442f97940eac3e90c1dac6e2de6d26010a7a",
    "run_external_geometry_v1.py": "c869a25c062b4bf5dc6b22e9f3e7fe03b69aeb30",
    "contract_v1.json": "5c76d0432e53ea7733216245f229d68ae0df1f77",
}


def git_blob(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()


def source_gate() -> tuple[float, int, int]:
    for name, expected in SHA.items():
        file = SRC / name
        assert git_blob(file) == expected, (name, "source Git blob changed")
        if name.endswith(".py"):
            ast.parse(file.read_text(encoding="utf-8"), filename=name)
    contract = json.loads((SRC / "contract_v1.json").read_text())
    cfg = contract["preprocessing"]
    alpha = float(cfg["alpha"])
    k = len(cfg["centered_height_edges_m"]) - 1
    min_shared = int(cfg["pair_common_support_min_fixes_each"])
    assert alpha == 0.5 and k == 10 and min_shared == 50
    native = (SRC / "run_v1.py").read_text()
    external = (SRC / "run_external_geometry_v1.py").read_text()
    # Independent source-code contract: full smoothing and pairwise test geometry.
    assert "(v.astype(float) + alpha) / (float(v.sum()) + alpha * k)" in native
    assert "(v.astype(float) + alpha) / (float(v.sum()) + alpha * K)" in external
    assert 'na = sum(a["cell_n"][c] for c in common)' in native
    assert 'nb = sum(b["cell_n"][c] for c in common)' in native
    assert "if na < min_common or nb < min_common:" in native
    assert 'for c in common:' in native
    print("PASS exact original Git source bytes, per-cell alpha=0.5 smoothing, ten height bins, pair-total shared-fix gate=50")
    return alpha, k, min_shared


def pz(counts: list[int], alpha: float) -> list[float]:
    K = len(counts)
    denom = sum(counts) + alpha * K
    assert denom > 0
    out = [(c + alpha) / denom for c in counts]
    assert math.isclose(sum(out), 1, abs_tol=1e-12)
    return out


def cvec(K: int, indices: list[int]) -> list[int]:
    out = [0] * K
    for index in indices:
        out[index] += 1
    return out


def source_like_pair(A: dict, B: dict, alpha: float, min_shared: int) -> dict:
    """Pure reimplementation of source's pair metrics, for invented inputs only."""
    ca, cb = set(A), set(B)
    na_tot = sum(sum(x) for x in A.values())
    nb_tot = sum(sum(x) for x in B.values())
    assert na_tot > 0 and nb_tot > 0
    common = ca & cb
    shared_a = sum(sum(A[c]) for c in common)
    shared_b = sum(sum(B[c]) for c in common)
    assert shared_a >= min_shared and shared_b >= min_shared
    pxy_a = {c: sum(v)/na_tot for c,v in A.items()}
    pxy_b = {c: sum(v)/nb_tot for c,v in B.items()}
    Oxy, Oxyz, Ozxy, raw = 0.0, 0.0, 0.0, 0.0
    for c in common:
        xa, xb = pxy_a[c], pxy_b[c]
        Oxy += min(xa, xb)
        pa, pb = pz(A[c], alpha), pz(B[c], alpha)
        Oxyz += sum(min(xa*u, xb*v) for u,v in zip(pa,pb))
        raw += min(xa,xb)*sum(min(u,v) for u,v in zip(pz(A[c],0),pz(B[c],0)))
    for c in common:
        w = min(pxy_a[c],pxy_b[c])/Oxy
        pa,pb = pz(A[c],alpha),pz(B[c],alpha)
        Ozxy += w*sum(min(u,v) for u,v in zip(pa,pb))
    assert Oxy > 0
    return {
        "shared_horizontal_cells": len(common),
        "shared_event_fixes_each": [shared_a, shared_b],
        "original_smoothing_alpha": alpha,
        "estimated_O_XY": Oxy,
        "estimated_smoothed_O_XYZ": Oxyz,
        "estimated_smoothed_O_Z_given_XY": Ozxy,
        "model_R_3D": 1.0-Oxyz/Oxy,
        "unsmoothed_sample_O_XYZ": raw,
    }


def test_math() -> None:
    alpha, K, gate = source_gate()
    # Per-session median-centered possible heights:
    # A: 25 events in bin 3 (~-75m) and 25 in bin 6 (~+75m)
    # B: 25 in bin 2 (~-150m) and 25 in bin 7 (~+150m).
    # No XY x Z cell has an observed common height bin.
    A_sparse = {i:cvec(K,[3 if i<25 else 6]) for i in range(50)}
    B_sparse = {i:cvec(K,[2 if i<25 else 7]) for i in range(50)}
    # Exactly the same total observations can instead be concentrated in one
    # horizontal cell: the fixed 50 shared-event gate still passes.
    A_dense = {0:cvec(K,[3]*25+[6]*25)}
    B_dense = {0:cvec(K,[2]*25+[7]*25)}
    for a,b,expected,label in [
        (A_sparse,B_sparse,5.0/6.0,"sparse 50 shared cells"),
        (A_dense,B_dense,1.0/11.0,"dense 1 shared cell"),
    ]:
        got = source_like_pair(a,b,alpha,gate)
        assert got["shared_event_fixes_each"] == [50,50]
        assert math.isclose(got["estimated_O_XY"],1,abs_tol=1e-12)
        assert math.isclose(got["unsmoothed_sample_O_XYZ"],0,abs_tol=1e-12)
        assert math.isclose(got["estimated_smoothed_O_XYZ"],expected,abs_tol=1e-12)
        assert math.isclose(got["estimated_smoothed_O_Z_given_XY"],expected,abs_tol=1e-12)
        assert 0 < got["model_R_3D"] < 1
        print("SYNTHETIC ONLY",label,got)
    print("PASS counterexamples: zero raw observed XY-height bin intersection can yield >0 smoothed 3D overlap")
    print("NOT A RESULT: no empirical bias size, significance change, confidence interval, ecology mechanism or raw-data sensitivity estimated")


if __name__ == "__main__":
    test_math()
