#!/usr/bin/env python3
"""Audit panel-indexed source profile counts and cross-source literal animal IDs.

Reads only immutable original Figure 6 CSV and derived pair labels. This is
provenance QA, not confirmation that repeated literal labels represent the
same physical animals in datasets six years apart.
"""
from __future__ import annotations
from collections import Counter, defaultdict
import csv
from pathlib import Path
import hashlib

HERE=Path(__file__).resolve().parent
ARCHIVE=HERE/"figures/original_jae/centered_shape_individual_profiles_v1.csv"
PAIRS=HERE/"figures/ORIGINAL_PROFILE_WITHIN_COHORT_OVERLAP_PAIRS_V1.csv"
PANELS={
    "eidolon":20,
    "hypsignathus":24,
    "phyllostomus_2022":33,
    "phyllostomus_2023":16,
    "phyllostomus_2016":10,
}
REPEATED={
    "71A0D95":frozenset({"phyllostomus_2016","phyllostomus_2022"}),
    "74DDA80":frozenset({"phyllostomus_2016","phyllostomus_2022"}),
}

def main() -> None:
    assert hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()==(
        "91cae4c22588db0976dfe3e273eabebaa89dc2844e996f42d01ef617672dc3f8"
    ),"Original JAE source CSV changed"
    with ARCHIVE.open(newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==103
    per_panel=Counter(r["panel"] for r in rows)
    assert per_panel==PANELS,(per_panel,PANELS)

    panel_keys=defaultdict(set)
    label_sources=defaultdict(set)
    lookup={}
    for row in rows:
        panel=row["panel"]
        ident=row["individual"]
        cohort=row["cohorts"]
        row_order=int(row["row_order"])
        assert ident and cohort
        assert ident not in panel_keys[panel],("Duplicate individual within one original panel",panel,ident)
        panel_keys[panel].add(ident)
        label_sources[ident].add(panel)
        key=(panel,row_order)
        assert key not in lookup
        lookup[key]=(ident,cohort)
    for panel,expected_n in PANELS.items():
        assert len(panel_keys[panel])==expected_n
        assert {rownum for pp,rownum in lookup if pp==panel}==set(range(1,expected_n+1)),panel

    # 101 *literal* original labels, not verified 101 or 103 distinct living bats.
    assert len(label_sources)==101,("Global source-ID strings drift",len(label_sources))
    actual_repeated={k:frozenset(v) for k,v in label_sources.items() if len(v)>1}
    assert actual_repeated==REPEATED,actual_repeated

    # Independently rebuild every eligible cohort-restricted pair from archived CSV.
    groups=defaultdict(list)
    for (panel,row_order),(ident,cohort) in lookup.items():
        groups[(panel,cohort)].append((row_order,ident))
    expected_pairs=set()
    for (panel,cohort),records in groups.items():
        records.sort()
        for i in range(len(records)):
            for j in range(i+1,len(records)):
                (id_i,bat_i),(id_j,bat_j)=records[i],records[j]
                assert bat_i!=bat_j,("One animal mistakenly paired with self",panel,cohort)
                expected_pairs.add((panel,cohort,id_i,id_j))
    assert len(expected_pairs)==684

    with PAIRS.open(newline="",encoding="utf-8") as f:
        output=list(csv.DictReader(f))
    assert len(output)==684
    observed=set()
    for p in output:
        panel=p["panel"]
        cohort=p["cohort"]
        i=int(p["source_row_order_i"])
        j=int(p["source_row_order_j"])
        assert i<j
        id_a,cohort_a=lookup[panel,i]
        id_b,cohort_b=lookup[panel,j]
        assert id_a!=id_b and cohort==cohort_a==cohort_b
        observed.add((panel,cohort,i,j))
    assert observed==expected_pairs,("Derived cohort pair universe does not match original",len(observed),len(expected_pairs))

    manuscript=(HERE/"INTEGRATED_MANUSCRIPT_V1.md").read_text(encoding="utf8")
    anonymous=(HERE/"COMPLETE_ANONYMOUS_TEXT_DRAFT_V1.md").read_text(encoding="utf8")
    for name,text in [("manuscript",manuscript),("anonymous",anonymous)]:
        assert "103 individual-by-panel profiles" in text,(name,"panel-indexing qualification absent")
        assert "two source identifiers" in text.lower(),(name,"cross-year label repeats not acknowledged")
        for forbidden in ["103 globally distinct bats","103 independent biological individuals",
                          "all 103 bats are different individuals"]:
            assert forbidden not in text,(name,forbidden)
    print("PASS: original 103 source-panel profiles / 101 distinct literal IDs /")
    print("      two repeated 2016+2022 source identifier strings; global biological identities UNVERIFIED")
    print("PASS: no invalid same-label or between-source-panel dyads among all 684 records")

if __name__=="__main__":
    main()
