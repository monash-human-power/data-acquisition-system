#pragma once

#include <cstdint>
#include "SensorReading.h"


// Define the base class that all sensors will be made from, no matter the communication format //

class SensorBase {
    protected:
        std::string sensorID;
        SensorReading lastReading;
    public:
        explicit SensorBase(std::string id) : sensorID(id) {};
        virtual ~SensorBase() {};

        virtual bool init() = 0;
        virtual bool read() = 0;
        virtual std::string serialize() const = 0;

        std::string getSensorID() const {
            return sensorID;
        }

    };