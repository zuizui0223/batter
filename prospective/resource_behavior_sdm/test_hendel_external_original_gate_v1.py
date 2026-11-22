"""No source biology in tests: official metadata, original digests and response gates."""
import hashlib,io,unittest,zipfile
from hendel_external_original_gate_v1 import (
 DOI,ENTRY,EXPECTED,API_STATUS,CONTENT_STATUS,metadata,original_archive_audit,official_api
)


def fake_api():
    version="https://datadryad.org/api/v2/versions/99"
    files=version+"/files"
    a={"Hendel_etal_2024_Data_DRYAD.xlsx":(15919,"e"*32),
       "README.md":(9811,"c"*32)}
    docs={
       ENTRY:{"identifier":DOI,"storageSize":15919+9811,
              "_links":{"stash:version":{"href":version}}},
       version:{"id":99,"versionNumber":1,"_links":{"stash:files":{"href":files}}},
       files:{"total":2,"_embedded":{"stash:files":[
             {"path":name,"size":size,"digestType":"md5","digest":digest,
              "_links":{"self":{"href":f"/api/v2/files/{100+i}"}}}
             for i,(name,(size,digest)) in enumerate(a.items())]}}
    }
    return lambda url:docs[url]


class HendelSourceGate(unittest.TestCase):
    def test_official_original_version_files_not_new_ecological_effect(self):
        x=metadata(fake_api())
        self.assertEqual(x["status"],API_STATUS)
        self.assertEqual(set(x["publisher_files"]),EXPECTED)
        self.assertFalse(x["source_biological_rows_read"])
    def test_wrong_original_doi_is_not_accepted(self):
        fetch=fake_api()
        def mismatch(url):
            r=fetch(url)
            return {**r,"identifier":"doi:wrong"} if url==ENTRY else r
        with self.assertRaisesRegex(ValueError,"DOI_MISMATCH"):
            metadata(mismatch)
    def test_wrong_publisher_digest_never_opens_xlsx(self):
        m=metadata(fake_api())
        f=io.BytesIO()
        with zipfile.ZipFile(f,"w") as z:
            z.writestr("Hendel_etal_2024_Data_DRYAD.xlsx",b"x"*15919)
            z.writestr("README.md",b"y"*9811)
        with self.assertRaisesRegex(ValueError,"DIGEST_MISMATCH"):
            original_archive_audit(m,lambda:f.getvalue())
    def test_nonofficial_url_refused(self):
        for u in ("https://example.invalid/api/v2/files/1","http://datadryad.org/api/v2/versions/1",
                  "https://datadryad.org/downloads/file_stream/12"):
            with self.assertRaises(ValueError):
                official_api(u)


if __name__=="__main__":
    unittest.main()
