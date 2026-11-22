"""Read only original Goldshtein GPS XY, cactus XY and structural support.

Original input: user-provided Mendeley v1 ZIP, SHA256 pinned. This audit NEVER
accesses GGA altitude or model response height. Uses artifact_tool for XLSX.
No GPS fixes, cactus coordinates, dates, IDs or row-level data are exported.
It does NOT validate the surveyed polygon, corrected AGL or real flower join.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from hashlib import sha256
from math import cos,radians,isfinite
from pathlib import Path
from tempfile import NamedTemporaryFile
import json
import re
import stat
import zipfile

ORIGINAL_SHA="069b12e6383fa7d84a1f7164fcfe16b0ce693469a7661262ce1a0ed73e423ebb"
MAP_RE=re.compile(r"GPS data/Bat [0-9]+/cacti\.xlsx$")
TRACK_RE=re.compile(r"GPS data/Bat [0-9]+/nmea-GeoTag[12]?\.txt$")


def nmea_degree(value,hemisphere):
    if not value or hemisphere not in ("N","S","E","W"):
        return None
    try:
        x=float(value)
        d=int(x//100)
        minutes=x-100*d
        if not 0<=minutes<60:
            return None
        out=d+minutes/60
        if hemisphere in ("S","W"):out=-out
        if not (-90<=out<=90 if hemisphere in ("N","S") else -180<=out<=180):
            return None
        return out
    except ValueError:
        return None


def _cross(a,b,c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


def convex_hull(points):
    pts=sorted(set(points))
    if len(pts)<3:return []
    low=[]
    for x in pts:
        while len(low)>1 and _cross(low[-2],low[-1],x)<=0:low.pop()
        low.append(x)
    high=[]
    for x in pts[::-1]:
        while len(high)>1 and _cross(high[-2],high[-1],x)<=0:high.pop()
        high.append(x)
    return low[:-1]+high[:-1]


def inside_hull(polygon,point):
    return len(polygon)>=3 and all(
        _cross(polygon[i],polygon[(i+1)%len(polygon)],point)>=-1e-7
        for i in range(len(polygon)))


def _cactus_map_from_xlsx(source,member):
    # Spreadsheet data are read only via artifact_tool; not printed or saved.
    from artifact_tool import Blob,SpreadsheetFile
    with NamedTemporaryFile(suffix=".xlsx") as tmp:
        with source.open(member) as stream:
            while True:
                chunk=stream.read(65536)
                if not chunk:break
                tmp.write(chunk)
        tmp.flush()
        wb=SpreadsheetFile.import_xlsx(Blob.load(tmp.name))
        values=wb.worksheets.get_item_at(0).get_range("A1:M1200").values
    header=[str(v).strip().lower() if v is not None else "" for v in values[0]]
    if "lat" not in header or "lon" not in header:
        raise ValueError("STOP_CACTUS_MAP_MISSING_COORDINATE_COLUMNS")
    lat_i,lon_i=header.index("lat"),header.index("lon")
    flower_i=next((i for i,v in enumerate(header) if v in ("open flowers","openflowers")),None)
    coords=[]
    flowers=Counter()
    for row in values[1:]:
        if row[lat_i] is None and row[lon_i] is None:continue
        a,b=row[lat_i],row[lon_i]
        if type(a) not in (int,float) or type(b) not in (int,float):
            raise ValueError("STOP_NONNUMERIC_CACTUS_MAP_XY")
        if not isfinite(a) or not isfinite(b):raise ValueError("STOP_NONFINITE_CACTUS_XY")
        coords.append((float(a),float(b)))
        if flower_i is not None:
            f=row[flower_i]
            if f is None:flowers["missing"]+=1
            elif type(f) not in (int,float) or not isfinite(f) or f<0:
                raise ValueError("STOP_INVALID_UNDATED_FLOWER_FIELD")
            elif f>0:flowers["positive"]+=1
    if len(coords)<3:raise ValueError("STOP_EMPTY_OR_DEGENERATE_MAP")
    return coords,("alt" in header),flower_i is not None,flowers


def _check_archive(source):
    infos=source.infolist()
    if len(infos)!=55 or sum(x.file_size for x in infos)>500_000_000:
        raise ValueError("STOP_UNEXPECTED_SOURCE_ARCHIVE_LAYOUT")
    names=set()
    for item in infos:
        name=item.filename
        if (name in names or name.startswith("/") or "\\" in name
            or ".." in Path(name).parts or stat.S_ISLNK(item.external_attr>>16)):
            raise ValueError("STOP_UNSAFE_ZIP_ENTRY")
        names.add(name)
    return names


def audit(path):
    with open(path,"rb") as handle:actual=sha256(handle.read()).hexdigest()
    if actual!=ORIGINAL_SHA:raise ValueError("STOP_SOURCE_ZIP_SHA256_MISMATCH")
    with zipfile.ZipFile(path) as z:
        names=_check_archive(z)
        maps=sorted(x for x in names if MAP_RE.fullmatch(x))
        tracks=sorted(x for x in names if TRACK_RE.fullmatch(x))
        if len(maps)!=8 or len(tracks)!=19:
            raise ValueError("STOP_MAPS_OR_TRACKS_NOT_EXPECTED")
        track_by_bat=defaultdict(list)
        for n in tracks:track_by_bat[n.rsplit("/",1)[0]].append(n)
        summary=Counter()
        for name in maps:
            coords,has_alt,has_flower,fl=_cactus_map_from_xlsx(z,name)
            summary["mapped_cacti"]+=len(coords)
            summary["maps_with_undated_openflower_column"]+=int(has_flower)
            summary["maps_with_altitude_column"]+=int(has_alt)
            summary["undated_openflower_positive"]+=fl["positive"]
            summary["undated_openflower_missing"]+=fl["missing"]
            ref_lat=sum(x[0] for x in coords)/len(coords)
            project=lambda a,b:(b*111195*cos(radians(ref_lat)),a*111195)
            poly=convex_hull(project(*p) for p in coords)
            if not poly:raise ValueError("STOP_DEGENERATE_CACTUS_CONVEX_HULL")
            seen=set()
            for filename in track_by_bat[name.rsplit("/",1)[0]]:
                summary["mapped_bat_nmea_files"]+=1
                with z.open(filename) as inp:
                    for line in inp:
                        if not line.startswith(b"$GPRMC,"):continue
                        r=line.decode("ascii","replace").split(",")
                        if len(r)<10 or r[2]!="A":continue
                        summary["mapped_valid_rmc"]+=1
                        lat=nmea_degree(r[3],r[4])
                        lon=nmea_degree(r[5],r[6])
                        if lat is None or lon is None:continue
                        fix=(r[1],r[9],r[3],r[4],r[5],r[6])
                        if fix in seen:continue
                        seen.add(fix)
                        if inside_hull(poly,project(lat,lon)):
                            summary["distinct_fix_inside_cactus_convex_hull"]+=1
            summary["mapped_distinct_xy_time_fixes"]+=len(seen)
    return {
        "schema":"batter.goldshtein_user_v1_source_xy_structure.v1",
        "source_claim_doi":"10.17632/jxghjjsttw.1",
        "uploaded_zip_sha256":ORIGINAL_SHA,
        "n_source_zip_entries":55,
        "n_tracking_animal_directories":len(track_by_bat),
        "n_original_nmea_files":19,
        "n_cactus_tables":len(maps),
        **dict(summary),
        "no_source_original_cactus_or_bat_identifiers_exported":True,
        "raw_GGA_altitude_or_AGL_response_read":False,
        "cactus_convex_hull_not_a_survey_coverage_polygon":True,
        "no_verified_night_aligned_independent_open_flower_census":True,
        "publisher_binary_digest_not_independently_authenticated":True,
        "source_join_admission":"STAGE_A_CANDIDATE_SPATIAL_OVERLAP_ONLY",
        "stage_b":"STOP_NO_VERIFIED_INDEPENDENT_NIGHT_AND_CACTUS_JOIN",
        "real_resource_height_predictive_gain":None
    }


if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("source_zip")
    p.add_argument("--receipt",required=True)
    a=p.parse_args()
    d=audit(a.source_zip)
    Path(a.receipt).write_text(json.dumps(d,indent=2)+"\n",encoding="utf-8")
    print("VERIFIED_SOURCE_MANIFEST_WITH_NO_GPS_HEIGHT",d["n_original_nmea_files"],d["n_cactus_tables"])
    print("STAGE_A",d["source_join_admission"],"STAGE_B",d["stage_b"])
