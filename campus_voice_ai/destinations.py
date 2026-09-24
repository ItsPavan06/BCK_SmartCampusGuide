"""
destinations.py
---------------
This module manages the list of known college destinations and provides
functionality to extract single or multiple destination entities from user queries,
with support for aliases and typo tolerance.
"""

import re
import difflib
from typing import Optional, Dict, List, Union, Tuple

# Dictionary mapping canonical destination names to lists of recognizable aliases and synonyms.
# All alias phrases are in lowercase for case-insensitive matching.
COLLEGE_DESTINATIONS: Dict[str, List[str]] = {
    "library": [
        "library",
        "central library",
        "reading room",
        "book bank",
        "digital library",
        "read books",
        "read book",
        "read",
        "study",
        "study room",
        "borrow books",
        "quiet place",
        "books",
    ],
    "canteen": [
        "canteen",
        "cafeteria",
        "food court",
        "mess",
        "cafe",
        "snack bar",
        "eat",
        "eat food",
        "eat something",
        "get food",
        "have lunch",
        "have breakfast",
        "have snacks",
        "drink coffee",
        "coffee",
        "tea",
        "hungry",
        "food",
        "snacks",
        "refreshments",
    ],
    "principal's office": [
        "principal's office",
        "principals office",
        "principal office",
        "principal cabin",
        "principal room",
        "director's office",
        "director office",
        "principles of",
        "principle of",
        "principles office",
        "principle office",
        "principle s",
        "principal",
        "principle",
        "meet principal",
        "meet director",
        "principal appointment",
        "director",
        "head of college",
    ],
    "computer lab": [
        "computer lab",
        "cs lab",
        "computer laboratory",
        "programming lab",
        "it lab",
        "data center",
        "computer love",
        "computers lab",
        "computer labs",
        "use computer",
        "use computers",
        "coding",
        "programming",
        "lab exam",
        "internet access",
    ],
    "admin block": [
        "admin block",
        "admin office",
        "administration office",
        "administrative block",
        "admission office",
        "accounts section",
        "pay fee",
        "pay fees",
        "fee payment",
        "admissions",
        "submit documents",
        "marksheet",
        "certificates",
    ],
    "auditorium": [
        "auditorium",
        "seminar hall",
        "audi",
        "main auditorium",
        "conference hall",
        "college event",
        "functions",
        "events",
        "cultural fest",
        "seminar",
    ],
    "sports complex": [
        "sports complex",
        "gym",
        "gymnasium",
        "playground",
        "cricket ground",
        "football ground",
        "badminton court",
        "play games",
        "play sports",
        "play",
        "workout",
        "exercise",
        "fitness",
    ],
    "hostel": [
        "hostel",
        "boys hostel",
        "girls hostel",
        "dormitory",
        "student residence",
        "dorm",
        "stay",
        "sleep",
    ],
    "placement cell": [
        "placement cell",
        "training and placement cell",
        "tnp cell",
        "career center",
        "interview",
        "job placement",
        "campus drive",
        "placements",
    ],
    "parking": [
        "parking",
        "parking lot",
        "bike stand",
        "vehicle parking",
        "park bike",
        "park car",
        "park vehicle",
        "park my bike",
        "park my car",
    ],
}


def normalize_text(text: str) -> str:
    """
    Cleans and standardizes input text: converts to lowercase and
    replaces punctuation (except apostrophes in words) with spaces.
    """
    text = text.lower()
    # Replace punctuation with space, preserving alphanumeric and apostrophe
    text = re.sub(r"[^\w\s']", " ", text)
    # Collapse multiple whitespaces into a single space
    return " ".join(text.split())


def _build_alias_mapping() -> Dict[str, str]:
    """Builds a reverse map from every alias to its canonical destination name."""
    mapping = {}
    for canonical, aliases in COLLEGE_DESTINATIONS.items():
        for alias in aliases:
            mapping[alias.lower()] = canonical
    return mapping


ALIAS_TO_CANONICAL = _build_alias_mapping()


