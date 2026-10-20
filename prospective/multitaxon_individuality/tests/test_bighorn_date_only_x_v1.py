"""Synthetic source-date recovery checks. No animal tracking data."""
import csv
from datetime import datetime
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from bighorn_date_only_x_v1 import date_only, source_rows


class TestDateOnly(unittest.TestCase):
    def test_invalid_seconds_suffix_preserves_day_without_guessing_second(self):
        y,m,d=date_only('2019-01-19 22:05:4S')
        self.assertEqual((y,m,d),(2019,1,datetime(2019,1,19).toordinal()))
        self.assertNotEqual(d,datetime(2019,1,20).toordinal())

    def test_unexpected_or_impossible_source_dates_rejected(self):
        for t in ('2019-02-30 01:02:4S','2019-01-01 01:02:45','2019-01-01 01:02:4Z',
                  '2019-01-01 01:02:SS','2019-01-01 01:02:4S extra','2019-01-01 01:02:4S+00'):
            with self.subTest(timestamp=t),self.assertRaises(ValueError):
                date_only(t)

    def test_source_reader_keeps_independent_raw_timestamp_keys(self):
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);gps=folder/'gps.csv';ref=folder/'ref.csv'
            with ref.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=['animal-id','tag-id']);w.writeheader()
                w.writerow({'animal-id':'a','tag-id':'t'})
            rows=[]
            for i,t in enumerate(('2019-01-01 01:00:0S','2019-01-01 01:05:0S',
                                   '2019-01-01 01:00:0S','2019-01-01 02:00:0S')):
                rows.append({'individual-local-identifier':'a','tag-local-identifier':'t',
                             'sensor-type':'gps','visible':'true','individual-taxon-canonical-name':'Alces alces',
                             'location-long':str(i if i==3 else 0),'location-lat':'0','timestamp':t})
            with gps.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
            events,audit=source_rows([(gps,'gps.csv')],(ref,'ref.csv'))
            self.assertEqual(len(events),3)
            self.assertEqual(audit['exact_duplicate_removed'],1)
            self.assertEqual(audit['malformed_date_or_position_removed'],0)
            self.assertFalse(audit['seconds_imputed'])
            self.assertFalse(audit['full_timestamp_or_utc_verified'])
            self.assertTrue(all(x[3]==datetime(2019,1,1).toordinal() for x in events))


if __name__=='__main__':unittest.main()