"""Release replay: fixed input ZIPs, original analysis code, matched aggregate receipts.
No source reacquisition or changes to ecological estimands. No raw rows exported."""
import hashlib,json,os,pathlib,subprocess,sys,zipfile,shutil,math
import requests,numpy,pandas,scipy
R=pathlib.Path(__file__).resolve().parent
O=pathlib.Path("paper_replay");O.mkdir(exist_ok=True)
W=pathlib.Path("replay_work");W.mkdir(exist_ok=True)
repo=os.environ["GITHUB_REPOSITORY"];assert repo=="zuizui0223/batter"
token=os.environ["GH_TOKEN"]
report={"status":"START","scope":"independent ZIP rehash and clean replay of four core recorded-label analyses, no new model","environment":{"python":sys.version.split()[0],"numpy":numpy.__version__,"pandas":pandas.__version__,"scipy":scipy.__version__},"inputs":{},"analyses":{}}
def sha(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def load(p):return json.loads(pathlib.Path(p).read_text())
def save():
    (O/"report.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print("PAPER_REPLAY_REPORT="+json.dumps(report,allow_nan=False),flush=True)
inputs=[
("common_forest",15007174727,"a5a08ae265f9729cd0b57f820b88b8440199288749006cb14dd82ee38616cbbb"),
("fixed_environment",15012939978,"afca6bf11fe5a75d7638a49de73b2cba1874e75d8cb24ed3f65c28957f25650a"),
("holdout",15010764600,"4ce5c239b1ad442d83b4861b899c504e40dfb02bb1a0c5e9ef335a650b34460c"),
("observation",15012136742,"053567fa0cc43993aec472a3c5bc966a2c6df5306767e66ff6d65f826a7cf900"),
("traits",15005261316,"7ed2df73b812f51f6376590136c79fb5acf42b41395e4e3f68830fb66120b490"),
("physical",15004406365,"3866df0cc71e1e5556162d26f9a757b7f31b0edddc339c1105ba7bd47e197408")]
def download(name,aid,pin):
    url=f"https://api.github.com/repos/{repo}/actions/artifacts/{aid}/zip"
    dest=W/(name+".zip");h=hashlib.sha256();n=0
    # Requests strips auth on cross-host redirects. Never log signed URLs or response text.
    with requests.get(url,headers={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"},stream=True,timeout=(20,90)) as r:
        if r.status_code!=200:raise RuntimeError(f"artifact {aid} HTTP {r.status_code}")
        with dest.open("wb") as f:
            for b in r.iter_content(1024*1024):
                n+=len(b)
                if n>50_000_000:raise ValueError("artifact budget exceeded")
                h.update(b);f.write(b)
    assert h.hexdigest()==pin,f"archive digest mismatch: {name}"
    out=W/name;out.mkdir()
    with zipfile.ZipFile(dest) as z:
        assert sum(i.file_size for i in z.infolist())<200_000_000
        for i in z.infolist():
            p=out/i.filename
            if not p.resolve().is_relative_to(out.resolve()):raise ValueError("unsafe zip path")
        z.extractall(out)
    dest.unlink()
    report["inputs"][name]={"artifact_id":aid,"archive_bytes":n,"sha256":h.hexdigest(),"archive_digest_verified":True}
    print("REPLAY_INPUT_VERIFIED",name,n,flush=True)
def compare(got,expected):
    """All originally reported comparable numeric fields, skip optimization stopping details.
    Expected receipts contain audit annotations and derived summaries not in original replay."""
    checks={"numeric":0,"other":0,"max_abs_numeric_difference":0.0}
    def visit(a,b,p):
        if isinstance(a,dict):
            if not isinstance(b,dict):raise ValueError("type mismatch "+p)
            for k,v in a.items():
                if k in ("optimizers","gradient_max_abs_error","output_sha256"):continue
                if k not in b:raise ValueError("unexpected field "+p+"/"+k)
                visit(v,b[k],p+"/"+k)
        elif isinstance(a,list):
            if not isinstance(b,list) or len(a)!=len(b):raise ValueError("length mismatch "+p)
            for i,(x,y) in enumerate(zip(a,b)):visit(x,y,p+"/"+str(i))
        elif isinstance(a,(int,float)) and not isinstance(a,bool):
            if not isinstance(b,(int,float)):raise ValueError("numeric type mismatch "+p)
            err=abs(a-b);checks["max_abs_numeric_difference"]=max(checks["max_abs_numeric_difference"],err)
            # Counts exact, continuous estimates tolerant only to floating point solver precision.
            if isinstance(a,int) and isinstance(b,int):
                if a!=b:raise ValueError("integer mismatch "+p)
            elif not math.isclose(a,b,rel_tol=1e-7,abs_tol=2e-7):raise ValueError("estimate mismatch "+p)
            checks["numeric"]+=1
        else:
            if a!=b:raise ValueError("value mismatch "+p)
            checks["other"]+=1
    visit(got,expected,"")
    return checks
cases=[
("observed_label_sorting_v1.py","1b7dd6768aad0735778ffd3744aa764643f2eb48","observed_label_sorting","OBSERVED_LABEL_SORTING_RECEIPT_V1.json"),
("sorting_transfer_diagnostic_v1.py","1ca160c5a1fe179e2f721ec3f4753a28a05d7e59","sorting_transfer_diagnostic","OBSERVED_LABEL_TRANSFER_RECEIPT_V1.json"),
("fixed_snapshot_profile_validation_v1.py","23cfa845156dd8db8abf8051e666d1f4f449a4e4","fixed_profile_validation","FIXED_SNAPSHOT_PROFILE_VALIDATION_RECEIPT_V1.json"),
("fixed_northern_transfer_v1.py","f25d1d25b923e5cb8ce108bc9da4c3cbbd1a60e3","northern_transfer","FIXED_NORTHERN_TRANSFER_RECEIPT_V1.json")]
try:
    for x in inputs:download(*x)
    for a,b in [("pilot","common_forest"),("environment","fixed_environment"),("audit","observation")]:
        (W/a).symlink_to(b,target_is_directory=True)
    for script,pin,out,receipt in cases:
        p=R/script
        assert subprocess.check_output(["git","hash-object",str(p)],text=True).strip()==pin,script
        result=subprocess.run([sys.executable,str(p.resolve())],cwd=W,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=480)
        if result.returncode:
            # No raw source data or signed URL; only exception category and exit code.
            raise RuntimeError("replay failed: "+script+" exit "+str(result.returncode))
        got=load(W/out/"report.json");expected=load(R/receipt)
        # Northern archived log intentionally omitted nested per-species support lists;
        # check those independently for sums and omit ONLY these lists in the comparison.
        if out=="northern_transfer":
            for domain in got["coverage"].values():
                for v in domain.values():
                    sp=v.pop("species_support")
                    assert sum(s["pass"] for s in sp)==v["species_passing"]
                    assert sum(s["cells"] for s in sp)==v["species_cells"]
        checks=compare(got,expected)
        report["analyses"][out]={"script_blob":pin,**checks,"status":"MATCH","result_sha256":sha(W/out/"report.json")}
        print("REPLAY_ANALYSIS_MATCH",out,checks,flush=True)
        save()
    report["status"]="CORE_REPLAY_MATCH"
except Exception as e:
    report["status"]="STOP";report["error_type"]=type(e).__name__
    report["error"]=str(e)[:200] if not isinstance(e,requests.RequestException) else "transport exception; no URL logged"
    save();raise
save()
