#pragma once

#include <string>

#include "../data/SensorReading.h"

class SensorBase
{
protected:
    std::string sensorID;
    SensorReading lastReading;

public:
    explicit SensorBase(std::string id)
        : sensorID(std::move(id))
    {
        lastReading.sensorID = sensorID;
    }

    virtual ~SensorBase() = default;

    virtual bool init() = 0;
    virtual bool read() = 0;

    std::string getSensorID() const
    {
        return sensorID;
    }

    const SensorReading& getLastReading() const
    {
        return lastReading;
    }
};