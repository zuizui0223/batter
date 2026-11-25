"""Reacquire hash-locked public FWS Access database, read only relevant tables.
Coordinates and source filenames stay private to runner; only aggregate QC output.
No interpreted detector effort or <=500m accuracy from coordinate presence alone.
"""
import collections,datetime as dt,hashlib,json,math,pathlib,re
import numpy as np,pandas as pd
from pyproj import Transformer
import fws_mobile_acoustic_source_gate_v1 as src
OUT=pathlib.Path("fws_relation_audit");OUT.mkdir(exist_ok=True)
PIN="adc036ca0e0b8f822925db22151562b01321ab61fc7d9c611aca21257da9b490"
R={"stage":"FWS call-event join and candidate geographic support only","source_sha256":PIN,"status":"START","limits":["Candidate valid coordinates are not verified <=500m spatial uncertainty.","GPS time difference, route length units and QA flag semantics need original documentation; no invented effort or accuracy.","No pooling with other archives or fitting biological model.","Route survey data and stationary detection records have different observation processes."]}
def save():
    (OUT/"report.json").write_text(json.dumps(R,indent=2,allow_nan=False))
    print("FWS_RELATION_REPORT="+json.dumps(R,allow_nan=False),flush=True)
def read(name,columns):
    import csv,io
    raw=src.call("mdb-export",str(src.P),name,timeout=120)
    reader=csv.reader(io.StringIO(raw))
    header=next(reader);assert len(set(header))==len(header)
    assert set(columns)<=set(header),(name,"missing fields")
    idx=[header.index(k) for k in columns];rows=[];bad=0
    for v in reader:
        if len(v)!=len(header):bad+=1;continue
        rows.append([v[i] for i in idx])
    expected=int(src.call("mdb-count",str(src.P),name,timeout=120).strip())
    R.setdefault("source_row_reconciliation",{})[name]={"mdb_count":expected,"csv_records":len(rows),"malformed_records":bad}
    save()
    assert bad==0 and len(rows)==expected,(name,expected,len(rows),bad)
    return pd.DataFrame(rows,columns=columns,dtype=str)
def text(d,k):
    return d[k].fillna("").astype(str).str.strip()
def dates(s):
    return pd.to_datetime(s,format="mixed",errors="coerce").dt.normalize()
def bucket(s,max_categories=30):
    c=s.fillna("").astype(str).str.strip().value_counts()
    if len(c)>max_categories:return {"distinct":len(c),"empty":int(c.get("",0))}
    return {k:int(v) for k,v in c.items()}
