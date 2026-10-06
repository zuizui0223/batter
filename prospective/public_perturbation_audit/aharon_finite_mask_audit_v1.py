#!/usr/bin/env python3
"""Aharon finite-mask support audit.

Reads selected totalTurns matrices only to count finite/zero/missing support.
Never emits nonzero turning magnitudes.
"""

from __future__ import annotations

import io
import json
import pathlib
import tempfile
import zipfile

import numpy as np
import scipy.io
from playwright.sync_api import sync_playwright

HERE=pathlib.Path(__file__).resolve().parent
SEL=HERE/"AHARON_PRIMARY_STRUCTURAL_SELECTION_V1.json"
OUTJ=HERE/"AHARON_FINITE_MASK_AUDIT_V1.json"
OUTM=HERE/"AHARON_FINITE_MASK_AUDIT_V1.md"

URL="https://data.mendeley.com/datasets/f6mvhj5gj9/3"


def accept_cookie(page):
    for name in ("Accept All","Accept all","Allow all","I agree","Accept"):
        try:
            loc=page.get_by_role("button",name=name)
            if loc.count():
                loc.first.click(timeout=1500)
                return
        except Exception:
            pass


def download_all(tmp):
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page(accept_downloads=True)
        page.goto(URL,wait_until="domcontentloaded",timeout=120000)
        page.wait_for_timeout(5000)
        accept_cookie(page)
        loc=None
        for sel in (
            'button:has-text("Download All")',
            'button:has-text("Download all")',
            'a:has-text("Download All")',
            'a:has-text("Download all")',
        ):
            q=page.locator(sel)
            if q.count():
                loc=q.first; break
        if loc is None:
            raise RuntimeError("Download All control not found")
        with page.expect_download(timeout=60000) as di:
            loc.click(timeout=10000)
        dl=di.value
        dest=tmp/dl.suggested_filename
        dl.save_as(str(dest))
        browser.close()
        return dest


def load_mat_from_bytes(data):
    with tempfile.NamedTemporaryFile(suffix=".mat") as tf:
        tf.write(data); tf.flush()
        m=scipy.io.loadmat(tf.name,variable_names=["totalTurns"])
    if "totalTurns" not in m:
        raise RuntimeError("totalTurns missing")
    arr=np.asarray(m["totalTurns"],dtype=float)
    if arr.ndim!=2:
        raise RuntimeError("totalTurns not 2-D")
    return arr


def audit_array(arr):
    finite=np.isfinite(arr)
    zeros=finite & (arr==0.0)
    rows,cols=arr.shape
    per=[]
    for j in range(cols):
        right=arr[0::2,j]
        left=arr[1::2,j]
        fr=np.isfinite(right)
        fl=np.isfinite(left)
        fnzr=fr & (right!=0.0)
        fnzl=fl & (left!=0.0)
        per.append({
            "trial_column":j+1,
            "finite_right":int(fnr:=fr.sum()),
            "finite_left":int(fnl:=fl.sum()),
            "finite_nonzero_right":int(fnzr.sum()),
            "finite_nonzero_left":int(fnzl.sum()),
            "finite_bilateral":bool(fnr>=1 and fnl>=1),
            "finite_nonzero_bilateral":bool(fnzr.sum()>=1 and fnzl.sum()>=1),
        })
    return {
        "shape":[rows,cols],
        "finite_cells":int(finite.sum()),
        "nonfinite_cells":int((~finite).sum()),
        "zero_cells":int(zeros.sum()),
        "finite_bilateral_trials":sum(x["finite_bilateral"] for x in per),
        "finite_nonzero_bilateral_trials":sum(x["finite_nonzero_bilateral"] for x in per),
        "trial_support":per,
    }


def main():
    sel=json.loads(SEL.read_text())
    selected=sel.get("selected")
    if not selected:
        result={"status":"STOP_NO_SELECTED_FIGURE","records":[]}
    else:
        fig=int(selected["figure"])
        expected={(r["bat"],r["condition"]):r for r in selected["records"]}
        result={"status":None,"figure":fig,"records":[]}
        with tempfile.TemporaryDirectory() as td:
            tmp=pathlib.Path(td)
            outer=download_all(tmp)
            with zipfile.ZipFile(outer) as oz:
                target=f"Figure {fig}.zip"
                candidates=[n for n in oz.namelist() if pathlib.Path(n).name.lower()==target.lower()]
                if len(candidates)!=1:
                    raise RuntimeError(f"expected one {target}, got {candidates}")
                nested=zipfile.ZipFile(io.BytesIO(oz.read(candidates[0])))
                for (bat,cond),meta in sorted(expected.items()):
                    suffix=f"{bat}_YRLturns_together_{cond}.mat".lower()
                    hits=[n for n in nested.namelist() if pathlib.Path(n).name.lower()==suffix]
                    if len(hits)!=1:
                        raise RuntimeError(f"file match {bat}/{cond}: {hits}")
                    arr=load_mat_from_bytes(nested.read(hits[0]))
                    aud=audit_array(arr)
                    result["records"].append({
                        "bat":bat,"condition":cond,"member":hits[0],**aud
                    })
        insufficient=[x for x in result["records"] if x["finite_bilateral_trials"]<5]
        zero_total=sum(x["zero_cells"] for x in result["records"])
        if insufficient:
            result["status"]="STOP_INSUFFICIENT_TRIAL_SUPPORT"
        elif zero_total>0:
            result["status"]="ZERO_ENCODING_NEEDS_FREEZE"
        else:
            result["status"]="PASS_FINITE_MASK_NUMERIC_PRIMARY_AUTHORIZED"
        result["zero_cells_total"]=zero_total

    OUTJ.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    L=["# Aharon finite-mask audit v1","","## Status","",f"**{result['status']}**",""]
    if result.get("figure"):
        L.append(f"- selected Figure: {result['figure']}")
    L.append(f"- total exact-zero cells: {result.get('zero_cells_total')}")
    L.append("")
    for r in result.get("records",[]):
        L += [
            f"## bat {r['bat']} / condition {r['condition']}","",
            f"- shape: {r['shape']}",
            f"- finite cells: {r['finite_cells']}",
            f"- nonfinite cells: {r['nonfinite_cells']}",
            f"- exact-zero cells: {r['zero_cells']}",
            f"- finite bilateral trial columns: {r['finite_bilateral_trials']}",
            f"- finite-nonzero bilateral trial columns: {r['finite_nonzero_bilateral_trials']}",""
        ]
    L += ["## Boundary","","No nonzero turning-point magnitude, mean, median, range, individual difference or condition difference is reported.",""]
    OUTM.write_text("\n".join(L)+"\n")
    print(OUTM.read_text())


if __name__=="__main__":
    main()
