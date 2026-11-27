"""Run: python whitworth_paired_v2.py <original user ZIP>
Recorded detection-session diversity only, not calibrated occupancy or FD of whole assemblage.
See WHITWORTH_PAIRED_ARCHIVE_CONTRACT_V2.md. Post-outcome decomposition explicitly separate.
"""
import hashlib, json, zipfile, sys
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist

p=sys.argv[1]
z=zipfile.ZipFile(p)
assert z.testzip() is None
assert hashlib.sha256(open(p,'rb').read()).hexdigest()=='9ea967aba1a1b1a9a38b4621594369f0d632998ba1efe7d535006ad8c6955330'
def read(n,**kw): return pd.read_csv(z.open(n),**kw)
a=read('occ_data_arb_6d.txt',index_col=0); t=read('occ_data_ter_6d.txt',index_col=0)
ea=read('occ_effort_arb_6d.txt',index_col=0); et=read('occ_effort_ter_6d.txt',index_col=0)
c=read('station_covariates.txt',sep='\t',index_col=0); s=read('species_data.txt',sep='\t').set_index('SPECIES')
assert a.index.equals(pd.Index(ea.UNIQUE)) and t.index.equals(pd.Index(et.UNIQUE))
assert c.UNIQUE.is_unique and c['UNIQUE.TER'].is_unique
assert set(a.index)<=set(c.UNIQUE) and set(t.index)<=set(c['UNIQUE.TER'])
for x,e in [(a,ea),(t,et)]: assert x.index.is_unique and np.all(x.values>=0) and np.all(x.values<=e.SESSIONS.to_numpy()[:,None])
cols=sorted(set(a)|set(t)); shared=sorted(set(a)&set(t)); assert (len(a.columns),len(t.columns),len(cols),len(shared))==(24,26,46,4)
d=c[c.UNIQUE.isin(a.index)&c['UNIQUE.TER'].isin(t.index)].copy().reset_index(drop=True)
assert len(d)==70
A=a.reindex(index=d.UNIQUE,columns=cols,fill_value=0).to_numpy(float); T=t.reindex(index=d['UNIQUE.TER'],columns=cols,fill_value=0).to_numpy(float)
eA=d.UNIQUE.map(ea.set_index('UNIQUE').SESSIONS).to_numpy(); eT=d['UNIQUE.TER'].map(et.set_index('UNIQUE').SESSIONS).to_numpy()
mass=pd.to_numeric(s.reindex(cols).WEIGHT,errors='coerce').to_numpy(); known=np.isfinite(mass)&(mass>0)
D=np.ones((len(cols),len(cols)))-np.eye(len(cols)); v=np.log(mass[known]); v=(v-v.min())/(v.max()-v.min()); DM=cdist(v[:,None],v[:,None],metric='cityblock')

def metrics(A,T,D):
    p=A/A.sum(1)[:,None]; q=T/T.sum(1)[:,None]; m=(p+q)/2
    Q=lambda x:np.einsum('ij,jk,ik->i',x,D,x)
    alpha=(Q(p)+Q(q))/2; gamma=Q(m); beta=gamma-alpha
    assert np.allclose(beta,-np.einsum('ij,jk,ik->i',p-q,D,p-q)/4)
    H=lambda x:-np.sum(x*np.log(np.where(x>0,x,1)),axis=1)
    return {'alpha':alpha,'gamma':gamma,'beta':beta,'beta_share':np.divide(beta,gamma,out=np.full_like(beta,np.nan),where=gamma>1e-12),'jsd':H(m)-(H(p)+H(q))/2,'richness':((A+T)>0).sum(1),'richness_A':(A>0).sum(1),'richness_T':(T>0).sum(1)}

