#!/usr/bin/env python3
"""Self-tests for the solution-repertoire restricted randomization design."""

from pathlib import Path
import importlib.util
import tempfile
import subprocess
import csv
import sys

HERE = Path(__file__).resolve().parent


def load_module(filename, name):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


inf = load_module("randomization_inference_reference_v1.py", "randinf")


def fake_rows(n_blocks):
    rows = []
    for b in range(1, n_blocks + 1):
        rows.extend([
            {"block": b, "animal_id": f"B{b:02d}_A1", "acquisition_start_family": "A"},
            {"block": b, "animal_id": f"B{b:02d}_A2", "acquisition_start_family": "A"},
            {"block": b, "animal_id": f"B{b:02d}_B1", "acquisition_start_family": "B"},
            {"block": b, "animal_id": f"B{b:02d}_B2", "acquisition_start_family": "B"},
        ])
    return rows


def test_assignment_counts():
    for blocks, expected in [(4, 256), (5, 1024), (6, 4096)]:
        assignments = list(inf.enumerate_treatment_assignments(fake_rows(blocks)))
        assert len(assignments) == expected, (blocks, len(assignments), expected)
        assert len({tuple(sorted(x.items())) for x in assignments}) == expected


def test_block_balance():
    rows = fake_rows(4)
    assignments = list(inf.enumerate_treatment_assignments(rows))
    row_by_id = {r["animal_id"]: r for r in rows}

    for assignment in assignments:
        for block in range(1, 5):
            block_ids = [r["animal_id"] for r in rows if r["block"] == block]
            assert sum(assignment[i] == "A" for i in block_ids) == 2
            assert sum(assignment[i] == "B" for i in block_ids) == 2

            for start in ("A", "B"):
                ids = [
                    i for i in block_ids
                    if row_by_id[i]["acquisition_start_family"] == start
                ]
                assert len(ids) == 2
                assert sorted(assignment[i] for i in ids) == ["A", "B"]


def test_delta_orientation():
    rows = fake_rows(4)
    observed = next(inf.enumerate_treatment_assignments(rows))

    scores = {}
    for row in rows:
        animal = row["animal_id"]
        open_family = observed[animal]
        other = "B" if open_family == "A" else "A"
        scores[(animal, open_family)] = 2.0
        scores[(animal, other)] = 0.0

    delta = inf.delta_a(scores, observed)
    assert abs(delta - 2.0) < 1e-12

    obs, p, n = inf.exact_one_sided_p(rows, scores, observed)
    assert abs(obs - 2.0) < 1e-12
    assert n == 256
    assert 0 < p <= 0.05, p


def run_schedule(ids):
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        ids_path = td / "ids.txt"
        out_path = td / "schedule.csv"
        ids_path.write_text("\n".join(ids) + "\n")

        subprocess.run(
            [
                sys.executable,
                str(HERE / "randomization_schedule_v1.py"),
                "--ids",
                str(ids_path),
                "--out",
                str(out_path),
            ],
            check=True,
        )
        with out_path.open(newline="") as fh:
            return list(csv.DictReader(fh))


def test_schedule_reproducibility_and_append_only():
    ids16 = [f"BAT{i:02d}" for i in range(1, 17)]
    ids20 = ids16 + [f"BAT{i:02d}" for i in range(17, 21)]

    first = run_schedule(ids16)
    second = run_schedule(ids16)
    assert first == second

    extended = run_schedule(ids20)
    assert extended[:16] == first
    assert [int(r["block"]) for r in extended[16:]] == [5, 5, 5, 5]


def test_schedule_rejects_invalid_n():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        ids_path = td / "ids.txt"
        out_path = td / "schedule.csv"
        ids_path.write_text("\n".join(f"BAT{i:02d}" for i in range(1, 15)) + "\n")

        proc = subprocess.run(
            [
                sys.executable,
                str(HERE / "randomization_schedule_v1.py"),
                "--ids",
                str(ids_path),
                "--out",
                str(out_path),
            ],
            capture_output=True,
            text=True,
        )
        assert proc.returncode != 0


if __name__ == "__main__":
    tests = [
        test_assignment_counts,
        test_block_balance,
        test_delta_orientation,
        test_schedule_reproducibility_and_append_only,
        test_schedule_rejects_invalid_n,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"PASS all {len(tests)} randomization-design tests")
