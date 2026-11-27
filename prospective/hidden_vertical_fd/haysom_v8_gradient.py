"""V8: frozen paired-camera structural-gradient analysis. No location-level output."""
import collections as C
import hashlib, io, json, math, re, sys, urllib.request, zipfile
from contextlib import ExitStack
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
import rasterio
from rasterio.io import MemoryFile
from rasterio.windows import Window
from pyproj import CRS, Transformer

def get(url, cap):
    q=urllib.request.Request(url,headers={'User-Agent':'batter-public-source-audit/1.0'})
    with urllib.request.urlopen(q,timeout=70) as r: b=r.read(cap+1)
    if len(b)>cap: raise ValueError('size limit')
    return b

def metadata(rid):
    m=json.loads(get(f'https://zenodo.org/api/records/{rid}',2*1024*1024))
    assert int(m['id'])==rid
    return {x['key']:x for x in m['files']}

def source_file(f, cap, sha=None):
    n=int(f['size']);assert n<=cap
    assert f['links']['self'].startswith('https://zenodo.org/')
    b=get(f['links']['self'],cap)
    a,h=f['checksum'].split(':',1)
    assert a in ('md5','sha256') and len(b)==n and hashlib.new(a,b).hexdigest()==h
    s=hashlib.sha256(b).hexdigest()
    if sha: assert s==sha
    return b, {'size':n,'publisher_checksum':f['checksum'],'sha256':s}

def norm(x): return ' '.join(str(x if x is not None else '').strip().casefold().split())
def key(x):
    m=re.fullmatch(r'(.+?)(?:_)?([ct])',norm(x))
    return (m[1],m[2].upper()) if m else None
def numeric(v,n):
    return len(v)==n and all(isinstance(x,(int,float)) and math.isfinite(x) and x>=0 and int(x)==x for x in v)
def parse(s,offset,n):
    r=list(s.iter_rows(min_row=1,max_row=10,values_only=True))
    assert norm(r[9][0])=='field_name' and norm(r[4][0])=='taxon_name'
    h=r[9][offset:]; t=r[4][offset:]
    assert len(h)==n and len(set(map(norm,h)))==n and list(map(norm,h))==list(map(norm,t))
    return h
def metrics(a,b,mode):
    if mode=='incidence': a=(a>0).astype(float); b=(b>0).astype(float)
    p=a/a.sum();q=b/b.sum();qa=1-p@p;qt=1-q@q;c=1-p@q
    if mode=='rarefied':
        m=min(a.sum(),b.sum())
        if m<2:return None
        qa*=((m-1)/m)*(a.sum()/(a.sum()-1))
        qt*=((m-1)/m)*(b.sum()/(b.sum()-1))
    alpha=(qa+qt)/2
    v=np.array([qa,qt,c,alpha,(c-alpha)/2,(c+alpha)/2])
    assert abs(v[3]+v[4]-v[5])<1e-10
    return v

