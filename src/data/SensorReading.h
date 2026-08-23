#pragma once

#include <cstdint>
#include <string>

struct SensorReading{
    // Just dummy variables for now, need to decide/find out what is needed
    std::string sensorID;
    std::uint64_t timestamp;
    float value;
    bool isValid;

};
