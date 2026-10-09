#pragma once

#include "I2CSensor.h"

#include <cstdint>
#include <string>

class GyroscopeSensor : public I2CSensor
{
public:
    GyroscopeSensor(
        const std::string& id,
        I2CBus& bus
    );

    bool init() override;
    bool read() override;

    bool calibrateGyroscope(
        int samples = 200,
        int delayMs = 5
    );

private:
    static constexpr uint8_t ADDRESS = 0x68;

    static constexpr float ACCEL_LSB = 16384.0f;
    static constexpr float GYRO_LSB = 131.0f;

    float accelX;
    float accelY;
    float accelZ;

    float gyroX;
    float gyroY;
    float gyroZ;

    float temperatureC;

    float gyroBiasX;
    float gyroBiasY;
    float gyroBiasZ;

    static int16_t combineSigned(
        uint8_t high,
        uint8_t low
    );

    static std::uint64_t currentTimestampMs();
};