"""V28 exact supplementary figure inspection. No invented classifier."""
import base64,hashlib,json,pathlib,urllib.request,io
import fitz
from PIL import Image
URL="https://pmc-oa-opendata.s3.amazonaws.com/PMC13723403.1/jexbio-229-251521-s1.pdf"
SHA="d68aa271a8719e4ea93e1eaad698f3b2c418d438ec16f78d5f28c7380570cf3f"
def main():
    with urllib.request.urlopen(URL,timeout=30) as r:b=r.read(2278551)
    assert len(b)==2278550 and hashlib.sha256(b).hexdigest()==SHA
    doc=fitz.open(stream=b,filetype="pdf");assert len(doc)==8
    p=doc[1];out=pathlib.Path("results");out.mkdir(exist_ok=True)
    pix=p.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False)
    pix.save(out/"bayer_fig_s2_page2_v28.png")
    report={"source_sha256":SHA,"page":2,"source_url":URL,"page_text":p.get_text(),"page_size":[p.rect.width,p.rect.height],"license":"CC BY 4.0; Bayer et al. 2026, doi:10.1242/jeb.251521"}
    (out/"bayer_fig_s2_page2_v28.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(report,indent=2,ensure_ascii=False),flush=True)
    # Lossy compact overview is only for transport for visual inspection; original PNG in artifact.
    im=Image.open(out/"bayer_fig_s2_page2_v28.png").convert("RGB")
    im.thumbnail((1100,1500))
    buf=io.BytesIO();im.save(buf,format="JPEG",quality=75,optimize=True)
    s=base64.b64encode(buf.getvalue()).decode("ascii")
    print("BEGIN_PAGE_IMAGE_V28")
    for i in range(0,len(s),3000):print(s[i:i+3000])
    print("END_PAGE_IMAGE_V28")
if __name__=="__main__":main()
