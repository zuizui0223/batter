#!/usr/bin/env python3
"""Build a sanitized anonymous analysis-review archive.

Requires git/network access so source files can be read from frozen source branches.
"""

from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import zipfile

from mirror_carollia_cc0_v1 import mirror_into as mirror_carollia_cc0

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BUILD = ROOT / "build" / "behavioral_ecology_review_archive_v1"
DIST = ROOT / "dist"
ZIP = DIST / "behavioral_ecology_anonymous_review_archive_v1.zip"

CURRENT_FILES = [
    "prospective/public_causal_synthesis/COMPLETE_ANONYMOUS_TEXT_V1.md",
    "prospective/public_causal_synthesis/EVIDENCE_MATRIX_V1.md",
    "prospective/public_causal_synthesis/MASTER_RESULTS_TABLE_V1.md",
    "prospective/public_causal_synthesis/MANUSCRIPT_NUMERICAL_AUDIT_V1.md",
    "prospective/public_causal_synthesis/SUPPLEMENTARY_MATERIAL_DRAFT_V1.md",
    "prospective/public_causal_synthesis/FIGURE_CAPTIONS_V1.md",
    "prospective/public_causal_synthesis/FIGURE_ALT_TEXT_V1.md",
    "prospective/public_causal_synthesis/plot_synthesis_figures_v1.py",
    "prospective/public_causal_synthesis/DATA_SOURCE_MANIFEST_V1.csv",
    "prospective/public_causal_synthesis/REVIEW_ARCHIVE_README_V1.md",
    "prospective/public_causal_synthesis/CAROLLIA_CC0_MIRROR_MANIFEST_V1.json",
    "prospective/public_causal_synthesis/mirror_carollia_cc0_v1.py",
    "figures/public_causal/FIGURE_1_CAUSAL_LAYERS_V1.svg",
    "figures/public_causal/FIGURE_2A_FIRST_FLIGHT_FORMATION_V1.svg",
    "figures/public_causal/FIGURE_2B_DEVELOPMENTAL_RANDOMIZATION_V1.svg",
    "figures/public_causal/FIGURE_3_ACUTE_PERTURBATION_IDENTITY_V1.svg",
    "figures/public_causal/FIGURE_4_PORTABILITY_AND_WILD_BOUNDARY_V1.svg",
]

