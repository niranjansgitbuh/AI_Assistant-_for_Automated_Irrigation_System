#Smart Irrigation System - Arduino/Raspberry Pi Code
#Overview
This repository contains the Arduino/Raspberry Pi code for a smart irrigation system that monitors soil moisture and temperature in real time. If the soil moisture level falls below a predefined threshold, the system automatically activates a water valve to irrigate the field.

#Features
Real-time monitoring of soil moisture and temperature
Automatic water valve control based on soil moisture levels
Serial communication with an AI assistant for sensor data requests
Manual control through serial commands
Hardware Requirements
Microcontroller: Arduino Uno/Nano or Raspberry Pi
Sensors:
Soil Moisture Sensor (e.g., FC-28, Capacitive Soil Sensor)
Temperature Sensor (e.g., DHT11/DHT22 or LM35) (Optional)
Water Valve & Relay Module
Power Supply for sensors and microcontroller
Installation & Setup
1. Connect the Hardware
Soil Moisture Sensor: Connect A0 (Analog Pin)
Temperature Sensor: Connect A1 (Analog Pin) (Optional)
Relay Module: Connect to Digital Pin 7
2. Upload Code to Arduino
Install the Arduino IDE (Download Here)
Connect your Arduino to your PC via USB
Open smart_irrigation.ino and select the correct COM Port
Click Upload
3. Serial Communication Commands
The AI assistant or any external program can send the following commands to the microcontroller:

'R' → Request soil moisture and temperature data
'W' → Open the water valve (Start irrigation)
'S' → Close the water valve (Stop irrigation)
Code Explanation
1. Pin Configuration
cpp
Copy
Edit
#define moisturePin A0  // Soil moisture sensor
#define relayPin 7      // Relay for water valve
#define tempPin A1      // Temperature sensor (Optional)
Assigns A0 for soil moisture
Assigns A1 for temperature sensor (if used)
Assigns Pin 7 for relay-controlled water valve
2. Setup Function
cpp
Copy
Edit
void setup() {
    Serial.begin(9600);
    pinMode(relayPin, OUTPUT);
    digitalWrite(relayPin, HIGH);  // Initially keep the valve off
}
Initializes serial communication
Configures relay as an output
Ensures the valve is OFF by default
3. Reading Sensor Data
cpp
Copy
Edit
if (command == 'R') {  // Request for sensor data
    int moisture = analogRead(moisturePin);
    float temperature = analogRead(tempPin) * 0.48828125;  // Convert to Celsius
    int moisturePercent = map(moisture, 1023, 0, 0, 100);
    Serial.print(moisturePercent);
    Serial.print(",");
    Serial.println(temperature);
}
Reads soil moisture and temperature
Converts temperature data into Celsius
Maps soil moisture from 0-1023 to 0-100%
Sends data over serial communication
4. Controlling the Water Valve
cpp
Copy
Edit
if (command == 'W') {  // Open Water Valve
    digitalWrite(relayPin, LOW);
}

if (command == 'S') {  // Stop Water Valve
    digitalWrite(relayPin, HIGH);
}
'W' command: Turns ON the water valve
'S' command: Turns OFF the water valve
Future Enhancements
✅ Integrate AI assistant for real-time voice-based irrigation control
✅ Wi-Fi connectivity for remote monitoring (ESP8266/ESP32)
✅ Cloud dashboard for historical data visualization

Contributors
👨‍💻 [Your Name] – AI & Embedded Systems Developer

