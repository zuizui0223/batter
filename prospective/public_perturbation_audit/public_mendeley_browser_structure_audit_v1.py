#!/usr/bin/env python3
"""Public-UI download-all structural audit using Playwright.

No numerical research outcomes are emitted.
"""

from __future__ import annotations
import io, json, pathlib, re, tempfile, zipfile
from playwright.sync_api import sync_playwright

HERE=pathlib.Path(__file__).resolve().parent
OUTJ=HERE/"PUBLIC_BROWSER_STRUCTURE_AUDIT_V1.json"
OUTM=HERE/"PUBLIC_BROWSER_STRUCTURE_AUDIT_V1.md"

SOURCES=[
 {"key":"aharon2017","url":"https://data.mendeley.com/datasets/f6mvhj5gj9/3"},
 {"key":"ma2025","url":"https://data.mendeley.com/datasets/964fv73w94/1"},
]

def mat_structure(data,name):
    out={"type":"mat","variables":[],"notes":[]}
    if data[:8]==b"\x89HDF\r\n\x1a\n":
        import h5py
        with h5py.File(io.BytesIO(data),"r") as h:
            def visit(path,obj):
                if isinstance(obj,h5py.Dataset):
                    out["variables"].append({"name":path,"shape":list(obj.shape),"dtype":str(obj.dtype)})
            h.visititems(visit)
        return out
    try:
        import scipy.io
        with tempfile.NamedTemporaryFile(suffix=".mat") as tf:
            tf.write(data); tf.flush()
            for var,shape,klass in scipy.io.whosmat(tf.name):
                out["variables"].append({"name":var,"shape":list(shape),"class":klass})
    except Exception as e:
        out["notes"].append(repr(e))
    return out

def m_structure(data,name):
    text=data.decode("utf-8","replace")
    # remove comments before token extraction
    clean=re.sub(r"%[^\n]*","",text)
    ids=sorted(set(re.findall(r"\b[A-Za-z]\w*\b",clean)))
    relevant=[x for x in ids if re.search(r"(bat|trial|flight|fly|noise|prey|land|speed|turn|slow|path|xyz|coord|condition)",x,re.I)]
    refs=[]
    for fn,file in re.findall(r"\b(load|readtable|readmatrix|readcell|xlsread)\s*\(\s*['\"]([^'\"]+)['\"]",clean,re.I):
        refs.append({"function":fn,"filename":file})
    return {"type":"matlab_script","relevant_identifiers":relevant[:800],"data_file_references":refs[:500]}

def xlsx_structure(data,name):
    import openpyxl
    out={"type":"xlsx","sheets":[]}
    with tempfile.NamedTemporaryFile(suffix=".xlsx") as tf:
        tf.write(data); tf.flush()
        wb=openpyxl.load_workbook(tf.name,read_only=True,data_only=False)
        for ws in wb.worksheets:
            header=[]
            try:
                first=next(ws.iter_rows(min_row=1,max_row=1))
                header=[None if c.value is None else str(c.value) for c in first]
            except StopIteration:
                pass
            out["sheets"].append({"name":ws.title,"max_row":ws.max_row,"max_column":ws.max_column,"header":header})
    return out

def inspect_archive(path):
    result={"archive_name":path.name,"members":[]}
    if not zipfile.is_zipfile(path):
        result["error"]="download_not_zip"
        return result
    with zipfile.ZipFile(path) as z:
        for info in z.infolist():
            rec={"name":info.filename,"size":info.file_size}
            ext=pathlib.Path(info.filename).suffix.lower()
            if ext in {".mat",".m",".xlsx",".xlsm"} and info.file_size <= 250_000_000:
                data=z.read(info)
                try:
                    if ext==".mat": rec["structure"]=mat_structure(data,info.filename)
                    elif ext==".m": rec["structure"]=m_structure(data,info.filename)
                    else: rec["structure"]=xlsx_structure(data,info.filename)
                except Exception as e:
                    rec["structure_error"]=repr(e)
            result["members"].append(rec)
    return result

def accept_cookie(page):
    for name in ("Accept All","Accept all","Allow all","I agree","Accept"):
        try:
            loc=page.get_by_role("button",name=name)
            if loc.count():
                loc.first.click(timeout=1500)
                return
        except Exception:
            pass

