from flask import Flask, jsonify, request, send_from_directory, render_template
import sqlite3
import os
import sys

# =========================================================
# PATH CONFIGURATION & IMPORTS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
FRONTEND_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATABASE = os.path.join(BASE_DIR, "campus.db")

# Add roots to sys.path
for p in [ROOT_DIR, BASE_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from core.integration_engine import process_kiosk_query
except ImportError:
    process_kiosk_query = None

try:
    from arduino import iot_manager, start_iot_background_listener
except ImportError:
    iot_manager = None
    start_iot_background_listener = None


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__, template_folder=FRONTEND_DIR, static_folder=STATIC_DIR, static_url_path="")


# ---------------------------------------------------------
# CORS & STATIC ASSET HEADERS
# ---------------------------------------------------------

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# FRONTEND ROUTES
# =========================================================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/index.html")
def index_html():
    return render_template("index.html")


@app.route("/listening.html")
def listening_html():
    return render_template("listening.html")


@app.route("/results.html")
def results_html():
    return render_template("results.html")


@app.route("/favicon.ico")
def favicon():
    try:
        return send_from_directory(STATIC_DIR, "bcklogo.png", mimetype="image/png")
    except Exception:
        return jsonify({"error": "Favicon not available"}), 404


@app.route("/<path:path>")
def static_proxy(path):
    file_path = os.path.join(STATIC_DIR, path)
    if os.path.exists(file_path):
        return send_from_directory(STATIC_DIR, path)
    return jsonify({"error": "Not found"}), 404


@app.route("/api")
@app.route("/api/status")
def home():

    return jsonify({
        "project": "Smart Campus Guide & AI Help Desk",
        "message": "Backend is running successfully",
        "status": "OK"
    })


# =========================================================
# SEARCH API
#
# Example:
# /search/BCA
# =========================================================

