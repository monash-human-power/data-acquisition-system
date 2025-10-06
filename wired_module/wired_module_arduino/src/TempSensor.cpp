#include "TempSensor.h"
#include <Arduino.h> // for String, for delay
#include "driver/i2c.h"

// SHT4x address and command set

#define TEMP_SENSOR_ADDRESS 0x44 // I2C address
#define TEMP_READ_COMMAND 0xFD // Measure temperature at high precision
#define TEMP_RESET_COMMAND 0x94 // optional reset for configure
#define TEMP_SERIAL_NUMBER 0x89

// Timing

// Constructor

TemperatureSensor::TemperatureSensor(i2c_port_t masterPortNum, uint8_t sensorAddress, uint8_t sensorID)
    : I2cSensorBase(masterPortNum, sensorAddress, sensorID) {
        // nothing like icm gyro...
}


// Configure

void TempSensor::configure() {
    write_sensor_register(0x07, 0x80, 1000);

   // optional reset
   const uint8_t reset = TEMP_RESET_COMMAND;
   (void)i2c_master_write_to_device(this->masterPortNum, this->sensorAddress, &reset, 1, 100);
    delay(2);

    // check device presence
    uint8_t cmd = TEMP_SERIAL_NUMBER;
    if (i2c_master_write_to_device(this->masterPortNum, this->sensorAddress, &cmd, 1, 100) != ESP_OK) {
        Serial.println("SHT4x: command write failed, unexpected device. ");
        return;
    }
    delay(1);

    // [TO DO: validate CRC bytes]

}

void  TempSensor::read() {
    
    // Get raw data from sensor
    read_sensor_register(0x03, 3, 1000);

    int32_t raw_temp = (this->readBuffer[0] << 16) | (this->readBuffer[1] << 8) | this->readBuffer[2];

    if (raw_temp & 0x800000) {
        raw_temp |= 0xFF000000; // sign extend 24-bit
    }

    float temp = static_cast<float>(raw_temp) / static_cast<float>(scaleFactor);
    this->temperature = this->c0 * 0.5f + this->c1 * temp;
}
