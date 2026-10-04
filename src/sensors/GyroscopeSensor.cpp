#include "GyroscopeSensor.h"

#include <chrono>
#include <iostream>
#include <thread>

GyroscopeSensor::GyroscopeSensor(
    const std::string& id,
    I2CBus& bus)
    : I2CSensor(id, bus, ADDRESS),
      accelX(0.0f),
      accelY(0.0f),
      accelZ(0.0f),
      gyroX(0.0f),
      gyroY(0.0f),
      gyroZ(0.0f),
      temperatureC(0.0f),
      gyroBiasX(0.0f),
      gyroBiasY(0.0f),
      gyroBiasZ(0.0f)
{
    lastReading.sensorID = sensorID;
    lastReading.timestamp = 0;
    lastReading.values.clear();
    lastReading.isValid = false;
}

bool GyroscopeSensor::init()
{
    auto whoami =
        bus.readRegisters(
            deviceAddress,
            0x75,
            1
        );

    if (whoami.size() != 1)
    {
        std::cerr
            << sensorID
            << ": could not read WHO_AM_I"
            << std::endl;

        return false;
    }

    if (whoami[0] != 0x68)
    {
        std::cerr
            << sensorID
            << ": warning: WHO_AM_I = 0x"
            << std::hex
            << static_cast<int>(whoami[0])
            << ", expected 0x68"
            << std::dec
            << std::endl;
    }

    // Reset device
    if (!bus.writeRegister(
            deviceAddress,
            0x6B,
            0x80))
    {
        return false;
    }

    std::this_thread::sleep_for(
        std::chrono::milliseconds(100)
    );

    // Wake device
    if (!bus.writeRegister(
            deviceAddress,
            0x6B,
            0x01))
    {
        return false;
    }

    std::this_thread::sleep_for(
        std::chrono::milliseconds(50)
    );

    // Gyroscope range = +/-250 degrees/sec
    if (!bus.writeRegister(
            deviceAddress,
            0x1B,
            0x00))
    {
        return false;
    }

    // Accelerometer range = +/-2g
    if (!bus.writeRegister(
            deviceAddress,
            0x1C,
            0x00))
    {
        return false;
    }

    // Digital low-pass filter
    if (!bus.writeRegister(
            deviceAddress,
            0x1A,
            0x03))
    {
        return false;
    }

    // No sample-rate division
    if (!bus.writeRegister(
            deviceAddress,
            0x19,
            0x00))
    {
        return false;
    }

    std::this_thread::sleep_for(
        std::chrono::milliseconds(20)
    );

    std::cout
        << sensorID
        << ": MPU6050 initialised successfully"
        << std::endl;

    return true;
}

bool GyroscopeSensor::read()
{
    auto data =
        bus.readRegisters(
            deviceAddress,
            0x3B,
            14
        );

    lastReading.sensorID = sensorID;
    lastReading.timestamp = currentTimestampMs();

    if (data.size() != 14)
    {
        lastReading.values.clear();
        lastReading.isValid = false;

        return false;
    }

    int16_t rawAx =
        combineSigned(data[0], data[1]);

    int16_t rawAy =
        combineSigned(data[2], data[3]);

    int16_t rawAz =
        combineSigned(data[4], data[5]);

    int16_t rawTemp =
        combineSigned(data[6], data[7]);

    int16_t rawGx =
        combineSigned(data[8], data[9]);

    int16_t rawGy =
        combineSigned(data[10], data[11]);

    int16_t rawGz =
        combineSigned(data[12], data[13]);

    accelX =
        static_cast<float>(rawAx) / ACCEL_LSB;

    accelY =
        static_cast<float>(rawAy) / ACCEL_LSB;

    accelZ =
        static_cast<float>(rawAz) / ACCEL_LSB;

    gyroX =
        static_cast<float>(rawGx) / GYRO_LSB
        - gyroBiasX;

    gyroY =
        static_cast<float>(rawGy) / GYRO_LSB
        - gyroBiasY;

    gyroZ =
        static_cast<float>(rawGz) / GYRO_LSB
        - gyroBiasZ;

    temperatureC =
        static_cast<float>(rawTemp) / 340.0f
        + 36.53f;

    lastReading.values.clear();

    lastReading.values["accel_x"] = accelX;
    lastReading.values["accel_y"] = accelY;
    lastReading.values["accel_z"] = accelZ;

    lastReading.values["gyro_x"] = gyroX;
    lastReading.values["gyro_y"] = gyroY;
    lastReading.values["gyro_z"] = gyroZ;

    lastReading.values["temperature_c"] = temperatureC;

    lastReading.isValid = true;

    return true;
}

bool GyroscopeSensor::calibrateGyroscope(
    int samples,
    int delayMs)
{
    float sumX = 0.0f;
    float sumY = 0.0f;
    float sumZ = 0.0f;

    int validSamples = 0;

    std::cout
        << sensorID
        << ": calibrating gyroscope..."
        << std::endl;

    for (int i = 0; i < samples; ++i)
    {
        auto data =
            bus.readRegisters(
                deviceAddress,
                0x3B,
                14
            );

        if (data.size() != 14)
        {
            continue;
        }

        int16_t rawGx =
            combineSigned(data[8], data[9]);

        int16_t rawGy =
            combineSigned(data[10], data[11]);

        int16_t rawGz =
            combineSigned(data[12], data[13]);

        sumX +=
            static_cast<float>(rawGx) / GYRO_LSB;

        sumY +=
            static_cast<float>(rawGy) / GYRO_LSB;

        sumZ +=
            static_cast<float>(rawGz) / GYRO_LSB;

        validSamples++;

        std::this_thread::sleep_for(
            std::chrono::milliseconds(delayMs)
        );
    }

    if (validSamples == 0)
    {
        std::cerr
            << sensorID
            << ": gyroscope calibration failed"
            << std::endl;

        return false;
    }

    gyroBiasX = sumX / validSamples;
    gyroBiasY = sumY / validSamples;
    gyroBiasZ = sumZ / validSamples;

    std::cout
        << sensorID
        << ": calibration complete"
        << std::endl;

    std::cout
        << "Gyro bias: "
        << gyroBiasX
        << ", "
        << gyroBiasY
        << ", "
        << gyroBiasZ
        << " dps"
        << std::endl;

    return true;
}

int16_t GyroscopeSensor::combineSigned(
    uint8_t high,
    uint8_t low)
{
    uint16_t combined =
        (static_cast<uint16_t>(high) << 8)
        | static_cast<uint16_t>(low);

    return static_cast<int16_t>(combined);
}

std::uint64_t GyroscopeSensor::currentTimestampMs()
{
    return static_cast<std::uint64_t>(
        std::chrono::duration_cast<
            std::chrono::milliseconds
        >(
            std::chrono::system_clock::now()
                .time_since_epoch()
        ).count()
    );
}