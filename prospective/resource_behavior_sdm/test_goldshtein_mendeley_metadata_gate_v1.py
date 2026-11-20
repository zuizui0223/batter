"""Source-free schema controls, not bat or botanical validation."""
import unittest
from goldshtein_mendeley_metadata_gate_v1 import DATASET,FILES,PASS,audit,source_url

def fake(url):
    if url==DATASET:
        return {"version":1,"short_id":"jxghjjsttw","doi":{"id":"10.17632/jxghjjsttw.1"}}
    if url.startswith(FILES):
        return {"results":[{"id":"file-a","filename":"gps_data.mat","size":12,
                            "content_details":{"sha256_hash":"a"*64}},
                           {"id":"file-b","filename":"cactus_flower_data.csv","size":18,
                            "content_details":{"sha256_hash":"b"*64}}]}
    raise AssertionError(url)

class TestGate(unittest.TestCase):
    def test_valid_schema_not_evidence_of_effect(self):
        a=audit(fake)
        self.assertEqual(a["status"],PASS)
        self.assertEqual(a["file_count"],2)
        self.assertFalse(a["event_level_resource_height_join_verified"])
        self.assertIsNone(a["high_dimensional_ecological_gain"])
    def test_wrong_doi(self):
        def bad(url):
            v=fake(url)
            if url==DATASET: v["doi"]["id"]="10.17632/wrong.1"
            return v
        with self.assertRaisesRegex(ValueError,"DOI_MISMATCH"): audit(bad)
    def test_wrong_version(self):
        def bad(url):
            v=fake(url)
            if url==DATASET: v["version"]=2
            return v
        with self.assertRaisesRegex(ValueError,"VERSION"): audit(bad)
    def test_duplicates(self):
        def bad(url):
            v=fake(url)
            if url!=DATASET: v["results"][1]["id"]="file-a"
            return v
        with self.assertRaisesRegex(ValueError,"DUPLICATE"): audit(bad)
    def test_hash_failure_and_missing_hash_supported(self):
        def missing(url):
            v=fake(url)
            if url!=DATASET: v["results"][0]["content_details"]={}
            return v
        self.assertIsNone(audit(missing)["files"][0]["publisher_sha256"])
        def malformed(url):
            v=fake(url)
            if url!=DATASET: v["results"][0]["content_details"]["sha256_hash"]="bad"
            return v
        with self.assertRaisesRegex(ValueError,"SHA256"): audit(malformed)
    def test_empty_and_external_url(self):
        def empty(url):
            return fake(url) if url==DATASET else []
        with self.assertRaisesRegex(ValueError,"EMPTY"): audit(empty)
        for url in ("https://fake.org/datasets/jxghjjsttw",
                    "http://api.data.mendeley.com/datasets/jxghjjsttw",
                    "https://api.data.mendeley.com/datasets/jxghjjsttw/zip"):
            with self.assertRaises(ValueError): source_url(url)

if __name__=="__main__": unittest.main()
