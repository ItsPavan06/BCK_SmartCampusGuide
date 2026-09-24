"""
test_navigation.py
------------------
Unit tests for Rakesh's Campus Navigation Engine (navigation.py).
Tests pathfinding, distance calculation, and direction generation.
"""

import unittest
from navigation import get_directions, resolve_location_id, CAMPUS_LOCATIONS


class TestCampusNavigation(unittest.TestCase):

    def test_location_resolution(self):
        """Test resolving aliases to canonical location IDs."""
        self.assertEqual(resolve_location_id("bca department"), "block_b")
        self.assertEqual(resolve_location_id("central library"), "library")
        self.assertEqual(resolve_location_id("cafeteria"), "canteen")
        self.assertEqual(resolve_location_id("principal cabin"), "principal_office")
        self.assertIsNone(resolve_location_id("non_existent_place"))

    def test_route_to_library(self):
        """Test route calculation from Main Gate to Central Library."""
        res = get_directions("library")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["destination_id"], "library")
        self.assertGreater(res["total_distance_meters"], 0)
        self.assertTrue(len(res["steps"]) >= 3)
        self.assertIn("Step 1", res["steps"][0])

    def test_route_to_bca_block(self):
        """Test route calculation from Main Gate to Block B (BCA Department)."""
        res = get_directions("block_b", start_location_query="main_gate")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["destination_name"], "Block B (BCA & Science)")
        self.assertEqual(res["total_distance_meters"], 110)
        self.assertEqual(res["estimated_time_minutes"], 2)

    def test_route_to_canteen(self):
        """Test route calculation to Canteen."""
        res = get_directions("canteen")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["destination_id"], "canteen")
        self.assertIn("Canteen", res["directions_text"])

    def test_all_known_destinations(self):
        """Verify that every campus location generates a valid route from Main Gate."""
        for loc_id in CAMPUS_LOCATIONS:
            if loc_id == "main_gate":
                continue
            res = get_directions(loc_id)
            self.assertEqual(res["status"], "success", f"Failed for {loc_id}")
            self.assertGreater(len(res["steps"]), 0, f"No steps generated for {loc_id}")


if __name__ == "__main__":
    unittest.main()
