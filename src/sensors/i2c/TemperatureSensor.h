#pragma once
#include "I2CSensor.h"

class TemperatureSensor : public I2CSensor {
public:
    explicit TemperatureSensor(std::string id, I2CBus& sharedBus, uint8_t addr = 0x44);

    ~TemperatureSensor() override = default;

    bool init() override;
    bool read() override;
};