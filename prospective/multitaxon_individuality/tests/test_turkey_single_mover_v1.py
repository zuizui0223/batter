"""Synthetic-only contracts: unique annual5 GPS graph outsider and seasonal motion."""
from __future__ import annotations

from itertools import combinations
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import turkey_single_mover_v1 as m
import turkey_component_season_centers_v1 as seasonal


class TestOriginalTurkeySingleMoverGeometry(unittest.TestCase):
    def test_six_core_animals_fourteen_edges_and_one_outsider(self):
        names=tuple("abcdefg")
        allpairs=set(combinations(names,2))
        self.assertEqual(len(allpairs),21)
        # Six annual-center core animals have 14 / 15 close graph pairs.
        inside={p for p in allpairs if 'g' not in p and p!=('e','f')}
        self.assertEqual(len(inside),14)
        comps=seasonal._components(inside)
        self.assertEqual([(len(a),len(e)) for a,e in comps],[(6,14)])
        core=comps[0][0]
        out=set(names)-core
        self.assertEqual(out,{'g'})
        hub='g'
        outside={p for p in allpairs if hub in p}
        self.assertEqual(len(outside),6)
        non5=allpairs-inside
        self.assertEqual(len(non5),7)
        self.assertEqual(len(non5&outside),6)

    def test_10_to25_km_far_edges_have_at_least_four_common_incident_edges(self):
        names=tuple("abcdefg")
        allpairs=set(combinations(names,2))
        core=set("abcdef"); hub='g'
        near5={p for p in allpairs if p[0] in core and p[1] in core
               and p!=('e','f')}
        outside=allpairs-near5
        self.assertEqual(len(outside),7)
        for far5 in combinations(sorted(outside),5):
            self.assertGreaterEqual(sum(hub in p for p in far5),4)

    def test_pair_centroid_summaries_nonzero_geographic_change(self):
        annual={2020:{'a':seasonal._xyz(0,0),'b':seasonal._xyz(0,1)}}
        early={2020:{'a':seasonal._xyz(0,0),'b':seasonal._xyz(0,.001)}}
        summer={2020:{'a':seasonal._xyz(0,0),'b':seasonal._xyz(0,1)}}
        summary=m._pair_annual_season_stats({('a','b')},annual,early,summer,2020)
        self.assertEqual(summary['n_original_source_pairs'],1)
        self.assertEqual(summary['n_source_pairs_closer_in_jan_feb'],1)
        self.assertLess(summary['jan_feb_centroid_separation_km']['median'],
                        summary['summer_centroid_separation_km']['median'])
        self.assertLess(summary['jan_feb_minus_summer_distance_km']['mean'],0)

    def test_incomplete_season_centres_mark_missing_not_no_difference(self):
        annual={2020:{'a':seasonal._xyz(0,0),'b':seasonal._xyz(0,1)}}
        early={2020:{'a':seasonal._xyz(0,0)}}
        summer={2020:{'a':seasonal._xyz(0,0),'b':seasonal._xyz(0,1)}}
        summary=m._pair_annual_season_stats({('a','b')},annual,early,summer,2020)
        self.assertEqual(summary['n_without_both_supported_source_season_centers'],1)
        self.assertIsNone(summary['jan_feb_centroid_separation_km']['median'])
        self.assertEqual(summary['jan_feb_centroid_separation_km']['n'],0)

    def test_single_individual_seasonal_shift_is_distinct_from_pair_replicates(self):
        early={2020:{'a':seasonal._xyz(0,0),'b':seasonal._xyz(0,.1),
                     'c':seasonal._xyz(0,.2)}}
        summer={2020:{'a':seasonal._xyz(0,10),'b':seasonal._xyz(0,.1),
                       'c':seasonal._xyz(0,.2)}}
        m1=m._individual_seasonal_movement({'a'},early,summer,2020)
        cores=m._individual_seasonal_movement({'b','c'},early,summer,2020)
        self.assertGreater(m1['median'],1000)
        self.assertLess(cores['median'],.001)
        self.assertEqual((m1['n'],cores['n']),(1,2))

    def test_empty_december_is_unavailable_not_zero_distance(self):
        early={2020:{'a':seasonal._xyz(0,0)}}
        summer={2020:{'a':seasonal._xyz(0,1)}}
        empty={}
        result=m._individual_seasonal_movement({'a'},empty,summer,2020)
        self.assertEqual(result['n'],0)
        self.assertIsNone(result['median'])


if __name__=='__main__':
    unittest.main()
