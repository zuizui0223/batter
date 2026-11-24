"""Schema-only public supplement admission; no metabolic response values printed."""
import json, hashlib, pathlib, urllib.request, io, zipfile, xml.etree.ElementTree as ET
ARTICLE=22643762
FILE=40195337
MD5="bcf9720442c11db72f0382764f830139"
SIZE=732642
W="{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
OUT=pathlib.Path("results/currie_figshare_s2_source_v4.json")
def get(url,limit):
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"batter-research-source-audit/1.0"}),timeout=45) as r:
        b=r.read(limit+1)
        if len(b)>limit: raise ValueError("size limit")
        return b
def txt(el):
    return " ".join("".join(t.text or "" for t in p.iter(W+"t")) for p in el.iter(W+"p")).strip()
def main():
    report={"scope":"public_document_schema_only","doi":"10.6084/m9.figshare.22643762.v1","file_id":FILE}
    try:
        meta=json.loads(get(f"https://api.figshare.com/v2/articles/{ARTICLE}/versions/1",1000000))
        f=next(x for x in meta["files"] if x["id"]==FILE)
        assert f["name"]=="rspb20230045_si_001.docx"
        assert f["computed_md5"]==MD5 and f["size"]==SIZE
        url=f["download_url"] # actual snake_case in official Figshare documentation
        report["published_download_url"]=url
        b=get(url,SIZE)
        assert len(b)==SIZE and hashlib.md5(b).hexdigest()==MD5
        report["sha256"]=hashlib.sha256(b).hexdigest()
        report["md5"]=MD5; report["bytes"]=len(b)
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            xml=z.read("word/document.xml")
        root=ET.fromstring(xml)
        body=root.find(W+"body")
        tables=[]
        caption=""
        for item in body:
            if item.tag==W+"p":
                t=txt(item)
                if "table s" in t.lower()[:60]: caption=t[:400]
            elif item.tag==W+"tbl":
                rows=item.findall(W+"tr")
                cells=[[txt(c) for c in r.findall(W+"tc")] for r in rows]
                tables.append({"index":len(tables),"preceding_caption":caption,
                    "rows":len(rows),"columns_first_row":len(cells[0]) if cells else 0,
                    "header":cells[0] if cells else [],"first_column_labels":[r[0] for r in cells[1:] if r and any(ch.isalpha() for ch in r[0])][:40]})
        report["tables"]=tables
        report["status"]="PUBLISHER_HASH_VERIFIED_SCHEMA_READ"
    except Exception as e:
        report["status"]="SOURCE_STOP";report["error"]=str(e)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(OUT.read_text())
    if report["status"]=="SOURCE_STOP": raise SystemExit(1)
if __name__=="__main__": main()
