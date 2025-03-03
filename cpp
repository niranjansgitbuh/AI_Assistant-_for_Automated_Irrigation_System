#define moisturePin A0  // Soil moisture sensor
#define relayPin 7      // Relay for water valve
#define tempPin A1      // Temperature sensor (Optional)

void setup() {
    Serial.begin(9600);
    pinMode(relayPin, OUTPUT);
    digitalWrite(relayPin, HIGH);  // Initially keep the valve off
}

void loop() {
    if (Serial.available() > 0) {
        char command = Serial.read();
        
        if (command == 'R') {  // Request for sensor data
            int moisture = analogRead(moisturePin);
            float temperature = analogRead(tempPin) * 0.48828125;  // Convert to Celsius
            int moisturePercent = map(moisture, 1023, 0, 0, 100);
            Serial.print(moisturePercent);
            Serial.print(",");
            Serial.println(temperature);
        }
        
        if (command == 'W') {  // Open Water Valve
            digitalWrite(relayPin, LOW);
        }
        
        if (command == 'S') {  // Stop Water Valve
            digitalWrite(relayPin, HIGH);
        }
    }
}
