"""V8c: exact SAFE gazetteer coordinate and Yoh row-grain audit. Aggregate outputs only."""
import collections as C, datetime as dt, csv, hashlib, io, json, math, re, urllib.request, zipfile
from pathlib import Path
from openpyxl import load_workbook

def get(url,cap):
    req=urllib.request.Request(url,headers={'User-Agent':'batter-public-source-audit/1.0'})
    with urllib.request.urlopen(req,timeout=45) as r:b=r.read(cap+1)
    if len(b)>cap:raise ValueError('size cap')
    return b
def fetch(rid,name,cap,sha=None,md5=None):
    meta=json.loads(get(f'https://zenodo.org/api/records/{rid}',2*1024**2))
    assert int(meta['id'])==rid
    f=next(x for x in meta['files'] if x['key']==name)
    assert int(f['size'])<=cap and f['links']['self'].startswith('https://zenodo.org/')
    b=get(f['links']['self'],cap)
    alg,h=f['checksum'].split(':',1)
    assert alg in ('md5','sha256') and len(b)==int(f['size']) and hashlib.new(alg,b).hexdigest()==h
    if sha: assert hashlib.sha256(b).hexdigest()==sha
    if md5: assert hashlib.md5(b).hexdigest()==md5
    return b,{'size':len(b),'sha256':hashlib.sha256(b).hexdigest(),'publisher_checksum':f['checksum']}
def norm(x):return ' '.join(str(x if x is not None else '').strip().casefold().split())
def key(x):
    m=re.fullmatch(r'(.+?)(?:_)?([ct])',norm(x))
    return (m[1],m[2].upper()) if m else None
def coord(lon,lat):
    try:
        lon,lat=float(lon),float(lat)
        return (lon,lat) if 116.5<lon<118.5 and 4<lat<6 else None
    except (ValueError,TypeError):return None
def gap(a,b):
    return 111320*math.hypot((a[0]-b[0])*math.cos(math.radians((a[1]+b[1])/2)),a[1]-b[1])
def loadgaz():
    b,r=fetch(3906082,'gazetteer.geojson',10*1024**2,md5='96109736d2356752afcfee1dbb385099')
    a,ar=fetch(3906082,'location_aliases.csv',2*1024**2,md5='8734199962ef18224b53b1209e613071')
    g=json.loads(b);assert g['type']=='FeatureCollection'
    geo=C.defaultdict(set);types=C.defaultdict(set);regions=C.defaultdict(set)
    for f in g['features']:
        p=f['properties'];n=norm(p.get('location'));gg=f.get('geometry') or {};typ=gg.get('type','missing')
        if not n:continue
        types[n].add(typ);regions[n].add(str(p.get('region')))
        if typ=='Point':
            c=gg.get('coordinates',[])
            if len(c)>=2:
                xy=coord(c[0],c[1])
                if xy:geo[n].add(xy)
    rr=csv.DictReader(io.StringIO(a.decode('utf-8-sig')))
    assert set(rr.fieldnames)>={'zenodo_record_id','location','alias'}
    aliases=C.defaultdict(set);scope=C.Counter()
    for row in rr:
        s=norm(row['zenodo_record_id']);scope[s if s in ('','na','global','all','none','null','nan') else 'record_specific']+=1
        # Only explicit global scope (including missing id in source's documented schema).
        if s in ('','na','global','all','none','null','nan'):s='global'
        aliases[s,norm(row['alias'])].add(norm(row['location']))
    return geo,types,regions,aliases,{'gazetteer':r,'aliases':ar,'unique_location_keys':len(types),'geometry_types':dict(C.Counter(t for v in types.values() for t in v)),'alias_scope_types':dict(scope)}
def loadbook(rid,file,sha):
    b,rc=fetch(rid,file,20*1024**2,sha=sha)
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        assert sum(x.file_size for x in z.infolist())<=768*1024**2 and z.testzip() is None
    return load_workbook(io.BytesIO(b),read_only=True,data_only=True),rc
