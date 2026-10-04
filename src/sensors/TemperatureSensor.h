#pragma once

#include "I2CSensor.h"

class TemperatureSensor : public I2CSensor
{
public:
    TemperatureSensor(
        const std::string& id,
        I2CBus& bus
    );

    bool init() override;
    bool read() override;

private:
    static constexpr uint8_t ADDRESS = 0x3C;

    static constexpr uint8_t WHOAMI_REG = 0x01;
    static constexpr uint8_t WHOAMI_VALUE = 0xA0;

    static constexpr uint8_t CTRL_REG = 0x04;
    static constexpr uint8_t TEMP_LOW_REG = 0x06;

    static std::uint64_t currentTimestampMs();
};