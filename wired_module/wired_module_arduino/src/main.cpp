#include <BarometerSensor.h>
#include <CAN.h>
#include <I2cMaster.h>
#include <MpuSensor.h>
#include <Adc1.h>

#include <vector>

#include "driver/i2c.h"

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
MpuSensor mpuSensor(i2cMaster.portNum, 0x68, 0x13);
BarometerSensor barometerSensor(i2cMaster.portNum, 0x76, 0x11);
Adc1 adc1(ADC1_CHANNEL_0, ADC_ATTEN_DB_12, ADC_WIDTH_BIT_12, 0x12);
std::vector<SensorBase*> sensors = {&mpuSensor,&barometerSensor,&adc1};
// ==================================================================

void onReceive(int packetSize) {
    // Get all bytes from packet
    uint8_t buffer[4];
    int i = 0;
    while (CAN.available()) {
        buffer[i] = CAN.read();
        i++;
    };

    // Convert bytes to float
    float data;
    memcpy(&data, buffer, sizeof(float));

    Serial.printf("Msg received | ID = 0x%lx | Data = %f\n", CAN.packetId(), data);
}

void setup() {
    // Setup CAN bus
    CAN.setPins(16, 17);
    Serial.begin(115200);
    while (!Serial);

    // Start the CAN bus at 500 kbps
    if (!CAN.begin(500E3)) {
        Serial.println("\n\nStarting CAN failed!\n\n");
        while (1);
    }

    // Configure can bus to loopback mode for self test
    CAN.loopback();

    // Set up receive callback, for self testing
    CAN.onReceive(onReceive);

    // Configure all sensors
    for (auto sensor : sensors) {
        sensor->configure();
    }
}

void loop() {
    // Send CAN bus from all sensors
    for (auto sensor : sensors) {
        sensor->send();
    }
    delay(1000);
}