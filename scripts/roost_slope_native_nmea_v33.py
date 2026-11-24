"""V33: original logger NMEA structural admission, no movement or altitude outcomes."""
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import PurePosixPath
from bisect import bisect_left,bisect_right
import io,json,math,re,zipfile,hashlib
import numpy as np
from openpyxl import load_workbook
from roost_fd_source_audit_v2 import OUT
from roost_slope_acoustic_gps_archive_v31 import FILES,fetch

SPECIES=["leptonycteris yerbabuenae","myotis myotis","myotis vivesi","rhinopoma microphyllum"]
MAPSHA="a9d64f04e8abe29cb728e1d2810bc4a572cbb9624c8410c1b5f7bdbfc3f91d17"
def sha(b):return hashlib.sha256(b).hexdigest()
def norm(x):return " ".join(str(x or "").casefold().split())
def summary(x):
    a=np.asarray(x,dtype=float);a=a[np.isfinite(a)]
    if not len(a):return {}
    return dict(zip(["min","q25","median","q75","max"],map(float,np.quantile(a,[0,.25,.5,.75,1]))))
def finite(s):
    try:return math.isfinite(float(s))
    except (ValueError,TypeError):return False
def dist(lat,lon,lat2,lon2):
    a,b=map(math.radians,[lat,lat2]);dl=math.radians(lon2-lon)
    u=math.sin((b-a)/2)**2+math.cos(a)*math.cos(b)*math.sin(dl/2)**2
    return 2*6371008.8*math.asin(math.sqrt(max(0,min(1,u))))
def sentence(s):
    # GGA/RMC recognized even if corrupt; invalid GGA will break chains.
    m=re.match(r"^\$(?:GP|GN)(GGA|RMC),",s)
    if not m:return None
    k=m.group(1)
    if "*" not in s:return k,None
    p,ck=s[1:].rsplit("*",1)
    if not re.fullmatch(r"[0-9a-fA-F]{2}",ck):return k,None
    v=0
    for ch in p:v^=ord(ch)
    if v!=int(ck,16):return k,None
    return k,p.split(",")
def clock(s):
    if not re.fullmatch(r"\d{6}(?:\.\d+)?",s):raise ValueError("time")
    h,m=int(s[:2]),int(s[2:4]);sec=float(s[4:])
    if h>=24 or m>=60 or not 0<=sec<60:raise ValueError("time")
    # exact equality to microsecond, no rounding to nearest whole second.
    return int(round((h*3600+m*60+sec)*1e6))
