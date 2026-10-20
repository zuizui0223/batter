import csv
import io
import json
import math
import tempfile
import unittest
import zipfile
from datetime import datetime
from pathlib import Path

import cross_source_seasonal_overlap_v1 as c


def synthetics(year=2019, first=(1,2), second=(3,4), n=3):
    records=[]
    for m in first+second:
        for a in range(n):
            for day in range(1,10):
                x=(.001 if m in first else (.001 if a==0 else .1))
                # matching source date day is calculated within same calendar month
                records.append((str(a),year,m,datetime(year,m,day).toordinal(),x,0.,str(a)))
    return records


class TestDecomposition(unittest.TestCase):
    def test_exact_identity_and_compensating_contributions(self):
        # The counts and mean-positive overlap in the earlier session are rounded.
        d=c.calculate_incidence_strength({str(k):.544 if k<6 else 0. for k in range(78)},
                                         {str(k):.232 if k<14 else 0. for k in range(78)})
        self.assertEqual(d['n_pairs'],78)
        self.assertEqual(d['pair_state_counts']['both_positive'],6)
        self.assertEqual(d['pair_state_counts']['summer_only'],8)
        self.assertAlmostEqual(d['winter']['mean_X'],6*.544/78)
        self.assertAlmostEqual(d['summer']['mean_X'],14*.232/78)
        self.assertAlmostEqual(d['winter_minus_summer_X'],.016/78)
        self.assertAlmostEqual(d['incidence_component'],-3.104/78)
        self.assertAlmostEqual(d['strength_component'],3.120/78)
        self.assertAlmostEqual(d['decomposition_residual'],0,places=12)

    def test_marginals_do_not_determine_pair_rewiring(self):
        w={'a':.4,'b':0,'c':0,'d':0}
        s1={'a':.2,'b':.2,'c':0,'d':0}
        s2={'a':0,'b':.2,'c':.2,'d':0}
        a=c.calculate_incidence_strength(w,s1)
        b=c.calculate_incidence_strength(w,s2)
        self.assertEqual(a['winter_minus_summer_X'],b['winter_minus_summer_X'])
        self.assertNotEqual(a['pair_state_counts'],b['pair_state_counts'])

    def test_empty_pairs_are_not_a_zero_result(self):
        self.assertEqual(c.calculate_incidence_strength({}, {})['status'], 'NOT_ESTIMABLE_NO_MATCHED_PAIRS')
        with self.assertRaises(ValueError):c.calculate_incidence_strength({'a':.1},{'b':.1})
        for v in (float('nan'),float('inf'),-1,1.01,None):
            with self.assertRaises(ValueError):c.calculate_incidence_strength({'a':v},{'a':0})

    def test_season_all_zero_has_defined_mean_but_undefined_strength(self):
        d=c.calculate_incidence_strength({'a':0,'b':0},{'a':.5,'b':0})
        self.assertEqual(d['winter']['mean_X'],0)
        self.assertIsNone(d['winter']['conditional_strength'])
        self.assertIsNone(d['incidence_component'])
        self.assertAlmostEqual(d['winter_minus_summer_X'],-.25)

    def test_month_support_and_season_support(self):
        obs={1:{('a','b'):.3},2:{('a','b'):.5},3:{('a','b'):.4},
             6:{('a','b'):.1},7:{('a','b'):.1}}
        self.assertAlmostEqual(c._combine_window(obs,(1,2,3))[('a','b')],.4)
        self.assertEqual(c._combine_window(obs,(6,7)),{('a','b'):.1})
        self.assertEqual(c._combine_window(obs,(8,9)),{})