SOURCE_GROUPS = {
    "harten_history": (
        "prospective/ontogenetic-path-dependence-v1",
        [
            "prospective/ontogenetic_path_dependence/SOURCE_B_SELF_HISTORY_ESTIMATOR_CONTRACT_V1.md",
            "prospective/ontogenetic_path_dependence/SOURCE_B_SELF_HISTORY_PRIMARY_RESULT_V1.md",
            "prospective/ontogenetic_path_dependence/source_b_self_history_outcome_from_bridge_v1.py",
            "prospective/ontogenetic_path_dependence/EARLY_SEED_VS_RECENT_HISTORY_DIAGNOSTIC_V1.md",
            "prospective/ontogenetic_path_dependence/early_seed_vs_recent_history_diagnostic_v1.py",
        ],
    ),
    "rachum_history_carrier": (
        "prospective/early-experience-history-carrier-v1",
        [
            "prospective/early_experience_history_carrier/NIGHTLY_STRATEGY_HISTORY_ESTIMATOR_CONTRACT_V1.md",
            "prospective/early_experience_history_carrier/NIGHTLY_STRATEGY_HISTORY_PRIMARY_RESULT_V1.md",
            "prospective/early_experience_history_carrier/nightly_strategy_history_primary_v1.py",
        ],
    ),
    "rachum_individualization": (
        "prospective/early-experience-specialization-v1",
        [
            "prospective/early_experience_specialization/PRIMARY_CONTRACT_V1.md",
            "prospective/early_experience_specialization/PRIMARY_RESULT_V1.json",
            "prospective/early_experience_specialization/run_primary_v1.py",
            "prospective/early_experience_specialization/STATE_REWRITING_SECONDARY_V1.md",
            "prospective/early_experience_specialization/STATE_REWRITING_SECONDARY_RESULT_V1.json",
            "prospective/early_experience_specialization/run_state_rewriting_secondary_v1.py",
        ],
    ),
    "auditory_feedback": (
        "prospective/auditory-feedback-individualization-v1",
        [
            "prospective/auditory_feedback_individualization/PRIMARY_INDIVIDUALIZATION_CONTRACT_V1.md",
            "prospective/auditory_feedback_individualization/PRIMARY_RESULT_V1.json",
            "prospective/auditory_feedback_individualization/run_individualization_primary_v1.m",
            "prospective/auditory_feedback_individualization/FEATURE_REALLOCATION_DECOMPOSITION_V1.md",
            "prospective/auditory_feedback_individualization/FEATURE_REALLOCATION_RESULT_V1.json",
            "prospective/auditory_feedback_individualization/run_feature_reallocation_v1.m",
        ],
    ),
    "pipistrellus_masker": (
        "prospective/reversible-sensory-perturbation-v2",
        [
            "prospective/reversible_sensory_perturbation_v2/PERSONAL_BIAS_RETENTION_CONTRACT_V1.md",
            "prospective/reversible_sensory_perturbation_v2/personal_bias_retention_v1.py",
        ],
    ),
    "myotis_masking": (
        "prospective/myotis-masker-personal-state-v1",
        [
            "prospective/myotis_masker_personal_state/MAIN_FLIGHT_TIME_STATE_CONTRACT_V1.md",
            "prospective/myotis_masker_personal_state/MYOTIS_PERSONAL_STATE_RESULT_V1.json",
            "prospective/myotis_masker_personal_state/run_myotis_personal_state_v1.py",
        ],
    ),
    "eptesicus_auditory": (
        "prospective/auditory-perturbation-policy-v1",
        [
            "prospective/auditory_perturbation_policy/ACOUSTIC_POLICY_PRIMARY_V1.md",
            "prospective/auditory_perturbation_policy/ACOUSTIC_POLICY_RESULT_V1.json",
            "prospective/auditory_perturbation_policy/run_acoustic_policy_primary_v1.py",
            "prospective/auditory_perturbation_policy/acoustic_policy_primary_self_test_v1.py",
        ],
    ),
    "aharon_navigation": (
        "prospective/public-perturbation-audit-v1",
        [
            "prospective/public_perturbation_audit/AHARON_CROSS_CONDITION_IDENTITY_CONTRACT_V1.md",
            "prospective/public_perturbation_audit/AHARON_FIGURE1_PRIMARY_V1.md",
            "prospective/public_perturbation_audit/AHARON_FIGURE1_PRIMARY_RESULT_V1.json",
            "prospective/public_perturbation_audit/run_aharon_figure1_primary_v1.py",
        ],
    ),
    "rhino_carollia": (
        "prospective/task-reset-lockin-v1",
        [
            "prospective/task_reset_lockin/TRANSPARENT_TWO_AXIS_POLICY_CONTRACT_V1.md",
            "prospective/task_reset_lockin/transparent_two_axis_policy_v1.py",
            "prospective/task_reset_lockin/CAROLLIA_FIXED_TWO_AXIS_VALIDATION_CONTRACT_V1.md",
            "prospective/task_reset_lockin/carollia_fixed_two_axis_validation_v1.py",
            "prospective/task_reset_lockin/CAROLLIA_FIXED_GEOMETRY_EXTERNAL_CONTRACT_V1.md",
            "prospective/task_reset_lockin/carollia_fixed_geometry_external_v1.py",
        ],
    ),
    "wild_boundary": (
        "prospective/evidence-provenance-correction-v1",
        [
            "prospective/field_policy_bridge/FIELD_EVIDENCE_PROVENANCE_GUARD_V1.md",
        ],
    ),
}

