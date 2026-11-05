import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from screen_turkey_month_support_v1 import screen

class MonthGate(unittest.TestCase):
    def rows(self,months):
        return [{'BirdID':str(a),'timestamp':f'2020-{m:02d}-{d:02d} 12:00:00'} for a in range(4) for m in months for d in range(1,8)]
    def test_april_cannot_replace_february(self):
        r=screen(self.rows([4]))
        self.assertEqual(r['primary_time_gate'][0]['status'],'STOP_NO_FEBRUARY_OBSERVATIONS')
    def test_seven_days_are_not_seven_rows(self):
        r=screen(self.rows([2,4])[:1]*100)
        self.assertEqual(r['primary_time_gate'][0]['status'],'STOP_FEWER_THAN_FOUR_PAIRED_ANIMALS')
    def test_calendar_gate_does_not_claim_independence(self):
        r=screen(self.rows([2,4]))
        self.assertEqual(r['primary_time_gate'][0]['status'],'TIME_SUPPORT_PASSES_ONLY_NOT_SOURCE_OR_POPULATION_VALIDATION')
        self.assertFalse(r['spatial_outcomes_computed'])