def locations(w):
    loc=C.defaultdict(list);stats=C.Counter()
    for r in w['Locations'].iter_rows(min_row=2,values_only=True):
        if r[0] is None:continue
        n=norm(r[0]);flag=norm(r[1]);xy=coord(r[3],r[2]);blank=r[2] is None and r[3] is None
        stats['new_flag_'+flag]+=1;stats['both_blank']+=int(blank);stats['valid_coordinate']+=int(xy is not None)
        loc[n].append((flag,xy,blank))
    return loc,dict(stats)
def resolve(names,rid,loc,geo,types,aliases):
    rec=[]
    for n in names:
        for flag,xy,blank in loc.get(n,[]):
            candidates=set()
            if n in types:candidates.add(n)
            candidates.update(aliases.get(('global',n),set()));candidates.update(aliases.get((str(rid),n),set()))
            pts=set().union(*(geo.get(x,set()) for x in candidates)) if candidates else set()
            if len(candidates)>1 or len(pts)>1:
                rec.append(('conflict',None));continue
            if xy is not None:
                if pts and gap(xy,next(iter(pts)))>10:rec.append(('conflict',None))
                else:rec.append(('direct',xy))
                continue
            if not blank or flag not in ('no','false','0','n'):
                rec.append(('no_admitted_point',None));continue
            if len(candidates)==1 and len(pts)==1:
                c=next(iter(candidates))
                if types[c]=={'Point'}:
                    rec.append(('official_exact' if c==n else 'official_alias',next(iter(pts))));continue
            rec.append(('nonpoint_or_unknown',None))
    xy={p for _,p in rec if p is not None}
    if any(k=='conflict' for k,_ in rec) or len(xy)>1:return 'conflict',None
    if not xy:return ('no_location_row' if not rec else rec[0][0]),None
    return next(k for k,p in rec if p is not None),next(iter(xy))
def timeparse(x):
    if isinstance(x,dt.datetime):return x.time()
    if isinstance(x,dt.time):return x
    if isinstance(x,str):
        for fmt in ('%H:%M:%S','%H:%M','%H:%M:%S.%f'):
            try:return dt.datetime.strptime(x.strip(),fmt).time()
            except ValueError:pass
    return None
def dateparse(x):
    if isinstance(x,dt.datetime):return x.date()
    if isinstance(x,dt.date):return x
    if isinstance(x,str):
        try:return dt.date.fromisoformat(x.strip())
        except ValueError:pass
    return None