def num(s):return pd.to_numeric(s,errors="coerce")
def main():
    src.acquire();assert src.R["source_sha256"]==PIN and src.R["original_bytes"]==65941504
    e=read("tbl_Events",["Event_ID","Location_ID","Date Start","Time Start","Time End","Rt Compl","Surv Rte Compl","Data OK","Data Rev","Data No OK","Route_length","CountSurveyNight","QAQC_Metadata","QAQC_GPS","QAQC_BatData","SoftwareVersion","BCIDSpeciesFilter"])
    c=read("tbl_BatCallID_Classification",["Data_ID","Event_ID","LAT","LONG","Date Start","Time","FILENAME","Call_ID","A_SP","A_Spper","A_Grp","A_Grpper","A_pulse","A_Dprob","A_ID","gps_diff","Count"])
    t=read("tlu_Species_BatCallID",["A_SP","Genus","Species","Full Species Name"])
    assert (len(e),len(c),len(t))==(1277,57471,18),(len(e),len(c),len(t))
    e["Event_ID"]=text(e,"Event_ID");c["Event_ID"]=text(c,"Event_ID")
    R["event_keys"]={"rows":len(e),"nonempty":int(e.Event_ID.ne("").sum()),"unique":int(e.Event_ID.nunique()),"duplicated_nonempty":int((e.Event_ID.ne("")&e.Event_ID.duplicated(False)).sum())}
    assert e.Event_ID.ne("").all() and not e.Event_ID.duplicated().any()
    e["event_date"]=dates(e["Date Start"])
    c["call_date"]=dates(c["Date Start"])
    R["date_parse"]={"event_valid":int(e.event_date.notna().sum()),"call_valid":int(c.call_date.notna().sum()),"event_years":{str(int(k)):int(v) for k,v in e.event_date.dt.year.dropna().value_counts().sort_index().items()},"call_years":{str(int(k)):int(v) for k,v in c.call_date.dt.year.dropna().value_counts().sort_index().items()}}
    lo=pd.Timestamp("2019-04-17");hi=pd.Timestamp("2023-03-16")
    e["period"]=e.event_date.between(lo,hi)
    ev=e[e.period].copy()
    R["event_quality"]={"all_events":len(e),"in_period":len(ev),"in_period_routes":int(text(ev,"Location_ID").replace("",np.nan).nunique()),"in_period_with_logged_start_end":int((text(ev,"Time Start").ne("")&text(ev,"Time End").ne("")).sum()),"in_period_with_numeric_positive_route_length":int(num(ev.Route_length).gt(0).sum()),"QA_flag_distributions_in_period":{k:bucket(ev[k]) for k in ["Rt Compl","Surv Rte Compl","Data OK","Data Rev","Data No OK","CountSurveyNight","QAQC_Metadata","QAQC_GPS","QAQC_BatData"]}}
    t["code"]=text(t,"A_SP").str.upper()
    t["scientific_name"]=text(t,"Genus")+" "+text(t,"Species")
    t["binomial_candidate"]=t.scientific_name.str.fullmatch(r"[A-Z][a-z]+ [a-z][a-z]+")&~text(t,"Species").str.lower().isin(["sp","spp","unknown","none","unidentified"])
    # Exact published lookup only; do not map ambiguous calls by name similarity.
    tm=t[t.code.ne("")&~t.code.duplicated(False)&t.binomial_candidate].set_index("code").scientific_name.to_dict()
    R["taxon_lookup"]={"rows":len(t),"unique_nonambiguous_binomial_codes":len(tm),"code_to_source_binomial":tm,"unresolved_codes":sorted(set(t.code)-set(tm))}
    c["code"]=text(c,"A_SP").str.upper();c["species"]=c.code.map(tm)
    c["filename"]=text(c,"FILENAME")
    c["lat"]=num(c.LAT);c["lon"]=num(c.LONG)
    c["gps_numeric"]=num(c.gps_diff)
    goodfile=c.Event_ID.ne("")&c.filename.ne("")
    dup=goodfile&c.duplicated(["Event_ID","filename"],False)
    R["call_keys"]={"rows":len(c),"nonempty_event_file":int(goodfile.sum()),"duplicate_event_file_rows":int(dup.sum()),"data_id_nonempty":int(text(c,"Data_ID").ne("").sum()),"unique_event_file_pairs":int(c.loc[goodfile,["Event_ID","filename"]].drop_duplicates().shape[0]),"source_Count_values":bucket(c.Count)}
    z=c.merge(e[["Event_ID","Location_ID","event_date","period","QAQC_Metadata","QAQC_GPS","QAQC_BatData"]],on="Event_ID",how="left",validate="many_to_one",indicator=True)
    assert len(z)==len(c)
    z["unique_event_file"]=goodfile.to_numpy()&~dup.to_numpy()
    z["both_date_match"]=z.event_date.notna()&z.call_date.notna()&z.event_date.eq(z.call_date)
    R["event_join"]={"matched_calls":int(z._merge.eq("both").sum()),"unmatched":int(z._merge.ne("both").sum()),"both_date_valid":int((z.event_date.notna()&z.call_date.notna()).sum()),"same_event_and_call_date":int(z.both_date_match.sum())}
    tests=[("matched_event",z._merge.eq("both")),("event_and_call_date_match",z.both_date_match),("frozen_period",z.event_date.between(lo,hi)),("unique_event_file",z.unique_event_file),("unambiguous_source_binomial",z.species.notna()),("finite_region_coordinates",np.isfinite(z.lat)&np.isfinite(z.lon)&z.lat.between(15,51.6)&z.lon.between(-130,-60))]
    live=pd.Series(True,index=z.index);steps=[]
    for name,check in tests:
        before=int(live.sum());live&=check.fillna(False);steps.append({"step":name,"rows":int(live.sum()),"lost":before-int(live.sum())})
    d=z[live].copy()
    R["candidate_attrition"]=steps;R["candidate_records"]=len(d);R["candidate_taxa"]=int(d.species.nunique());R["candidate_survey_events"]=int(d.Event_ID.nunique());R["candidate_routes"]=int(text(d,"Location_ID").replace("",np.nan).nunique())
    R["candidate_GPS_difference_numeric_records"]=int(d.gps_numeric.notna().sum())
    R["candidate_QA_distributions"]={k:bucket(d[k]) for k in ["QAQC_Metadata","QAQC_GPS","QAQC_BatData"]}
    P=Transformer.from_crs(4326,6933,always_xy=True)
    if len(d):
        x,y=P.transform(d.lon.to_numpy(),d.lat.to_numpy());assert np.isfinite(x).all() and np.isfinite(y).all()
        d["cell_x"]=np.floor(x/1000).astype(int);d["cell_y"]=np.floor(y/1000).astype(int)
        v=d[["species","cell_x","cell_y"]].drop_duplicates();sp=[]
        for name,g in v.groupby("species",sort=True):
            n=len(g);nb=int(g.groupby([g.cell_x//200,g.cell_y//200]).size().ge(5).sum())
            dd=d[d.species.eq(name)]
            sp.append({"species":name,"candidate_cells":n,"candidate_blocks_ge5":nb,"candidate_events":int(dd.Event_ID.nunique()),"candidate_records":len(dd),"passes_geometry_only":bool(n>=30 and nb>=4)})
        R["geographic_candidate_support"]=sp
        R["candidate_cells"]=len(d[["cell_x","cell_y"]].drop_duplicates())
        R["candidate_species_cells"]=len(v)
        R["candidate_species_geography_only_pass"]=sum(x["passes_geometry_only"] for x in sp)
    R["verified_500m_accuracy_records"]=None
    R["admitted_for_original_SDM"]=False
    R["status"]="RELATION_AUDIT_COMPLETE_REQUIRES_OBSERVATION_PRECISION_AND_QA_SEMANTICS";save()
if __name__=="__main__":
    try:main()
    except Exception as e:
        R.update(status="INCOMPLETE",error_type=type(e).__name__);save();raise
    finally:src.P.unlink(missing_ok=True)
