"""Synthetic sensitivity study; current scores are not utilization probabilities."""
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from scipy.ndimage import gaussian_filter
from itertools import combinations
import csv
from pathlib import Path


def solve(n, u, v, c, source, sink):
    assert source != sink and np.all(c > 0)
    L = sparse.coo_matrix((np.r_[c,c,-c,-c],
                           (np.r_[u,v,u,v],np.r_[u,v,v,u])),shape=(n,n)).tocsr()
    b = np.zeros(n); b[source]=1; b[sink]=-1
    keep = np.arange(n)!=sink
    phi=np.zeros(n); phi[keep]=spsolve(L[keep][:,keep],b[keep])
    I=c*(phi[u]-phi[v]); R=phi[source]-phi[sink]
    err=max(np.max(np.abs(L@phi-b)),abs(np.sum(I**2/c)-R))
    assert np.isfinite(err) and err < 1e-9
    score=np.bincount(np.r_[u,v],weights=np.r_[abs(I),abs(I)],minlength=n)
    return score/score.sum(),R,err


def tests():
    u=np.array([0,1]);v=np.array([1,2]);c=np.array([.5,1/3])
    p,r,e=solve(3,u,v,c,0,2); assert np.isclose(r,5)
    p2,r2,_=solve(3,u,v,c,2,0); assert np.allclose(p,p2) and np.isclose(r,r2)
    p3,r3,_=solve(3,u,v,7*c,0,2); assert np.allclose(p,p3) and np.isclose(r3,r/7)
    u=np.array([0,1,0,2]);v=np.array([1,3,2,3]);c=np.ones(4)
    p,r,e=solve(4,u,v,c,0,3); assert np.isclose(r,1) and np.allclose(p,.25)


def graph(h,nz):
    nx,ny=h.shape
    z=np.arange(nz)[None,None,:]+.5
    agl=z-h[:,:,None]; valid=agl>0
    ids=np.full(valid.shape,-1,int);ids[valid]=np.arange(valid.sum())
    uu=[];vv=[]
    for k in range(3):
        a=[slice(None)]*3;b=a.copy();a[k]=slice(None,-1);b[k]=slice(1,None)
        i=ids[tuple(a)];j=ids[tuple(b)];ok=(i>=0)&(j>=0)
        uu.append(i[ok]);vv.append(j[ok])
    u=np.concatenate(uu);v=np.concatenate(vv)
    feature=(agl[valid][u]+agl[valid][v])/(2*nz)-.5
    return ids,u,v,feature


def terrain(seed, amplitude, nx=20, ny=20):
    # Identical elevation histogram, fixed endpoint bands. Rearrange spatial ranks only.
    rng=np.random.default_rng(seed);x,y=np.mgrid[0:nx-4,0:ny]
    vals=np.sort(np.floor(amplitude*np.exp(-((x-(nx-5)/2)/2.6)**2)).astype(int).ravel())
    fields={"transverse_ridge":-abs(x-(nx-5)/2)+1e-5*y,
            "longitudinal_ridge":-abs(y-(ny-1)/2)+1e-5*x,
            "gapped_ridge":-abs(x-(nx-5)/2)-5*np.exp(-((y-(ny-1)/2)/2.5)**2),
            "patchy":gaussian_filter(rng.normal(size=x.shape),2,mode='reflect')}
    result={}
    for name,field in fields.items():
        h=np.zeros((nx,ny),int);q=np.empty(x.size,int);q[np.argsort(field.ravel(),kind='stable')]=vals
        h[2:-2,:]=q.reshape(x.shape);result[name]=h
    assert len({tuple(np.bincount(h.ravel(),minlength=amplitude+1)) for h in result.values()})==1
    return result


def metrics(p):
    overlap=[np.minimum(p[i],p[j]).sum() for i,j in combinations(range(3),2)]
    q=2/9*np.dot([.5,1,.5],1-np.array(overlap));return q,overlap


def run():
    tests(); rows=[];nz=12; source=(1,10,2)
    # Fixed design: 3 amplitudes x 4 spatial arrangements x 3 endpoints x 3 trait contrasts.
    # Patchy terrain uses four independent seeds, other geometries are deterministic.
    for amp in (3,6,9):
        for seed in range(4):
            for name,h in terrain(seed,amp).items():
                if name!='patchy' and seed!=0: continue
                ids,u,v,feature=graph(h,nz);n=int((ids>=0).sum());s=ids[source]
                for target,sink in [('low_central',(18,10,2)),('low_offset',(18,3,2)),('high_central',(18,10,8))]:
                    t=ids[sink]; assert s>=0 and t>=0
                    for strength in (1.,3.,6.):
                        sol=[solve(n,u,v,np.exp(-beta*feature),s,t) for beta in (-strength,0.,strength)]
                        q,o=metrics([a[0] for a in sol])
                        rows.append(dict(amplitude=amp,seed=seed,terrain=name,target=target,strength=strength,
                            volume=n,qspace=q,rao_q=4/9,overlap_extreme=o[1],
                            resistance_low=sol[0][1],resistance_mid=sol[1][1],resistance_high=sol[2][1],
                            max_error=max(a[2] for a in sol)))
    out=Path(__file__).with_name('roost_connectivity_sensitivity_v2.csv')
    with out.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(f'{len(rows)} scenarios, {len(rows)*3} solves; max residual {max(r["max_error"] for r in rows):.3g}')


if __name__=='__main__':run()
