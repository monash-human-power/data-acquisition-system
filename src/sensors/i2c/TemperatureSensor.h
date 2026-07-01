#pragma once
#include "I2CSensor.h"

class TemperatureSensor : public I2CSensor {
public:
    explicit TemperatureSensor(I2CBus& sharedBus, int id, int addr = 0x44);

    ~TemperatureSensor() override = default;

    bool init() override;
    SensorReading read() override;
};