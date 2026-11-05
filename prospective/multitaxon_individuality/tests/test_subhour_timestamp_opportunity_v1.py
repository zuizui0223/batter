"""Synthetic-only sub-hour source-timestamp match support contracts."""
from collections import defaultdict
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import subhour_timestamp_opportunity_v1 as v


def make_times(animals, source_months=(1,2,6,7), days=range(1,9),
               shifted=None):
    out={}
    shifted=shifted or {}
    for month in source_months:
        for day in days:
            ordinal=20190000+month*100+day
            for animal in animals:
                lag=shifted.get(animal,0)
                out[(2019,month,animal,ordinal)]=(3600+lag,10800+lag,18000+lag,25200+lag)
    return out


class TestSubhourSupport(unittest.TestCase):
    def test_greedy_maximum_one_to_one_matching(self):
        self.assertEqual(v.paired_fix_count((0,600,1200),(450,1000,2000),600),2)
        self.assertEqual(v.paired_fix_count((0,0,0),(0,),0),1)
        self.assertEqual(v.paired_fix_count((0,900),(900,),900),1)
        self.assertEqual(v.paired_fix_count((0,),(901,),900),0)

    def test_fifteen_minutes_is_subset_of_thirty_minute_support(self):
        by=make_times(('a','b','c'),shifted={'c':1500})
        pairs={('a','b'),('a','c'),('b','c')}
        small=v.time_opportunity(by,pairs,2019,900)
        large=v.time_opportunity(by,pairs,2019,1800)
        self.assertEqual(small['n_eligible_dyads'],1)
        self.assertEqual(large['n_eligible_dyads'],3)
        self.assertEqual(small['n_eligible_animals'],2)
        self.assertTrue(small['_eligible_pairs_private']<=large['_eligible_pairs_private'])
        self.assertEqual(small['status'],'STOP_SMALL_OPPORTUNITY_NOT_ZERO_ENCOUNTER')

    def test_source_readiness_floor_with_nine_independent_pair_opportunities(self):
        animals=('a','b','c','d','e')
        from itertools import combinations
        pairs=set(combinations(animals,2))
        out=v.time_opportunity(make_times(animals),pairs,2019,900)
        self.assertEqual(out['n_eligible_dyads'],10)
        self.assertEqual(out['n_eligible_animals'],5)
        self.assertEqual(out['status'],'TIME_OPPORTUNITY_SUFFICIENT_FOR_SEPARATE_SOURCE_ACCURACY_AND_POPULATION_AUDIT')

    def test_requires_three_matchable_fixes_per_date_not_one(self):
        by=make_times(('a','b'))
        by={key:values[:2] for key,values in by.items()}
        r=v.time_opportunity(by,{('a','b')},2019,1800)
        self.assertEqual(r['n_eligible_dyads'],0)
        self.assertEqual(r['n_dyad_dates_with_at_least_three_matched_fixes'],0)
        self.assertIsNone(r['qualifying_dates_per_eligible_dyad']['median'])

    def test_seven_dates_and_two_months_per_season(self):
        pairs={('a','b')}
        by=make_times(('a','b'),days=range(1,7))
        self.assertEqual(v.time_opportunity(by,pairs,2019,1800)['n_eligible_dyads'],0)
        by=make_times(('a','b'),source_months=(1,6,7))
        self.assertEqual(v.time_opportunity(by,pairs,2019,1800)['n_eligible_dyads'],0)

    def test_no_source_cross_year_pairing_and_valid_positive_counts(self):
        by=make_times(('a','b'))
        pairs={('a','b')}
        r=v.time_opportunity(by,pairs,2019,900)
        self.assertEqual(r['n_eligible_dyads'],1)
        self.assertEqual(r['n_dyad_dates_with_at_least_three_matched_fixes'],32)
        self.assertEqual(r['total_greedy_one_to_one_fix_matches_on_qualifying_dyad_dates'],128)
        self.assertEqual(r['qualifying_dates_per_eligible_dyad']['median'],32)
        self.assertEqual(v.time_opportunity(by,pairs,2020,900)['n_eligible_dyads'],0)


if __name__=='__main__':
    unittest.main()