def camera_data(out):
    f=metadata(5018280)['Haysom_etal_2021_Frontiers.xlsx']
    b,receipt=source_file(f,20*1024**2,'7c356be1ecae1a4a6a0a118fe2ca508c2afb7277eaf93a1e771df76234084c2a')
    out['camera_source']=receipt
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        assert sum(x.file_size for x in z.infolist())<=768*1024**2 and z.testzip() is None
    w=load_workbook(io.BytesIO(b),read_only=True,data_only=True)
    rare=w['Rarefaction_Input'];ordn=w['Ordination_Input']
    parse(rare,2,55);parse(ordn,5,43)
    eff=C.Counter();ev=0
    for row in rare.iter_rows(min_row=11,values_only=True):
        if all(x is None for x in row):continue
        k=key(row[1]);assert k and numeric(row[2:],55)
        eff[k]+=1;ev+=sum(row[2:])
    assert (len(eff),sum(eff.values()),ev)==(100,16013,7999)
    pp=C.defaultdict(dict);forward=C.defaultdict(set);reverse=C.defaultdict(set);seen=set()
    for r in ordn.iter_rows(min_row=11,values_only=True):
        if all(x is None for x in r):continue
        k=key(r[1]);f=norm(r[2]);t=norm(r[3]);st=norm(r[4])
        assert k and f in ('logged','unlogged') and t and st in ('canopy','terrestrial')
        l='C' if st=='canopy' else 'T'
        assert k[1]==l and k in eff and k not in seen and l not in pp[f,t] and numeric(r[5:],43)
        seen.add(k);forward[f,t].add(k[0]);reverse[k[0]].add((f,t));pp[f,t][l]=(k,np.array(r[5:],dtype=float))
    assert len(seen)==79 and len(forward)==len(reverse)==48 and all(len(x)==1 for x in list(forward.values())+list(reverse.values()))
    loc=C.defaultdict(set); invalid=0
    for r in w['Locations'].iter_rows(min_row=2,values_only=True):
        if not r[0]:continue
        try:
            lat,lon=float(r[2]),float(r[3])
            assert 0<lat<10 and 110<lon<125
            loc[norm(r[0])].add((lon,lat))
        except (ValueError,TypeError,AssertionError):invalid+=1
    w.close()
    pairs=[];locstat=C.Counter()
    for (f,t),d in pp.items():
        if set(d)!={'C','T'}:continue
        ka,a=d['C'];kb,b=d['T'];assert ka[0]==kb[0]
        if min(eff[ka],eff[kb])<91 or min(a.sum(),b.sum())<=0:continue
        coords=loc.get(ka[0],set())|loc.get(t,set())
        locstat['base_exact']+=int(ka[0] in loc);locstat['tree_exact']+=int(t in loc)
        xy=next(iter(coords)) if len(coords)==1 else None
        if xy is None:locstat['missing_or_conflict']+=1
        pairs.append(dict(forest=f,a=a,b=b,xy=xy))
    ns=C.Counter(p['forest'] for p in pairs)
    assert dict(ns)=={'unlogged':16,'logged':11}
    # All prior count/incidence means from V7b (fixed source replay).
    expected={
      ('count','unlogged'):[.3836970956683327,.7644491310839971,.9567933656589014,.5740731133761648,.19136012614136824,.765433239517533],
      ('count','logged'):[.5511704520948307,.7588772816263197,.9823522359556123,.6550238668605753,.16366418454751852,.8186880514080936],
      ('incidence','unlogged'):[.43898809523809534,.9033407564657565,.9832271316646318,.6711644258519258,.1560313529063529,.8271957787582787],
      ('incidence','logged'):[.6681818181818182,.8928440246622066,.9773591980410162,.7805129214220122,.09842313830950195,.8789360597315142]}
    err=max(float(np.max(np.abs(np.mean([metrics(p['a'],p['b'],m) for p in pairs if p['forest']==f],axis=0)-v))) for (m,f),v in expected.items())
    assert err<1e-8
    out['camera_support']={'n':len(pairs),'forests':dict(ns),'V7b_max_absolute_replay_error':err,'location_keys':len(loc),'invalid_location_rows':invalid,'location_match':dict(locstat),'located':sum(p['xy'] is not None for p in pairs)}
    return pairs

def region_files(out,stack):
    files=metadata(4020697);regions={};receipts={};stops={}
    kinds=['pad_canopy_height','pai','pai_02_10m']
    wanted=[f'{r}_{k}.tif' for r in ['Danum','Maliau','SAFE'] for k in kinds]
    assert all(k in files for k in wanted) and sum(int(files[k]['size']) for k in wanted)<=60*1024**2
    for r in ['Danum','Maliau','SAFE']:
        try:
            ds=[]
            for k in kinds:
                fn=f'{r}_{k}.tif';b,rc=source_file(files[fn],20*1024**2)
                receipts[fn]=rc
                mf=stack.enter_context(MemoryFile(b));d=stack.enter_context(mf.open());ds.append(d)
            d=ds[0];crs=CRS.from_user_input(d.crs)
            assert crs.is_projected and all(abs(a.unit_conversion_factor-1)<1e-6 for a in crs.axis_info[:2])
            T=d.transform
            assert abs(T.a-20)<.1 and abs(T.e+20)<.1 and abs(T.b)<1e-9 and abs(T.d)<1e-9
            assert all(x.count==1 and x.crs==d.crs and x.transform.almost_equals(T,precision=1e-8) and x.shape==d.shape for x in ds)
            regions[r]=(ds,Transformer.from_crs(4326,crs,always_xy=True))
        except Exception as e:stops[r]=type(e).__name__+': '+str(e)[:140]
    out['raster_receipts']=receipts;out['raster_regions_admitted']=list(regions);out['raster_region_stops']=stops
    return regions

