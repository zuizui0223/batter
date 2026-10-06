#!/usr/bin/env python3
"""Compatibility shim for the superseded acoustic primary implementation.

Authoritative numeric implementation:
    run_acoustic_policy_primary_v1.py

This file remains only because an older workflow/self-test references it.
It MUST delegate the numerical primary to the authoritative implementation.
"""

from __future__ import annotations

import numpy as np

import run_acoustic_policy_primary_v1 as P

BATS=P.BATS


def stat(c, saline_mapping):
    """Compatibility form of the frozen exact identity statistic."""
    mapping=tuple(saline_mapping[b] for b in BATS)
    kval,vals=P.statistic(c,mapping)
    saline={bat:c[(bat,1)] for bat in BATS}
    out={}
    for i,ligbat in enumerate(BATS):
        assigned=mapping[i]
        target=c[(ligbat,2)]
        dself=float(np.linalg.norm(target-saline[assigned]))
        others=[saline[mapping[j]] for j in range(len(BATS)) if j!=i]
        dother=float(np.mean([np.linalg.norm(target-x) for x in others]))
        out[ligbat]={
            "assigned_saline_bat":assigned,
            "self_distance":dself,
            "other_distance":dother,
            "K_i":dother-dself,
        }
    return kval,out


def main():
    P.main()


if __name__=="__main__":
    main()
