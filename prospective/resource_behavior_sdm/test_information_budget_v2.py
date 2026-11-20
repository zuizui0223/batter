"""Two distinct synthetic mechanisms, no original bat records."""
import math
import unittest
from information_budget_v2 import identity_information_budget
from resource_behavior_sdm import joint_use_distribution


def distribution(pi_a, pi_b, height_a, height_b):
    return joint_use_distribution(
        {("XY", "night"):0}, {"i":1,"j":1},
        {("i","XY","night"):{"A":pi_a,"B":1-pi_a},
         ("j","XY","night"):{"A":pi_b,"B":1-pi_b}},
        {("i","XY","night","A"):{"low":height_a,"high":1-height_a},
         ("j","XY","night","A"):{"low":height_b,"high":1-height_b},
         ("i","XY","night","B"):{"low":.1,"high":.9},
         ("j","XY","night","B"):{"low":.1,"high":.9}},
    )


class MIInformationBudgetTests(unittest.TestCase):
    def test_state_allocation_only(self):
        # Same height use within EACH state, but state frequencies differ.
        j=joint_use_distribution(
            {("XY","night"):0},{"i":1,"j":1},
            {("i","XY","night"):{"A":.9,"B":.1},
             ("j","XY","night"):{"A":.1,"B":.9}},
            {(i,"XY","night",b):({"low":.8,"high":.2} if b=="A" else {"low":.2,"high":.8})
             for i in ("i","j") for b in ("A","B")}
        )
        r=identity_information_budget(j)
        self.assertGreater(r["state_allocation_identity_nats"],.1)
        self.assertAlmostEqual(r["within_state_vertical_identity_nats"],0.,places=12)
        self.assertGreater(r["marginal_vertical_identity_nats"],0.)
        self.assertAlmostEqual(r["joint_state_height_identity_nats"],
           r["state_allocation_identity_nats"],places=12)

    def test_within_state_only(self):
        j=distribution(.5,.5,.95,.05)
        r=identity_information_budget(j)
        self.assertAlmostEqual(r["state_allocation_identity_nats"],0,places=12)
        self.assertGreater(r["within_state_vertical_identity_nats"],0)
        self.assertAlmostEqual(r["joint_state_height_identity_nats"],
                               r["within_state_vertical_identity_nats"],places=12)

    def test_both_and_chain_rule(self):
        j=distribution(.8,.2,.9,.1)
        r=identity_information_budget(j)
        self.assertGreater(r["state_allocation_identity_nats"],0)
        self.assertGreater(r["within_state_vertical_identity_nats"],0)
        self.assertAlmostEqual(r["chain_rule_error_nats"],0,places=12)
        self.assertIsNone(r["ecological_resource_causation"])

    def test_invalid_joint_stops(self):
        with self.assertRaises(ValueError):
            identity_information_budget({})
        with self.assertRaises(ValueError):
            identity_information_budget({("i","XY","t","A","low"):.5})
        with self.assertRaises(ValueError):
            identity_information_budget({("i","XY","t","A","low"):float("nan")})


if __name__=="__main__":
    unittest.main()