def audit_source(browser,src,tmp):
    page=browser.new_page(accept_downloads=True)
    network=[]
    page.on("response",lambda r: network.append({"url":r.url,"status":r.status,"content_type":r.headers.get("content-type")})
            if ("mendeley" in r.url and ("file" in r.url or "dataset" in r.url or "download" in r.url)) else None)
    page.goto(src["url"],wait_until="domcontentloaded",timeout=120000)
    page.wait_for_timeout(6000)
    accept_cookie(page)
    page.wait_for_timeout(1000)

    candidates=[]
    for selector in [
        'button:has-text("Download All")',
        'button:has-text("Download all")',
        'a:has-text("Download All")',
        'a:has-text("Download all")',
    ]:
        try:
            loc=page.locator(selector)
            if loc.count(): candidates.append(loc.first)
        except Exception: pass

    out={"key":src["key"],"url":src["url"],"title":page.title(),"network":network[-300:],"download":None}
    if not candidates:
        out["error"]="download_all_control_not_found"
        page.close(); return out

    try:
        with page.expect_download(timeout=60000) as di:
            candidates[0].click(timeout=10000)
        dl=di.value
        dest=tmp/(src["key"]+"__"+dl.suggested_filename)
        dl.save_as(str(dest))
        out["download"]={
            "suggested_filename":dl.suggested_filename,
            "url":dl.url,
            "size":dest.stat().st_size,
            "archive":inspect_archive(dest),
        }
    except Exception as e:
        out["error"]="download_failed:"+repr(e)
    page.close()
    return out

def derive(src):
    names=[]
    if src.get("download") and src["download"].get("archive"):
        for m in src["download"]["archive"].get("members",[]):
            names.append(m.get("name",""))
            st=m.get("structure") or {}
            for v in st.get("variables",[]): names.append(v.get("name",""))
            names.extend(st.get("relevant_identifiers",[]))
            names.extend(x.get("filename","") for x in st.get("data_file_references",[]))
    text=" ".join(names)
    nums=sorted(set(re.findall(r"(?<![A-Za-z])(?:bat[_-]?)?(\d{2,4})(?![A-Za-z])",text,re.I)))
    cond=sorted(set(x for x in names if re.search(r"(turn|slow|speed|wind|con|condition|noise|prey|land|flight)",x,re.I)))[:500]
    return {"numeric_bat_tokens":nums[:300],"condition_like_tokens":cond}

def render(res):
    L=["# Public browser structural audit v1","","## Status","",
       "**PUBLIC DOWNLOAD-ALL STRUCTURE ONLY; NO NUMERIC OUTCOMES REPORTED.**",""]
    for s in res["sources"]:
        L += [f"## {s['key']}","",f"- page title: {s.get('title')}",f"- error: {s.get('error')}"]
        dl=s.get("download") or {}
        ar=dl.get("archive") or {}
        L += [f"- archive: {dl.get('suggested_filename')}",f"- archive bytes: {dl.get('size')}",
              f"- archive members: {len(ar.get('members') or [])}"]
        toks=s.get("tokens") or {}
        L += [f"- numeric bat-like tokens: {', '.join(toks.get('numeric_bat_tokens') or []) or 'none'}",
              f"- condition-like tokens: {len(toks.get('condition_like_tokens') or [])}",""]
        for m in (ar.get("members") or [])[:300]:
            L.append(f"### {m.get('name')}")
            L.append(f"- bytes: {m.get('size')}")
            st=m.get("structure") or {}
            if st.get("type")=="mat":
                L.append(f"- MAT variables: {len(st.get('variables') or [])}")
                for v in (st.get("variables") or [])[:200]:
                    L.append(f"  - \`{v.get('name')}\` shape={v.get('shape')} class={v.get('class') or v.get('dtype')}")
            elif st.get("type")=="matlab_script":
                L.append("- relevant identifiers: "+", ".join(st.get("relevant_identifiers") or []))
                for r in st.get("data_file_references") or []: L.append(f"  - data reference: {r}")
            elif st.get("type")=="xlsx":
                for sh in st.get("sheets") or []:
                    L.append(f"  - sheet \`{sh['name']}\`: rows={sh['max_row']} cols={sh['max_column']} header={sh['header']}")
            L.append("")
    L += ["## Boundary","","Downloaded research bytes were used only for structural metadata extraction and discarded in the CI runner.",""]
    return "\n".join(L)

def main():
    out={"audit_version":1,"sources":[]}
    with tempfile.TemporaryDirectory() as td:
        tmp=pathlib.Path(td)
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            for src in SOURCES:
                try:
                    r=audit_source(browser,src,tmp); r["tokens"]=derive(r); out["sources"].append(r)
                except Exception as e:
                    out["sources"].append({"key":src["key"],"error":repr(e),"tokens":{}})
            browser.close()
    OUTJ.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
    OUTM.write_text(render(out)+"\n")
    print(OUTM.read_text())

if __name__=="__main__":
    main()
