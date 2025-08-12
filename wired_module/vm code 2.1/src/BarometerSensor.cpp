#include "BarometerSensor.h"
#include <Arduino.h> // for String

void BarometerSensor::configure() {
    write_sensor_register(0x07, 0x80, 1000);

    // set to continuous temperature measurement 
    write_sensor_register(0x08, 0x06, 1000);

    // get coefficients
    read_sensor_register(0x10, 3, 1000);

    this->c0 = (this->readBuffer[0] << 4) | (this->readBuffer[1] >> 4);
    if (this->c0 & (1 << 11))
        this->c0 |= 0xF000;

    this->c1 = ((this->readBuffer[1] & 0xF) << 8) | this->readBuffer[2];
    if (this->c1 & (1 << 11))
        this->c1 |= 0xF000;
}

void BarometerSensor::read() {
    // Get raw data from sensor
    read_sensor_register(0x03, 3, 1000);

    int32_t raw_temp = (this->readBuffer[0] << 16) | (this->readBuffer[1] << 8) | this->readBuffer[2];

    if (raw_temp & 0x800000) {
        raw_temp |= 0xFF000000; // sign extend 24-bit
    }

    float temp = static_cast<float>(raw_temp) / static_cast<float>(scaleFactor);
    this->temperature = this->c0 * 0.5f + this->c1 * temp;
}

String BarometerSensor::generateJson() {
    return "{\"sensors\":[{\"type\":\"barometer\",\"value\":" + String(this->temperature, 2) + "}]}";
}

void BarometerSensor::send() {
    sendJson(this->sensorID, generateJson());
}