def buffer_values(ds,transform,xy):
    x,y=transform.transform(*xy);d=ds[0];t=d.transform
    c0=math.floor((x-100-t.c)/t.a); c1=math.ceil((x+100-t.c)/t.a)
    r0=math.floor((t.f-y-100)/(-t.e));r1=math.ceil((t.f-y+100)/(-t.e))
    cols=np.arange(c0,c1);rows=np.arange(r0,r1)
    inside=(t.c+(cols[None,:]+.5)*t.a-x)**2+(t.f+(rows[:,None]+.5)*t.e-y)**2<=100**2
    nominal=int(inside.sum())
    rr0=max(0,r0);rr1=min(d.height,r1);cc0=max(0,c0);cc1=min(d.width,c1)
    if rr1<=rr0 or cc1<=cc0:return None
    mask=inside[rr0-r0:rr1-r0,cc0-c0:cc1-c0].copy()
    arrays=[v.read(1,window=Window(cc0,rr0,cc1-cc0,rr1-rr0),masked=True).astype(float) for v in ds]
    for a in arrays:mask&=~np.ma.getmaskarray(a)&np.isfinite(a.filled(np.nan))
    h,p,l=[a.filled(np.nan) for a in arrays]
    mask&=(h>0)&(p>0)&(l>=0)&(l<=p+1e-6)
    n=int(mask.sum());coverage=n/nominal if nominal else 0
    if coverage<.8:return None
    val=np.array([np.mean(h[mask]),np.mean(p[mask]),np.mean(l[mask])/np.mean(p[mask])])
    assert np.all(np.isfinite(val)) and val[1]>0 and 0<=val[2]<=1+1e-6
    return val,coverage

def fit(x,y,xt,model):
    if model=='N':return np.full((len(xt),y.shape[1]),y.mean(axis=0)),None
    n={'F':1,'H':3,'L':4,'Q':4}[model]
    x=x[:,:n];xt=xt[:,:n]
    mu=x.mean(0);sd=x.std(0);sd=np.where(sd>1e-12,sd,1.)
    z=(x-mu)/sd;zt=(xt-mu)/sd
    info=None
    if model=='Q':
        a=z[:,3]**2;b=zt[:,3]**2;m=a.mean();s=a.std()
        if s<=1e-12:s=1.
        z=np.column_stack((z,(a-m)/s));zt=np.column_stack((zt,(b-m)/s))
    Z=np.column_stack((np.ones(len(z)),z));ZT=np.column_stack((np.ones(len(zt)),zt))
    penalty=np.eye(Z.shape[1]);penalty[0,0]=0
    beta=np.linalg.solve(Z.T@Z+penalty,Z.T@y)
    if model=='Q':
        q=beta[-1]/s;lin=beta[-2];peak=np.divide(-lin,2*q,out=np.full_like(q,np.nan),where=abs(q)>1e-12)*sd[3]+mu[3]
        info={'quadratic_raw':(q/sd[3]**2).tolist(),'turning_point':[float(v) if np.isfinite(v) else None for v in peak]}
    return ZT@beta,info

