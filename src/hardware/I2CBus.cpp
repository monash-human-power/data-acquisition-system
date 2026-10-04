#include "I2CBus.h"

#include <filesystem>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>

#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>

I2CBus::I2CBus(const std::string& devicePath)
{
    fileDescriptor = open(devicePath.c_str(), O_RDWR);

    if (fileDescriptor < 0)
    {
        throw std::runtime_error(
            "Failed to open I2C bus at: " + devicePath
        );
    }

    if (ioctl(fileDescriptor, I2C_RETRIES, 1) < 0)
    {
        std::cerr << "Warning: Could not set I2C retries"
                  << std::endl;
    }

    if (ioctl(fileDescriptor, I2C_TIMEOUT, 1) < 0)
    {
        std::cerr << "Warning: Could not set I2C timeout"
                  << std::endl;
    }
}

I2CBus::~I2CBus()
{
    if (fileDescriptor >= 0)
    {
        close(fileDescriptor);
    }
}

bool I2CBus::selectDevice(uint8_t deviceAddress)
{
    if (ioctl(fileDescriptor, I2C_SLAVE, deviceAddress) < 0)
    {
        std::cerr
            << "Failed to select I2C device address: 0x"
            << std::hex
            << static_cast<int>(deviceAddress)
            << std::dec
            << std::endl;

        return false;
    }

    return true;
}

bool I2CBus::writeRegister(
    uint8_t deviceAddress,
    uint8_t reg,
    uint8_t value)
{
    if (!selectDevice(deviceAddress))
    {
        return false;
    }

    uint8_t buffer[2] = {reg, value};

    if (write(fileDescriptor, buffer, 2) != 2)
    {
        std::cerr
            << "Failed to write to device 0x"
            << std::hex
            << static_cast<int>(deviceAddress)
            << std::dec
            << std::endl;

        return false;
    }

    return true;
}

std::vector<uint8_t> I2CBus::readRegisters(
    uint8_t deviceAddress,
    uint8_t startReg,
    size_t length)
{
    std::vector<uint8_t> data(length, 0);

    if (!selectDevice(deviceAddress))
    {
        return {};
    }

    if (write(fileDescriptor, &startReg, 1) != 1)
    {
        std::cerr
            << "Failed to select register 0x"
            << std::hex
            << static_cast<int>(startReg)
            << " on device 0x"
            << static_cast<int>(deviceAddress)
            << std::dec
            << std::endl;

        return {};
    }

    if (read(
            fileDescriptor,
            data.data(),
            length
        ) != static_cast<ssize_t>(length))
    {
        std::cerr
            << "Failed to read data from device 0x"
            << std::hex
            << static_cast<int>(deviceAddress)
            << std::dec
            << std::endl;

        return {};
    }

    return data;
}

bool I2CBus::writeCommand(
    uint8_t deviceAddress,
    uint8_t command)
{
    if (!selectDevice(deviceAddress))
    {
        return false;
    }

    if (write(fileDescriptor, &command, 1) != 1)
    {
        std::cerr
            << "Failed to write command to 0x"
            << std::hex
            << static_cast<int>(deviceAddress)
            << std::dec
            << std::endl;

        return false;
    }

    return true;
}

std::vector<uint8_t> I2CBus::readBytes(
    uint8_t deviceAddress,
    size_t length)
{
    std::vector<uint8_t> data(length, 0);

    if (!selectDevice(deviceAddress))
    {
        return {};
    }

    if (read(
            fileDescriptor,
            data.data(),
            length
        ) != static_cast<ssize_t>(length))
    {
        std::cerr
            << "Failed to read data from 0x"
            << std::hex
            << static_cast<int>(deviceAddress)
            << std::dec
            << std::endl;

        return {};
    }

    return data;
}

std::string I2CBus::resolveMuxChannel(
    int parentBus,
    uint8_t muxAddress,
    uint8_t channel)
{
    std::stringstream muxName;

    muxName
        << parentBus
        << "-"
        << std::setfill('0')
        << std::setw(4)
        << std::hex
        << static_cast<int>(muxAddress);

    std::filesystem::path sysfsPath =
        "/sys/bus/i2c/devices";

    sysfsPath /= muxName.str();
    sysfsPath /= "channel-" + std::to_string(channel);

    try
    {
        std::filesystem::path resolved =
            std::filesystem::canonical(sysfsPath);

        std::string busName =
            resolved.filename().string();

        // Normally the final path is something like:
        // .../i2c-10
        if (busName.rfind("i2c-", 0) != 0)
        {
            throw std::runtime_error(
                "Unexpected mux channel path: " +
                resolved.string()
            );
        }

        return "/dev/" + busName;
    }
    catch (const std::filesystem::filesystem_error& e)
    {
        throw std::runtime_error(
            "Could not resolve mux channel " +
            std::to_string(channel) +
            ": " +
            e.what()
        );
    }
}