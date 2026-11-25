"""Independent macro coverage by coordinate uncertainty and spatial grain.
No ecological model, no inferred uncertainty, no primary gate change.
"""
import collections,csv,gzip,hashlib,itertools,json,math,pathlib
from urllib.parse import quote
import duckdb,requests
from pyproj import Transformer
OUT=pathlib.Path("macro_grain_census");OUT.mkdir(exist_ok=True)
ROOT=pathlib.Path(__file__).resolve().parent
INV=pathlib.Path("fixed/object_inventory.json")
PIN="14692b344c86a9f392f987924921d2c4cc723483a1669d808192d5003b0a3fae"
BASE="https://gbif-public-data.s3.us-east-1.amazonaws.com/"
OLD=json.loads((ROOT/"IN_DOMAIN_CONTINENTAL_CENSUS_RECEIPT_V1.json").read_text())
assert OLD["audit"]["run_id"]==45657223272 and OLD["status"]=="REGIONAL_COVERAGE_COMPLETE_NO_MODEL"
REGIONS=OLD["regions"]
assert REGIONS=={"North_America":{"countries":["US","CA","MX"],"bbox":[-130,15,-60,51.6]},"East_Asia":{"countries":["CN","JP","MN","KP","KR","TW"],"bbox":[73,15,146,51.6]}}
P=Transformer.from_crs(4326,6933,always_xy=True)
I=Transformer.from_crs(6933,4326,always_xy=True)
report={"stage":"independent continental macro precision and scale census, no fit","snapshot_doi":"10.15468/dl.8yrbe7","inventory_sha256":PIN,"prior_run":45657223272,"status":"START","regions":{},"limits":["Counts before trait, forest, terrain, roost and calibrated effort admission.","Coordinate-uncertainty metadata are source-reported, not verified positional error.","Grain-compatible cohorts are different from same-record aggregation.","No missing uncertainty imputation, no actual 3D occupancy, no primary gate relaxation."]}
def sha(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def literal(x):return "'"+str(x).replace("'","''")+"'"
def save():
    (OUT/"report.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print("MACRO_GRAIN_REPORT="+json.dumps(report,allow_nan=False),flush=True)
def block_center(cell,g):
    # Integer arithmetic: center of a coarse cell, zero-origin EPSG:6933.
    return ((2*cell[0]+1)*g//400,(2*cell[1]+1)*g//400)
def whole_block(cell,g):
    x,y=cell
    bx=x*g//200;by=y*g//200
    return (bx,by) if ((x+1)*g-1)//200==bx and ((y+1)*g-1)//200==by else None
def pass_roster(by,ns):
    result=[]
    for k,bb in sorted(by.items()):
        nc=sum(map(len,bb.values()));nb=sum(len(v)>=5 for v in bb.values())
        result.append({"key":k,"names":sorted(ns[k]),"cells":nc,"blocks_ge5":nb,"pass":nc>=30 and nb>=4 and len(ns[k])==1})
    return result
def census(rows,g,threshold):
    cells=collections.defaultdict(lambda:collections.defaultdict(set))
    contained=collections.defaultdict(lambda:collections.defaultdict(set))
    domain=collections.defaultdict(lambda:collections.defaultdict(set))
    names=collections.defaultdict(set);providers=collections.Counter();sources_by_species=collections.defaultdict(collections.Counter)
    ag=collections.Counter();n=0;cross_n=0;boundary_n=0
    for name,key,x,y,ds,year,lic,u,count in rows:
        if u>threshold:continue
        c=(x//g,y//g);center=block_center(c,g);whole=whole_block(c,g)
        names[key].add(name);cells[key][center].add(c);n+=count
        if ds:providers[ds]+=count;sources_by_species[key][ds]+=count
        _,lat_hi=I.transform(0,(c[1]+1)*g*1000)
        is_domain=lat_hi<=51.6
        if not is_domain:boundary_n+=count
        if whole is None:cross_n+=count;continue
        contained[key][whole].add(c)
        if is_domain:
            domain[key][whole].add(c)
            ag[(name,key,*c,ds,year,lic)]+=count
    all_c=pass_roster(cells,names);inside=pass_roster(contained,names);dom=pass_roster(domain,names)
    eligible={v["key"] for v in dom if v["pass"]}
    strata=collections.defaultdict(lambda:collections.defaultdict(set))
    for (name,k,x,y,ds,yr,lic),count in ag.items():
        if k in eligible and ds and yr:
            b=whole_block((x,y),g);assert b is not None
            strata[(ds,yr,*b)][k].add((x,y))
    pairs=collections.defaultdict(set);ng=0;ncomparisons=0
    for st,v in strata.items():
        for a,b in itertools.combinations(sorted(v),2):
            n_pair=len(v[a])*len(v[b])-len(v[a]&v[b])
            if n_pair>0:
                pairs[(a,b)].add(st[2:]);ng+=1;ncomparisons+=min(128,n_pair)
    # One common domain-qualified row archive per arm/grain, no raw XY.
    summary={"records":n,"species_keys":len(names),"providers":len(providers),"species_cells":sum(x["cells"] for x in all_c),"unique_cells":len({c for d in cells.values() for v in d.values() for c in v}),"top_provider_record_share":max(providers.values())/n if providers and n else None,"geographic_pass_center":sum(x["pass"] for x in all_c),"geographic_pass_wholly_contained":sum(x["pass"] for x in inside),"geographic_pass_within_training_latitude_and_block":len(eligible),"records_crossing_200km_cell_boundary":cross_n,"records_in_latitude_boundary_cells":boundary_n,"passing_species_cell_roster":dom,"source_year_block_support_among_domain_passing":{"strata":len(strata),"multispecies_strata":sum(len(x)>1 for x in strata.values()),"comparison_groups":ng,"capped_comparisons":ncomparisons,"pairs_with_at_least_one_block":len(pairs),"pairs_with_at_least_four_blocks":sum(len(v)>=4 for v in pairs.values()),"possible_pairs":len(eligible)*(len(eligible)-1)//2,"providers":len({s[0] for s in strata}),"species_provider_max_share":{k:max(sources_by_species[k].values())/sum(sources_by_species[k].values()) for k in sorted(eligible) if sources_by_species[k]}}}
    return summary,ag
def main():
    assert sha(INV)==PIN
    objects=json.loads(INV.read_text())
    assert len(objects)==8 and sum(o["size"] for o in objects)==9077637625
    urls=[]
    for o in objects:
        u=BASE+quote(o["key"],safe="/=")
        h=requests.head(u,timeout=(15,30));h.raise_for_status()
        assert int(h.headers["Content-Length"])==o["size"] and h.headers["ETag"].strip('"')==o["etag"].strip('"')
        urls.append(u)
    report["source_objects_verified"]=len(urls)
    con=duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs; SET threads=3; SET memory_limit='4GB'; SET preserve_insertion_order=false;")
    source="read_parquet(["+",".join(map(literal,urls))+"], hive_partitioning=false)"
    cols={r[0].lower():r[0] for r in con.execute("DESCRIBE SELECT * FROM "+source).fetchall()}
    req=["gbifid","datasetkey","species","specieskey","order","countrycode","decimallatitude","decimallongitude","coordinateuncertaintyinmeters","eventdate","basisofrecord","occurrencestatus","hasgeospatialissues","license"]
    assert set(req)<=set(cols)
    C=lambda k:'"'+cols[k]+'"'
    uncertainty="TRY_CAST("+C("coordinateuncertaintyinmeters")+" AS DOUBLE)"
    common=" AND ".join([C("order")+"='Chiroptera'","TRY_CAST("+C("eventdate")+" AS DATE) BETWEEN DATE '2019-04-17' AND DATE '2023-03-16'","upper(replace(CAST("+C("occurrencestatus")+" AS VARCHAR),' ','')) IN ('PRESENT','DETECTED')","upper(replace(CAST("+C("basisofrecord")+" AS VARCHAR),' ','_')) IN ('HUMAN_OBSERVATION','MACHINE_OBSERVATION','OBSERVATION')","TRY_CAST("+C("hasgeospatialissues")+" AS BOOLEAN)=false",C("species")+" IS NOT NULL",C("specieskey")+" IS NOT NULL",C("gbifid")+" IS NOT NULL"])
    for region,v in REGIONS.items():
        l,b,r,t=v["bbox"]
        where=common+" AND "+C("countrycode")+" IN ("+",".join(map(literal,v["countries"]))+") AND "+C("decimallongitude")+f" BETWEEN {l} AND {r} AND "+C("decimallatitude")+f" BETWEEN {b} AND {t}"
        # Query all other eligible records once to diagnose precision missingness.
        cat=f"""CASE WHEN {uncertainty} IS NULL THEN 'missing_or_unparseable'
        WHEN NOT isfinite({uncertainty}) THEN 'nonfinite'
        WHEN {uncertainty}<=0 THEN 'nonpositive'
        WHEN {uncertainty}<0.000001 THEN 'below_numeric_guard'
        WHEN {uncertainty}<=500 THEN '1km_eligible'
        WHEN {uncertainty}<=3000 THEN 'additional_6km'
        WHEN {uncertainty}<=6000 THEN 'additional_12km'
        ELSE 'over_6000m' END"""
        ac=con.execute("SELECT "+cat+" AS precision_group,count(*),count(DISTINCT "+C("gbifid")+"),count(DISTINCT "+C("specieskey")+"),count(DISTINCT "+C("datasetkey")+") FROM "+source+" WHERE "+where+" GROUP BY 1 ORDER BY 1").fetchall()
        attr={k:{"rows":int(n),"unique_ids":int(u),"species_keys":int(s),"providers":int(d)} for k,n,u,s,d in ac}
        assert all(x["rows"]==x["unique_ids"] for x in attr.values())
        rr={"pre_precision_records":sum(x["rows"] for x in attr.values()),"precision_attrition":attr,"arms":{}}
        report["regions"][region]=rr
        save()
        if rr["pre_precision_records"]>5_000_000:raise ValueError("pre-precision record budget exceeded")
        selected=[C(k) for k in ["species","specieskey","decimallongitude","decimallatitude","datasetkey"]]+["year(TRY_CAST("+C("eventdate")+" AS DATE))",C("license"),uncertainty]
        query="SELECT "+",".join(selected)+",count(*) FROM "+source+" WHERE "+where+" AND "+uncertainty+" BETWEEN 0.000001 AND 6000 GROUP BY ALL"
        rows=[]
        cur=con.execute(query)
        while True:
            batch=cur.fetchmany(50000)
            if not batch:break
            for name,key,lon,lat,ds,yr,lic,u,n in batch:
                x,y=P.transform(lon,lat);assert math.isfinite(x) and math.isfinite(y)
                rows.append((str(name),str(key),math.floor(x/1000),math.floor(y/1000),str(ds) if ds is not None else "",int(yr),str(lic),float(u),int(n)))
        n=sum(x[-1] for x in rows)
        assert n==sum(attr.get(k,{}).get("rows",0) for k in ("1km_eligible","additional_6km","additional_12km"))
        if n>3_000_000:raise ValueError("scale-compatible record budget exceeded")
        strict,ag=census(rows,1,500)
        prior=OLD["coverage"][region]
        expected={"records":prior["unique_records"],"species_keys":prior["species_keys"],"providers":prior["providers"],"species_cells":prior["species_cells"],"unique_cells":prior["unique_cells"],"geographic_pass_center":prior["geographic_pass_species_before_trait_filter"]}
        rr["strict_1km_replay_checks"]={k:strict[k]==v for k,v in expected.items()}
        assert all(rr["strict_1km_replay_checks"].values()),region
        rr["arms"]["1km_same_and_compatible"]=strict
        for label,g,cut in [("6km_same",6,500),("12km_same",12,500),("6km_compatible",6,3000),("12km_compatible",12,6000)]:
            s,ag=census(rows,g,cut)
            s["grain_km"]=g;s["maximum_uncertainty_m"]=cut
            rr["arms"][label]=s
            # Coarse cells wholly contained in training latitude and the frozen 200-km block.
            path=OUT/(region+"_"+label+"_domain_cells.csv.gz")
            with gzip.open(path,"wt",encoding="utf-8",newline="") as f:
                w=csv.writer(f);w.writerow(["species","snapshot_species_key","cell_x_at_grain","cell_y_at_grain","dataset_key","year","license","records"])
                for k,n in sorted(ag.items(),key=lambda x:tuple(map(str,x[0]))):w.writerow([*k,n])
            s["domain_cell_table_sha256"]=sha(path)
        rr["primary_1km_admitted"]=False
        rr["any_coarse_geographic_upper_bound_20"]=any(x["geographic_pass_within_training_latitude_and_block"]>=20 for x in rr["arms"].values())
        rr["any_model_admitted"]=False
        save()
    report["status"]="MACRO_GRAIN_CENSUS_COMPLETE_NO_MODEL";save()
if __name__=="__main__":
    try:main()
    except Exception as e:
        report.update(status="INCOMPLETE",error=type(e).__name__+": "+str(e)[:240]);save();raise
