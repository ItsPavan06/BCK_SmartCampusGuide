"""
intent.py
---------
This module analyzes natural language text queries to determine user intent
(such as 'navigation' or 'college_info') and orchestrates destination extraction.
"""

import re
from typing import Dict, Any, Optional, Union, List
from destinations import extract_destination, extract_origin_and_destination, normalize_text

# Regex patterns identifying navigation-oriented questions and commands
NAVIGATION_PATTERNS = [
    r"\bwhere\s+is\b",
    r"\bwhere\s+are\b",
    r"\bwhere's\b",
    r"\bwhere\s+can\s+i\b",
    r"\bwhere\s+can\s+we\b",
    r"\bwhere\s+can\s+i\s+find\b",
    r"\bwhere\s+to\b",
    r"\bwhere\s+should\s+i\b",
    r"\bhow\s+do\s+i\s+get\s+to\b",
    r"\bhow\s+can\s+i\s+get\s+to\b",
    r"\bhow\s+to\s+get\s+to\b",
    r"\bhow\s+to\s+reach\b",
    r"\btake\s+me\s+to\b",
    r"\bshow\s+me\s+the\s+way\s+to\b",
    r"\bdirections?\s+to\b",
    r"\bway\s+to\b",
    r"\broute\s+to\b",
    r"\blocation\s+of\b",
    r"\bguide\s+me\s+to\b",
    r"\blead\s+me\s+to\b",
    r"\bnavigate\s+to\b",
    r"\bfind\s+the\b",
    r"\bhow\s+do\s+i\s+reach\b",
    r"\bvisit\b",
    r"\bgo\s+to\b",
    r"\bhow\s+can\s+i\s+visit\b",
    r"\bplace\s+to\b",
    r"\blooking\s+for\b",
    r"\bwant\s+to\b",
]

# Regex patterns identifying informational queries about college operations
COLLEGE_INFO_PATTERNS = [
    r"\bwhen\s+does\b",
    r"\bwhen\s+is\b",
    r"\bwhen\s+will\b",
    r"\btimings?\b",
    r"\bhours?\b",
    r"\breopen\b",
    r"\breopening\b",
    r"\bopen\b",
    r"\bclose\b",
    r"\bholiday\b",
    r"\bvacation\b",
    r"\badmission\b",
    r"\bfees?\b",
    r"\bfee\s+structure\b",
    r"\bexam\b",
    r"\bexaminations?\b",
    r"\bschedule\b",
    r"\bsyllabus\b",
    r"\beligibility\b",
    r"\bcontact\s+number\b",
    r"\bphone\s+number\b",
    r"\bemail\b",
    r"\bwho\s+is\b",
    r"\bprincipal\s+name\b",
]


def is_college_info_query(normalized_text: str) -> bool:
    """
    Checks if the query matches general college information patterns
    (e.g., timings, dates, admissions, exams).
    """
    for pattern in COLLEGE_INFO_PATTERNS:
        if re.search(pattern, normalized_text):
            return True
    return False


def is_navigation_query(normalized_text: str) -> bool:
    """
    Checks if the query contains navigational phrasing or direction requests.
    """
    for pattern in NAVIGATION_PATTERNS:
        if re.search(pattern, normalized_text):
            return True
    return False


def detect_intent_and_destination(query: str) -> Dict[str, Any]:
    """
    Analyzes the transcribed query to determine the intent, origin, and destination(s).
    """
    if not query or not query.strip():
        return {"intent": "unknown", "origin": None, "destination": None}

    normalized = normalize_text(query)
    extracted_origin, extracted_dest = extract_origin_and_destination(query)

    # 1. If query contains navigation phrasing AND a matched destination, prioritize navigation!
    if is_navigation_query(normalized) and extracted_dest is not None:
        return {
            "intent": "navigation",
            "origin": extracted_origin,
            "destination": extracted_dest
        }

    # 2. Informational queries (timings, exam dates, fee structure questions without direction intent)
    if is_college_info_query(normalized):
        return {
            "intent": "college_info",
            "origin": None,
            "destination": None
        }

    # 3. Navigation queries fallback (matches navigation phrase OR known destination)
    if is_navigation_query(normalized) or extracted_dest is not None or extracted_origin is not None:
        return {
            "intent": "navigation",
            "origin": extracted_origin,
            "destination": extracted_dest
        }

    # 4. Default fallback for general or unrecognized queries
    return {
        "intent": "college_info",
        "origin": None,
        "destination": None
    }
