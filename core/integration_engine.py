"""
core/integration_engine.py
--------------------------
Unified Intelligence & Navigation Engine for Bhandarkars' Arts & Science College Help Desk.

Bridges:
1. Prathiksha's AI/NLP Intent Processor (ai_processor.py, campus_data.py)
2. Rakesh's Campus Navigation & Entity Extractor (navigation.py, destinations.py, intent.py)
3. SQLite Knowledge Base (campus.db)
"""

import os
import sys
import sqlite3
import re
from typing import Dict, Any, Optional, List, Tuple

# Setup import paths to access modules in the unified AI/navigation package
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AI_DIR = os.path.join(BASE_DIR, "campus_voice_ai")
BACKEND_DIR = os.path.join(BASE_DIR, "app")
DB_PATH = os.path.join(BACKEND_DIR, "campus.db")

for path in [AI_DIR, BACKEND_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import unified AI/navigation modules
try:
    from navigation import get_directions, resolve_location_id, CAMPUS_LOCATIONS, DEFAULT_KIOSK_LOCATION
    from destinations import extract_destination, extract_origin_and_destination, normalize_text
    from intent import detect_intent_and_destination, is_navigation_query, is_college_info_query
    from ai_processor import process_query as nlp_process_query, identify_intent
    from campus_data import campus_data
except ImportError as e:
    raise ImportError(f"Error importing unified campus AI modules: {e}")


def get_db_connection() -> sqlite3.Connection:
    """Connect to SQLite database with Row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# Mapping from NLP / Database destination names to graph nodes in navigation.py
LOCATION_TO_GRAPH_NODE = {
    "library": "library",
    "central library": "library",
    "canteen": "canteen",
    "cafeteria": "canteen",
    "food court": "canteen",
    "bca department": "block_b",
    "bca": "block_b",
    "bca block": "block_b",
    "computer science": "block_b",
    "computer lab": "computer_lab",
    "cs lab": "computer_lab",
    "bca lab 1": "computer_lab",
    "bca lab 2": "computer_lab",
    "bca lab 3": "computer_lab",
    "bca lab 4": "computer_lab",
    "bca lab 5": "computer_lab",
    "puc lab": "computer_lab",
    "principal chamber": "principal_office",
    "principal's office": "principal_office",
    "principal office": "principal_office",
    "admin block": "admin_block",
    "administrative block": "admin_block",
    "admin office": "admin_block",
    "admission office": "admin_block",
    "fee payment office": "admin_block",
    "student service centre": "admin_block",
    "college office": "admin_block",
    "auditorium": "auditorium",
    "sports complex": "sports_complex",
    "playground": "sports_complex",
    "sports ground": "sports_complex",
    "girls indoor games": "library",  # located behind library
    "boys indoor games": "sports_complex",
    "hostel": "hostel",
    "boys hostel": "hostel",
    "girls hostel": "hostel",
    "placement cell": "placement_cell",
    "parking": "parking",
    "main gate": "main_gate",
    "entrance": "main_gate",
    "block a": "block_a",
    "block b": "block_b",
}


def map_to_graph_node(location_str: str) -> Optional[str]:
    """Resolves arbitrary campus text or entity to a navigation graph node."""
    if not location_str:
        return None
    cleaned = normalize_text(str(location_str))
    
    # 1. Exact match in manual mapping
    if cleaned in LOCATION_TO_GRAPH_NODE:
        return LOCATION_TO_GRAPH_NODE[cleaned]
    
    # 2. Substring match in manual mapping
    for key, node in LOCATION_TO_GRAPH_NODE.items():
        if key in cleaned:
            return node
            
    # 3. Fallback to navigation.py's internal alias resolver
    resolved = resolve_location_id(location_str)
    if isinstance(resolved, list):
        return resolved[0] if resolved else None
    return resolved


def query_database_details(name_keyword: str) -> Optional[Dict[str, Any]]:
    """Searches departments, locations, and offices in SQLite for building and floor details."""
    conn = get_db_connection()
    cur = conn.cursor()
    pattern = f"%{name_keyword}%"

    # Search locations table
    cur.execute("SELECT name, location, details FROM locations WHERE name LIKE ? OR location LIKE ? LIMIT 1", (pattern, pattern))
    row = cur.fetchone()
    if row:
        conn.close()
        return {
            "name": row["name"],
            "location": row["location"],
            "floor": "",
            "details": row["details"] or ""
        }

    # Search departments table
    cur.execute("SELECT name, location, floor, details FROM departments WHERE name LIKE ? LIMIT 1", (pattern,))
    row = cur.fetchone()
    if row:
        conn.close()
        return {
            "name": row["name"],
            "location": row["location"],
            "floor": row["floor"] or "",
            "details": row["details"] or ""
        }

    # Search offices table
    cur.execute("SELECT name, location, floor, details FROM offices WHERE name LIKE ? LIMIT 1", (pattern,))
    row = cur.fetchone()
    if row:
        conn.close()
        return {
            "name": row["name"],
            "location": row["location"],
            "floor": row["floor"] or "",
            "details": row["details"] or ""
        }

    conn.close()
    return None


def search_all_database(keyword: str) -> List[Dict[str, Any]]:
    """Broad search across all database tables matching keyword."""
    conn = get_db_connection()
    cur = conn.cursor()
    val = f"%{keyword}%"
    records = []

    # Departments
    cur.execute("SELECT name, location, floor, details FROM departments WHERE name LIKE ? OR details LIKE ?", (val, val))
    for r in cur.fetchall():
        records.append({
            "table": "departments",
            "title": r["name"],
            "location": r["location"],
            "floor": r["floor"],
            "details": r["details"]
        })

    # Locations
    cur.execute("SELECT name, location, details FROM locations WHERE name LIKE ? OR details LIKE ?", (val, val))
    for r in cur.fetchall():
        records.append({
            "table": "locations",
            "title": r["name"],
            "location": r["location"],
            "floor": "",
            "details": r["details"]
        })

    # Offices
    cur.execute("SELECT name, location, floor, details FROM offices WHERE name LIKE ? OR details LIKE ?", (val, val))
    for r in cur.fetchall():
        records.append({
            "table": "offices",
            "title": r["name"],
            "location": r["location"],
            "floor": r["floor"],
            "details": r["details"]
        })

    # Scholarships
    cur.execute("SELECT name, eligibility, information FROM scholarships WHERE name LIKE ? OR eligibility LIKE ?", (val, val))
    for r in cur.fetchall():
        records.append({
            "table": "scholarships",
            "title": r["name"],
            "location": "Admin Block - Scholarship Help",
            "floor": "First Floor",
            "details": f"Eligibility: {r['eligibility']}. {r['information']}"
        })

    # Placements
    cur.execute("SELECT company, program, course, year, students FROM placements WHERE company LIKE ? OR course LIKE ?", (val, val))
    for r in cur.fetchall():
        records.append({
            "table": "placements",
            "title": f"Placement: {r['company']}",
            "location": "Placement Cell",
            "floor": "Admin Block - 1st Floor",
            "details": f"{r['course']} ({r['year']}) - {r['students']} students selected"
        })

    conn.close()
    return records


def get_nearby_secondary_location(primary_node: str) -> Dict[str, Any]:
    """Finds a sensible adjacent or nearby location on campus as secondary recommendation."""
    # Predefined interesting landmarks by vicinity
    nearby_recommendations = {
        "library": {
            "title": "Computer Science Lab",
            "location": "Block B · 1st Floor",
            "details": "Modern computing lab with internet access and programming environment.",
            "walk_time": "1 min",
            "tag": "ALSO NEARBY"
        },
        "block_b": {
            "title": "Central Library",
            "location": "Block B · 2nd Floor",
            "details": "Study tables, digital library catalog, and reading room.",
            "walk_time": "1 min",
            "tag": "ON SAME BLOCK"
        },
        "canteen": {
            "title": "Sports Complex & Ground",
            "location": "Sports Block",
            "details": "Outdoor ground, gymnasium, and indoor sports amenities.",
            "walk_time": "2 min",
            "tag": "NEARBY"
        },
        "admin_block": {
            "title": "Principal's Office",
            "location": "Admin Block · Ground Floor",
            "details": "Executive office of the college principal.",
            "walk_time": "30 sec",
            "tag": "IN THIS BUILDING"
        },
        "principal_office": {
            "title": "Administrative Office",
            "location": "Admin Block · Ground Floor",
            "details": "Admissions, fees, document verification, and student support.",
            "walk_time": "30 sec",
            "tag": "IN THIS BUILDING"
        },
        "computer_lab": {
            "title": "Central Library",
            "location": "Block B · 2nd Floor",
            "details": "Quiet study area, reference section, and book bank.",
            "walk_time": "1 min",
            "tag": "UPSTAIRS"
        }
    }

    if primary_node in nearby_recommendations:
        return nearby_recommendations[primary_node]
    
    # Fallback to general suggestion
    return {
        "title": "Student Service Centre",
        "location": "Admin Block · Ground Floor",
        "details": "Help desk, query resolution, and student records.",
        "walk_time": "2 min",
        "tag": "HELP DESK"
    }


def process_kiosk_query(query: str, origin: Optional[str] = None) -> Dict[str, Any]:
    """
    Main integrated query processor for the College Kiosk.
    Analyzes user text, detects intent, computes shortest path navigation if applicable,
    pulls database records, and formats structured response for web UI and speech.
    """
    if not query or not query.strip():
        return {
            "status": "empty",
            "query": "",
            "intent": "unknown",
            "speech_text": "Please ask a question about Bhandarkars' College campus or facilities.",
            "primary_result": {
                "title": "Bhandarkars' College Help Desk",
                "subtitle": "Ask me anything",
                "description": "You can ask for directions (e.g. 'Where is the library?'), college timings, admissions, departments, or emergency contacts.",
                "walk_time": "",
                "distance": "",
                "status_badge": "READY",
                "floor_info": "",
                "hours": "Mon-Sat 8:30 AM - 6:00 PM"
            },
            "secondary_result": None,
            "navigation_details": None
        }

    raw_query = query.strip()
    norm_query = normalize_text(raw_query)

    # ---------------------------------------------------------
    # 1. EMERGENCY CHECK
    # ---------------------------------------------------------
    emergency_keywords = ["emergency", "ambulance", "hospital", "police", "security", "fire", "doctor", "first aid"]
    if any(re.search(r"\b" + kw + r"\b", norm_query) for kw in emergency_keywords):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT service, contact, information FROM emergency")
        rows = cur.fetchall()
        conn.close()

        first_service = rows[0] if rows else None
        speech = "In case of emergency, contact campus security or ambulance immediately."
        if first_service:
            speech = f"For {first_service['service']}, call {first_service['contact']}."

        services_summary = " · ".join([f"{r['service']}: {r['contact']}" for r in rows[:3]])

        return {
            "status": "success",
            "query": raw_query,
            "intent": "emergency",
            "speech_text": speech,
            "primary_result": {
                "title": "Emergency Services",
                "subtitle": "Immediate Assistance",
                "description": f"Emergency contacts: {services_summary}",
                "walk_time": "Instant",
                "distance": "",
                "status_badge": "URGENT",
                "floor_info": "Campus Security & First Aid",
                "hours": "24/7 Support Available"
            },
            "secondary_result": {
                "title": "Administrative Office",
                "location": "Admin Block · Ground Floor",
                "details": "Campus staff is available during working hours for emergency reporting.",
                "walk_time": "1 min",
                "tag": "OFFICIAL CONTACT"
            },
            "navigation_details": None
        }

    # ---------------------------------------------------------
    # 2. RUN NLP CLASSIFICATION & ENTITY EXTRACTION
    # ---------------------------------------------------------
    # Rakesh's intent & origin/destination detector
    rakesh_intent_data = detect_intent_and_destination(raw_query)
    # Prathiksha's AI NLP intent & matching processor
    prathiksha_data = nlp_process_query(raw_query)

    detected_intent = rakesh_intent_data.get("intent")
    extracted_origin = rakesh_intent_data.get("origin") or origin or DEFAULT_KIOSK_LOCATION
    extracted_dest = rakesh_intent_data.get("destination") or prathiksha_data.get("destination")

    # If Prathiksha identifies a specific information intent with a canned response
    prathiksha_type = prathiksha_data.get("type")
    prathiksha_intent = prathiksha_data.get("intent")

    # ---------------------------------------------------------
    # 3. COURSES & ACADEMIC PROGRAMS CHECK
    # ---------------------------------------------------------
    if (
        prathiksha_intent == "COURSES" or
        any(re.search(r"\b" + kw + r"\b", norm_query) for kw in ["course", "courses", "degree", "degrees", "programs", "programmes", "bca", "bsc", "bcom", "bba", "ba"])
        and not any(re.search(r"\b" + kw + r"\b", norm_query) for kw in ["where", "how to get", "directions", "route", "way to", "reach", "lab", "department"])
    ):
        courses_text = "Bhandarkars' College offers undergraduate degree programs in BA, BSc, BCom, BBA, and BCA affiliated with Mangalore University."
        speech = courses_text
        nav_data = get_directions("block_b", start_location_query=extracted_origin)

        return {
            "status": "success",
            "query": raw_query,
            "intent": "courses",
            "speech_text": speech,
            "primary_result": {
                "title": "Academic Programs & Courses",
                "subtitle": "Undergraduate Degree Streams",
                "description": courses_text,
                "walk_time": "2 min",
                "distance": f"{nav_data.get('total_distance_meters', 60)}m",
                "status_badge": "COURSES",
                "floor_info": "Block A & Block B",
                "hours": "Academic Year Schedule",
                "steps": nav_data.get("steps", [])
            },
            "secondary_result": {
                "title": "BCA & Computer Science Block",
                "location": "Block B",
                "details": "Department offering modern computer applications curriculum.",
                "walk_time": "2 min",
                "tag": "SPOTLIGHT"
            },
            "navigation_details": nav_data
        }

    # ---------------------------------------------------------
    # 4. ADMISSIONS CHECK
    # ---------------------------------------------------------
    if prathiksha_intent == "ADMISSION" or any(re.search(r"\b" + kw + r"\b", norm_query) for kw in ["admission", "admissions", "apply", "application"]):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT name, location, timing, information FROM admissions LIMIT 1")
        adm = cur.fetchone()
        conn.close()

        title = adm["name"] if adm else "Admission Office"
        location = adm["location"] if adm else "Administrative Block"
        timing = adm["timing"] if adm else "8:30 AM - 6:00 PM"
        info = adm["information"] if adm else "Admission process and applications are handled through the College Office."
        speech = f"Admissions are handled at the College Office in the Administrative Block from {timing}."

        nav_data = get_directions("admin_block", start_location_query=extracted_origin)

        return {
            "status": "success",
            "query": raw_query,
            "intent": "admission",
            "speech_text": speech,
            "primary_result": {
                "title": title,
                "subtitle": location,
                "description": info,
                "walk_time": f"{nav_data.get('estimated_time_minutes', 1)} min",
                "distance": f"{nav_data.get('total_distance_meters', 10)}m",
                "status_badge": "ADMISSIONS",
                "floor_info": "Admin Block · Ground Floor",
                "hours": timing,
                "steps": nav_data.get("steps", [])
            },
            "secondary_result": {
                "title": "Academic Programs",
                "location": "BA, BSc, BCom, BBA, BCA",
                "details": "Undergraduate degree programs affiliated with Mangalore University.",
                "walk_time": "",
                "tag": "PROGRAMS"
            },
            "navigation_details": nav_data
        }

    # ---------------------------------------------------------
    # 5. TIMING QUERIES CHECK
    # ---------------------------------------------------------
    is_timing_specific = any(kw in norm_query for kw in ["timing", "timings", "hours", "when does", "when is", "open time", "close time", "closing time", "opening time", "reopen"])
    if is_timing_specific or prathiksha_intent in ["LIBRARY_TIMING", "COLLEGE_OFFICE_HOURS"]:
        conn = get_db_connection()
        cur = conn.cursor()

        if "library" in norm_query or prathiksha_intent == "LIBRARY_TIMING":
            cur.execute("SELECT name, weekday_timing, saturday_timing, sunday_timing, facilities FROM library LIMIT 1")
            lib = cur.fetchone()
            conn.close()

            title = lib["name"] if lib else "Central Library"
            weekday = lib["weekday_timing"] if lib else "8:30 AM to 5:15 PM"
            sat = lib["saturday_timing"] if lib else "8:30 AM to 1:00 PM"
            desc = f"Monday to Friday: {weekday}. Saturday: {sat}. Official holidays closed."
            speech = f"The library is open from {weekday} on weekdays, and {sat} on Saturdays."

            nav_data = get_directions("library", start_location_query=extracted_origin)

            return {
                "status": "success",
                "query": raw_query,
                "intent": "timing",
                "speech_text": speech,
                "primary_result": {
                    "title": title,
                    "subtitle": "Library Working Hours",
                    "description": desc,
                    "walk_time": f"{nav_data.get('estimated_time_minutes', 1)} min",
                    "distance": f"{nav_data.get('total_distance_meters', 20)}m",
                    "status_badge": "TIMINGS",
                    "floor_info": "Block B · 2nd Floor",
                    "hours": weekday,
                    "steps": nav_data.get("steps", [])
                },
                "secondary_result": get_nearby_secondary_location("library"),
                "navigation_details": nav_data
            }

        # College Office Hours
        cur.execute("SELECT name, information FROM campus_info WHERE name LIKE '%Office%'")
        office_rows = cur.fetchall()
        conn.close()

        if office_rows:
            timing_text = " · ".join([f"{r['name']}: {r['information']}" for r in office_rows])
            speech = f"The College Office operates {', '.join([f'{r['name']} from {r['information']}' for r in office_rows])}."
        else:
            timing_text = "The College Office operates from 9:15 AM to 5:15 PM on weekdays, and 9:15 AM to 1:00 PM on Saturdays."
            speech = timing_text

        nav_data = get_directions("admin_block", start_location_query=extracted_origin)

        return {
            "status": "success",
            "query": raw_query,
            "intent": "timing",
            "speech_text": speech,
            "primary_result": {
                "title": "College Office Hours",
                "subtitle": "Administrative Block",
                "description": timing_text,
                "walk_time": "1 min",
                "distance": f"{nav_data.get('total_distance_meters', 10)}m",
                "status_badge": "HOURS",
                "floor_info": "Admin Block · Ground Floor",
                "hours": "Mon-Sat 8:30 AM - 6:00 PM",
                "steps": nav_data.get("steps", [])
            },
            "secondary_result": {
                "title": "Fee Payment Counter",
                "location": "Admin Block · 1st Floor",
                "details": "Fee collection, challans, and accounts office.",
                "walk_time": "1 min",
                "tag": "RELATED OFFICE"
            },
            "navigation_details": nav_data
        }

    # ---------------------------------------------------------
    # 6. NAVIGATION / LOCATION QUERIES
    # ---------------------------------------------------------
    is_nav = (
        detected_intent == "navigation" or
        is_navigation_query(norm_query) or
        prathiksha_type == "location" or
        extracted_dest is not None
    )

    if is_nav and extracted_dest:
        # Resolve destination to graph node
        if isinstance(extracted_dest, list):
            # Multi-destination itinerary
            dest_nodes = [map_to_graph_node(d) for d in extracted_dest]
            dest_nodes = [d for d in dest_nodes if d]
            if not dest_nodes:
                dest_nodes = extracted_dest
            nav_data = get_directions(dest_nodes, start_location_query=extracted_origin)
            
            d_names = ", ".join([d.replace("_", " ").title() for d in extracted_dest])
            speech = f"Here are the directions to {d_names}."
            if nav_data.get("status") == "success":
                speech = f"The route to {d_names} is approximately {nav_data.get('total_distance_meters')} meters, taking about {nav_data.get('estimated_time_minutes')} minutes."

            return {
                "status": "success",
                "query": raw_query,
                "intent": "navigation",
                "speech_text": speech,
                "primary_result": {
                    "title": f"Route to {d_names}",
                    "subtitle": f"Multi-stop Navigation ({len(dest_nodes)} places)",
                    "description": nav_data.get("directions_text", f"Directions to {d_names}"),
                    "walk_time": f"{nav_data.get('estimated_time_minutes', 2)} min",
                    "distance": f"{nav_data.get('total_distance_meters', 100)}m",
                    "status_badge": "BEST ROUTE",
                    "floor_info": f"Starting from {CAMPUS_LOCATIONS.get(extracted_origin, {}).get('name', 'Admin Block')}",
                    "hours": "Open campus access",
                    "steps": nav_data.get("steps", [])
                },
                "secondary_result": get_nearby_secondary_location(dest_nodes[0] if dest_nodes else "admin_block"),
                "navigation_details": nav_data
            }

        # Single destination
        dest_str = str(extracted_dest)
        graph_node = map_to_graph_node(dest_str) or resolve_location_id(dest_str)
        if not graph_node:
            graph_node = "library" if "library" in norm_query else "admin_block"

        nav_data = get_directions(graph_node, start_location_query=extracted_origin)
        db_details = query_database_details(dest_str)

        dest_display = CAMPUS_LOCATIONS.get(graph_node, {}).get("name", dest_str.replace("_", " ").title())
        dest_block = CAMPUS_LOCATIONS.get(graph_node, {}).get("block", "")
        
        description_text = ""
        if db_details and db_details.get("details"):
            description_text = db_details["details"]
        elif prathiksha_data.get("response"):
            description_text = prathiksha_data["response"]
        else:
            description_text = f"{dest_display} is located in {dest_block}."

        floor_info = db_details.get("floor") if db_details else dest_block
        if not floor_info:
            floor_info = dest_block

        est_time = nav_data.get("estimated_time_minutes", 1) if nav_data.get("status") == "success" else 1
        est_dist = nav_data.get("total_distance_meters", 50) if nav_data.get("status") == "success" else 50
        steps = nav_data.get("steps", [])

        speech = f"{dest_display} is in {dest_block}. It is about {est_dist} meters away, a {est_time} minute walk from here."

        return {
            "status": "success",
            "query": raw_query,
            "intent": "navigation",
            "speech_text": speech,
            "primary_result": {
                "title": dest_display,
                "subtitle": floor_info,
                "description": description_text,
                "walk_time": f"{est_time} min",
                "distance": f"{est_dist}m",
                "status_badge": "BEST MATCH",
                "floor_info": floor_info,
                "hours": "Working hours: 8:30 AM - 5:15 PM",
                "steps": steps
            },
            "secondary_result": get_nearby_secondary_location(graph_node),
            "navigation_details": nav_data
        }

    # ---------------------------------------------------------
    # 4. TIMING QUERIES
    # ---------------------------------------------------------
    if is_timing_specific or prathiksha_intent in ["LIBRARY_TIMING", "COLLEGE_OFFICE_HOURS"]:
        conn = get_db_connection()
        cur = conn.cursor()

        if "library" in norm_query or prathiksha_intent == "LIBRARY_TIMING":
            cur.execute("SELECT name, weekday_timing, saturday_timing, sunday_timing, facilities FROM library LIMIT 1")
            lib = cur.fetchone()
            conn.close()

            title = lib["name"] if lib else "Central Library"
            weekday = lib["weekday_timing"] if lib else "8:30 AM to 5:15 PM"
            sat = lib["saturday_timing"] if lib else "8:30 AM to 1:00 PM"
            desc = f"Monday to Friday: {weekday}. Saturday: {sat}. Official holidays closed."
            speech = f"The library is open from {weekday} on weekdays, and {sat} on Saturdays."

            # Calculate route to library as supplementary info
            nav_data = get_directions("library", start_location_query=extracted_origin)

            return {
                "status": "success",
                "query": raw_query,
                "intent": "timing",
                "speech_text": speech,
                "primary_result": {
                    "title": title,
                    "subtitle": "Library Working Hours",
                    "description": desc,
                    "walk_time": f"{nav_data.get('estimated_time_minutes', 1)} min",
                    "distance": f"{nav_data.get('total_distance_meters', 20)}m",
                    "status_badge": "TIMINGS",
                    "floor_info": "Block B · 2nd Floor",
                    "hours": weekday,
                    "steps": nav_data.get("steps", [])
                },
                "secondary_result": get_nearby_secondary_location("library"),
                "navigation_details": nav_data
            }

        # College Office Hours
        cur.execute("SELECT name, information FROM campus_info WHERE name LIKE '%Office%' OR information LIKE '%hour%' OR information LIKE '%timing%' LIMIT 1")
        off = cur.fetchone()
        conn.close()

        timing_text = off["information"] if off else "The College Office operates from 8:30 AM to 6:00 PM from Monday to Saturday."
        speech = timing_text

        nav_data = get_directions("admin_block", start_location_query=extracted_origin)

        return {
            "status": "success",
            "query": raw_query,
            "intent": "timing",
            "speech_text": speech,
            "primary_result": {
                "title": "College Office Hours",
                "subtitle": "Administrative Block",
                "description": timing_text,
                "walk_time": "1 min",
                "distance": f"{nav_data.get('total_distance_meters', 10)}m",
                "status_badge": "HOURS",
                "floor_info": "Admin Block · Ground Floor",
                "hours": "Mon-Sat 8:30 AM - 6:00 PM",
                "steps": nav_data.get("steps", [])
            },
            "secondary_result": {
                "title": "Fee Payment Counter",
                "location": "Admin Block · 1st Floor",
                "details": "Fee collection, challans, and accounts office.",
                "walk_time": "1 min",
                "tag": "RELATED OFFICE"
            },
            "navigation_details": nav_data
        }

    # ---------------------------------------------------------
    # 5. ADMISSION / COURSES / SCHOLARSHIP / GENERAL INFO
    # ---------------------------------------------------------
    # Admissions
    if "admission" in norm_query or prathiksha_intent == "ADMISSION":
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT name, location, timing, information FROM admissions LIMIT 1")
        adm = cur.fetchone()
        conn.close()

        title = adm["name"] if adm else "Admission Office"
        location = adm["location"] if adm else "Administrative Block"
        timing = adm["timing"] if adm else "8:30 AM - 6:00 PM"
        info = adm["information"] if adm else "Admission process and applications are handled through the College Office."
        speech = f"Admissions are handled at the College Office in the Administrative Block from {timing}."

        nav_data = get_directions("admin_block", start_location_query=extracted_origin)

        return {
            "status": "success",
            "query": raw_query,
            "intent": "admission",
            "speech_text": speech,
            "primary_result": {
                "title": title,
                "subtitle": location,
                "description": info,
                "walk_time": f"{nav_data.get('estimated_time_minutes', 1)} min",
                "distance": f"{nav_data.get('total_distance_meters', 10)}m",
                "status_badge": "ADMISSIONS",
                "floor_info": "Admin Block · Ground Floor",
                "hours": timing,
                "steps": nav_data.get("steps", [])
            },
            "secondary_result": {
                "title": "Academic Programs",
                "location": "BA, BSc, BCom, BBA, BCA",
                "details": "Undergraduate degree programs affiliated with Mangalore University.",
                "walk_time": "",
                "tag": "PROGRAMS"
            },
            "navigation_details": nav_data
        }

    # Courses offered
    if "course" in norm_query or "courses" in norm_query or "degree" in norm_query or prathiksha_intent == "COURSES":
        courses_text = "The college offers undergraduate degrees in BA, BSc, BCom, BBA, and BCA across arts, commerce, and science streams."
        speech = courses_text

        nav_data = get_directions("block_b", start_location_query=extracted_origin)

        return {
            "status": "success",
            "query": raw_query,
            "intent": "courses",
            "speech_text": speech,
            "primary_result": {
                "title": "Academic Programs & Courses",
                "subtitle": "Undergraduate Streams",
                "description": courses_text,
                "walk_time": "2 min",
                "distance": f"{nav_data.get('total_distance_meters', 60)}m",
                "status_badge": "COURSES",
                "floor_info": "Block A & Block B",
                "hours": "Academic Year Schedule",
                "steps": nav_data.get("steps", [])
            },
            "secondary_result": {
                "title": "BCA & Computer Science Block",
                "location": "Block B",
                "details": "Department offering modern computer applications curriculum.",
                "walk_time": "2 min",
                "tag": "SPOTLIGHT"
            },
            "navigation_details": nav_data
        }

    # Search database for specific keyword match (Department, office, scholarship, placement)
    db_matches = search_all_database(norm_query)
    if not db_matches:
        # Try extracting nouns or keywords
        words = [w for w in norm_query.split() if len(w) > 3 and w not in ["where", "what", "which", "find", "tell", "about", "there"]]
        for w in words:
            db_matches = search_all_database(w)
            if db_matches:
                break

    if db_matches:
        top_match = db_matches[0]
        title = top_match["title"]
        loc = top_match["location"] or "Campus Ground"
        floor = top_match["floor"] or ""
        desc = top_match["details"] or f"Located at {loc}."
        
        # Map location to graph node for directions
        graph_node = map_to_graph_node(loc) or map_to_graph_node(title) or "admin_block"
        nav_data = get_directions(graph_node, start_location_query=extracted_origin)

        speech = f"{title} is located in {loc}. {desc}"

        return {
            "status": "success",
            "query": raw_query,
            "intent": top_match["table"],
            "speech_text": speech,
            "primary_result": {
                "title": title,
                "subtitle": f"{loc} {('· ' + floor) if floor else ''}".strip(),
                "description": desc,
                "walk_time": f"{nav_data.get('estimated_time_minutes', 1)} min",
                "distance": f"{nav_data.get('total_distance_meters', 40)}m",
                "status_badge": top_match["table"].upper(),
                "floor_info": floor or loc,
                "hours": "College hours: 8:30 AM - 5:15 PM",
                "steps": nav_data.get("steps", [])
            },
            "secondary_result": get_nearby_secondary_location(graph_node),
            "navigation_details": nav_data
        }

    # ---------------------------------------------------------
    # 6. PRATHIKSHA NLP FALLBACK OR UNKNOWN
    # ---------------------------------------------------------
    if prathiksha_data.get("intent") != "UNKNOWN":
        p_response = prathiksha_data.get("response", "")
        p_dest = prathiksha_data.get("destination")
        graph_node = map_to_graph_node(p_dest) if p_dest else "admin_block"
        nav_data = get_directions(graph_node, start_location_query=extracted_origin) if p_dest else None

        return {
            "status": "success",
            "query": raw_query,
            "intent": prathiksha_data.get("intent", "college_info"),
            "speech_text": p_response,
            "primary_result": {
                "title": (p_dest.replace("_", " ").title() if p_dest else "Campus Information"),
                "subtitle": CAMPUS_LOCATIONS.get(graph_node, {}).get("block", "Campus"),
                "description": p_response,
                "walk_time": f"{nav_data.get('estimated_time_minutes', 1)} min" if nav_data else "",
                "distance": f"{nav_data.get('total_distance_meters', 20)}m" if nav_data else "",
                "status_badge": "CAMPUS INFO",
                "floor_info": CAMPUS_LOCATIONS.get(graph_node, {}).get("block", ""),
                "hours": "Working days: 8:30 AM - 5:15 PM",
                "steps": nav_data.get("steps", []) if nav_data else []
            },
            "secondary_result": get_nearby_secondary_location(graph_node if graph_node else "admin_block"),
            "navigation_details": nav_data
        }

    # Default friendly fallback
    speech_fallback = "Sorry, I could not find a specific match for your question. You can ask for locations like the Library, Canteen, BCA Department, Principal's Office, or timings."
    return {
        "status": "unknown",
        "query": raw_query,
        "intent": "unknown",
        "speech_text": speech_fallback,
        "primary_result": {
            "title": "Bhandarkars' College Campus Guide",
            "subtitle": "Need help finding something?",
            "description": "I didn't quite catch that. Try asking:\n• 'Where is the library?'\n• 'How to reach the canteen?'\n• 'Where is the BCA department?'\n• 'What are the library timings?'",
            "walk_time": "",
            "distance": "",
            "status_badge": "HELP",
            "floor_info": "Admin Block Kiosk",
            "hours": "Always at your service",
            "steps": []
        },
        "secondary_result": {
            "title": "Administrative Office",
            "location": "Admin Block · Ground Floor",
            "details": "Visit the central office for staff assistance and student inquiries.",
            "walk_time": "1 min",
            "tag": "CAMPUS HELP"
        },
        "navigation_details": None
    }


if __name__ == "__main__":
    print("Testing Integration Engine...")
    test_queries = [
        "Where is the library?",
        "When does the library open?",
        "How do I get to the canteen?",
        "Where is the principal's office?",
        "Where is the BCA department?",
        "Where is the library and canteen?",
        "What are the emergency numbers?",
        "What courses are offered?",
        "Where can I find Chemistry department?"
    ]
    for q in test_queries:
        res = process_kiosk_query(q)
        print(f"\n[Query] {q}")
        print(f" Intent: {res['intent']}")
        print(f" Title:  {res['primary_result']['title']}")
        print(f" Speech: {res['speech_text']}")
        if res.get("navigation_details"):
            print(f" Route:  {res['primary_result']['distance']} ({res['primary_result']['walk_time']}) - {len(res['primary_result'].get('steps', []))} steps")
