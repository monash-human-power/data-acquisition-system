#pragma once

#include <cstdint>

struct SensorReading{
    // Just dummy variables for now, need to decide/find out what is needed
    uint8_t sensorID;
    long timestamp;
    float value;
    bool isValid;

};
