"""Synthetic source animal seasonal center and disconnected graph contracts."""
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
import math
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import seasonal_gps_centroid_components_v1 as sub
import source_spatial_influence_v1 as source


@dataclass(frozen=True)
class FakeFix:
    animal: str
    year: int
    month: int
    day: int
    lat: float
    lon: float


def seasonal_fixed_animals(*, one_winter_month=False, longitude_wrap=False):
    xs=[]
    winter=(1,) if one_winter_month else (1,2)
    months=winter+(6,7)
    for animal in ('a','b'):
        for m in months:
            for d in range(1,9):
                if longitude_wrap:
                    lon=179.8 if animal=='a' else -179.8
                elif m in winter:
                    lon=0
                else:
                    lon=0 if animal=='a' else .1
                for k in range(2):
                    xs.append(FakeFix(animal,2019,m,20190000+m*100+d,
                                      k*.00001,lon))
    return xs


class TestSeasonalCentroidComponents(unittest.TestCase):
    def test_daily_normalized_spherical_center_valid_and_seasonally_different(self):
        centers=sub.seasonal_day_equal_centroids(seasonal_fixed_animals())
        self.assertEqual(len(centers),4)
        paired={('a','b')}
        stats=sub._summarize_season_centroid_distances(paired,2019,centers)
        self.assertEqual(stats['n_source_pairs_with_both_season_centers'],1)
        self.assertAlmostEqual(stats['winter_km']['mean'],0,places=5)
        self.assertGreater(stats['summer_km']['mean'],10)
        self.assertEqual(stats['n_pairs_winter_centers_closer'],1)
        self.assertLess(stats['winter_minus_summer_km']['mean'],0)

    def test_longitude_wraparound_correct(self):
        centers=sub.seasonal_day_equal_centroids(
            seasonal_fixed_animals(longitude_wrap=True))
        stats=sub._summarize_season_centroid_distances({('a','b')},2019,centers)
        self.assertLess(stats['winter_km']['mean'],60)
        self.assertLess(stats['summer_km']['mean'],60)

    def test_season_without_two_months_is_not_estimated_not_zero_distance(self):
        centers=sub.seasonal_day_equal_centroids(
            seasonal_fixed_animals(one_winter_month=True))
        self.assertEqual(len(centers),2)
        stats=sub._summarize_season_centroid_distances({('a','b')},2019,centers)
        self.assertEqual(stats['status'],'NOT_ESTIMABLE_SOURCE_SEASON_CENTER_SUPPORT')
        self.assertEqual(stats['n_unavailable_source_pair_season_centers'],1)
        self.assertIsNone(stats['winter_km'])
        self.assertIsNone(stats['fraction_pairs_winter_centers_closer'])

    def test_geographically_disconnected_anonymous_pair_graph(self):
        pairs=set(combinations('abcde',2))|set(combinations('fghij',2))
        components=sub._components(pairs)
        self.assertEqual(len(components),2)
        self.assertEqual([len(c[0]) for c in components],[5,5])
        self.assertEqual([len(c[1]) for c in components],[10,10])
        self.assertEqual(sum(len(edges) for _,edges in components),20)

    def test_components_with_two_animals_or_few_edges_are_stop(self):
        pairs={('a','b')}
        parts=sub._components(pairs)
        self.assertEqual(len(parts),1)
        score=source._summary_for_edges({},parts[0][1])
        self.assertEqual(score['status'],
           'NOT_ESTIMABLE_INSUFFICIENT_WITHIN_SOURCE_PAIR_SUPPORT')

    def test_all_pairwise_closer_fractions_and_quantiles_consistent(self):
        centers=sub.seasonal_day_equal_centroids(seasonal_fixed_animals())
        stats=sub._summarize_season_centroid_distances({('a','b')},2019,centers)
        self.assertEqual(stats['n_pairs_winter_centers_closer'],1)
        self.assertEqual(stats['fraction_pairs_winter_centers_closer'],1)
        self.assertAlmostEqual(stats['winter_km']['q10'],
                               stats['winter_km']['q90'])
        self.assertAlmostEqual(stats['summer_km']['q10'],
                               stats['summer_km']['q90'])

    def test_signed_geography_categories_do_not_require_false_significance(self):
        self.assertEqual(sub.RADII,(.5,1.,2.))
        self.assertEqual(sub.THRESHOLDS,(5.,10.,25.))
        self.assertEqual(sub.TIME_TOLS,(900,1800))
        self.assertEqual(len(sub.SEEDS),12)


if __name__=='__main__':
    unittest.main()
