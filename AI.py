import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import serial  # For reading sensor data from Arduino/Raspberry Pi
import time

# Initialize speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Set up serial communication (Change COM3 to your Arduino port)
ser = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)  # Wait for connection

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour < 12:
        speak("Good Morning!")
    elif hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("My name is AgroSearch. How can I help you?")

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening....")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
    except Exception:
        print("Say that again please...")
        return "None"
    return query.lower()

def read_sensor_data():
    ser.write(b'R')  # Send request to microcontroller
    data = ser.readline().decode('utf-8').strip()  # Read response
    if data:
        try:
            moisture, temperature = map(float, data.split(","))
            print(f"Soil Moisture: {moisture}%, Temperature: {temperature}°C")
            return moisture, temperature
        except ValueError:
            return None, None
    return None, None

def control_water_valve(moisture):
    threshold = 30  # Adjust based on soil type
    if moisture is not None and moisture < threshold:
        speak("Soil moisture is low. Activating water valve.")
        ser.write(b'W')  # Command to open valve
        time.sleep(5)  # Let the water flow
        ser.write(b'S')  # Command to stop water
        speak("Watering completed.")
    else:
        speak("Soil moisture is adequate.")

if __name__ == "__main__":
    wishMe()
    while True:
        query = takeCommand()
        
        if 'wikipedia' in query:
            speak('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            results = wikipedia.summary(query, sentences=2)
            speak("According to Wikipedia")
            print(results)
            speak(results)
        
        elif 'check soil' in query or 'moisture level' in query:
            moisture, temperature = read_sensor_data()
            if moisture is not None:
                speak(f"The current soil moisture is {moisture} percent and the temperature is {temperature} degrees Celsius.")
                control_water_valve(moisture)
            else:
                speak("Sorry, I couldn't read sensor data.")
