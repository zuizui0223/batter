"""V27: NLM-supported public PMC Cloud Service only; no browser challenge workaround."""
import io,json,hashlib,pathlib,urllib.parse,urllib.request,xml.etree.ElementTree as ET
BASE="https://pmc-oa-opendata.s3.amazonaws.com/"
PMC="PMC13723403";DOI="10.1242/jeb.251521";NAME="jexbio-229-251521-s1.pdf"
OUT=pathlib.Path("results/bayer_supplement_v27.json")
def get(url,n):
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"batter scholarly source audit/1.0"}),timeout=30) as r:
        b=r.read(n+1)
        assert len(b)<=n and len(b)>0
        return b,r.headers.get("ETag")
def main():
    result={"scope":"exact open-access supplement admission only","pmcid":PMC,"article_doi":DOI}
    try:
        q=BASE+"?"+urllib.parse.urlencode({"list-type":"2","prefix":PMC+"."})
        raw,_=get(q,2_000_000);tree=ET.fromstring(raw);ns={"s":"http://s3.amazonaws.com/doc/2006-03-01/"}
        assert tree.findtext("s:IsTruncated",namespaces=ns)=="false"
        objects=[]
        for x in tree.findall("s:Contents",ns):
            objects.append({"key":x.findtext("s:Key",namespaces=ns),"size":int(x.findtext("s:Size",namespaces=ns)),"etag":x.findtext("s:ETag",namespaces=ns)})
        result["objects"]=objects
        selected=[]
        for p in sorted({x["key"].split("/")[0] for x in objects}):
            if not p.startswith(PMC+"."):continue
            xm=[x for x in objects if x["key"]==p+"/"+p+".xml"]
            sf=[x for x in objects if x["key"]==p+"/"+NAME]
            if len(xm)!=1 or len(sf)!=1:continue
            x,_=get(BASE+urllib.parse.quote(xm[0]["key"],safe="/"),4_000_000)
            root=ET.fromstring(x)
            meta=root.find(".//article-meta")
            assert meta is not None
            ids=[v.text for v in meta.findall("article-id") if v.get("pub-id-type")=="doi"]
            if DOI not in ids:continue
            licenses=meta.findall(".//license")
            license_info=" ".join(ET.tostring(l,encoding="unicode") for l in licenses)
            if "creativecommons.org/licenses/by/4.0" not in license_info:continue
            linked=[n for n in meta.iter() if any(str(v).endswith(NAME) for v in n.attrib.values())]
            if not linked:
                linked=[n for n in root.iter() if any(str(v).endswith(NAME) for v in n.attrib.values())]
            if not linked:continue
            selected.append((p,sf[0],hashlib.sha256(x).hexdigest()))
        if len(selected)!=1:raise ValueError("Unique final DOI/license/supplement not established")
        p,f,xsha=selected[0]
        b,etag=get(BASE+urllib.parse.quote(f["key"],safe="/"),10_000_000)
        assert len(b)==f["size"] and b.startswith(b"%PDF-")
        if etag and f["etag"]:assert etag==f["etag"]
        import pypdf
        doc=pypdf.PdfReader(io.BytesIO(b))
        pages=[]
        for j,page in enumerate(doc.pages):
            t=page.extract_text() or ""
            if any(q in t.lower() for q in ("fig. s2","figure s2","decision tree","classification tree")):
                # Record only page location and whether text is recoverable.
                pages.append({"page_1_based":j+1,"characters":len(t)})
        path=OUT.parent/NAME;path.parent.mkdir(exist_ok=True);path.write_bytes(b)
        result.update(status="SUPPLEMENT_VERIFIED",version=p,xml_sha256=xsha,source_key=f["key"],
          bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),etag=etag,license="CC BY 4.0; Bayer et al. (2026), The Company of Biologists",
          pages=len(doc.pages),decision_tree_candidate_pages=pages,
          interpretation="Visual examination of the actual page is required before implementing classifier.")
    except Exception as e:result.update(status="STOP",error=repr(e))
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(result,indent=2)+"\n");print(OUT.read_text())
if __name__=="__main__":main()
