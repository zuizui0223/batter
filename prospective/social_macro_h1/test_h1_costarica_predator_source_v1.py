import math
import unittest
from h1_costarica_predator_cue_source_v1 import parse, describe

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
