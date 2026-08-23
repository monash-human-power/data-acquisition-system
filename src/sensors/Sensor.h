#pragma once

#include <cstdint>
#include <sstream>
#include <string>

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

        std::string getSensorID() const {
            return sensorID;
        }

        virtual std::string serialize() const{
            std::stringstream ss;
            ss << this->lastReading.sensorID << "," << this->lastReading.timestamp << "," << this->lastReading.value << "," << this->lastReading.isValid;

            return ss.str();
        }
    };
