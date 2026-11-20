"""Mocks official Dryad metadata, NEVER actual records/experiment outcomes."""
import unittest
from dryad_rous_source_manifest import DOI, ENTRY, REQUIRED_FILES, STATUS, audit, official_url


class DryadRousSourceTests(unittest.TestCase):
    def fake(self, drop=None):
        names = [x for x in REQUIRED_FILES if x!=drop]
        files = [{"id":i+1,"path":n,"size":100+i, "digest":"aaa", "digestType":"md5"}
                 for i,n in enumerate(names)]
        d={
            ENTRY:{"identifier":DOI, "_links":{"stash:version":{"href":"/api/v2/versions/1"}},
                   "storageSize":sum(x["size"] for x in files)},
            "https://datadryad.org/api/v2/versions/1":{
                "id":1, "versionNumber":2, "_links":{"stash:files":{"href":"/api/v2/versions/1/files"}}
            },
            "https://datadryad.org/api/v2/versions/1/files":{
                "total":len(files),"_embedded":{"stash:files":files}
            }
        }
        return lambda u:d[u]

    def test_expected_source_files_are_metadata_only(self):
        a=audit(self.fake())
        self.assertEqual(a["status"],STATUS)
        self.assertEqual(a["declared_total_file_count"],len(REQUIRED_FILES))
        self.assertFalse(a["original_bat_and_tree_response_rows_opened"])
        self.assertFalse(a["individual_event_join_demonstrated"])
        self.assertIsNone(a["5d_resource_effect"])

    def test_missing_required_file_is_hard_stop(self):
        with self.assertRaisesRegex(RuntimeError,"SOURCE_REQUIRED_FILES_MISSING"):
            audit(self.fake(drop="Tags_manipulated_and_visiting.csv"))

    def test_reject_offhost_and_non_api(self):
        for u in ("https://other.example/api/v2/data", "http://datadryad.org/api/v2/test",
                  "https://datadryad.org/downloads/file_stream/1234", "//other.example/api/v2/f"):
            with self.assertRaises(ValueError):
                official_url(u)


if __name__=="__main__":
    unittest.main()
