"""Synthetic native-timestamp geodesic matching and exact proximity null tests."""
from datetime import datetime
from itertools import combinations
from pathlib import Path
import math
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import subhour_geodesic_proximity_v1 as x


def fix(t,km=0):
    return (float(t),0.,float(km)/111.32)


def invented(animals=('a','b','c'),days=range(1,9),months=(1,2,6,7),gap=0):
    by={}
    for month in months:
        for day in days:
            ordinal=datetime(2019,month,day).toordinal()
            for animal in animals:
                time_shift=gap if animal!='a' else 0
                by[(2019,month,animal,ordinal)]=tuple(
                    fix(3600+time_shift+i*7200,km=i*3) for i in range(3))
    return by


class TestSubhourGeodesic(unittest.TestCase):
    def test_real_original_fix_pairs_are_one_to_one(self):
        a=(fix(0),fix(600),fix(1200))
        b=(fix(450),fix(1000),fix(2000))
        r=x.one_to_one_time_pairs(a,b,600)
        self.assertEqual(len(r),2)
        self.assertEqual(len({pair[0][0] for pair in r}),2)
        self.assertEqual(len({pair[1][0] for pair in r}),2)
        self.assertEqual(x.one_to_one_time_pairs(a,b,1800)[-1][0][0],1200)

    def test_strict_15min_v_30min_opportunity(self):
        base={('a','b'),('a','c'),('b','c')}
        by=invented(gap=1500)
        small=x._derive_opportunity(by,base,2019,900)
        big=x._derive_opportunity(by,base,2019,1800)
        self.assertEqual(set(small),{('b','c')})
        self.assertEqual(set(big),base)

    def test_selected_dates_months_and_exact_fix_count(self):
        by=invented()
        support=x._derive_opportunity(by,{('a','b'),('b','c'),('a','c')},2019,900)
        self.assertEqual(len(support),3)
        out=x._one_seed(support,'turkey',2019,900,4)
        self.assertEqual(len(out),3)
        for r in out:
            self.assertEqual(r['n_matched_dyads'],3)
            self.assertEqual(r['n_selected_dyad_dates'],84)
            self.assertEqual(r['n_selected_direct_fix_pairs'],252)
            self.assertEqual(r['winter_mean_abs_recording_gap_seconds'],0)

    def test_missing_three_fix_day_and_second_season_are_stop(self):
        by=invented()
        sparse={k:v[:2] for k,v in by.items()}
        self.assertFalse(x._derive_opportunity(sparse,{('a','b')},2019,1800))
        partial={k:v for k,v in by.items() if k[1] in (1,6,7)}
        self.assertFalse(x._derive_opportunity(partial,{('a','b')},2019,1800))
        less={k:v for k,v in by.items() if k[3]!=datetime(2019,k[1],7).toordinal()
              and k[3]!=datetime(2019,k[1],8).toordinal()}
        self.assertFalse(x._derive_opportunity(less,{('a','b')},2019,1800))

    def test_aligned_positions_exceed_exact_location_permutation(self):
        pairs=tuple((fix(0,i*3),fix(0,i*3)) for i in range(3))
        r,dt=x.daily_nearby_statistics(pairs)
        self.assertEqual(dt,0)
        self.assertEqual(r[1.]['O'],1.)
        self.assertAlmostEqual(r[1.]['N'],1/3)
        self.assertAlmostEqual(r[1.]['D'],2/3)

    def test_misaligned_partner_has_negative_relative_time_coincidence(self):
        pairs=tuple((fix(0,i*3),fix(0,((i+1)%3)*3)) for i in range(3))
        r,_=x.daily_nearby_statistics(pairs)
        self.assertEqual(r[1.]['O'],0)
        self.assertAlmostEqual(r[1.]['N'],1/3)
        self.assertAlmostEqual(r[1.]['D'],-1/3)

    def test_stationary_animals_do_not_create_artificial_positive_D(self):
        pairs=tuple((fix(i*7200,0),fix(i*7200,0)) for i in range(3))
        r,_=x.daily_nearby_statistics(pairs)
        self.assertEqual(r[1.],{'O':1.,'N':1.,'D':0.})

    def test_far_apart_source_geographic_positions_not_misclassified_as_encounter(self):
        pairs=tuple((fix(i*7200,0),fix(i*7200,30)) for i in range(3))
        r,_=x.daily_nearby_statistics(pairs)
        for radius in x.RADII_KM:
            self.assertEqual(r[radius],{'O':0.,'N':0.,'D':0.})

    def test_seed_select_reproducible_source_order_independent(self):
        data=[(fix(t,1),fix(t,3)) for t in range(10)]
        a=x._select(data,3,'a',2019,'day',5)
        b=x._select(list(reversed(data)),3,'a',2019,'day',5)
        self.assertEqual(a,b)
        self.assertEqual(len(set(a)),3)
        with self.assertRaises(AssertionError):
            x._select(data,11,'too-many')

    def test_metric_probabilities_geodesic_sensitivity_monotone(self):
        a=fix(100,0)
        b=fix(100,.8)
        self.assertGreater(x.haversine_km(a,b),.5)
        self.assertLess(x.haversine_km(a,b),1)
        self.assertEqual(x.haversine_km(a,a),0)


if __name__=='__main__':
    unittest.main()
