import sqlite3
import os


# =========================================================
# DATABASE LOCATION
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "campus.db")


# =========================================================
# CREATE DATABASE AND TABLES
# =========================================================

def create_database():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # -----------------------------------------------------
    # DEPARTMENTS
    # -----------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT,
        floor TEXT,
        details TEXT
    )
    """)

    # -----------------------------------------------------
    # LOCATIONS
    # -----------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT,
        details TEXT
    )
    """)

    # -----------------------------------------------------
    # OFFICES
    # -----------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS offices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT,
        floor TEXT,
        details TEXT
    )
    """)

    # -----------------------------------------------------
    # LIBRARY
    # -----------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS library (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT,
        floor TEXT,
        weekday_timing TEXT,
        saturday_timing TEXT,
        sunday_timing TEXT,
        facilities TEXT
    )
    """)

    # -----------------------------------------------------
    # ADMISSIONS
    # -----------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT,
        timing TEXT,
        information TEXT
    )
    """)

    # -----------------------------------------------------
    # EMERGENCY
    # -----------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emergency (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service TEXT NOT NULL,
        contact TEXT,
        information TEXT
    )
    """)

    # -----------------------------------------------------
    # CAMPUS INFORMATION
    # -----------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS campus_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        information TEXT
    )
    """)

    # -----------------------------------------------------
    # SCHOLARSHIPS
    # -----------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scholarships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        eligibility TEXT,
        information TEXT
    )
    """)

    # -----------------------------------------------------
    # PLACEMENTS
    # -----------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS placements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT NOT NULL,
        program TEXT,
        course TEXT,
        year TEXT,
        students TEXT
    )
    """)

    connection.commit()
    connection.close()

    print("Database and tables created successfully!")


# =========================================================
# INSERT CAMPUS DATA
# =========================================================

def insert_campus_data():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Clear old data so repeated execution does not duplicate
    # campus records.

    tables = [
        "departments",
        "locations",
        "offices",
        "library",
        "admissions",
        "emergency",
        "campus_info",
        "scholarships",
        "placements"
    ]

    for table in tables:
        cursor.execute(f"DELETE FROM {table}")

    # =====================================================
    # DEPARTMENTS
    # =====================================================

    departments = [

        (
            "BCA",
            "BCA Block",
            "First Floor",
            "BCA staff room is on the first floor."
        ),

        (
            "Chemistry Department",
            "BCA Block",
            "Ground Floor",
            "Centre of the block."
        ),

        (
            "Hindi Department",
            "BCA Block",
            "Centre",
            "Located at the centre of BCA Block."
        ),

        (
            "Sanskrit Department",
            "BCA Block",
            "",
            "Beside Hindi Department."
        ),

        (
            "BM Department",
            "Admin Block",
            "First Floor",
            "Located on the first floor of Admin Block."
        ),

        (
            "Kannada Department",
            "Admin Block",
            "First Floor",
            "Opposite side, first floor right."
        ),

        (
            "Physics Department & Laboratory",
            "Admin Block",
            "",
            "Right side of Kannada Department."
        ),

        (
            "Botany Department & Lab",
            "",
            "Second Floor",
            "Left side / near porch."
        ),

        (
            "Zoology Lab & Department",
            "",
            "",
            "Opposite Botany Department."
        ),

        (
            "Psychology & Journalism",
            "",
            "Second Floor",
            "Near / adjacent to room 912."
        ),

        (
            "Maths Department",
            "",
            "",
            "Near room 215."
        ),

        (
            "Statistics Department",
            "",
            "",
            "Beside Maths Department."
        ),

        (
            "History & Sociology",
            "",
            "First Floor",
            "Located on the first floor."
        ),

        (
            "Kannada Department",
            "",
            "",
            "Near room 207."
        )
    ]

    cursor.executemany("""
    INSERT INTO departments
    (name, location, floor, details)
    VALUES (?, ?, ?, ?)
    """, departments)

    # =====================================================
    # LOCATIONS
    # =====================================================

    locations = [

        (
            "BCA Lab 1",
            "BCA Block",
            "First Floor - 84 computers"
        ),

        (
            "BCA Lab 2",
            "BCA Block",
            "First Floor - 84 computers"
        ),

        (
            "BCA Lab 3",
            "BCA Block",
            "First Floor - 55 computers"
        ),

        (
            "BCA Lab 4",
            "BCA Block",
            "First Floor - 60 computers"
        ),

        (
            "BCA Lab 5",
            "BCA Block",
            "First Floor - 30 computers"
        ),

        (
            "PUC Lab",
            "BCA Block",
            "Near staff room"
        ),

        (
            "Innovation Council / Student Project",
            "Campus",
            "Centre"
        ),

        (
            "Canteen",
            "Near BCA Block Gate",
            "Straight then left"
        ),

        (
            "Parking",
            "Near BCA Block Gate",
            "Straight then right"
        ),

        (
            "Library",
            "Near BCA Block Gate",
            "Near BCA block gate"
        ),

        (
            "Boys Indoor",
            "Near RN Shetty Hall",
            ""
        ),

        (
            "Girls Indoor",
            "Backside of Library",
            ""
        ),

        (
            "Girls Hostel",
            "Beside Girls Indoor",
            ""
        ),

        (
            "Boys Hostel",
            "Near Koya Kutty Hall",
            ""
        )
    ]

    cursor.executemany("""
    INSERT INTO locations
    (name, location, details)
    VALUES (?, ?, ?)
    """, locations)

    # =====================================================
    # OFFICES
    # =====================================================

    offices = [

        (
            "Principal Chamber",
            "Admin Block",
            "First Floor",
            "Principal office."
        ),

        (
            "Fee Payment Office",
            "Admin Block",
            "First Floor",
            "Fee payment services."
        ),

        (
            "Admission Office",
            "Admin Block",
            "First Floor",
            "Admission services."
        ),

        (
            "Scholarship Help",
            "Admin Block",
            "First Floor",
            "Scholarship assistance."
        ),

        (
            "Student Service Centre",
            "Admin Block",
            "Ground Floor",
            "Student and staff services."
        ),

        (
            "Career Guidance Room",
            "BCA Block",
            "Ground Floor",
            "Career guidance and placement support."
        )
    ]

    cursor.executemany("""
    INSERT INTO offices
    (name, location, floor, details)
    VALUES (?, ?, ?, ?)
    """, offices)

    # =====================================================
    # LIBRARY
    # =====================================================

    cursor.execute("""
    INSERT INTO library
    (
        name,
        location,
        floor,
        weekday_timing,
        saturday_timing,
        sunday_timing,
        facilities
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "Library",
        "Library Block / Near BCA Block Gate",
        "Second Floor",
        "8:00 AM - 5:15 PM",
        "8:00 AM - 1:30 PM",
        "Closed",
        "Library and learning resources"
    ))

    # =====================================================
    # ADMISSION
    # =====================================================

    cursor.execute("""
    INSERT INTO admissions
    (name, location, timing, information)
    VALUES (?, ?, ?, ?)
    """, (
        "Admission Office",
        "Admin Block - First Floor",
        "Monday-Friday: 9:15 AM - 5:15 PM; Saturday: 9:15 AM - 1:00 PM",
        "Admission and application assistance."
    ))

    # =====================================================
    # EMERGENCY
    # =====================================================

    emergency_data = [

        (
            "Emergency",
            "112",
            "India emergency response number."
        ),

        (
            "Ambulance",
            "108",
            "Ambulance emergency service."
        ),

        (
            "Government Hospital",
            "08254-234808",
            "Sub-Divisional Hospital, Kundapura."
        ),

        (
            "Police",
            "100",
            "Police emergency number."
        ),

        (
            "Fire & Emergency",
            "101",
            "Fire and emergency service."
        ),

        (
            "First Aid",
            "Not specified",
            "Specific campus first-aid information was not specified."
        ),

        (
            "Security",
            "Not specified",
            "Specific campus security information was not specified."
        )
    ]

    cursor.executemany("""
    INSERT INTO emergency
    (service, contact, information)
    VALUES (?, ?, ?)
    """, emergency_data)

    # =====================================================
    # CAMPUS INFORMATION
    # =====================================================

    campus_data = [

        (
            "College Classes - Monday-Friday",
            "9:30 AM - 4:40 PM"
        ),

        (
            "College Classes - Saturday",
            "9:30 AM - 1:05 PM"
        ),

        (
            "Office - Monday-Friday",
            "9:15 AM - 5:15 PM"
        ),

        (
            "Office - Saturday",
            "9:15 AM - 1:00 PM"
        )
    ]

    cursor.executemany("""
    INSERT INTO campus_info
    (name, information)
    VALUES (?, ?)
    """, campus_data)

    # =====================================================
    # SCHOLARSHIPS
    # =====================================================

    scholarships = [

        (
            "Sir C.V. Raman Scholarship",
            "First Year B.Sc. students. Any two subjects among Physics, Chemistry, Mathematics, Botany and Zoology. SC/ST: 60%; others: 65%.",
            "Scholarship information from college project PDF."
        ),

        (
            "Scholarship for Physically Handicapped Students",
            "Physically handicapped students.",
            "Scholarship information from college project PDF."
        ),

        (
            "Sanchi Honnamma Scholarship",
            "Lady students with at least 45% marks in qualifying II PUC examination.",
            "Scholarship information from college project PDF."
        ),

        (
            "Other Backward Class Scholarship",
            "OBC students whose parents' annual income is not more than Rs. 11,000/-.",
            "Eligibility as stated in the supplied college PDF."
        ),

        (
            "E.B.L. to Group-I Category Students",
            "Group-I category students who come to the college within 5 km distance.",
            "Scholarship information from college project PDF."
        ),

        (
            "Smt. Seetha Bai Sridhar Godbole Memorial Scholarship",
            "Awarded by the Academy of General Education on the recommendation of the Principal.",
            "Scholarship information from college project PDF."
        ),

        (
            "Scholarship to Children of Beedi Workers",
            "Children of Beedi workers.",
            "Scholarship information from college project PDF."
        ),

        (
            "Bhandarkars' College Trust Scholarship",
            "Merit.",
            "Scholarship information from college project PDF."
        ),

        (
            "Heggunje Rajeeva Shetty Charitable Society Scholarship",
            "Merit-cum-means.",
            "Scholarship information from college project PDF."
        ),

        (
            "Post-Matric Scholarship to SC/ST Students",
            "SC/ST students are eligible.",
            "Scholarship information from college project PDF."
        )
    ]

    cursor.executemany("""
    INSERT INTO scholarships
    (name, eligibility, information)
    VALUES (?, ?, ?)
    """, scholarships)

    # =====================================================
    # PLACEMENTS
    # =====================================================

    placements = [

        (
            "Capgemini",
            "Placement",
            "BCA",
            "2024-25",
            "BCA III students"
        ),

        (
            "TCS - Smart",
            "Placement",
            "BCA",
            "2024-25",
            "BCA III students"
        ),

        (
            "Wipro (WLP)",
            "Placement",
            "BCA",
            "2024-25",
            "BCA III students"
        ),

        (
            "Cognizant",
            "Placement",
            "BCA",
            "2024-25",
            "BCA III students"
        ),

        (
            "TCS - Ignite",
            "Placement",
            "BCA",
            "2024-25",
            "BCA III students"
        ),

        (
            "TCS - BPS",
            "Placement",
            "B.Com",
            "2024-25",
            "B.Com students"
        ),

        (
            "TCS - BPS",
            "Placement",
            "BBA",
            "2024-25",
            "BBA students"
        ),

        (
            "Optum",
            "Placement",
            "B.Sc",
            "2024-25",
            "B.Sc students"
        )
    ]

    cursor.executemany("""
    INSERT INTO placements
    (company, program, course, year, students)
    VALUES (?, ?, ?, ?, ?)
    """, placements)

    connection.commit()
    connection.close()

    print("Campus data inserted successfully!")


