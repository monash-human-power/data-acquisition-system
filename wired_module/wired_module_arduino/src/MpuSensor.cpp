#include "MpuSensor.h"
#include <cstring>

void MpuSensor::configure() {
    write_sensor_register(0x4E, 0x0F, 2000);
    delay(100);
}

void MpuSensor::read() {
    // Read accelerometer data from registers 0x1F to 0x24
    read_sensor_register(0x1F, 6, 2000); // ACCEL_X/Y/Z_OUT
    int16_t accX = (readBuffer[0] << 8) | readBuffer[1];
    int16_t accY = (readBuffer[2] << 8) | readBuffer[3];
    int16_t accZ = (readBuffer[4] << 8) | readBuffer[5];

    // Convert to g using ±16g scale => 2048 LSB/g (or adjust if using ±2g)
    float ax = (float)accX / 2048.0f;
    float ay = (float)accY / 2048.0f;
    float az = (float)accZ / 2048.0f;

    // Read gyro data from registers 0x25 to 0x2A
    read_sensor_register(0x25, 6, 2000); // GYRO_X/Y/Z_OUT
    int16_t gyroX = (readBuffer[0] << 8) | readBuffer[1];
    int16_t gyroY = (readBuffer[2] << 8) | readBuffer[3];
    int16_t gyroZ = (readBuffer[4] << 8) | readBuffer[5];

    // Convert to °/s using ±2000 dps => 16.4 LSB/°/s (or adjust scale)
    float gz = (float)gyroZ / 16.4f;

    // Only sending Z accel and Z gyro for now
    float data[2] = { az, gz };
    memcpy(this->canBuffer, data, sizeof(data));
}

void MpuSensor::send() {
    // Retrieve accelerometer and gyroscope data (stored in canBuffer)
    float az = ((float*)this->canBuffer)[0];  // Z-axis acceleration
    float gz = ((float*)this->canBuffer)[1];  // Z-axis gyroscope

    // Create JSON string — Example: {"sensors":[{"type":"mpu","acceleration_z":0.123,"gyro_z":2.345}]}
    String json = "{\"sensors\":[{\"type\":\"mpu\",\"acceleration_z\":" + String(az, 4) + 
                  ",\"gyro_z\":" + String(gz, 4) + "}]}";

    sendJson(this->canId, json);  // Use the instance's CAN ID
}
