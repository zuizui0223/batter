import unittest
from collections import defaultdict
from itertools import combinations
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import turkey_core_effort_influence_v1 as f

class Diagnostics(unittest.TestCase):
    def daily(self,mode):
        d=defaultdict(dict)
        for m in (2,3,4,6,7):
            for a in range(6):
                for day in range(1,29):
                    lon=a*.001
                    if mode=='distributed' and m!=2:lon*=3
                    if mode=='single' and m!=2 and a==5:lon+=.1
                    d[(2020,m,str(a))][day]=f.geo._xyz(0,lon)
        return d
    def diagnostic(self,mode):
        names=list(map(str,range(6)))
        return f.group_diagnostics(2020,names,list(combinations(names,2)),self.daily(mode))
    def test_stationary_core_not_changed_by_calendar(self):
        r=self.diagnostic('stationary')
        self.assertEqual(r['balanced_summary']['apr_minus_feb']['whole_group']['maximum'],0)
    def test_distributed_expansion_survives_all_deletions(self):
        r=self.diagnostic('distributed')
        self.assertGreater(r['balanced_summary']['apr_minus_feb']['worst_animal_deletion']['minimum'],0)
        self.assertEqual(r['balanced_summary']['apr_minus_feb']['whole_group']['n'],24)
    def test_single_animal_expansion_detected_by_deletion(self):
        r=self.diagnostic('single')
        self.assertGreater(r['balanced_summary']['apr_minus_feb']['whole_group']['minimum'],0)
        self.assertEqual(r['balanced_summary']['apr_minus_feb']['worst_animal_deletion']['minimum'],0)
    def test_missing_common_dates_stop(self):
        d=self.daily('distributed');d[(2020,4,'0')]={k:v for k,v in d[(2020,4,'0')].items() if k<7}
        r=f.group_diagnostics(2020,list(map(str,range(6))),list(combinations(map(str,range(6)),2)),d)
        self.assertEqual(r['status'],'STOP_COMMON_DAY_SUPPORT')

if __name__=='__main__':unittest.main()
