"""Synthetic-only PLOS three-paired-bat transfer, source intake and STOP tests."""
from __future__ import annotations
from collections import defaultdict
from contextlib import contextmanager
import io
import math
import random
import unittest
from unittest.mock import patch
import zipfile

import plos2016_three_paired_bats_exploratory_transfer_v1 as m


def mock_trials(target_z_effect=0.4,seed=401):
    rng=random.Random(seed)
    rows=[]
    for bat in range(5):
        targets=(0,1) if bat<3 else ((0,) if bat==3 else (1,))
        for target in targets:
            n=4 if bat<3 else 3
            for trial in range(n):
                frame=[]
                for i in range(14):
                    x=0.25+0.05*i+rng.gauss(0,.15)
                    y=rng.gauss(0,.08)
                    z=(0.75+target*target_z_effect+
                       .15*math.sin(i/2)+rng.gauss(0,.13))
                    frame.append((math.hypot(x,y),z))
                rows.append({
                  "bat":"fake%d"%bat,"target":target,
                  "group":("fake%d"%bat,target,str(trial)),
                  "frames":frame})
    return rows


def workbook_synthetic_zip():
    # Synthetic XML source; original sha/header can never be faked as admitted.
    import xml.etree.ElementTree as ET
    root=ET.Element(m.SHEET_NS+"worksheet")
    sd=ET.SubElement(root,m.SHEET_NS+"sheetData")
    head=ET.SubElement(sd,m.SHEET_NS+"row",{"r":"1"})
    for col in "ABCEFG":
        c=ET.SubElement(head,m.SHEET_NS+"c",{"r":col+"1","t":"inlineStr"})
        is_=ET.SubElement(c,m.SHEET_NS+"is")
        ET.SubElement(is_,m.SHEET_NS+"t").text=col
    strings=[]
    def sval(txt):
        if txt not in strings:
            strings.append(txt)
        return str(strings.index(txt))
    n=1
    for bat in range(5):
        targets=("flower","sham") if bat<3 else (("flower",) if bat==3 else ("sham",))
        for target in targets:
            count=4 if bat<3 else 3
            for trial in range(count):
                for rowidx in range(14):
                    n+=1
                    row=ET.SubElement(sd,m.SHEET_NS+"row",{"r":str(n)})
                    x=.22+.05*rowidx
                    y=.12
                    z=.70+int(target=="sham")*.55+rowidx*.01+bat*.03
                    for key,v in (("A",x),("B",y),("C",z),("E",target),
                                  ("F","bat"+str(bat)),("G","test"+str(trial))):
                        c=ET.SubElement(row,m.SHEET_NS+"c",{"r":key+str(n)})
                        if key in "EFG":
                            c.set("t","s")
                            ET.SubElement(c,m.SHEET_NS+"v").text=sval(v)
                        else:
                            ET.SubElement(c,m.SHEET_NS+"v").text=str(v)
    sroot=ET.Element(m.SHEET_NS+"sst")
    for value in strings:
        si=ET.SubElement(sroot,m.SHEET_NS+"si")
        ET.SubElement(si,m.SHEET_NS+"t").text=value
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,"w") as z:
        z.writestr("xl/worksheets/sheet1.xml",ET.tostring(root))
        z.writestr("xl/sharedStrings.xml",ET.tostring(sroot))
    return buf.getvalue()


class PLOSExploratoryTests(unittest.TestCase):
    def test_strict_source_gate_only_accepts_previous_failed_pair_structure(self):
        meta={"n_animal_groups":5,
              "n_source_target_levels":2,
              "n_bat_target_pairs":8,
              "n_distinct_bat_target_trial_sequences":30,
              "individual_total_trial_counts_sorted":[3,3,8,8,8],
              "target_group_counts_sorted":[15,15],
              "bat_target_coverage_histogram":{"1":2,"2":3},
              "status":"PLOS_BAT_TARGET_TRIAL_SUPPORT_STOP"}
        hdr={"source_sha256":m.SHA,
             "verified_original_first_row_column_names":m.HEADER}
        with patch.object(m,"parse_labels",return_value=meta), patch.object(
                m,"inspect_publisher_header",return_value=hdr):
            x=m.source_blind_structure_gate(b"FICTITIOUS")
            self.assertFalse(x["original_five_bat_gate_pass"])
            self.assertEqual(x["n_paired_bats"],3)
        bad=dict(meta,n_bat_target_pairs=10)
        with patch.object(m,"parse_labels",return_value=bad), patch.object(
                m,"inspect_publisher_header",return_value=hdr):
            with self.assertRaisesRegex(ValueError,"CHANGED_SOURCE_BAT_TARGET"):
                m.source_blind_structure_gate(b"FICTITIOUS")

    def test_xlsx_synthetic_csv_style_label_intake_only_three_paired_bats(self):
        with patch.object(m,"source_blind_structure_gate",return_value={"ok":True}):
            tracks=m._source_rows_after_gate(workbook_synthetic_zip())
        self.assertEqual(len(tracks),24)
        self.assertEqual(len({t["bat"] for t in tracks}),3)
        self.assertEqual(len({t["target"] for t in tracks}),2)
        self.assertEqual(sum(len(t["frames"]) for t in tracks),336)
        self.assertNotIn("Distance toT",str(tracks))

    def test_exploratory_model_equal_bat_holdout_can_produce_signal(self):
        data=mock_trials(target_z_effect=1.2)
        with patch.object(m,"_source_rows_after_gate",return_value=data):
            out=m.exploratory_paired_bat_lobo_from_source(b"FAKE")
        self.assertEqual(out["n_source_bats_paired_and_eligible"],3)
        self.assertEqual(out["n_source_trial_groups_eligible"],24)
        self.assertFalse(out["exact_0_05_test_possible"])
        self.assertEqual(out["minimum_one_sided_bat_signflip_p"],.125)
        self.assertEqual(len(out["results_by_anonymous_fold"]),3)
        self.assertTrue(all(len(x["four_train_bat_whole_label_swaps"])==4
                            for x in out["results_by_anonymous_fold"]))
        self.assertNotIn("fake",str(out))
        self.assertIsNone(out["ecological_resource_conditional_wild_3D_height_gain"])

    def test_heldout_after_target_relabel_is_not_a_pooled_bat_effect(self):
        data=mock_trials(target_z_effect=0.)
        a=m._train(data)
        score=m._score([t for t in data if t["bat"]=="fake1"],a)
        self.assertEqual(len(score[1]),2)
        self.assertTrue(math.isfinite(score[0]))


if __name__=="__main__":
    unittest.main()
