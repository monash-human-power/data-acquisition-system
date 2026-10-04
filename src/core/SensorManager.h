#pragma once

#include "../sensors/Sensor.h"
#include "../data/SensorReading.h"

#include <cstddef>
#include <memory>
#include <vector>

class SensorManager
{
public:
    void addSensor(std::shared_ptr<SensorBase> sensor);

    bool initAll();

    void readAll();

    std::vector<SensorReading> getReadings() const;

    std::size_t getSensorCount() const;

private:
    std::vector<std::shared_ptr<SensorBase>> sensors;
};