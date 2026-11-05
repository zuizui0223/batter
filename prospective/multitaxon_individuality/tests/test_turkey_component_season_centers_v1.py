"""Synthetic tests: original GPS seasonal centers & disconnected spatial groups.

No original animal locations, animal IDs or positions are included.
"""
from __future__ import annotations
from datetime import datetime
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import turkey_component_season_centers_v1 as m
import cross_source_seasonal_x_v2 as geo


def original_fix(animal, year, month, day, lat, lon):
    return geo.Fix(animal,year,month,datetime(year,month,day).toordinal(),lat,lon)


class TestTurkeyComponentSeasonCenters(unittest.TestCase):
    def test_components_disconnected_and_singleton_not_invented(self):
        edge={('a','b'),('b','c'),('a','c'),('d','e'),('d','f')}
        results=m._components(edge)
        self.assertEqual([(len(x),len(y)) for x,y in results],[(3,3),(3,2)])
        self.assertEqual(set().union(*(x for x,_ in results)),set("abcdef"))

    def test_annual_center_crosses_antimeridian_not_false_zero(self):
        events=[
            original_fix('a',2019,1,1,0,179),
            original_fix('a',2019,1,2,0,-179),
            original_fix('a',2019,1,3,0,179),
            original_fix('a',2019,1,4,0,-179),
            original_fix('a',2019,1,5,0,179),
            original_fix('a',2019,1,6,0,-179),
            original_fix('a',2019,1,7,0,179)]
        centers,counts=m.seasonal_source_centres(events,(1,2,12))
        self.assertEqual(counts[2019]['a'],7)
        antipodal=m._xyz(0,180)
        self.assertLess(geo.centroid_distance_km(centers[2019]['a'],antipodal),20)

    def test_daily_balance_not_gps_fix_count_weighted(self):
        events=[]
        for _ in range(100):
            events.append(original_fix('a',2019,1,1,0,0))
        for day in range(2,8):
            events.append(original_fix('a',2019,1,day,0,90))
        centers,counts=m.seasonal_source_centres(events,(1,))
        self.assertEqual(counts[2019]['a'],7)
        target=m._xyz(0,90)
        # Six equal-weight observation days near lon90 dominate the
        # one day with hundred fixes near lon0.
        self.assertLess(geo.centroid_distance_km(centers[2019]['a'],target),1600)

    def test_season_missing_observation_days_excluded_not_zero(self):
        ev=[original_fix('a',2019,1,day,0,0) for day in range(1,7)]
        result,counts=m.seasonal_source_centres(ev,(1,2,12))
        self.assertNotIn('a',result.get(2019,{}))
        self.assertNotIn('a',counts.get(2019,{}))

    def test_pair_season_distance_distinguishes_geographic_closer_winter(self):
        centers={'winter':{2019:{'a':m._xyz(0,0),'b':m._xyz(0,.001)}},
                 'summer':{2019:{'a':m._xyz(0,0),'b':m._xyz(0,1)}}}
        outcome=m._pairwise_season_distance({('a','b')},centers,2019)
        self.assertEqual(outcome['n_pairs_with_both_centres'],1)
        self.assertEqual(outcome['fraction_pairs_winter_centres_closer'],1)
        self.assertLess(outcome['winter_distances_km']['median'],
                        outcome['comparator_distances_km']['median'])
        centers['winter'][2019].pop('b')
        missing=m._pairwise_season_distance({('a','b')},centers,2019)
        self.assertEqual(missing['n_pairs_with_both_centres'],0)
        self.assertIsNone(missing['winter_minus_comparator_distance_km']
                          if 'winter_minus_comparator_distance_km' in missing else None)

    def test_disjoint_2020_pair_classes_and_2019_component_preconditions(self):
        # Construct 2020 clique 14 edges among six animals,
        # plus seven additional dyads with 5–10/10–25km
        allpairs=set()
        for a,b in [('a','b'),('a','c'),('a','d'),('a','e'),
                    ('a','f'),('b','c'),('b','d'),('b','e'),
                    ('b','f'),('c','d'),('c','e'),('c','f'),
                    ('d','e'),('e','f'),('a','g'),('b','g'),
                    ('c','g'),('d','g'),('e','g'),('f','g'),
                    ('d','f')]:
            allpairs.add((a,b))
        near5={p for p in allpairs if p[1]!='g' and p!=('d','f')}
        dist={p:(2 if p in near5 else 7 if p in {('a','g'),('b','g')} else 14)
              for p in allpairs}
        parts=m._group_sets(2020,allpairs,dist)
        self.assertEqual(len(parts['annual_0_to5km']),14)
        self.assertEqual(len(parts['annual_5_to10km']),2)
        self.assertEqual(len(parts['annual_10_to25km']),5)
        self.assertEqual(len(parts['annual_5_to25km']),7)

    def test_exact_shared_days_and_3_original_source_fixes_for_paired_centers(self):
        support={}
        for mon in (1,2,6,7):
            dates={}
            for day in range(1,9):
                ordinal=datetime(2019,mon,day).toordinal()
                triples=[]
                for hour in (1,7,13):
                    a=(hour*3600.,0.,0.)
                    b=(hour*3600.,0.,.001)
                    triples.append((a,b,b,b))
                dates[ordinal]=tuple(triples)
            support[mon]=dates
        pair=('a','b')
        c=m._matched_selected_season_center(support,'winter',pair,'turkey',2019,900,3)
        self.assertEqual(len(c),2)
        self.assertLess(geo.centroid_distance_km(*c),.2)
        q=m._paired_sample_center_deltas({pair:support},{pair},'turkey',2019,900)
        self.assertEqual(q['n_pairs'],1)
        self.assertEqual(len(q['seed_summaries']),12)
        self.assertLess(q['median_winter_distance_across_seeds_km'],.2)

    def test_result_summary_rejects_below_eight_pair_L1_but_retains_geometry(self):
        pairs={('a','b'),('b','c')}
        out=m.spatial._summary_for_edges({},pairs)
        self.assertEqual(out['status'],'NOT_ESTIMABLE_INSUFFICIENT_WITHIN_SOURCE_PAIR_SUPPORT')
        self.assertEqual(out['n_pairs'],2)
        self.assertEqual(out['radii'],[])


if __name__ == '__main__':
    unittest.main()
