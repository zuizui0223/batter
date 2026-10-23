"""Synthetic and source-receipt tests for one animal appearing in 2020 5 long dyads.

No animal tag names, raw tracks, or coordinates are loaded by the tests.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import validate_turkey_single_mover_v1 as mod


def stat(n,minv,meanv,medianv,maxv):
    return {'n':n,'min':minv,'mean':meanv,'median':medianv,'max':maxv}


def group(n=5,shift=-3):
    return {'n_original_source_pairs':n,
        'n_without_both_supported_source_season_centers':0,
        'annual_centroid_separation_km':stat(n,2,3,3,5),
        'jan_feb_centroid_separation_km':stat(n,1,2,2,4),
        'summer_centroid_separation_km':stat(n,3,5,5,7),
        'jan_feb_minus_summer_distance_km':stat(n,-6,shift,-3,-1),
        'n_source_pairs_closer_in_jan_feb':n,
        'n_source_pairs_farther_in_jan_feb':0}


class TestTurkeys2020SingleMoverReceipt(unittest.TestCase):
    def test_distance_stats_validate_negative_delta_but_not_negative_length(self):
        mod._size_stats(stat(3,-5,-3,-4,-1),3,signed=True)
        with self.assertRaises(AssertionError):
            mod._size_stats(stat(3,-5,-3,-4,-1),3,signed=False)

    def test_pair_group_checks_exact_mean_difference(self):
        mod._pair_group(group(),5,expected_closer=5)
        p=group(shift=-2)
        with self.assertRaises(AssertionError):
            mod._pair_group(p,5)

    def test_pair_support_not_imputed_as_zero(self):
        g=group()
        g['n_without_both_supported_source_season_centers']=1
        with self.assertRaises(AssertionError):
            mod._pair_group(g,5)

    def test_pair_count_and_closeness_tally(self):
        g=group()
        g['n_source_pairs_closer_in_jan_feb']=6
        with self.assertRaises(AssertionError):
            mod._pair_group(g,5)

    def test_source_sha256_matches_frozen_publisher_result(self):
        raw=mod._source_document(mod.HERE/mod.ORIGINAL_NAME)
        self.assertEqual(raw['source'],'turkey')
        self.assertEqual(raw['n_reused_original_animal_IDs_between_years'],0)
        self.assertTrue(raw['complete_original_source_MD5_SHA256_reference_verified'])

    def test_exact_original_anonymous_2019_component_reconciliation(self):
        result=mod.derive(mod.HERE/mod.ORIGINAL_NAME)
        comps=result['year_2019_components']
        self.assertEqual([(x['n_source_animals'],x['n_original_annual5_geographic_dyads']) for x in comps],
                         [(11,53),(7,20)])
        self.assertEqual([x['jan_feb_closer_than_summer_dyads'] for x in comps],[38,17])
        self.assertTrue(all(x['median_janfeb_pair_center_distance_km']
                            <x['median_summer_pair_center_distance_km'] for x in comps))

    def test_all_five_annulus_dyads_share_an_individual_not_five_replications(self):
        data=mod.derive(mod.HERE/mod.ORIGINAL_NAME)
        y=data['year_2020']
        self.assertEqual(y['n_annual10_to25km_pairs'],5)
        self.assertEqual(y['n_annual10_to25km_pairs_sharing_isolated_source_animal'],5)
        self.assertEqual(y['n_annual5_to25km_pairs_sharing_isolated_source_animal'],6)
        self.assertEqual(y['december_2020_supported_original_animals'],0)
        self.assertGreater(y['isolated_original_animal_janfeb_to_summer_center_shift_km'],
                           y['six_core_animal_source_shift_max_km'])
        self.assertGreater(y['isolated_shift_relative_to_core_median'],10)
        self.assertLess(y['annual10_to25km_pairs_janfeb_center_median_km'],
                        y['annual10_to25km_pairs_summer_center_median_km'])
        self.assertFalse(data['source_populations_independent_verified'])

    def test_any_changed_raw_source_receipt_is_rejected(self):
        import tempfile
        original=(mod.HERE/mod.ORIGINAL_NAME).read_text()
        data=json.loads(original)
        data['raw_animal_id']='PRIVATE_DO_NOT_PUBLISH'
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/mod.ORIGINAL_NAME
            target.write_text(json.dumps(data))
            with self.assertRaises(AssertionError):
                mod._source_document(target)


if __name__=='__main__':
    unittest.main()
