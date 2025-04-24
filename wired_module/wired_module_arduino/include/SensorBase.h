#include <CAN.h>
#include <ArduinoJson.h>  // Include ArduinoJson for JSON handling

#ifndef SENSOR_BASE
#define SENSOR_BASE

// Abstract Class
class SensorBase {
public:
    uint8_t sensorID;

    // Abstract methods
    virtual void configure() = 0;
    virtual void read() = 0;

    // Method to send the sensor data in JSON format
    void send() {
        String json = generateJson();        // Generate the JSON string
        sendJson(sensorID, json);            // Send the JSON data over CAN
    }

protected:
    // Pure virtual function for generating JSON data in derived classes
    virtual String generateJson() = 0;

    // Function to send JSON data over CAN
    void sendJson(uint8_t sensorID, String json) {
        CAN.beginPacket(sensorID);
        CAN.write(json.c_str(), json.length());  // Write JSON string to CAN packet
        CAN.endPacket();
    }
};

#endif