TEXT_SUFFIXES = {".md", ".py", ".m", ".json", ".csv", ".txt", ".yml", ".yaml", ".svg"}

def run(*args):
    return subprocess.run(args, cwd=ROOT, check=True, capture_output=True, text=False)

def sanitize_bytes(data: bytes, path: str) -> bytes:
    suffix = Path(path).suffix.lower()
    if suffix not in TEXT_SUFFIXES:
        return data
    text = data.decode("utf-8", errors="strict")
    replacements = {
        "zuizui0223/batter": "ANONYMIZED_AUTHOR_REPOSITORY",
        "github.com/zuizui0223/batter": "ANONYMIZED_AUTHOR_REPOSITORY",
        "zuizui0223": "ANONYMIZED_AUTHOR",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("utf-8")

def write(rel: str, data: bytes):
    dest = BUILD / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(sanitize_bytes(data, rel))

def copy_current():
    for rel in CURRENT_FILES:
        src = ROOT / rel
        if not src.exists():
            raise SystemExit(f"missing current archive input: {rel}")
        outrel = rel
        if rel.endswith("REVIEW_ARCHIVE_README_V1.md"):
            outrel = "README.md"
        elif rel.startswith("prospective/public_causal_synthesis/"):
            outrel = "synthesis/" + Path(rel).name
        elif rel.startswith("figures/public_causal/"):
            outrel = "figures/" + Path(rel).name
        write(outrel, src.read_bytes())

def fetch_ref(ref: str):
    subprocess.run(
        ["git", "fetch", "--depth=1", "origin", ref],
        cwd=ROOT,
        check=True,
    )

def copy_source_groups():
    provenance = {}
    for group, (ref, paths) in SOURCE_GROUPS.items():
        fetch_ref(ref)
        sha = subprocess.run(
            ["git", "rev-parse", "FETCH_HEAD"],
            cwd=ROOT, check=True, capture_output=True, text=True
        ).stdout.strip()
        provenance[group] = {"ref": ref, "commit": sha, "files": []}
        for path in paths:
            proc = subprocess.run(
                ["git", "show", f"FETCH_HEAD:{path}"],
                cwd=ROOT, capture_output=True
            )
            if proc.returncode != 0:
                raise SystemExit(f"missing frozen source file {ref}:{path}")
            outrel = f"source_analyses/{group}/{Path(path).name}"
            write(outrel, proc.stdout)
            provenance[group]["files"].append(outrel)
    write("SOURCE_ANALYSIS_PROVENANCE.json", (json.dumps(provenance, indent=2) + "\n").encode())

def anonymity_scan():
    banned = [
        b"zuizui0223",
        b"github.com/zuizui0223",
        b"ZHANG Ruiqi",
        "張瑞琪".encode("utf-8"),
    ]
    hits = []
    for p in BUILD.rglob("*"):
        if not p.is_file():
            continue
        data = p.read_bytes()
        for token in banned:
            if token.lower() in data.lower():
                hits.append((str(p.relative_to(BUILD)), token.decode("utf-8", errors="replace")))
    if hits:
        raise SystemExit(f"anonymous archive identity scan failed: {hits[:20]}")

def checksums():
    rows = []
    for p in sorted(BUILD.rglob("*")):
        if p.is_file():
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            rows.append(f"{h}  {p.relative_to(BUILD).as_posix()}")
    (BUILD / "SHA256SUMS.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")

def make_zip():
    DIST.mkdir(parents=True, exist_ok=True)
    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(BUILD.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(BUILD))
    print(f"archive={ZIP}")
    print(f"bytes={ZIP.stat().st_size}")
    print(f"sha256={hashlib.sha256(ZIP.read_bytes()).hexdigest()}")

def main():
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)
    copy_current()
    copy_source_groups()
    mirror_carollia_cc0(BUILD)
    anonymity_scan()
    checksums()
    anonymity_scan()
    make_zip()

if __name__ == "__main__":
    main()
