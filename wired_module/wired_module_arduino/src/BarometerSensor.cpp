#include "BarometerSensor.h"

#include <cstring>

void BarometerSensor::configure() {
    // use external sensor
    write_sensor_register(0x07,0x80,1000);

    // set to continous temperature measurement 
    write_sensor_register(0x08, 0x06, 1000);

    // get coefficients
    read_sensor_register(0x10, 3, 1000);

    this->c0 = this->readBuffer[0] << 4 | this->readBuffer[1] >> 4;
    if (this->c0 & (1 << 11))
        this->c0 = this->c0 | 0XF000;

    this->c1 = ((this->readBuffer[1] & 0xF) << 8) | this->readBuffer[2];

    if (this->c1 & (1 << 11))
        this->c1 = this->c1 | 0XF000;
}

void BarometerSensor ::read() {
    // Get raw data from sensor
    read_sensor_register(0x03, 3, 1000);

    int32_t raw_temp = (this->readBuffer[0] << 8) | this->readBuffer[1];
    raw_temp = (raw_temp << 8) | this->readBuffer[2];

    if (raw_temp & (1 << 23)) {
        raw_temp = raw_temp | 0XFF000000;
    }

    float temp = (float)raw_temp / (float)this->scaleFactor;
    temp = this->c0 * 0.5 + this->c1 * temp;

    // Write to CAN buffer
    memcpy(this->canBuffer, &temp, sizeof(temp));
}