@app.route("/search/<path:keyword>")
def search(keyword):

    connection = get_connection()
    cursor = connection.cursor()

    value = "%" + keyword + "%"

    results = []

    # -----------------------------------------------------
    # DEPARTMENTS
    # -----------------------------------------------------

    cursor.execute("""
        SELECT name, location, floor, details
        FROM departments
        WHERE name LIKE ?
           OR location LIKE ?
           OR floor LIKE ?
           OR details LIKE ?
    """, (value, value, value, value))

    for row in cursor.fetchall():

        results.append({
            "type": "department",
            "name": row["name"],
            "location": row["location"],
            "floor": row["floor"],
            "details": row["details"]
        })


    # -----------------------------------------------------
    # LOCATIONS
    # -----------------------------------------------------

    cursor.execute("""
        SELECT name, location, details
        FROM locations
        WHERE name LIKE ?
           OR location LIKE ?
           OR details LIKE ?
    """, (value, value, value))

    for row in cursor.fetchall():

        results.append({
            "type": "location",
            "name": row["name"],
            "location": row["location"],
            "details": row["details"]
        })


    # -----------------------------------------------------
    # OFFICES
    # -----------------------------------------------------

    cursor.execute("""
        SELECT name, location, floor, details
        FROM offices
        WHERE name LIKE ?
           OR location LIKE ?
           OR floor LIKE ?
           OR details LIKE ?
    """, (value, value, value, value))

    for row in cursor.fetchall():

        results.append({
            "type": "office",
            "name": row["name"],
            "location": row["location"],
            "floor": row["floor"],
            "details": row["details"]
        })


    # -----------------------------------------------------
    # LIBRARY
    # -----------------------------------------------------

    cursor.execute("""
        SELECT name,
               location,
               floor,
               weekday_timing,
               saturday_timing,
               sunday_timing,
               facilities
        FROM library
        WHERE name LIKE ?
           OR location LIKE ?
           OR floor LIKE ?
           OR weekday_timing LIKE ?
           OR saturday_timing LIKE ?
           OR sunday_timing LIKE ?
           OR facilities LIKE ?
    """, (
        value,
        value,
        value,
        value,
        value,
        value,
        value
    ))

    for row in cursor.fetchall():

        results.append({
            "type": "library",
            "name": row["name"],
            "location": row["location"],
            "floor": row["floor"],
            "weekday_timing": row["weekday_timing"],
            "saturday_timing": row["saturday_timing"],
            "sunday_timing": row["sunday_timing"],
            "facilities": row["facilities"]
        })


    # -----------------------------------------------------
    # ADMISSIONS
    # -----------------------------------------------------

    cursor.execute("""
        SELECT name, location, timing, information
        FROM admissions
        WHERE name LIKE ?
           OR location LIKE ?
           OR timing LIKE ?
           OR information LIKE ?
    """, (value, value, value, value))

    for row in cursor.fetchall():

        results.append({
            "type": "admission",
            "name": row["name"],
            "location": row["location"],
            "timing": row["timing"],
            "information": row["information"]
        })


    # -----------------------------------------------------
    # EMERGENCY
    # -----------------------------------------------------

    cursor.execute("""
        SELECT service, contact, information
        FROM emergency
        WHERE service LIKE ?
           OR contact LIKE ?
           OR information LIKE ?
    """, (value, value, value))

    for row in cursor.fetchall():

        results.append({
            "type": "emergency",
            "service": row["service"],
            "contact": row["contact"],
            "information": row["information"]
        })


    # -----------------------------------------------------
    # CAMPUS INFORMATION
    # -----------------------------------------------------

    cursor.execute("""
        SELECT name, information
        FROM campus_info
        WHERE name LIKE ?
           OR information LIKE ?
    """, (value, value))

    for row in cursor.fetchall():

        results.append({
            "type": "campus_info",
            "name": row["name"],
            "information": row["information"]
        })


    # -----------------------------------------------------
    # SCHOLARSHIPS
    # -----------------------------------------------------

    cursor.execute("""
        SELECT name, eligibility, information
        FROM scholarships
        WHERE name LIKE ?
           OR eligibility LIKE ?
           OR information LIKE ?
    """, (value, value, value))

    for row in cursor.fetchall():

        results.append({
            "type": "scholarship",
            "name": row["name"],
            "eligibility": row["eligibility"],
            "information": row["information"]
        })


    # -----------------------------------------------------
    # PLACEMENTS
    # -----------------------------------------------------

    cursor.execute("""
        SELECT company, program, course, year, students
        FROM placements
        WHERE company LIKE ?
           OR program LIKE ?
           OR course LIKE ?
           OR year LIKE ?
           OR students LIKE ?
    """, (
        value,
        value,
        value,
        value,
        value
    ))

    for row in cursor.fetchall():

        results.append({
            "type": "placement",
            "company": row["company"],
            "program": row["program"],
            "course": row["course"],
            "year": row["year"],
            "students": row["students"]
        })


    connection.close()


    return jsonify({
        "keyword": keyword,
        "count": len(results),
        "results": results
    })


# =========================================================
# LOCATION API
#
# Example:
# /location/BCA%20Lab%201
# =========================================================

