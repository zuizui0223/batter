"""Offline synthetic checks; no original tracking data or animal names are emitted."""
from __future__ import annotations
from collections import Counter
from datetime import datetime
import importlib
import csv
import hashlib
import io
import json
from unittest.mock import patch
import math
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parent))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

# The repository's real deer_geography_v1 is imported on GitHub Actions.
# For local standalone package checks, fall back to a minimal compatible
# test adapter using the independently tested earlier occupancy implementation.
try:
    import deer_geography_v1
except ModuleNotFoundError:
    import types
    older=importlib.import_module('cross_source_seasonal_overlap_v1')
    fake=types.ModuleType('deer_geography_v1')
    fake.DEFAULT_SCALES_KM=(1.,2.,5.,10.)
    fake.DEFAULT_ORIGINS=((0.,0.),(.5,0.),(0.,.5),(.5,.5))
    def geography(events,animals,lat_cos,min_shared_days=7):
        assert min_shared_days==7
        rows=[(e.animal,e.year,e.month,e.day,e.lon,e.lat,'private') for e in events]
        pairs={(w,x,y):older.pair_date_geography(rows,events[0].year,events[0].month,w,(x,y),lat_cos)
               for w in fake.DEFAULT_SCALES_KM for x,y in fake.DEFAULT_ORIGINS}
        return {},pairs
    fake.compute_geography_overlap=geography
    sys.modules['deer_geography_v1']=fake

import cross_source_seasonal_x_v2 as m


class TestIncidence(unittest.TestCase):
    def test_exact_symmetry_and_four_states(self):
        first={'a':.8,'b':.2,'c':0,'d':0}
        second={'a':.3,'b':0,'c':.5,'d':0}
        result=m.describe(first,second)
        self.assertEqual(result['n_pairs'],4)
        self.assertEqual(result['dyad_states'],{'neither':1,'season1_only':1,'season2_only':1,'both':1})
        self.assertAlmostEqual(result['season1']['mean_X'],.25)
        self.assertAlmostEqual(result['season2']['mean_X'],.2)
        self.assertAlmostEqual(result['incidence_component']+result['positive_strength_component'],.05)
        self.assertAlmostEqual(result['decomposition_residual'],0)

    def test_unmatched_risk_set_rejected(self):
        with self.assertRaises(ValueError):m.describe({'a':.1},{'b':.1})
        for bad in (float('nan'),float('inf'),-1,1.01,None,True):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):m.describe({'a':bad},{'a':0})

    def test_no_pairs_is_missing_not_zero(self):
        self.assertEqual(m.describe({},{}),{'status':'NOT_ESTIMABLE_NO_MATCHED_DYADS','n_pairs':0})
        result=m.describe({'a':0,'b':0},{'a':.2,'b':0})
        self.assertIsNone(result['season1']['positive_strength'])
        self.assertIsNone(result['positive_strength_component'])
        self.assertAlmostEqual(result['difference_season1_minus_season2'],-.1)

    def test_marginal_means_do_not_identify_pair_transitions(self):
        first={'a':.4,'b':0,'c':0,'d':0}
        second1={'a':.2,'b':.2,'c':0,'d':0}
        second2={'a':0,'b':.2,'c':.2,'d':0}
        self.assertEqual(m.describe(first,second1)['difference_season1_minus_season2'],
                         m.describe(first,second2)['difference_season1_minus_season2'])
        self.assertNotEqual(m.describe(first,second1)['dyad_states'],m.describe(first,second2)['dyad_states'])

    def test_synthetic_session_marginals_do_not_reconstruct_unknown_pairing(self):
        first={i:(.544 if i<6 else 0) for i in range(78)}
        second={i:(.232 if i<14 else 0) for i in range(78)}
        d=m.describe(first,second)
        self.assertAlmostEqual(d['difference_season1_minus_season2'],.016/78)
        self.assertAlmostEqual(d['incidence_component'],-3.104/78)
        self.assertAlmostEqual(d['positive_strength_component'],3.12/78)


