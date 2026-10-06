#!/usr/bin/env python3
"""Synthetic self-test for the frozen 4-bat exact identity statistic."""

import importlib.util
import itertools
import pathlib
import numpy as np

HERE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"acoustic_policy_primary_v1.py")
P=importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)

def main():
    # Four clearly distinct Saline centroids; Ligand preserves identity exactly.
    c={}
    saline={
        "jane":np.array([-3.,0.,0.,0.]),
        "bea":np.array([-1.,2.,0.,0.]),
        "jason":np.array([1.,0.,2.,0.]),
        "stella":np.array([3.,0.,0.,2.]),
    }
    for b,v in saline.items():
        c[(b,1)]=v
        c[(b,2)]=v.copy()

    observed={b:b for b in P.BATS}
    kobs,ind=P.stat(c,observed)
    assert kobs > 0
    assert all(v["K_i"] > 0 for v in ind.values())

    null=[]
    for perm in itertools.permutations(P.BATS):
        mapping={lig:sal for lig,sal in zip(P.BATS,perm)}
        k,_=P.stat(c,mapping)
        null.append(k)

    extreme=sum(x >= kobs-1e-15 for x in null)
    assert len(null)==24
    assert extreme==1, (kobs,extreme,sorted(null,reverse=True)[:5])
    assert abs(extreme/24 - 1/24) < 1e-15

    # Null sanity: all centroids identical => every mapping ties, p=1.
    z=np.zeros(4)
    c0={}
    for b in P.BATS:
        c0[(b,1)]=z.copy()
        c0[(b,2)]=z.copy()
    k0,_=P.stat(c0,observed)
    null0=[]
    for perm in itertools.permutations(P.BATS):
        mapping={lig:sal for lig,sal in zip(P.BATS,perm)}
        x,_=P.stat(c0,mapping)
        null0.append(x)
    assert k0==0
    assert sum(x >= k0-1e-15 for x in null0)==24

    print("PASS acoustic-policy exact identity self-test")
    print("permutations=24")
    print("minimum exact p=1/24")

if __name__=="__main__":
    main()
