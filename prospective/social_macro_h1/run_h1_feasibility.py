#!/usr/bin/env python3
"""Read-only audit of evidence counts, not a biological effect estimator.

No p-values or causal claims can be produced from this review-index dataset.
Run: python prospective/social_macro_h1/run_h1_feasibility.py
Run tests: python -m unittest discover -s prospective/social_macro_h1 -p 'test_*.py'
"""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def read_rows(name):
    with (ROOT / name).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))

def audit():
    old = read_rows("REVIEW_TABLE2_BASELINE_V1.csv")
    new = read_rows("POST2022_PRIMARY_EVIDENCE_V1.csv")
    assert old and new
    assert len({r["review_case_id"] for r in old}) == len(old), "duplicate review case ID"
    assert len({r["case_id"] for r in new}) == len(new), "duplicate post-2022 case ID"
    assert all(r["independent_post2022_holdout"] == "no" for r in old), (
        "review theory-building cases must not be coded as independent holdouts"
    )
    assert all(r["independent_post2022_primary_source"] == "yes" for r in new), (
        "post-2022 cases must have primary source traceability"
    )
    assert all(r["original_primary_study_verified"] == "no" for r in old), (
        "review extraction must not masquerade as independent primary coding"
    )
    assert all(r["h1_strategy_four_class_eligible"] in {"yes", "no"} for r in new)
    valid_categories = {"local_enhancement", "group_facilitation",
                        "following", "recruitment", "unknown"}
    assert set(r["strategy_verbatim_category"] for r in old) <= valid_categories
    taxon_set = sorted({r["taxon_verbatim"] for r in old
                        if r["taxon_is_pooled_group"] == "no"})
    n_both = sum(r["persistence_relative_to_bout"] != "unknown"
                 and r["social_information_location"] != "unknown"
                 for r in old)
    mismatch = sum(
        r["persistence_relative_to_bout"] in {"short", "long"}
        and r["social_information_location"] in {"near", "away"}
        and ((r["persistence_relative_to_bout"] == "short") !=
             (r["social_information_location"] == "near"))
        for r in old
    )
    observed_taxa = sorted({r["species_as_published"] for r in new
                             if not r["species_as_published"].startswith("MULTI_TAXON")})
    return {
        "status": "structural_feasibility_only_no_fitted_comparative_model",
        "source_boundary": "2022 theory-development Table2 != independent holdout",
        "review_table2": {
            "cases": len(old),
            "explicit_named_taxa": len(taxon_set),
            "pooled_taxon_rows": sum(r["taxon_is_pooled_group"] == "yes" for r in old),
            "resolved_strategy_cases": sum(r["strategy_verbatim_category"] != "unknown" for r in old),
            "strategy_counts": dict(sorted(Counter(r["strategy_verbatim_category"] for r in old).items())),
            "persistence_and_location_known_cases": n_both,
            "review_table_mismatches_to_published_framework": mismatch,
            "independent_outcome_validation": False,
        },
        "post2022_targeted_evidence": {
            "records_not_independent_effects": len(new),
            "named_taxa": len(observed_taxa),
            "study_clusters": len({r["study_id"] for r in new}),
            "four_class_independently_coded_cases": sum(r["h1_strategy_four_class_eligible"] == "yes" for r in new),
            "unresolved_taxon_or_aggregate_rows": sum(
                r["species_as_published"].startswith("MULTI_TAXON") for r in new),
            "response_direction_counts_not_meta_analytic": dict(sorted(
                Counter(r["observed_response"] for r in new).items())),
            "search_complete": False,
            "two_blinded_coders_completed": False,
            "species_names": observed_taxa,
        },
        "primary_phylogenetic_h1_strategy_model": "STOP_insufficient_independent_strategy_cases",
        "primary_phylogenetic_h1_occurrence_model": "STOP_no_taxon_sampling_frame_with_effort_adjusted_negatives",
        "h3_individual_memory_tradeoff": "STOP_no_same_species_harmonized_memory_and_social_info_estimator",
        "next_target": "systematic source screening and harmonized cue response data with tested negative conditions",
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    result = audit()
    txt = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(txt, encoding="utf-8")
    print(txt, end="")

if __name__ == "__main__":
    main()
