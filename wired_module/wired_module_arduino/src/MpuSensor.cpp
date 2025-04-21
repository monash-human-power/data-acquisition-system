#include "MpuSensor.h"

#include <cstring>

void MpuSensor::configure() {
    write_sensor_register(0x6B, 0, 2000);
    write_sensor_register(0x19, 7, 2000);
}

void MpuSensor ::read() {
    // Get raw data from sensor
    read_sensor_register(0x3B, 6, 2000);

    int16_t RAWX = (this->readBuffer[0] << 8) | this->readBuffer[1];
    int16_t RAWY = (this->readBuffer[2] << 8) | this->readBuffer[3];
    int16_t RAWZ = (this->readBuffer[4] << 8) | this->readBuffer[5];

    float xg = (float)RAWX / 16384;
    float yg = (float)RAWY / 16384;
    float zg = (float)RAWZ / 16384;

    // Write to CAN buffer
    memcpy(this->canBuffer, &zg, sizeof(zg));
}
