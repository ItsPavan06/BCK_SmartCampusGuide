"""
voice.py
--------
This module handles microphone audio capture and Speech-to-Text (STT) conversion
using the SpeechRecognition library.

Optimized for ultra-fast, low-latency voice capture with cached audio sources,
one-time background calibration, and real-time output flushing.
"""

import sys
from typing import Optional

try:
    import speech_recognition as sr
except ImportError:
    sr = None

# Global cached recognizer and microphone for zero-delay instant listening
_GLOBAL_RECOGNIZER = None
_GLOBAL_MICROPHONE = None
_IS_CALIBRATED = False


def is_speech_recognition_available() -> bool:
    """Checks if speech_recognition package is installed."""
    return sr is not None


def get_audio_engine():
    """Initializes and returns cached recognizer and microphone objects."""
    global _GLOBAL_RECOGNIZER, _GLOBAL_MICROPHONE, _IS_CALIBRATED

    if not is_speech_recognition_available():
        return None, None

    if _GLOBAL_RECOGNIZER is None:
        _GLOBAL_RECOGNIZER = sr.Recognizer()
        # Balanced endpointing: allows natural pauses without cutting off word endings
        _GLOBAL_RECOGNIZER.pause_threshold = 0.9
        _GLOBAL_RECOGNIZER.non_speaking_duration = 0.4
        _GLOBAL_RECOGNIZER.dynamic_energy_threshold = True

    if _GLOBAL_MICROPHONE is None:
        _GLOBAL_MICROPHONE = sr.Microphone()

    return _GLOBAL_RECOGNIZER, _GLOBAL_MICROPHONE


def calibrate_microphone_once(duration: float = 0.5):
    """Performs one-time ambient noise calibration so subsequent calls start instantly."""
    global _IS_CALIBRATED
    recognizer, mic = get_audio_engine()
    if recognizer and mic and not _IS_CALIBRATED:
        try:
            with mic as source:
                print("[Voice] Calibrating microphone for room acoustics...", flush=True)
                recognizer.adjust_for_ambient_noise(source, duration=duration)
                _IS_CALIBRATED = True
        except Exception:
            pass


def capture_speech_from_microphone(
    timeout: int = 6,
    phrase_time_limit: int = 12,
    language: str = "en-US"
) -> Optional[str]:
    """
    Captures live audio with minimum latency and converts it into text.

    Parameters:
        timeout (int): Maximum seconds to wait for speech to begin.
        phrase_time_limit (int): Maximum seconds of speech recording time.
        language (str): BCP-47 language tag (default: 'en-US').

    Returns:
        Optional[str]: Transcribed text if successful, or None if failed.
    """
    global _IS_CALIBRATED

    if not is_speech_recognition_available():
        print("[Voice Error] 'SpeechRecognition' library is not installed.", flush=True)
        print("Please run: pip install -r requirements.txt", flush=True)
        return None

    recognizer, microphone = get_audio_engine()

    try:
        with microphone as source:
            # Calibrate only on the first run, skip on subsequent queries for 0ms startup lag
            if not _IS_CALIBRATED:
                recognizer.adjust_for_ambient_noise(source, duration=0.4)
                _IS_CALIBRATED = True

            print("[Voice] Listening... Speak your question now.", flush=True)
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )

            print("[Voice] Processing speech...", flush=True)
            # Use Google Speech Recognition API for speech-to-text
            transcribed_text = recognizer.recognize_google(audio, language=language)
            print(f"[Voice] Recognized: \"{transcribed_text}\"", flush=True)
            return transcribed_text.strip()

    except sr.WaitTimeoutError:
        print("[Voice Warning] No speech detected within the timeout window.", flush=True)
        return None
    except sr.UnknownValueError:
        print("[Voice Warning] Could not understand audio. Please speak clearly.", flush=True)
        return None
    except sr.RequestError as e:
        print(f"[Voice Error] Speech recognition network error; {e}", flush=True)
        return None
    except OSError as e:
        print(f"[Voice Error] Microphone device error: {e}", flush=True)
        return None
    except Exception as e:
        print(f"[Voice Error] Unexpected error: {e}", flush=True)
        return None
