"""Independent output validation with no private original GPS."""
import importlib
from pathlib import Path
import sys
import unittest
from datetime import datetime

sys.path.insert(0,str(Path(__file__).resolve().parent))
# Reuse the previous adapter only for local standalone tests.
import test_cross_source_seasonal_x_v2 as tests
import cross_source_seasonal_x_v2 as x
import validate_cross_source_seasonal_x_v2 as v


class ValidateAggregateTests(unittest.TestCase):
    def document(self):
        events=[]
        for m in (1,2,6,7):
            for d in range(1,9):
                for a in ('A','B','C'):
                    xpos=.1 if a=='A' or (a=='B' and m<6) or (a=='C' and m>=6) else 20.1
                    events.append(x.Fix(a,2019,m,datetime(2019,m,d).toordinal(),.1/111.32,xpos/111.32))
        rows=x.compare_events(events,{'A':'s','B':'s','C':'s'})
        return {'schema_version':2,'status':'EXPLORATORY_NOT_CROSS_TAXON_INFERENCE',
                'source':{'label':'turkey','status':'COMPLETE_EXPLORATORY_GEOGRAPHIC_X',
                          'estimable_rows':sum(r['status']=='DESCRIPTIVE_MATCHED_DYADS' for r in rows),
                          'file_receipts':[{'md5_verified':True}], 'comparisons':rows}}

    def test_complete_grid_and_identity(self):
        data=self.document()
        r=v.validate_document(data)
        self.assertEqual(r['scenarios_verified'],320)
        self.assertGreater(r['matched_scenarios'],0)

    def test_missing_scenario_and_broken_counts_rejected(self):
        data=self.document()
        data['source']['comparisons'].pop()
        with self.assertRaisesRegex(AssertionError,'incomplete'):
            v.validate_document(data)
        data=self.document()
        supported=next(row for row in data['source']['comparisons'] if row['n_pairs']>0)
        supported['dyad_states']['neither']+=1
        with self.assertRaisesRegex(AssertionError,'partition'):
            v.validate_document(data)

    def test_no_md5_never_passes_as_source_verified(self):
        data=self.document()
        data['source']['file_receipts'][0]['md5_verified']=False
        with self.assertRaisesRegex(AssertionError,'MD5'):
            v.validate_document(data)

    def test_no_data_is_not_zero_evidence(self):
        data=self.document()
        data['source']['status']='NOT_ESTIMABLE_MATCHED_SEASONAL_DYADS'
        data['source']['comparisons']=x.compare_events([], {})
        data['source']['estimable_rows']=0
        r=v.validate_document(data)
        self.assertEqual(r['matched_scenarios'],0)

if __name__=='__main__':
    unittest.main()
