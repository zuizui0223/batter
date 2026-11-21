"""Source-free tiny CSV checksum and header parsing tests."""
import hashlib
import unittest

from dryad_rous_original_header_gate import (
    HEADER_FILES, PASS, header_audit, original_bytes
)
from dryad_rous_source_manifest import DOI, STATUS


class RousOriginalHeaderTests(unittest.TestCase):
    def fixture(self):
        sources={
            "Field_Manipulation_Table.csv":b"date,treatment\n01,0\n",
            "manipulations_trees_locations.csv":b"X_ITM,Y_ITM\n1,2\n",
            "Tags_manipulated_and_visiting.csv":b"tag,treatment\nID,control\n",
        }
        return sources, {
            "dataset_doi":DOI, "status":STATUS,
            "required_original_file_metadata":[
                {"public_file_id":i+1,"file_name":name,"size_bytes":len(sources[name]),
                 "digest_type":"sha-256","digest":hashlib.sha256(sources[name]).hexdigest()}
                for i,name in enumerate(HEADER_FILES)
            ]
        }

    def test_only_headers_and_not_animal_rows(self):
        src, meta=self.fixture()
        by_id={i+1:src[n] for i,n in enumerate(HEADER_FILES)}
        result=header_audit(meta,lambda i,n:by_id[i])
        self.assertEqual(result["status"],PASS)
        self.assertEqual(result["csv_files_verified"],3)
        self.assertFalse(result["parsed_original_biological_rows"])
        self.assertFalse(result["sqlite_tracks_downloaded"])
        self.assertIsNone(result["empirical_5d_gain"])
        self.assertEqual(result["original_csv_header_schema"][0]["column_names_only"],
                         ["date","treatment"])

    def test_md5_author_digest_is_also_supported(self):
        src,meta=self.fixture()
        meta["required_original_file_metadata"][0]["digest_type"]="md5"
        meta["required_original_file_metadata"][0]["digest"]=hashlib.md5(
            src[HEADER_FILES[0]]).hexdigest()
        by_id={i+1:src[n] for i,n in enumerate(HEADER_FILES)}
        self.assertEqual(header_audit(meta,lambda i,n:by_id[i])["status"],PASS)

    def test_source_mismatch_and_bad_size_rejected(self):
        src,meta=self.fixture()
        by_id={i+1:src[n] for i,n in enumerate(HEADER_FILES)}
        meta["required_original_file_metadata"][0]["digest"]="badsha"
        with self.assertRaisesRegex(RuntimeError,"ORIGINAL_FILE_HASH_MISMATCH"):
            header_audit(meta,lambda i,n:by_id[i])
        with self.assertRaises(ValueError):
            original_bytes(1,100001)

    def test_doi_mismatch_or_fake_bytes_rejected(self):
        src,meta=self.fixture()
        with self.assertRaisesRegex(RuntimeError,"ORIGINAL_METADATA_NOT_AUTHENTICATED"):
            header_audit({**meta,"dataset_doi":"unknown"},lambda i,n:b"")
        with self.assertRaisesRegex(RuntimeError,"ORIGINAL_FILE_BYTES_NOT_VERIFIED"):
            header_audit(meta,lambda i,n:b"x")


if __name__=="__main__":
    unittest.main()