def extract_all_destinations(query: str) -> List[str]:
    """
    Extracts all unique canonical destinations mentioned in the query in order of appearance.
    Supports multi-destination sentences (e.g. "library and canteen") and typo tolerance (e.g. "libbrary").

    Parameters:
        query (str): The transcribed text query from the user.

    Returns:
        List[str]: List of canonical destination names found in the query.
    """
    if not query:
        return []

    normalized_query = normalize_text(query)
    found_matches: List[Tuple[int, str]] = []  # List of (start_index, canonical_name)
    matched_spans: List[Tuple[int, int]] = []  # List of (start_index, end_index)

    # 1. Exact alias matching (prioritizing longer phrases first to avoid sub-phrase conflicts)
    # Sort all aliases by length descending
    all_aliases = sorted(ALIAS_TO_CANONICAL.keys(), key=len, reverse=True)

    for alias in all_aliases:
        pattern = r"\b" + re.escape(alias) + r"\b"
        for match in re.finditer(pattern, normalized_query):
            start, end = match.span()
            # Check if this span overlaps with an already matched longer span
            overlap = any(s <= start < e or s < end <= e for s, e in matched_spans)
            if not overlap:
                canonical = ALIAS_TO_CANONICAL[alias]
                found_matches.append((start, canonical))
                matched_spans.append((start, end))

    # 2. Fuzzy matching for un-matched tokens (handles typos like "libbrary", "cantene")
    words = normalized_query.split()
    single_word_aliases = [a for a in ALIAS_TO_CANONICAL.keys() if " " not in a]

    for word in words:
        # Skip if word is very short or already part of a matched destination
        if len(word) < 4:
            continue

        # Check if the word is already covered by a matched span
        word_start = normalized_query.find(word)
        if word_start != -1:
            already_matched = any(s <= word_start < e for s, e in matched_spans)
            if already_matched:
                continue

        # Check fuzzy match against single-word destination aliases
        close_matches = difflib.get_close_matches(word, single_word_aliases, n=1, cutoff=0.75)
        if close_matches:
            matched_alias = close_matches[0]
            canonical = ALIAS_TO_CANONICAL[matched_alias]
            # Avoid duplicate canonical destinations if already found
            if not any(c == canonical for _, c in found_matches):
                found_matches.append((word_start, canonical))

    # Sort matches by appearance in sentence
    found_matches.sort(key=lambda x: x[0])

    # Return distinct canonical names in order of appearance
    seen = set()
    ordered_destinations = []
    for _, canonical in found_matches:
        if canonical not in seen:
            seen.add(canonical)
            ordered_destinations.append(canonical)

    return ordered_destinations


def extract_destination(query: str) -> Optional[Union[str, List[str]]]:
    """
    Extracts destination(s) from a text query.

    If a single destination is found, returns the string (e.g. 'library').
    If multiple destinations are found (e.g. 'library and canteen'), returns a list of strings.
    If no destination is found, returns None.

    Examples:
        >>> extract_destination("Where is the library?")
        'library'
        >>> extract_destination("Where is the libbrary and canteen?")
        ['library', 'canteen']
    """
    destinations = extract_all_destinations(query)
    if not destinations:
        return None
    if len(destinations) == 1:
        return destinations[0]
    return destinations


def extract_origin_and_destination(query: str) -> Tuple[Optional[str], Optional[Union[str, List[str]]]]:
    """
    Extracts both origin (starting location) and destination(s) from a text query.
    
    Examples:
        >>> extract_origin_and_destination("I am in canteen and I want to visit the principal's office")
        ('canteen', "principal's office")
        >>> extract_origin_and_destination("From canteen to library")
        ('canteen', 'library')
    """
    if not query:
        return None, None

    normalized = normalize_text(query)
    all_dests = extract_all_destinations(query)
    if not all_dests:
        return None, None

    # Check for origin phrases like "in canteen", "at library", "from canteen"
    origin_patterns = [
        r"\b(?:i am in|i'm in|i am at|i'm at|currently in|currently at|standing in|standing at|from)\s+([a-z0-9\s']+?)\s+(?:and|how|to|take|way|route|directions?|visit|go|reach|can)\b",
        r"\bfrom\s+([a-z0-9\s']+?)\s+to\b"
    ]

    detected_origin_canonical = None
    for pattern in origin_patterns:
        match = re.search(pattern, normalized)
        if match:
            phrase_segment = match.group(1)
            # Find if this segment contains a known destination alias
            origin_match = extract_destination(phrase_segment)
            if origin_match:
                if isinstance(origin_match, list):
                    detected_origin_canonical = origin_match[0]
                else:
                    detected_origin_canonical = origin_match
                break

    if detected_origin_canonical and detected_origin_canonical in all_dests:
        # Remove origin from destination list
        remaining_dests = [d for d in all_dests if d != detected_origin_canonical]
        if not remaining_dests:
            dest_result = None
        elif len(remaining_dests) == 1:
            dest_result = remaining_dests[0]
        else:
            dest_result = remaining_dests
        return detected_origin_canonical, dest_result

    # Default: first extracted destination if single, or all destinations
    if len(all_dests) == 1:
        return None, all_dests[0]
    return None, all_dests

