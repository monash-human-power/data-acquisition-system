#pragma once

#include <cstdint>
#include "Sensor.h"\

// The base class for all Analog sensors 
class AnalogSensor : public SensorBase {
    protected:
        

    public:
        explicit AnalogSensor(uint8_t id, );
        virtual ~AnalogSensor();

        bool init() override;

        SensorReading read() override = 0; 
};