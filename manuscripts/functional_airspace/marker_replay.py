import pandas as pd, numpy as np, zipfile, hashlib, json, sys, re
from pathlib import Path
from scipy.special import gammaln, logsumexp
from scipy.optimize import brentq
P=Path(sys.argv[1]); OUT=Path(sys.argv[2]); DIAGNOSTIC="--diagnostic" in sys.argv[3:]
EXPECT={'cleaed_manual.output_27.11.2023.csv':'5b38a948d10488702c99bae21dd65fb511100b3b2025822c2a838e18f9313a71','Marker_night_inventory_0704.2022_edit_(2).csv':'dedcd14bffc2c29696b58b085ffd8de49fb7526eb24478eae13a5a73ed3a9561','raw_insect_data_tidied_27112023.csv':'f0dc944fccc73779dd5441510fa0a3d871baecaa87adc2aa14788ee13df3fcfb','README.md':'ff378f60cdeaf8e2246bd3b219f8095459237b5045cc32988e5dfe3911b08109','Turbines_(3).kml':'7704b87af5d0d4945a01e23573cce0655ff1edd14948237561531ffeeca4824d'}
with zipfile.ZipFile(P) as z:
    receipt={n:hashlib.sha256(z.read(n)).hexdigest() for n in EXPECT}; assert receipt==EXPECT
    raw=pd.read_csv(z.open('cleaed_manual.output_27.11.2023.csv'),low_memory=False)
    inv=pd.read_csv(z.open('Marker_night_inventory_0704.2022_edit_(2).csv'),sep=';')
res={'scope':'original source replay, paired-site observed feeding-mark allocation, not abundance/true capture/causal selection','zip_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'source_sha256':receipt,'raw_rows':len(raw),'author_cleaning_code_blob':'043a31dfa6c475898059d99cf49ae4a0fbdb4770'}
a=raw.loc[raw['AUTO.ID.'].notna() & raw['AUTO.ID.'].ne('Noise')].copy(); res['after_auto_noise']=len(a)
# The published Rmd assigns undefined mo; use immediately preceding read_csv, not an imagined second source.
fix1='S4U10067_20200716_232445_000_SREwLRE.wav'; fix2='S4U08483_20200808_002648_000.wav'; fix3='MARKER-2020_20200901_230046_000.wav'
for name in (fix1,fix2,fix3):assert a['IN.FILE'].eq(name).sum()==1
# literal published corrections; no regex escaping of author patterns.
a.loc[a['IN.FILE'].eq(fix1),'MANUAL.ID']='SRE__LRE';a.loc[a['IN.FILE'].eq(fix1),'IN.FILE']=fix1.replace('_SREwLRE','')
if not DIAGNOSTIC:
    a.loc[a['IN.FILE'].eq(fix2),'MANUAL.ID']=a.loc[a['IN.FILE'].eq(fix2),'MANUAL.ID'].str.replace('.B','',regex=True)
a.loc[a['IN.FILE'].eq(fix3),'MANUAL.ID']=a.loc[a['IN.FILE'].eq(fix3),'MANUAL.ID'].str.replace('BABA','SRE',regex=True)
s=a['MANUAL.ID']; assert s.notna().all()
for x,y in [('__',':'),('LRE_',''),('MRE_',''),('SRE_',''),('EMU','VEMU'),('VVEMU','VEMU'),('UNK_BABA_EPNI','NoID'),('UNK','NoID'),('_UNK','NoID'),('LRE1','LR1'),('.A/D','.S'),('.S/D','.S'),('.S/A','.S'),('PIPI','MR1'),('MR2','MR1'),('MRE1','MR1'),('MRE2','MR1'),('_NoID.S','NoID.S')]:s=s.str.replace(x,y,regex=True)
a['parsed']=s
res['multi_colon_rows']=int((s.str.count(':')>1).sum()); assert res['multi_colon_rows']==0
p=s.str.split(':',n=1,expand=True); cols=['INDIR','OUTDIR','IN.FILE','DURATION','DATE','TIME','HOUR','DATE.12','TIME.12','HOUR.12','AUTO.ID.','PULSES','MATCH.RATIO','MANUAL.ID']
bat1=a[cols].assign(label=p[0]);bat2=a[cols].assign(label=p[1]).dropna();res['second_pass_complete']=len(bat2)
# dplyr full_join on every column, including missing matching as default.
a=bat1.merge(bat2,how='outer',on=list(bat1.columns));res['parsed_passes']=len(a)
s=a.label
beh=np.select([s.str.contains('.B',regex=True,na=False),s.str.contains('.S',regex=True,na=False),s.str.contains('.B.S',regex=True,na=False),s.str.contains('.S.B',regex=True,na=False)],['Feeding','Social','Feeding','Feeding'],default='Commuting')
a['behavior']=np.where(a['MANUAL.ID'].eq('SRE_BABA'),'Commuting',beh)
res['before_manual_noise_behavior']=a.behavior.value_counts().to_dict()
for x,y in [('.B',''),('.S',''),('BA','BABA'),('EPNI.','EPNI'),('LRE','LR1'),('SRE.','SRE'),('SRE','SR1'),('VEMU.','VEMU')]:s=s.str.replace(x,y,regex=True)
a['taxon']=s;res['before_manual_noise_taxon']=s.value_counts().to_dict()
a=a.loc[a.taxon.ne('Noise') & a.taxon.notna()].copy();res['all_passes']=len(a)
gmap={x:g for g,ls in {'SRE':['BABA','SR1','PAUR'],'MRE':['MR1','PINA','PIPY'],'LRE':['EPNI','LR1','LR2','VEMU','NYNO'],'NoID':['NoID']}.items() for x in ls};a['guild']=a.taxon.map(gmap);assert a.guild.notna().all();res['guild_total']=a.guild.value_counts().to_dict()
site_pairs=[('MetA','Met45'),('MetB','Met95')]+[(q+str(i).zfill(2),('N' if q=='C' else 'P')+str(i).zfill(2)) for i in [2,4,8,9,10,11,14] for q in ['C','P']]
a['site']=np.select([a.OUTDIR.str.contains(x,regex=True,na=False) for x,_ in site_pairs],[y for _,y in site_pairs],default='UNMATCHED');assert a.site.ne('UNMATCHED').all()
res['site_role_count']=int(a.site.nunique());ground=a.loc[a.site.str.startswith(('N','P'))].copy();res['ground_passes']=len(ground);res['ground_behavior']=ground.behavior.value_counts().to_dict();res['tower_passes']=len(a)-len(ground)
inv['site']=inv.Site.replace(dict(site_pairs));inv['night']=pd.to_datetime(inv.night,format='%d.%m.%Y',errors='raise');assert inv['active.night'].eq(True).all() and not inv.duplicated(['site','night']).any();res['ground_active_nights']=int(inv.site.str.startswith(('N','P')).sum());res['total_active_nights']=len(inv)
expected={'after_auto_noise':19297,'second_pass_complete':186,'parsed_passes':19483,'all_passes':19438,'site_role_count':16,'ground_passes':19206,'tower_passes':232,'ground_active_nights':811,'total_active_nights':951}; mismatches={k:[res[k],v] for k,v in expected.items() if res[k]!=v};
for k,v in {'Feeding':4034,'Social':547}.items():
    if res['ground_behavior'].get(k)!=v:mismatches['ground_'+k]=[res['ground_behavior'].get(k),v]
res['reconciliation_mismatches']=mismatches
if DIAGNOSTIC:
    res['status']='DIAGNOSTIC_ONLY';OUT.write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2));sys.exit(0)