def main():
    out={}
    try:
        geo,types,regions,aliases,receipt=loadgaz();out['gazetteer']=receipt
        w,rc=loadbook(5018280,'Haysom_etal_2021_Frontiers.xlsx','7c356be1ecae1a4a6a0a118fe2ca508c2afb7277eaf93a1e771df76234084c2a')
        loc,ls=locations(w);eff=C.Counter()
        for r in w['Rarefaction_Input'].iter_rows(min_row=11,values_only=True):
            if all(v is None for v in r):continue
            k=key(r[1]);assert k;eff[k]+=1
        pp=C.defaultdict(dict);forward=C.defaultdict(set);reverse=C.defaultdict(set)
        for r in w['Ordination_Input'].iter_rows(min_row=11,values_only=True):
            if all(v is None for v in r):continue
            k=key(r[1]);f=norm(r[2]);t=norm(r[3]);st=norm(r[4]);l='C' if st=='canopy' else 'T'
            assert k and st in ('canopy','terrestrial') and k[1]==l and l not in pp[f,t] and k in eff
            pp[f,t][l]=(k,sum(r[5:]));forward[f,t].add(k[0]);reverse[k[0]].add((f,t))
        assert len(forward)==len(reverse)==48 and all(len(v)==1 for v in list(forward.values())+list(reverse.values()))
        stat=C.Counter();forest=C.Counter();joined=C.Counter()
        for (f,t),d in pp.items():
            if set(d)!={'C','T'}:continue
            a,b=d['C'],d['T'];assert a[0][0]==b[0][0]
            if min(eff[a[0]],eff[b[0]])<91 or min(a[1],b[1])<=0:continue
            forest[f]+=1;k,xy=resolve(set((t,a[0][0])),5018280,loc,geo,types,aliases)
            stat[k]+=1;joined[f]+=int(xy is not None)
        assert forest==C.Counter({'unlogged':16,'logged':11})
        out['haysom']={'source':rc,'location_rows':ls,'paired_forests':dict(forest),'resolution':dict(stat),'georeferenced_by_forest':dict(joined)};w.close()
        w,rc=loadbook(7740421,'SAFE_data_archive_Yoh2.xlsx','0c874b45b265d326c9cff12db30f96fa6cbf5f19cbfe24530a64bc72fcf25da2')
        loc,ls=locations(w);dates=C.defaultdict(set);nights=C.defaultdict(set);structures=C.defaultdict(set);hab=C.defaultdict(set)
        seen=set();clockseen=set();exactdup=0;clockdup=0;clockbad=0;inwindow=0;count=0;tt=C.Counter();dtp=C.Counter();labels=C.Counter()
        for r in w['MasterData'].iter_rows(min_row=11,values_only=True):
            if all(v is None for v in r):continue
            count+=1;n=norm(r[1]);lab=norm(r[8]);labels[lab]+=1;hab[n].add(norm(r[9]))
            full=tuple(r[1:]);exactdup+=int(full in seen);seen.add(full)
            dtp[type(r[2]).__name__]+=1;tt[type(r[3]).__name__]+=1
            da=dateparse(r[2]);ti=timeparse(r[3])
            if da and ti:
                dates[n].add(da);sec=ti.hour*3600+ti.minute*60+ti.second+ti.microsecond/1e6
                nights[n].add(da-dt.timedelta(days=int(ti.hour<12)))
                inwindow+=int(sec>=18*3600+15*60 or sec<=6*3600+15*60)
                k=(n,da,ti,lab);clockdup+=int(k in clockseen);clockseen.add(k)
            else:clockbad+=1
            vals=[]
            for v in r[10:14]:
                try:
                    x=float(v);vals.append(x if math.isfinite(x) else None)
                except (ValueError,TypeError):vals.append(None)
            structures[n].add(tuple(vals))
        assert count==134920 and len(hab)==45 and len(labels)==21
        stat=C.Counter();byhab=C.defaultdict(C.Counter);complete=0;completegeo=0
        for n in hab:
            assert len(hab[n])==1
            f=next(iter(hab[n]));k,xy=resolve([n],7740421,loc,geo,types,aliases)
            stat[k]+=1
            byhab[f]['sites']+=1;byhab[f]['georeferenced']+=int(xy is not None)
            comp=len(structures[n])==1 and None not in next(iter(structures[n]))
            complete+=int(comp);completegeo+=int(comp and xy is not None);byhab[f]['complete_structure_and_geo']+=int(comp and xy is not None)
        out['yoh']={'source':rc,'location_rows':ls,'resolution':dict(stat),'support_by_habitat':{k:dict(v) for k,v in byhab.items()},'complete_structure':complete,'complete_structure_and_geo':completegeo,'rows':count,'identical_row_repetitions':exactdup,'same_site_date_time_label_repetitions':clockdup,'unparsed_date_time':clockbad,'within_published_clock_window':inwindow,'date_types':dict(dtp),'time_types':dict(tt),'observed_night_count_distribution':dict(C.Counter(len(nights[n]) for n in hab))};w.close()
        out['status']='audit_complete'
    except Exception as e:out.update(status='stopped',error=type(e).__name__+': '+str(e)[:160])
    Path('safe_v8c_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
if __name__=='__main__':main()
