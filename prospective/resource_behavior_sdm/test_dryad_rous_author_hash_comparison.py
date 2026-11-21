"""Known-truth original-publisher hash controls with synthetic CSV bytes."""
import hashlib
import unittest

from dryad_rous_author_hash_comparison import (
    TWO_FILES, VERIFIED, audit_author_match,
)
from dryad_rous_source_manifest import DOI, STATUS


class AuthorHashTests(unittest.TestCase):
    def setup(self):
        data={TWO_FILES[0]:b"night,treatment\n1,yes\n",
              TWO_FILES[1]:b"bat,night\n1,2\n"}
        m={"status":STATUS,"dataset_doi":DOI,
           "required_original_file_metadata":[
                {"file_name":name,"size_bytes":len(raw),"digest_type":"md5",
                 "digest":hashlib.md5(raw).hexdigest()}
                for name,raw in data.items()
            ]}
        return data,m

    def test_two_original_source_files_match_and_no_rows_consumed(self):
        data,m=self.setup()
        p=audit_author_match(m, lambda name,n:data[name])
        self.assertEqual(p["status"],VERIFIED)
        self.assertEqual(p["matched_original_files_count"],2)
        self.assertFalse(p["original_biological_rows_read"])
        self.assertFalse(p["third_original_tree_location_hash_confirmed"])
        self.assertIsNone(p["new_5d_resource_behavior_coefficient"])

    def test_no_hash_match_no_original_source_claim(self):
        data,m=self.setup()
        m["required_original_file_metadata"][0]["digest"]="deadbeef"
        with self.assertRaisesRegex(RuntimeError,"AUTHOR_SOURCE_PUBLISHER_DIGEST_MISMATCH"):
            audit_author_match(m,lambda name,n:data[name])

    def test_no_sharing_unverified_source_and_no_silent_size_fix(self):
        data,m=self.setup()
        m["required_original_file_metadata"][1]["size_bytes"]+=2
        with self.assertRaisesRegex(RuntimeError,"AUTHOR_SOURCE_ORIGINAL_SIZE_MISMATCH"):
            audit_author_match(m,lambda name,n:data[name])
        data,m=self.setup()
        m["status"]="SOURCE_STOP"
        with self.assertRaisesRegex(RuntimeError,"PUBLISHER_METADATA_NOT_VERIFIED"):
            audit_author_match(m,lambda name,n:data[name])


if __name__=="__main__":
    unittest.main()