# Resolve the exact pre-existing one-count mismatch by reproducing the single author correction.
# The diagnostic run is pre-fit and does not estimate any ecological outcome.
if mismatches == {'ground_Feeding':[4033,4034]}:
    diagnostic_path=OUT.parent/'diagnostic_no_correction2.json'
    diagnostic=json.loads(diagnostic_path.read_text())
    assert diagnostic['source_sha256']==receipt and diagnostic['reconciliation_mismatches']=={}
    assert diagnostic['ground_behavior']['Feeding']==4034 and diagnostic['ground_behavior']['Commuting']==res['ground_behavior']['Commuting']-1
    res['reconciliation_resolution']='Documented author correction 2 changes one PAUR feeding label to commuting; pre-fit counterfactual matches published counts; retain final author labels.'
    mismatches={}
if mismatches:
    res['status']='STOP_RECONCILIATION';OUT.write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2));sys.exit(2)
# Separate source integrity from a predeclared scientific support gate.
ground['night']=pd.to_datetime(ground['DATE.12'],format='%Y-%m-%d',errors='raise');ground['marked']=ground.behavior.eq('Feeding').astype(int)
# only explicitly active observed detector nights; audit exclusions rather than invent zeros.
ground=ground.merge(inv[['site','night','active.night']],how='left',on=['site','night'],validate='many_to_one');res['ground_passes_unmatched_active_inventory']=int(ground['active.night'].isna().sum());res['unmatched_ground_feeding']=int(ground.loc[ground['active.night'].isna(),'marked'].sum())
ground=ground.loc[ground['active.night'].eq(True) & ground.guild.isin(['SRE','LRE'])].copy()
# site-level availability from inventory, independent of marks.
inv=inv.loc[inv.site.str.startswith(('N','P'))].copy();inv['loc']=inv.site.str[1:];inv['side']=inv.site.str[0]; paired=inv.groupby(['loc','night']).side.nunique();paired=paired.loc[paired.eq(2)].index
res['paired_active_nights']=len(paired)
ground['loc']=ground.site.str[1:];ground['side']=ground.site.str[0];ground=ground.loc[pd.MultiIndex.from_frame(ground[['loc','night']]).isin(paired)].copy()
res['paired_active_target_guild_passes']=len(ground);res['paired_active_target_guild_feeding']=int(ground.marked.sum())
q=ground.groupby(['loc','night','guild','side']).marked.agg(n='size',f='sum').unstack('side',fill_value=0);q.columns=[x+y for x,y in q.columns];q=q.reset_index();q['f']=q.fN+q.fP;q['k']=q.fN
s=q.loc[(q.nN>0)&(q.nP>0)&(q.f>0)&(q.f<q.nN+q.nP)].copy();counts=s.groupby(['loc','guild']).size().unstack(fill_value=0).reindex(index=sorted(inv['loc'].unique()),columns=['SRE','LRE'],fill_value=0)
# anonymized location identifiers, only aggregate support, never dates or original site labels.
res['informative_nights_by_anonymous_locality']=[{'locality':i+1,'SRE':int(r.SRE),'LRE':int(r.LRE)} for i,(_,r) in enumerate(counts.iterrows())]
keep=counts.index[counts.ge(5).all(axis=1)];res['eligible_localities']=len(keep);res['informative_strata_all']=len(s)
if len(keep)<6:
    res['status']='STOP_INSUFFICIENT_PAIRED_GUILD_SUPPORT';OUT.write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2));sys.exit(0)
