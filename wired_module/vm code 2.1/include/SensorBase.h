#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

#ifndef SENSOR_BASE
#define SENSOR_BASE

extern PubSubClient mqttClient;  // Declare external MQTT client

class SensorBase {
public:
    uint8_t sensorID;
    virtual ~SensorBase() = default;
    virtual void configure() = 0;
    virtual void read() = 0;

    virtual void send() {
        String json = generateJson();        // Generate the JSON string
        sendJson(sensorID, json);            // Send via MQTT
    }

protected:
    virtual String generateJson() = 0;

    void sendJson(uint8_t sensorID, String json) {
       char topic[32];
       snprintf(topic, sizeof(topic), "sensor/%02x", sensorID);
       mqttClient.publish(topic, json.c_str());
    }
};

#endif

