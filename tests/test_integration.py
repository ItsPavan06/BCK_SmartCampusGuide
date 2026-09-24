"""
test_integration.py
-------------------
End-to-End Integration Test Suite for Bhandarkars' Arts & Science College Help Desk.

Verifies:
1. Core Integration Engine (NLP + Dijkstra Navigation + SQLite)
2. Flask REST APIs (/api/query, /api/iot/*, /api/destinations, /api/health)
3. Frontend Static Serving (/index.html, /listening.html, /results.html)
4. IoT State Management (PIR motion sensor actions)
"""

import os
import sys
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(ROOT_DIR, "app")

for p in [ROOT_DIR, BACKEND_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

import importlib.util
from core.integration_engine import process_kiosk_query

# Load Flask backend app from the canonical app directory to avoid clash with Rakesh's app.py
backend_app_path = os.path.join(BACKEND_DIR, "app.py")
spec = importlib.util.spec_from_file_location("backend_app", backend_app_path)
backend_app = importlib.util.module_from_spec(spec)
sys.modules["backend_app"] = backend_app
spec.loader.exec_module(backend_app)

app = backend_app.app
iot_manager = backend_app.iot_manager


class TestIntegrationEngine(unittest.TestCase):
    """Tests natural language query routing, Dijkstra pathfinding, and DB integration."""

    def test_navigation_query_library(self):
        res = process_kiosk_query("Where is the library?")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["intent"], "navigation")
        self.assertIn("Library", res["primary_result"]["title"])
        self.assertGreater(len(res["primary_result"]["steps"]), 0)
        self.assertIn("meters", res["speech_text"].lower())

    def test_navigation_query_canteen(self):
        res = process_kiosk_query("How do I get to the canteen?")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["intent"], "navigation")
        self.assertIn("Canteen", res["primary_result"]["title"])
        self.assertGreater(len(res["primary_result"]["steps"]), 0)

    def test_multi_destination_query(self):
        res = process_kiosk_query("Where is the library and canteen?")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["intent"], "navigation")
        self.assertIn("Library", res["primary_result"]["title"])
        self.assertIn("Canteen", res["primary_result"]["title"])
        self.assertGreater(len(res["primary_result"]["steps"]), 5)

    def test_origin_and_destination_navigation(self):
        res = process_kiosk_query("From canteen to library")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["intent"], "navigation")
        self.assertIn("Library", res["primary_result"]["title"])

    def test_timing_query_library(self):
        res = process_kiosk_query("When does the library open?")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["intent"], "timing")
        self.assertIn("open", res["speech_text"].lower())
        self.assertIn("8:", res["speech_text"])

    def test_college_office_hours(self):
        res = process_kiosk_query("What are the college office hours?")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["intent"], "timing")
        self.assertIn("9:15", res["speech_text"])

    def test_admission_query(self):
        res = process_kiosk_query("Where can I apply for admission?")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["intent"], "admission")
        self.assertIn("Admission", res["primary_result"]["title"])

    def test_emergency_query(self):
        res = process_kiosk_query("What is the ambulance emergency number?")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["intent"], "emergency")
        self.assertIn("Emergency", res["primary_result"]["title"])

    def test_courses_query(self):
        res = process_kiosk_query("What courses are offered in this college?")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["intent"], "courses")
        self.assertIn("BCA", res["speech_text"])

    def test_department_lookup(self):
        res = process_kiosk_query("Where is the Chemistry Department?")
        self.assertEqual(res["status"], "success")
        self.assertIn("Chemistry", res["primary_result"]["title"])
        self.assertIn("BCA Block", res["speech_text"])

    def test_unknown_fallback(self):
        res = process_kiosk_query("xyzqwerty nonexistent question")
        self.assertEqual(res["status"], "unknown")
        self.assertIn("Sorry", res["speech_text"])


class TestFlaskAPIAndEndpoints(unittest.TestCase):
    """Tests REST API endpoints and web client responses."""

    def setUp(self):
        self.client = app.test_client()

    def test_health_endpoint(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["database_exists"])
        self.assertTrue(data["integration_engine_ready"])

    def test_destinations_endpoint(self):
        res = self.client.get("/api/destinations")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreater(data["count"], 5)
        self.assertTrue(any(d["id"] == "library" for d in data["destinations"]))

    def test_query_endpoint(self):
        res = self.client.post("/api/query", json={"query": "Where is the principal's office?"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("Principal", data["primary_result"]["title"])

    def test_backward_compatible_search(self):
        res = self.client.get("/search/BCA")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreater(data["count"], 0)

    def test_iot_status_and_trigger(self):
        # Trigger PERSON_DETECTED
        trigger_res = self.client.post("/api/iot/trigger", json={"message": "PERSON_DETECTED"})
        self.assertEqual(trigger_res.status_code, 200)
        self.assertEqual(trigger_res.get_json()["action"], "WELCOME")

        # Check status
        status_res = self.client.get("/api/iot/status")
        self.assertEqual(status_res.status_code, 200)
        self.assertEqual(status_res.get_json()["state"], "WELCOME")

        # Trigger NO_PERSON
        trigger_res2 = self.client.post("/api/iot/trigger", json={"message": "NO_PERSON"})
        self.assertEqual(trigger_res2.status_code, 200)
        self.assertEqual(trigger_res2.get_json()["action"], "STANDBY")

    def test_static_pages_served(self):
        # Index page
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Bhandarkars", res.data)

        # Listening page
        res = self.client.get("/listening.html")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"listening", res.data.lower())

        # Results page
        res = self.client.get("/results.html")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"results", res.data.lower())

        # Static assets
        res_css = self.client.get("/style.css")
        self.assertEqual(res_css.status_code, 200)
        res_js = self.client.get("/app.js")
        self.assertEqual(res_js.status_code, 200)


if __name__ == "__main__":
    unittest.main()
