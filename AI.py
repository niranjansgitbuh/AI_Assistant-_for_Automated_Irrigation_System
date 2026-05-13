"""
AgroSearch - AI Assistant for Automated Irrigation System
----------------------------------------------------------
This assistant uses voice commands to:
  - Check soil moisture and temperature via a microcontroller (Arduino/RPi)
  - Automatically control a water valve based on moisture thresholds
  - Search Wikipedia for farming/general queries
  - Greet the user based on the time of day
"""

import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import serial
import time
import sys

# ─────────────────────────────────────────────
# CONFIGURATION — adjust these to match your setup
# ─────────────────────────────────────────────
SERIAL_PORT = 'COM3'        # Change to your Arduino/RPi port (e.g. '/dev/ttyUSB0' on Linux)
BAUD_RATE = 9600            # Must match the baud rate set in your microcontroller sketch
MOISTURE_THRESHOLD = 30     # Minimum acceptable soil moisture (%) before watering is triggered
WATERING_DURATION = 5       # How long (seconds) the valve stays open per watering cycle
WIKIPEDIA_SENTENCES = 2     # Number of sentences to fetch from Wikipedia summaries

# ─────────────────────────────────────────────
# SPEECH ENGINE SETUP
# ─────────────────────────────────────────────
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')

# Index 0 = Male voice, Index 1 = Female voice — change to preference
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 170)    # Speech speed (words per minute); default ~200
engine.setProperty('volume', 1.0)  # Volume: 0.0 (silent) to 1.0 (full)

# ─────────────────────────────────────────────
# SERIAL (MICROCONTROLLER) CONNECTION SETUP
# ─────────────────────────────────────────────
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Allow time for the serial connection to stabilise
    print(f"[INFO] Connected to microcontroller on {SERIAL_PORT}")
except serial.SerialException:
    print(f"[ERROR] Could not connect to {SERIAL_PORT}. Check your port and connection.")
    ser = None  # Gracefully handle missing hardware


# ─────────────────────────────────────────────
# CORE FUNCTIONS
# ─────────────────────────────────────────────

def speak(audio):
    """Convert text to speech and play it aloud."""
    print(f"[AgroSearch]: {audio}")
    engine.say(audio)
    engine.runAndWait()


def wishMe():
    """Greet the user with a time-appropriate message on startup."""
    hour = datetime.datetime.now().hour
    if hour < 12:
        speak("Good Morning!")
    elif hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("My name is AgroSearch. Your smart irrigation assistant. How can I help you?")


def takeCommand():
    """
    Listen for a voice command via the microphone.
    Returns the recognised text in lowercase, or 'none' on failure.
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n[Listening...]")
        r.adjust_for_ambient_noise(source, duration=0.5)  # Filter background noise
        r.pause_threshold = 1  # Seconds of silence before considering speech done
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            print("[Timeout] No speech detected.")
            return "none"

    try:
        print("[Recognising...]")
        query = r.recognize_google(audio, language='en-in')
        print(f"[You said]: {query}")
    except sr.UnknownValueError:
        print("[ERROR] Could not understand audio. Please try again.")
        return "none"
    except sr.RequestError:
        speak("Speech recognition service is unavailable. Check your internet connection.")
        return "none"

    return query.lower()


def read_sensor_data():
    """
    Request sensor readings from the microcontroller over serial.
    Expects the microcontroller to respond with: 'moisture,temperature'
    e.g. '45.3,28.7'
    Returns (moisture, temperature) as floats, or (None, None) on failure.
    """
    if ser is None:
        speak("Sensor hardware is not connected.")
        return None, None

    try:
        ser.write(b'R')                              # 'R' = Read sensor command
        time.sleep(0.5)                              # Brief wait for the microcontroller to respond
        raw = ser.readline().decode('utf-8').strip() # Read one line of response

        if not raw:
            print("[WARNING] No data received from sensor.")
            return None, None

        parts = raw.split(",")
        if len(parts) != 2:
            print(f"[WARNING] Unexpected data format: '{raw}'")
            return None, None

        moisture = float(parts[0])
        temperature = float(parts[1])
        print(f"[Sensor] Soil Moisture: {moisture}%  |  Temperature: {temperature}°C")
        return moisture, temperature

    except (ValueError, serial.SerialException) as e:
        print(f"[ERROR] Sensor read failed: {e}")
        return None, None


def control_water_valve(moisture):
    """
    Decide whether to activate the water valve based on soil moisture.
    Sends 'W' (open valve) or 'S' (stop valve) commands to the microcontroller.
    """
    if ser is None:
        speak("Cannot control valve. Hardware is not connected.")
        return

    if moisture is None:
        speak("Moisture data unavailable. Skipping irrigation decision.")
        return

    if moisture < MOISTURE_THRESHOLD:
        speak(f"Soil moisture is {moisture:.1f} percent, which is below the threshold of {MOISTURE_THRESHOLD} percent.")
        speak("Activating water valve now.")
        ser.write(b'W')                  # Open valve
        time.sleep(WATERING_DURATION)    # Keep valve open for configured duration
        ser.write(b'S')                  # Close valve
        speak("Watering cycle completed. Valve closed.")
    else:
        speak(f"Soil moisture is {moisture:.1f} percent. No irrigation needed.")


def search_wikipedia(query):
    """Search Wikipedia and speak a short summary of the result."""
    speak("Searching Wikipedia, please wait...")
    # Remove the trigger word before searching
    search_term = query.replace("wikipedia", "").strip()
    try:
        results = wikipedia.summary(search_term, sentences=WIKIPEDIA_SENTENCES)
        speak("According to Wikipedia:")
        print(f"[Wikipedia]: {results}")
        speak(results)
    except wikipedia.exceptions.DisambiguationError as e:
        speak(f"That topic is ambiguous. Try being more specific. For example: {e.options[0]}.")
    except wikipedia.exceptions.PageError:
        speak("Sorry, I couldn't find a Wikipedia page for that topic.")


def show_help():
    """Tell the user what commands are available."""
    help_text = (
        "Here are the commands you can use: "
        "Say 'check soil' or 'moisture level' to read sensor data and trigger irrigation if needed. "
        "Say 'wikipedia' followed by a topic to search for information. "
        "Say 'exit' or 'quit' to shut down AgroSearch."
    )
    speak(help_text)


# ─────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────

if __name__ == "__main__":
    wishMe()
    speak("Say 'help' at any time to hear available commands.")

    while True:
        query = takeCommand()

        if query == "none":
            # Nothing was heard — loop back and listen again
            continue

        # ── Wikipedia search ──────────────────────────────
        elif 'wikipedia' in query:
            search_wikipedia(query)

        # ── Soil sensor check + auto irrigation ──────────
        elif 'check soil' in query or 'moisture level' in query:
            moisture, temperature = read_sensor_data()
            if moisture is not None:
                speak(
                    f"Soil moisture is {moisture:.1f} percent "
                    f"and temperature is {temperature:.1f} degrees Celsius."
                )
                control_water_valve(moisture)
            else:
                speak("Sorry, I was unable to retrieve sensor data. Please check the connection.")

        # ── Help command ──────────────────────────────────
        elif 'help' in query:
            show_help()

        # ── Graceful exit ─────────────────────────────────
        elif 'exit' in query or 'quit' in query or 'stop' in query:
            speak("Shutting down AgroSearch. Goodbye!")
            if ser and ser.is_open:
                ser.close()  # Close serial port cleanly before exiting
            sys.exit(0)

        # ── Unrecognised command ──────────────────────────
        else:
            speak("I didn't catch a valid command. Say 'help' to hear what I can do.")
