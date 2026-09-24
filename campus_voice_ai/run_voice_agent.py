"""
run_voice_agent.py
------------------
Hands-Free Continuous Voice Agent.
Runs in an automatic continuous loop without interactive menus or keyboard prompts.

Pipeline:
Mic Listening -> Speech-to-Text -> Navigation Route Engine -> Text-to-Speech -> Repeat
"""

import time
import sys
from voice import capture_speech_from_microphone, is_speech_recognition_available, calibrate_microphone_once
from app import run_pipeline
from tts import speak_text, generate_response_speech_text, is_tts_available


def run_hands_free_loop():
    """Continuous hands-free voice assistant loop."""
    print("\n============================================================", flush=True)
    print("      COLLEGE AI HELP-DESK - HANDS-FREE CONTINUOUS MODE     ", flush=True)
    print("============================================================", flush=True)
    print("  • System listens automatically for your questions.", flush=True)
    print("  • Responses are spoken out loud via Text-to-Speech.", flush=True)
    print("  • Press Ctrl+C in terminal to stop.", flush=True)
    print("============================================================\n", flush=True)

    if not is_speech_recognition_available():
        print("[Error] SpeechRecognition library is missing.", flush=True)
        print("Please install requirements: pip install -r requirements.txt", flush=True)
        return

    # Pre-calibrate microphone once at startup for instant listening in loop
    calibrate_microphone_once(duration=0.5)

    # Initial welcome chime/speech
    speak_text("College Help Desk Agent activated. How can I help you today?")

    while True:
        try:
            print("\n[Voice Agent] Ready & Listening...", flush=True)
            query_text = capture_speech_from_microphone(timeout=6, phrase_time_limit=10)

            if query_text:
                print(f"[Voice Agent] Transcribed Speech: \"{query_text}\"", flush=True)
                result = run_pipeline(query_text)

                nav_details = result.get("navigation_details")
                if nav_details and nav_details.get("status") == "success":
                    speech_text = nav_details["directions_text"]
                else:
                    speech_text = generate_response_speech_text(
                        result.get("intent"), 
                        result.get("destination")
                    )

                print(f"[Voice Agent] Responding: \"{speech_text}\"", flush=True)
                speak_text(speech_text)
                
                # Brief pause before next cycle
                time.sleep(0.3)
            else:
                # Silence or no speech detected; small pause before next listen
                time.sleep(0.5)

        except KeyboardInterrupt:
            print("\n\n[Voice Agent] Stopping continuous voice mode. Goodbye!", flush=True)
            speak_text("Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"[Voice Agent Error] An error occurred: {e}", flush=True)
            time.sleep(1)


if __name__ == "__main__":
    run_hands_free_loop()