def regression(df,y):
    X=df[['FACTOR1','logeff','CAM.HEIGHT']].copy(); X=(X-X.mean())/X.std(ddof=0)
    dat=X.copy(); dat['y']=y; dat['group']=df.SurveyName; dat['site']=df.SITE
    dat=dat.dropna(); names=['FACTOR1','logeff','CAM.HEIGHT']
    def fit(dat):
        xx=dat[names]-dat.groupby('group')[names].transform('mean'); yy=dat.y-dat.groupby('group').y.transform('mean')
        if np.linalg.matrix_rank(xx)<3:return None
        return float(np.linalg.lstsq(xx,yy,rcond=None)[0][0])
    group_slopes=[]
    for name,g in dat.groupby('group'):
        if len(g)>=4 and g.FACTOR1.std()>0:
            group_slopes.append(float(np.polyfit(g.FACTOR1,g.y,1)[0]))
    loso=[fit(dat[dat.site!=s]) for s in sorted(dat.site.unique())]
    return {'n':len(dat),'sites':int(dat.site.nunique()),'groups':int(dat.group.nunique()),'mean':float(dat.y.mean()),'slope':fit(dat),'loso':loso,'unadjusted_group_slopes':group_slopes}

d['logeff']=np.log(eA/eT)
res={'audit':{'file_members':len(z.namelist()),'A_rows':len(a),'T_rows':len(t),'union':len(cols),'shared':len(shared),'traits_matched':int(sum(x in s.index for x in cols)),'mass_complete':int(known.sum()),'A_mass_complete':sum(x in set(np.array(cols)[known]) for x in a.columns),'T_mass_complete':sum(x in set(np.array(cols)[known]) for x in t.columns),'A_total':int(a.values.sum()),'T_total':int(t.values.sum()),'pairs':len(d),'sites':int(d.SITE.nunique()),'groups':int(d.SurveyName.nunique()),'paired_nonzero':int(((A.sum(1)>0)&(T.sum(1)>0)).sum()),'paired_effort12':int(((eA>=12)&(eT>=12)).sum())},'results':{}}
for threshold in [12,3]:
    use=(eA>=threshold)&(eT>=threshold)&(A.sum(1)>0)&(T.sum(1)>0)
    df=d.loc[use].reset_index(drop=True)
    for weight in ['count','incidence']:
        aa=A[use];tt=T[use]
        if weight=='incidence':aa=(aa>0).astype(float);tt=(tt>0).astype(float)
        q=metrics(aa,tt,D)
        covA=aa[:,known].sum(1)/aa.sum(1);covT=tt[:,known].sum(1)/tt.sum(1)
        complete=(covA>0)&(covT>0)
        mout=metrics(aa[complete][:,known],tt[complete][:,known],DM)
        rr={'species_identity':{k:regression(df,y) for k,y in q.items()},'mass_coverage':{'A':float(aa[:,known].sum()/aa.sum()),'T':float(tt[:,known].sum()/tt.sum()),'median_A':float(np.median(covA)),'median_T':float(np.median(covT)),'nonzero_pairs':int(complete.sum())},'restricted_mass':{k:regression(df.loc[complete].reset_index(drop=True),y) for k,y in mout.items() if k in ['alpha','gamma','beta','beta_share']}}
        # Post-outcome diagnostic: beta = within-layer concentration terms minus overlap.
        pp,qq=aa/aa.sum(1)[:,None],tt/tt.sum(1)[:,None]
        selfA=(pp**2).sum(1)/4;selfT=(qq**2).sum(1)/4;cross=-(pp*qq).sum(1)/2
        beta=selfA+selfT+cross
        assert np.allclose(beta,q['beta'])
        inter=((aa>0)&(tt>0)).sum(1);union=((aa+tt)>0).sum(1)
        rr['postoutcome_decomposition']={k:regression(df,v) for k,v in {'A_concentration_term':selfA,'T_concentration_term':selfT,'negative_cross_overlap_term':cross,'beta':beta,'shared_species':inter,'jaccard':inter/union}.items()}
        assert np.isclose(sum(rr['postoutcome_decomposition'][k]['slope'] for k in ['A_concentration_term','T_concentration_term','negative_cross_overlap_term']),rr['species_identity']['beta']['slope'])
        res['results'][f'{threshold}_{weight}']=rr
print(json.dumps(res,indent=2,default=lambda x:x.item()))
