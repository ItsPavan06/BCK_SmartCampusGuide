"""
tts.py
------
This module handles Text-to-Speech (TTS) voice output using the pyttsx3 library.
It converts textual answers into spoken speech via Windows SAPI5 audio engine.
"""

import sys
from typing import Optional, Union, List

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


def is_tts_available() -> bool:
    """Checks if pyttsx3 library is installed and available."""
    return pyttsx3 is not None


def speak_text(text: str, rate: int = 190, volume: float = 1.0) -> bool:
    """
    Converts input text into spoken speech output.

    Parameters:
        text (str): The text message to speak out loud.
        rate (int): Speech rate in words per minute (default: 190).
        volume (float): Speech volume from 0.0 to 1.0 (default: 1.0).

    Returns:
        bool: True if speech was successfully spoken, False otherwise.
    """
    if not is_tts_available():
        print("[TTS Warning] 'pyttsx3' is not installed. Text-to-speech skipped.")
        print("Install dependencies with: pip install -r requirements.txt")
        return False

    if not text or not text.strip():
        return False

    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", rate)
        engine.setProperty("volume", volume)

        print(f"\n[TTS Speaking] Spoken output: \"{text.strip()}\"")
        engine.say(text.strip())
        engine.runAndWait()
        return True

    except Exception as e:
        print(f"[TTS Error] Could not synthesize speech: {e}")
        return False


def generate_response_speech_text(intent: str, destination: Optional[Union[str, List[str]]]) -> str:
    """
    Generates a natural spoken response string based on the NLU result.
    This acts as a placeholder for Prathiksha's AI module response.
    """
    if intent == "navigation" and destination:
        if isinstance(destination, list):
            dest_names = [d.replace("_", " ").title() for d in destination]
            dest_display = " and ".join(dest_names)
            return f"The destinations requested are {dest_display}. Displaying multi-stop directions now."
        dest_display = str(destination).replace("_", " ").title()
        return f"The destination requested is {dest_display}. Displaying directions now."
    elif intent == "navigation":
        return "I recognized a navigation query, but could not determine the specific campus destination."
    elif intent == "college_info":
        return "This is a general college information query. Database lookup will provide details."
    else:
        return "Sorry, I could not understand your query."


if __name__ == "__main__":
    print("Testing TTS module...")
    if is_tts_available():
        speak_text("Hello Rakesh! Text to Speech module is active and working properly.")
    else:
        print("pyttsx3 is not installed.")
