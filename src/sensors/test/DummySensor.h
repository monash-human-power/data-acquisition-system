#pragma once

#include "../Sensor.h"

#include <cstdlib>
#include <ctime>
#include <cstdint>
#include <string>

class DummySensor : public SensorBase
{
public:
    explicit DummySensor(const std::string& id)
        : SensorBase(id)
    {
        std::srand(static_cast<unsigned int>(std::time(nullptr)));
    }

    bool init() override
    {
        return true;
    }

    bool read() override
    {
        float value =
            static_cast<float>(std::rand()) /
            static_cast<float>(RAND_MAX / 100.0f);

        std::uint64_t timestamp =
            static_cast<std::uint64_t>(std::time(nullptr));

        lastReading = {
            sensorID,
            timestamp,
            value,
            true
        };

        return true;
    }
};