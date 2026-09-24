# test_ai.py

from ai_processor import process_query


test_questions = [

    # Library
    "Where can I find the library?",
    "Where can I read books?",
    "Where can I study?",
    "Where can I borrow books?",

    # BCA
    "Where is the BCA department?",
    "Where is computer science?",

    # Principal
    "Where is the principal's office?",
    "Where is the principal chamber?",

    # Canteen
    "Where can I eat?",
    "Where is the canteen?",

    # Indoor games
    "Where are the girls indoor games?",
    "Where are the boys indoor games?",

    # Playground
    "Where is the playground?",
    "Where is the sports ground?",

    # Admission
    "Where can I get admission information?",
    "How can I apply for admission?",

    # Information
    "When does the library open?",
    "What are the library timings?",
    "When is the college office open?",
    "What are the college office hours?",
    "What courses are offered?",
    "Which courses are available?",

    # Unknown
    "Where is the science department?"
]


print("======================================")
print("       SMART CAMPUS AI/NLP TEST")
print("======================================")


for question in test_questions:

    result = process_query(question)

    print("\nQuestion       :", question)
    print("Intent         :", result["intent"])
    print("Matching Score :", result["matching_score"])
    print("Destination    :", result["destination"])
    print("Type           :", result["type"])
    print("Response       :", result["response"])
