"""V5 frozen source-table extraction and conditional wind geometry audit."""
import hashlib, io, json, math, pathlib, re, urllib.request, zipfile, xml.etree.ElementTree as ET
import numpy as np
W="{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
URL="https://ndownloader.figshare.com/files/40195337"
SHA="a3fd844edc28df1bf28da8f6cb3fb6f5db536a12418b78441b05731b9c5eb206"
MD5="bcf9720442c11db72f0382764f830139"
BATS={"Carollia perspicillata","Eidolon helvum","Hypsignathus monstrosus","Leptonycteris yerbabuenae","Phyllostomus hastatus","Pipistrellus nathusii","Pteropus alecto (gouldii)","Pteropus poliocephalus"}
OUT=pathlib.Path("results/currie_s2_s3_v5.json")
NUM=r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)"
def txt(el):
    return " ".join("".join(t.text or "" for t in p.iter(W+"t")) for p in el.iter(W+"p")).strip()
def number(s,missing=False):
    s=s.strip().replace("−","-")
    if missing and (not s or s.lower() in {"n/a","na","n.a.","–","—","-"}):return None
    p=re.fullmatch(r"("+NUM+r")\s*(?:±\s*("+NUM+r"))?\s*\*?",s)
    if not p: raise ValueError("ambiguous numeric token "+repr(s))
    return float(p[1])
def table(t):
    return [[txt(c) for c in row.findall(W+"tc")] for row in t.findall(W+"tr")]
def frac(u,w):
    return max(0,1-(w/u)**2)**1.5
def model_speed(m,b,s,k,cd):
    a=2*k*(m*9.81)**2/(1.2*math.pi*b*b)
    B=.5*1.2*s*cd
    return (a/B)**.25
def scenario(rows):
    assert rows[0][:5]==["Species","Body Mass (kg)","Wbf (Hz)","Cdb","Wingspan (m)"]
    assert rows[0][5].startswith("Wing Area")
    out=[]
    for row in rows[1:]:
        if not row or row[0] not in BATS: continue
        assert len(row)==7
        m,b,s=map(number,(row[1],row[4],row[5]))
        assert 0.001<m<3 and .08<b<2.5 and .001<s<1.0
        ar=b*b/s; wl=m*9.81/s
        assert 2<ar<20 and 1<wl<150
        u=model_speed(m,b,s,1.2,.08)
        us=[model_speed(m,b,s,k,cd) for k in (1,1.2,1.4) for cd in (.05,.08,.12)]
        out.append({"species":row[0],"mass_kg":m,"span_m":b,"area_m2":s,"AR":ar,"WL_N_m2":wl,"proxy_speed_m_s":u,
                    "area_fraction_w2":frac(u,2),"area_fraction_w4":frac(u,4),
                    "speed_sensitivity":[min(us),max(us)],
                    "area_w4_sensitivity":[frac(min(us),4),frac(max(us),4)],
                    "allometry_flag_in_cells":any("*" in v for v in row),"source":row[6]})
    assert len(out)==8 and {r["species"] for r in out}==BATS
    # Mass-only comparator scaled to the same geometric mean prediction (NOT observed speed).
    scale=math.exp(np.mean([math.log(r["proxy_speed_m_s"]/r["mass_kg"]**(1/6)) for r in out]))
    for r in out:
        r["mass_only_proxy_speed"]=scale*r["mass_kg"]**(1/6)
        r["mass_only_area_fraction_w4"]=frac(r["mass_only_proxy_speed"],4)
        r["morphology_minus_mass_area_w4"]=r["area_fraction_w4"]-r["mass_only_area_fraction_w4"]
    return sorted(out,key=lambda x:x["proxy_speed_m_s"])
def efficiency(rows):
    assert len(rows)==13 and rows[0][:3]==["Species","Speed (ms-1)","Measured conversion efficiency (%)"]
    data=[]
    for r in rows[1:]:
        assert len(r)==5
        data.append(dict(species=r[0],speed=number(r[1]),measured=number(r[2],True),afpt=number(r[3],True),mass=number(r[4],True)))
    groups={s:[r for r in data if r["species"]==s] for s in sorted({r["species"] for r in data})}
    results={}
    for name,rr in groups.items():
        # complete support for all three columns
        pairs=[r for r in rr if all(r[c] is not None for c in ("measured","afpt","mass"))]
        results[name]={"n_paired":len(pairs),"mae_afpt_pp":float(np.mean([abs(r["afpt"]-r["measured"]) for r in pairs])) if pairs else None,
            "mae_mass_pp":float(np.mean([abs(r["mass"]-r["measured"]) for r in pairs])) if pairs else None}
    a,b="Carollia perspicillata","Pipistrellus nathusii"
    transfers=[]
    for train,test in [(a,b),(b,a)]:
        tr={r["speed"]:r["measured"] for r in groups[train] if r["measured"] is not None}
        te={r["speed"]:r["measured"] for r in groups[test] if r["measured"] is not None}
        shared=sorted(tr.keys()&te.keys())
        if len(shared)<2: transfers.append({"train":train,"test":test,"status":"STOP_INSUFFICIENT_SHARED_SUPPORT","shared":shared});continue
        # fit only shared support to ensure no extra training data beyond common speed range
        x=np.array(shared); y=np.array([tr[s] for s in shared]); obs=np.array([te[s] for s in shared])
        slope,intercept=np.polyfit(x,y,1)
        transfers.append({"train":train,"test":test,"shared_speed":shared,"n":len(shared),
                          "train_slope_pp_per_m_s":float(slope),
                          "mae_constant_pp":float(np.mean(abs(obs-y.mean()))),
                          "mae_speed_pp":float(np.mean(abs(obs-(slope*x+intercept))))})
    return {"published_comparator_descriptive":results,"two_species_transfer_boundary":transfers}
def main():
    report={"scope":"authenticated_source_table_audit_and_conditional_proxy_not_full_power_validation"}
    try:
        with urllib.request.urlopen(urllib.request.Request(URL,headers={"User-Agent":"batter-research-source-audit/1.0"}),timeout=45) as r:
            raw=r.read(732643)
        assert len(raw)==732642 and hashlib.sha256(raw).hexdigest()==SHA and hashlib.md5(raw).hexdigest()==MD5
        root=ET.fromstring(zipfile.ZipFile(io.BytesIO(raw)).read("word/document.xml"))
        tables=root.find(W+"body").findall(W+"tbl")
        s2,s3=table(tables[1]),table(tables[2])
        report["source_sha256"]=SHA
        report["s2_area_header_ooxml"]=ET.tostring(tables[1].findall(W+"tr")[0].findall(W+"tc")[5],encoding="unicode")
        report["s2_rows"]=s2;report["s3_rows"]=s3
        try:
            report["morphology_scenario"]=scenario(s2)
            report["s2_status"]="CONDITIONAL_PROXY_COMPUTED"
        except Exception as e:report["s2_status"]="STOP";report["s2_error"]=repr(e)
        try:
            report["efficiency_audit"]=efficiency(s3)
            report["s3_status"]="DESCRIPTIVE_TRANSFER_BOUNDARY_COMPUTED"
        except Exception as e:report["s3_status"]="STOP";report["s3_error"]=repr(e)
    except Exception as e:
        report["source_error"]=repr(e)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+"\n")
    print(OUT.read_text())
    if report.get("s2_status")=="STOP" or report.get("s3_status")=="STOP" or "source_error" in report:raise SystemExit(1)
if __name__=="__main__":main()
