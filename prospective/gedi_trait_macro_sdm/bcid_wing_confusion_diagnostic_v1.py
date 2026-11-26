"""Independent reference-call confusion graph; see BCID_WING_CONFUSION_CONTRACT_V1.md.
No inference of unreported outputs, no FWS correction, no publisher code execution.
"""
import collections,csv,hashlib,io,itertools,json,pathlib,re,zipfile
import numpy as np,pandas as pd,requests
O=pathlib.Path("bcid_wing_confusion");O.mkdir(exist_ok=True)
R={"stage":"BCID 2.8b reference-call label audit and wing confusion graph","status":"START","doi":"10.1371/journal.pone.0300664","new_fit":False,"limits":["Conditional on reported reference-file output; absent report rows are not classified noise/unknown by this script.","Selected reference calls, converted zero-crossing, one classifier and settings; no actual field detection kernel.","Trait-label permutation ignores phylogenetic dependence, source-specific recording dependence and other call traits. Not a causal test or inferential population p-value.","No transfer of confusion rates to FWS or Polesia."]}
PINS={"input_files_1.csv":"75136994ae7291ee8811d8eb7c66a4ab86a051eb0f3a7af08a9377788e72b198","Species Info.csv":"3e75c74542bad92e93f4340ef62f672b61a5fc850bcdf9e52072b2e15cabacba","zc_files_5.txt":"183ceb676bac8ce7b52b1dc646b23d96cb9ba8afe8f90d0bfef40ea106bee41d"}
ZIP="db6e0891953017cd2bc29fdfd50ebd09e51400ccd8dd13c7de6e09639df33508"
TRAITS="99a19c169e18a0bafa4a518b7f844b56d2fe846cac13d5c035f4eae562a74c7b"
def sha(b):return hashlib.sha256(b).hexdigest()
def save():
    s=json.dumps(R,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else x.tolist() if isinstance(x,np.ndarray) else None)
    (O/"report.json").write_text(s+"\n")
    print("BCID_WING_REPORT="+s,flush=True)
def source():
    # Public original S4 ZIP; verify pinned bytes then read only.
    u="https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0300664.s004"
    with requests.get(u,stream=True,timeout=(15,45),headers={"Accept-Encoding":"identity"}) as q:
        q.raise_for_status();a=bytearray()
        for b in q.iter_content(65536):
            a.extend(b);assert len(a)<=1000000
    raw=bytes(a);assert sha(raw)==ZIP
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        out={}
        for k,v in PINS.items():
            p=z.read("PLOS_script/"+k);assert sha(p)==v
            out[k]=p.decode("utf-8-sig",errors="strict")
        code=z.read("PLOS_script/PLOS_script.r")
        R["source"]={"zip_bytes":len(raw),"zip_sha256":ZIP,"table_sha256":PINS,"publisher_R_source_sha256":sha(code),"publisher_code_executed":False}
        # Preserve relevant public processing statements only as semantic
        # breadcrumbs; do not run code or emit paths or filenames.
        lines=code.decode("utf-8-sig",errors="replace").splitlines()
        match=[i for i,x in enumerate(lines) if re.search(r"zc_files_5|input_files_1|BCID",x,re.I)]
        R["publisher_script_BCID_reference_lines"]=len(match)
        R["publisher_script_contains_reference_input"]=any("input_files_1" in x for x in lines)
        R["publisher_script_contains_BCID_output"]=any("zc_files_5" in x for x in lines)
        save()
    return out