class TestSourceGeography(unittest.TestCase):
    def test_identical_and_separate_pair_7date_support(self):
        events=[]
        for a,lon in (('a',.0),('b',.0),('c',10.)):
            for d in range(1,9):
                events.append((a,2019,1,datetime(2019,1,d).toordinal(),lon,0.,a))
        got=c.pair_date_geography(events,2019,1,1,(0,0))
        self.assertEqual(got[('a','b')],1.)
        self.assertEqual(got[('a','c')],0.)
        self.assertEqual(got[('b','c')],0.)
        # Non-concurrent observed dates cannot be inferred to have overlap 0.
        events=[r for r in events if r[0]!='b' or datetime(2019,1,1).toordinal()<=r[3]<=datetime(2019,1,6).toordinal()]
        got=c.pair_date_geography(events,2019,1,1,(0,0))
        self.assertNotIn(('a','b'),got)

    def test_pair_day_balancing_and_date_intersection(self):
        records=[]
        for d in range(1,8):
            t=datetime(2019,1,d).toordinal()
            records.extend([('a',2019,1,t,0.,0.,'a'),('b',2019,1,t,0.,0.,'b')])
        # Date without b must be ignored even if a has many distant fixes
        for _ in range(200):records.append(('a',2019,1,datetime(2019,1,8).toordinal(),8.,0.,'a'))
        got=c.pair_date_geography(records,2019,1,1,(0,0))
        self.assertAlmostEqual(got[('a','b')],1.)

    def test_artificial_early_late_complete_pairs(self):
        records=synthetics()
        output=c.compute_source_comparisons(records)
        self.assertEqual(len(output),2*4*4*2)
        e=[r for r in output if r['window']=='early_late' and r['year']==2019
           and r['grid_km']==1 and r['origin_x_fraction']==r['origin_y_fraction']==0][0]
        self.assertEqual(e['n_pairs'],3)
        self.assertEqual(e['n_matched_animals'],3)
        self.assertGreaterEqual(e['winter_minus_summer_X'],0)
        self.assertEqual(e['pair_state_counts']['both_positive'],1)
        self.assertEqual(e['pair_state_counts']['winter_only'],2)

    def test_reference_join_and_quality_filter(self):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp)
            ref=base/'ref.csv';data=base/'gps.csv'
            with ref.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=['animal-id','tag-id','animal-sex','study-site']);w.writeheader()
                w.writerow({'animal-id':'a','tag-id':'t','animal-sex':'f','study-site':'test'})
            events=[{'individual-local-identifier':'a','tag-local-identifier':'t','sensor-type':'gps','visible':'true',
                     'individual-taxon-canonical-name':'Alces alces','location-lat':'0','location-long':'1',
                     'timestamp':'2019-01-01 00:00:00.000'},
                    {'individual-local-identifier':'a','tag-local-identifier':'t','sensor-type':'gps','visible':'true',
                     'individual-taxon-canonical-name':'Alces alces','location-lat':'0','location-long':'1',
                     'timestamp':'2019-01-01 00:00:00.000'}]
            with data.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=list(events[0]));w.writeheader();w.writerows(events)
            rows,audit=c._source_year_records([(data,'gps.csv')],(ref,'ref.csv'),'Alces alces')
            self.assertEqual(len(rows),1)
            self.assertEqual(audit['filter_counts']['identical_duplicate_removed'],1)
            self.assertEqual(audit['reference_animals'],1)
            self.assertEqual(audit['source_clock_verified_utc'],False)
            self.assertEqual(audit['source_calendar_years_parsed_before_position_qc'], {'2019':2})
            self.assertIn('timestamp', audit['source_columns'])

    def test_zip_ignores_macos_metadata_but_requires_real_csv(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'gps.bin'
            with zipfile.ZipFile(path,'w') as f:
                f.writestr('__MACOSX/._gps.csv', 'junk')
                f.writestr('folder/gps.csv','a,b\n1,2\n')
            result=list(c._read_csv(path,'gps.csv.zip'))
            self.assertEqual(result,[{'a':'1','b':'2'}])
            with zipfile.ZipFile(path,'w') as f:
                f.writestr('a.csv','a\n1\n');f.writestr('b.csv','a\n2\n')
            with self.assertRaises(ValueError):list(c._read_csv(path,'gps.csv.zip'))


if __name__=='__main__': unittest.main()
