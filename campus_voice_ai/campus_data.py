# campus_data.py

campus_data = {

    # =========================================================
    # LOCATION
    # =========================================================

    "LIBRARY": {
        "keywords": [
            "library",
            "central library",
            "reading room",
            "book bank",
            "digital library",
            "books",
            "book",
            "read books",
            "read book",
            "reading",
            "read",
            "study",
            "study room",
            "borrow books",
            "borrow book",
            "borrow",
            "quiet place",
            "place to study",
            "place to read"
        ],
        "response": (
            "The library is in a separate building in front of "
            "the Computer Science Block."
        ),
        "destination": "library",
        "type": "location"
    },


    "BCA_LOCATION": {
        "keywords": [
            "bca",
            "bca department",
            "bca block",
            "computer science",
            "computer science department",
            "computer science block",
            "computer applications",
            "computer application department",
            "computer application block"
        ],
        "response": (
            "The BCA and Computer Science Department is in the "
            "Computer Science Block, located in front of the library."
        ),
        "destination": "bca department",
        "type": "location"
    },


    "PRINCIPAL_CHAMBER": {
        "keywords": [
            "principal",
            "principal office",
            "principal's office",
            "principal chamber",
            "principal's chamber",
            "office of principal",
            "where is principal"
        ],
        "response": (
            "The Principal's Chamber is located on the first floor "
            "of the Administrative Block."
        ),
        "destination": "principal chamber",
        "type": "location"
    },


    "CANTEEN": {
        "keywords": [
            "canteen",
            "food",
            "eat",
            "eating",
            "eat food",
            "get food",
            "have food",
            "lunch",
            "hungry",
            "food court",
            "place to eat",
            "place to have food",
            "where to eat",
            "where can i eat"
        ],
        "response": (
            "The canteen is located behind the Main Building, "
            "near the Computer Science Block, and has a separate entrance."
        ),
        "destination": "canteen",
        "type": "location"
    },


    "GIRLS_INDOOR_GAMES": {
        "keywords": [
            "girls indoor",
            "girls indoor games",
            "girls indoor game",
            "indoor games girls",
            "indoor game girls",
            "girls games"
        ],
        "response": (
            "The Girls' Indoor Games building is located behind the library."
        ),
        "destination": "girls indoor games",
        "type": "location"
    },


    "BOYS_INDOOR_GAMES": {
        "keywords": [
            "boys indoor",
            "boys indoor games",
            "boys indoor game",
            "indoor games boys",
            "indoor game boys",
            "boys games"
        ],
        "response": (
            "The Boys' Indoor Games building is located behind "
            "or to the right side of the Administrative Block."
        ),
        "destination": "boys indoor games",
        "type": "location"
    },


    "PLAYGROUND": {
        "keywords": [
            "playground",
            "sports ground",
            "sports field",
            "play area",
            "ground",
            "field",
            "play",
            "sports",
            "where to play"
        ],
        "response": (
            "The playground is located behind the Administrative Block."
        ),
        "destination": "playground",
        "type": "location"
    },


    "ADMISSION": {
        "keywords": [
            "admission",
            "admissions",
            "admission information",
            "admission process",
            "admission procedure",
            "apply for admission",
            "application",
            "how to apply",
            "how can i apply",
            "where to apply",
            "apply"
        ],
        "response": (
            "Admission is handled through the College Office "
            "in the Administrative Block."
        ),
        "destination": "college office",
        "type": "information"
    },


    # =========================================================
    # INFORMATION
    # =========================================================

    "LIBRARY_TIMING": {
        "keywords": [
            "library timing",
            "library timings",
            "library time",
            "library hours",
            "library opening time",
            "library closing time",
            "when does library open",
            "when is library open",
            "when does library close",
            "when is library closed",
            "library opens",
            "library closes",
            "what time is library",
            "library schedule",
            "library hours of operation",
            "library working hours",
            "library working time",
            "library opening hours",
            "library closing hours",
            "library open",
            "library close",
            "library open now"
        ],

        "response": (
            "The library is open from 8:30 AM to 5:15 PM "
            "on all official working days."
        ),
        "destination": None,
        "type": "information"
    },


    "COLLEGE_OFFICE_HOURS": {
        "keywords": [
            "college office timing",
            "college office timings",
            "college office time",
            "college office hours",
            "office timing",
            "office timings",
            "office hours",
            "office opening time",
            "office closing time",
            "when is college office open",
            "when does college office open",
            "when does office open",
            "what time is college office"
        ],
        "response": (
            "The College Office operates from 8:30 AM to 6:00 PM "
            "from Monday to Saturday."
        ),
        "destination": None,
        "type": "information"
    },


    "COURSES": {
        "keywords": [
            "courses",
            "course",
            "courses offered",
            "courses available",
            "degree courses",
            "programs",
            "programmes",
            "program",
            "what courses are offered",
            "what courses are available",
            "which courses are offered",
            "which courses are available",
            "what can i study"
        ],
        "response": (
            "The college offers BA, BSc, BCom, BBA, and BCA courses."
        ),
        "destination": None,
        "type": "information"
    }
}
