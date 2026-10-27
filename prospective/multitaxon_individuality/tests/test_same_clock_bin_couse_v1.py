"""Synthetic-only tests of original-source matched-bin geography versus temporal alignment."""
from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path
import math
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import same_clock_bin_couse_v1 as s
import cross_source_seasonal_x_v2 as old


def fabricated(*, aligned=True, people=('a','b','c'), months=(1,2,6,7),
               days=range(1,9), hours=(0,6), lon_delta=.09):
    timed=[]
    for month in months:
        for day in days:
            ordinal=datetime(2019,month,day).toordinal()
            for animal in people:
                for index,hour in enumerate(hours):
                    # All animals visit the SAME two places on the same day.
                    # Only alignment of their clock labels differs.
                    x=index if animal=='a' or aligned else 1-index
                    timed.append(s.TimedFix(animal,2019,month,ordinal,
                                             lat=.001,lon=.001+x*lon_delta,hour=hour))
    untimed=[old.Fix(v.animal,v.year,v.month,v.day,v.lat,v.lon) for v in timed]
    return timed,untimed


class TestClockBinCouse(unittest.TestCase):
    def test_asynchronous_same_spatial_set_versus_aligned_clock(self):
        grid=(5.,0.,0.)
        self.assertEqual(s.day_statistics([(0,0),(1,0)],[(1,0),(0,0)]),
                         (1.,0.,.5,-.5))
        self.assertEqual(s.day_statistics([(0,0),(1,0)],[(0,0),(1,0)]),
                         (1.,1.,.5,.5))
        self.assertEqual(s.day_statistics([(0,0),(0,0)],[(1,0),(1,0)]),
                         (0.,0.,0.,0.))
        with self.assertRaises(AssertionError):
            s.day_statistics([(0,0)],[(0,0)])

    def test_source_clock_day_and_shared_bin_eligibility_fixed_before_spatial_scoring(self):
        timed,untimed=fabricated()
        centers=old.annual_day_balanced_centroids(untimed)
        base=s._base_pair_set(untimed,2019,centers)
        self.assertEqual(len(base),3)
        by,support=s.time_supported_pairs(base,timed,6,2019)
        self.assertEqual(len(support),3)
        for monthly in support.values():
            self.assertEqual(set(monthly),{1,2,6,7})
            self.assertEqual(len(monthly[1]),8)
            self.assertEqual(set(monthly[1].values()),{(0,1)})
        self.assertEqual(by[(2019,1,'a',datetime(2019,1,1).toordinal(),0)][0],(.001,.001))

    def test_7_shared_dates_2_months_per_season_are_necessary(self):
        timed,untimed=fabricated(days=range(1,7))
        centers=old.annual_day_balanced_centroids(untimed)
        self.assertFalse(s._base_pair_set(untimed,2019,centers))
        timed,untimed=fabricated(months=(1,6,7))
        centers=old.annual_day_balanced_centroids(untimed)
        self.assertFalse(s._base_pair_set(untimed,2019,centers))

    def test_one_common_bin_date_is_missing_not_zero_T(self):
        timed,untimed=fabricated()
        timed=[v for v in timed if not (v.animal=='c' and v.hour==6)]
        centers=old.annual_day_balanced_centroids(untimed)
        base=s._base_pair_set(untimed,2019,centers)
        _,support=s.time_supported_pairs(base,timed,6,2019)
        self.assertEqual(set(support),{('a','b')})

    def test_three_hour_vs_six_hour_opportunity_differs(self):
        timed,untimed=fabricated(hours=(1,5))
        base=s._base_pair_set(untimed,2019,old.annual_day_balanced_centroids(untimed))
        _,six=s.time_supported_pairs(base,timed,6,2019)
        _,three=s.time_supported_pairs(base,timed,3,2019)
        self.assertEqual(len(six),0)
        self.assertEqual(len(three),3)

    def test_random_source_fix_draw_reproducible_and_row_order_invariant(self):
        x=[(.1,.2),(.3,.4),(.5,.6)]
        self.assertEqual(s._choice(x,1,'animal','day','bin'),
                         s._choice(list(reversed(x)),1,'animal','day','bin'))
        self.assertEqual(len(s._choice(x,3,'all')),3)
        with self.assertRaises(AssertionError):
            s._choice(x,4,'too-many')

    def test_evaluation_finds_positive_and_negative_conditional_temporal_alignment(self):
        synchronous,untimed=fabricated(aligned=True)
        asynch,_=fabricated(aligned=False)
        grid=(5.,0.,0.)
        cases=[]
        for timed in (synchronous,asynch):
            centers=old.annual_day_balanced_centroids(untimed)
            pairs=s._base_pair_set(untimed,2019,centers)
            by,support=s.time_supported_pairs(pairs,timed,6,2019)
            rows=s.evaluate_seed(by,support,'black_bear',2019,6,3,
                                 math.cos(math.radians(.001)))
            ref=next(row for row in rows if (row['grid_km'],row['origin_x_fraction'],row['origin_y_fraction'])==grid)
            cases.append(ref)
            self.assertEqual(ref['n_supported_dyads'],3)
            self.assertEqual(ref['n_pair_dates'],3*2*2*7)
            self.assertEqual(ref['mean_shared_clock_bins_per_pair_date'],2.)
            self.assertLessEqual(ref['winter']['T'],ref['winter']['X'])
            self.assertAlmostEqual(ref['winter']['D'],ref['winter']['T']-ref['winter']['N'])
            self.assertEqual(ref['winter_minus_summer']['D'],0)
        self.assertGreater(cases[0]['winter']['D'],cases[1]['winter']['D'])

    def test_any_grid_x_smaller_than_T_rejected_and_no_one_bin(self):
        with self.assertRaises(AssertionError):
            s.day_statistics([(0,0),(1,0)],[(0,0)])
        t,x=s.fabricated if False else (None,None)
        self.assertEqual(s.day_statistics([(0,0),(0,0)],[(0,0),(0,0)]),
                         (1.,1.,1.,0.))

    def test_2019_no_2020_observations_retained_as_non_estimable(self):
        timed,untimed=fabricated()
        centers=old.annual_day_balanced_centroids(untimed)
        self.assertEqual(s._base_pair_set(untimed,2020,centers),set())

    def test_date_aggregation_no_hardcoded_source_animals(self):
        timed,untimed=fabricated(people=('q','r'))
        base=s._base_pair_set(untimed,2019,old.annual_day_balanced_centroids(untimed))
        self.assertEqual(len(base),1)
        by,support=s.time_supported_pairs(base,timed,6,2019)
        self.assertEqual(len(support),1)
        rows=s.evaluate_seed(by,support,'white_tailed_deer',2019,6,0,
                             math.cos(math.radians(.001)))
        self.assertEqual(len(rows),4)
        self.assertEqual(rows[0]['n_supported_dyads'],1)
        self.assertTrue(all(row['n_pair_dates']==28 for row in rows))


if __name__=='__main__':
    unittest.main()
