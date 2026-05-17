#pragma once

#include <cstdint>
#include "SensorReading.h"


// Define the base class that all sensors will be made from, no matter the communication format //

class SensorBase {
    protected:
        int sensorID;

    public:
        explicit SensorBase(uint8_t id) : sensorID(id) {};
        virtual ~SensorBase() {};

        virtual bool init() = 0;
        virtual SensorReading read() = 0;

        uint8_t getSensorID() const {
            return sensorID;
        }

    };