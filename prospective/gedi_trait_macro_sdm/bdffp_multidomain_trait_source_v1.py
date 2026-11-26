"""One bounded official Table S2 source retrieval and structural audit. No ecological fit."""
import hashlib,json,pathlib,zipfile,xml.etree.ElementTree as ET
import requests
U="https://media.springernature.com/original/springer-static/esm/art%3A10.1007%2Fs10980-022-01493-x/MediaObjects/10980_2022_1493_MOESM1_ESM.docx"
O=pathlib.Path("bdffp_multidomain_source");O.mkdir(exist_ok=True)
R={"status":"START","doi":"10.1007/s10980-022-01493-x","url":U,"ecological_fit":False}
def save():
    (O/"report.json").write_text(json.dumps(R,indent=2,ensure_ascii=False)+"\n")
    print("BDFFP_TRAIT_SOURCE="+json.dumps(R,ensure_ascii=False),flush=True)
def main():
    p=O/"official_supplement.docx"
    with requests.get(U,stream=True,timeout=(20,60),allow_redirects=False,headers={"Accept-Encoding":"identity"}) as r:
        R["http"]=r.status_code;R["content_type"]=r.headers.get("Content-Type");R["content_length"]=r.headers.get("Content-Length")
        if r.status_code!=200:
            R["status"]="STOP_HTTP";return
        b=bytearray()
        for c in r.iter_content(65536):
            b.extend(c)
            if len(b)>5*1024**2:raise ValueError("source cap")
        if R["content_length"] is not None:assert len(b)==int(R["content_length"])
    R["bytes"]=len(b);R["sha256"]=hashlib.sha256(b).hexdigest()
    p.write_bytes(b)
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None and "word/document.xml" in z.namelist()
        assert z.getinfo("word/document.xml").file_size<=20*1024**2
        e=ET.fromstring(z.read("word/document.xml"))
    ns={"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    tables=[]
    for i,t in enumerate(e.findall(".//w:tbl",ns)):
        rows=[[" ".join(x.text or "" for x in c.findall(".//w:t",ns)) for c in rr.findall("./w:tc",ns)] for rr in t.findall("./w:tr",ns)]
        tables.append({"table_index":i,"rows":len(rows),"column_counts":sorted(set(map(len,rows))),"header":rows[0] if rows else []})
    R["tables"]=tables;R["status"]="SOURCE_BYTES_READY_REQUIRES_TRAIT_SCHEMA_REVIEW"
if __name__=="__main__":
    try:main()
    except Exception as e:R.update(status="STOP_SOURCE_OR_QC",error_type=type(e).__name__,reason=str(e)[:180])
    finally:save()
