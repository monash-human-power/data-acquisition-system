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

    read_sensor_register(0x43, 6, 2000);  // Gyro X, Y, Z

    int16_t RAW_GX = (this->readBuffer[0] << 8) | this->readBuffer[1];
    int16_t RAW_GY = (this->readBuffer[2] << 8) | this->readBuffer[3];
    int16_t RAW_GZ = (this->readBuffer[4] << 8) | this->readBuffer[5];

    float gz = (float)RAW_GZ / 131.0;  // Assuming ±250°/s full scale (131 LSB/°/s)

    float data[2] = { zg, gz };
    memcpy(this->canBuffer, data, sizeof(data));
}
