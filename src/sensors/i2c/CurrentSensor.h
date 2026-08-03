#pragma once
#include "I2CSensor.h"

// Current Sensor based on the max17320
class CurrentSensor : public I2CSensor {
private:
    // TODO: Set the sensing resistor based on PCB
    // Currently set as 2.2mOhm resistor
    float SENSE_RESISTOR_OHMS = 0.0022f; 

public:
    explicit CurrentSensor(std::string id, I2CBus& sharedBus, uint8_t addr = 0x36);

    ~CurrentSensor() override = default;

    bool init() override;
    bool read() override;
};