"""Source-pinned original Ducke XLSX -> LOCAL matched plot-guild records.

Use artifact_tool (NOT pandas/openpyxl) to read the 8 original XLSX sheets.
Do not commit original source rows, exact LAT/LONG or plot-level derived JSON.
This file is a reproducible import adapter; CI runs only offline pure-source
helpers. Original input upload has to be supplied by a data steward.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import datetime as dt
import hashlib
import json
import re
import statistics
import tempfile
from pathlib import Path
import zipfile

SOURCE_ZIP_SHA="55c784e2f7b37987e3657d3ba3d5cf6a41bb3554a11904969d1376c977bcdbce"
SOURCE_XLSX_SHA="1fad327f61de4f144a44d1d889726ee8743d4edaf1eae87cdc2d5e2bc86bb9a6"
MEMBER="Bats_Ducke_data_metadata.xlsx"
FOOD12=frozenset(("Annona","Anthurium","Astrocaryum","Bactris","Clidemia",
                  "Henriettea","Mauritia","Oenocarpus","Peperomia","Philodendron",
                  "Piper","Rhodospatha"))
SHEETS={"Bats_Ducke":(1190,6),"Fruits":(310,4),
        "Insects":(50,23),"Terrain_elevation":(50,4)}
START=dt.date(2013,10,1);END=dt.date(2014,2,28)
ACCEPT_GUILDS=frozenset(("Frugivore","Nectarivore","Gleaning animalivore",
                         "Aerial_insectivore","Sanguivore"))

def canon_site(site):
    m=re.fullmatch(r"(?:L|LO)([3-8])_(\d{4})",str(site))
    if m:return "L"+m.group(1)+"_"+m.group(2)
    m=re.fullmatch(r"PO_?(\d{1,2})",str(site))
    if m:return "PO_"+format(int(m.group(1)),"02d")
    raise ValueError("STOP_UNRECOGNIZED_SOURCE_PLOT_ALIAS")

def parse_source_date(source):
    try:return dt.datetime.strptime(source,"%m_%d_%Y").date()
    except (ValueError,TypeError):raise ValueError("STOP_MALFORMED_SOURCE_DATE")

def parse_original_zip(zip_path):
    from artifact_tool import Blob,SpreadsheetFile
    p=Path(zip_path)
    if hashlib.sha256(p.read_bytes()).hexdigest()!=SOURCE_ZIP_SHA:
        raise ValueError("STOP_ORIGINAL_DRYAD_ZIP_HASH_CHANGED")
    with zipfile.ZipFile(p) as archive:
        if archive.namelist()!=[MEMBER]:
            raise ValueError("STOP_ORIGINAL_DRYAD_ARCHIVE_CONTENT_CHANGED")
        raw=archive.read(MEMBER)
    if hashlib.sha256(raw).hexdigest()!=SOURCE_XLSX_SHA:
        raise ValueError("STOP_ORIGINAL_DRYAD_WORKBOOK_HASH_CHANGED")
    with tempfile.TemporaryDirectory() as work:
        pathname=Path(work)/MEMBER
        pathname.write_bytes(raw)
        book=SpreadsheetFile.import_xlsx(Blob.load(str(pathname)))
        result={}
        for sheetname,(nrow,ncol) in SHEETS.items():
            vals=book.worksheets.get_item(sheetname).get_range_by_indexes(0,0,nrow,ncol).values
            columns=vals[0]
            if not columns or len(set(columns))!=len(columns):
                raise ValueError("STOP_SOURCE_DUPLICATE_HEADERS")
            result[sheetname]=[dict(zip(columns,r)) for r in vals[1:] if r[0] is not None]
    return result

def build_matched_source(rows):
    for name in SHEETS:
        if name not in rows:raise ValueError("STOP_MISSING_INPUT_SHEET")
    aliases=defaultdict(set)
    for name,table in rows.items():
        for record in table:
            alias=record["Plots"]
            aliases[(name,canon_site(alias))].add(alias)
    if any(len(ids)!=1 for ids in aliases.values()):
        raise ValueError("STOP_AMBIGUOUS_ONE_TO_MANY_PLOT_ALIAS")
    bat_plots={canon_site(r["Plots"]) for r in rows["Bats_Ducke"]}
    for name in ("Insects","Terrain_elevation"):
        sites={canon_site(r["Plots"]) for r in rows[name]}
        if sites!=bat_plots or len(rows[name])!=len(sites):
            raise ValueError("STOP_NONONE_TO_ONE_BAT_ENVIRONMENT_JOIN")
    insect={canon_site(r["Plots"]):r for r in rows["Insects"]}
    terrain={canon_site(r["Plots"]):r for r in rows["Terrain_elevation"]}
    fruit=defaultdict(list)
    for record in rows["Fruits"]:
        fruit[(canon_site(record["Plots"]),parse_source_date(record["Date_MM_DD_YYYY"]))].append(record)
    captured=defaultdict(list)
    abnormal_dates=0
    noncaptures=0
    for r in rows["Bats_Ducke"]:
        date=parse_source_date(r["Date_MM_DD_YYYY"])
        if date.year>2014:abnormal_dates+=1
        if r["Species"]=="Night_without_capture":
            noncaptures+=1;continue
        if r["Guild"] not in ACCEPT_GUILDS:
            raise ValueError("STOP_BAT_GUILD_CODE_UNKNOWN")
        if START<=date<=END:
            captured[(canon_site(r["Plots"]),date)].append(r)
    nights=[]
    for (site,date),original_bats in captured.items():
        matching=fruit.get((site,date))
        if not matching:
            continue  # NO ZERO-FOOD IMPUTATION: source lacks this survey night
        if any(type(x["Amount"]) not in (float,int) or x["Amount"]<0 for x in matching):
            raise ValueError("STOP_NEGATIVE_OR_MISSING_FRUIT_COUNT")
        guild=Counter(b["Guild"] for b in original_bats)
        total=sum(x["Amount"] for x in matching)
        food=sum(x["Amount"] for x in matching if x["Genus"] in FOOD12)
        nights.append({"site":site,"date":date,"n_captures":len(original_bats),
                       "frug":guild["Frugivore"],"glean":guild["Gleaning animalivore"],
                       "aerial":guild["Aerial_insectivore"],
                       "nectar":guild["Nectarivore"],
                       "sanguivore":guild["Sanguivore"],"fruit_all":total,
                       "fruit_batfood_12":food,"fruit_other":total-food})
    group=defaultdict(list)
    for record in nights:group[record["site"]].append(record)
    out=[]
    for site,sc in sorted(group.items()):
        n=sum(q["n_captures"] for q in sc)
        if n<1:raise ValueError("STOP_EMPTY_CAPTURE_DENOMINATOR")
        terr=terrain[site]
        env=insect[site]
        data={"plot":site,"block":"PO" if site.startswith("PO_") else site.split("_")[0],
              "captures":n,"n_matched_nights":len(sc),
              "design_added_riparian_plot":site.startswith("PO_"),
              "elevation_m":float(terr["Terrain_elevation_(m)"]),
              "latitude":float(terr["LAT"]),"longitude":float(terr["LONG"]),
              "insect_mass_g":float(env["Insect_mass"])}
        for key in ("frug","glean","aerial","nectar","sanguivore"):
            data[key]=sum(q[key] for q in sc)
        for key in ("fruit_all","fruit_batfood_12","fruit_other"):
            data[key]=statistics.mean(q[key] for q in sc)
        out.append(data)
    qc={"source_year_range_verified":[START.isoformat(),END.isoformat()],
        "raw_bat_rows":len(rows["Bats_Ducke"]),"raw_fruit_rows":len(rows["Fruits"]),
        "year_abnormal_rows_gt_2014":abnormal_dates,"noncapture_marker_rows":noncaptures,
        "full_one_to_one_environment_plots":len(bat_plots),
        "matched_plots":len(out),"matched_plot_nights":len(nights),
        "matched_captures":sum(r["captures"] for r in out),
        "matched_frugivores":sum(r["frug"] for r in out),
        "no_imputation_of_missing_fruit":True}
    if not(len(bat_plots)==49 and len(out)==46 and len(nights)==103 and
           qc["matched_captures"]==810 and qc["matched_frugivores"]==573):
        raise ValueError("STOP_UPLOADED_ORIGINAL_SOURCE_ELIGIBILITY_DRIFT")
    return out,qc

def main():
    app=argparse.ArgumentParser()
    app.add_argument("--source-zip",required=True)
    app.add_argument("--local-output",required=True)
    app.add_argument("--aggregate-qc",required=True)
    args=app.parse_args()
    plots,qc=build_matched_source(parse_original_zip(args.source_zip))
    # PRIVATE local original plot information; never publish to GitHub.
    Path(args.local_output).write_text(json.dumps(plots,indent=2)+"\n")
    Path(args.aggregate_qc).write_text(json.dumps(qc,indent=2)+"\n")
    print("DUCKE_SOURCE_ELIGIBLE",qc["matched_plots"],qc["matched_plot_nights"],
          qc["matched_captures"],flush=True)
    print("NO RAW SOURCE RECORDS OR GPS POSITIONS POSTED",flush=True)

if __name__=="__main__":
    main()
