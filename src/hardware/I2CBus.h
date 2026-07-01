#pragma once

#include <cstdint>
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

    // Some I2C want direct commands instead of registers
    bool writeCommand(uint8_t deviceAddress, uint8_t command);
    std::vector<uint8_t> readBytes(uint8_t deviceAddress, size_t length);

private:
    int fileDescriptor;
    bool selectDevice(uint8_t deviceAddress);
};