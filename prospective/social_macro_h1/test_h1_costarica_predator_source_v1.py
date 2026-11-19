import math
import unittest
from h1_costarica_predator_cue_source_v1 import parse, describe, group_bounds

class TestCostaRicaSourceContract(unittest.TestCase):
    def make_synthetic_source(self):
        lines=["bat;experiment;order;treatment;bat_type;period;response"]
        for i in range(38):
            order="NP-P" if i<22 else "P-NP"
            nonpred="control" if i<14 else "frugivorous" if i<26 else "insectivorous"
            for t,bat_type in [("non-predator",nonpred),("predator","carnivorous")]:
                for phase,value in [("before",6),("during",0 if t=="predator" else 6),("after",6)]:
                    lines.append(f"{i+1};CP;{order};{t};{bat_type};{phase};{value}")
        return ("\n".join(lines)+"\n").encode()
    def test_structural_count_and_fixed_direction(self):
        rows=parse(self.make_synthetic_source())
        d=describe(rows)
        self.assertEqual(d["n_responder_bats"],38)
        self.assertEqual(d["negative_bats"],38)
        self.assertAlmostEqual(d["mean_primary_log_contrast"],-math.log(7))
    def test_unknown_33_groups_group_equal_bounds(self):
        rows=parse(self.make_synthetic_source())
        effects=[r["primary"] for r in rows]
        out=group_bounds(effects,33)
        self.assertEqual(out["n_source_responders"],38)
        self.assertEqual(out["n_published_groups"],33)
        self.assertEqual(out["enumerated_group_size_shapes"],7)
        self.assertAlmostEqual(out["sharp_lower_equal_group_mean"],-math.log(7),places=10)
        self.assertAlmostEqual(out["sharp_upper_equal_group_mean"],-math.log(7),places=10)
        self.assertIn("STOP",out["unknown_physical_group_cluster_p"])
        # Non-constant known-truth values: exhaustive size allocation yields
        # bounds containing any explicitly feasible six-person group assignment.
        vals=list(range(38))
        q=group_bounds(vals,33)
        singleton=sum(vals[:32])+sum(vals[32:38])/6
        feasible_mean=singleton/33
        self.assertLessEqual(q["sharp_lower_equal_group_mean"],feasible_mean)
        self.assertGreaterEqual(q["sharp_upper_equal_group_mean"],feasible_mean)

    def test_reject_incomplete_pair(self):
        lines=self.make_synthetic_source().decode().splitlines()
        with self.assertRaisesRegex(ValueError,"228 original source rows"):
            parse(("\n".join(lines[:-1])+"\n").encode())
    def test_reject_changed_source_codes(self):
        raw=self.make_synthetic_source().replace(b";NP-P;non-predator;",b";BAD;non-predator;",1)
        with self.assertRaisesRegex(ValueError,"Unrecognized stimulus order"):
            parse(raw)

if __name__=="__main__":
    unittest.main()
