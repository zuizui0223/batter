"""Synthetic publisher REST responses only; no bat data is used."""
import copy
import unittest
from independent_resource_vertical_dryad_gate_v1 import (
    SOURCES, PASS, _entry, audit_one, audit_both, _official
)


def fixture():
    cases={}
    for key,source in SOURCES.items():
        doi=source["doi"]
        entry=_entry(doi)
        ver="https://datadryad.org/api/v2/versions/"+key
        files=ver+"/files"
        listing=[{"_links":{"self":{"href":"/api/v2/files/"+str(i+1+(100 if key=="chrotopterus_2026" else 0))}},
                  "path":name,"size":100+i,"digestType":"md5","digest":"0"*32}
                 for i,name in enumerate(sorted(source["expected"]))]
        cases[entry]={"identifier":"doi:"+doi,
                      "_links":{"stash:version":{"href":ver}},
                      "storageSize":sum(z["size"] for z in listing)}
        cases[ver]={"id":key,"versionNumber":1,
                    "_links":{"stash:files":{"href":files}}}
        cases[files]={"total":len(listing),"_embedded":{"stash:files":listing}}
    return cases


class DryadIndependentSourcesTests(unittest.TestCase):
    def test_two_sources_verified_without_join_or_food_promotion(self):
        docs=fixture()
        r=audit_both(lambda url:docs[url])
        self.assertEqual(r["n_metadata_pass"],2)
        self.assertFalse(r["cross_dataset_observational_join_allowed"])
        self.assertIsNone(r["new_empirical_3d_plus_food_gain"])
        self.assertEqual([x["original_file_count"] for x in r["results"]],[5,1])
        self.assertTrue(all(x["status"]==PASS for x in r["results"]))

    def test_missing_resource_file_is_hard_stop(self):
        docs=fixture()
        e=_entry(SOURCES["chrotopterus_2026"]["doi"])
        ver=docs[e]["_links"]["stash:version"]["href"]
        files=docs[ver]["_links"]["stash:files"]["href"]
        docs[files]["_embedded"]["stash:files"][-1]["path"]="unexpected.zip"
        with self.assertRaisesRegex(RuntimeError,"INVENTORY_MISMATCH"):
            audit_one("chrotopterus_2026",lambda url:docs[url])

    def test_explicit_failures_without_partial_fake_pass(self):
        docs=fixture()
        e=_entry(SOURCES["ducke_bats_2018"]["doi"])
        docs[e]["identifier"]="doi:wrong"
        r=audit_both(lambda url:docs[url])
        self.assertEqual(r["n_metadata_pass"],1)
        self.assertEqual(r["results"][1]["status"],"DRYAD_ORIGINAL_METADATA_SOURCE_STOP")

    def test_host_policy_rejects_dangerous_urls(self):
        for u in ["http://datadryad.org/api/v2/test",
                  "https://fake.example/api/v2/test",
                  "https://datadryad.org/downloads/file_stream/444"]:
            with self.assertRaises(ValueError):
                _official(u)

if __name__=="__main__":
    unittest.main()