s=s.loc[s['loc'].isin(keep)].copy();res['informative_strata_eligible']=len(s)
# exact noncentral hypergeometric conditional log likelihood; no fixed table limit.
def lc(n,k):return gammaln(n+1)-gammaln(k+1)-gammaln(n-k+1)
rows=[]
for r in s.itertuples(index=False):
    lo=max(0,r.f-r.nP);hi=min(r.nN,r.f);ks=np.arange(lo,hi+1);c=lc(r.nN,ks)+lc(r.nP,r.f-ks);rows.append((r.loc,r.guild,ks,c,r.k,float(c[r.k-lo])))
def stat(r,b):
    _,_,ks,c,k,ck=r;u=c+b*ks;z=logsumexp(u);return ck+b*k-z,float(np.dot(ks,np.exp(u-z)))
def fit(rs,g=None):
    n=pd.Series([r[0] for r in rs]).value_counts().to_dict();L=len(n);rs=[r for r in rs if g is None or r[1]==g]
    def grad(b):return .2*b+sum((stat(r,b)[1]-r[4])/(L*n[r[0]]) for r in rs)
    if grad(-6)>=0:return -6.
    if grad(6)<=0:return 6.
    return float(brentq(grad,-6,6,xtol=1e-12))
# exact invariant: normalizes, swap site sign, null mean.
r=('test','SRE',np.arange(9),lc(20,np.arange(9))+lc(20,8-np.arange(9)),4,0.)
assert abs(stat(r,0)[1]-4)<1e-12
out=[]
for i,l in enumerate(keep):
    tr=[r for r in rows if r[0]!=l];te=[r for r in rows if r[0]==l];b1=fit(tr);b2={g:fit(tr,g) for g in ['SRE','LRE']}
    lp=np.array([[stat(r,0)[0],stat(r,b1)[0],stat(r,b2[r[1]])[0]] for r in te]);m=lp.mean(axis=0);out.append({'locality':i+1,'n_strata':len(te),'M1_beta':b1,'M2_beta':b2,'M0':m[0],'M1':m[1],'M2':m[2],'M1_M0':m[1]-m[0],'M2_M1':m[2]-m[1],'M2_M0':m[2]-m[0]})
res['folds']=out;res['means']={k:float(np.mean([x[k] for x in out])) for k in ['M0','M1','M2','M1_M0','M2_M1','M2_M0']};d=np.array([x['M2_M0'] for x in out]);res['positive_localities']=int((d>0).sum());res['omission_mean_range']=[float((d.sum()-d).min()/(len(d)-1)),float((d.sum()-d).max()/(len(d)-1))];res['directional_screen']=bool(d.mean()>0 and res['omission_mean_range'][0]>0 and res['positive_localities']>=5);res['status']='EMPIRICAL_CONDITIONAL_PREDICTION_COMPLETE_DESCRIPTIVE_ONLY';OUT.write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
