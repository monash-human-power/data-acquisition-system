#include <WiFi.h>
#include <PubSubClient.h>

#include <BarometerSensor.h>
#include <I2cMaster.h>
/* #include <MpuSensor.h>
#include <Adc1.h>
# include <GpsSensor.h>
# include <ICM42670.h>
# include "DPS368.cpp" */
# include <vector>
# include "driver/i2c.h"
#include "secrets.h"

WiFiClient espClient;
PubSubClient mqttClient(espClient);  // Declared globally for SensorBase access

// I2C Config
#define I2C_NUM I2C_NUM_0
#define I2C_SCL GPIO_NUM_22
#define I2C_SDA GPIO_NUM_21

I2cMaster i2cMaster(I2C_NUM, I2C_SDA, I2C_SCL, 400000);

// Sensor Setup
/* MpuSensor mpuSensor(i2cMaster.portNum, 0x68, 0x13); // ICM-42670-P
Adc1 adc1(ADC1_CHANNEL_0, ADC_ATTEN_DB_12, ADC_WIDTH_BIT_12, 0x12);
GpsSensor gpsSensor(2, 16, 17, 0x14);  // UART2, RX=16, TX=17
Dps368Sensor dps368Sensor(i2cMaster.portNum, 0x77, 0x15); // DPS368 sensor 
ICM42670 icm42670Sensor(i2cMaster.portNum, 0x68, 0x16);  // ICM-42670-P sensor */

BarometerSensor barometerSensor(i2cMaster.portNum, 0x76, 0x11);

std::vector<SensorBase*> sensors = {
    /* &mpuSensor,
    &adc1,
    &gpsSensor,
    &dps368Sensor,
    &icm42670Sensor */
    &barometerSensor
};

// Wi-Fi and MQTT Helpers
void connectToWiFi() {
    Serial.print("Connecting to Wi-Fi");
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
        delay(2500);
        Serial.println(WiFi.status()); 
    }
    Serial.println("\nWi-Fi connected. IP: " + WiFi.localIP().toString());
}

void connectToMQTT() {
    mqttClient.setServer(mqttServer, mqttPort);
    while (!mqttClient.connected()) {
        Serial.print("Connecting to MQTT...");
        if (mqttClient.connect("ESP32Client")) {
            Serial.println("connected");
        } else {
            Serial.print("failed, rc=");
            Serial.print(mqttClient.state());
            Serial.println(" try again in 2 seconds");
            delay(2000);
        }
    }
}

// Setup & Loop
void setup() {
    connectToWiFi();
    connectToMQTT();

    for (auto sensor : sensors) {
        sensor->configure();
    } 
    Serial.begin(9600);        // Start serial communication at 115200 baud
    delay(1000);
    
    Serial.println("Connecting to WiFi...");
    WiFi.begin(ssid, password);
    
    // Wait for connection
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
        delay(2500);
        Serial.println(WiFi.status()); 
  }
  
  Serial.println();
  Serial.println("WiFi connected!");
  Serial.print("Board IP address: ");
  Serial.println(WiFi.localIP()); 
}

void loop() {

    if (!mqttClient.connected()) {
        connectToMQTT();
    }
    mqttClient.loop();

    barometerSensor.read();
    String payload = barometerSensor.generateJson();

    char topic[32];
    snprintf(topic, sizeof(topic), "sensor/%02x", barometerSensor.sensorID);

    if (mqttClient.connected()) {
        bool published = mqttClient.publish(topic, payload.c_str());
        Serial.print("Publish status: ");
        Serial.println(published ? "Success" : "Failed");
    } else {
        Serial.println("MQTT disconnected before publish!");
    }

    /*for (auto sensor : sensors) {
        sensor->send();  // This calls generateJson() and publishes via MQTT
    }*/

    delay(2000);

    /* // Generate a random float between 0 and 100
    float dummyValue = random(0, 10000) / 100.0f;

    // Create JSON string manually
    String payload = "{\"sensor\":\"dummy\",\"value\":";
    payload += String(dummyValue, 2);
    payload += "}";

    // Publish to test/topic
    mqttClient.publish("test/topic", payload.c_str());

    Serial.println("Published: " + payload);

    delay(2000);  // Publish every second */
}
