#pragma once

#include <cstdint>
#include <string>
#include <unordered_map>

struct SensorReading
{
    std::string sensorID;
    std::uint64_t timestamp = 0;

    // Sensor-specific values.
    // Example for gyro:
    // accel_x, accel_y, accel_z,
    // gyro_x, gyro_y, gyro_z,
    // temperature_c
    std::unordered_map<std::string, float> values;

    bool isValid = false;
};