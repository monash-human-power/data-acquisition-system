#include "MpuSensor.h"
#include <cstring>

MpuSensor::MpuSensor(uint8_t canId) : SensorBase(canId) {}

void MpuSensor::configure() {
    write_sensor_register(0x4E, 0x0F, 2000);
    delay(100);
}

void MpuSensor::read() {
    // Read accelerometer data
    read_sensor_register(0x1F, 6, 2000);
    int16_t accX = (readBuffer[0] << 8) | readBuffer[1];
    int16_t accY = (readBuffer[2] << 8) | readBuffer[3];
    int16_t accZ = (readBuffer[4] << 8) | readBuffer[5];

    float ax = (float)accX / 2048.0f;
    float ay = (float)accY / 2048.0f;
    float az = (float)accZ / 2048.0f;

    // Read gyroscope data
    read_sensor_register(0x25, 6, 2000);
    int16_t gyroX = (readBuffer[0] << 8) | readBuffer[1];
    int16_t gyroY = (readBuffer[2] << 8) | readBuffer[3];
    int16_t gyroZ = (readBuffer[4] << 8) | readBuffer[5];

    float gz = (float)gyroZ / 16.4f;

    // Store Z-axis accel and gyro in CAN buffer
    float data[2] = { az, gz };
    memcpy(this->canBuffer, data, sizeof(data));
}

String MpuSensor::generateJson() {
    float az = ((float*)this->canBuffer)[0];
    float gz = ((float*)this->canBuffer)[1];

    String json = "{\"sensors\":[{\"type\":\"mpu\",\"acceleration_z\":" + String(az, 4) +
                  ",\"gyro_z\":" + String(gz, 4) + "}]}";
    return json;
}

void MpuSensor::send() {
    sendJson(this->canId, generateJson());
}
