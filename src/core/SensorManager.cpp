#include "SensorManager.h"

#include <iostream>

void SensorManager::addSensor(std::shared_ptr<SensorBase> sensor)
{
    sensors.push_back(sensor);
}

bool SensorManager::initAll()
{
    bool allSuccessful = true;

    for (const auto& sensor : sensors)
    {
        bool success = sensor->init();

        if (!success)
        {
            std::cerr << "Failed to initialise sensor: "
                      << sensor->getSensorID()
                      << std::endl;

            allSuccessful = false;
        }
    }

    return allSuccessful;
}

void SensorManager::readAll()
{
    for (const auto& sensor : sensors)
    {
        bool success = sensor->read();

        if (!success)
        {
            std::cerr << "Failed to read sensor: "
                      << sensor->getSensorID()
                      << std::endl;
        }
    }
}

std::vector<std::string> SensorManager::serializeAll() const
{
    std::vector<std::string> output;

    for (const auto& sensor : sensors)
    {
        output.push_back(sensor->serialize());
    }

    return output;
}

std::size_t SensorManager::getSensorCount() const
{
    return sensors.size();
}