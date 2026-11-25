"""Frozen paired-camera resource contrast; read-only source replay; aggregate output only."""
import sys, pathlib, hashlib, json, zipfile
import numpy as np, pandas as pd
from scipy.special import gammaln, logsumexp
from scipy.optimize import minimize

zip_path=pathlib.Path(sys.argv[1]); output=pathlib.Path(sys.argv[2]); root=pathlib.Path(__file__).resolve().parent
replay=root/'marker_replay.py'
# Reuse exactly the authenticated pre-fit parser and reconciliation, before its old endpoint.
code=replay.read_bytes()
assert hashlib.sha256(code).hexdigest()=='8288d5b1a9d1360c9da3d107036a00ffacfdcaf5524664c947e37914318d51c3'
prefix=code.decode().split('# Separate source integrity from a predeclared scientific support gate.')[0]
assert len(prefix)<len(code) and (root/'diagnostic_no_correction2.json').exists()
old_argv=sys.argv; sys.argv=[str(replay),str(zip_path),str(root/'replay_prefit_resource.json')]
ns={}; exec(compile(prefix,str(replay),'exec'),ns);sys.argv=old_argv
# Ground passes and active detector inventory from authenticated old pre-fit stage.
ground=ns['ground'].copy();inv=ns['inv'].copy()
assert ns['res']['ground_behavior']=={'Commuting':14626,'Feeding':4033,'Social':547}
assert ns['res']['source_sha256']['raw_insect_data_tidied_27112023.csv']=='f0dc944fccc73779dd5441510fa0a3d871baecaa87adc2aa14788ee13df3fcfb'
with zipfile.ZipFile(zip_path) as z:
    cam=pd.read_csv(z.open('raw_insect_data_tidied_27112023.csv'))
res={'scope':'post-V3 secondary mechanism exploration; two camera localities; no true prey density, causal effect, new regions or 3D SDM','contract':'MARKER_RESOURCE_CONTRACT_V1.md','source_sha256':ns['res']['source_sha256'],'source_zip_sha256':ns['res']['zip_sha256'],'input_rows':len(cam)}
def finish(status):
    res['status']=status; output.write_text(json.dumps(res,indent=2)+'\n'); print(json.dumps(res,indent=2))