# =========================================================
# ADD DATA
# =========================================================

def add_data(table, values):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    queries = {

        "departments": """
        INSERT INTO departments
        (name, location, floor, details)
        VALUES (?, ?, ?, ?)
        """,

        "locations": """
        INSERT INTO locations
        (name, location, details)
        VALUES (?, ?, ?)
        """,

        "offices": """
        INSERT INTO offices
        (name, location, floor, details)
        VALUES (?, ?, ?, ?)
        """,

        "library": """
        INSERT INTO library
        (name, location, floor, weekday_timing,
         saturday_timing, sunday_timing, facilities)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,

        "admissions": """
        INSERT INTO admissions
        (name, location, timing, information)
        VALUES (?, ?, ?, ?)
        """,

        "emergency": """
        INSERT INTO emergency
        (service, contact, information)
        VALUES (?, ?, ?)
        """,

        "campus_info": """
        INSERT INTO campus_info
        (name, information)
        VALUES (?, ?)
        """,

        "scholarships": """
        INSERT INTO scholarships
        (name, eligibility, information)
        VALUES (?, ?, ?)
        """,

        "placements": """
        INSERT INTO placements
        (company, program, course, year, students)
        VALUES (?, ?, ?, ?, ?)
        """
    }

    if table not in queries:
        print("Table not supported.")
        connection.close()
        return

    cursor.execute(queries[table], values)

    connection.commit()
    connection.close()

    print("Data added successfully!")


# =========================================================
# UPDATE DATA
# =========================================================

def update_data(table, record_id, values):

    columns = {

        "departments":
        "name=?, location=?, floor=?, details=?",

        "locations":
        "name=?, location=?, details=?",

        "offices":
        "name=?, location=?, floor=?, details=?",

        "library":
        """name=?, location=?, floor=?,
        weekday_timing=?, saturday_timing=?,
        sunday_timing=?, facilities=?""",

        "admissions":
        "name=?, location=?, timing=?, information=?",

        "emergency":
        "service=?, contact=?, information=?",

        "campus_info":
        "name=?, information=?",

        "scholarships":
        "name=?, eligibility=?, information=?",

        "placements":
        "company=?, program=?, course=?, year=?, students=?"
    }

    if table not in columns:
        print("Table not supported.")
        return

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    query = f"""
    UPDATE {table}
    SET {columns[table]}
    WHERE id=?
    """

    cursor.execute(query, (*values, record_id))

    connection.commit()
    connection.close()

    print("Data updated successfully!")


# =========================================================
# DELETE DATA
# =========================================================

def delete_data(table, record_id):

    allowed_tables = [
        "departments",
        "locations",
        "offices",
        "library",
        "admissions",
        "emergency",
        "campus_info",
        "scholarships",
        "placements"
    ]

    if table not in allowed_tables:
        print("Table not supported.")
        return

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        f"DELETE FROM {table} WHERE id=?",
        (record_id,)
    )

    connection.commit()
    connection.close()

    print("Data deleted successfully!")


# =========================================================
# SEARCH DATA
# =========================================================

def search_data(keyword):

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    value = "%" + keyword + "%"
    results = []

    # Departments

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

    # Locations

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

    # Offices

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

    # Library

    cursor.execute("""
    SELECT name, location, floor,
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
        value, value, value, value,
        value, value, value
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

    # Admissions

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

    # Emergency

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

    # Campus Information

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

    # Scholarships

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

    # Placements

    cursor.execute("""
    SELECT company, program, course, year, students
    FROM placements
    WHERE company LIKE ?
       OR program LIKE ?
       OR course LIKE ?
       OR year LIKE ?
       OR students LIKE ?
    """, (value, value, value, value, value))

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

    return results


# =========================================================
# GET LOCATION
# =========================================================

def get_location(name):

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    value = "%" + name + "%"

    # Offices

    cursor.execute("""
    SELECT name, location, floor, details
    FROM offices
    WHERE name LIKE ?
       OR location LIKE ?
    LIMIT 1
    """, (value, value))

    row = cursor.fetchone()

    if row:
        connection.close()
        return dict(row)

    # Departments

    cursor.execute("""
    SELECT name, location, floor, details
    FROM departments
    WHERE name LIKE ?
       OR location LIKE ?
    LIMIT 1
    """, (value, value))

    row = cursor.fetchone()

    if row:
        connection.close()
        return dict(row)

    # Locations

    cursor.execute("""
    SELECT name, location, details
    FROM locations
    WHERE name LIKE ?
       OR location LIKE ?
    LIMIT 1
    """, (value, value))

    row = cursor.fetchone()

    if row:
        connection.close()
        return dict(row)

    # Admissions

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
        return dict(row)

    # Library

    cursor.execute("""
    SELECT name, location, floor, facilities
    FROM library
    WHERE name LIKE ?
       OR location LIKE ?
    LIMIT 1
    """, (value, value))

    row = cursor.fetchone()

    connection.close()

    if row:
        return dict(row)

    return None


# =========================================================
# GET TIMING
# =========================================================

def get_timing(name):

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    value = "%" + name + "%"

    # Library

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

        return {
            "name": row["name"],
            "Monday-Friday": row["weekday_timing"],
            "Saturday": row["saturday_timing"],
            "Sunday": row["sunday_timing"]
        }

    # Admissions

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

        return {
            "name": row["name"],
            "timing": row["timing"],
            "information": row["information"]
        }

    # Campus Information

    cursor.execute("""
    SELECT name, information
    FROM campus_info
    WHERE name LIKE ?
       OR information LIKE ?
    """, (value, value))

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    # Remove the old database once and recreate it.
    # This guarantees that the database schema is correct.

    if os.path.exists(DATABASE):

        os.remove(DATABASE)

        print("Old campus.db removed.")

    create_database()

    insert_campus_data()

    print()
    print("Database setup completed!")
    print("campus.db is ready!")
    print("Database location:")
    print(DATABASE)