"""Synthetic source-GPS monthly ecology contracts — no original animal tracks."""
from __future__ import annotations

from datetime import datetime
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import cross_source_seasonal_x_v2 as geo
import turkey_component_season_centers_v1 as previous
import turkey_monthly_core_separation_v1 as monthly


def fix(year,month,day,animal,lon,lat=0):
    return geo.Fix(animal,year,month,datetime(year,month,day).toordinal(),lat,lon)


class TestMonthlyTurkeyOriginalSourceGPS(unittest.TestCase):
    def test_one_month_requires_at_least_seven_distinct_original_days(self):
        data=[fix(2020,1,d,'a',0.) for d in range(1,7)]
        centres,counts=monthly.month_centroids(data)
        self.assertEqual(centres,{})
        self.assertEqual(counts,{})
        data.append(fix(2020,1,7,'a',0.))
        data.append(fix(2020,2,1,'b',0.))
        centres,counts=monthly.month_centroids(data)
        self.assertEqual(set(centres),{(2020,1)})
        self.assertEqual(set(centres[(2020,1)]),{'a'})
        self.assertEqual(counts[(2020,1)]['a'],7)

    def test_day_equal_weighting_not_fix_count_overweighting(self):
        data=[fix(2020,1,d,'a',0.) for d in range(1,7)]
        data.extend(fix(2020,1,7,'a',.1) for _ in range(100))
        centres,_=monthly.month_centroids(data)
        observed=centres[(2020,1)]['a']
        origin=previous._xyz(0,0)
        far=previous._xyz(0,.1)
        near_km=geo.centroid_distance_km(observed,origin)
        far_km=geo.centroid_distance_km(observed,far)
        self.assertLess(near_km,3)
        self.assertGreater(far_km,7)

    def test_antimeridian_geographic_month_centres_wrap_correctly(self):
        events=[fix(2020,1,d,'a',179.9 if d%2==0 else -179.9)
                for d in range(1,9)]
        centres,_=monthly.month_centroids(events)
        dateline=previous._xyz(0,180)
        self.assertLess(geo.centroid_distance_km(centres[(2020,1)]['a'],dateline),2)

    def test_pair_distance_summary_never_outputs_raw_animal_pair_names(self):
        pts={'a':previous._xyz(0,0),'b':previous._xyz(0,.001),
             'c':previous._xyz(0,.002)}
        pairs={('a','b'),('a','c'),('b','c')}
        r=monthly.describe_distances(pairs,pts)
        self.assertEqual(r['status'],'DESCRIPTIVE_SOURCE_MONTH_CENTROID_DISTANCE')
        self.assertEqual(r['n_original_pairs'],3)
        self.assertEqual(r['n_animals_in_valid_monthly_pairs'],3)
        self.assertGreater(r['distance_km']['median'],0)
        self.assertNotIn("'a'",str(r))
        self.assertNotIn("'b'",str(r))
        self.assertNotIn("'c'",str(r))
        self.assertNotIn('animal_id',str(r).lower())

    def test_insufficient_valid_pairs_return_none_not_zero(self):
        pts={'a':previous._xyz(0,0),'b':previous._xyz(0,.001)}
        pairs={('a','b'),('a','c'),('b','c')}
        r=monthly.describe_distances(pairs,pts)
        self.assertEqual(r['n_valid_monthly_pairs'],1)
        self.assertEqual(r['status'],'NOT_ESTIMABLE_MONTHLY_SOURCE_SUPPORT')
        self.assertIsNone(r['distance_km'])

    def test_fixed_2020_one_mover_winter_close_summer_separated(self):
        # Synthetic positions only; no original GPS or wildlife site disclosure.
        core=('a','b','c','d','e','f')
        isolate='z'
        allfixes=[]
        for month,iso_long in ((1,0.),(2,0.),(3,.025),(4,.06),(5,.09),(6,.13),(7,.13),(8,.13)):
            for day in range(1,11):
                for name in core:
                    allfixes.append(fix(2020,month,day,name,0.))
                allfixes.append(fix(2020,month,day,isolate,iso_long))
        centres,_=monthly.month_centroids(allfixes)
        pairs={(isolate,name) for name in core}
        states=[]
        for month in range(1,13):
            group=monthly.describe_distances(pairs,centres.get((2020,month),{}))
            if group['n_valid_monthly_pairs']<4:
                state='UNOBSERVED'
            elif group['distance_km']['median']<=1:
                state='CLOSE'
            elif group['distance_km']['median']>=5:
                state='SEPARATED'
            else:state='INTERMEDIATE'
            states.append({'month':month,'state':state})
        self.assertEqual([r['state'] for r in states[:8]],
            ['CLOSE','CLOSE','INTERMEDIATE','SEPARATED',
             'SEPARATED','SEPARATED','SEPARATED','SEPARATED'])
        bracket=monthly.transition_bracket(states)
        self.assertEqual((bracket['last_observed_close_month'],
                          bracket['first_later_observed_separated_month']),(2,4))
        self.assertEqual(bracket['observed_intermediate_months_in_bracket'],1)
        self.assertEqual(bracket['unobserved_months_in_bracket'],0)

    def test_gap_bracket_must_report_unobserved_calendar_months(self):
        x=[{'month':m,'state':'CLOSE' if m==2 else
               'SEPARATED' if m==7 else 'UNOBSERVED'}
           for m in range(1,13)]
        r=monthly.transition_bracket(x)
        self.assertEqual(r['last_observed_close_month'],2)
        self.assertEqual(r['first_later_observed_separated_month'],7)
        self.assertEqual(r['unobserved_months_in_bracket'],4)
        self.assertEqual(r['status'],'OBSERVATION_BRACKET_NOT_TRACKED_TRANSITION_TIME')

    def test_no_supported_close_then_separated_bracket_is_null(self):
        x=[{'month':m,'state':'UNOBSERVED' if m!=7 else 'SEPARATED'}
           for m in range(1,13)]
        self.assertEqual(monthly.transition_bracket(x),
            {'status':'NO_SUPPORTED_CLOSE_TO_SEPARATED_BRACKET'})

    def test_distance_domain_and_zero_pair_semantics(self):
        pts={'a':previous._xyz(0,0),'b':previous._xyz(0,0)}
        row=monthly.describe_distances({('a','b')},pts)
        self.assertIsNone(row['distance_km'])
        self.assertEqual(row['n_valid_monthly_pairs'],1)
        self.assertIsNone(monthly.describe_distances(set(),pts)['eligible_pair_fraction'])

    def test_previous_source_center_reference_matches_date_equal_month_logic(self):
        data=[fix(2020,1,d,'a',0.) for d in range(1,10)]
        data+=[fix(2020,1,d,'b',.01) for d in range(1,10)]
        original,counts=previous.seasonal_source_centres(data,(1,),min_dates=7)
        computed, days=monthly.month_centroids(data)
        self.assertEqual(original[2020],computed[(2020,1)])
        self.assertEqual(counts[2020],days[(2020,1)])


if __name__=='__main__':
    unittest.main()