# Camera lexical month.day.year differs from README. All dates resolve under actual format and survey range.
cam['dt']=pd.to_datetime(cam.Date+' '+cam.Time,format='%m.%d.%Y %H:%M:%S',errors='raise')
assert cam.dt.between('2020-07-01','2020-10-01',inclusive='left').all()
assert not cam.duplicated(['Site','dt']).any() and cam.Hour.eq(cam.dt.dt.hour).all()
assert set(cam.Site)=={'C08','P08','C11','P11'} and set(cam.Viable)=={'Yes','No'}
valid=cam.Viable.eq('Yes'); assert cam.loc[valid,['Count','InsectPresAbs']].notna().all().all()
assert cam.loc[~valid,['Count','InsectPresAbs']].isna().all().all()
assert (cam.loc[valid,'Count']>=0).all() and (cam.loc[valid,'Count']%1==0).all()
assert cam.loc[valid,'Count'].gt(0).astype(int).eq(cam.loc[valid,'InsectPresAbs']).all()
res['valid_photos']=int(valid.sum());res['unviable_photos']=int((~valid).sum());res['camera_date_format']='MM.DD.YYYY, inconsistent with README';res['camera_keys_unique']=True
cam=cam.loc[valid].copy();cam['site']=cam.Site.str.replace('C','N',regex=False);cam['loc']=cam.site.str[1:];cam['side']=cam.site.str[0];cam['hour']=cam.dt.dt.floor('h');cam['night']=(cam.hour-pd.Timedelta(hours=12)).dt.normalize()
# Confirm time alignment on all source ground passes, including outside the camera subset.
ground['hour']=pd.to_datetime(ground['DATE']+' '+ground['HOUR'].astype(int).astype(str).str.zfill(2)+':00:00',format='%Y-%m-%d %H:%M:%S',errors='raise')
ground['night']=(ground.hour-pd.Timedelta(hours=12)).dt.normalize();assert ground.night.eq(pd.to_datetime(ground['DATE.12'],format='%Y-%m-%d')).all();assert (ground.hour-pd.Timedelta(hours=12)).dt.hour.eq(ground['HOUR.12'].astype(int)).all()
res['ground_clock_alignment_verified']=True
inv=inv.loc[inv.site.isin(cam.site.unique()),['site','night','active.night']].copy();assert inv['active.night'].eq(True).all()
cam=cam.merge(inv,on=['site','night'],how='inner',validate='many_to_one');res['valid_photos_on_active_nights']=len(cam)
h=cam.groupby(['loc','night','hour','side']).Count.agg(n='size',avg='mean').unstack('side');h.columns=[a+b for a,b in h.columns];h=h.reset_index();h=h.loc[h.nN.ge(3)&h.nP.ge(3)].copy();res['paired_camera_hours_pre_night_gate']=len(h)
n=h.groupby(['loc','night']).size();keep=n[n>=3].index;h=h.loc[pd.MultiIndex.from_frame(h[['loc','night']]).isin(keep)].copy();res['paired_camera_hours']=len(h);res['paired_camera_nights']=len(keep);res['photos_in_matched_hours']=int((h.nN+h.nP).sum());res['camera_nights_per_locality']=h.groupby('loc').night.nunique().sort_index().tolist()
# Equal hour weights; no response used in choosing the resource support.
r=h.groupby(['loc','night']).agg(resourceN=('avgN','mean'),resourceP=('avgP','mean'),hours=('hour','size')).reset_index();r['d']=np.log1p(r.resourceN)-np.log1p(r.resourceP)
res['resource_contrast_quantiles']=np.quantile(r.d,[0,.25,.5,.75,1]).tolist() if len(r) else []
ground['loc']=ground.site.str[1:];ground['side']=ground.site.str[0];ground=ground.loc[ground.guild.isin(['SRE','LRE'])].copy();ground=ground.merge(h[['loc','night','hour']],on=['loc','night','hour'],how='inner',validate='many_to_one');ground['marked']=ground.behavior.eq('Feeding').astype(int);res['matched_target_guild_passes']=len(ground);res['matched_feeding_passes']=int(ground.marked.sum())
q=ground.groupby(['loc','night','guild','side']).marked.agg(n='size',f='sum').unstack('side',fill_value=0);q.columns=[a+b for a,b in q.columns];q=q.reset_index().merge(r[['loc','night','d']],on=['loc','night'],validate='many_to_one');q['f']=q.fN+q.fP;q['k']=q.fN
res['both_pass_strata']=int((q.nN.gt(0)&q.nP.gt(0)).sum());s=q.loc[q.nN.gt(0)&q.nP.gt(0)&q.f.gt(0)&q.f.lt(q.nN+q.nP)].copy();s['week']=((s.night-pd.Timestamp('2020-07-01')).dt.days//7).astype(int)
locs=sorted(r['loc'].unique());cats=[(l,g) for l in locs for g in ['SRE','LRE']];cnt=s.groupby(['loc','guild']).size().reindex(pd.MultiIndex.from_tuples(cats),fill_value=0)
res['informative_strata']=len(s);res['informative_per_locality_guild']=[{'locality':i//2+1,'guild':g,'n':int(cnt[l,g])} for i,(l,g) in enumerate(cats)]
ws=s.groupby('week')['loc'].nunique();weeks=sorted(s.week.unique());res['weeks_total']=len(weeks);res['weeks_both_localities']=int(ws.eq(2).sum())
res['support_gate']=bool(len(locs)==2 and len(cats)==4 and cnt.ge(12).all() and ws.eq(2).sum()>=6 and all(set(zip(s.loc[s.week.ne(w),'loc'],s.loc[s.week.ne(w),'guild']))==set(cats) for w in weeks))
if not res['support_gate']:
    finish('STOP_INSUFFICIENT_MATCHED_RESOURCE_SUPPORT');sys.exit(0)
# Fixed log-likelihood and gradients, evaluated on the exact same held-out rows.
catmap={c:i for i,c in enumerate(cats)}
def lc(n,k):return gammaln(n+1)-gammaln(k+1)-gammaln(n-k+1)
rows=[]
for x in s.itertuples(index=False):
    lo=max(0,x.f-x.nP); hi=min(x.nN,x.f); ks=np.arange(lo,hi+1); c=lc(x.nN,ks)+lc(x.nP,x.f-ks)
    rows.append(dict(loc=x.loc,guild=x.guild,week=int(x.week),k=x.k,ks=ks,c=c,ck=float(c[x.k-lo]),d=float(x.d),cat=catmap[(x.loc,x.guild)]))
def design(row,m):
    x=np.zeros(m);x[row['cat']]=1
    if m==5:x[4]=row['d']
    if m==6:x[4+(row['guild']=='LRE')]=row['d']
    return x
def stat(row,b):
    u=row['c']+b*row['ks'];z=logsumexp(u);return row['ck']+b*row['k']-z, float(np.dot(row['ks'],np.exp(u-z)))
def objective(b,rr):
    counts={l:sum(r['loc']==l for r in rr) for l in locs};L=len([c for c in counts.values() if c]);v=.1*np.dot(b,b);grad=.2*b.copy()
    for r in rr:
        x=design(r,len(b));lp,e=stat(r,float(x@b));w=1/(L*counts[r['loc']]);v-=w*lp;grad+=w*(e-r['k'])*x
    return v,grad
def fit(rr,m):
    z=minimize(objective,np.zeros(m),args=(rr,),jac=True,method='L-BFGS-B',bounds=[(-6,6)]*m,options={'ftol':1e-13,'gtol':1e-9,'maxiter':1000})
    if not z.success:raise RuntimeError('fit nonconvergence: '+str(z.message))
    return z.x
# numerical checks: normalized conditional mass, swap, and finite difference gradient
r0=rows[0]; beta=.7; u=r0['c']+beta*r0['ks'];assert abs(np.exp(u-logsumexp(u)).sum()-1)<1e-12
b=np.linspace(-.3,.3,5); _,g=objective(b,rows);eps=1e-5;gn=np.array([(objective(b+np.eye(5)[i]*eps,rows)[0]-objective(b-np.eye(5)[i]*eps,rows)[0])/(2*eps) for i in range(5)]);assert np.max(abs(g-gn))<1e-6
res['gradient_max_error']=float(np.max(abs(g-gn))); held=[];fold=[]
for wi,w in enumerate(weeks):
    tr=[r for r in rows if r['week']!=w];te=[r for r in rows if r['week']==w];bs=[fit(tr,m) for m in [4,5,6]]
    fold.append({'week':wi+1,'n_test':len(te),'gamma':float(bs[1][4]),'gamma_SRE':float(bs[2][4]),'gamma_LRE':float(bs[2][5])})
    for r in te:
        scores=[stat(r,0)[0]]+[stat(r,float(design(r,len(b))@b))[0] for b in bs];held.append({'loc':r['loc'],'guild':r['guild'],'week':wi+1,**{f'A{i}':x for i,x in enumerate(scores)}})
df=pd.DataFrame(held); df['A1_A0']=df.A1-df.A0;df['A2_A1']=df.A2-df.A1;df['A3_A2']=df.A3-df.A2;df['A2_A0']=df.A2-df.A0
cols=['A0','A1','A2','A3','A1_A0','A2_A1','A3_A2','A2_A0'];eq=lambda d:d.groupby('loc')[cols].mean().mean().to_dict()
res['means']=eq(df);res['locality_scores']=[{'locality':i+1,**eq(df[df['loc']==l])} for i,l in enumerate(locs)]
for f in fold:f.update(eq(df[df.week.eq(f['week'])]));f['both_localities']=df.loc[df.week.eq(f['week']),'loc'].nunique()==2
res['folds']=fold;res['week_omission_primary_range']=[float(min(eq(df[df.week.ne(w)])['A2_A1'] for w in df.week.unique())),float(max(eq(df[df.week.ne(w)])['A2_A1'] for w in df.week.unique()))]
res['positive_weeks']=sum(f['A2_A1']>0 for f in fold);res['gamma_median']=float(np.median([f['gamma'] for f in fold]));res['directional_screen']=bool(res['means']['A2_A1']>0 and all(v['A2_A1']>0 for v in res['locality_scores']) and res['positive_weeks']>len(fold)/2 and res['week_omission_primary_range'][0]>0 and res['gamma_median']>0)
finish('EMPIRICAL_RESOURCE_CONDITIONAL_PREDICTION_COMPLETE_DESCRIPTIVE_ONLY')
