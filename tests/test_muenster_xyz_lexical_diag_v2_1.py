from scripts.diagnose_muenster_xyz_csv_grammar_v2_1 import (
    describe_cell,lexical_preview,
)

def test_original_source_coordinate_values_not_echoed():
    r=lexical_preview(b"12.431,53.33,-24.71\n13.232,54.21,32.1\n")
    assert r["source_physical_rows"]==2
    assert all(t=="finite_number" for t in
               r["first_five_row_structure_only"][0]["lexical_cell_types"])
    assert "12.431" not in str(r)
    assert r["numeric_XYZ_values_opened_or_printed"] is False

def test_source_header_text_identified_without_looking_at_later_coordinates():
    r=lexical_preview(b"x,y,z\n2,3,4\n")
    assert r["possible_literal_textual_first_row_header_tokens"]==["x","y","z"]
    assert r["first_five_row_structure_only"][0]["lexical_cell_types"]==[
       "text_or_metadata","text_or_metadata","text_or_metadata"]

def test_missing_and_ambiguous_original_tokens_separate():
    assert describe_cell("NaN")=="missing_NaN_or_infinity"
    assert describe_cell("")=="blank"
    assert describe_cell("metres")=="text_or_metadata"
    assert describe_cell("-4.23")=="finite_number"

def test_semicolon_and_tab_delimiters_as_source_types_only():
    assert lexical_preview(b"1;2;3\n")["delimiter_type"]=="semicolon"
    assert lexical_preview(b"1\t2\t3\n")["delimiter_type"]=="tab"
