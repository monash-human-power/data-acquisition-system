#pragma once

#include <cstdint>
#include "Sensor.h"
#include "I2CBus.h"

// The base class for all I2C sensors, will require deciding on I2C interaction methods before fully implementing
class I2CSensor : public SensorBase {
    protected:
        u_int8_t deviceAddress;
        // Will likely need to add a bus and other info related to connection, plus functions for children to use
        I2CBus& bus;

    public:
        explicit I2CSensor(uint8_t id, I2CBus& bus, uint8_t addr);
        virtual ~I2CSensor();

        bool init() override;

        SensorReading read() override = 0; 
};