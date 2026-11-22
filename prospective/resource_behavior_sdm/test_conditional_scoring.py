"""Pure synthetic conditional prediction controls (never biological evidence)."""
import math
import unittest

from conditional_scoring import conditional_heldout_log_score, paired_conditional_gain
from resource_behavior_sdm import joint_use_distribution, project_horizontal


def scenario(own=0.9):
    return joint_use_distribution(
        {("cell", "night"): 0.0},
        {"ind1": 1.0, "ind2": 1.0},
        {("ind1", "cell", "night"): {"forage": 1.0},
         ("ind2", "cell", "night"): {"forage": 1.0}},
        {("ind1", "cell", "night", "forage"): {"low": own, "high": 1-own},
         ("ind2", "cell", "night", "forage"): {"low": 1-own, "high": own}},
    )


class TestConditionalScoring(unittest.TestCase):
    def setUp(self):
        self.events = [
            ("ind1", "cell", "night", "forage", "low"),
            ("ind2", "cell", "night", "forage", "high"),
        ]

    def test_conditional_gain_even_with_same_xy(self):
        own, pooled = scenario(.9), scenario(.5)
        self.assertEqual(project_horizontal(own), project_horizontal(pooled))
        self.assertAlmostEqual(
            paired_conditional_gain(own, pooled, self.events),
            math.log(.9/.5),
        )

    def test_policy_transfer_can_worsen_conditional_score(self):
        self.assertLess(
            paired_conditional_gain(scenario(.1), scenario(.5), self.events), 0
        )

    def test_one_state_three_targets_are_equivalent(self):
        for target in ("height", "state_height", "height_given_state"):
            self.assertAlmostEqual(
                conditional_heldout_log_score(scenario(.9), self.events, target),
                math.log(.9),
            )

    def test_state_mixture_must_not_be_confused_with_within_state_height(self):
        model = joint_use_distribution(
            {("A", "t"): 0.0}, {"i": 1.0},
            {("i", "A", "t"): {"forage": .8, "commute": .2}},
            {("i", "A", "t", "forage"): {"low": .9, "high": .1},
             ("i", "A", "t", "commute"): {"low": .1, "high": .9}},
        )
        events = [("i", "A", "t", "forage", "low")]
        self.assertAlmostEqual(
            conditional_heldout_log_score(model, events, "state_height"), math.log(.72)
        )
        self.assertAlmostEqual(
            conditional_heldout_log_score(model, events, "height"), math.log(.74)
        )
        self.assertAlmostEqual(
            conditional_heldout_log_score(model, events, "height_given_state"),
            math.log(.9),
        )

    def test_unseen_support_never_discarded(self):
        wrong = [("ind1", "cell", "night", "forage", "high")]
        self.assertEqual(conditional_heldout_log_score(scenario(1), wrong), -math.inf)
        with self.assertRaisesRegex(ValueError, "STOP_UNMATCHED_HELDOUT_SUPPORT"):
            paired_conditional_gain(scenario(1), scenario(.5), wrong)
        with self.assertRaisesRegex(ValueError, "STOP_UNMATCHED_HELDOUT_SUPPORT"):
            paired_conditional_gain(
                scenario(.9), scenario(.5),
                [("new_animal", "cell", "night", "forage", "low")]
            )

    def test_empty_bad_target_and_unnormalized_fail(self):
        with self.assertRaises(ValueError):
            conditional_heldout_log_score(scenario(), [])
        with self.assertRaises(ValueError):
            conditional_heldout_log_score(scenario(), self.events, "unknown")
        with self.assertRaises(ValueError):
            conditional_heldout_log_score({("i","x","t","b","z"):.8}, self.events)


if __name__ == "__main__":
    unittest.main()
