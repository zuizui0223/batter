"""Native overlap for shifted 10m rasters, no mask interpolation.
Coordinate convention: x east, v=-y south; all origins in a shared projected CRS.
"""
import math
import numpy as np
STEP=10.0
TOL=1e-7
KEYS=("H50","H95","PPR","brw","power")
def partition(origins,base):
    e=[0.,STEP]
    for o in origins:
        q=(float(o)-base)%STEP
        if TOL<q<STEP-TOL:e.append(q)
    e.sort()
    merged=[e[0]]
    for v in e[1:]:
        if v-merged[-1]>TOL:merged.append(v)
    merged[-1]=STEP
    assert len(merged)>=2 and abs(sum(np.diff(merged))-STEP)<TOL
    return merged
def integrate(layers,base_x,base_v,shape):
    """layers[k]=(array,valid,inside,x_origin,v_origin), where origins are
    for the actual bounded array, not rounded to the reference grid.
    Return joint fraction, metric numerators, and nonphysical area diagnostics.
    """
    assert set(layers)==set(KEYS)
    h,w=shape
    for k,(a,m,i,x,v) in layers.items():
        assert a.shape==m.shape==i.shape and a.ndim==2
        assert not np.any(m&~i)
        if k in ("brw","power"):
            if np.any(m&~np.isin(a,[0,1])):raise ValueError("unexpected mask codes "+k)
    xx=partition([a[3] for a in layers.values()],base_x)
    vv=partition([a[4] for a in layers.values()],base_v)
    den=np.zeros(shape,dtype=np.float64)
    nums=np.zeros((3,h,w),dtype=np.float64)
    invalid=0.;total=0.
    for v0,v1 in zip(vv[:-1],vv[1:]):
        for x0,x1 in zip(xx[:-1],xx[1:]):
            wt=(v1-v0)*(x1-x0)/(STEP*STEP);total+=wt
            # Midpoint lies within a single native pixel for every source.
            x=base_x+STEP*np.arange(w)+(x0+x1)/2
            v=base_v+STEP*np.arange(h)+(v0+v1)/2
            picked={}
            for k,(a,m,i,ox,ov) in layers.items():
                c=np.floor((x-ox)/STEP).astype(np.int64)
                r=np.floor((v-ov)/STEP).astype(np.int64)
                if c.min()<0 or r.min()<0 or c.max()>=a.shape[1] or r.max()>=a.shape[0]:
                    raise ValueError("insufficient native window padding "+k)
                p=np.ix_(r,c)
                picked[k]=(a[p],m[p],i[p])
            a,ma,_=picked["H50"];b,mb,_=picked["H95"];p,mp,_=picked["PPR"]
            br,brm,_=picked["brw"];pw,pwm,pwi=picked["power"]
            physical=ma&mb&mp
            order=(a>=0)&(b>=a)&(b<=150)&(p>=0)&(p<=1)
            invalid+=wt*int((physical&~order).sum())
            valid=physical&order&brm&(br==0)&pwi&~(pwm&(pw==1))
            den+=wt*valid
            for j,z in enumerate((a,b,p)):
                nums[j]+=wt*np.where(valid,z,0.)
    assert abs(total-1)<1e-9 and np.all(den>=-TOL) and np.all(den<=1+TOL)
    assert np.all(np.isfinite(nums))
    return den,nums,{"x_intervals":len(xx)-1,"y_intervals":len(vv)-1,"invalid_equivalent_10m_pixels":float(invalid)}
def synthetic_checks():
    # Reference grid spans [0,10] x [0,10] in one reference pixel.
    # Arrays have padding, origins are genuine projected coordinates.
    def layer(value,ox=-10.,ov=-10.):
        a=np.full((5,5),float(value));m=np.ones(a.shape,bool);i=m.copy()
        return a,m,i,ox,ov
    def base():
        return {"H50":layer(6),"H95":layer(12),"PPR":layer(.3),"brw":layer(0),"power":layer(0)}
    def evaluate(d):return integrate(d,0.,0.,(1,1))
    a=base();den,num,info=evaluate(a)
    assert np.allclose(den,1) and np.allclose(num[:,0,0],[6,12,.3])
    # Boundary x=5 in mask: first half is excluded, second half allowed.
    a=base();br=layer(0,-15,-10);br[0][:,:2]=1;a["brw"]=br
    den,num,info=evaluate(a);assert np.allclose(den,.5) and np.allclose(num[:,0,0],[3,6,.15])
    # Fractional offset x=2.5: first 2.5m excluded.
    a=base();br=layer(0,-17.5,-10);br[0][:,:2]=1;a["brw"]=br
    den,num,info=evaluate(a);assert np.allclose(den,.75)
    # Orthogonal shifted sparse power mask excludes lower 40% in y;
    # use inside extent explicitly, NoData inside means no mapped line.
    pw=layer(0,-10,-16);pw[1][:]=False;pw[0][2,:]=1;pw[1][2,:]=True
    a["power"]=pw
    den,num,info=evaluate(a);assert np.allclose(den,.75*.4)
    # Metric missing for right half, and valid zero in PPR is retained.
    a=base();h50=layer(6,-15,-10);h50[1][:,2:]=False;a["H50"]=h50;a["PPR"]=layer(0)
    den,num,info=evaluate(a);assert np.allclose(den,.5) and np.allclose(num[:,0,0],[3,6,0])
    # Outside sparse mask extent is NOT treated as clear.
    a=base();pw=layer(0,-15,-10);pw[1][:]=False;pw[2][:,2:]=False;a["power"]=pw
    den,num,info=evaluate(a);assert np.allclose(den,.5)
    # Shifted numeric source boundaries: 6m and 10m occupy half each.
    a=base();h50=layer(6,-15,-10);h50[0][:,2:]=10;a["H50"]=h50
    den,num,info=evaluate(a);assert np.allclose(den,1) and np.allclose(num[:,0,0],[8,12,.3])
    return {"aligned":True,"half_pixel":True,"fractional_shift":True,"joint_shifted_masks":True,"missing_metric":True,"sparse_mask_footprint":True,"weighted_numeric_conservation":True}
if __name__=="__main__":
    import json
    print("AHN_OVERLAP_SYNTHETIC="+json.dumps(synthetic_checks()),flush=True)
