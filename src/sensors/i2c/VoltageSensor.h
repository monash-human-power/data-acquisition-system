#pragma once
#include "I2CSensor.h"

// Voltage Sensor is based on the max17320, can also be used to implement other features:
// state of charge, intantaneous current, and temperature, by using their respective I2C registers
class VoltageSensor : public I2CSensor {
public:
    explicit VoltageSensor(std::string id, I2CBus& sharedBus, uint8_t addr = 0x36);

    ~VoltageSensor() override = default;

    bool init() override;
    bool read() override;
};