#include <BarometerSensor.h>
#include <CAN.h>
#include <I2cMaster.h>
#include <MpuSensor.h>
#include <Adc1.h>
#include <GpsSensor.h>

#include <vector>
#include "driver/i2c.h"

#include "DPS368.cpp"

#define I2C_NUM I2C_NUM_0
#define I2C_SCL GPIO_NUM_22
#define I2C_SDA GPIO_NUM_21

// Function prototypes
static esp_err_t i2c_master_init(void);
void onReceive(int packetSize);
void setup();
void loop();

// ==================================================================
// SETUP SENSORS HERE
// ==================================================================
I2cMaster i2cMaster(I2C_NUM, I2C_SDA, I2C_SCL, 400000);

MpuSensor mpuSensor(i2cMaster.portNum, 0x68, 0x13); // ICM-42670-P
BarometerSensor barometerSensor(i2cMaster.portNum, 0x76, 0x11);
Adc1 adc1(ADC1_CHANNEL_0, ADC_ATTEN_DB_12, ADC_WIDTH_BIT_12, 0x12);
GpsSensor gpsSensor(2, 16, 17, 0x14);  // UART2, RX=16, TX=17
Dps368Sensor dps368Sensor(i2cMaster.portNum, 0x77, 0x15); // Add your DPS368 sensor here

std::vector<SensorBase*> sensors = {
    &mpuSensor,
    &barometerSensor,
    &adc1,
    &gpsSensor,
    &dps368Sensor  // Add to sensors list
};
// ==================================================================

void onReceive(int packetSize) {
    // Get all bytes from packet
    uint8_t buffer[4];
    int i = 0;
    while (CAN.available()) {
        buffer[i++] = CAN.read();
    }

    // Convert bytes to float
    float data;
    memcpy(&data, buffer, sizeof(float));

    Serial.printf("Msg received | ID = 0x%lx | Data = %f\n", CAN.packetId(), data);
}

void setup() {
    // Setup CAN bus
    CAN.setPins(4, 5);  // or your preferred TX/RX pins
    Serial.begin(115200);
    while (!Serial);

    if (!CAN.begin(500E3)) {
        Serial.println("\n\nStarting CAN failed!\n\n");
        while (1);
    }

    CAN.loopback();
    CAN.onReceive(onReceive);

    // Configure all sensors
    for (auto sensor : sensors) {
        sensor->configure();
    }
}

void loop() {
    for (auto sensor : sensors) {
        sensor->send();
    }
    delay(1000);
}