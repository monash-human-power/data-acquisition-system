#include "MAX17320.h"
#include <iostream>
#include <chrono>

MAX17320::MAX17320(const std::string id, I2CBus& sharedBus)
    : I2CSensor(id, bus) {}

bool MAX17320::init() {
    // 0x36 is MAX17320 address, battery voltage is on register 0xDA
    std::vector<uint8_t> testRead = bus->readRegisters(0x36, 0xDA, 2);
    if (testRead.empty()) {
        return false;
    }
    return true;
}

bool MAX17320::read() {
    SensorReading newReading;
    newReading.isValid = false;

    // 2 byte voltage
    std::vector<uint8_t> voltageData = bus->readRegisters(0x36, 0xDA, 2);

    if (voltageData.empty()) {
        this->lastReading = reading;
        return false;
    }
    
    // Read as LSB first
    uint16_t rawVoltage = (voltData[1] << 8) | voltData[0];
    
    // From datasheet
    float voltage = rawVoltage * 0.0003125f;

    newReading.value = voltage;
    
    newReading.timestamp = std::chrono::duration_cast<std::chrono::milliseconds>(
                               std::chrono::system_clock::now().time_since_epoch()
                           ).count();
    newReading.isValid = true;

    this->lastReading = newReading;

    return true;
}