#pragma once

#include <cstdint>

struct SensorReading{
    // Just dummy variables for now, need to decide/find out what is needed
    std::string sensorID;
    long timestamp;
    float value;
    bool isValid;

};
