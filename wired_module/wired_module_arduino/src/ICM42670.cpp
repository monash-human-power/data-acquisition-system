#include "ICM42670.h"
#include "SensorBase.h"

void ICM42670::configure() {
    // Reset device
    write_sensor_register(0x11, 0x01, 1000); // DEVICE_CONFIG register
    delay(100);

    // Set to Low Noise Mode for Gyro
    write_sensor_register(0x4E, 0x07, 1000); // PWR_MGMT0: Enable Accel + Gyro in LN mode

    // Set Gyro Config (e.g., 2000 dps full scale, 1.1 kHz BW)
    write_sensor_register(0x4F, 0x03, 1000); // GYRO_CONFIG0: 2000 dps FS and 1.1 kHz ODR

    // Route data ready interrupt to INT1 (optional)
    write_sensor_register(0x14, 0x01, 1000); // INT_CONFIG

    delay(50);
}

void GyroSensor::read() {
    // Read 6 bytes of gyro data from registers 0x25 to 0x2A
    read_sensor_register(0x25, 6, 1000);

    int16_t rawX = (readBuffer[0] << 8) | readBuffer[1];
    int16_t rawY = (readBuffer[2] << 8) | readBuffer[3];
    int16_t rawZ = (readBuffer[4] << 8) | readBuffer[5];

    // Convert raw to dps (2000 dps = scale factor of 16.4 LSB/dps)
    gyroX = static_cast<float>(rawX) / 16.4f;
    gyroY = static_cast<float>(rawY) / 16.4f;
    gyroZ = static_cast<float>(rawZ) / 16.4f;
}

String GyroSensor::generateJson() {
    return "{\"sensors\":[{\"type\":\"gyroscope\",\"x\":" + String(gyroX, 2) +
           ",\"y\":" + String(gyroY, 2) + ",\"z\":" + String(gyroZ, 2) + "}]}";
}

void GyroSensor::send() {
    sendJson(0x123, generateJson()); // Example CAN ID
}
