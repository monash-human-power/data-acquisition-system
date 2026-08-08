#pragma once

#include <cstdint>
#include "Sensor.h"

// The base class for all Analog sensors 

// Analog is no longer needed. With the pi 5, an analog sensor would be implemented with an ADC hat,
// this ADC hat would communicate with I2C, so the sensor can be treated as I2C for code purposes.
class AnalogSensor : public SensorBase {
    protected:
        

    public:
        explicit AnalogSensor(uint8_t id);
        virtual ~AnalogSensor();

        bool init() override;

        bool read() override = 0; 
};