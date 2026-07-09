#pragma once

#include <cstdint>
#include "Sensor.h"
#include "I2CBus.h"

class I2CSensor : public SensorBase {
    protected:
        uint8_t deviceAddress;
        I2CBus& bus;

    public:
        explicit I2CSensor(std::string id, I2CBus& bus, uint8_t addr);
        virtual ~I2CSensor();

        bool init() override = 0;

        bool read() override = 0;
        
};