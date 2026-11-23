"""Source-free original GPS-stereo author file grammar checks."""
import csv,io,json,unittest
from scripts.audit_happ_georeferenced_stereo_source_v1 import (
    flight_header_structure,camera_source_structure,git_blob
)


class HappSourceMetaTests(unittest.TestCase):
    def synthetic(self,n=22):
        out=io.StringIO()
        w=csv.writer(out)
        w.writerow(["","nr","datetime","x1","y1","x2","y2","lat","lon","height"])
        for i in range(n):
            w.writerow([i,i+1,"SEALED_TIME", "X_NOT_OPENED","Y_NOT_OPENED",
                        "X2_SEALED","Y2_SEALED","LAT_SEALED","LON_SEALED","HEIGHT_SEALED"])
        return out.getvalue().encode()

    def test_required_gps_and_stereo_field_labels_not_numeric_contents(self):
        x=flight_header_structure(self.synthetic())
        self.assertEqual(x["source_data_rows"],22)
        self.assertEqual(x["columns_per_row"],10)
        self.assertFalse(x["raw_numeric_drone_GPS_or_pixels_inspected"])
        self.assertNotIn("SEALED_TIME",str(x))

    def test_source_header_missing_gps_stops(self):
        raw=self.synthetic().replace(b",lat,lon,height",b",lat,lon,other")
        with self.assertRaisesRegex(ValueError,"exact published"):
            flight_header_structure(raw)

    def test_ragged_original_source_stops_without_cherry_picking(self):
        raw=self.synthetic()+b"1,2,3\n"
        with self.assertRaisesRegex(ValueError,"grammar"):
            flight_header_structure(raw)

    def test_camera_intrinsics_and_reference_source_only(self):
        payload={
            "ref":[49.,11.],
            "camintrinsicMatrix1":[[100,0,50],[0,100,50],[0,0,1]],
            "camintrinsicMatrix2":[[100,0,50],[0,100,50],[0,0,1]],
        }
        r=camera_source_structure(json.dumps(payload).encode())
        self.assertTrue(r["source_ref_coordinate_present"])
        self.assertFalse(r["source_intrinsic_numeric_parameters_used"])

    def test_git_blob_hash_verifies_source_bytes(self):
        import hashlib
        blob=b"example\n"
        self.assertEqual(git_blob(blob),hashlib.sha1(b"blob 8\0example\n").hexdigest())


if __name__=="__main__":
    unittest.main()
