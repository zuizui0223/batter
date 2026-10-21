"""Synthetic only: dyad anchoring reversal and original path-order controls."""
from datetime import datetime
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import day_shift_preserved_trajectory_v1 as day


def fake_days(animals=('a','b'), months=(1,2,6,7,12), days=range(1,11),
              spacing_km=4.0, omit_a_days=()):
    rows={}
    for m in months:
        for d in days:
            ordinal=datetime(2019,m,d).toordinal()
            for a in animals:
                if a=='a' and d in omit_a_days:continue
                positions=tuple((float(3600+7200*k),.001,
                    spacing_km*d/111.32) for k in range(3))
                rows[(2019,m,a,ordinal)]=positions
    return rows


class TestReverseAnchorDesign(unittest.TestCase):
    def test_reverse_pair_membership_is_symmetric_when_original_support_is_symmetric(self):
        src=fake_days()
        a=day.eligible_day_shift(src,{('a','b')},2019,900)
        b=day.eligible_day_shift(src,{('b','a')},2019,900)
        self.assertEqual(len(a),1)
        self.assertEqual(len(b),1)
        self.assertEqual(set(a),{('a','b')})
        self.assertEqual({(y,x) for x,y in b},set(a))

    def test_unequal_original_fix_day_support_can_make_directional_eligibility_differ(self):
        src=fake_days(omit_a_days=(1,10))
        # A has GPS on days 2..9, B on 1..10:
        # A->B has 8 eligible anchor days; B->A only 6.
        forward=day.eligible_day_shift(src,{('a','b')},2019,900)
        reverse=day.eligible_day_shift(src,{('b','a')},2019,900)
        self.assertEqual(len(forward),1)
        self.assertEqual(len(reverse),0)
        self.assertEqual(set(forward) & {(b,a) for a,b in reverse},set())

    def test_same_animals_with_reversed_anchor_can_have_identical_response_when_tracks_match(self):
        src=fake_days()
        first=day.eligible_day_shift(src,{('a','b')},2019,900)
        second=day.eligible_day_shift(src,{('b','a')},2019,900)
        out1=day._one_seed(first,'turkey',2019,900,0)
        out2=day._one_seed(second,'turkey',2019,900,0)
        self.assertEqual(len(out1),len(out2))
        for r1,r2 in zip(out1,out2):
            self.assertEqual(r1['radius_km'],r2['radius_km'])
            self.assertEqual(r1['n_dyads'],1)
            self.assertEqual(r1['winter_minus_summer']['same_minus_adjacent'],0)
            self.assertEqual(r2['winter_minus_summer']['same_minus_adjacent'],0)
            self.assertEqual(r1['winter']['same'],r2['winter']['same'])
            self.assertEqual(r1['winter']['previous_day'],r2['winter']['previous_day'])

    def test_common_original_pair_set_is_pre_score_intersection(self):
        src=fake_days(animals=('a','b','c'),omit_a_days=(1,10))
        pairs={('a','b'),('a','c'),('b','c')}
        forward=day.eligible_day_shift(src,pairs,2019,900)
        reverse=day.eligible_day_shift(src,{(b,a) for a,b in pairs},2019,900)
        common=set(forward) & {(b,a) for a,b in reverse}
        self.assertEqual(common,{('b','c')})
        self.assertEqual(len(forward),3)
        self.assertEqual(len(reverse),1)

    def test_15_minute_opportunity_nests_in_30_minute(self):
        src=fake_days()
        shifted={key: tuple((t+(1200 if key[2]=='b' else 0),lat,lon)
                    for t,lat,lon in positions) for key,positions in src.items()}
        for pair in ({('a','b')},{('b','a')}):
            self.assertEqual(len(day.eligible_day_shift(shifted,pair,2019,900)),0)
            self.assertEqual(len(day.eligible_day_shift(shifted,pair,2019,1800)),1)

    def test_source_month_and_year_boundary_not_bypassed(self):
        src=fake_days(months=(1,6,7))
        self.assertEqual(day.eligible_day_shift(src,{('a','b')},2019,900),{})
        src=fake_days()
        self.assertEqual(day.eligible_day_shift(src,{('a','b')},2020,900),{})


if __name__=='__main__':
    unittest.main()
