#pragma once
#include "I2CSensor.h"

// Note that this is the same sensor as the temperature sensor, 
// but is written here so that it can be treated as two distinct sensors if needed
class HumiditySensor : public I2CSensor {
public:
    explicit HumiditySensor(I2CBus& sharedBus, int id, int addr = 0x44);

    ~HumiditySensor() override = default;

    bool init() override;
    SensorReading read() override;
};