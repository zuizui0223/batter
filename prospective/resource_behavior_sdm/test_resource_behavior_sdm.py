"""Source-free unit tests; none are empirical bat or plant results."""
import math
import unittest

from resource_behavior_sdm import (
    detected_event_distribution,
    habitat_log_scores,
    identity_vertical_information,
    identity_vertical_information_given_state,
    resource_conditioned_state_policies,
    joint_use_distribution,
    mean_heldout_event_log_score,
    project_horizontal,
    project_horizontal_time,
)


def toy_vertical_strategy():
    """Two equally present toy individuals use distinct heights, same XY."""
    return joint_use_distribution(
        {("A", "night"): 0.0},
        {"I1": 1.0, "I2": 1.0},
        {
            ("I1", "A", "night"): {"forage": 1.0},
            ("I2", "A", "night"): {"forage": 1.0},
        },
        {
            ("I1", "A", "night", "forage"): {"low": 1.0},
            ("I2", "A", "night", "forage"): {"high": 1.0},
        },
    )


class ResourceBehaviorSDMTests(unittest.TestCase):
    def test_projection_integrity(self):
        use = toy_vertical_strategy()
        self.assertAlmostEqual(math.fsum(use.values()), 1.0)
        self.assertEqual(project_horizontal_time(use), {("A", "night"): 1.0})
        self.assertEqual(project_horizontal(use), {"A": 1.0})

    def test_individuality_without_horizontal_partition(self):
        """Mathematical possibility, not a bat mechanism or field result."""
        use = toy_vertical_strategy()
        by_individual = {
            individual: sum(p for (i, _, _, _, _), p in use.items() if i == individual)
            for individual in ("I1", "I2")
        }
        self.assertAlmostEqual(by_individual["I1"], 0.5)
        self.assertAlmostEqual(by_individual["I2"], 0.5)
        self.assertAlmostEqual(identity_vertical_information(use), math.log(2.0))

    def test_no_individuality_for_identical_vertical_policy(self):
        use = joint_use_distribution(
            {("A", "night"): 0.0},
            {"I1": 1.0, "I2": 1.0},
            {
                ("I1", "A", "night"): {"forage": 1.0},
                ("I2", "A", "night"): {"forage": 1.0},
            },
            {
                ("I1", "A", "night", "forage"): {"low": 0.25, "high": 0.75},
                ("I2", "A", "night", "forage"): {"low": 0.25, "high": 0.75},
            },
        )
        self.assertAlmostEqual(identity_vertical_information(use), 0.0, places=12)

    def test_behavioral_state_switches_without_extra_horizontal_cells(self):
        use = joint_use_distribution(
            {("A", "dusk"): 0.0, ("A", "night"): 0.0},
            {"I1": 1.0},
            {
                ("I1", "A", "dusk"): {"commute": 1.0},
                ("I1", "A", "night"): {"forage": 1.0},
            },
            {
                ("I1", "A", "dusk", "commute"): {"high": 1.0},
                ("I1", "A", "night", "forage"): {"low": 1.0},
            },
        )
        self.assertAlmostEqual(use[("I1", "A", "dusk", "commute", "high")], 0.5)
        self.assertAlmostEqual(use[("I1", "A", "night", "forage", "low")], 0.5)
        self.assertEqual(project_horizontal(use), {"A": 1.0})

    def test_behavioral_mixture_can_explain_individuality_without_partition(self):
        """Same vertical rule per state, different state proportions per bat."""
        use = joint_use_distribution(
            {("A", "t"): 0.0}, {"I1": 1.0, "I2": 1.0},
            {("I1", "A", "t"): {"forage": 0.8, "commute": 0.2},
             ("I2", "A", "t"): {"forage": 0.2, "commute": 0.8}},
            {("I1", "A", "t", "forage"): {"low": 0.2, "high": 0.8},
             ("I1", "A", "t", "commute"): {"low": 0.8, "high": 0.2},
             ("I2", "A", "t", "forage"): {"low": 0.2, "high": 0.8},
             ("I2", "A", "t", "commute"): {"low": 0.8, "high": 0.2}},
        )
        self.assertAlmostEqual(identity_vertical_information(use), 0.06627772298751894, places=12)
        self.assertAlmostEqual(identity_vertical_information_given_state(use), 0.0, places=12)
        self.assertAlmostEqual(project_horizontal(use)["A"], 1.0, places=12)
        self.assertTrue(all(p > 0.0 for p in use.values()))

    def test_measured_resource_can_shift_behavior_not_horizontal_cells(self):
        base = {
            ("I1", "A", "dry"): {"forage": 0.0, "commute": 0.0},
            ("I1", "A", "fruiting"): {"forage": 0.0, "commute": 0.0},
        }
        resources = {("A", "dry"): 0.0, ("A", "fruiting"): 1.0}
        states = resource_conditioned_state_policies(
            base, resources, {"forage": 2.0, "commute": 0.0}
        )
        zero = resource_conditioned_state_policies(
            base, resources, {"forage": 0.0, "commute": 0.0}
        )
        self.assertGreater(
            states[("I1", "A", "fruiting")]["forage"],
            states[("I1", "A", "dry")]["forage"],
        )
        self.assertAlmostEqual(zero[("I1", "A", "fruiting")]["forage"], 0.5)
        height = {
            ("I1", "A", t, b): {"low": 0.1, "high": 0.9} if b == "forage"
                              else {"low": 0.9, "high": 0.1}
            for t in ("dry", "fruiting")
            for b in ("forage", "commute")
        }
        use = joint_use_distribution(
            {("A", "dry"): 0.0, ("A", "fruiting"): 0.0},
            {"I1": 1.0}, states, height,
        )
        self.assertEqual(project_horizontal(use), {"A": 1.0})
        high_fruiting = sum(p for (i, x, t, b, z), p in use.items()
                           if t == "fruiting" and z == "high")
        high_dry = sum(p for (i, x, t, b, z), p in use.items()
                       if t == "dry" and z == "high")
        self.assertGreater(high_fruiting, high_dry)
        self.assertAlmostEqual(high_dry / 0.5, 0.5, places=12)
        self.assertAlmostEqual(high_fruiting / 0.5, 0.8046376623823058, places=12)

    def test_resource_policy_missing_support_is_stop(self):
        base = {("I1", "A", "t"): {"forage": 0.0, "commute": 0.0}}
        with self.assertRaises(ValueError):
            resource_conditioned_state_policies(
                base, {}, {"forage": 1.0, "commute": 0.0}
            )
        with self.assertRaises(ValueError):
            resource_conditioned_state_policies(
                base, {("A", "t"): 1.0}, {"forage": 1.0}
            )

    def test_resource_ablation_not_an_empirical_fit(self):
        space = {("A", "t"): 0.0, ("B", "t"): 0.0}
        generic = {("A", "t"): 1.0, ("B", "t"): 1.0}
        partner = {("A", "t"): 1.0, ("B", "t"): 0.0}
        same = habitat_log_scores(space, generic, partner, beta_linked=0.0)
        changed = habitat_log_scores(space, generic, partner, beta_linked=2.0)
        self.assertEqual(same[("A", "t")], same[("B", "t")])
        self.assertGreater(changed[("A", "t")], changed[("B", "t")])
        self.assertEqual(habitat_log_scores(space, generic, partner), space)

    def test_resource_missingness_does_not_impute_zero(self):
        with self.assertRaises(ValueError):
            habitat_log_scores({("A", "t"): 0.0}, {}, {("A", "t"): 1.0})
        with self.assertRaises(ValueError):
            habitat_log_scores(
                {("A", "t"): 0.0},
                {("A", "t"): float("nan")},
                {("A", "t"): 1.0},
            )

    def test_detection_is_not_biological_use(self):
        use = toy_vertical_strategy()
        q = {("A", "night", "forage", "low"): 0.2,
             ("A", "night", "forage", "high"): 1.0}
        detected = detected_event_distribution(use, q)
        self.assertAlmostEqual(math.fsum(detected.values()), 1.0)
        self.assertAlmostEqual(
            detected[("I1", "A", "night", "forage", "low")], 1.0/6.0
        )
        self.assertAlmostEqual(
            use[("I1", "A", "night", "forage", "low")], 0.5
        )

    def test_missing_or_zero_detection_is_explicit_stop(self):
        use = toy_vertical_strategy()
        with self.assertRaises(KeyError):
            detected_event_distribution(use, {})
        with self.assertRaises(ValueError):
            detected_event_distribution(
                use, {("A", "night", "forage", "low"): 0.0,
                      ("A", "night", "forage", "high"): 0.0}
            )
        with self.assertRaises(ValueError):
            detected_event_distribution(
                use, {("A", "night", "forage", "low"): 2.0,
                      ("A", "night", "forage", "high"): 1.0}
            )

    def test_missing_behavior_and_vertical_policy_stop(self):
        with self.assertRaises(KeyError):
            joint_use_distribution({("A", "night"): 0.0}, {"I1": 1.0}, {}, {})
        with self.assertRaises(KeyError):
            joint_use_distribution(
                {("A", "night"): 0.0}, {"I1": 1.0},
                {("I1", "A", "night"): {"forage": 1.0}}, {},
            )
        with self.assertRaises(ValueError):
            joint_use_distribution(
                {("A", "night"): 0.0}, {"I1": 0.0},
                {}, {},
            )

    def test_heldout_score_never_invents_support(self):
        use = toy_vertical_strategy()
        event = ("I1", "A", "night", "forage", "low")
        self.assertAlmostEqual(mean_heldout_event_log_score(use, [event]), math.log(.5))
        self.assertEqual(
            mean_heldout_event_log_score(
                use, [("I3", "A", "night", "forage", "low")]
            ),
            float("-inf"),
        )
        with self.assertRaises(ValueError):
            mean_heldout_event_log_score(use, [])


if __name__ == "__main__":
    unittest.main()
