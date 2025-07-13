#include "ICM42670.h"
#include "SensorBase.h"

/* Register addresses (USER BANK 0)*/
namespace {
constexpr uint8_t REG_DEVICE_CONFIG  = 0x01;   // soft-reset
constexpr uint8_t REG_INT_CONFIG     = 0x06;   // interrupt pin cfg (optional)
constexpr uint8_t REG_PWR_MGMT0      = 0x1F;   // enable gyro / accel
constexpr uint8_t REG_GYRO_CONFIG0   = 0x20;   // FSR & ODR
constexpr uint8_t REG_GYRO_DATA_XYZ  = 0x11;   // first of 6 data bytes
constexpr uint8_t REG_WHO_AM_I       = 0x75;   // fixed device ID

/* Conversion constant for ±2000 dps full-scale (FS_SEL = 00)  
   From datasheet: 16.4 LSB = 1 deg/s */
constexpr float   DPSSCALE = 16.4f;
} // namespace

/* Constructor*/
GyroSensor::GyroSensor(i2c_port_t port,
                       uint8_t    address,
                       uint8_t    id)
    : I2cSensorBase(port, address, id),
      gyroX(0), gyroY(0), gyroZ(0) {}

/* Configure sensor registers*/
void GyroSensor::configure()
{
    /* 1)  Softreset */
    write_sensor_register(REG_DEVICE_CONFIG, 0x01, 1000);
    delay(50);

    /* 2)  Power-up gyro + accel in Low-Noise mode (bits [3:0] = 0b0111) */
    write_sensor_register(REG_PWR_MGMT0, 0x07, 1000);

    /* 3)  Gyro full-scale ±2000 dps & 1.1 kHz ODR (FS_SEL = 00, ODR = 011) */
    write_sensor_register(REG_GYRO_CONFIG0, 0x03, 1000);

    /* 4) (Optional) set INT1 active-high, push-pull, pulse mode   BIT0 = 1 */
    // write_sensor_register(REG_INT_CONFIG, 0x01, 1000);

    /* 5)  Verify WHO_AM_I = 0x67 (optional sanity check) */
    read_sensor_register(REG_WHO_AM_I, 1, 1000);
    if (readBuffer[0] != 0x67) {
        Serial.printf("ICM-42670-P: unexpected WHO_AM_I (0x%02X)\n", readBuffer[0]);
    }
}

/*  Read 6 bytes of gyro data*/
void GyroSensor::read()
{
    read_sensor_register(REG_GYRO_DATA_XYZ, 6, 1000);

    int16_t rawX = int16_t(readBuffer[0] << 8 | readBuffer[1]);
    int16_t rawY = int16_t(readBuffer[2] << 8 | readBuffer[3]);
    int16_t rawZ = int16_t(readBuffer[4] << 8 | readBuffer[5]);

    gyroX = rawX / DPSSCALE;
    gyroY = rawY / DPSSCALE;
    gyroZ = rawZ / DPSSCALE;
}

/* JSON payload for this sensor*/
String GyroSensor::generateJson()
{
    // two decimal places is enough precision for most telemetry streams
    return String("{\"sensor\":\"gyroscope\",\"x\":") + String(gyroX, 2) +
           ",\"y\":" + String(gyroY, 2) +
           ",\"z\":" + String(gyroZ, 2) + "}";
}