def main():
    d=source()
    sp=pd.read_csv(io.StringIO(d["Species Info.csv"]),dtype=str,keep_default_na=False)
    assert len(sp)==9 and sp.abbv.is_unique and sp["Genus species"].is_unique
    codes=sp.abbv.str.strip().tolist();names=dict(zip(codes,sp["Genus species"].str.strip()))
    assert len(codes)==9 and all(re.fullmatch(r"[A-Z]{4}",c) for c in codes)
    assert all(re.fullmatch(r"[A-Z][a-z]+ [a-z]+",n) for n in names.values())
    ins=list(csv.reader(io.StringIO(d["input_files_1.csv"])))
    assert len(ins)==1500 and all(len(x)==1 for x in ins)
    orig={}
    for row in ins:
        # This is a reference-file key, never emitted to output.
        m=re.fullmatch(r"([A-Z]+_[0-9]+)\.wav",row[0].strip(),re.I)
        assert m,"unrecognized reference filename convention"
        k=m[1].upper();assert k not in orig
        code=k.split("_")[0];assert code in set(codes)|{"NOISE"}
        orig[k]=code
    truth=collections.Counter(orig.values());assert truth["NOISE"]==380 and sum(truth[c] for c in codes)==1120
    header=["FILENAME","SPECIES","SP PERCENT","GROUP","GR PERCENT","TOTAL PULSES","DISC PROB","FOLDER"]
    rows={};odd=collections.Counter()
    for line in d["zc_files_5.txt"].splitlines():
        a=line.split("\t")
        if a==header:odd["headers"]+=1;continue
        if not a[0].strip().lower().endswith(".zc"):
            odd["non_data_lines"]+=1;continue
        assert len(a)==8,"unexpected report column count"
        m=re.fullmatch(r"([A-Z]+_[0-9]+)(?:_[0-9]+_[0-9]+)?\.zc",a[0].strip(),re.I)
        if not m:odd["unrecognized_report_keys"]+=1;continue
        k=m[1].upper()
        if k not in orig:odd["unmatched_report_keys"]+=1;continue
        assert k not in rows,"duplicate BCID reference key"
        # Folder and independent input-file reference label must agree.
        actual=orig[k];folder=a[7].strip().upper()
        if folder!=actual:odd["folder_reference_disagreement"]+=1;continue
        pred=a[1].strip().upper()
        rows[k]=pred if pred else "EMPTY_REPORTED_LABEL"
    R["reference_reconciliation"]={"reference_total":len(orig),"true_counts":dict(truth),"matched_output_rows":len(rows),"omitted_reference_rows":len(orig)-len(rows),"omitted_by_true_label":dict(collections.Counter(orig[k] for k in orig if k not in rows)),"report_structure":dict(odd),"predicted_labels":dict(collections.Counter(rows.values()))}
    save()
    assert not any(odd[k] for k in ["unrecognized_report_keys","unmatched_report_keys","folder_reference_disagreement"])
    assert len(rows)>0
    # Keep all explicit predicted categories, including unknown/empty/noise.
    matrix={c:dict(collections.Counter(p for k,p in rows.items() if orig[k]==c)) for c in codes+["NOISE"]}
    R["reported_confusion_counts"]=matrix;R["reference_metrics"]={}
    for c in codes:
        q=matrix[c];n=sum(q.values())
        R["reference_metrics"][names[c]]={"reference_files":truth[c],"reported_rows":n,"correct_reported":q.get(c,0),"conditional_correct_fraction":q.get(c,0)/n if n else None,"wrong_named":sum(q.get(k,0) for k in codes if k!=c),"other_reported":sum(v for k,v in q.items() if k not in codes)}
    p=pathlib.Path("wing/primary_LSA_physical.csv");assert sha(p.read_bytes())==TRAITS
    t=pd.read_csv(p).set_index("scientificName.iucn");assert len(t)==280 and t.index.is_unique
    cc=[c for c in codes if names[c] in t.index];n=len(cc)
    R["trait_match"]={"matched_taxa":n,"names":[names[c] for c in cc],"unmatched_names":[names[c] for c in codes if c not in cc]}
    M=np.array([[matrix[c].get(k,0) if k!=c else 0 for k in cc] for c in cc],dtype=int)
    row=M.sum(1);active=row>0;wrong=int(M.sum())
    R["graph_support"]={"matched_taxa":n,"active_true_taxa":int(active.sum()),"wrong_named_matched_calls":wrong,"retained_wrong_named_call_fraction":wrong/max(1,sum(R["reference_metrics"][names[c]]["wrong_named"] for c in codes))}
    if n<6 or active.sum()<5 or wrong<30:
        R["status"]="STOP_INSUFFICIENT_CONFUSION_GRAPH_SUPPORT";save();return
    X=t.loc[[names[c] for c in cc],["AR","WL_N_m2","mass_g_physical"]].to_numpy(float)
    assert np.isfinite(X).all() and (X>0).all()
    X[:,1:]=np.log(X[:,1:]);sd=X.std(0);assert (sd>0).all()
    X=(X-X.mean(0))/sd
    D=np.sqrt(((X[:,None,:]-X[None,:,:])**2).sum(2))
    W=np.zeros_like(M,dtype=float);W[active]=M[active]/row[active,None]/active.sum()
    assert np.isclose(W.sum(),1)
    observed=float((W*D).sum())
    null=[];gen=itertools.permutations(range(n))
    while True:
        batch=list(itertools.islice(gen,4096))
        if not batch:break
        idx=np.array(batch);a=D[idx[:,:,None],idx[:,None,:]]
        null.extend((a*W[None,:,:]).sum((1,2)).tolist())
    v=np.array(null)
    import math
    assert len(v)==math.factorial(n)
    R["graph_result"]={"observed_equal_species_weighted_trait_distance":observed,"permutation_mean":float(v.mean()),"difference_observed_minus_null":float(observed-v.mean()),"permutation_quantiles":np.quantile(v,[.025,.5,.975]).tolist(),"exact_lower_tail_fraction":float((v<=observed+1e-12).mean()),"permutations":len(v)}
    R["status"]="COMPLETE_DESCRIPTIVE_CONFUSION_GRAPH_ONLY";save()
if __name__=="__main__":
    try:main()
    except Exception as e:R.update(status="INCOMPLETE",error_type=type(e).__name__,error=str(e)[:160]);save();raise
