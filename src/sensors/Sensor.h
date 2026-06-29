#pragma once

#include <string>

class Sensor
{
public:
    virtual bool init() = 0;

    virtual bool read() = 0;

    virtual std::string serialize() const = 0;

    virtual std::string getSensorID() const = 0;

    virtual ~Sensor() = default;
};