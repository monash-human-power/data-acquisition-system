#include "I2CBus.h"
#include <iostream>

#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>

I2CBus::I2CBus(const std::string& devicePath) {
    fileDescriptor = open(devicePath.c_str(), O_RDWR);
    
    if (fileDescriptor < 0) {
        throw std::runtime_error("Failed to open I2C bus at: " + devicePath);
    }

    // Limit retries for failed reads
    if (ioctl(fileDescriptor, I2C_RETRIES, 1) < 0) {
        std::cerr << "Warning: Could not set I2C retries" << std::endl;
    }

    // Set a 10ms timeout on reads
    if (ioctl(fileDescriptor, I2C_TIMEOUT, 1) < 0) {
        std::cerr << "Warning: Could not set I2C timeout" << std::endl;
    }
}

I2CBus::~I2CBus() {
    if (fileDescriptor >= 0) {
        close(fileDescriptor);
    }
}

bool I2CBus::selectDevice(uint8_t deviceAddress) {
    if (ioctl(fileDescriptor, I2C_SLAVE, deviceAddress) < 0) {
        std::cerr << "Failed to select I2C device address: 0x" << std::hex << (int)deviceAddress << std::endl;
        return false;
    }
    return true;
}

// Don't know if any of our sensors will actually need this, but have it anyway in case
bool I2CBus::writeRegister(uint8_t deviceAddress, uint8_t reg, uint8_t value) {
    if (!selectDevice(deviceAddress)) return false;

    uint8_t buffer[2] = {reg, value};
    
    if (write(fileDescriptor, buffer, 2) != 2) {
        std::cerr << "Failed to write to device 0x" << std::hex << (int)deviceAddress << std::endl;
        return false;
    }
    return true;
}

std::vector<uint8_t> I2CBus::readRegisters(uint8_t deviceAddress, uint8_t startReg, size_t length) {
    std::vector<uint8_t> data(length, 0);
    
    if (!selectDevice(deviceAddress)) {
        return std::vector<uint8_t>(); 
    }

    if (write(fileDescriptor, &startReg, 1) != 1) {
        std::cerr << "Failed to announce request to register 0x" << std::hex << (int)deviceAddress << std::endl;
        return std::vector<uint8_t>();
    }

    if (read(fileDescriptor, data.data(), length) != static_cast<ssize_t>(length)) {
        std::cerr << "Failed to read data from device 0x" << std::hex << (int)deviceAddress << std::endl;
        return std::vector<uint8_t>();
    }
    
    return data;
}

bool I2CBus::writeCommand(uint8_t deviceAddress, uint8_t command) {
    if (!selectDevice(deviceAddress)) return false;

    if (write(fileDescriptor, &command, 1) != 1) {
        std::cerr << "Failed to write command to 0x" << std::hex << (int)deviceAddress << std::endl;
        return false;
    }
    return true;
}

std::vector<uint8_t> I2CBus::readBytes(uint8_t deviceAddress, size_t length) {
    std::vector<uint8_t> data(length, 0);
    
    if (!selectDevice(deviceAddress)) {
        return std::vector<uint8_t>(); 
    }

    if (read(fileDescriptor, data.data(), length) != static_cast<ssize_t>(length)) {
        std::cerr << "Failed to read data from 0x" << std::hex << (int)deviceAddress << std::endl;
        return std::vector<uint8_t>();
    }
    
    return data;
}