def cv(pairs,mode,grain):
    use=[p for p in pairs if mode!='rarefied' or min(p['a'].sum(),p['b'].sum())>=2]
    x=np.array([[int(p['forest']=='logged'),p['structure'][0],math.log(p['structure'][1]),p['structure'][2]] for p in use])
    y=np.array([metrics(p['a'],p['b'],mode) for p in use])
    fs=C.Counter(p['forest'] for p in use); blocks=C.defaultdict(list)
    for i,p in enumerate(use):blocks[tuple(math.floor(v/grain) for v in p['utm'])].append(i)
    result={'n':len(use),'forest_counts':dict(fs),'blocks':len(blocks),'block_sizes':sorted(map(len,blocks.values()))}
    if len(use)<20 or any(fs[f]<8 for f in ('logged','unlogged')) or len(blocks)<5:
        return {**result,'status':'insufficient_support'}
    for ii in blocks.values():
        tr=np.ones(len(use),bool);tr[ii]=False
        if tr.sum()<15 or len(set(x[tr,0]))!=2:return {**result,'status':'insufficient_training_support'}
    result['structural_ranges_by_forest']={f:{'height': [float(np.min(x[x[:,0]==i,1])),float(np.max(x[x[:,0]==i,1]))],'pai':[float(np.exp(np.min(x[x[:,0]==i,2]))),float(np.exp(np.max(x[x[:,0]==i,2])))],'low_fraction':[float(np.min(x[x[:,0]==i,3])),float(np.max(x[x[:,0]==i,3]))]} for i,f in enumerate(['unlogged','logged'])}
    mods=['N','F','H','L','Q'];mse={m:[] for m in mods};shape=[]
    for _,ii in sorted(blocks.items()):
        tr=np.ones(len(use),bool);tr[ii]=False
        for m in mods:
            pred,s=fit(x[tr],y[tr],x[ii],m);mse[m].append(np.mean((pred-y[ii])**2,axis=0))
            if m=='Q':shape.append(s)
    result['mse']={m:np.mean(v,axis=0).tolist() for m,v in mse.items()}
    gains={}
    for a,b in [('F','N'),('H','F'),('L','H'),('L','N'),('Q','L'),('Q','N')]:
        g=np.asarray(mse[b])-np.asarray(mse[a])
        gains[a+'-'+b]={'mean':g.mean(0).tolist(),'positive_blocks':(g>0).sum(0).tolist(),'range':[g.min(0).tolist(),g.max(0).tolist()],'canopy_by_block':g[:,0].tolist()}
    result['gains']=gains
    _,info=fit(x,y,x,'Q');result['full_quadratic']=info
    result['ratio_central_10_90']=np.quantile(x[:,3],[.1,.9]).tolist();result['fold_quadratic']=shape
    result['status']='scored'
    return result

def main():
    out={'metric_order':['Q_canopy','Q_ground','cross','alpha','beta','gamma']}
    try:
        pairs=camera_data(out)
        with ExitStack() as stack:
            regions=region_files(out,stack);joined=[];stat=C.Counter();cov=[];utm=Transformer.from_crs(4326,32650,always_xy=True)
            for p in pairs:
                if p['xy'] is None:stat['missing_location']+=1;continue
                candidates=[]
                for name,(ds,t) in regions.items():
                    v=buffer_values(ds,t,p['xy'])
                    if v is not None:candidates.append((name,*v))
                if len(candidates)!=1:stat['no_qualifying_region' if not candidates else 'ambiguous_region']+=1;continue
                name,v,c=candidates[0];stat['region_'+name]+=1;cov.append(c)
                joined.append({**p,'structure':v,'utm':utm.transform(*p['xy'])})
        out['join']={'n':len(joined),'counts':dict(stat),'forests':dict(C.Counter(p['forest'] for p in joined)),'coverage_range':[min(cov),max(cov)] if cov else None}
        if len(joined)>=20:
            out['tests']={f'{m}_{g}':cv(joined,m,g) for m in ['count','incidence','rarefied'] for g in [1000,2000]}
            out['status']='completed' if any(v['status']=='scored' for v in out['tests'].values()) else 'nonadmitted_support'
        else:out['status']='nonadmitted_join'
    except Exception as e:out.update(status='stopped',error=type(e).__name__+': '+str(e)[:240])
    Path('haysom_v8_gradient.json').write_text(json.dumps(out,indent=2,allow_nan=False));print(json.dumps(out,allow_nan=False))
if __name__=='__main__':main()