class TestSeasonSupport(unittest.TestCase):
    def test_two_months_each_season_and_same_pair_set(self):
        pair=('a','b')
        first=m._window_score({1:{pair:.8},2:{pair:.6},3:{pair:.5}},(1,2,3))
        second=m._window_score({6:{pair:.2},7:{pair:.4}},(6,7,8))
        self.assertAlmostEqual(first[pair],(.8+.6+.5)/3)
        self.assertAlmostEqual(second[pair],.3)
        self.assertEqual(m._window_score({1:{pair:.2}},(1,2)),{})

    def test_actual_pair_rewiring_with_known_shared_dates(self):
        events=[]
        # Four distinct pairs; all animals in the same synthetic study label.
        # Winter two months: A/B share same cells; summer two months: A/C.
        for month in (1,2,6,7):
            for day in range(1,9):
                for animal in ('A','B','C'):
                    x = 0.1 if animal=='A' or (animal=='B' and month in (1,2)) or (animal=='C' and month in (6,7)) else 20.1
                    events.append(m.Fix(animal,2019,month,datetime(2019,month,day).toordinal(),0.1/111.32,x/111.32))
        result=m.compare_events(events, {'A':'site','B':'site','C':'site'})
        selected=[row for row in result if row['year']==2019 and row['window']=='winter_summer'
                  and row['grid_km']==1 and row['origin_x_fraction']==row['origin_y_fraction']==0
                  and row['risk_set_mode']=='same_reference_label'][0]
        self.assertEqual(selected['n_pairs'],3)
        self.assertEqual(selected['dyad_states']['season1_only'],1)
        self.assertEqual(selected['dyad_states']['season2_only'],1)
        self.assertEqual(selected['dyad_states']['both'],0)
        self.assertEqual(selected['dyad_states']['neither'],1)
        self.assertEqual(selected['n_matched_animals'],3)

    def test_stratum_requires_known_identical_reference_label(self):
        events=[]
        for month in (1,2,6,7):
            for day in range(1,9):
                for a in ('A','B','C'):
                    events.append(m.Fix(a,2019,month,datetime(2019,month,day).toordinal(),.1/111.32,.1/111.32))
        result=m.compare_events(events, {'A':'same','B':'same','C':'other'})
        src=[r for r in result if r['year']==2019 and r['grid_km']==1 and r['origin_x_fraction']==r['origin_y_fraction']==0 and r['window']=='winter_summer' and r['risk_set_mode']=='source_wide'][0]
        group=[r for r in result if r['year']==2019 and r['grid_km']==1 and r['origin_x_fraction']==r['origin_y_fraction']==0 and r['window']=='winter_summer' and r['risk_set_mode']=='same_reference_label'][0]
        self.assertEqual(src['n_pairs'],3)
        self.assertEqual(group['n_pairs'],1)


class TestReader(unittest.TestCase):
    def test_zip_macos_artifacts_ignored_and_multi_csv_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'a.zip'
            with zipfile.ZipFile(path,'w') as z:
                z.writestr('__MACOSX/._a.csv','junk')
                z.writestr('a.csv','field\nvalue\n')
            self.assertEqual(list(m._csv_rows(path,'a.csv.zip')), [{'field':'value'}])
            with zipfile.ZipFile(path,'w') as z:
                z.writestr('a.csv','a\n1\n')
                z.writestr('b.csv','a\n2\n')
            with self.assertRaises(ValueError):list(m._csv_rows(path,'a.csv.zip'))


