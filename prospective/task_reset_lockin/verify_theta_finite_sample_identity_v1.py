#!/usr/bin/env python3
"""Independent algebra check of all-subsets theta averaging.
No bat observations or external dependencies: this theorem is purely combinatorial.
"""
import itertools
import json
from math import comb

def direct(y,x,m):
    subs=itertools.combinations(x,m)
    return sum((y-sum(s)/m)**2 for s in subs)/comb(len(x),m)

def theorem(y,x,m):
    n=len(x)
    avg=sum(x)/n
    v=sum((z-avg)**2 for z in x)/n
    return (y-avg)**2+v*(n-m)/(m*(n-1))

def fraction(n,m):
    return n*(m-1)/(m*(n-1))

def main():
    checks=0
    for x in [
        [0.1, 7, -5],
        [1.2,2.7,10,-0.8],
        [-9,12,5,3,40],
        [1, 1, 1, 1, 1, 1],
        [-100,100,-75,75,50],
    ]:
        for y in [-10000, -1.7, 0, 17.3, 5000]:
            n=len(x)
            for m in range(1,n+1):
                a=direct(y,x,m);b=theorem(y,x,m)
                assert abs(a-b)<1e-7*max(1,abs(a),abs(b)), (x,y,m,a,b)
                checks+=1
            if len(set(x))>1:
                full=direct(y,x,n)
                mse1=direct(y,x,1)
                for m in range(1,n+1):
                    observed=1-(direct(y,x,m)-full)/(mse1-full)
                    expected=fraction(n,m)
                    assert abs(observed-expected)<1e-7, (observed,expected)
                    checks+=1
    expected={"A":(4,8/9),"B":(3,1),"C":(4,8/9),"D":(5,5/6),"E":(4,8/9)}
    for b,(n,want) in expected.items():
        assert abs(fraction(n,3)-want)<1e-12,b
        checks+=1
    print(json.dumps({
        "status":"PASS",
        "number_of_checks":checks,
        "identity":"all-subset MSE equals full-mean MSE plus finite-population subset sampling variance",
        "theta_recovery_fraction_is_structurally_determined":True,
        "ratios_at_m3":{b:fraction(n,3) for b,(n,_) in expected.items()}
    },sort_keys=True))

if __name__=="__main__":
    main()
