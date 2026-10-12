#pragma once
#include "I2CSensor.h"

// The pre-emptive code for the wheel speed sensor, 
// check finalised wheel speed code to see if this needs to be changed

// Wheel Speed Sensor interfaces with a custom ATTiny85 slave.
// It retrieves a pre-calculated 4-byte float representing speed in km/h.
class WheelSpeedSensor : public I2CSensor {
public:
    // Defaulting to 0x45 (need to see what is set in the ATTiny)
    explicit WheelSpeedSensor(std::string id, I2CBus& sharedBus, uint8_t addr = 0x45);

    ~WheelSpeedSensor() override = default;

    bool init() override;
    bool read() override;
};