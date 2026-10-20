"""Synthetic overlap topology checks and checksum-pinned aggregate regression."""
from pathlib import Path
import unittest
from validate_edge_topology_v1 import edge_statistics, verify_zip


def example(first, second):
    assert len(first)==len(second)
    n=len(first)
    both=sum(a>0 and b>0 for a,b in zip(first,second))
    only1=sum(a>0 and b==0 for a,b in zip(first,second))
    only2=sum(a==0 and b>0 for a,b in zip(first,second))
    neither=n-both-only1-only2
    p=(both+only1)/n
    q=(both+only2)/n
    v1=sum(first)/n
    v2=sum(second)/n
    st1=v1/p if p else None
    st2=v2/q if q else None
    inc=(p-q)*(st1+st2)/2 if p and q else None
    strength=(st1-st2)*(p+q)/2 if p and q else None
    return {'status':'DESCRIPTIVE_MATCHED_DYADS','n_pairs':n,
        'dyad_states':{'both':both,'neither':neither,'season1_only':only1,'season2_only':only2},
        'season1':{'positive_pairs':both+only1,'positive_fraction':p,'mean_X':v1,'positive_strength':st1},
        'season2':{'positive_pairs':both+only2,'positive_fraction':q,'mean_X':v2,'positive_strength':st2},
        'difference_season1_minus_season2':v1-v2,'incidence_component':inc,'positive_strength_component':strength}


class TestEdgeTopology(unittest.TestCase):
    def test_same_mean_and_positive_fraction_can_hide_opposite_pair_retention(self):
        winter=[.5,.5,0,0]
        stable=edge_statistics(example(winter,[.5,.5,0,0]))
        replaced=edge_statistics(example(winter,[0,0,.5,.5]))
        for name in ('mean_first','mean_second','incidence','strength','delta'):
            self.assertAlmostEqual(stable[name],replaced[name])
        self.assertEqual((stable['jaccard'],replaced['jaccard']),(1,0))
        self.assertEqual((stable['phi'],replaced['phi']),(1,-1))

    def test_exact_additive_decomposition(self):
        row=edge_statistics(example([.3,.1,0,0],[.2,0,0,.1]))
        self.assertAlmostEqual(row['delta'],.025)
        self.assertAlmostEqual(row['incidence']+row['strength'],row['delta'])
        self.assertEqual((row['both'],row['only_first'],row['only_second'],row['neither']),(1,1,1,1))
        self.assertAlmostEqual(row['jaccard'],1/3)

    def test_all_zero_edges_do_not_have_zero_turnover(self):
        row=edge_statistics(example([0,0],[0,0]))
        self.assertIsNone(row['jaccard'])
        self.assertIsNone(row['phi'])
        self.assertIsNone(row['strength'])
        self.assertEqual(row['delta'],0)

    def test_missing_conditional_strength_not_imputed(self):
        row=edge_statistics(example([0,0,0],[.2,0,0]))
        self.assertIsNone(row['incidence'])
        self.assertIsNone(row['strength'])
        self.assertEqual(row['jaccard'],0)

    def test_corrupt_aggregate_rejected(self):
        bad=example([.6,0],[.2,.1])
        bad['dyad_states']['season2_only']=2
        with self.assertRaises(AssertionError):
            edge_statistics(bad)
        bad=example([.6,0],[.2,.1])
        bad['season1']['mean_X']+=.1
        with self.assertRaises(AssertionError):
            edge_statistics(bad)

    def test_all_1280_original_source_scenarios_reconciled(self):
        archive=Path(__file__).resolve().parents[1]/'CROSS_SOURCE_NEARBY_DYAD_V2_FULL_AGGREGATES_2026_10_20.zip'
        result=verify_zip(archive)
        self.assertEqual((result['n_groups'],result['n_settings'],result['n_stopped_sources']),(80,1280,1))
        self.assertEqual(len(result['focus']),5)
        by={(r['source'],r['year']):r for r in result['focus']}
        self.assertEqual(by[('black_bear',2020)]['reference']['only_second'],10)
        self.assertEqual(by[('white_tailed_deer',2020)]['signs16']['incidence']['1'],16)
        self.assertEqual(by[('white_tailed_deer',2020)]['signs16']['strength']['-1'],16)
        self.assertEqual(by[('turkey',2020)]['signs16']['delta']['1'],16)
        self.assertEqual(by[('turkey',2020)]['reference']['second_already_in_first'],1)


if __name__=='__main__':
    unittest.main()
