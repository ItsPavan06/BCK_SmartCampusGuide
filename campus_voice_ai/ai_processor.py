# ai_processor.py

import re
from campus_data import campus_data


def preprocess_query(query):
    """
    Convert the user's query into a standard form.
    """

    query = query.lower()

    # Remove apostrophes
    query = query.replace("'", "")

    # Remove special characters
    query = re.sub(r"[^a-zA-Z0-9\s]", " ", query)

    # Remove extra spaces
    query = re.sub(r"\s+", " ", query).strip()

    return query


def keyword_matches(query, keyword):
    """
    Check whether a keyword or phrase exists in the query.
    """

    keyword = preprocess_query(keyword)

    if not keyword:
        return False

    # Match complete words/phrases
    pattern = r"\b" + re.escape(keyword) + r"\b"

    return re.search(pattern, query) is not None


def identify_intent(query):
    """
    Identify the most relevant campus intent.

    Longer and more specific keywords receive higher scores.
    """

    query = preprocess_query(query)

    best_intent = "UNKNOWN"
    best_score = 0

    for intent, information in campus_data.items():

        score = 0

        for keyword in information["keywords"]:

            keyword = preprocess_query(keyword)

            if keyword_matches(query, keyword):

                # Give higher weight to longer phrases
                words = len(keyword.split())

                if words >= 3:
                    score += 5
                elif words == 2:
                    score += 3
                else:
                    score += 1

        if score > best_score:
            best_score = score
            best_intent = intent

    return best_intent, best_score


def generate_response(query):
    """
    Generate a response based on the identified intent.
    """

    intent, score = identify_intent(query)

    if intent == "UNKNOWN":

        return {
            "query": query,
            "intent": "UNKNOWN",
            "matching_score": 0,
            "response": (
                "Sorry, I could not understand your question. "
                "Please ask about campus locations or information."
            ),
            "destination": None,
            "type": "unknown"
        }

    information = campus_data[intent]

    return {
        "query": query,
        "intent": intent,
        "matching_score": score,
        "response": information["response"],
        "destination": information["destination"],
        "type": information["type"]
    }


def process_query(query):
    """
    Main function used by other modules.
    """

    if not query or not query.strip():

        return {
            "query": query,
            "intent": "UNKNOWN",
            "matching_score": 0,
            "response": "Please enter a question.",
            "destination": None,
            "type": "unknown"
        }

    return generate_response(query)


# =========================================================
# MANUAL TESTING
# =========================================================

if __name__ == "__main__":

    print("--------------------------------------")
    print(" Smart Campus AI / NLP Module")
    print("--------------------------------------")

    while True:

        query = input("\nAsk your question: ")

        if query.lower() in ["exit", "quit", "stop"]:
            print("AI module stopped.")
            break

        result = process_query(query)

        print("\nIntent         :", result["intent"])
        print("Matching Score :", result["matching_score"])
        print("Destination    :", result["destination"])
        print("Type           :", result["type"])
        print("Response       :", result["response"])
