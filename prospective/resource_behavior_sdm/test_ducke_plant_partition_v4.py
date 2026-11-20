"""No animal rows opened. Synthetic regression tests of v4 12/10 label null."""
import random
import unittest
from ducke_plant_partition_v4 import (
    FOOD12,abundance_quartiles,draw_partitions,materialize_partition,
    null_stats, split_logscore, N_DRAW
)


class PlantPartitionControls(unittest.TestCase):
    def setUp(self):
        self.names=sorted(FOOD12)+["synthetic_g"+str(i) for i in range(9)]+["Not_identified"]
        self.assertEqual(len(set(self.names)),22)
        self.counts={name:i+1 for i,name in enumerate(sorted(self.names))}

    def test_randomized_sets_and_abundance_support(self):
        draws=list(draw_partitions(self.names,FOOD12,self.counts,"unrestricted"))
        self.assertEqual(len(draws),199)
        self.assertTrue(all(len(x)==12 for x in draws))
        self.assertEqual(draws[:4],list(draw_partitions(
            self.names,FOOD12,self.counts,"unrestricted"))[:4])
        q=abundance_quartiles(self.names,self.counts)
        c=[len(set(x)&FOOD12) for x in q]
        constrained=list(draw_partitions(self.names,FOOD12,self.counts,"abundance_stratified"))
        self.assertTrue(all([len(set(x)&set(p)) for p in q]==c for x in constrained))
        self.assertEqual(len(constrained),N_DRAW)

    def test_missing_categories_and_invalid_fruit_fail(self):
        row={"source_fruit_by_category":{x:0.0 for x in self.names}}
        values=materialize_partition([row],FOOD12,self.names)
        self.assertNotIn("source_fruit_by_category",values[0])
        self.assertEqual(values[0]["fruit_all"],0.0)
        del row["source_fruit_by_category"][self.names[0]]
        with self.assertRaisesRegex(ValueError,"MISSING_22"):
            materialize_partition([row],FOOD12,self.names)

    def test_unknown_plant_category_not_a_named_genus(self):
        row={"source_fruit_by_category":{x:1.0 for x in self.names}}
        rows=materialize_partition([row],FOOD12,self.names,named_only=True)
        self.assertEqual(rows[0]["fruit_batfood_12"],12)
        self.assertEqual(rows[0]["fruit_other"],9)
        self.assertEqual(rows[0]["fruit_all"],21)

    def test_tail_is_reproducible_but_not_confirmatory(self):
        vals=[0.1]*4+[0.0]*195
        r=null_stats(vals,0.1,0.0)
        self.assertEqual(r["n_at_least_observed"],4)
        self.assertAlmostEqual(r["exploratory_plus_one_tail_fraction"],.025)
        self.assertTrue(r["not_confirmatory_p_value"])

    def test_number_of_simulation_draws_is_frozen(self):
        with self.assertRaisesRegex(ValueError,"UNKNOWN_NULL"):
            list(draw_partitions(self.names,FOOD12,self.counts,"unrestricted",n=9))


if __name__=="__main__":
    unittest.main()
