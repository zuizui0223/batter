"""Bounded anonymous GFZ V3 actual GEDI PAVD query on deterministic candidate cells.
Source/schema and shot coverage only; no ecological outcome or model fit."""
import collections,hashlib,importlib.metadata,json,math,pathlib,sys
import numpy as np,pandas as pd,geopandas as gpd
from shapely.geometry import box
from pyproj import Transformer
import gedidb as gdb
OUT=pathlib.Path("gedidb_v3_pavd_gate");OUT.mkdir(exist_ok=True)
SRC=pathlib.Path("pilot/species_cell_source_year_environment.csv.gz")
PIN="5bd65cd8c56bac84c033a4972064622c172554a676d198868ef0776c49a2786b"
BUCKET="dog-ext--gedidb--gedi-l2-l4-v003"
ENDPOINT="https://s3.gfz.de"
UPSTREAM="cb42331f86fd64e4e9d4b9e5ecac7abadb6c2cd9"
START="2019-04-17";END="2023-03-16"
FIELDS=["pavd_z","rh:98","pai","cover","dz","l2a_quality_flag_rel3","l2b_quality_flag_rel3","degrade_flag","sensitivity"]
report={"stage":"public actual GEDI footprint V3 preflight, no ecological fit","status":"START","source_endpoint":ENDPOINT,"source_bucket":BUCKET,"source_software_doi":"10.5281/zenodo.13885229","upstream_commit":UPSTREAM,"input_sha256":PIN,"date_range":[START,END],"fields":FIELDS,"query_budget_cells":12,"query_budget_shots":200000,"original_ORNL_V2_admitted":False,"main_sdm_admitted":False,"cells":[],"limits":["V3 shot-level public database, not original V2 ORNL 2339 gridded product.","Basic source quality checks are not the full original leaf-on, terrain, coverage, water and land filtering.","PAVD bin labels retained; no inferred lower allocation, biological occupancy or flight altitude.","Twelve deterministic cells are an engineering preflight, not a representative regional survey."]}
def sha(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def serial(v):
    if isinstance(v,np.generic):return v.item()
    raise TypeError(type(v).__name__)
def save():
    (OUT/"report.json").write_text(json.dumps(report,indent=2,allow_nan=False,default=serial)+"\n")
    print("GEDIDB_PAVD_REPORT="+json.dumps(report,allow_nan=False,default=serial),flush=True)
def hashkey(v):
    return hashlib.sha256(str(v).encode()).hexdigest()
def main():
    assert sha(SRC)==PIN
    report["software"]={k:importlib.metadata.version(k) for k in ("gedidb","tiledb","numpy","pandas","pyproj","geopandas")}
    try:
        d=importlib.metadata.distribution("gedidb").read_text("direct_url.json")
        info=json.loads(d) if d else {}
        assert info.get("vcs_info",{}).get("commit_id")==UPSTREAM,"upstream installed commit not pinned"
        report["upstream_installed_commit_verified"]=True
    except (ValueError,AttributeError):
        raise ValueError("upstream installation provenance missing")
    roster=sorted(["5218524","5218507","2432439","5218522","2432359","5218471","5218464","2432389","2432416","2432655","2432614","2432470","9754263","2432564"])
    f=pd.read_csv(SRC,dtype={"species_key":str,"dataset_key":str,"year":str},keep_default_na=False,low_memory=False)
    f=f[f.forest_profile_support.astype(str).str.lower().eq("true")&f.species_key.isin(roster)&f.dataset_key.ne("")&f.year.str.fullmatch(r"20[0-9]{2}")]
    u=f[["cell_x","cell_y"]].drop_duplicates()
    assert len(u)==1796
    I=Transformer.from_crs(6933,4326,always_xy=True);P=Transformer.from_crs(4326,6933,always_xy=True)
    bb=collections.defaultdict(list)
    for x,y in u.itertuples(index=False,name=None):
        x,y=int(x),int(y);_,latlo=I.transform(0,y*1000);_,lathi=I.transform(0,(y+1)*1000)
        if -51.6<=latlo<=lathi<=51.6:bb[(x//200,y//200)].append((x,y))
    chosen=[min(bb[b],key=hashkey) for b in sorted(bb,key=hashkey)[:12]]
    assert len(chosen)==12
    report["in_domain_candidate_cells"]=sum(map(len,bb.values()))
    report["candidate_blocks"]=len(bb)
    report["selection_hash"]=hashkey(chosen);save()
    provider=gdb.GEDIProvider(storage_type="s3",s3_bucket=BUCKET,url=ENDPOINT,config_overrides={"vfs.s3.no_sign_request":"true","vfs.s3.connect_timeout_ms":"15000","vfs.s3.request_timeout_ms":"90000","vfs.s3.max_parallel_ops":"4","sm.compute_concurrency_level":"4","sm.io_concurrency_level":"4","py.init_buffer_bytes":"1048576"})
    try:
        metadata=provider.get_available_variables()
        need={v.split(":")[0] for v in FIELDS}
        assert need.issubset(set(metadata.index)),f"missing documented variables: {sorted(need-set(metadata.index))}"
        m=metadata.loc[sorted(need)].fillna("").astype(str)
        report["source_metadata"]={k:{str(c):str(x)[:800] for c,x in row.items() if x!=""} for k,row in m.iterrows()}
        pp=report["source_metadata"]["pavd_z"];rr=report["source_metadata"]["rh"]
        # Named labels from actual public array metadata, not inferred by array position.
        labels=[int(float(x)) for x in pp["profile_labels"].split(",")]
        rhlabels=[int(float(x)) for x in rr["profile_labels"].split(",")]
        assert labels==list(range(0,150,5)) and 98 in rhlabels
        report["pavd_profile_labels_m"]=labels
        report["status"]="PUBLIC_SCHEMA_READY";save()
        total=0
        for i,(x,y) in enumerate(chosen):
            rec={"index":i+1,"cell_hash":hashkey((x,y)),"status":"QUERY_START"}
            report["cells"].append(rec);save()
            l,b=I.transform(x*1000,y*1000);r,t=I.transform((x+1)*1000,(y+1)*1000)
            roi=gpd.GeoDataFrame(geometry=[box(l,b,r,t)],crs="EPSG:4326")
            data=provider.get_data(variables=FIELDS,geometry=roi,start_time=START,end_time=END,query_type="bounding_box",return_type="dataframe")
            if data is None or len(data)==0:
                rec.update(status="NO_RETURNED_SHOTS",returned_shots=0,in_cell_shots=0,basic_quality_shots=0,complete_first16_shots=0,complete_full30_shots=0,pass10=False,pass25=False)
                save();continue
            total+=len(data)
            if total>200000:raise ValueError("predeclared shot budget exceeded")
            required={"latitude","longitude","time","shot_number","pavd_z","rh_p98",*FIELDS[2:]}
            assert required.issubset(data.columns),f"returned schema lacks fields {sorted(required-set(data.columns))}"
            rec["returned_shots"]=int(len(data))
            xx,yy=P.transform(data.longitude.to_numpy(float),data.latitude.to_numpy(float))
            time=pd.to_datetime(data.time,errors="coerce",utc=True)
            valid=(np.isfinite(xx)&np.isfinite(yy)&(xx>=x*1000)&(xx<(x+1)*1000)&(yy>=y*1000)&(yy<(y+1)*1000)&time.ge(pd.Timestamp(START,tz="UTC"))&time.lt(pd.Timestamp(END,tz="UTC")+pd.Timedelta(days=1)))
            data=data.loc[valid].copy()
            assert data.shot_number.notna().all()
            rec["in_cell_rows"]=int(len(data));rec["duplicate_shot_ids"]=int(data.shot_number.duplicated().sum())
            if rec["duplicate_shot_ids"]:raise ValueError("duplicate shot identifiers within queried cell")
            rec["in_cell_shots"]=int(len(data))
            if not len(data):
                rec.update(status="NO_IN_CELL_SHOTS",basic_quality_shots=0,complete_first16_shots=0,complete_full30_shots=0,pass10=False,pass25=False);save();continue
            prof=np.asarray(data.pavd_z.tolist(),dtype=float)
            assert prof.shape==(len(data),30)
            q=(data.l2a_quality_flag_rel3.eq(1)&data.l2b_quality_flag_rel3.eq(1)&data.degrade_flag.eq(0)&data.sensitivity.between(.9,1)).to_numpy(bool)
            ok=np.isfinite(prof)&(prof>=0)
            first=ok[:,:16].all(1)
            full=ok.all(1)
            dz=pd.to_numeric(data.dz,errors="coerce").to_numpy(float)
            pai=pd.to_numeric(data.pai,errors="coerce").to_numpy(float)
            cover=pd.to_numeric(data.cover,errors="coerce").to_numpy(float)
            rh=pd.to_numeric(data.rh_p98,errors="coerce").to_numpy(float)
            physical=np.isfinite(pai)&(pai>=0)&np.isfinite(cover)&(cover>=0)&(cover<=100)&np.isfinite(rh)&(rh>=0)&(rh<=150)&np.isfinite(dz)&np.isclose(dz,5)
            use=q&first&physical
            rec.update(status="ACTUAL_PAVD_SHOTS_READ",basic_quality_shots=int(q.sum()),complete_first16_shots=int((q&first).sum()),complete_full30_shots=int((q&full).sum()),joint_basic_profile_scalar_support=int(use.sum()),quality_dz5_shots=int((q&np.isclose(dz,5)).sum()),quality_pavd_nonnegative_bin_counts=ok[q].sum(0).astype(int).tolist(),pass10=bool(use.sum()>=10),pass25=bool(use.sum()>=25))
            if use.any():
                rec["mean_first16_pavd"]=prof[use,:16].mean(0).tolist()
                rec["mean_pai"]=float(pai[use].mean());rec["mean_rh98_m"]=float(rh[use].mean())
                rec["mean_cover_source_units"]=float(cover[use].mean())
            if (q&full&physical).any():
                v=q&full&physical
                rec["complete_profile_sum_vs_pai_abs_median"]=float(np.median(np.abs(5*prof[v].sum(1)-pai[v])))
            save()
        report["summary"]={"queried_cells":len(report["cells"]),"returned_shots":sum(v["returned_shots"] for v in report["cells"]),"in_cell_shots":sum(v["in_cell_shots"] for v in report["cells"]),"basic_quality_shots":sum(v["basic_quality_shots"] for v in report["cells"]),"joint_complete_first16_scalar_shots":sum(v.get("joint_basic_profile_scalar_support",0) for v in report["cells"]),"cells_pass10":sum(v["pass10"] for v in report["cells"]),"cells_pass25":sum(v["pass25"] for v in report["cells"])}
        report["status"]="PUBLIC_ACTUAL_PAVD_SOURCE_READY" if report["summary"]["joint_complete_first16_scalar_shots"]>0 else "PUBLIC_SOURCE_READ_NO_JOINT_PROFILE_SUPPORT"
        save()
    finally:
        provider.close()
try:main()
except Exception as e:
    report.update(status="STOP",error_type=type(e).__name__,error=str(e)[:250]);save();raise
