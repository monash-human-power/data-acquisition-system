#pragma once

#include "Sensor.h"
#include "SPIBus.h"

// The base class for all SPI sensors
class SPISensor : public SensorBase {
    protected:
        SPIBus& bus;

    public:
        explicit SPISensor(std::string id, SPIBus& bus);
        virtual ~SPISensor();

        bool init() override = 0;

        bool read() override = 0;
};
