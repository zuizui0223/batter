"""Analyze user-supplied original Hendel Excel; never commit source rows.

Read XLSX with artifact_tool, then pass a schema-checked mapping into the
pre-existing source-free leave-one-site-out ridge evaluator.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from hendel_heldout_prey_activity_v1 import (
    TARGETS, evaluate_heldout_sites, validate_original_source_rows
)

EXPECTED_SHA256 = "b550d9b2ed1448191dfee85caaa5f27321c6a78c65c8925816a340695513b5a3"
SOURCE_HEADERS = (
    "plotID", "DOY", "DOY_carabidae", "temp_min", "elevation", "ForMI",
    "SR_trees", "cf_share", "ndsm_sd", "Opn_mean", "DBHMean", "ndead",
    "TreMs_bat_A", "understory_cover", "SR_understory", "mothcount_total",
    "moth_richness", "carabidae", "carabidae_SR", "SRE", "MRE", "LRE", "Ppip",
)
SOURCE_TO_ENGINE = {"mothcount_total": "mothcount", "carabidae_SR": "carabidae_S"}
SCORE_KEYS = (
    "moth_abundance_given_forest",
    "moth_richness_given_abundance",
    "beetle_abundance_given_forest",
    "beetle_richness_given_abundance",
)

def normalize_original_matrix(matrix):
    if len(matrix) != 66 or tuple(matrix[0]) != SOURCE_HEADERS:
        raise ValueError("STOP_HENDEL_ORIGINAL_65x23_SCHEMA_UNEXPECTED")
    data = []
    for row in matrix[1:]:
        if len(row) != len(SOURCE_HEADERS):
            raise ValueError("STOP_HENDEL_ORIGINAL_ROW_WIDTH")
        item = dict(zip(SOURCE_HEADERS, row))
        for old, new in SOURCE_TO_ENGINE.items():
            if new in item or item.get(old) is None:
                raise ValueError("STOP_HENDEL_SOURCE_PREDICTOR_MAP_MISSING")
            item[new] = item.pop(old)
        data.append(item)
    validate_original_source_rows(data)
    return data

def build_receipt(path, include_delete_one=False):
    from artifact_tool import Blob, SpreadsheetFile
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError("STOP_HENDEL_UPLOADED_XLSX_SHA256_MISMATCH")
    workbook = SpreadsheetFile.import_xlsx(Blob.load(str(path)))
    matrix = workbook.worksheets.get_item_at(0).get_range("A1:W66").values
    data = normalize_original_matrix(matrix)
    scores = evaluate_heldout_sites(data)
    receipt = {
        "schema": "batter.hendel_user_upload_source_local_heldout_v1",
        "status": "USER_UPLOADED_ORIGINAL_XLSX_SOURCE_LOCAL_EXPLORATORY",
        "source_uploaded_sha256": digest,
        "publisher_digest_verified": False,
        "source_published_paper_n_plots": 64,
        "source_xlsx_n_unique_plots": len(data),
        "unexplained_64_vs_65_difference": True,
        "preexisting_engine_column_aliases": SOURCE_TO_ENGINE,
        "full_heldout_engine_receipt": scores,
        "source_raw_rows_committed": False,
        "source_ids_or_activity_rows_returned": False,
        "geographically_independent_test": False,
        "resource_conditioned_individual_3d_height": None,
    }
    if include_delete_one:
        summary = {t: {k: [] for k in SCORE_KEYS} for t in TARGETS}
        for drop in range(len(data)):
            result = evaluate_heldout_sites(data[:drop] + data[drop + 1:])
            for t in TARGETS:
                for k in SCORE_KEYS:
                    summary[t][k].append(
                        result["per_guild_equal_site_gain"][t][k]
                    )
        receipt["exhaustive_delete_one_site_64_row_sensitivity"] = {
            t: {k: {"min": min(vals), "max": max(vals),
                    "positive_subsets": sum(v > 0 for v in vals),
                    "subsets": len(vals)}
                for k, vals in summary[t].items()}
            for t in TARGETS
        }
    return receipt

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--original-xlsx", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--delete-one", action="store_true")
    args = parser.parse_args()
    result = build_receipt(args.original_xlsx, args.delete_one)
    target = Path(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print("HENDEL_USER_UPLOAD_QUALIFIED", result["source_xlsx_n_unique_plots"])
    print("HENDEL_STATUS", result["status"])
    print("HENDEL_RAW_OUTPUT_EXCLUDED", result["source_raw_rows_committed"])

if __name__ == "__main__":
    main()
