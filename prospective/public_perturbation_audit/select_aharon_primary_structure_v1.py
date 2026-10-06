#!/usr/bin/env python3
"""Select the Aharon primary figure from structural metadata only.

Reads variable names/shapes/classes from PUBLIC_BROWSER_STRUCTURE_AUDIT_V1.json.
Never reads turning-point numeric values.
"""

from __future__ import annotations
import json, pathlib, re
from collections import defaultdict

HERE=pathlib.Path(__file__).resolve().parent
SRC=HERE/"PUBLIC_BROWSER_STRUCTURE_AUDIT_V1.json"
OUTJ=HERE/"AHARON_PRIMARY_STRUCTURAL_SELECTION_V1.json"
OUTM=HERE/"AHARON_PRIMARY_STRUCTURAL_SELECTION_V1.md"

TURN_RE=re.compile(r"^(?P<bat>\d+)_YRLturns_together_(?P<condition>.+)$",re.I)
FIG_RE=re.compile(r"Figure\s*([1-4])",re.I)

def walk(m,parent="",records=None):
    if records is None: records=[]
    name=m.get("name","")
    path=(parent+"/"+name).strip("/")
    st=m.get("structure") or {}
    if st.get("type")=="mat":
        figm=FIG_RE.search(path)
        fig=int(figm.group(1)) if figm else None
        for v in st.get("variables",[]):
            mm=TURN_RE.match(v.get("name",""))
            if mm and fig is not None:
                shape=v.get("shape") or []
                records.append({
                    "figure":fig,
                    "container_path":path,
                    "variable":v.get("name"),
                    "bat":mm.group("bat"),
                    "condition":mm.group("condition"),
                    "shape":shape,
                    "class":v.get("class") or v.get("dtype"),
                })
    for ch in st.get("members",[]):
        walk(ch,path,records)
    return records

def evaluate(records,fig):
    rr=[x for x in records if x["figure"]==fig]
    by=defaultdict(dict)
    for x in rr:
        by[x["condition"]][x["bat"]]=x
    conditions=sorted(by)
    if len(conditions)<2:
        return {"figure":fig,"eligible":False,"reason":"<2 conditions","conditions":conditions}
    common=set(by[conditions[0]])
    for c in conditions[1:]:
        common &= set(by[c])
    common=sorted(common)
    shape_ok=True
    bad=[]
    for c in conditions:
        for b in common:
            x=by[c][b]
            sh=x.get("shape") or []
            if len(sh)!=2 or sh[0]<2 or sh[1]<5:
                shape_ok=False; bad.append({"condition":c,"bat":b,"shape":sh})
    eligible=len(common)>=4 and shape_ok
    return {
        "figure":fig,
        "eligible":eligible,
        "conditions":conditions,
        "common_bats":common,
        "n_common_bats":len(common),
        "n_conditions":len(conditions),
        "shape_gate_ok":shape_ok,
        "bad_shapes":bad,
        "records":[x for x in rr if x["bat"] in common],
    }

def main():
    j=json.loads(SRC.read_text())
    ah=next((x for x in j["sources"] if x.get("key")=="aharon2017"),None)
    if not ah or not ah.get("download"):
        result={"status":"STOP_NO_AHARON_BROWSER_ARCHIVE","figures":[],"selected":None}
    else:
        records=[]
        for m in ah["download"]["archive"].get("members",[]):
            walk(m,"",records)
        figs=[evaluate(records,f) for f in (1,2,3,4)]
        selected=next((x for x in figs if x["eligible"]),None)
        result={
            "status":"STRUCTURAL_FIGURE_SELECTED_NEEDS_FINITE_MASK_AUDIT" if selected else "STOP_NO_STRUCTURALLY_IDENTIFIED_AHARON_PRIMARY",
            "figure_evaluations":figs,
            "selected":selected,
            "turning_variables_found":len(records),
        }
    OUTJ.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    L=["# Aharon primary structural selection v1","","## Status","",f"**{result['status']}**",""]
    L.append(f"- turning variables found: {result.get('turning_variables_found',0)}")
    for x in result.get("figure_evaluations",[]):
        L += [
            f"## Figure {x['figure']}","",
            f"- eligible: {x['eligible']}",
            f"- conditions: {', '.join(x.get('conditions') or []) or 'none'}",
            f"- common bats: {', '.join(x.get('common_bats') or []) or 'none'}",
            f"- n common bats: {x.get('n_common_bats')}",
            f"- shape gate: {x.get('shape_gate_ok')}",""
        ]
        for r in x.get("records",[]):
            L.append(f"- \`{r['variable']}\`: shape={r['shape']} class={r['class']}")
        L.append("")
    if result.get("selected"):
        L += ["## Selected primary figure","",f"**Figure {result['selected']['figure']}**","",
              "Selection used structure only. Numeric turning-point values remain unopened.",""]
    L += ["## Next gate","","Run a finite-mask-only audit under the frozen Aharon contract. Do not compute turn medians until that gate passes.",""]
    OUTM.write_text("\n".join(L)+"\n")
    print(OUTM.read_text())

if __name__=="__main__":
    main()
