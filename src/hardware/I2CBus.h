#pragma once

#include <cstdint>
#include <cstddef>
#include <string>
#include <vector>

class I2CBus
{
public:
    explicit I2CBus(const std::string& devicePath);

    ~I2CBus();

    bool writeRegister(uint8_t deviceAddress,
                       uint8_t reg,
                       uint8_t value);

    std::vector<uint8_t> readRegisters(uint8_t deviceAddress,
                                       uint8_t startReg,
                                       size_t length);

    bool writeCommand(uint8_t deviceAddress, uint8_t command);

    std::vector<uint8_t> readBytes(uint8_t deviceAddress, size_t length);

    // Resolve a TCA9548A mux channel to its dynamically assigned
    // Linux /dev/i2c-X child bus.
    static std::string resolveMuxChannel(
        int parentBus,
        uint8_t muxAddress,
        uint8_t channel
    );

private:
    int fileDescriptor;

    bool selectDevice(uint8_t deviceAddress);
};