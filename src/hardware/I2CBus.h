#pragma once

#include <cstdint>
#include <string>
#include <vector>

class I2CBus
{
public:
    explicit I
    2CBus(const std::string& devicePath);

    bool writeRegister(uint8_t deviceAddress,
                       uint8_t reg,
                       uint8_t value);

    std::vector<uint8_t> readRegisters(uint8_t deviceAddress,
                                       uint8_t startReg,
                                       size_t length);

private:
    int fileDescriptor;
};