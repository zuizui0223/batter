"""V9: frozen archive-conditional diversity prediction. Aggregate outputs only."""
import collections as C
import datetime as dt
import json,math
from pathlib import Path
import numpy as np
from pyproj import Transformer
from safe_v8c_audit import loadgaz,loadbook,locations,resolve,norm,dateparse,timeparse

LABELS=tuple(sorted(['fm','qcf']+['fmqcf'+str(i) for i in range(1,7)]+['cf_'+x for x in ['crob','hcer','hdia','hgal','hrid','racu','raff','rbor','rcre','rluc','rphi','rsed','rtri']]))
TYPES=('fm','cf','fmqcf','qcf')
HAB=('old-growth forest','logged forest','heavily logged forest')
M=np.array([[int((('cf' if k.startswith('cf_') else 'fmqcf' if k.startswith('fmqcf') else k)==g)) for g in TYPES] for k in LABELS])
assert len(LABELS)==21 and np.all(M.sum(1)==1)
A=1-float(np.sum(M.sum(0)*(M.sum(0)-1)))/(21*20)
ORDER=['calltype_Q','phonic_Q','within_type_component','calltype_excess','composition_MSE']
MODELS=['N','F','B','S','Q']

def response(p):
    assert np.all(p>=0) and abs(p.sum()-1)<1e-10
    g=p@M;q=1-g@g;r=1-p@p
    w=r-q;e=q-A*r
    assert w>=-1e-10
    check=0.
    for k in range(4):
        a=p[M[:,k]==1];check+=a.sum()**2-a@a
    assert abs(w-check)<1e-10
    return np.r_[q,r,w,e,g]

def project(v):
    u=np.sort(v)[::-1];css=np.cumsum(u)-1
    k=np.flatnonzero(u-css/np.arange(1,len(v)+1)>0)[-1]
    p=np.maximum(v-css[k]/(k+1),0)
    assert abs(p.sum()-1)<1e-10 and np.all(p>=0)
    return p

def prediction(x,y,xt,model):
    # Columns: 3 habitat indicators, log observed nights, extent,height,TRI,shape.
    if model=='N':
        pred=np.repeat(y.mean(0)[None,:],len(xt),axis=0)
        return pred,None
    n={'F':4,'B':7,'S':8,'Q':8}[model]
    x=x[:,:n];xt=xt[:,:n]
    mu=x.mean(0);sd=x.std(0);active=sd>1e-12
    sd[:3]=1.;sd[~active]=1.
    z=(x-mu)/sd;zt=(xt-mu)/sd
    z[:,~active]=0.;zt[:,~active]=0.
    qscale=None
    if model=='Q':
        sq=z[:,7]**2;sqt=zt[:,7]**2;qm=sq.mean();qs=sq.std()
        qscale=qs if qs>1e-12 else 1.
        z=np.column_stack([z,(sq-qm)/qscale if qs>1e-12 else np.zeros(len(z))])
        zt=np.column_stack([zt,(sqt-qm)/qscale if qs>1e-12 else np.zeros(len(zt))])
    Z=np.c_[np.ones(len(z)),z];ZT=np.c_[np.ones(len(zt)),zt]
    ridge=np.eye(Z.shape[1]);ridge[0,0]=0
    coef=np.linalg.solve(Z.T@Z+ridge,Z.T@y)
    # independent augmented least-squares check
    L=np.diag(np.sqrt(np.diag(ridge)))
    ref=np.linalg.lstsq(np.vstack([Z,L]),np.vstack([y,np.zeros((len(L),y.shape[1]))]),rcond=None)[0]
    assert np.max(np.abs(ZT@(coef-ref)))<1e-9
    assert np.all(np.isfinite(coef))
    info=None
    if model=='Q' and active[7]:
        q=coef[-1]/qscale;lin=coef[-2]
        tp=np.divide(-lin,2*q,out=np.full_like(q,np.nan),where=np.abs(q)>1e-12)*sd[7]+mu[7]
        info={'raw_quadratic':(q/sd[7]**2).tolist(),'turning_point':[float(t) if np.isfinite(t) else None for t in tp]}
    return ZT@coef,info

def loss(pred,y):
    z=pred.copy()
    z[:,0]=np.clip(z[:,0],0,.75)
    z[:,1]=np.clip(z[:,1],0,20/21)
    z[:,4:]=np.array([project(a) for a in z[:,4:]])
    e=(z-y)**2;raw=(pred-y)**2
    return np.r_[e[:,:4].mean(0),e[:,4:].mean()],raw[:,:4].mean(0)

