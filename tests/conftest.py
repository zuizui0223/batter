"""Add repository-root scripts to the *test runner* import path.

The prospective original-source auditors live in `scripts/`, not inside
the installed `src/batter` package. The existing all-tests GitHub workflow
calls the standalone `pytest` command, where the repository root may not
be on sys.path. This is a test collection/packaging fix only; it does not
modify model scores, source data, frozen JAE code or scientific assumptions.
"""
from pathlib import Path
import sys

ROOT = str(Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
