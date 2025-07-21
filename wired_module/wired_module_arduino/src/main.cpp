#include <WiFi.h>
#include <PubSubClient.h>

#include <BarometerSensor.h>
#include <I2cMaster.h>
#include <MpuSensor.h>
#include <Adc1.h>
# include <GpsSensor.h>
# include <ICM42670.h>

# include <vector>
# include "driver/i2c.h"
# include "DPS368.cpp"
#include "secrets.h"

WiFiClient espClient;
PubSubClient mqttClient(espClient);  // Declared globally for SensorBase access

// I2C Config
#define I2C_NUM I2C_NUM_0
#define I2C_SCL GPIO_NUM_22
#define I2C_SDA GPIO_NUM_21

I2cMaster i2cMaster(I2C_NUM, I2C_SDA, I2C_SCL, 400000);

// Sensor Setup
MpuSensor mpuSensor(i2cMaster.portNum, 0x68, 0x13); // ICM-42670-P
BarometerSensor barometerSensor(i2cMaster.portNum, 0x76, 0x11);
Adc1 adc1(ADC1_CHANNEL_0, ADC_ATTEN_DB_12, ADC_WIDTH_BIT_12, 0x12);
GpsSensor gpsSensor(2, 16, 17, 0x14);  // UART2, RX=16, TX=17
Dps368Sensor dps368Sensor(i2cMaster.portNum, 0x77, 0x15); // DPS368 sensor
ICM42670 icm42670Sensor(i2cMaster.portNum, 0x68, 0x16); // ICM-42670-P sensor

std::vector<SensorBase*> sensors = {
    &mpuSensor,
    &barometerSensor,
    &adc1,
    &gpsSensor,
    &dps368Sensor
};

// Wi-Fi and MQTT Helpers
void connectToWiFi() {
    WiFi.begin(ssid, password);
    Serial.print("Connecting to Wi-Fi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
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
    Serial.begin(115200);
    connectToWiFi();
    connectToMQTT();

    for (auto sensor : sensors) {
        sensor->configure();
    }
}

void loop() {
    if (!mqttClient.connected()) {
        connectToMQTT();
    }
    mqttClient.loop();  // Handle incoming/outgoing MQTT messages

    for (auto sensor : sensors) {
        sensor->send();  // This calls generateJson() and publishes via MQTT
    }

    delay(1000);  // Check every second
}