def evaluate(pairs,mode,grain):
    n=len(pairs);x=np.array([[int(p['hab']==h) for h in HAB]+[math.log(p['nights']),p['s'][0],p['s'][1],p['s'][3],p['s'][2]] for p in pairs],float)
    y=np.array([response(p[mode]) for p in pairs])
    blocks=C.defaultdict(list)
    for i,p in enumerate(pairs):blocks[tuple(math.floor(v/grain) for v in p['utm'])].append(i)
    ret={'n':n,'blocks':len(blocks),'block_sizes':sorted(map(len,blocks.values()))}
    if n!=33 or len(blocks)<5:return {**ret,'status':'insufficient_support'}
    unknown=0
    for ii in blocks.values():
        tr=np.ones(n,bool);tr[ii]=False
        if tr.sum()<20 or len({pairs[j]['hab'] for j in np.flatnonzero(tr)})<2:return {**ret,'status':'insufficient_training_support'}
        train={pairs[j]['hab'] for j in np.flatnonzero(tr)}
        unknown+=sum(pairs[j]['hab'] not in train for j in ii)
    lossrows={m:[] for m in MODELS};rawrows={m:[] for m in MODELS}
    for _,ii in sorted(blocks.items()):
        tr=np.ones(n,bool);tr[ii]=False
        for m in MODELS:
            pred,_=prediction(x[tr],y[tr],x[ii],m)
            v,raw=loss(pred,y[ii]);lossrows[m].append(v);rawrows[m].append(raw)
    ret['mse']={m:np.mean(v,axis=0).tolist() for m,v in lossrows.items()}
    ret['unclipped_scalar_mse']={m:np.mean(v,axis=0).tolist() for m,v in rawrows.items()}
    gains={}
    for a,b in [('F','N'),('B','F'),('S','B'),('S','N'),('Q','S'),('Q','N')]:
        d=np.asarray(lossrows[b])-np.asarray(lossrows[a]);om=(d.sum(0)-d)/(len(d)-1)
        gains[a+'-'+b]={'mean':d.mean(0).tolist(),'positive_blocks':(d>0).sum(0).tolist(),'leave_block_mean_range':[om.min(0).tolist(),om.max(0).tolist()]}
    ret['gains']=gains
    ret['heldout_absent_class_sites']=unknown
    ret['outcome_range']=[y.min(0).tolist(),y.max(0).tolist()]
    _,ret['full_quadratic']=prediction(x,y,x,'Q')
    ret['shape_central_10_90']=np.quantile(x[:,7],[.1,.9]).tolist()
    ret['status']='scored'
    return ret

