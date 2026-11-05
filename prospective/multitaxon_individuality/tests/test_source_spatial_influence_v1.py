"""Synthetic original-GPS topology, reused subject and individual-influence contracts.

Never uses raw published study positions, exact source dates, original IDs or
animal site locations. Source-specific real results are checked in the
original-data workflow via exact prior whole-GPS output replay.
"""
from __future__ import annotations

from datetime import datetime
from itertools import combinations
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import source_spatial_influence_v1 as mod
import day_shift_preserved_trajectory_v1 as day


def fake_byday(animals=('a','b','c'),months=(1,2,6,7,12),days=range(1,11)):
    out={}
    for m in months:
        for d in days:
            ordinal=datetime(2019,m,d).toordinal()
            for animal in animals:
                out[(2019,m,animal,ordinal)]=tuple(
                    (3600+7200*k,.001,(d+k/10)/111.32) for k in range(3))
    return out


class TestSourceSpatialInfluence(unittest.TestCase):
    def test_connected_components_split_known_disconnected_graph(self):
        edges={('a','b'),('a','c'),('b','c'),('d','e')}
        result=mod._component_counts(edges)
        self.assertEqual(result['n_connected_components'],2)
        self.assertEqual(result['component_animal_counts'],[3,2])
        self.assertEqual(result['component_dyad_counts'],[3,1])
        self.assertEqual(result['n_component_pairs_sum'],len(edges))
        self.assertEqual(result['n_components_meeting_3_animals_and_8_dyads'],0)

    def test_connected_components_one_large_cluster_not_independent_replicates(self):
        a='abcdef'
        edges=set(combinations(a,2))
        result=mod._component_counts(edges)
        self.assertEqual(result['n_connected_components'],1)
        self.assertEqual(result['component_animal_counts'],[6])
        self.assertEqual(result['component_dyad_counts'],[15])
        self.assertEqual(result['n_components_meeting_3_animals_and_8_dyads'],1)

    def test_fixed_dyad_weights_AND_source_animal_LOO(self):
        animals='abcdef'
        pairs=set(combinations(animals,2))
        values={}
        for di in mod.DIRECTIONS:
            for pair in pairs:
                for seed in mod.SEEDS:
                    for radius in mod.RADII_KM:
                        values[(di,pair,seed,radius)]=.025+(seed/50000)
        checks=mod._summary_for_edges(values,pairs)
        self.assertEqual(checks['n_pairs'],15)
        self.assertEqual(checks['n_animals'],6)
        self.assertEqual(len(checks['radii']),6)
        self.assertTrue(all(x['seed_signs']['positive']==12 for x in checks['radii']))
        loo=mod._loo(values,pairs)
        self.assertEqual(len(loo),6)
        for x in loo:
            self.assertEqual(x['n_animal_deletions_attempted'],6)
            self.assertEqual(x['n_estimable_animal_deletions'],6)
            self.assertEqual(x['n_omissions_with_positive_mean'],6)
            self.assertTrue(x['all_valid_omissions_positive_10_of_12'])

    def test_minimum_source_pair_support_never_treats_missing_as_zero(self):
        edges=set(combinations('abcd',2))
        result=mod._summary_for_edges({},edges)
        self.assertEqual(result['status'],
                         'NOT_ESTIMABLE_INSUFFICIENT_WITHIN_SOURCE_PAIR_SUPPORT')
        self.assertEqual(result['n_pairs'],6)
        self.assertEqual(result['radii'],[])
        loo=mod._loo({},edges)
        self.assertTrue(all(x['n_estimable_animal_deletions']==0 for x in loo))
        self.assertTrue(all(x['source_animal_loo_delta_mean_range'] is None for x in loo))

    def test_animal_influence_removes_incident_pair_edges(self):
        animals='abcdef'
        pairs=set(combinations(animals,2))
        values={}
        for di in mod.DIRECTIONS:
            for pair in pairs:
                for seed in mod.SEEDS:
                    for radius in mod.RADII_KM:
                        values[(di,pair,seed,radius)]=-1 if 'a' in pair else .2
        base=mod._summary_for_edges(values,pairs)
        self.assertLess(base['radii'][0]['winter_minus_summer_L_mean'],0)
        loo=mod._loo(values,pairs)
        r=loo[0]
        self.assertEqual(r['n_omissions_with_positive_mean'],1)
        self.assertEqual(r['n_omissions_with_at_least_10_of_12_positive_source_draws'],1)
        self.assertAlmostEqual(r['source_animal_loo_delta_mean_range'][1],.2)

    def test_full_original_dyad_sampling_reproduced_by_one_dyad_at_a_time(self):
        byday=fake_byday()
        original_pairs=set(combinations('abc',2))
        forward=day.eligible_day_shift(byday,original_pairs,2019,900)
        backward=day.eligible_day_shift(
            byday,{(b,a) for a,b in original_pairs},2019,900)
        self.assertEqual(len(forward),3)
        self.assertEqual(len(backward),3)
        pinned=[]
        for seed in mod.SEEDS:
            for name,pairs in (
                (mod.DIRECTIONS[0],forward),
                (mod.DIRECTIONS[1],backward),
            ):
                for row in day._one_seed(pairs,'turkey',2019,900,seed):
                    pinned.append({'direction':name,**row})
        per_pair=mod._per_pair_and_replay(
            forward,backward,'turkey',2019,900,pinned)
        self.assertEqual(len(per_pair),2*3*12*3)
        source=mod._summary_for_edges(per_pair,original_pairs)
        self.assertEqual(source['n_pairs'],3)
        self.assertEqual(source['status'],
                         'NOT_ESTIMABLE_INSUFFICIENT_WITHIN_SOURCE_PAIR_SUPPORT')

    def test_year_subject_sets_and_pair_reuse_counts_distinct(self):
        one={('a','b'),('a','c'),('b','c')}
        two={('b','c'),('b','d')}
        self.assertEqual(len(mod._animals(one)&mod._animals(two)),2)
        self.assertEqual(len(one&two),1)

    def test_source_sign_count_zero_is_separate_from_negative(self):
        self.assertEqual(mod.signs((.1,0,-.1,1e-15)),
                         {'positive':1,'negative':1,'near_zero':2})


if __name__ == '__main__':
    unittest.main()