@app.route("/location/<path:name>")
def location(name):

    connection = get_connection()
    cursor = connection.cursor()

    value = "%" + name + "%"


    # -----------------------------------------------------
    # LOCATIONS TABLE
    # -----------------------------------------------------

    cursor.execute("""
        SELECT name, location, details
        FROM locations
        WHERE name LIKE ?
           OR location LIKE ?
           OR details LIKE ?
        LIMIT 1
    """, (value, value, value))

    row = cursor.fetchone()

    if row:

        connection.close()

        return jsonify({
            "type": "location",
            "name": row["name"],
            "location": row["location"],
            "details": row["details"]
        })


    # -----------------------------------------------------
    # DEPARTMENTS TABLE
    # -----------------------------------------------------

    cursor.execute("""
        SELECT name, location, floor, details
        FROM departments
        WHERE name LIKE ?
           OR location LIKE ?
           OR floor LIKE ?
           OR details LIKE ?
        LIMIT 1
    """, (value, value, value, value))

    row = cursor.fetchone()

    if row:

        connection.close()

        return jsonify({
            "type": "department",
            "name": row["name"],
            "location": row["location"],
            "floor": row["floor"],
            "details": row["details"]
        })


    # -----------------------------------------------------
    # OFFICES TABLE
    # -----------------------------------------------------

    cursor.execute("""
        SELECT name, location, floor, details
        FROM offices
        WHERE name LIKE ?
           OR location LIKE ?
           OR floor LIKE ?
           OR details LIKE ?
        LIMIT 1
    """, (value, value, value, value))

    row = cursor.fetchone()

    if row:

        connection.close()

        return jsonify({
            "type": "office",
            "name": row["name"],
            "location": row["location"],
            "floor": row["floor"],
            "details": row["details"]
        })


    # -----------------------------------------------------
    # ADMISSIONS TABLE
    # -----------------------------------------------------

    cursor.execute("""
        SELECT name, location, timing, information
        FROM admissions
        WHERE name LIKE ?
           OR location LIKE ?
        LIMIT 1
    """, (value, value))

    row = cursor.fetchone()

    if row:

        connection.close()

        return jsonify({
            "type": "admission",
            "name": row["name"],
            "location": row["location"],
            "timing": row["timing"],
            "information": row["information"]
        })


    # -----------------------------------------------------
    # LIBRARY TABLE
    # -----------------------------------------------------

    cursor.execute("""
        SELECT name, location, floor, facilities
        FROM library
        WHERE name LIKE ?
           OR location LIKE ?
           OR floor LIKE ?
           OR facilities LIKE ?
        LIMIT 1
    """, (value, value, value, value))

    row = cursor.fetchone()

    connection.close()

    if row:

        return jsonify({
            "type": "library",
            "name": row["name"],
            "location": row["location"],
            "floor": row["floor"],
            "facilities": row["facilities"]
        })


    return jsonify({
        "message": "Location not found",
        "searched_for": name
    }), 404


# =========================================================
# TIMING API
#
# Example:
# /timing/Library
# =========================================================

@app.route("/timing/<path:name>")
def timing(name):

    connection = get_connection()
    cursor = connection.cursor()

    value = "%" + name + "%"


    # -----------------------------------------------------
    # LIBRARY
    # -----------------------------------------------------

    cursor.execute("""
        SELECT name,
               weekday_timing,
               saturday_timing,
               sunday_timing
        FROM library
        WHERE name LIKE ?
           OR location LIKE ?
        LIMIT 1
    """, (value, value))

    row = cursor.fetchone()

    if row:

        connection.close()

        return jsonify({
            "type": "library",
            "name": row["name"],
            "Monday-Friday": row["weekday_timing"],
            "Saturday": row["saturday_timing"],
            "Sunday": row["sunday_timing"]
        })


    # -----------------------------------------------------
    # ADMISSIONS
    # -----------------------------------------------------

    cursor.execute("""
        SELECT name, timing, information
        FROM admissions
        WHERE name LIKE ?
           OR location LIKE ?
        LIMIT 1
    """, (value, value))

    row = cursor.fetchone()

    if row:

        connection.close()

        return jsonify({
            "type": "admission",
            "name": row["name"],
            "timing": row["timing"],
            "information": row["information"]
        })


    # -----------------------------------------------------
    # CAMPUS INFORMATION
    # -----------------------------------------------------

    cursor.execute("""
        SELECT name, information
        FROM campus_info
        WHERE name LIKE ?
           OR information LIKE ?
    """, (value, value))

    rows = cursor.fetchall()

    connection.close()

    if rows:

        timing_list = []

        for row in rows:

            timing_list.append({
                "name": row["name"],
                "information": row["information"]
            })

        return jsonify({
            "type": "campus_info",
            "timings": timing_list
        })


    return jsonify({
        "message": "Timing information not found"
    }), 404


# =========================================================
# EMERGENCY API
#
# Example:
# /emergency
# =========================================================

