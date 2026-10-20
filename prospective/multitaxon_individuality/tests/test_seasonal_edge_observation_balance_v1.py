"""Synthetic-only contracts for original-source effort-standardized X."""
from collections import Counter
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import seasonal_edge_observation_balance_v1 as mod
from cross_source_seasonal_x_v2 import Fix, describe, annual_day_balanced_centroids


def events(animals=('a','b'), k=2, *, far=False):
    out=[]
    for year in (2019,):
        for month in (1,2,6,7,12):
            for day in range(1,11):
                for animal in animals:
                    for i in range(k):
                        lon=0.0 if animal=='a' else (2 if far else .001)
                        out.append(Fix(animal,year,month,year*10000+month*100+day,
                                       .001+i*.0001,lon))
    return out


class TestEffortBalance(unittest.TestCase):
    def test_pair_mask_precedes_grid_and_matches_calendar_support(self):
        original=events()
        by=mod._group(original)
        centers=annual_day_balanced_centroids(original)
        pairs,days=mod._supported_pairs(original,by,2019,1,centers)
        self.assertEqual(len(pairs),1)
        pair=pairs[0]
        self.assertEqual(set(days[pair]),{1,2,6,7,12})
        self.assertEqual(len(days[pair][1]),10)
        missing=[x for x in original if x.month not in (2,7)]
        by2=mod._group(missing)
        pairs2,_=mod._supported_pairs(missing,by2,2019,1,
                                       annual_day_balanced_centroids(missing))
        self.assertEqual(pairs2,[])

    def test_two_fix_eligibility_is_explicit_not_missing_as_zero(self):
        original=events(k=1)
        by=mod._group(original)
        centers=annual_day_balanced_centroids(original)
        a,_=mod._supported_pairs(original,by,2019,1,centers)
        b,_=mod._supported_pairs(original,by,2019,2,centers)
        self.assertEqual(len(a),1)
        self.assertEqual(len(b),0)

    def test_centroid_filter_excludes_distant_pairs(self):
        original=events(far=True)
        pairs,_=mod._supported_pairs(original,mod._group(original),2019,1,
                                      annual_day_balanced_centroids(original))
        self.assertEqual(pairs,[])

    def test_no_replacement_and_permutation_invariance(self):
        items=[(.1,.1),(.2,.2),(.3,.3),(.4,.4)]
        a=mod._draw(items,2,'FIX',1,'a')
        self.assertEqual(a,mod._draw(list(reversed(items)),2,'FIX',1,'a'))
        self.assertEqual(len(set(a)),2)
        with self.assertRaises(ValueError):
            mod._draw(items,5,'FIX')

    def test_equal_day_and_month_displacement_overlap_bounds(self):
        original=events()
        by=mod._group(original)
        centers=annual_day_balanced_centroids(original)
        pairs,monthly=mod._supported_pairs(original,by,2019,1,centers)
        c=math.cos(math.radians(sum(e.lat for e in original)/len(original)))
        r=mod._compute_grid_seed(by,2019,pairs,monthly,1,3,(5.,0.,0.),c)
        self.assertEqual(r['n_pairs'],1)
        self.assertEqual((r['winter_mean_X'],r['summer_mean_X']),(1.,1.))
        self.assertEqual(r['both_edges'],1)
        self.assertEqual(r['jaccard_positive_edges'],1.)
        self.assertEqual(r['delta_incidence'],0.)
        self.assertEqual(r['delta_conditional_strength'],0.)

    def test_repeated_draws_are_reproducible_and_match_source_rows(self):
        original=events()
        by=mod._group(original)
        centers=annual_day_balanced_centroids(original)
        pairs,monthly=mod._supported_pairs(original,by,2019,2,centers)
        assert len(pairs)==1
        c=math.cos(math.radians(sum(e.lat for e in original)/len(original)))
        a=mod._compute_grid_seed(by,2019,pairs,monthly,2,11,(1.,.5,.5),c)
        b=mod._compute_grid_seed(by,2019,pairs,monthly,2,11,(1.,.5,.5),c)
        self.assertEqual(a,b)
        self.assertEqual(a['winter_mean_X'],1.)
        self.assertEqual(a['summer_mean_X'],1.)

    def test_undefined_conditional_strength_not_zero(self):
        rows=mod._summarize_draws([{'winter_mean_X':0.,'summer_mean_X':0.,
                                   'delta_mean_X':0.,'winter_edge_fraction':0.,
                                   'summer_edge_fraction':0.,'delta_incidence':None,
                                   'delta_conditional_strength':None,
                                   'jaccard_positive_edges':None}])
        self.assertIsNone(rows['delta_incidence']['mean'])
        self.assertIsNone(rows['delta_conditional_strength']['mean'])
        self.assertEqual(rows['delta_mean_X']['near_zero_seeds'],1)

    def test_core_decomposition_matches_synthetic_source_comparison(self):
        pair=('a','b')
        w={pair:.5};s={pair:.25}
        result=describe(w,s)
        self.assertAlmostEqual(result['incidence_component'],0)
        self.assertAlmostEqual(result['positive_strength_component'],.25)


if __name__=='__main__':
    unittest.main()
