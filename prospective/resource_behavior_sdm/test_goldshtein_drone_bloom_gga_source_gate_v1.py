"""Source-free test of observation-date, NMEA pairing and XY-only grouping."""
from datetime import date, datetime, timedelta
import unittest

from goldshtein_drone_bloom_xy_morning_gate_v1 import (
    count_gap60_episodes, nmea_coordinate, source_following_morning
)
from goldshtein_gga_drone_datum_source_gate_v1 import (
    _date_from_rmc_fields, _nmea_source_pair
)


class RealSourceEligibilityContracts(unittest.TestCase):
    def test_sonora_evening_and_morning_map_to_census_morning(self):
        self.assertEqual(source_following_morning(datetime(2016, 5, 23, 2, 30)),
                         date(2016, 5, 23))
        self.assertEqual(source_following_morning(datetime(2016, 5, 23, 10, 30)),
                         date(2016, 5, 23))
        self.assertIsNone(source_following_morning(datetime(2016, 5, 23, 19, 30)))

    def test_nmea_lat_lon_semantics(self):
        self.assertAlmostEqual(nmea_coordinate("3121.5000", "N"),31.35833333333)
        self.assertAlmostEqual(nmea_coordinate("11234.5000", "W"),-112.575)
        self.assertIsNone(nmea_coordinate("3161.00", "N"))
        self.assertIsNone(nmea_coordinate(None, "W"))

    def test_source_episodes_not_number_of_GPS_fixes(self):
        zero=datetime(2016,5,23,2,0)
        events=[
            ("fake_bat",date(2016,5,23),zero,1,3),
            ("fake_bat",date(2016,5,23),zero+timedelta(seconds=30),1,3),
            ("fake_bat",date(2016,5,23),zero+timedelta(seconds=91),1,3),
            ("fake_bat",date(2016,5,23),zero+timedelta(seconds=92),2,0),
        ]
        self.assertEqual(count_gap60_episodes(events),(3,2))

    def test_pair_GGA_and_RMC_only_same_source_position_and_time(self):
        gg=(4,"020304.00","3121.50","N","11234.50","W",149.0,None)
        rm=(6,"020304.00","3121.50","N","11234.50","W","230516")
        self.assertTrue(_nmea_source_pair(gg,rm))
        self.assertFalse(_nmea_source_pair(gg,(16,)+rm[1:]))
        self.assertFalse(_nmea_source_pair(gg,(6,"020305.00")+rm[2:]))
        self.assertFalse(_nmea_source_pair(gg,(6,"020304.00","3121.51")+rm[3:]))

    def test_RMC_has_12_fields_not_13(self):
        fields=["$GPRMC","020304.00","A","3121.50","N",
                "11234.50","W","","","230516","",""]
        self.assertEqual(len(fields),12)
        self.assertEqual(_date_from_rmc_fields(fields),
                         datetime(2016,5,23,2,3,4))
        fields[2]="V"
        self.assertIsNone(_date_from_rmc_fields(fields))


if __name__=="__main__":
    unittest.main()
