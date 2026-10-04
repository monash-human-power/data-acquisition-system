#pragma once

#include "SensorReading.h"

#include <string>
#include <vector>

class DataSerialiser
{
public:
    static std::string toJSON(
        const SensorReading& reading
    );

    static std::vector<std::string> toJSON(
        const std::vector<SensorReading>& readings
    );

private:
    static std::string escapeJSONString(
        const std::string& input
    );
};