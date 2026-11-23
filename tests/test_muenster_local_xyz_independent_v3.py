"""Independent NumPy parser tests only, no original bat source mocked as biology."""
import numpy as np
import pytest

from scripts.verify_muenster_local_XYZ_v3_independent import (
    numpy_author_csv_triple_counts,
)


def test_source_numpy_pt1_and_missing_nan_zero_substitution_avoided():
    raw=b"pt1_X,pt1_Y,pt1_Z\n1,2,3\nNaN,NaN,NaN\n1,2,NaN\n4,5,6\n"
    assert numpy_author_csv_triple_counts(raw)=={"pt1":2}


def test_source_numpy_sixcolumn_tracks_are_two_target_streams():
    raw=(b"pt1_X,pt1_Y,pt1_Z,pt2_X,pt2_Y,pt2_Z\n"
         b"1,2,3,NaN,NaN,NaN\n"
         b"2,3,4,5,6,7\n")
    assert numpy_author_csv_triple_counts(raw)=={"pt1":2,"pt2":1}


def test_independent_parser_rejects_unrecognized_nonXYZ_header():
    with pytest.raises(ValueError,match="header"):
        numpy_author_csv_triple_counts(
            b"badA,badB,badC\n1,2,3\n"
        )


def test_independent_parser_accepts_tab_separated_original_author_fields():
    raw=b"pt1_X\tpt1_Y\tpt1_Z\n1\t2\t3\n"
    assert numpy_author_csv_triple_counts(raw)=={"pt1":1}
