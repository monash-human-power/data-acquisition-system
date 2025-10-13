#include "TempSensor.h"
#include <Arduino.h> // for String, for delay
#include "driver/i2c.h"

// SHT4x address and command set
#define TEMP_SENSOR_ADDRESS 0x44 // I2C address
#define TEMP_READ_COMMAND 0xFD // Measure temperature at high precision
#define TEMP_RESET_COMMAND 0x94 // optional reset for configure
#define TEMP_SERIAL_NUMBER 0x89 // Sensor serial number for WHO_AM_I check

// CRC parameters (Sensirion)
#define CRC8_POLY = 0x31;
#define CRC8_INIT = 0xFF;

// Timing
#define READ_DELAY_MS = 10;
#define SERIAL_DELAY_MS = 1;

// Constructor

TempSensor::TempSensor(i2c_port_t masterPortNum, uint8_t sensorAddress, uint8_t sensorID)
    : I2cSensorBase(masterPortNum, sensorAddress, sensorID) {
        // nothing like icm gyro...
}

// 0. Conversion Helpers

float TempSensor::convert_temp(uint16_t raw_t){
    // formula from datasheet
    return (175.0f * (float)raw_t / 65535.0f) - 45.0f;

}

float TempSensor::convert_humidity(uint16_t raw_h){
    // formula from datasheet
    return (125.0f * (float)raw_h / 65535.0f) - 6.0f;

}

uint8_t TempSensor::crc8_sensirion(const uint8_t *data, size_t len) {
    uint8_t crc = CRC8_INIT;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int b = 0; b < 8; ++b) {
            crc = (crc & 0x80) ? (uint8_t)((crc << 1) ^ CRC8_POLY) : (uint8_t)(crc << 1);
        }
    }
    return crc;
}

bool TempSensor::check_word_crc(const uint8_t *w) {
    // for each reading => MSB - LSB - CRC
    return crc8_sensirion(w, 2) == w[2];
}


// 1. Configure

void TempSensor::configure() {
    


   // optional reset
   const uint8_t reset = TEMP_RESET_COMMAND;
   (void)i2c_master_write_to_device(this->masterPortNum, this->sensorAddress, &reset, 1, 100);
    delay(2);

    // check device presence
    uint8_t cmd = TEMP_SERIAL_NUMBER;
    esp_err_t err = i2c_master_write_to_device(this->masterPortNum, this->sensorAddress,
                                               &cmd, 1, 1000);
    if (err != ESP_OK) {
        Serial.println("Command write failed.");
        return;
    }

    delay(SERIAL_DELAY_MS);

    uint8_t buf[6] = {0};
    err = i2c_master_read_from_device(this->masterPortNum, this->sensorAddress,
                                      buf, sizeof(buf), 1000);
    if (err != ESP_OK) {
        Serial.println("Serial read failed.")
    };

    // [TO DO: validate CRC bytes]

}

// 2. Read

void  TempSensor::read() {

    // Start high-precision measurement
    const uint8_t cmd = TEMP_READ_COMMAND;

    // Write command
    if (i2c_master_write_to_device(this->masterPortNum, this->sensorAddress,
                                   &cmd, 1, 1000) != ESP_OK) {
        Serial.println("SHT4x: measure cmd write failed");
        return;
    }
    
    delay(READ_DELAY_MS);

    // Read the measurement
    uint8_t buf[6] = {0};
    if (i2c_master_read_from_device(this->masterPortNum, this->sensorAddress,
                                    buf, sizeof(buf), 1000) != ESP_OK) {
        Serial.println("SHT4x: data read failed");
        return;
    }
// [TO DO: Implement crc check] might be unecessary

// Convert measurements

    uint16_t raw_t  = (uint16_t(buf[0]) << 8) | buf[1];
    uint16_t raw_rh = (uint16_t(buf[3]) << 8) | buf[4];

    temperature = convert_temp(raw_t);
    humidity = convert_humidity(raw_rh);
    valid = true;
    
}

String TempSensor::generateJson() {
    return "{\"sensors\":[{\"type\":\"sht4x\",\"temperature\":" +
           String(temperature_c, 2) + ",\"humidity\":" + String(humidity_rh, 2) + "}]}";
}

// send function? 