def coords(a,b,c,d):
    def one(x,hem,lim,good):
        if hem not in good or not finite(x):raise ValueError("position")
        v=float(x)
        if v<0:raise ValueError("position")
        deg=int(v//100);minute=v-deg*100
        if not 0<=minute<60 or deg+minute/60>lim:raise ValueError("position")
        return (deg+minute/60)*(1 if hem in ("N","E") else -1)
    return one(a,b,90,("N","S")),one(c,d,180,("E","W"))
def rmc(f):
    if f is None or len(f)<10 or f[2]!="A":return None
    try:
        t=clock(f[1]);lat,lon=coords(f[3],f[4],f[5],f[6])
        if not re.fullmatch(r"\d{6}",f[9]):return None
        day=datetime.strptime(f[9],"%d%m%y").replace(tzinfo=timezone.utc)
        if not 2000<=day.year<=2023:return None
        return t,int(day.timestamp()*1e6),lat,lon
    except (ValueError,OverflowError):return None

def decode(b):
    seq=[];c=Counter();sat=[];hdop=[]
    for l in b.decode("utf-8-sig",errors="replace").splitlines():
        t=sentence(l.strip())
        if t is None:continue
        k,f=t;seq.append((k,f));c[k]+=1
        if f is None:c[k+"_bad_checksum_or_format"]+=1
    # use adjacent acquisition sentence indices, not same clock from another day
    R={i:rmc(f) for i,(k,f) in enumerate(seq) if k=="RMC"}
    c["RMC_valid_status_date_time_xy"]=sum(v is not None for v in R.values())
    rows=[]
    for i,(k,f) in enumerate(seq):
        if k!="GGA":continue
        row=None;reason=None
        if f is None or len(f)<13:reason="checksum_or_format"
        else:
            try:
                t=clock(f[1])
                if f[6] not in ("1","2"):reason="fix_quality_not_1_2"
                else:
                    lat,lon=coords(f[2],f[3],f[4],f[5])
                    if not finite(f[9]) or f[10]!="M":reason="height_missing_or_unit"
                    else:
                        c["GGA_valid_xyz_time_quality"]+=1
                        if finite(f[11]) and f[12]=="M":c["geoid_present_m"]+=1
                        matches=set()
                        for j in range(max(0,i-8),min(len(seq),i+9)):
                            v=R.get(j)
                            if v is not None and v[0]==t and dist(lat,lon,v[2],v[3])<=20:
                                matches.add(v[1])
                        if len(matches)!=1:reason="no_unique_same_time_RMC_date"
                        else:
                            row=(next(iter(matches))+t,lat,lon)
                            if finite(f[7]):sat.append(float(f[7]))
                            if finite(f[8]):hdop.append(float(f[8]))
            except (ValueError,OverflowError,IndexError):reason="invalid_time_or_xy"
        if row is None:c["GGA_rejected_"+str(reason)]+=1
        else:c["GGA_RMC_valid_pair"]+=1
        rows.append(row)
    counts=Counter(r[0] for r in rows if r is not None)
    out=[];chain=[];gaps=[]
    for row in rows:
        if row is None or counts[row[0]]!=1:
            if row is not None:c["duplicate_utc_rows"]+=1
            if chain:out.append(chain);chain=[]
            continue
        if chain:
            dt=(row[0]-chain[-1][0])/1e6
            if dt>0:gaps.append(dt)
            if dt<=0 or dt>65:
                c["chain_break_gap_or_nonincrease"]+=1
                out.append(chain);chain=[]
        chain.append(row)
    if chain:out.append(chain)
    c["unique_timestamp_valid_rows"]=sum(map(len,out))
    return out,c,gaps,sat,hdop

def anchors_and_windows(chains):
    result=Counter()
    for chain in chains:
        times=[r[0] for r in chain];n=len(chain);i=0
        while i<n:
            ids=[i];current=i
            while True:
                target=times[current]+60_000_000
                a=bisect_left(times,target-5_000_000,current+1)
                b=bisect_right(times,target+5_000_000,a)
                if a==b:break
                current=min(range(a,b),key=lambda k:(abs(times[k]-target),times[k]))
                ids.append(current)
            i=current+1
            if len(ids)<3:continue
            result["anchor_chains_ge3"]+=1
            result["anchor_rows"]+=len(ids)
            for j in range(0,len(ids)-2,2):
                r0,r1,r2=[chain[k] for k in ids[j:j+3]]
                result["candidate_windows"]+=1
                dt1=(r1[0]-r0[0])/1e6;dt2=(r2[0]-r1[0])/1e6
                assert 55<=dt1<=65 and 55<=dt2<=65
                v1=dist(r0[1],r0[2],r1[1],r1[2])/dt1
                v2=dist(r1[1],r1[2],r2[1],r2[2])/dt2
                if 2<=v1<=50 and 2<=v2<=50:result["horizontal_eligible_windows"]+=1
    return result

def flag(x):
    if x is None or str(x).strip()=="":return "missing"
    if finite(x) and float(x) in (0,1):return str(int(float(x)))
    return "other"
def load_mapping(b):
    w=load_workbook(io.BytesIO(b),read_only=True,data_only=True)
    try:
        it=w.worksheets[0].values;cols=[str(x or "").strip() for x in next(it)]
        keys={k:i for i,k in enumerate(cols)}
        assert {"species","batName","dataGPS","dataAudio","sampleRate"}<=set(keys)
        rows={}
        for r in it:
            s=norm(r[keys["species"]]);a=norm(r[keys["batName"]]);assert s in SPECIES and a
            k=(s,a);assert k not in rows
            v=r[keys["sampleRate"]]
            rows[k]={"gps":flag(r[keys["dataGPS"]]),"audio":flag(r[keys["dataAudio"]]),
                "sample_rate_metadata":str(float(v)) if finite(v) and 0<float(v)<=1000000 else "other_or_missing"}
        assert len(rows)==25
        return rows
    finally:w.close()

def run():
    b=fetch(FILES["data_zip"]);result={"status":"native_NMEA_structural_gate","zip_sha256":sha(b),"numeric_altitude_outcomes_read":False,"acoustic_outcomes_read":False,"species":{}}
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        infos=[i for i in z.infolist() if not i.is_dir() and "__MACOSX" not in PurePosixPath(i.filename).parts and not PurePosixPath(i.filename).name.startswith("._") and PurePosixPath(i.filename).name.lower()!=".ds_store"]
        mapping=[z.read(i) for i in infos if PurePosixPath(i.filename).suffix.lower()==".xlsx"]
        bmap=next(x for x in mapping if sha(x)==MAPSHA);m=load_mapping(bmap)
        matched=defaultdict(list);unmatched=0;ambiguous=0;nlog=0
        for i in infos:
            if PurePosixPath(i.filename).suffix.lower()!=".txt":continue
            raw=z.read(i)
            if raw.startswith(b"\x00\x05\x16\x07"):continue
            nlog+=1
            pp=[norm(p) for p in PurePosixPath(i.filename).parts[:-1]]
            ks=[k for k in m if any(pp[j]==k[0] and pp[j+1]==k[1] for j in range(len(pp)-1))]
            if len(ks)!=1:
                if ks:ambiguous+=1
                else:unmatched+=1
                continue
            matched[ks[0]].append(raw)
        result["mapping"]={"rows":len(m),"substantive_logger_files":nlog,"unmatched_logger_files":unmatched,
           "ambiguous_logger_files":ambiguous,"unique_mapped_individuals":sum(len(v)==1 for v in matched.values()),
           "multiple_logger_individuals":sum(len(v)>1 for v in matched.values())}
        for s in SPECIES:
            subset={k:v for k,v in m.items() if k[0]==s}
            c=Counter();wins=[];fixes=[];gaps=[];sat=[];hdop=[];win_audit=Counter();ng=0
            for k,v in subset.items():
                if v["gps"]!="1" or len(matched.get(k,[]))!=1:continue
                ng+=1
                chains,ct,dt,ss,hh=decode(matched[k][0])
                c.update(ct);gaps.extend(dt);sat.extend(ss);hdop.extend(hh)
                ww=anchors_and_windows(chains);win_audit.update(ww)
                wins.append(ww["horizontal_eligible_windows"]);fixes.append(ct["unique_timestamp_valid_rows"])
            eligible=sum(x>=50 for x in wins)
            result["species"][s]={"workbook_rows":len(subset),"gps_flags":dict(Counter(v["gps"] for v in subset.values())),
                "audio_flags":dict(Counter(v["audio"] for v in subset.values())),
                "sample_rate_metadata_labels":dict(Counter(v["sample_rate_metadata"] for v in subset.values())),
                "mapped_GPS_flag1_individuals":ng,"NMEA_counts":dict(c),"valid_rows_per_individual":summary(fixes),
                "native_gap_seconds":summary(gaps),"satellite_count":summary(sat),"HDOP":summary(hdop),
                "window_audit":dict(win_audit),"eligible_windows_per_individual":summary(wins),
                "individuals_ge50_windows":eligible,"V29_like_structural_gate":eligible>=6}
        result["species_passing"]=sum(v["V29_like_structural_gate"] for v in result["species"].values())
    return result
def test():
    def wrap(s):
        c=0
        for ch in s:c^=ord(ch)
        return "$"+s+"*"+format(c,"02X")
    g=wrap("GPGGA,120000.00,5000.0000,N,01000.0000,E,1,8,1.0,100.0,M,30.0,M,,")
    r=wrap("GPRMC,120000.00,A,5000.0000,N,01000.0000,E,0.0,0.0,010123,,,A")
    ch,c,*_=decode((g+"\n"+r).encode())
    assert c["GGA_RMC_valid_pair"]==1 and len(ch)==1
    _,c,*_=decode((g[:-2]+"ZZ\n"+r).encode())
    assert c["GGA_RMC_valid_pair"]==0
    # synthetic coordinates only: one 3-anchor sequence and a valid moving window
    chain=[(i*60_000_000,0.,i*.003) for i in range(3)]
    assert anchors_and_windows([chain])["horizontal_eligible_windows"]==1
def main():
    dest=OUT/"audit_v33_native_nmea.json"
    test()
    try:r=run();r["synthetic_tests"]="pass"
    except Exception as e:r={"status":"blocked","error_type":type(e).__name__,"synthetic_tests":"pass"}
    dest.write_text(json.dumps(r,indent=2,allow_nan=False))
    print(dest.read_text())
    return 0 if r["status"]=="native_NMEA_structural_gate" else 2
if __name__=="__main__":raise SystemExit(main())
