"""
app.py
------
Main entry point for the College AI Help-Desk Voice Processing Module.

Pipeline Flow:
1. Microphone Audio Capture (voice.py)
2. Speech-to-Text Conversion (voice.py)
3. Intent Detection (intent.py)
4. Destination Extraction (destinations.py)
5. Structured JSON Output
"""

import json
import sys
from typing import Dict, Any

from voice import capture_speech_from_microphone, is_speech_recognition_available
from intent import detect_intent_and_destination
from tts import speak_text, generate_response_speech_text, is_tts_available
from navigation import get_directions


def run_pipeline(text: str) -> Dict[str, Any]:
    """
    Executes the NLU & Navigation processing pipeline on transcribed text.

    Pipeline:
    1. STT Transcribed text (Rakesh)
    2. Intent / Origin / Destination Extraction (Handoff contract to Prathiksha)
    3. Campus Route & Direction Calculation (Rakesh - navigation.py)
    """
    nlu_result = detect_intent_and_destination(text)
    intent = nlu_result.get("intent")
    origin = nlu_result.get("origin")
    destination = nlu_result.get("destination")

    nav_data = None
    if intent == "navigation" and destination:
        nav_data = get_directions(destination, start_location_query=origin)

    return {
        "intent": intent,
        "origin": origin,
        "destination": destination,
        "navigation_details": nav_data
    }


def print_banner():
    """Prints welcome banner and pipeline overview."""
    banner = r"""
============================================================
       COLLEGE AI HELP-DESK - VOICE & NAVIGATION MODULE       
============================================================
 Flow: Mic -> STT -> AI Payload -> Navigation Route -> TTS
============================================================
    """
    print(banner)


def handle_microphone_input(enable_tts: bool = True):
    """Captures speech from microphone and processes it through the pipeline."""
    print("\n--- [Microphone Input Mode] ---")
    query_text = capture_speech_from_microphone()

    if not query_text:
        print("[App] No valid speech input received. Please try again.\n")
        return

    print("\n[App] Processing Query...")
    result = run_pipeline(query_text)

    # Print structured JSON output
    print("\n--- [Structured Output] ---")
    print(json.dumps(result, indent=4))
    print("---------------------------\n")

    # Speak response out loud using TTS
    if enable_tts:
        nav_details = result.get("navigation_details")
        if nav_details and nav_details.get("status") == "success":
            speech_text = nav_details["directions_text"]
        else:
            speech_text = generate_response_speech_text(result.get("intent"), result.get("destination"))
        
        speak_text(speech_text)


def handle_text_input(enable_tts: bool = True):
    """Allows manual text input for quick testing and simulation."""
    print("\n--- [Text Simulation Mode] ---")
    user_query = input("Enter your question: ").strip()

    if not user_query:
        print("[App] Empty input. Aborted.\n")
        return

    print(f"\n[App] Input Text: \"{user_query}\"")
    result = run_pipeline(user_query)

    # Print structured JSON output
    print("\n--- [Structured Output] ---")
    print(json.dumps(result, indent=4))
    print("---------------------------\n")

    # Speak response out loud using TTS
    if enable_tts:
        nav_details = result.get("navigation_details")
        if nav_details and nav_details.get("status") == "success":
            speech_text = nav_details["directions_text"]
        else:
            speech_text = generate_response_speech_text(result.get("intent"), result.get("destination"))
        
        speak_text(speech_text)



def run_automated_tests():
    """Runs built-in sample queries to verify pipeline functionality."""
    print("\n--- [Running Sample Test Queries] ---")
    sample_queries = [
        "Where is the library?",
        "How do I get to the canteen?",
        "Where is the principal's office?",
        "Take me to the computer lab.",
        "Where is the library and canteen?",
        "How do I get to the libbrary and canteen?",
        "When does the college reopen?",
        "What are the library timings?",
        "How to reach the sports complex?",
        "Who is the principal of this college?",
    ]

    for idx, query in enumerate(sample_queries, start=1):
        result = run_pipeline(query)
        print(f"\nTest {idx}: \"{query}\"")
        print(json.dumps(result, indent=4))

    print("\n[App] All automated tests completed!\n")


def main():
    """Main application loop."""
    print_banner()

    # Check dependency availability
    if not is_speech_recognition_available():
        print("[Notice] SpeechRecognition is not yet installed.")
        print("To enable microphone input, install dependencies with:")
        print("    pip install -r requirements.txt\n")

    while True:
        print("Select an option:")
        print("  1. Speak into Microphone (Voice Pipeline)")
        print("  2. Type a Query (Text Test Mode)")
        print("  3. Run Built-in Test Cases")
        print("  4. Exit")

        choice = input("\nEnter choice (1-4): ").strip()

        if choice == "1":
            handle_microphone_input()
        elif choice == "2":
            handle_text_input()
        elif choice == "3":
            run_automated_tests()
        elif choice == "4" or choice.lower() in ("exit", "quit", "q"):
            print("\nExiting College Voice Agent. Goodbye!")
            sys.exit(0)
        else:
            print("\n[Invalid choice] Please enter 1, 2, 3, or 4.\n")


if __name__ == "__main__":
    main()
