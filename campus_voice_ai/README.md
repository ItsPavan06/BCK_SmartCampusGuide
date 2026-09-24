# College AI Help-Desk - Voice Processing Module

A modular, beginner-friendly Python prototype for a college AI help-desk agent. This module focuses exclusively on the voice and natural language understanding (NLU) pipeline: capturing speech, converting it to text, detecting the user's intent, extracting college destinations, and returning structured data.

---

## 🚀 Pipeline Flow

```text
  [User Speaks]
        │
        ▼
┌───────────────┐
│  Microphone   │  Audio capture via `voice.py`
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Speech-to-Text│  Google Speech Recognition STT via `voice.py`
└───────┬───────┘
        │
        ▼
┌───────────────┐
│Intent Detect. │  Classifies intent ('navigation' vs 'college_info') via `intent.py`
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  Destination  │  Extracts campus location entity via `destinations.py`
│  Extraction   │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│Text-to-Speech │  Synthesizes speech output via `tts.py` (pyttsx3)
└───────────────┘
```

---

## 📁 Project Structure

```text
college_voice_agent/
│
├── app.py             # Main entry point and CLI interactive controller
├── voice.py           # Microphone audio capture & Speech-to-Text (STT)
├── tts.py             # Text-to-Speech (TTS) voice synthesis engine
├── intent.py          # Intent classification & query dispatching logic
├── destinations.py    # Campus destinations dictionary and entity extraction
├── requirements.txt   # Python package dependencies
└── README.md          # Setup and usage documentation
```

---

## 📋 Expected Output Formats

### 1. Navigation Queries
For questions asking for single or multiple directions/locations:
- *"Where is the library?"*
- *"How do I get to the canteen?"*
- *"Where is the principal's office?"*
- *"Take me to the computer lab."*
- *"Where is the library and canteen?"*

**Single Destination Output:**
```json
{
    "intent": "navigation",
    "destination": "library"
}
```

**Multi-Destination Output:**
```json
{
    "intent": "navigation",
    "destination": [
        "library",
        "canteen"
    ]
}
```

### 2. General College Info Queries
For non-navigation questions regarding college timings, schedules, reopening dates, etc.:
- *"When does the college reopen?"*
- *"What are the library timings?"*

**Structured Output:**
```json
{
    "intent": "college_info",
    "destination": null
}
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- **Python 3.8+** installed on your system.
- A working **Microphone** connected to your computer.
- An active **Internet Connection** (required for Google Speech Recognition STT).

### 2. (Optional) Create a Virtual Environment
It is recommended to use a virtual environment to manage dependencies:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install all required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

> **Note for PyAudio on Windows:**
> If `pip install -r requirements.txt` encounters an error compiling `PyAudio`, run:
> ```bash
> pip install pipwin
> pipwin install pyaudio
> ```
> Or install pre-built wheels via `pip install pyaudio`.

---

### 1. Hands-Free Continuous Mode (Zero Prompts)
Run the agent in an automatic continuous listening & speaking loop without menus:

```bash
python run_voice_agent.py
```

### 2. Interactive Menu Mode
Run the menu-based prototype:

```bash
python app.py
```

When you run `app.py`, you will see a menu:

1. **Option 1 (Microphone Input)**: Captures audio from your microphone, transcribes it, and outputs the structured JSON.
2. **Option 2 (Text Test Mode)**: Allows you to type queries directly in the terminal to test the NLU pipeline without speaking.
3. **Option 3 (Built-in Test Cases)**: Runs the pre-configured sample queries automatically to demonstrate both navigation and informational responses.
4. **Option 4 (Exit)**: Exits the application.

---

## 🧩 Module Breakdown

- **[app.py](file:///c:/Users/Rakesh/Documents/college_voice_agent/app.py)**: The main entry point. Orchestrates voice capture, invokes intent classification, calculates routes, and triggers spoken audio output.
- **[voice.py](file:///c:/Users/Rakesh/Documents/college_voice_agent/voice.py)**: Handles ambient noise calibration, microphone audio streaming, and speech-to-text conversion via Google Speech Recognition API.
- **[tts.py](file:///c:/Users/Rakesh/Documents/college_voice_agent/tts.py)**: Synthesizes spoken voice responses using offline `pyttsx3` engine (Windows SAPI5).
- **[navigation.py](file:///c:/Users/Rakesh/Documents/college_voice_agent/navigation.py)**: Calculates campus shortest paths (Dijkstra algorithm), distance, walking time, and step-by-step turn directions.
- **[test_navigation.py](file:///c:/Users/Rakesh/Documents/college_voice_agent/test_navigation.py)**: Automated unit test suite verifying route calculations across campus destinations.
- **[intent.py](file:///c:/Users/Rakesh/Documents/college_voice_agent/intent.py)**: Categorizes utterances into `navigation` or `college_info` intents using natural language pattern matching.
- **[destinations.py](file:///c:/Users/Rakesh/Documents/college_voice_agent/destinations.py)**: Maintains a dictionary of college places (Library, Canteen, Principal's Office, Computer Lab, Admin Block, etc.) and alias mapping with boundary-aware entity extraction.
