"""Synthetic source-tracking tests for ordered +/-1-day original GPS reference.

No biological animal IDs, GPS coordinates or original tracking records used.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import math
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import day_shift_preserved_trajectory_v1 as mod
import subhour_geodesic_proximity_v1 as geodesic


def records(*, animals=('a','b','c'), months=(1,2,6,7,12),
            days=range(1,11), move_per_day_km=4.0, b_time_offset=0):
    """Invented animals visit a daily geographic patch; 3 observed times/day."""
    out={}
    for month in months:
        for day in days:
            ordinal=datetime(2019,month,day).toordinal()
            for animal in animals:
                coords=[]
                for index in range(3):
                    second=3600 + 7200*index
                    if animal != 'a':
                        second += b_time_offset
                    lon=(day*move_per_day_km)/(111.32)
                    coords.append((float(second),.001,lon))
                out[(2019,month,animal,ordinal)]=tuple(sorted(coords))
    return out


class TestOriginalDayShift(unittest.TestCase):
    def test_one_to_one_matches_are_unique_and_sorted(self):
        a=[(0.,.0,.0),(600.,.0,.0),(1200.,.0,.0)]
        b=[(200.,.0,.0),(800.,.0,.0),(1800.,.0,.0)]
        valid=mod._time_matches_by_A(a,b,600)
        self.assertEqual(len(valid),3)
        self.assertEqual(len(set(valid.values())),3)
        self.assertEqual(len(mod._time_matches_by_A(a,b,100)),0)

    def test_common_A_fix_is_explicitly_shared_by_all_reference_days(self):
        by=records(animals=('a','b'))
        support=mod.eligible_day_shift(by,{('a','b')},2019,900)
        self.assertEqual(set(support),{('a','b')})
        monthly=support[('a','b')]
        self.assertEqual(set(monthly),{1,2,6,7,12})
        self.assertEqual(len(monthly[1]),8)  # only d=2..9 have both neighbors
        for anchors in monthly[1].values():
            self.assertEqual(len(anchors),3)
            for a,b0,bprev,bnext in anchors:
                self.assertEqual(a[0],b0[0])
                self.assertEqual(a[0],bprev[0])
                self.assertEqual(a[0],bnext[0])
        self.assertAlmostEqual(mod._daily_proximity(monthly[1][min(monthly[1])])[0][.5]['same'],1)
        self.assertEqual(mod._daily_proximity(monthly[1][min(monthly[1])])[0][2.]['previous_day'],0)

    def test_stationary_source_day_reference_does_not_show_spurious_day_specific_effect(self):
        by=records(move_per_day_km=0)
        supported=mod.eligible_day_shift(by,{('a','b'),('a','c'),('b','c')},2019,900)
        res=mod._one_seed(supported,'turkey',2019,900,3)
        self.assertEqual(len(res),3)
        for r in res:
            self.assertEqual(r['n_dyads'],3)
            self.assertEqual(r['n_sampled_pair_dates'],84)
            self.assertEqual(r['n_sampled_fix_triples'],252)
            for season in ('winter','summer'):
                self.assertAlmostEqual(r[season]['same'],1)
                self.assertAlmostEqual(r[season]['previous_day'],1)
                self.assertAlmostEqual(r[season]['next_day'],1)
                self.assertAlmostEqual(r[season]['same_minus_adjacent'],0)

    def test_consecutive_day_spatial_drift_creates_same_day_surplus(self):
        by=records(move_per_day_km=4)
        supported=mod.eligible_day_shift(by,{('a','b')},2019,900)
        result=mod._one_seed(supported,'black_bear',2019,900,5)
        self.assertEqual(len(result),3)
        for row in result:
            for season in ('winter','summer'):
                self.assertEqual(row[season]['same'],1.)
                self.assertEqual(row[season]['previous_day'],0.)
                self.assertEqual(row[season]['next_day'],0.)
                self.assertEqual(row[season]['same_minus_adjacent'],1.)

    def test_failed_15min_but_pass_30min_original_tolerance(self):
        by=records(animals=('a','b'),b_time_offset=1200)
        self.assertFalse(mod.eligible_day_shift(by,{('a','b')},2019,900))
        supported=mod.eligible_day_shift(by,{('a','b')},2019,1800)
        self.assertEqual(len(supported),1)
        row=mod._one_seed(supported,'white_tailed_deer',2019,1800,0)[0]
        for season in ('winter','summer'):
            self.assertAlmostEqual(
                row['mean_abs_source_clock_gap_seconds'][season]['same'],1200)
            self.assertAlmostEqual(
                row['mean_abs_source_clock_gap_seconds'][season]['next_day'],1200)

    def test_missing_adjacent_recording_dates_is_not_zero_proximity(self):
        by=records(days=range(1,8))
        self.assertFalse(mod.eligible_day_shift(by,{('a','b')},2019,900))
        sparse={k:v for k,v in records().items() if k[1] in (1,6,7)}
        self.assertFalse(mod.eligible_day_shift(sparse,{('a','b')},2019,900))

    def test_no_cross_source_year_or_month_shift(self):
        by=records(animals=('a','b'))
        self.assertFalse(mod.eligible_day_shift(by,{('a','b')},2020,900))
        for month in (1,2,6,7,12):
            Jan1=datetime(2019,month,1).toordinal()
            assert Jan1 not in mod.eligible_day_shift(by,{('a','b')},2019,900)[('a','b')][month]

    def test_negative_day_specific_surplus_is_not_forced_positive(self):
        vals=[((3600+i*7200,.001,0),
               (3600+i*7200,.001,.3),
               (3600+i*7200,.001,0),
               (3600+i*7200,.001,.6)) for i in range(3)]
        data,_=mod._daily_proximity(vals)
        self.assertEqual(data[1.]['same'],0)
        self.assertEqual(data[1.]['previous_day'],1)
        self.assertEqual(data[1.]['next_day'],0)
        self.assertAlmostEqual(
            data[1.]['same']-(data[1.]['previous_day']+data[1.]['next_day'])/2,-.5)

    def test_sampled_anchor_matches_have_consistent_original_source_time(self):
        by=records()
        pairs={('a','b'),('a','c'),('b','c')}
        selected=mod.eligible_day_shift(by,pairs,2019,900)
        result=mod._one_seed(selected,'turkey',2019,900,9)
        for row in result:
            self.assertEqual(
                row['winter_minus_summer']['same_minus_adjacent'],0)
            for season in ('winter','summer'):
                for name in ('same','previous_day','next_day'):
                    self.assertLessEqual(
                        row['mean_abs_source_clock_gap_seconds'][season][name],900)

    def test_radius_grids_share_identical_date_and_fixes(self):
        by=records()
        supported=mod.eligible_day_shift(by,{('a','b')},2019,900)
        res=mod._one_seed(supported,'turkey',2019,900,4)
        self.assertEqual([x['radius_km'] for x in res],[.5,1.,2.])
        for month in ('winter','summer'):
            for name in ('same','previous_day','next_day'):
                p=[r[month][name] for r in res]
                self.assertEqual(p,sorted(p))
        for x in res:
            self.assertEqual(x['n_sampled_pair_dates'],28)
            self.assertEqual(x['n_sampled_fix_triples'],84)


if __name__=='__main__':
    unittest.main()
