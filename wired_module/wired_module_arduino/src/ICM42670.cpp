#include "ICM42670.h"
#include "SensorBase.h"

// === Register Addresses ===
#define REG_DEVICE_CONFIG    0x11
#define REG_PWR_MGMT0        0x4E
#define REG_GYRO_CONFIG0     0x4F
#define REG_INT_CONFIG       0x14
#define REG_GYRO_DATA_XYZ    0x25  // X, Y, Z gyro starting register

// === Constructor ===
GyroSensor::GyroSensor(i2c_port_t masterPortNum, uint8_t sensorAddress, uint8_t sensorID)
    : I2cSensorBase(masterPortNum, sensorAddress, sensorID),
      gyroX(0), gyroY(0), gyroZ(0) {}

// === Configure Sensor ===
void GyroSensor::configure() {
    write_sensor_register(REG_DEVICE_CONFIG, 0x01, 1000);  // Soft reset
    delay(100);

    write_sensor_register(REG_PWR_MGMT0, 0x07, 1000);      // Enable accel + gyro, low-noise mode
    write_sensor_register(REG_GYRO_CONFIG0, 0x03, 1000);   // 2000 dps, 1.1 kHz ODR
    write_sensor_register(REG_INT_CONFIG, 0x01, 1000);     // Optional: route interrupt to INT1

    delay(50);
}

// === Read Gyro Data ===
void GyroSensor::read() {
    read_sensor_register(REG_GYRO_DATA_XYZ, 6, 1000);  // Read 6 bytes: X, Y, Z

    int16_t rawX = (readBuffer[0] << 8) | readBuffer[1];
    int16_t rawY = (readBuffer[2] << 8) | readBuffer[3];
    int16_t rawZ = (readBuffer[4] << 8) | readBuffer[5];

    // Convert to dps: 2000 dps FS = 16.4 LSB/dps
    gyroX = static_cast<float>(rawX) / 16.4f;
    gyroY = static_cast<float>(rawY) / 16.4f;
    gyroZ = static_cast<float>(rawZ) / 16.4f;
}

// === JSON Format ===
String GyroSensor::generateJson() {
    return "{\"sensor\":\"gyroscope\",\"x\":" + String(gyroX, 2) +
           ",\"y\":" + String(gyroY, 2) +
           ",\"z\":" + String(gyroZ, 2) + "}";
}
