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
            # Structural audit only: never emit numeric/formula values.
            string_cells=[]
            for row in ws.iter_rows(min_row=1,max_row=min(ws.max_row or 1,5)):
                for cell in row:
                    if isinstance(cell.value,str) and cell.value.strip():
                        string_cells.append({
                            "row":cell.row,
                            "column":cell.column,
                            "value":cell.value[:200],
                        })
            out["sheets"].append({
                "name":ws.title,
                "max_row":ws.max_row,
                "max_column":ws.max_column,
                "string_cells_first5rows":string_cells[:100],
            })
    return out


def inspect_member_bytes(data,name,depth=0):
    ext=pathlib.Path(name).suffix.lower()
    rec={"name":name,"size":len(data)}
    try:
        if ext==".mat":
            rec["structure"]=mat_structure(data,name)
        elif ext==".m":
            rec["structure"]=m_structure(data,name)
        elif ext in {".xlsx",".xlsm"}:
            rec["structure"]=xlsx_structure(data,name)
        elif ext==".zip" and depth < 3:
            rec["structure"]={"type":"nested_zip","members":[]}
            with zipfile.ZipFile(io.BytesIO(data)) as nz:
                for ni in nz.infolist():
                    child={"name":ni.filename,"size":ni.file_size}
                    child_ext=pathlib.Path(ni.filename).suffix.lower()
                    if child_ext in {".mat",".m",".xlsx",".xlsm",".zip"} and ni.file_size <= 250_000_000:
                        child_data=nz.read(ni)
                        child=inspect_member_bytes(child_data,ni.filename,depth+1)
                    rec["structure"]["members"].append(child)
    except Exception as e:
        rec["structure_error"]=repr(e)
    return rec


def inspect_archive(path):
    result={"archive_name":path.name,"members":[]}
    if not zipfile.is_zipfile(path):
        result["error"]="download_not_zip"
        return result
    with zipfile.ZipFile(path) as z:
        for info in z.infolist():
            ext=pathlib.Path(info.filename).suffix.lower()
            if ext in {".mat",".m",".xlsx",".xlsm",".zip"} and info.file_size <= 250_000_000:
                data=z.read(info)
                result["members"].append(inspect_member_bytes(data,info.filename,0))
            else:
                result["members"].append({"name":info.filename,"size":info.file_size})
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
    def walk_member(m):
        names.append(m.get("name",""))
        st=m.get("structure") or {}
        for v in st.get("variables",[]):
            names.append(v.get("name",""))
        names.extend(st.get("relevant_identifiers",[]))
        names.extend(x.get("filename","") for x in st.get("data_file_references",[]))
        for ch in st.get("members",[]):
            walk_member(ch)
    if src.get("download") and src["download"].get("archive"):
        for m in src["download"]["archive"].get("members",[]):
            walk_member(m)
    text=" ".join(names)
    nums=sorted(set(re.findall(r"(?<![A-Za-z])(?:bat[_-]?)?(\d{2,4})(?![A-Za-z])",text,re.I)))
    cond=sorted(set(x for x in names if re.search(r"(turn|slow|speed|wind|con|condition|noise|prey|land|flight)",x,re.I)))[:500]
    return {"numeric_bat_tokens":nums[:300],"condition_like_tokens":cond}


def render_member(m,L,level=3):
    prefix="#"*min(level,6)
    L.append(f"{prefix} {m.get('name')}")
    L.append(f"- bytes: {m.get('size')}")
    st=m.get("structure") or {}
    if st.get("type")=="mat":
        L.append(f"- MAT variables: {len(st.get('variables') or [])}")
        for v in (st.get("variables") or [])[:300]:
            L.append(f"  - \`{v.get('name')}\` shape={v.get('shape')} class={v.get('class') or v.get('dtype')}")
    elif st.get("type")=="matlab_script":
        L.append("- relevant identifiers: "+", ".join(st.get("relevant_identifiers") or []))
        for r in st.get("data_file_references") or []:
            L.append(f"  - data reference: {r}")
    elif st.get("type")=="xlsx":
        for sh in st.get("sheets") or []:
            L.append(
                f"  - sheet \`{sh['name']}\`: rows={sh['max_row']} cols={sh['max_column']} "
                f"string_cells_first5rows={sh['string_cells_first5rows']}"
            )
    elif st.get("type")=="nested_zip":
        L.append(f"- nested members: {len(st.get('members') or [])}")
        for child in st.get("members") or []:
            render_member(child,L,level+1)
    if m.get("structure_error"):
        L.append(f"- structure error: {m['structure_error']}")
    L.append("")


def render(res):
    L=["# Public browser structural audit v1","","## Status","",
       "**PUBLIC DOWNLOAD-ALL STRUCTURE ONLY; NO NUMERIC OUTCOMES REPORTED BY V2 AUDITOR.**",""]
    for s in res["sources"]:
        L += [f"## {s['key']}","",f"- page title: {s.get('title')}",f"- error: {s.get('error')}"]
        dl=s.get("download") or {}
        ar=dl.get("archive") or {}
        L += [f"- archive: {dl.get('suggested_filename')}",f"- archive bytes: {dl.get('size')}",
              f"- archive members: {len(ar.get('members') or [])}"]
        toks=s.get("tokens") or {}
        L += [f"- numeric bat-like tokens: {', '.join(toks.get('numeric_bat_tokens') or []) or 'none'}",
              f"- condition-like tokens: {len(toks.get('condition_like_tokens') or [])}",""]
        for m in (ar.get("members") or [])[:500]:
            render_member(m,L,3)
    L += ["## Boundary","",
          "Research files were used only for structural metadata extraction and discarded in the CI runner.",
          "For Ma 2025, the first V1 audit accidentally emitted numeric row-1 values from two amplitude spreadsheets; those endpoints are quarantined in STRUCTURAL_AUDIT_NUMERIC_OPENING_INCIDENT_V1.md.",""]
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
