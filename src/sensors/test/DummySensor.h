#pragma once
#include "Sensor.h"
#include <cstdlib> 
#include <ctime> 

// A dummy sensor that returns a random float from 0-100, to test without wiring everything up
class DummySensor : public SensorBase {
public:
    explicit DummySensor(int id) : SensorBase(id) {
        std::srand(static_cast<unsigned int>(std::time(nullptr)));
    }

    SensorReading read() override {
        float value = static_cast<float>(std::rand()) / (static_cast<float>(RAND_MAX / 100.0f));
        
        uint32_t timestamp = static_cast<uint32_t>(std::time(nullptr));

        return {sensorID, timestamp, value, true};
    }
};