def main():
    out={'metric_order':ORDER,'fixed_reference_coefficient':A,'calltype_order':TYPES,'calltype_label_counts':M.sum(0).tolist()}
    try:
        assert np.allclose(project(np.array([.1,.2,.3,.4])),[.1,.2,.3,.4])
        assert np.allclose(project(np.array([-1.,0.,2.,0.])),[0.,0.,1.,0.])
        assert np.allclose(response(np.ones(21)/21)[3],0)
        geo,types,regions,aliases,receipt=loadgaz();out['gazetteer']=receipt
        w,rc=loadbook(7740421,'SAFE_data_archive_Yoh2.xlsx','0c874b45b265d326c9cff12db30f96fa6cbf5f19cbfe24530a64bc72fcf25da2')
        out['source']=rc
        loc,ls=locations(w)
        sh=w['MasterData'];head=next(sh.iter_rows(min_row=10,max_row=10,values_only=True))
        assert [norm(a) for a in head[1:14]]==['location','date','time','auto_id','accuracy','threslevel','manual_id_clean','final_id','treatment','fc_100m','chm_100m','shape_100m','tri_100m']
        author={norm(r[0]) for r in w['Taxa'].iter_rows(min_row=2,values_only=True) if r[0] is not None}
        assert set(LABELS)<=author
        labels={v:i for i,v in enumerate(LABELS)}
        sites=C.defaultdict(C.Counter);night=C.defaultdict(lambda:C.defaultdict(C.Counter))
        window=C.defaultdict(C.Counter);struct=C.defaultdict(set);hab=C.defaultdict(set);rows=0;alllabels=C.Counter()
        for r in sh.iter_rows(min_row=11,values_only=True):
            if all(v is None for v in r):continue
            rows+=1;site=norm(r[1]);lab=norm(r[8]);da=dateparse(r[2]);ti=timeparse(r[3])
            assert site and lab in labels and da and ti
            allLabelsKey=labels[lab];alllabels[lab]+=1
            sites[site][allLabelsKey]+=1
            night[site][da-dt.timedelta(days=int(ti.hour<12))][allLabelsKey]+=1
            sec=ti.hour*3600+ti.minute*60+ti.second+ti.microsecond/1e6
            if sec>=65700 or sec<=22500:window[site][allLabelsKey]+=1
            hab[site].add(norm(r[9]))
            vals=[]
            for v in r[10:14]:
                try:
                    x=float(v);vals.append(x if math.isfinite(x) else None)
                except (ValueError,TypeError):vals.append(None)
            struct[site].add(tuple(vals))
        w.close()
        assert rows==134920 and len(sites)==45 and set(alllabels)==set(LABELS)
        assert sum(sum(c.values()) for c in window.values())==134207
        def vec(c):return np.array([c.get(i,0) for i in range(21)],float)
        def prob(v):
            assert v.sum()>0
            return v/v.sum()
        trans=Transformer.from_crs(4326,32650,always_xy=True)
        pairs=[];res=C.Counter();nh=C.Counter();rowsused=0;modecheck=True
        for site in sorted(sites):
            assert len(hab[site])==1
            h=next(iter(hab[site]));k,xy=resolve([site],7740421,loc,geo,types,aliases)
            res[k]+=1
            if xy is None or len(struct[site])!=1 or None in next(iter(struct[site])):continue
            assert h in HAB
            s=next(iter(struct[site]));counts=vec(sites[site]);pn=np.mean([prob(vec(c)) for c in night[site].values()],axis=0)
            pw=vec(window[site]);assert pw.sum()>0
            pairs.append({'hab':h,'s':s,'utm':trans.transform(*xy),'nights':len(night[site]),'count':prob(counts),'night_equal':pn,'incidence':prob((counts>0).astype(float)),'clock_window':prob(pw)})
            nh[h]+=1;rowsused+=int(counts.sum())
        assert res==C.Counter({'official_exact':41,'direct':1,'no_admitted_point':3})
        assert len(pairs)==33 and nh==C.Counter({'old-growth forest':4,'logged forest':7,'heavily logged forest':22})
        structmat=np.array([p['s'] for p in pairs])
        names=['extent','height','shape','TRI']
        out['support']={'archive_rows':rows,'archived_sites':45,'matched_sites':33,'forests':dict(nh),'matched_record_rows':rowsused,'location_resolution':dict(res),'window_rows':134207,'archive_calltype_counts':{g:int(sum(alllabels[k] for i,k in enumerate(LABELS) if M[i,j])) for j,g in enumerate(TYPES)},'observed_nights':dict(C.Counter(p['nights'] for p in pairs)),'covariate_correlation':np.corrcoef(structmat,rowvar=False).tolist(),'structure_range_by_forest':{h:{k:[float(np.min(structmat[[p['hab']==h for p in pairs],i])),float(np.max(structmat[[p['hab']==h for p in pairs],i]))] for i,k in enumerate(names)} for h in HAB}}
        out['tests']={f'{m}_{g}':evaluate(pairs,m,g) for m in ['count','night_equal','incidence','clock_window'] for g in [1000,2000]}
        t=out['tests']
        primary=all(t[f'count_{g}']['status']=='scored' and t[f'count_{g}']['gains']['S-B']['mean'][0]>0 and t[f'count_{g}']['gains']['S-B']['positive_blocks'][0]/t[f'count_{g}']['blocks']>=.6 and t[f'count_{g}']['gains']['S-N']['mean'][0]>0 for g in [1000,2000])
        sensitivity=all(t[f'{m}_{g}']['status']=='scored' and t[f'{m}_{g}']['gains']['S-B']['mean'][0]>0 for m in ['night_equal','incidence'] for g in [1000,2000])
        out['primary_screen']={'count':primary,'sensitivity':sensitivity,'pass':primary and sensitivity}
        out['descriptive_by_forest']={h:{m:np.mean([response(p[m]) for p in pairs if p['hab']==h],axis=0).tolist() for m in ['count','night_equal','incidence']} for h in HAB}
        out['status']='completed' if any(v['status']=='scored' for v in t.values()) else 'nonadmitted_support'
    except Exception as e:
        out.update(status='stopped',error=type(e).__name__+': '+str(e)[:180])
    Path('yoh_v9_calltype_structure.json').write_text(json.dumps(out,indent=2,allow_nan=False));print(json.dumps(out,allow_nan=False))
if __name__=='__main__':main()
