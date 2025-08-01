#include <WiFi.h>
<<<<<<< HEAD
#include <PubSubClient.h>
#include <ArduinoJson.h>
=======
#include <CAN.h>
#include <ArduinoJson.h>  // Include ArduinoJson for JSON handling
>>>>>>> spi-class

#ifndef SENSOR_BASE
#define SENSOR_BASE

<<<<<<< HEAD
extern PubSubClient mqttClient;  // Declare external MQTT client

=======
extern PubSubClient mqttClient; // Declare external MQTT client

// Abstract Class
>>>>>>> spi-class
class SensorBase {
public:
    uint8_t sensorID;

    virtual void configure() = 0;
    virtual void read() = 0;

    void send() {
        String json = generateJson();        // Generate the JSON string
        sendJson(sensorID, json);            // Send via MQTT
    }

protected:
    virtual String generateJson() = 0;

    void sendJson(uint8_t sensorID, String json) {
<<<<<<< HEAD
        char topic[32];
        snprintf(topic, sizeof(topic), "sensor/%02x", sensorID);
        mqttClient.publish(topic, json.c_str());
=======
       char topic[32];
       snprintf(topic, sizeof(topic), "sensor/%02x", sensorID);
       mqttClient.publish(topic, json.c_str());
>>>>>>> spi-class
    }
};

#endif

