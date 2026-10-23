"""Source-locked and synthetic dyad numerator accounting, not a biological test."""
from __future__ import annotations
from pathlib import Path
import json
import math
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import turkey_dyad_accounting_v1 as mod


class TestSourceTurkeySignedAccounting(unittest.TestCase):
    def test_three_annuli_reconstitute_exact_original_mean(self):
        old={5:(14,-.02),10:(16,-.01),25:(21,.03)}
        d=mod.band_decompose(old,{5:14,10:16,25:21})
        self.assertAlmostEqual(d['whole_source']['winter_minus_summer_L_mean'],.03)
        self.assertEqual([v['n_original_dyads'] for v in d['annuli']],[14,2,5])
        self.assertAlmostEqual(d['annuli'][0]['signed_sum_over_dyads'],-.28)
        self.assertAlmostEqual(d['annuli'][1]['signed_sum_over_dyads'],+.12)
        self.assertAlmostEqual(d['annuli'][2]['signed_sum_over_dyads'],+.79)
        self.assertGreater(d['far10to25_fraction_of_signed_whole_source_sum'],1)
        self.assertTrue(d['annuli'][2]['below_minimum_eight_pair_standalone_biological_gate'])

    def test_signed_far_fraction_is_null_if_original_mean_zero(self):
        old={5:(14,-.01),10:(16,0),25:(21,0)}
        d=mod.band_decompose(old,{5:14,10:16,25:21})
        self.assertIsNone(d['far10to25_fraction_of_signed_whole_source_sum'])

    def test_all_original_source_year_gap_direction_radius_records(self):
        d=mod.derive()
        self.assertEqual(d['n_year_gap_orientation_radius_comparisons'],24)
        self.assertEqual(len(d['results']),24)
        self.assertEqual(set(x['year'] for x in d['results']),{2019,2020})
        self.assertEqual(set(x['time_tolerance_seconds'] for x in d['results']),{900,1800})
        self.assertTrue(d['year2020_one_animal_in_all_five_far10_to25km_dyads'])
        for entry in d['results']:
            self.assertAlmostEqual(sum(b['signed_sum_over_dyads'] for b in entry['annuli']),
                                   entry['whole_source']['signed_sum_over_dyads'])
            self.assertEqual(sum(b['n_original_dyads'] for b in entry['annuli']),
                             entry['whole_source']['n_original_dyads'])
            if entry['year']==2020:
                self.assertEqual([b['n_original_dyads'] for b in entry['annuli']],[14,2,5])

    def test_2020_source_500m_original_forward_five_far_dyads_exceed_net_signed_effect(self):
        d=mod.derive()
        row=next(x for x in d['results'] if
                 (x['year'],x['time_tolerance_seconds'],
                  x['geodesic_GPS_near_radius_km'],
                  x['animal_anchor_orientation'])==(2020,900,.5,'original_A_to_B'))
        self.assertGreater(row['whole_source']['winter_minus_summer_L_mean'],0)
        self.assertLess(row['annuli'][0]['winter_minus_summer_L_mean'],0)
        self.assertGreater(row['annuli'][2]['winter_minus_summer_L_mean'],0)
        self.assertGreater(row['far10to25_fraction_of_signed_whole_source_sum'],1)

    def test_current_2019_geographic_far_edge_annulus_has_no_five_pair_isolate_inference(self):
        d=mod.derive()
        row=next(x for x in d['results'] if
                 (x['year'],x['time_tolerance_seconds'],
                  x['geodesic_GPS_near_radius_km'],
                  x['animal_anchor_orientation'])==(2019,900,.5,'original_A_to_B'))
        self.assertEqual(row['whole_source']['n_original_dyads'],112)
        self.assertEqual([v['n_original_dyads'] for v in row['annuli']],[73,5,34])
        self.assertLess(abs(row['annuli'][2]['winter_minus_summer_L_mean']),1e-8)

    def test_reject_source_dyad_count_changes_and_invalid_effects(self):
        with self.assertRaises(AssertionError):
            mod.band_decompose({5:(14,.01),10:(16,.02),25:(22,.03)},
                               {5:14,10:16,25:21})
        with self.assertRaises(AssertionError):
            mod.band_decompose({5:(14,.01),10:(16,.02),25:(21,20)},
                               {5:14,10:16,25:21})

    def test_blobs_and_source SHA_are_git_content_addressed(self):
        src=mod.BASE/mod.INFLUENCE_NAME
        raw=src.read_bytes()
        self.assertEqual(mod.blob_sha(raw),mod.INFLUENCE_GIT_BLOB)
        self.assertNotEqual(mod.blob_sha(raw+b'bad'),mod.INFLUENCE_GIT_BLOB)


if __name__=='__main__':
    unittest.main()
