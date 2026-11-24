"""V7 public source gate: Carollia direct power and independent morphology/thermal archive."""
import csv,hashlib,io,json,pathlib,urllib.request,zipfile,xml.etree.ElementTree as ET
from PIL import Image
P=pathlib.Path("results/carollia_sources_v7.json")
def get(url,n=20_000_000):
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"batter-research/1.0 (public scholarly source audit)"}),timeout=35) as r:
        b=r.read(n+1)
        if len(b)>n:raise ValueError("size limit")
        if not b:raise ValueError("empty")
        return b
def digest(b):return {"bytes":len(b),"md5":hashlib.md5(b).hexdigest(),"sha256":hashlib.sha256(b).hexdigest()}
def direct():
    out={}
    base="https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4006254/"
    try:
        b=get(base+"fullTextXML",3_000_000)
        root=ET.fromstring(b)
        out["xml"]=digest(b)
        out["doi"]=[x.text for x in root.findall(".//article-id") if x.get("pub-id-type")=="doi"]
        out["figures"]=[{"id":f.get("id"),"label":"".join(f.find("label").itertext()) if f.find("label") is not None else "",
            "graphics":[g.attrib for g in f.findall(".//graphic")]} for f in root.findall(".//fig")]
        out["tables"]=[{"id":t.get("id"),"label":"".join(t.find("label").itertext()) if t.find("label") is not None else "",
            "caption":" ".join(t.find("caption").itertext())[:350] if t.find("caption") is not None else "",
            "header":["".join(v.itertext()) for v in t.findall(".//thead//th")]} for t in root.findall(".//table-wrap")]
        out["supplement_links"]=[s.attrib for s in root.findall(".//supplementary-material//media")]
    except Exception as e:out["xml_error"]=repr(e)
    try:
        b=get(base+"supplementaryFiles")
        out["archive"]=digest(b);z=zipfile.ZipFile(io.BytesIO(b))
        out["members"]=[{"name":x.filename,"bytes":x.file_size} for x in z.infolist()]
        out["fig_candidates"]=[]
        for x in z.infolist():
            name=x.filename.lower()
            if name.endswith((".jpg",".jpeg",".png",".gif",".tif",".tiff")) and x.file_size<5_000_000:
                raw=z.read(x)
                try:
                    im=Image.open(io.BytesIO(raw));out["fig_candidates"].append({"name":x.filename,**digest(raw),"dimensions":list(im.size)})
                except Exception:pass
    except Exception as e:out["archive_error"]=repr(e)
    try:
        raw=get("https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC4006254",100000)
        out["ncbi_oa"]=raw.decode("utf8")[:4000]
    except Exception as e:out["oa_error"]=repr(e)
    return out
EXPECTED={"WingMorph.txt":"83c25901480df694ab049016955ce130","WingTA.txt":"3352bc873a20ff8e197e2d8b8e74cc20","HeadTA.txt":"19773a41ac4fbbca02ed57bca33d9818","BodyTA.txt":"22d0bc7b1e43b58635f71ef611715660","ArmTA.txt":"e3f9f5c4cbc9a2be9c656cee94eef31b","HeatLoss.R":"585513066648b83104597a6a3de5cf15","PowFlight.R":"00c6f7a1ea6806944b7d58baa361ab0f","Script-HeatLoss-FlightPerformance.R":"3bbb2830a9c4243ee872cb52e73c2373"}
def thermal():
    out={"record":7126170,"files":{}}
    try:
        m=json.loads(get("https://zenodo.org/api/records/7126170",2_000_000))
        assert m["id"]==7126170
        out["doi"]=m.get("doi")
        for f in m["files"]:
            name=f["key"]
            if name not in EXPECTED:continue
            d={"url":f["links"]["self"],"publisher_checksum":f["checksum"]};out["files"][name]=d
            try:
                raw=get(d["url"],100000)
                d.update(digest(raw))
                assert d["md5"]==EXPECTED[name] and f["checksum"]=="md5:"+EXPECTED[name]
                text=raw.decode("utf-8-sig")
                if name.endswith(".txt"):
                    lines=[l for l in text.splitlines() if l.strip()]
                    d["header"]=lines[0];d["rows_excluding_header"]=len(lines)-1
                    d["field_count_first_data_row"]=len(lines[1].split()) if len(lines)>1 else 0
                else:
                    # Methods source, not observation values; restrict output to formula/code lines.
                    d["methods_code"]=text if name in {"HeatLoss.R","PowFlight.R"} else "\n".join(l for l in text.splitlines() if any(k in l for k in ("read.table","read.csv","merge(","HeatLoss","PowFlight","lm(","glm(","source(","rename(","colnames(","rownames(")))[:9000]
                d["status"]="HASH_VERIFIED"
            except Exception as e:d["status"]="STOP";d["error"]=repr(e)
        out["status"]="ALL_HASH_VERIFIED" if set(out["files"])==set(EXPECTED) and all(x["status"]=="HASH_VERIFIED" for x in out["files"].values()) else "INCOMPLETE"
    except Exception as e:out["status"]="STOP";out["error"]=repr(e)
    return out
def main():
    report={"scope":"source_admission_only_no_biological_model_fit","direct":direct(),"thermal":thermal()}
    P.parent.mkdir(parents=True,exist_ok=True);P.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n");print(P.read_text())
if __name__=="__main__":main()
