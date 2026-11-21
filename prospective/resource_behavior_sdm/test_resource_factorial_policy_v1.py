"""Known-truth resource × state × height tests, not biological results."""
import math
import unittest

from resource_factorial_policy_v1 import (
    factorial_resource_use_models, score_resource_factorial,
)
from resource_behavior_sdm import project_horizontal_time


def factory(r0=1.0):
    ht={("cell","early"):0.0,("cell","late"):0.0}
    r={("cell","early"):r0,("cell","late"):-r0}
    states={
      ("i","cell","early"):{"forage":0.0,"commute":0.0},
      ("i","cell","late"):{"forage":0.0,"commute":0.0},
    }
    heights={
      ("i","cell",time,state):{"low":0.0,"high":0.0}
      for time in ("early","late") for state in ("forage","commute")
    }
    return factorial_resource_use_models(
      ht,{"i":1.0},states,heights,r,
      {"forage":2.0,"commute":-2.0},
      {"forage":{"low":-1.0,"high":1.0},
       "commute":{"low":0.0,"high":0.0}},
    )


class FactorialResourcePolicyTests(unittest.TestCase):
    def test_horizontal_marginal_exactly_unchanged(self):
        m=factory()
        base=project_horizontal_time(m["base"])
        for name,v in m.items():
            self.assertEqual(set(project_horizontal_time(v)),set(base))
            for key,p in base.items():
                self.assertAlmostEqual(project_horizontal_time(v)[key],p)

    def test_allocation_channel_and_height_channel_separable(self):
        e=[("i","cell","early","forage","high")]
        joint=score_resource_factorial(factory(),e,"state_height")
        self.assertGreater(joint["state_allocation_increment_nats_per_event"],0)
        self.assertGreater(joint["within_state_height_increment_nats_per_event"],0)
        self.assertGreater(joint["joint_increment_nats_per_event"],0)
        self.assertIsNone(joint["field_biological_resource_effect"])
        height=score_resource_factorial(factory(),e,"height")
        # If state-height kernels stay 50/50, mere state reallocation
        # cannot change a height-only heldout score.
        self.assertAlmostEqual(height["state_allocation_increment_nats_per_event"],0)
        self.assertGreater(height["within_state_height_increment_nats_per_event"],0)

    def test_wrong_resource_context_hurts_predictive_score(self):
        e=[("i","cell","early","forage","high")]
        wrong=score_resource_factorial(factory(-1),e,"state_height")
        self.assertLess(wrong["joint_increment_nats_per_event"],0)

    def test_no_pseudocount_rescue(self):
        with self.assertRaisesRegex(ValueError,"STOP_UNMATCHED_HELDOUT_SUPPORT"):
            score_resource_factorial(
              factory(),[("unknown","cell","early","forage","high")],"height"
            )

    def test_incorrect_candidate_list_stops(self):
        with self.assertRaises(ValueError):
            score_resource_factorial({"base":factory()["base"]},
                [("i","cell","early","forage","high")],"height")

    def test_missing_resource_and_height_response_stop(self):
        from resource_factorial_policy_v1 import resource_conditioned_height_policies
        logits={("i","A","t","forage"):{"low":0,"high":0}}
        with self.assertRaises(ValueError):
            resource_conditioned_height_policies(logits,{},{"forage":{"low":1,"high":-1}})
        with self.assertRaises(ValueError):
            resource_conditioned_height_policies(logits,{("A","t"):1},{"forage":{"low":1}})
        with self.assertRaises(ValueError):
            resource_conditioned_height_policies(logits,{("A","t"):float("nan")},
                     {"forage":{"low":1,"high":-1}})

    def test_finite_scores_and_arithmetic_nonadditivity(self):
        r=score_resource_factorial(factory(),
             [("i","cell","early","forage","high")],"state_height")
        self.assertEqual(r["n_events"],1)
        self.assertTrue(math.isfinite(r["score_nonadditivity_nats_per_event"]))
        self.assertAlmostEqual(
             r["joint_increment_nats_per_event"],
             r["state_allocation_increment_nats_per_event"]+
             r["within_state_height_increment_nats_per_event"]+
             r["score_nonadditivity_nats_per_event"]
        )


if __name__=="__main__": unittest.main()
