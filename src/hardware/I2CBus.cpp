#include "I2CBus.h"

#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>

#include <iostream>
#include <stdexcept>

I2CBus::I2CBus(const std::string& devicePath)
{
    fileDescriptor = open(devicePath.c_str(), O_RDWR);

    if (fileDescriptor < 0)
    {
        throw std::runtime_error("Failed to open I2C bus: " + devicePath);
    }
}

I2CBus::~I2CBus()
{
    if (fileDescriptor >= 0)
    {
        close(fileDescriptor);
    }
}

bool I2CBus::writeRegister(uint8_t deviceAddress,
                           uint8_t reg,
                           uint8_t value)
{
    if (ioctl(fileDescriptor, I2C_SLAVE, deviceAddress) < 0)
    {
        std::cerr << "Failed to select I2C device: 0x"
                  << std::hex << static_cast<int>(deviceAddress)
                  << std::dec << std::endl;

        return false;
    }

    uint8_t buffer[2];

    buffer[0] = reg;
    buffer[1] = value;

    ssize_t bytesWritten = write(fileDescriptor, buffer, 2);

    return bytesWritten == 2;
}

std::vector<uint8_t> I2CBus::readRegisters(uint8_t deviceAddress,
                                           uint8_t startReg,
                                           size_t length)
{
    std::vector<uint8_t> data(length);

    if (ioctl(fileDescriptor, I2C_SLAVE, deviceAddress) < 0)
    {
        std::cerr << "Failed to select I2C device: 0x"
                  << std::hex << static_cast<int>(deviceAddress)
                  << std::dec << std::endl;

        return {};
    }

    ssize_t bytesWritten = write(fileDescriptor, &startReg, 1);

    if (bytesWritten != 1)
    {
        std::cerr << "Failed to write start register" << std::endl;
        return {};
    }

    ssize_t bytesRead = read(fileDescriptor, data.data(), length);

    if (bytesRead != static_cast<ssize_t>(length))
    {
        std::cerr << "Failed to read requested bytes" << std::endl;
        return {};
    }

    return data;
}