class TestSourceIntegrity(unittest.TestCase):
    def test_reference_join_duplicates_and_source_flags(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            reference = root / 'original-reference.csv'
            gps = root / 'original-gps.csv'
            with reference.open('w', newline='') as f:
                writer = csv.DictWriter(f, ['animal-id','tag-id','study-site'])
                writer.writeheader()
                writer.writerows([{'animal-id':'A','tag-id':'ta','study-site':'site'},
                                  {'animal-id':'B','tag-id':'tb','study-site':'site'}])
            def row(animal,tag,lat='2',when='2019-01-01 01:00:00',**extra):
                return {'individual-local-identifier':animal,'tag-local-identifier':tag,
                        'sensor-type':extra.get('sensor','gps'),'visible':extra.get('visible','true'),
                        'individual-taxon-canonical-name':'Ursus americanus',
                        'location-lat':lat,'location-long':'3','timestamp':when,
                        'algorithm-marked-outlier':extra.get('outlier','false')}
            gpsrows=[row('A','ta'),row('A','ta'),row('A','ta',lat='4'),
                     row('B','tb'),row('A','wrong',when='2019-01-02 01:00:00'),
                     row('A','ta',lat='99',when='2019-01-03 01:00:00'),
                     row('A','ta',when='2019-01-04 01:00:00',outlier='true'),
                     row('A','ta',when='2019-01-05 01:00:00',sensor='acceleration'),
                     row('B','tb',when='2021-01-01 01:00:00')]
            with gps.open('w', newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(gpsrows[0]))
                writer.writeheader();writer.writerows(gpsrows)
            events,audit,groups=m.read_originals([(gps,gps.name)],(reference,reference.name),'Ursus americanus')
            self.assertEqual(len(events),1)
            self.assertEqual(audit['identical_duplicate'],1)
            self.assertEqual(audit['conflicting_timestamp'],1)
            self.assertEqual(audit['source_outlier'],1)
            self.assertEqual(audit['missing_reference_pair'],1)
            self.assertEqual(audit['invalid_position'],1)
            self.assertEqual(audit['outside_fixed_years'],1)
            self.assertEqual(groups,{'A':'site','B':'site'})
            self.assertNotIn('A',json.dumps(audit))
            self.assertEqual(audit['retained_fixes_by_year'],{'2019':1})

    def test_publisher_md5_and_size_are_enforced(self):
        data=b'publisher-verified-original'
        with tempfile.TemporaryDirectory() as folder:
            entry={'uuid':'synthetic','filename':'source.csv','size':len(data),
                   'md5':hashlib.md5(data,usedforsecurity=False).hexdigest(),
                   'role':'reference','url':'https://example.invalid/source'}
            with patch.object(m,'urlopen',return_value=io.BytesIO(data)):
                path,receipt=m._download(entry,Path(folder))
            self.assertEqual(path.read_bytes(),data)
            self.assertTrue(receipt['md5_verified'])
            path.write_bytes(b'corrupted')
            with patch.object(m,'urlopen',return_value=io.BytesIO(data)):
                newpath,newreceipt=m._download(entry,Path(folder))
            self.assertEqual(newpath.read_bytes(),data)
            self.assertEqual(receipt['sha256'],newreceipt['sha256'])
            entry['md5']='0'*32
            with self.assertRaisesRegex(ValueError,'MD5'):
                m._download(entry,Path(folder))
            self.assertFalse(path.exists())

    def test_error_stage_reports_no_private_values(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(m,'_manifest',side_effect=ValueError('sensitive tracking identifier and coordinates')):
                result=m.process_source('black_bear',Path(folder))
            self.assertEqual(result['status'],'STOP_SOURCE_OR_ANALYSIS_ERROR')
            self.assertEqual(result['error_stage'],'MANIFEST')
            self.assertEqual(result['error_class'],'ValueError')
            self.assertNotIn('sensitive',json.dumps(result))
            self.assertNotIn('coordinates',json.dumps(result))

    def test_centroid_distance_proximity_and_dateline(self):
        a=m.Fix('A',2019,1,1,0.,0.)
        b=m.Fix('B',2019,1,1,0.,.1)
        c=m.Fix('C',2019,1,1,0.,3.)
        centers=m.annual_day_balanced_centroids([a,b,c])
        self.assertLess(m.centroid_distance_km(centers[2019]['A'],centers[2019]['B']),25)
        self.assertGreater(m.centroid_distance_km(centers[2019]['A'],centers[2019]['C']),100)
        wrap=m.annual_day_balanced_centroids([m.Fix('D',2019,1,1,0.,179.5),
                                              m.Fix('D',2019,1,2,0.,-179.5),
                                              m.Fix('E',2019,1,1,0.,180.)])
        self.assertLess(m.centroid_distance_km(wrap[2019]['D'],wrap[2019]['E']),1e-5)

    def test_nearby_dyad_risk_set_is_nested(self):
        events=[]
        for month in (1,2,6,7):
            for day in range(1,9):
                for a,lon in (('A',0.),('B',.1),('C',3.)):
                    events.append(m.Fix(a,2019,month,datetime(2019,month,day).toordinal(),0.,lon))
        out=m.compare_events(events,{})
        def pair_count(mode):
            return next(row['n_pairs'] for row in out if row['year']==2019 and row['window']=='winter_summer'
                        and row['grid_km']==5 and row['origin_x_fraction']==row['origin_y_fraction']==0
                        and row['risk_set_mode']==mode)
        self.assertEqual(pair_count('source_wide'),3)
        self.assertEqual(pair_count('near_centroid_25km'),1)
        self.assertEqual(pair_count('near_centroid_50km'),1)
        self.assertEqual(pair_count('near_centroid_100km'),1)
        self.assertEqual(pair_count('same_reference_label'),0)

    def test_all_grid_scenarios_always_report_missing_as_status(self):
        comparison=m.compare_events([], {})
        self.assertEqual(len(comparison),len(m.YEARS)*len(m.WINDOWS)*16*5)
        self.assertTrue(all(x['status']=='NOT_ESTIMABLE_NO_MATCHED_DYADS' for x in comparison))
        self.assertEqual(set(m.SOURCES),{'black_bear','turkey','moose','moose_snowy_range','white_tailed_deer'})


if __name__=='__main__': unittest.main()
