#!/usr/bin/env python3
"""Synthetic-only noncoupling proof: conditional movement identity ≠ niche segregation.

This is a *logical methods control*, not any analyzed Movebank animal data.
Shows why identity predictive gain and a DIFFERENT held-out ecological endpoint
must be measured, rather than treating one nested 3D overlap as a second test.
"""
from __future__ import annotations

import math


def overlap(a:tuple[float,...],b:tuple[float,...])->float:
    assert len(a)==len(b) and abs(sum(a)-1)<1e-10 and abs(sum(b)-1)<1e-10
    assert all(x>=0 for x in a+b)
    return sum(min(x,y) for x,y in zip(a,b))


def expect_log_gain(individual:tuple[float,...],
                    pop:tuple[float,...])->float:
    """Expected held-out log probability gain in nats/fix under known toy law."""
    assert len(individual)==len(pop)
    return sum(p*math.log(p/q) for p,q in zip(individual,pop) if p>0)


def test_two_constructs()->None:
    population=(.5,.5)

    # Toy A: animals choose opposite step directions in exactly the same
    # two environmental patches/space-use distributions. This is individual
    # behavioral predictability without resource/area differentiation.
    movement_A=(.8,.2);movement_B=(.2,.8)
    habitat_A=(.5,.5);habitat_B=(.5,.5)
    G_A=expect_log_gain(movement_A,population)
    G_B=expect_log_gain(movement_B,population)
    space_overlap=overlap(habitat_A,habitat_B)
    assert math.isclose(G_A,G_B,abs_tol=1e-12)
    assert .19<G_A<.20
    assert math.isclose(space_overlap,1.,abs_tol=1e-12)
    print(f"SYNTHETIC example A: conditional identity G={G_A:.6f} nats per independent toy step; habitat overlap={space_overlap:.3f}")

    # Toy B: every animal has the SAME movement-decision distribution given
    # hypothetical context, but its marginal patch allocation is different.
    # Predictive conditional movement individuality is zero even when spatial
    # use is differentiated. Independent availability is not modeled here.
    movement_A2=population;movement_B2=population
    habitat_A2=(.9,.1);habitat_B2=(.1,.9)
    G2=max(expect_log_gain(movement_A2,population),
           expect_log_gain(movement_B2,population))
    spatial_overlap2=overlap(habitat_A2,habitat_B2)
    assert math.isclose(G2,0.,abs_tol=1e-12)
    assert math.isclose(spatial_overlap2,.2,abs_tol=1e-12)
    print(f"SYNTHETIC example B: conditional identity G={G2:.6f}; descriptive spatial overlap={spatial_overlap2:.3f}")

    assert G_A>G2 and space_overlap>spatial_overlap2
    print("PASS conditional identity and observed spatial allocation are logically distinct objects")
    print("NOT REAL DATA. Spatial-overlap values do not alone prove niche/resource/competition partitioning.")
    print("A real co-use or resource endpoint requires independent source context, common availability, temporal opportunity and biological-unit nulls.")


if __name__=="__main__":
    test_two_constructs()
