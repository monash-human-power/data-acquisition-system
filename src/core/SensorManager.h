#pragma once

#include "Sensor.h"

#include <memory>
#include <string>
#include <vector>

class SensorManager
{
public:
    void addSensor(std::shared_ptr<Sensor> sensor);

    bool initAll();

    void readAll();

    std::vector<std::string> serializeAll() const;

    size_t getSensorCount() const;

private:
    std::vector<std::shared_ptr<Sensor>> sensors;
};