@app.route("/emergency")
def emergency():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT service, contact, information
        FROM emergency
    """)

    rows = cursor.fetchall()

    connection.close()

    emergency_list = []

    for row in rows:

        emergency_list.append({
            "service": row["service"],
            "contact": row["contact"],
            "information": row["information"]
        })

    return jsonify({
        "count": len(emergency_list),
        "emergency_services": emergency_list
    })


# =========================================================
# QUESTION API
#
# AI/NLP TEAM WILL USE THIS LATER
#
# This backend does NOT contain AI/NLP.
# It simply receives their processed information.
# =========================================================

@app.route("/question", methods=["POST"])
def question():

    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "status": "error",
            "message": "JSON data is required"
        }), 400


    question_text = data.get("question")

    if not question_text:

        return jsonify({
            "status": "error",
            "message": "Question is required"
        }), 400


    # Process question through the integrated AI NLP & Navigation engine
    if process_kiosk_query:
        result = process_kiosk_query(question_text)
        return jsonify(result)

    return jsonify({
        "status": "success",
        "question": question_text,
        "message": "Question received by backend"
    })


# =========================================================
# UNIFIED KIOSK QUERY API
# =========================================================

@app.route("/api/query", methods=["POST", "OPTIONS"])
def api_query():
    """Main query endpoint for Kiosk Web Frontend and external clients."""
    if request.method == "OPTIONS":
        return "", 204

    data = request.get_json(silent=True) or {}
    query_text = data.get("query", "").strip()
    origin = data.get("origin")

    if not process_kiosk_query:
        return jsonify({
            "status": "error",
            "message": "Integration engine not loaded"
        }), 500

    result = process_kiosk_query(query_text, origin=origin)
    return jsonify(result)


# =========================================================
# SERVER MICROPHONE VOICE LISTEN API
# =========================================================

@app.route("/api/voice-listen", methods=["POST", "GET"])
def api_voice_listen():
    """Captures live audio from physical microphone on kiosk hardware via voice.py."""
    try:
        from voice import capture_speech_from_microphone, is_speech_recognition_available
        if not is_speech_recognition_available():
            return jsonify({
                "status": "browser_fallback_recommended",
                "message": "SpeechRecognition library not installed on host. Use browser Web Speech API."
            }), 200

        text = capture_speech_from_microphone(timeout=5, phrase_time_limit=10)
        if not text:
            return jsonify({
                "status": "no_speech",
                "message": "No speech detected within listening window."
            }), 200

        if process_kiosk_query:
            result = process_kiosk_query(text)
            result["recognized_text"] = text
            return jsonify(result)

        return jsonify({
            "status": "success",
            "recognized_text": text
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# =========================================================
# IOT PIR MOTION SENSOR APIS
# =========================================================

@app.route("/api/iot/status", methods=["GET"])
def api_iot_status():
    """Returns current state of PIR motion sensor."""
    if iot_manager:
        return jsonify(iot_manager.get_status())
    return jsonify({
        "state": "STANDBY",
        "connected": False,
        "port": "Unavailable"
    })


@app.route("/api/iot/trigger", methods=["POST"])
def api_iot_trigger():
    """Simulates or manually triggers a PIR motion sensor event."""
    data = request.get_json(silent=True) or {}
    message = data.get("message", "PERSON_DETECTED")

    if iot_manager:
        action = iot_manager.trigger_event(message)
        return jsonify({
            "status": "success",
            "message": message,
            "action": action,
            "iot_status": iot_manager.get_status()
        })

    return jsonify({
        "status": "error",
        "message": "IoT Manager not initialized"
    }), 500


# =========================================================
# CAMPUS DESTINATIONS & HEALTH
# =========================================================

@app.route("/api/destinations", methods=["GET"])
def api_destinations():
    """Returns all recognizable campus locations and aliases."""
    try:
        from navigation import CAMPUS_LOCATIONS
        return jsonify({
            "count": len(CAMPUS_LOCATIONS),
            "destinations": [
                {
                    "id": k,
                    "name": v["name"],
                    "block": v["block"],
                    "aliases": v["aliases"]
                }
                for k, v in CAMPUS_LOCATIONS.items()
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def api_health():
    """Health check for backend, database, and modules."""
    return jsonify({
        "status": "healthy",
        "database_exists": os.path.exists(DATABASE),
        "iot_status": iot_manager.get_status() if iot_manager else None,
        "integration_engine_ready": process_kiosk_query is not None
    })



# =========================================================
# AI/NLP RESULT API
#
# AI/NLP TEAM CAN SEND THEIR RESULT HERE
#
# Example JSON:
#
# {
#     "intent": "location",
#     "destination": "BCA Lab 1"
# }
#
# =========================================================

@app.route("/ai-result", methods=["POST"])
def ai_result():

    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "status": "error",
            "message": "JSON data is required"
        }), 400


    intent = data.get("intent")
    destination = data.get("destination")


    if not intent:

        return jsonify({
            "status": "error",
            "message": "Intent is required"
        }), 400


    # -----------------------------------------------------
    # LOCATION
    # -----------------------------------------------------

    if intent == "location" and destination:

        connection = get_connection()
        cursor = connection.cursor()

        value = "%" + destination + "%"


        # Locations

        cursor.execute("""
            SELECT name, location, details
            FROM locations
            WHERE name LIKE ?
               OR location LIKE ?
               OR details LIKE ?
            LIMIT 1
        """, (value, value, value))

        row = cursor.fetchone()

        if row:

            connection.close()

            return jsonify({
                "status": "success",
                "intent": intent,
                "result": {
                    "name": row["name"],
                    "location": row["location"],
                    "details": row["details"]
                }
            })


        # Departments

        cursor.execute("""
            SELECT name, location, floor, details
            FROM departments
            WHERE name LIKE ?
               OR location LIKE ?
               OR floor LIKE ?
               OR details LIKE ?
            LIMIT 1
        """, (value, value, value, value))

        row = cursor.fetchone()

        if row:

            connection.close()

            return jsonify({
                "status": "success",
                "intent": intent,
                "result": {
                    "name": row["name"],
                    "location": row["location"],
                    "floor": row["floor"],
                    "details": row["details"]
                }
            })


        # Offices

        cursor.execute("""
            SELECT name, location, floor, details
            FROM offices
            WHERE name LIKE ?
               OR location LIKE ?
               OR floor LIKE ?
               OR details LIKE ?
            LIMIT 1
        """, (value, value, value, value))

        row = cursor.fetchone()

        connection.close()

        if row:

            return jsonify({
                "status": "success",
                "intent": intent,
                "result": {
                    "name": row["name"],
                    "location": row["location"],
                    "floor": row["floor"],
                    "details": row["details"]
                }
            })


        return jsonify({
            "status": "not_found",
            "message": "Destination not found",
            "destination": destination
        }), 404


    # -----------------------------------------------------
    # EMERGENCY
    # -----------------------------------------------------

    if intent == "emergency":

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT service, contact, information
            FROM emergency
        """)

        rows = cursor.fetchall()

        connection.close()

        emergency_list = []

        for row in rows:

            emergency_list.append({
                "service": row["service"],
                "contact": row["contact"],
                "information": row["information"]
            })


        return jsonify({
            "status": "success",
            "intent": "emergency",
            "result": emergency_list
        })


    # -----------------------------------------------------
    # OTHER INTENTS
    # -----------------------------------------------------

    return jsonify({
        "status": "success",
        "intent": intent,
        "destination": destination,
        "message": "AI/NLP result received by backend"
    })


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    print("--------------------------------------")
    print(" Smart Campus Guide Backend")
    print("--------------------------------------")

    print("Database:")
    print(DATABASE)

    if not os.path.exists(DATABASE):

        print()
        print("ERROR: campus.db not found.")
        print("Run databasse.py first.")
        print()

    else:

        print("Database found.")
        if start_iot_background_listener:
            try:
                start_iot_background_listener()
                print("IoT PIR background monitor started.")
            except Exception as e:
                print(f"IoT start notice: {e}")
        print("Flask server starting at http://127.0.0.1:5000 ...")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )